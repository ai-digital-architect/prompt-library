"""The judge tribunal.

Judges are used only for dimensions with no oracle: root-cause reasoning,
remediation viability, communication. Everything the graph or the toolchain can
decide is decided there first.

The design corrects three specific failure modes:

1. **Self-preference.** A candidate is never judged by its own family. Even
   blinded, a judge favours stylistic conventions it shares with a candidate.

2. **Correlated panels.** Adding judges does not add independent evidence — a
   2026 study found strongly correlated errors across model panels. So panel
   independence is MEASURED on a gold set and an effective panel size is derived.
   Three highly-correlated judges are reported as closer to one than to three,
   rather than being counted as three.

3. **Silent judge drift.** A provider-side model update re-bases every score
   with no signal. Judges are version-pinned and re-run a fixed gold set before
   every round; agreement drift beyond a threshold quarantines the round.

And one thing v1 missed entirely: judge prompts go through the SAME adapter
layer as candidate prompts. Otherwise the judging layer carries exactly the
prompt confound the lane design exists to eliminate.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Any

JUDGE_ROLES = ("evidence_auditor", "domain_expert", "adversarial_reviewer", "arbiter")

FAMILY_OF = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "google",
}


@dataclass
class JudgeSpec:
    role: str
    model_id: str
    provider: str
    adapter_id: str
    adapter_version: str
    prompt_hash: str
    effort: str | None = None
    reasoning_mode: str | None = None

    def pin(self) -> str:
        """Version pin. Any change here changes what the panel measures."""
        raw = f"{self.role}|{self.model_id}|{self.adapter_id}|{self.adapter_version}|{self.prompt_hash}|{self.effort}|{self.reasoning_mode}"
        return "judge:" + hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Panel:
    judges: list[JudgeSpec] = field(default_factory=list)
    version: str = "1.0.0"
    cross_family_rule: bool = True
    blinding: bool = True
    position_check: bool = True

    def eligible_for(self, candidate_provider: str) -> list[JudgeSpec]:
        """Drop judges from the candidate's own family."""
        if not self.cross_family_rule:
            return list(self.judges)
        fam = FAMILY_OF.get(candidate_provider, candidate_provider)
        return [j for j in self.judges if FAMILY_OF.get(j.provider, j.provider) != fam]

    def pin(self) -> str:
        return "panel:" + hashlib.sha256("|".join(sorted(j.pin() for j in self.judges)).encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# Blinding
# --------------------------------------------------------------------------

def blind(candidates: dict[str, Any], seed: int) -> tuple[dict[str, Any], dict[str, str]]:
    """Relabel candidates as A, B, C… in randomized order.

    Returns (blinded, mapping-from-label-to-model). The mapping is stored
    separately from the transcript so a reviewer with store access cannot undo
    the blinding by reading one file.
    """
    rng = random.Random(seed)
    items = list(candidates.items())
    rng.shuffle(items)
    labels = [chr(ord("A") + i) for i in range(len(items))]
    blinded = {labels[i]: content for i, (_, content) in enumerate(items)}
    mapping = {labels[i]: model for i, (model, _) in enumerate(items)}
    return blinded, mapping


def position_pairs(labels: list[str]) -> list[tuple[str, str]]:
    """Round-robin, both orders. Running only A-vs-B leaves position bias
    invisible; running both and comparing the verdicts makes it measurable."""
    out = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            out.append((a, b))
            out.append((b, a))
    return out


def position_consistency(verdicts: dict[tuple[str, str], str]) -> dict[str, Any]:
    """Fraction of pairs where the verdict survived swapping the order."""
    checked = 0
    consistent = 0
    for (a, b), winner in verdicts.items():
        rev = verdicts.get((b, a))
        if rev is None:
            continue
        checked += 1
        if winner == rev:
            consistent += 1
    rate = round(consistent / checked, 4) if checked else None
    return {
        "pairs_checked": checked,
        "consistent": consistent,
        "consistency_rate": rate,
        "note": ("position bias detected — verdicts flip when the order is swapped; "
                 "treat pairwise rankings from this panel as unreliable"
                 if rate is not None and rate < 0.8 else ""),
    }


# --------------------------------------------------------------------------
# Bradley-Terry ranking
# --------------------------------------------------------------------------

def bradley_terry(wins: dict[tuple[str, str], int], iterations: int = 200,
                  tol: float = 1e-8) -> dict[str, float]:
    """Fit Bradley-Terry strengths from pairwise wins via MM iteration.

    `wins[(a, b)]` is the number of times a beat b. Returns normalized strengths.
    Pairwise comparison with a fitted ranking is more robust than absolute 1-10
    ratings, which drift between judges and between rounds.
    """
    players = sorted({p for pair in wins for p in pair})
    if not players:
        return {}
    p = {x: 1.0 for x in players}
    for _ in range(iterations):
        new = {}
        for a in players:
            num = sum(w for (x, y), w in wins.items() if x == a)
            den = 0.0
            for (x, y), w in wins.items():
                if x == a:
                    den += w / (p[a] + p[y])
                elif y == a:
                    den += w / (p[x] + p[a])
            new[a] = num / den if den > 0 else p[a]
        total = sum(new.values()) or 1.0
        new = {k: v / total * len(players) for k, v in new.items()}
        if max(abs(new[k] - p[k]) for k in players) < tol:
            p = new
            break
        p = new
    return {k: round(v, 4) for k, v in sorted(p.items(), key=lambda kv: -kv[1])}


# --------------------------------------------------------------------------
# Panel independence and drift
# --------------------------------------------------------------------------

def effective_panel_size(judge_errors: dict[str, list[float]]) -> dict[str, Any]:
    """Discount panel size by measured inter-judge error correlation.

    n_eff = n / (1 + (n-1) * mean_pairwise_correlation)

    Three judges whose errors correlate at 0.9 give an effective size of about
    1.1. Reporting them as three would overstate the evidence by roughly a factor
    of three, which is how a panel produces false confidence.
    """
    judges = sorted(judge_errors)
    n = len(judges)
    if n < 2:
        return {"n": n, "effective_n": float(n), "mean_correlation": 0.0}

    from .stats import _pearson
    cors = []
    for i, a in enumerate(judges):
        for b in judges[i + 1:]:
            xa, xb = judge_errors[a], judge_errors[b]
            m = min(len(xa), len(xb))
            if m > 2:
                cors.append(_pearson(xa[:m], xb[:m]))
    mean_c = sum(cors) / len(cors) if cors else 0.0
    n_eff = n / (1 + (n - 1) * max(0.0, mean_c)) if n > 1 else float(n)
    return {
        "n": n,
        "effective_n": round(n_eff, 2),
        "mean_correlation": round(mean_c, 4),
        "note": ("panel errors are strongly correlated — adding judges of this kind adds "
                 "little independent evidence; diversify by family and by lens instead"
                 if mean_c > 0.6 else ""),
    }


def judge_drift(current_agreement: dict[str, float], baseline_agreement: dict[str, float],
                threshold: float = 0.08) -> dict[str, Any]:
    """Compare gold-set agreement to the recorded baseline.

    Run BEFORE each leaderboard round. Without it, a silent provider-side model
    update re-bases every score in the round with no visible signal at all.
    """
    drifted = {}
    for judge, base in baseline_agreement.items():
        cur = current_agreement.get(judge)
        if cur is None:
            drifted[judge] = {"status": "missing", "note": "judge not re-run on the gold set"}
            continue
        delta = round(cur - base, 4)
        if abs(delta) > threshold:
            drifted[judge] = {"baseline": base, "current": cur, "delta": delta,
                              "status": "DRIFT"}
    return {
        "threshold": threshold,
        "drifted": drifted,
        "quarantine_round": bool(drifted),
        "note": ("quarantine this round: at least one judge's agreement with human ground "
                 "truth moved beyond threshold, so scores are not comparable to previous rounds"
                 if drifted else "judges stable against the gold set"),
    }


# --------------------------------------------------------------------------
# Human ground truth
# --------------------------------------------------------------------------

def krippendorff_alpha_nominal(ratings: dict[str, dict[str, str]]) -> float | None:
    """Inter-rater reliability among the HUMANS, for nominal categories.

    `ratings[item][rater] = category`.

    This runs BEFORE any judge is validated. If the architects do not agree with
    each other on a dimension, no model judge can be validated against them —
    that dimension is not judgeable and belongs in commentary, not in the scored
    index. Skipping this step is what makes most evaluation programmes'
    judge-validation numbers meaningless.
    """
    units = [list(r.values()) for r in ratings.values() if len(r) > 1]
    if not units:
        return None

    categories = sorted({v for u in units for v in u})
    if len(categories) < 2:
        return 1.0

    do = 0.0
    total_pairs = 0
    for u in units:
        m = len(u)
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                total_pairs += 1
                if u[i] != u[j]:
                    do += 1
    do = do / total_pairs if total_pairs else 0.0

    allv = [v for u in units for v in u]
    n = len(allv)
    counts = {c: allv.count(c) for c in categories}
    de = 1.0 - sum((cnt / n) ** 2 for cnt in counts.values()) if n else 0.0
    de = de * n / (n - 1) if n > 1 else de
    if de == 0:
        return 1.0
    return round(1 - do / de, 4)


def judgeability_gate(alpha_by_dimension: dict[str, float | None],
                      floor: float = 0.67) -> dict[str, Any]:
    """Decide which dimensions are judgeable at all.

    0.67 is the conventional floor for tentative conclusions. Below it, a
    dimension goes to commentary rather than into the scored index — reporting a
    number nobody can reproduce is worse than reporting no number.
    """
    scored, commentary = [], []
    for dim, alpha in alpha_by_dimension.items():
        if alpha is not None and alpha >= floor:
            scored.append(dim)
        else:
            commentary.append({"dimension": dim, "alpha": alpha,
                               "reason": "human raters do not agree well enough for this to be "
                                         "judgeable by a model either"})
    return {"floor": floor, "scored_dimensions": scored, "commentary_only": commentary}

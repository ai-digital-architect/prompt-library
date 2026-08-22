"""Scoring: quality index, calibration, abstention, evidence.

Deliberate structure: the quality index blends ONLY the dimensions that describe
how well the model found and explained real problems. Calibration, abstention,
reliability and economics are reported beside it and never folded in.

That separation is not tidiness. Blending calibration into quality hides the
trade-off that matters most for routing: a slightly less accurate but
well-calibrated model is often the better production choice, because its
low-confidence output can be escalated automatically. A blended index makes that
model look simply worse.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .match import OVER_CLAIM_MULTIPLIER, MatchResult
from .resolve import ClaimReport, ResolutionReport

# Quality index weights. Part of SCORING_VERSION — changing them invalidates
# cross-round comparison until a backfill runs.
WEIGHTS = {
    "detection": 0.30,
    "evidence": 0.25,
    "root_cause": 0.15,
    "severity": 0.10,
    "completeness": 0.10,
    "remediation": 0.07,
    "communication": 0.03,
}

# Evidence sub-weights.
EV_W_RESOLUTION = 0.5
EV_W_VERIFIED = 0.4
EV_W_CONTRADICTED = 0.3   # subtracted

SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

# Reliability floor for calibration bins. Below this, a bin's accuracy is noise.
MIN_PER_BIN = 5


@dataclass
class Scores:
    detection_f_beta: float = 0.0
    precision: float | None = None     # None = undefined, not zero
    recall: float | None = None
    beta: float = 1.0
    evidence: float | None = None
    root_cause: float | None = None
    severity_agreement: float | None = None
    completeness: float = 0.0
    remediation: float | None = None
    communication: float | None = None
    quality_index: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k != "notes"} | {"notes": self.notes}


def evidence_score(res: ResolutionReport, claims: ClaimReport,
                   resolver_miss_rate: float = 0.0) -> float | None:
    """Evidence grounding.

    `resolver_miss_rate` is our own measured failure rate, subtracted so that our
    matcher's shortcomings do not silently become the model's score. It is
    published alongside the number rather than applied invisibly.
    """
    if res.referenced == 0 and claims.asserted == 0:
        # Nothing was claimed, so there is nothing to ground. This is the correct
        # response on a clean-file control; returning 0.0 would penalize it. The
        # dimension is dropped and the remaining weights renormalize.
        return None

    resolution = res.resolution_rate
    resolution = min(1.0, resolution + resolver_miss_rate)

    if claims.asserted:
        # UNKNOWN verdicts are excluded from the denominator entirely — a claim
        # the provider cannot decide is not evidence for or against the model.
        decidable = claims.verified_true + claims.contradicted
        verified = claims.verified_true / decidable if decidable else 0.0
        contradicted = claims.contradicted / decidable if decidable else 0.0
    else:
        verified = contradicted = 0.0

    raw = EV_W_RESOLUTION * resolution + EV_W_VERIFIED * verified - EV_W_CONTRADICTED * contradicted
    denom = EV_W_RESOLUTION + EV_W_VERIFIED
    return round(max(0.0, min(1.0, raw / denom)), 4)


def completeness_score(m: MatchResult, reported: int = 0) -> float:
    """Fraction of the oracle set that was found.

    An empty oracle is complete only if the model also reported nothing.
    Returning 1.0 unconditionally let a trial that `detection_score` had just
    scored 0.0 as a precision failure collect full completeness credit from the
    very same empty oracle.
    """
    if not m.oracle_total:
        return 1.0 if reported == 0 else 0.0
    return round(len(m.matched_oracle_ids) / m.oracle_total, 4)


def severity_agreement(findings: list[dict[str, Any]], oracle_findings: list[dict[str, Any]],
                       m: MatchResult) -> float | None:
    """Rank agreement between reported and oracle severity on matched findings.

    Spearman over the matched pairs. Returns None below three pairs, where a
    correlation coefficient is noise rather than a measurement.
    """
    oracle_by_id = {o.get("oracle_id"): o for o in oracle_findings}
    finding_by_id = {f.get("id"): f for f in findings}
    pairs = []
    for a in m.assignments:
        if a.tier in ("full", "located", "adjacent") and a.oracle_id:
            f = finding_by_id.get(a.finding_id)
            o = oracle_by_id.get(a.oracle_id)
            if not f or not o or not o.get("severity"):
                continue
            fr = SEVERITY_RANK.get(str(f.get("severity", "")).lower())
            orr = SEVERITY_RANK.get(str(o.get("severity", "")).lower())
            if fr is None or orr is None:
                continue
            pairs.append((fr, orr))
    if len(pairs) < 3:
        return None
    return round(_spearman([p[0] for p in pairs], [p[1] for p in pairs]), 4)


def _spearman(x: list[float], y: list[float]) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


# --------------------------------------------------------------------------
# Calibration — reported as its own axis
# --------------------------------------------------------------------------

@dataclass
class Calibration:
    brier: float | None = None
    ece: float | None = None
    discrimination_auc: float | None = None
    n: int = 0
    bins: list[dict[str, Any]] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {"brier": self.brier, "ece": self.ece,
                "discrimination_auc": self.discrimination_auc,
                "n": self.n, "bins_used": len(self.bins),
                "reliability_bins": self.bins, "note": self.note}


def calibration(pairs: list[tuple[float, bool]], bins: int = 10) -> Calibration:
    """Brier score, expected calibration error, and discrimination AUC.

    Discrimination is reported alongside calibration because a model can be
    perfectly calibrated and useless: always saying 0.5 on a balanced set is
    well-calibrated and carries no information. AUC catches that.
    """
    if not pairs:
        return Calibration()
    n = len(pairs)
    brier = sum((c - (1.0 if ok else 0.0)) ** 2 for c, ok in pairs) / n

    # Equal-mass bins, so a model that clusters its confidences does not get a
    # flattering ECE from mostly-empty bins.
    #
    # Partition by index rather than by a fixed chunk size. A fixed size both
    # over-produces bins (n=25, bins=10 gave 13) and, when n < bins, puts every
    # sample in its own bin — which makes ECE equal mean|conf-acc| and therefore
    # non-zero even for a perfectly calibrated pair. Confidence sets per trial are
    # typically 3-10 findings, so that was the common case, not the edge case.
    ordered = sorted(pairs, key=lambda p: p[0])
    # At least MIN_PER_BIN samples per bin. One sample per bin makes ECE equal
    # mean|conf - acc|, which is non-zero even for a perfectly calibrated set —
    # a measurement artifact, not miscalibration.
    nb = max(1, min(bins, n // MIN_PER_BIN))
    edges = [round(i * n / nb) for i in range(nb + 1)]
    ece = 0.0
    bin_rows = []
    for lo, hi in zip(edges, edges[1:]):
        chunk = ordered[lo:hi]
        if not chunk:
            continue
        conf = sum(c for c, _ in chunk) / len(chunk)
        acc = sum(1 for _, ok in chunk if ok) / len(chunk)
        ece += (len(chunk) / n) * abs(conf - acc)
        bin_rows.append({"n": len(chunk), "mean_confidence": round(conf, 4),
                         "accuracy": round(acc, 4), "gap": round(acc - conf, 4)})

    pos = [c for c, ok in pairs if ok]
    neg = [c for c, ok in pairs if not ok]
    auc = None
    if pos and neg:
        wins = sum(1 for p in pos for q in neg if p > q)
        ties = sum(1 for p in pos for q in neg if p == q)
        auc = round((wins + 0.5 * ties) / (len(pos) * len(neg)), 4)

    cal = Calibration(brier=round(brier, 4), ece=round(ece, 4),
                      discrimination_auc=auc, n=n, bins=bin_rows)
    if n < MIN_PER_BIN * 2:
        cal.note = (f"only {n} confidence value(s) — ECE over a single bin. Calibration "
                    f"is a per-model aggregate; read it across a suite, not per trial.")
    return cal


def isotonic_recalibration(pairs: list[tuple[float, bool]]) -> list[tuple[float, float]]:
    """Fit a monotone confidence map (pool-adjacent-violators) on the dev set.

    Published, not applied to the leaderboard: the leaderboard reports raw
    calibration, and the routing layer may apply this map. Applying it before
    scoring would let a badly-calibrated model borrow the fit's credit.
    """
    if not pairs:
        return []
    data = sorted(pairs, key=lambda p: p[0])
    xs = [c for c, _ in data]
    ys = [1.0 if ok else 0.0 for _, ok in data]
    w = [1.0] * len(ys)
    i = 0
    while i < len(ys) - 1:
        if ys[i] > ys[i + 1]:
            tot_w = w[i] + w[i + 1]
            avg = (ys[i] * w[i] + ys[i + 1] * w[i + 1]) / tot_w
            ys[i:i + 2] = [avg]
            w[i:i + 2] = [tot_w]
            xs[i:i + 2] = [xs[i]]
            i = max(0, i - 1)
        else:
            i += 1
    return [(round(x, 4), round(y, 4)) for x, y in zip(xs, ys)]


# --------------------------------------------------------------------------
# Abstention — a first-class correct answer
# --------------------------------------------------------------------------

@dataclass
class Abstention:
    abstained: int = 0
    correct_abstentions: int = 0
    over_claims: int = 0
    unanswerable_total: int = 0
    penalty: float = 0.0

    @property
    def abstention_precision(self) -> float | None:
        if not self.abstained:
            return None
        return round(self.correct_abstentions / self.abstained, 4)

    @property
    def over_claim_rate(self) -> float | None:
        if not self.unanswerable_total:
            return None
        return round(self.over_claims / self.unanswerable_total, 4)

    def to_dict(self) -> dict:
        return {
            "abstained": self.abstained,
            "correct_abstentions": self.correct_abstentions,
            "over_claims": self.over_claims,
            "unanswerable_total": self.unanswerable_total,
            "abstention_precision": self.abstention_precision,
            "over_claim_rate": self.over_claim_rate,
            "penalty": round(self.penalty, 4),
        }


def score_abstention(response: dict[str, Any], oracle: dict[str, Any],
                     questions: list[dict[str, Any]]) -> Abstention:
    """Reward correct abstention; penalize over-claiming at 1.5x a false positive.

    Two derived metrics keep this from being gamed. Abstention precision punishes
    a model that abstains everywhere; over-claim rate punishes one that answers
    everything. A model has to actually know which items are answerable.
    """
    ab = Abstention()
    answerable = {q["id"]: bool(q.get("answerable", True)) for q in questions}
    for oa in oracle.get("answers", []) or []:
        if oa.get("expected_abstention"):
            answerable[oa["question_id"]] = False
    ab.unanswerable_total = sum(1 for v in answerable.values() if not v)

    abstained_ids = {a.get("question_id") for a in (response.get("abstentions") or [])}
    ab.abstained = len(abstained_ids)
    for qid in abstained_ids:
        if qid in answerable and not answerable[qid]:
            ab.correct_abstentions += 1

    answered_ids = {a.get("question_id") for a in (response.get("answers") or [])}
    for qid, is_answerable in answerable.items():
        if not is_answerable and qid in answered_ids and qid not in abstained_ids:
            ab.over_claims += 1

    # Findings on a task the oracle marks wholly unanswerable are also over-claims.
    if oracle.get("answerable") is False and (response.get("findings") or []):
        ab.over_claims += len(response["findings"])
        ab.unanswerable_total = max(ab.unanswerable_total, len(response["findings"]))

    ab.penalty = ab.over_claims * OVER_CLAIM_MULTIPLIER
    return ab


# --------------------------------------------------------------------------
# Quality index
# --------------------------------------------------------------------------

def quality_index(s: Scores) -> float:
    """Weighted blend over the dimensions present.

    Dimensions with no grader available (root_cause, remediation and
    communication need the tribunal) are dropped and the remaining weights
    renormalized, so a run without judges produces a defensible index over what
    it actually measured instead of silently scoring those dimensions zero.
    """
    parts = {
        "detection": s.detection_f_beta,
        "evidence": s.evidence,
        "root_cause": s.root_cause,
        "severity": s.severity_agreement,
        "completeness": s.completeness,
        "remediation": s.remediation,
        "communication": s.communication,
    }
    total_w = 0.0
    acc = 0.0
    missing = []
    for k, v in parts.items():
        if v is None:
            missing.append(k)
            continue
        w = WEIGHTS[k]
        # Spearman is in [-1,1]; map to [0,1] before blending.
        val = (v + 1) / 2 if k == "severity" else v
        acc += w * max(0.0, min(1.0, val))
        total_w += w
    if missing:
        s.notes.append(
            "quality_index computed over available dimensions only; not graded: "
            + ", ".join(missing)
        )
    return round(100.0 * acc / total_w, 2) if total_w else 0.0


def detection_score(match: MatchResult, findings: list[dict[str, Any]],
                    beta: float, semantic_relations: dict[str, Any] | None,
                    notes: list[str]) -> tuple[float, float | None, float | None]:
    """Detection, with the two degenerate cases handled explicitly.

    An empty oracle is not one situation but three, and a naive F-score collapses
    all of them to zero:

      * A QUESTION-STYLE task (semantic suite) has no oracle findings at all —
        its checkable content is relations. Detection comes from relation recall
        penalized by hallucination on the deliberately-false relations. Scoring
        it as zero would make the entire semantic suite unusable.

      * A CLEAN-FILE CONTROL has an empty oracle on purpose: the correct answer
        is an empty findings array. Returning nothing earns full credit; inventing
        a finding earns none. This item is the whole reason over-claiming is
        measurable.

      * A genuinely empty oracle with reported findings is a precision failure.
    """
    if match.oracle_total > 0:
        return match.f_beta(beta), match.precision(), match.recall()

    if semantic_relations and semantic_relations.get("recall") is not None:
        recall = float(semantic_relations["recall"])
        halluc = semantic_relations.get("hallucination_rate")
        precision = 1.0 - float(halluc) if halluc is not None else 1.0
        if precision == 0 and recall == 0:
            f = 0.0
        else:
            b2 = beta * beta
            f = ((1 + b2) * precision * recall) / (b2 * precision + recall) if (precision or recall) else 0.0
        notes.append(
            "detection scored from oracle relations (question-style task): "
            f"{semantic_relations['true_relations_recalled']}/"
            f"{semantic_relations['true_relations_total']} true relations recalled, "
            f"{semantic_relations['false_relations_asserted']}/"
            f"{semantic_relations['false_relations_total']} false relations asserted."
        )
        return round(f, 4), round(precision, 4), round(recall, 4)

    if not findings:
        notes.append("empty oracle and empty finding set — correctly reported nothing. "
                     "Precision and recall are undefined here and are reported as null.")
        return 1.0, None, None

    notes.append(
        f"empty oracle but {len(findings)} finding(s) reported — scored as a precision failure. "
        f"This is the clean-file control working as intended. Precision and recall are "
        f"undefined over an empty oracle and are reported as null."
    )
    return 0.0, None, None


def score_trial(match: MatchResult, res: ResolutionReport, claims: ClaimReport,
                findings: list[dict[str, Any]], oracle_findings: list[dict[str, Any]],
                beta: float = 1.0, resolver_miss_rate: float = 0.0,
                tribunal_scores: dict[str, float] | None = None,
                semantic_relations: dict[str, Any] | None = None) -> Scores:
    t = tribunal_scores or {}
    notes: list[str] = []
    f_beta, precision, recall = detection_score(match, findings, beta, semantic_relations, notes)
    s = Scores(
        detection_f_beta=f_beta,
        precision=precision,
        recall=recall,
        beta=beta,
        evidence=evidence_score(res, claims, resolver_miss_rate),
        root_cause=t.get("root_cause"),
        severity_agreement=severity_agreement(findings, oracle_findings, match),
        completeness=completeness_score(match, reported=len(findings)),
        remediation=t.get("remediation"),
        communication=t.get("communication"),
    )
    s.notes.extend(notes)
    if match.unverifiable:
        s.notes.append(
            f"{match.unverifiable} reported finding(s) were unmatched but not refutable from "
            f"the corpus — excluded from precision rather than counted against the model."
        )
    if res.demoted_findings:
        s.notes.append(
            f"{len(res.demoted_findings)} finding(s) demoted for resting on multiple fuzzy "
            f"entity matches: {', '.join(res.demoted_findings[:5])}"
        )
    if claims.unknown:
        s.notes.append(
            f"{claims.unknown} claim(s) returned UNKNOWN from the evidence provider and were "
            f"excluded from the evidence denominator — a gap in our graph is not a model error."
        )
    s.quality_index = quality_index(s)
    return s

"""Finding matching and credit assignment.

Precision and recall require a defined notion of "the same finding", and v1 of
the approach document did not have one. Without it, F1 is not reproducible
across runs or reviewers, and the headline number of the whole benchmark rests
on an undefined term.

The rule implemented here:

A reported finding `r` matches a known finding `k` when all three hold:
  1. TYPE compatibility — same type, or within one level in the ontology
     (`sql_injection` matches `CWE-89`; `injection` matches it at partial credit)
  2. LOCATION overlap — resolved entity sets intersect, OR evidence line ranges
     overlap by at least one line
  3. CAUSAL agreement — the stated root cause is equivalent to the oracle's.
     Required for full credit; its absence yields partial credit.

Assignment is ONE-TO-ONE via maximum-weight bipartite matching. Without that, a
model can report the same oracle finding five different ways and harvest five
true positives — a degenerate strategy that would dominate the leaderboard.

`F_beta` rather than `F1`: beta is declared per suite. Security is recall-leaning
(a missed vulnerability costs more than a false alarm); controls is
precision-leaning (a false non-compliance finding carries real organizational
cost). Using one beta everywhere is a hidden policy choice, so it is made
explicit and versioned in the suite manifest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Credit tiers. These weights are part of SCORING_VERSION — changing them
# invalidates cross-round comparison until a backfill runs.
CREDIT = {
    "full": 1.0,
    "located": 0.6,      # right type and place, wrong causal story
    "adjacent": 0.3,     # right type, wrong place but same component
    "miss": 0.0,
}

FALSE_POSITIVE_COST = 1.0
SUSPECTED_FP_COST = 0.5      # an honest "I could not confirm this" costs less
OVER_CLAIM_MULTIPLIER = 1.5  # answering an item the oracle marks unanswerable


@dataclass
class Assignment:
    finding_id: str
    oracle_id: str | None
    tier: str
    credit: float
    reason: str = ""
    score: float = 0.0


@dataclass
class MatchResult:
    assignments: list[Assignment] = field(default_factory=list)
    true_positive_credit: float = 0.0
    false_positive_cost: float = 0.0
    unverifiable: int = 0
    oracle_total: int = 0
    matched_oracle_ids: set[str] = field(default_factory=set)

    def precision(self) -> float | None:
        """None when nothing was reported and nothing was refuted.

        Precision over an empty reported set is undefined, not zero. Persisting a
        hard 0 there drags every precision aggregate down with trials where the
        model correctly reported nothing.
        """
        denom = self.true_positive_credit + self.false_positive_cost
        return round(self.true_positive_credit / denom, 4) if denom > 0 else None

    def recall(self) -> float | None:
        """None when the oracle is empty — vacuous recall is not credit."""
        if not self.oracle_total:
            return None
        return round(self.true_positive_credit / self.oracle_total, 4)

    def f_beta(self, beta: float = 1.0) -> float:
        p = self.precision() or 0.0
        r = self.recall() or 0.0
        if p == 0 and r == 0:
            return 0.0
        b2 = beta * beta
        return round(((1 + b2) * p * r) / (b2 * p + r), 4)


# --------------------------------------------------------------------------
# Type ontology
# --------------------------------------------------------------------------

# Alias groups: members are treated as the SAME type. Kept small and explicit —
# a sprawling alias table quietly inflates recall.
_ALIASES = [
    {"cwe-89", "sql_injection", "sqli", "unparameterized_query"},
    {"cwe-79", "xss", "cross_site_scripting"},
    {"cwe-798", "hardcoded_credentials", "embedded_credentials"},
    {"cwe-22", "path_traversal", "directory_traversal"},
    {"cwe-502", "unsafe_deserialization", "insecure_deserialization"},
    {"cwe-862", "missing_authorization", "broken_authorization", "missing_authz"},
    {"cwe-306", "missing_authentication", "missing_authn"},
    {"missing_timeout", "no_timeout", "unbounded_call"},
    {"unbounded_retry", "no_retry_limit", "infinite_retry"},
    {"layer_violation", "layering_violation", "architecture_layer_violation"},
    {"cyclic_dependency", "circular_dependency", "dependency_cycle"},
    {"shared_datastore", "shared_database", "inappropriate_database_sharing"},
    {"single_az_dependency", "single_region_dependency", "no_redundancy"},
    {"shared_thread_pool", "missing_bulkhead", "no_isolation"},
]

# Parent categories: a member matches its parent at ADJACENT credit only.
_PARENTS = {
    "injection": {"cwe-89", "cwe-79", "sql_injection", "xss"},
    "authorization": {"cwe-862", "broken_authorization", "missing_authorization"},
    "resiliency": {"missing_timeout", "unbounded_retry", "shared_thread_pool",
                   "single_az_dependency"},
}


def _norm_type(t: str) -> str:
    return re.sub(r"[\s\-]+", "_", (t or "").strip().lower())


# The tables above are authored in human form ("CWE-89"); normalize them once at
# import so a table entry can never fail to match an incoming type purely because
# of punctuation. Without this, an ontology miss is indistinguishable from a model
# that failed to find the bug.
_ALIASES = [{_norm_type(x) for x in group} for group in _ALIASES]
_PARENTS = {_norm_type(k): {_norm_type(x) for x in v} for k, v in _PARENTS.items()}


def type_distance(a: str, b: str) -> float:
    """1.0 = same, 0.5 = one ontology level apart, 0.0 = unrelated."""
    na, nb = _norm_type(a), _norm_type(b)
    if na == nb:
        return 1.0
    for group in _ALIASES:
        if na in group and nb in group:
            return 1.0
    for parent, children in _PARENTS.items():
        if (na == parent and nb in children) or (nb == parent and na in children):
            return 0.5
    return 0.0


# --------------------------------------------------------------------------
# Location
# --------------------------------------------------------------------------

def _line_span(spec: str | None) -> tuple[int, int] | None:
    if not spec:
        return None
    if "-" in str(spec):
        lo, hi = str(spec).split("-", 1)
        try:
            return int(lo), int(hi)
        except ValueError:
            return None
    try:
        n = int(spec)
        return n, n
    except (ValueError, TypeError):
        return None


def location_overlap(finding: dict[str, Any], oracle: dict[str, Any],
                     resolved_nodes: list[str], tolerance: int = 0) -> tuple[bool, str]:
    oracle_entities = {_norm_type(e) for e in (oracle.get("entities") or [])}
    reported = {_norm_type(n) for n in resolved_nodes if n}
    reported |= {_norm_type(e.get("ref", "")) for e in (finding.get("entities") or [])
                 if isinstance(e, dict)}
    if oracle_entities & reported:
        return True, "entity intersection"
    # suffix match: PaymentClient.callGateway vs com.acme.PaymentClient.callGateway
    for oe in oracle_entities:
        for re_ in reported:
            if oe and re_ and (oe.endswith("." + re_) or re_.endswith("." + oe)):
                return True, "entity suffix match"

    for oev in (oracle.get("evidence") or []):
        ospan = _line_span(oev.get("lines"))
        ofile = (oev.get("file") or "").lower()
        for fev in (finding.get("evidence") or []):
            if not isinstance(fev, dict):
                continue
            ffile = (fev.get("file") or "").lower()
            if ofile and ffile and not (ofile.endswith(ffile) or ffile.endswith(ofile)):
                continue
            fspan = _line_span(fev.get("lines"))
            if ospan and fspan:
                lo = max(ospan[0], fspan[0]) - tolerance
                hi = min(ospan[1], fspan[1]) + tolerance
                if lo <= hi:
                    return True, "line range overlap"
            elif ofile and ffile:
                return True, "same file"
    return False, ""


# --------------------------------------------------------------------------
# Causal agreement
# --------------------------------------------------------------------------

def causal_agreement(finding: dict[str, Any], oracle: dict[str, Any]) -> bool:
    """Lexical agreement by default.

    This is the one dimension with no oracle, so it is where the tribunal earns
    its keep: when a judge panel is available, `judge_causal` overrides this. The
    lexical check is a floor that keeps the pipeline runnable without judges, not
    a claim that root-cause reasoning can be graded by keyword.
    """
    expected = [_norm_type(x) for x in (oracle.get("expected_root_cause") or [])]
    if not expected:
        return True     # nothing to disagree with
    text = _norm_type(finding.get("root_cause", "") + " " + finding.get("type", ""))
    for e in expected:
        toks = [t for t in e.split("_") if len(t) > 3]
        if not toks:
            continue
        if sum(1 for t in toks if t in text) >= max(1, len(toks) // 2):
            return True
    return False


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------

def _pair_score(finding, oracle, resolved_nodes, tolerance, judge_causal=None):
    td = type_distance(finding.get("type", ""), oracle.get("type", ""))
    if td == 0.0:
        return 0.0, "miss", "type mismatch"
    overlap, why = location_overlap(finding, oracle, resolved_nodes, tolerance)
    causal = judge_causal(finding, oracle) if judge_causal else causal_agreement(finding, oracle)

    if td == 1.0 and overlap and causal:
        return 1.0, "full", f"type+location({why})+cause"
    if td == 1.0 and overlap:
        return 0.6, "located", f"type+location({why}), causal disagreement"
    if td >= 0.5 and overlap:
        return 0.3, "adjacent", f"ontology-adjacent type, location({why})"
    if td == 1.0 and not overlap:
        return 0.3, "adjacent", "type match, location not confirmed"
    return 0.0, "miss", "insufficient agreement"


def _max_weight_assignment(pairs: list[tuple[float, int, int]]) -> list[tuple[int, int, float]]:
    """True maximum-weight one-to-one assignment (Jonker-Volgenant / Hungarian).

    Greedy descending is NOT optimal here and understates credit whenever two
    findings compete for one oracle: greedy takes a 1.0 and forfeits two 0.6s.
    Since `true_positive_credit` feeds both recall and cost-per-correct-finding,
    that understatement propagates into the headline economics.

    Implemented directly rather than via scipy — the matrices are tens on a side
    and a scientific stack is a heavy dependency for one function.
    """
    if not pairs:
        return []
    rows = sorted({fi for _, fi, _ in pairs})
    cols = sorted({oi for _, _, oi in pairs})
    ri = {r: i for i, r in enumerate(rows)}
    ci = {c: i for i, c in enumerate(cols)}
    w = {(ri[fi], ci[oi]): sc for sc, fi, oi in pairs}

    n, m = len(rows), len(cols)
    transposed = n > m
    if transposed:
        w = {(c, r): v for (r, c), v in w.items()}
        n, m = m, n

    INF = float("inf")
    cost = [[0.0] * m for _ in range(n)]
    for (r, c), v in w.items():
        cost[r][c] = -v                      # maximize weight == minimize cost

    u = [0.0] * (n + 1)
    v_ = [0.0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0
            for j in range(1, m + 1):
                if used[j]:
                    continue
                cur = cost[i0 - 1][j - 1] - u[i0] - v_[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v_[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    out: list[tuple[int, int, float]] = []
    for j in range(1, m + 1):
        if p[j] == 0:
            continue
        r, c = p[j] - 1, j - 1
        if transposed:
            r, c = c, r
        score = w.get((c, r) if transposed else (r, c), 0.0)
        if score > 0:
            out.append((rows[r], cols[c], score))
    return out


def match_findings(
    findings: list[dict[str, Any]],
    oracle_findings: list[dict[str, Any]],
    resolutions: dict[str, list[str]] | None = None,
    tolerance: int = 0,
    judge_causal=None,
    refuted: set[str] | None = None,
) -> MatchResult:
    """Align reported findings to oracle findings and assign credit.

    `refuted` names findings an evidence auditor actively refuted. Only refuted
    unmatched findings count against precision. An unmatched finding that cannot
    be refuted from the corpus is `unverifiable` — reported separately rather
    than counted as a false positive, because our oracle being incomplete is not
    the model's error.
    """
    resolutions = resolutions or {}
    refuted = refuted or set()
    result = MatchResult(oracle_total=len(oracle_findings))

    pairs: list[tuple[float, int, int]] = []
    meta: dict[tuple[int, int], tuple[str, str]] = {}
    for fi, f in enumerate(findings):
        nodes = resolutions.get(f.get("id", ""), [])
        for oi, o in enumerate(oracle_findings):
            score, tier, reason = _pair_score(f, o, nodes, tolerance, judge_causal)
            if score > 0:
                pairs.append((score, fi, oi))
                meta[(fi, oi)] = (tier, reason)

    assigned = _max_weight_assignment(pairs)
    matched_f = {fi for fi, _, _ in assigned}

    for fi, oi, score in assigned:
        tier, reason = meta[(fi, oi)]
        oid = oracle_findings[oi].get("oracle_id", f"O-{oi}")
        result.assignments.append(Assignment(
            finding_id=findings[fi].get("id", f"F-{fi}"),
            oracle_id=oid, tier=tier, credit=score, reason=reason, score=score))
        result.true_positive_credit += score
        result.matched_oracle_ids.add(oid)

    for fi, f in enumerate(findings):
        if fi in matched_f:
            continue
        fid = f.get("id", f"F-{fi}")
        if fid in refuted:
            cost = SUSPECTED_FP_COST if f.get("status") == "SUSPECTED" else FALSE_POSITIVE_COST
            result.false_positive_cost += cost
            result.assignments.append(Assignment(fid, None, "false_positive", -cost,
                                                 "refuted by evidence auditor"))
        else:
            result.unverifiable += 1
            result.assignments.append(Assignment(
                fid, None, "unverifiable", 0.0,
                "unmatched and not refutable from the corpus — excluded from precision"))

    for oi, o in enumerate(oracle_findings):
        oid = o.get("oracle_id", f"O-{oi}")
        if oid not in result.matched_oracle_ids:
            result.assignments.append(Assignment("—", oid, "miss", 0.0, "no reported finding matched"))

    result.true_positive_credit = round(result.true_positive_credit, 4)
    result.false_positive_cost = round(result.false_positive_cost, 4)
    return result

"""Failure disposition engine.

Every trial terminates in exactly one disposition. This module is short and it
is the most important file in the harness.

The reason: a naive harness treats any response it cannot parse as a wrong
answer. A safety refusal arrives as HTTP 200 with an empty-looking body, so it
gets scored as recall zero. Since the security suite is the one most likely to
trigger safety classifiers, and classifier coverage differs by vendor, that
single mistake produces a leaderboard that systematically ranks
classifier-bearing models lower on security — a wrong strategic conclusion drawn
from a parsing bug.

The counter-rule is that exclusions are always published. A model with a 30%
refusal rate on the security suite has a real, decision-relevant property.
Hiding it behind an exclusion is as misleading as scoring it zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Disposition(str, Enum):
    OK = "OK"
    REFUSAL_SAFETY = "REFUSAL_SAFETY"      # excluded from quality scoring, reported
    REFUSAL_POLICY = "REFUSAL_POLICY"      # scored as a miss, reported separately
    SCHEMA_INVALID = "SCHEMA_INVALID"      # scored as a miss
    TRUNCATED = "TRUNCATED"                # retry once, then scored as a miss
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"    # scored as a miss
    TIMEOUT = "TIMEOUT"                    # retry once, then scored as a miss
    RATE_LIMITED = "RATE_LIMITED"          # retried; never a capability failure
    PROVIDER_ERROR = "PROVIDER_ERROR"      # retried, then excluded
    HARNESS_ERROR = "HARNESS_ERROR"        # excluded; quarantine the run
    DRY_RUN = "DRY_RUN"                    # compiled and validated; never invoked


# Dispositions excluded from quality scoring entirely. Everything here is a
# statement about the harness or the provider, not about model capability.
EXCLUDED_FROM_SCORING = {
    Disposition.REFUSAL_SAFETY,
    Disposition.RATE_LIMITED,
    Disposition.PROVIDER_ERROR,
    Disposition.HARNESS_ERROR,
    Disposition.DRY_RUN,
}

# Dispositions that ARE the model's responsibility. Partial content is still
# graded — a truncated response that found the right bug before running out of
# room tells you something, and zeroing it would hide that. But none of these
# ever counts as a SUCCESS for pass@k / pass^k: an unusable response is not a
# success no matter what was in the fragment.
SCORED_AS_MISS = {
    Disposition.REFUSAL_POLICY,
    Disposition.SCHEMA_INVALID,
    Disposition.TRUNCATED,
    Disposition.BUDGET_EXCEEDED,
    Disposition.TIMEOUT,
}

RETRY_POLICY = {
    Disposition.RATE_LIMITED: {"max_retries": 5, "backoff_s": [2, 5, 15, 45, 120]},
    Disposition.PROVIDER_ERROR: {"max_retries": 2, "backoff_s": [3, 10]},
    Disposition.TIMEOUT: {"max_retries": 1, "backoff_s": [0]},
    Disposition.TRUNCATED: {"max_retries": 1, "backoff_s": [0], "raise_output_ceiling": True},
    # No SCHEMA_INVALID retry. A reprompt that appends "return valid JSON" edits
    # the request AFTER the fairness validator ran, so it would escape the
    # contract — and schema conformance is a property worth measuring rather than
    # coaching away. Repair happens in the normalizer, where it is recorded.

}


@dataclass
class DispositionResult:
    disposition: Disposition
    detail: str | None = None
    scored: bool = True
    retryable: bool = False

    def to_dict(self) -> dict:
        return {
            "disposition": self.disposition.value,
            "disposition_detail": self.detail,
            "scored": self.scored,
            "retryable": self.retryable,
        }


def classify(adapter, resp, *, schema_valid: bool | None = None,
             budget_exceeded: bool = False, harness_error: str | None = None) -> DispositionResult:
    """Assign a disposition. Order matters — the earliest matching rule wins."""

    if harness_error:
        return DispositionResult(Disposition.HARNESS_ERROR, harness_error,
                                 scored=False, retryable=False)

    # Transport-level outcomes first.
    if resp.status == 429:
        return DispositionResult(Disposition.RATE_LIMITED, "provider throttling",
                                 scored=False, retryable=True)
    if resp.status >= 500 or resp.status == 0:
        return DispositionResult(Disposition.PROVIDER_ERROR,
                                 resp.error or f"HTTP {resp.status}",
                                 scored=False, retryable=True)
    if resp.status in (401, 403):
        return DispositionResult(Disposition.HARNESS_ERROR,
                                 "authentication failed — check credentials, not the model",
                                 scored=False, retryable=False)
    if resp.status == 404:
        # A retired model looks exactly like this. It is not a capability failure.
        return DispositionResult(Disposition.PROVIDER_ERROR,
                                 "model or endpoint not found (retired model?)",
                                 scored=False, retryable=False)
    if resp.status == 400:
        # Almost always our bug: a rejected parameter, a malformed schema, a
        # stale adapter still sending sampling parameters.
        msg = _err_message(resp) or "bad request"
        return DispositionResult(Disposition.HARNESS_ERROR,
                                 f"HTTP 400 — likely a stale adapter: {msg}",
                                 scored=False, retryable=False)

    # A refusal can arrive as a perfectly successful HTTP 200.
    is_refusal, category = adapter.refusal(resp)
    if is_refusal:
        if _is_safety_category(category):
            return DispositionResult(Disposition.REFUSAL_SAFETY,
                                     f"category={category}", scored=False, retryable=False)
        # A scope or policy decline is the model's answer, not a classifier
        # intervention, so it is scored as a miss rather than excluded. Keeping
        # these apart matters: excluding them would let a model opt out of hard
        # tasks with no cost to its score.
        return DispositionResult(Disposition.REFUSAL_POLICY,
                                 f"category={category}", scored=True, retryable=False)

    if budget_exceeded:
        return DispositionResult(Disposition.BUDGET_EXCEEDED, "evidence budget exhausted",
                                 scored=True, retryable=False)

    if adapter.truncated(resp):
        return DispositionResult(Disposition.TRUNCATED, "output ceiling reached",
                                 scored=True, retryable=True)

    if schema_valid is False:
        return DispositionResult(Disposition.SCHEMA_INVALID,
                                 "response failed schema validation after repair attempts",
                                 scored=True, retryable=True)

    return DispositionResult(Disposition.OK, None, scored=True, retryable=False)


# Categories that indicate a safety classifier rather than a scope or policy
# decline. Matched loosely because vendors phrase these differently and the
# consequence of a miss is asymmetric: mislabelling a safety refusal as a policy
# one scores it as a miss, which is the failure this whole module exists to stop.
_SAFETY_MARKERS = (
    "safety", "harm", "cyber", "offensive", "weapon", "bio", "csam", "minor",
    "prohibited", "blocklist", "block", "violence", "sexual", "self_harm",
    "reasoning_extraction", "dangerous",
)


def _is_safety_category(category: str | None) -> bool:
    if not category:
        # Unattributed refusals default to SAFETY. Getting this wrong in the
        # other direction penalizes classifier-bearing models, which is the
        # expensive mistake.
        return True
    c = str(category).lower()
    return any(m in c for m in _SAFETY_MARKERS)


def _err_message(resp) -> str | None:
    e = resp.body.get("error")
    if isinstance(e, dict):
        return str(e.get("message"))[:300]
    if isinstance(e, str):
        return e[:300]
    return None


def exclusion_summary(dispositions: list[str]) -> dict:
    """Aggregate for the report. Never rendered without the scores beside it."""
    total = len(dispositions) or 1
    counts: dict[str, int] = {}
    for d in dispositions:
        counts[d] = counts.get(d, 0) + 1
    excluded = sum(counts.get(d.value, 0) for d in EXCLUDED_FROM_SCORING)
    return {
        "total_trials": len(dispositions),
        "counts": dict(sorted(counts.items())),
        "excluded": excluded,
        "excluded_rate": round(excluded / total, 4),
        "refusal_safety_rate": round(counts.get(Disposition.REFUSAL_SAFETY.value, 0) / total, 4),
        "schema_invalid_rate": round(counts.get(Disposition.SCHEMA_INVALID.value, 0) / total, 4),
        "budget_exceeded_rate": round(counts.get(Disposition.BUDGET_EXCEEDED.value, 0) / total, 4),
    }


def confidence_flag(excluded_rate: float, threshold: float = 0.10) -> str | None:
    """Quarantine marker for the leaderboard.

    Above the threshold, the surviving trials are a biased sample of the task set
    and the comparison should not be read as a clean ranking.
    """
    if excluded_rate > threshold:
        return "LOW_CONFIDENCE"
    return None

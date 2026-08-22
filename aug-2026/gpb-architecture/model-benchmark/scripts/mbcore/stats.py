"""Statistics: paired cluster bootstrap, pass@k / pass^k, frontiers, item analysis.

The single most common statistical error in model benchmarking is treating
repeated trials as independent samples. They are not: five trials of the same
task on the same model are correlated, and pooling them inflates the effective
sample size and therefore the significance of any difference.

So: the unit of resampling is the TASK. Trials are averaged within a task first,
and the bootstrap resamples tasks with replacement. Because every model sees the
same tasks, the comparison is paired, which is both more honest and far more
powerful than treating the two score sets as independent samples.

No numpy or scipy — the arithmetic here is simple and a benchmark harness should
not carry a scientific stack it barely uses.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------------------------
# Reliability
# --------------------------------------------------------------------------

def pass_at_k(successes_per_task: list[list[bool]], k: int = 1) -> float:
    """Fraction of tasks where at least one of the first k trials succeeded.

    "Can it succeed?" — the optimistic number, and the one usually quoted.
    """
    if not successes_per_task:
        return 0.0
    hits = sum(1 for trials in successes_per_task if any(trials[:k]))
    return round(hits / len(successes_per_task), 4)


def pass_hat_k(successes_per_task: list[list[bool]], k: int = 3) -> float | None:
    """Fraction of tasks where ALL of the first k trials succeeded.

    "Does it succeed predictably?" — the production-relevant number. A model with
    pass@1 of 0.9 and pass^3 of 0.4 is not a reliable component of a pipeline,
    and the mean alone would never show that.

    Returns None — not 0.0 — when no task has k trials. A study run at one trial
    cannot speak to pass^3, and printing 0.00 under prose that reads a low pass^k
    as unreliability would be a fabricated finding.
    """
    eligible = [t for t in successes_per_task if len(t) >= k]
    if not eligible:
        return None
    hits = sum(1 for trials in eligible if all(trials[:k]))
    return round(hits / len(eligible), 4)


def variance_profile(scores_per_task: list[list[float]]) -> dict[str, float]:
    """Mean, median, spread, and worst-case — because averaging 93/92/45/94/91
    hides the 45, and the 45 is what pages someone at 3am."""
    flat = [s for task in scores_per_task for s in task]
    if not flat:
        return {}
    per_task_means = [sum(t) / len(t) for t in scores_per_task if t]
    within = [_stdev(t) for t in scores_per_task if len(t) > 1]
    return {
        "mean": round(sum(flat) / len(flat), 4),
        "median": round(_median(flat), 4),
        "stdev_overall": round(_stdev(flat), 4),
        "mean_within_task_stdev": round(sum(within) / len(within), 4) if within else 0.0,
        "between_task_stdev": round(_stdev(per_task_means), 4) if len(per_task_means) > 1 else 0.0,
        "min_trial": round(min(flat), 4),
        "p10_trial": round(_percentile(flat, 10), 4),
    }


# --------------------------------------------------------------------------
# Paired cluster bootstrap
# --------------------------------------------------------------------------

@dataclass
class PairedComparison:
    model_a: str
    model_b: str
    mean_difference: float
    ci_low: float
    ci_high: float
    p_a_better: float
    n_tasks: int
    minimum_detectable_effect: float
    significant: bool
    note: str = ""

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def paired_cluster_bootstrap(
    a_by_task: dict[str, list[float]],
    b_by_task: dict[str, list[float]],
    model_a: str = "A",
    model_b: str = "B",
    resamples: int = 10000,
    ci: float = 0.95,
    seed: int = 20260822,
) -> PairedComparison:
    """Bootstrap the paired difference, resampling TASKS not trials."""
    shared = sorted(set(a_by_task) & set(b_by_task))
    if not shared:
        return PairedComparison(model_a, model_b, 0, 0, 0, 0.5, 0, 0, False,
                                "no shared tasks — not a valid comparison")

    diffs = []
    for t in shared:
        av = a_by_task[t]
        bv = b_by_task[t]
        if not av or not bv:
            continue
        diffs.append(sum(av) / len(av) - sum(bv) / len(bv))

    n = len(diffs)
    if n < 2:
        return PairedComparison(model_a, model_b, diffs[0] if diffs else 0, 0, 0, 0.5, n, 0,
                                False, "fewer than two shared tasks")

    rng = random.Random(seed)
    means = []
    for _ in range(resamples):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()

    alpha = (1 - ci) / 2
    lo = means[int(alpha * resamples)]
    hi = means[min(resamples - 1, int((1 - alpha) * resamples))]
    observed = sum(diffs) / n
    if all(d == 0 for d in diffs):
        # Identical scores on every task. P(A>B) = 0 would read as "A is certainly
        # worse"; the honest value for a tie is 0.5.
        p_better = 0.5
    else:
        p_better = sum(1 for m in means if m > 0) / resamples

    # Minimum detectable effect at 80% power for this design, so that a
    # "no significant difference" result is interpretable rather than ambiguous.
    sd = _stdev(diffs)
    mde = round(2.8 * sd / math.sqrt(n), 4) if n else 0.0

    significant = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)
    note = "" if significant else (
        f"difference not distinguishable from zero at {int(ci * 100)}% confidence. "
        f"With {n} tasks this design can only detect differences of about {mde:.3f} or larger."
    )

    return PairedComparison(
        model_a=model_a, model_b=model_b,
        mean_difference=round(observed, 4),
        ci_low=round(lo, 4), ci_high=round(hi, 4),
        p_a_better=round(p_better, 4), n_tasks=n,
        minimum_detectable_effect=mde, significant=significant, note=note,
    )


def benjamini_hochberg(pvalues: list[float], fdr: float = 0.05) -> list[bool]:
    """FDR control across the model x suite grid.

    A leaderboard runs dozens of simultaneous comparisons; at the 5% level a few
    will look significant by chance alone. Uncorrected values stay available —
    the correction is reported, not substituted.
    """
    n = len(pvalues)
    if not n:
        return []
    order = sorted(range(n), key=lambda i: pvalues[i])
    keep = [False] * n
    max_i = -1
    for rank, i in enumerate(order, 1):
        if pvalues[i] <= fdr * rank / n:
            max_i = rank
    for rank, i in enumerate(order, 1):
        if rank <= max_i:
            keep[i] = True
    return keep


# --------------------------------------------------------------------------
# Pareto frontiers and iso-budget interpolation
# --------------------------------------------------------------------------

@dataclass
class FrontierPoint:
    label: str
    cost: float
    quality: float
    latency_ms: float = 0.0
    config: dict[str, Any] = field(default_factory=dict)


def pareto_frontier(points: list[FrontierPoint]) -> list[FrontierPoint]:
    """Points not dominated on (lower cost, higher quality)."""
    front: list[FrontierPoint] = []
    for p in sorted(points, key=lambda x: (x.cost, -x.quality)):
        if not front or p.quality > front[-1].quality:
            front.append(p)
    return front


def interpolate_at_budget(front: list[FrontierPoint], budget: float) -> float | None:
    """Quality reachable at a given spend.

    Returns None when the frontier does not reach the budget point. A model that
    cannot operate at $0.05/task is reported ABSENT there — never extrapolated,
    because extrapolating a curve past its measured range is how a benchmark
    invents a capability nobody observed.
    """
    if not front:
        return None
    affordable = [p for p in front if p.cost <= budget]
    if not affordable:
        return None
    return round(max(p.quality for p in affordable), 4)


def iso_budget_table(frontiers: dict[str, list[FrontierPoint]],
                     budgets: list[float]) -> list[dict[str, Any]]:
    rows = []
    for model, front in sorted(frontiers.items()):
        row: dict[str, Any] = {"model": model}
        for b in budgets:
            q = interpolate_at_budget(front, b)
            row[f"${b:g}/task"] = q if q is not None else "absent"
        rows.append(row)
    return rows


# --------------------------------------------------------------------------
# Item analysis
# --------------------------------------------------------------------------

def item_statistics(scores_by_task_by_model: dict[str, dict[str, float]],
                    discrimination_floor: float = 0.15,
                    score_max: float = 1.0) -> list[dict[str, Any]]:
    """Difficulty and discrimination per item.

    An item every model passes, or every model fails, separates nothing: it costs
    money on every round and carries no information.

    `score_max` normalizes the incoming scale — quality index arrives in [0,100],
    and computing `1 - mean` on it produced difficulties like -93.87.

    Discrimination is the CORRECTED item-total correlation: the item's own score
    is removed from each model's total. Correlating an item against a total that
    contains it inflates discrimination and under-retires items, which is the
    opposite of what this analysis is for.
    """
    models = sorted({m for t in scores_by_task_by_model.values() for m in t})
    scale = score_max or 1.0
    totals = {m: 0.0 for m in models}
    for task_scores in scores_by_task_by_model.values():
        for m in models:
            totals[m] += task_scores.get(m, 0.0) / scale

    rows = []
    for task, task_scores in sorted(scores_by_task_by_model.items()):
        vals = [task_scores.get(m, 0.0) / scale for m in models]
        if not vals:
            continue
        difficulty = round(max(0.0, min(1.0, 1 - sum(vals) / len(vals))), 4)
        # corrected item-total: remove this item from each model's total
        tot = [totals[m] - task_scores.get(m, 0.0) / scale for m in models]
        disc = round(_pearson(vals, tot), 4) if len(models) > 2 else 0.0
        status = "active"
        if len(models) > 2 and abs(disc) < discrimination_floor:
            status = "regression"
        rows.append({
            "task": task,
            "observed_difficulty": difficulty,
            "discrimination": disc,
            "status": status,
            "note": ("separates nothing at the current roster — retire to the regression set"
                     if status == "regression" else ""),
        })
    return rows


def generalization_gap(dev_score: float, sealed_score: float) -> dict[str, Any]:
    """Development minus sealed. A widening gap means the programme is fitting
    its own benchmark, which is the failure mode a sealed set exists to catch."""
    gap = round(dev_score - sealed_score, 4)
    if gap > 8:
        verdict = "large — prompt/orchestration work is fitting the development set"
    elif gap > 3:
        verdict = "moderate — watch the trend across rounds"
    else:
        verdict = "small — development performance is generalizing"
    return {"development": dev_score, "sealed": sealed_score, "gap": gap, "verdict": verdict}


# --------------------------------------------------------------------------

def _median(v: list[float]) -> float:
    s = sorted(v)
    n = len(s)
    if not n:
        return 0.0
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def _stdev(v: list[float]) -> float:
    n = len(v)
    if n < 2:
        return 0.0
    m = sum(v) / n
    return math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))


def _percentile(v: list[float], p: float) -> float:
    if not v:
        return 0.0
    s = sorted(v)
    k = (len(s) - 1) * p / 100.0
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return s[int(k)]
    return s[lo] * (hi - k) + s[hi] * (k - lo)


def _pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else 0.0

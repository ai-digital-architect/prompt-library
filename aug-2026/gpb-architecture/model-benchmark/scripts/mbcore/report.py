"""Reporting.

A report that renders a ranking and nothing else is worse than no report: it
invites a decision the data may not support. So every rendering carries, in
order:

  1. a comparability statement — is this round comparable to the last one?
  2. the exclusions — dispositions, refusal rates, quarantine flags
  3. the frontiers and the iso-budget table
  4. the separate axes: calibration, abstention, economics, reliability
  5. the version block
  6. footnotes for derived profiles, imputed pricing and promotional pricing

If a section cannot be produced, the report says so rather than omitting it
silently. A missing section that looks like an absent problem is the failure
mode this whole design is trying to avoid.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .disposition import EXCLUDED_FROM_SCORING, Disposition, confidence_flag, exclusion_summary
from .stats import (
    FrontierPoint,
    item_statistics,
    iso_budget_table,
    paired_cluster_bootstrap,
    pareto_frontier,
    pass_at_k,
    pass_hat_k,
    variance_profile,
)


def build_report(grades: list[dict[str, Any]], manifests: list[dict[str, Any]],
                 study: dict[str, Any]) -> dict[str, Any]:
    """Aggregate graded trials into the report structure."""
    by_model: dict[str, list[dict]] = defaultdict(list)
    for g in grades:
        by_model[g["model_id"]].append(g)

    # Keyed on the run_id, which now carries the sweep point. Keying on
    # (model, task, trial) collapsed every effort rung of the same trial onto one
    # entry, so one rung's latency was handed to another rung's frontier point.
    manifest_by_run = {m.get("run_id"): m for m in manifests}

    models: dict[str, Any] = {}
    frontiers: dict[str, list[FrontierPoint]] = {}
    quality_by_task: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for model, gs in by_model.items():
        dispositions = [g.get("disposition", "OK") for g in gs]
        excl = exclusion_summary(dispositions)
        flag = confidence_flag(excl["excluded_rate"],
                               study.get("guards", {}).get("abort_on_exclusion_rate", 0.10))

        scored = [g for g in gs if g.get("scored", True)
                  and g.get("disposition") not in {d.value for d in EXCLUDED_FROM_SCORING}]

        per_task_scores: dict[str, list[float]] = defaultdict(list)
        per_task_success: dict[str, list[bool]] = defaultdict(list)
        for g in scored:
            q = (g.get("scores") or {}).get("quality_index", 0.0)
            per_task_scores[g["task_id"]].append(q)
            # Success requires a clean completion, not just a decent score on a
            # fragment: a truncated or schema-invalid response is unusable in
            # production regardless of what survived in it.
            clean = g.get("disposition") == "OK"
            per_task_success[g["task_id"]].append(
                clean and q >= study.get("success_threshold", 60.0))
            quality_by_task[g["task_id"]][model].append(q)

        cost_points: list[FrontierPoint] = []
        by_config: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
        for g in scored:
            econ = g.get("economics") or {}
            cost = econ.get("cold_cost_usd")
            q = (g.get("scores") or {}).get("quality_index")
            if cost is None or q is None:
                continue
            key = str(g.get("effort") or "default")
            if g.get("reasoning_mode"):
                key += f"+{g['reasoning_mode']}"
            m = manifest_by_run.get(g.get("run_id"))
            latency = ((m or {}).get("timing") or {}).get("wall_clock_ms") or 0
            by_config[key].append((cost, q, latency))
        for cfg, rows in by_config.items():
            n = len(rows)
            cost_points.append(FrontierPoint(
                label=f"{model}@{cfg}",
                cost=round(sum(r[0] for r in rows) / n, 6),
                quality=round(sum(r[1] for r in rows) / n, 3),
                latency_ms=round(sum(r[2] for r in rows) / n, 1),
                config={"effort": cfg},
            ))
        frontiers[model] = pareto_frontier(cost_points)

        tp = sum((g.get("matching") or {}).get("true_positive_credit", 0.0) for g in scored)
        total_cost = sum((g.get("economics") or {}).get("cold_cost_usd") or 0.0 for g in scored)

        models[model] = {
            "trials": len(gs),
            "scored_trials": len(scored),
            "exclusions": excl,
            "confidence_flag": flag,
            "quality": variance_profile(list(per_task_scores.values())),
            "pass_at_1": pass_at_k(list(per_task_success.values()), 1),
            "pass_hat_3": pass_hat_k(list(per_task_success.values()), 3),
            "calibration": _mean_axis(scored, "calibration", ["brier", "ece", "discrimination_auc"]),
            "abstention": _mean_axis(scored, "abstention",
                                     ["abstention_precision", "over_claim_rate"]),
            "resolution_rate": _mean_field(scored, "resolution", "resolution_rate"),
            "economics": {
                "total_cold_cost_usd": round(total_cost, 4),
                "cost_per_correct_finding": (round(total_cost / tp, 6) if tp > 0 else None),
                "credited_true_positives": round(tp, 3),
            },
            "flags": _cost_flags(scored),
            "frontier": [p.__dict__ for p in frontiers[model]],
        }

    budgets = study.get("iso_cost_points_usd_per_task", [0.05, 0.25, 1.00])
    iso = iso_budget_table(frontiers, budgets)

    comparisons = []
    names = sorted(models)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            av = {t: v[a] for t, v in quality_by_task.items() if a in v}
            bv = {t: v[b] for t, v in quality_by_task.items() if b in v}
            comparisons.append(paired_cluster_bootstrap(av, bv, a, b).to_dict())

    item_rows = item_statistics(
        {t: {m: sum(v) / len(v) for m, v in per_model.items() if v}
         for t, per_model in quality_by_task.items()},
        score_max=100.0,   # quality_index is 0-100; without this, difficulty came out negative
    )

    return {
        "study_id": study.get("study_id"),
        "models": models,
        "iso_budget_table": iso,
        "iso_cost_points": budgets,
        "paired_comparisons": comparisons,
        "item_analysis": item_rows,
        "versions": _version_block(manifests),
        "comparability": _comparability(manifests),
        "footnotes": _footnotes(manifests, models),
    }


def _mean_axis(grades: list[dict], section: str, fields: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for f in fields:
        vals = [(g.get(section) or {}).get(f) for g in grades]
        vals = [v for v in vals if isinstance(v, (int, float))]
        out[f] = round(sum(vals) / len(vals), 4) if vals else None
    return out


def _mean_field(grades: list[dict], section: str, field: str) -> float | None:
    vals = [(g.get(section) or {}).get(field) for g in grades]
    vals = [v for v in vals if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 4) if vals else None


def _cost_flags(grades: list[dict]) -> list[str]:
    flags: set[str] = set()
    for g in grades:
        for f in (g.get("economics") or {}).get("flags", []) or []:
            flags.add(f)
        if (g.get("economics") or {}).get("imputed_pricing"):
            flags.add("imputed")
        if (g.get("economics") or {}).get("promotional_pricing"):
            flags.add("promotional")
    return sorted(flags)


def _version_block(manifests: list[dict]) -> dict[str, Any]:
    seen: dict[str, set] = defaultdict(set)
    for m in manifests:
        for k, v in (m.get("versions") or {}).items():
            if v:
                seen[k].add(str(v))
    return {k: (sorted(v)[0] if len(v) == 1 else sorted(v)) for k, v in seen.items()}


def _comparability(manifests: list[dict]) -> dict[str, Any]:
    """Refuse to imply comparability the versions do not support."""
    critical = ["scoring", "matcher", "resolver", "response_schema"]
    versions = _version_block(manifests)
    mixed = [k for k in critical if isinstance(versions.get(k), list)]
    if mixed:
        return {
            "comparable_within_round": False,
            "reason": f"mixed versions within this round for: {', '.join(mixed)}. "
                      f"Re-run or backfill before comparing these trials to each other.",
        }
    return {
        "comparable_within_round": True,
        "cross_round_note": (
            "Comparable to a previous round only if that round used the same scoring, matcher, "
            "resolver and response_schema versions. If any differ, run a backfill first — "
            "`mb.py report` refuses a cross-version comparison unless --allow-incompatible is set."
        ),
    }


def _footnotes(manifests: list[dict], models: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    derived = sorted({m.get("model", {}).get("model_id") for m in manifests
                      if m.get("model", {}).get("derived_profile")})
    if derived:
        notes.append(
            f"Derived adapter profile — no dedicated upstream template exists for "
            f"{', '.join(x for x in derived if x)}. The profile is inherited from a sibling model "
            f"with a documented-identical API surface. Validate against vendor documentation "
            f"before treating these results as load-bearing."
        )
    for model, data in models.items():
        if "imputed" in data.get("flags", []):
            notes.append(f"{model}: cost figures use an IMPUTED price — no separately published "
                         f"rate was transcribed for this model.")
        if "promotional" in data.get("flags", []):
            notes.append(f"{model}: cost figures use PROMOTIONAL pricing and are not comparable "
                         f"to figures computed after the promotion expires.")
        if "long_prompt_surcharge" in data.get("flags", []):
            notes.append(f"{model}: at least one trial crossed the long-prompt threshold and was "
                         f"billed at the surcharged session rate.")
        if "stale_pricing" in data.get("flags", []):
            notes.append(f"{model}: the pricing table is older than its staleness window — "
                         f"re-verify against vendor pricing before quoting these figures.")
        if data.get("confidence_flag"):
            notes.append(f"{model}: {data['confidence_flag']} — excluded trial rate "
                         f"{data['exclusions']['excluded_rate']:.1%}; the surviving trials are a "
                         f"biased sample of the task set.")
        rr = data.get("resolution_rate")
        if rr is not None and rr < 0.7:
            notes.append(f"{model}: entity resolution rate {rr:.0%}. Low resolution can mean "
                         f"imprecise naming by the model OR gaps in our resolver — check "
                         f"grades.jsonl `resolution.unresolved_refs` before attributing it.")
    return notes


# --------------------------------------------------------------------------
# Markdown rendering
# --------------------------------------------------------------------------

def render_markdown(report: dict[str, Any]) -> str:
    L: list[str] = []
    a = L.append

    a(f"# Benchmark report — {report.get('study_id', 'untitled study')}")
    a("")

    comp = report.get("comparability", {})
    a("## Comparability")
    a("")
    if comp.get("comparable_within_round"):
        a("Within this round: **comparable** — every trial used one scoring, matcher, resolver "
          "and response-schema version.")
        a("")
        a(comp.get("cross_round_note", ""))
    else:
        a(f"**Not comparable.** {comp.get('reason')}")
    a("")

    a("## Exclusions")
    a("")
    a("Published before the scores, because a model that declines 30% of the security suite has "
      "a decision-relevant property that a ranking alone would hide.")
    a("")
    a("| Model | Trials | Scored | Excluded | Safety refusals | Schema invalid | Flag |")
    a("|---|---:|---:|---:|---:|---:|---|")
    for model, d in sorted(report["models"].items()):
        e = d["exclusions"]
        a(f"| {model} | {d['trials']} | {d['scored_trials']} | {e['excluded_rate']:.1%} | "
          f"{e['refusal_safety_rate']:.1%} | {e['schema_invalid_rate']:.1%} | "
          f"{d.get('confidence_flag') or '—'} |")
    a("")

    a("## Quality and reliability")
    a("")
    a("`pass^3` — all three trials succeeded — is the production-relevant number. A model with "
      "high `pass@1` and low `pass^3` is not a reliable pipeline component, and the mean hides it.")
    a("")
    a("| Model | Mean | Median | Worst trial | pass@1 | pass^3 | Entity resolution |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    scored_rows = [(m, d) for m, d in report["models"].items() if d.get("scored_trials")]
    unscored = [m for m, d in report["models"].items() if not d.get("scored_trials")]
    for model, d in sorted(scored_rows, key=lambda kv: -(kv[1]["quality"].get("mean") or 0)):
        q = d["quality"]
        rr = d.get("resolution_rate")
        a(f"| {model} | {_f1(q.get('mean'))} | {_f1(q.get('median'))} | "
          f"{_f1(q.get('min_trial'))} | {_f2(d['pass_at_1'])} | {_f2(d['pass_hat_3'])} | "
          f"{f'{rr:.0%}' if rr is not None else '—'} |")
    for model in sorted(unscored):
        a(f"| {model} | — | — | — | — | — | — |")
    a("")
    if unscored:
        a(f"_{', '.join(sorted(unscored))} had no scored trials — every attempt was excluded "
          f"(see the table above). No quality is reported rather than 0.0: a model that was "
          f"never measured is not a model that scored zero._")
        a("")
    if any(d.get("pass_hat_3") is None for _, d in scored_rows):
        a("_`pass^3` is blank where the study ran fewer than three trials per task. It is a "
          "statement this design cannot make, not a low score._")
        a("")

    a("## Iso-budget comparison")
    a("")
    a("Vendor effort labels are not a common scale, so headline comparisons are made at declared "
      "spend points on each model's measured cost/quality frontier. `absent` means the model's "
      "frontier does not reach that budget — never extrapolated.")
    a("")
    rows = report.get("iso_budget_table", [])
    if rows:
        cols = list(rows[0].keys())
        a("| " + " | ".join(cols) + " |")
        a("|" + "|".join(["---"] * len(cols)) + "|")
        for r in rows:
            a("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    else:
        a("_No frontier points — cost or quality was unavailable for every trial._")
    a("")

    a("## Economics")
    a("")
    a("Cold cost is the headline: the honest marginal cost of a genuinely new task. "
      "Cost per correct finding is the primary operational number.")
    a("")
    a("| Model | Cold cost (total) | Credited findings | Cost / correct finding | Flags |")
    a("|---|---:|---:|---:|---|")
    for model, d in sorted(report["models"].items()):
        if not d.get("scored_trials"):
            continue
        e = d["economics"]
        cpf = e.get("cost_per_correct_finding")
        a(f"| {model} | ${e['total_cold_cost_usd']:.4f} | {e['credited_true_positives']:.1f} | "
          f"{f'${cpf:.4f}' if cpf is not None else 'undefined (no correct findings)'} | "
          f"{', '.join(d.get('flags', [])) or '—'} |")
    a("")

    a("## Calibration and abstention")
    a("")
    a("Reported separately from quality on purpose. A slightly less accurate but well-calibrated "
      "model is often the better production choice, because its low-confidence output can be "
      "escalated automatically — blending these into one index hides exactly that trade-off.")
    a("")
    a("| Model | Brier ↓ | ECE ↓ | Discrimination AUC ↑ | Abstention precision ↑ | Over-claim rate ↓ |")
    a("|---|---:|---:|---:|---:|---:|")
    for model, d in sorted(report["models"].items()):
        c, ab = d["calibration"], d["abstention"]
        a(f"| {model} | {_f(c.get('brier'))} | {_f(c.get('ece'))} | "
          f"{_f(c.get('discrimination_auc'))} | {_f(ab.get('abstention_precision'))} | "
          f"{_f(ab.get('over_claim_rate'))} |")
    a("")

    a("## Paired comparisons")
    a("")
    a("Bootstrap resamples **tasks**, not trials — trials within a task are correlated and "
      "pooling them inflates significance. Every model saw the same tasks, so the comparison "
      "is paired.")
    a("")
    a("| A | B | Mean diff | 95% CI | P(A>B) | Tasks | MDE | Significant |")
    a("|---|---|---:|---|---:|---:|---:|---|")
    for cmp_ in report.get("paired_comparisons", []):
        a(f"| {cmp_['model_a']} | {cmp_['model_b']} | {cmp_['mean_difference']:+.2f} | "
          f"[{cmp_['ci_low']:+.2f}, {cmp_['ci_high']:+.2f}] | {cmp_['p_a_better']:.3f} | "
          f"{cmp_['n_tasks']} | {cmp_['minimum_detectable_effect']:.2f} | "
          f"{'yes' if cmp_['significant'] else 'no'} |")
    a("")
    nonsig = [c for c in report.get("paired_comparisons", []) if not c["significant"]]
    if nonsig:
        a(f"_{len(nonsig)} comparison(s) were not distinguishable from zero. That is a statement "
          f"about this design's power, not evidence the models are equivalent — see the MDE "
          f"column for the smallest difference this task count could detect._")
        a("")

    items = report.get("item_analysis", [])
    retire = [i for i in items if i["status"] == "regression"]
    if items:
        a("## Item analysis")
        a("")
        a(f"{len(items)} items analysed; **{len(retire)}** separate nothing at the current roster "
          f"(every model passes or every model fails). Retiring those to a cheap regression set "
          f"keeps the suite sharp and cuts cost with no information loss.")
        a("")
        if retire:
            a("| Item | Difficulty | Discrimination |")
            a("|---|---:|---:|")
            for i in retire[:20]:
                a(f"| {i['task']} | {i['observed_difficulty']:.2f} | {i['discrimination']:.2f} |")
            a("")

    a("## Versions")
    a("")
    for k, v in sorted(report.get("versions", {}).items()):
        a(f"- **{k}**: {v}")
    a("")

    notes = report.get("footnotes", [])
    if notes:
        a("## Footnotes")
        a("")
        for n in notes:
            a(f"- {n}")
        a("")

    return "\n".join(L)


def _f(v: Any) -> str:
    return f"{v:.3f}" if isinstance(v, (int, float)) else "—"


def _f1(v: Any) -> str:
    return f"{v:.1f}" if isinstance(v, (int, float)) else "—"


def _f2(v: Any) -> str:
    return f"{v:.2f}" if isinstance(v, (int, float)) else "—"

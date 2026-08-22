---
name: benchmark-planning
description: >
  Scope a model-benchmark study: which models, which lanes, how many trials, what
  it will cost, and what difference the design can actually detect. Load this
  before running anything — most wasted benchmark spend is decided at planning
  time, not at run time.
parent: model-benchmark
---

# Benchmark planning

The expensive mistakes in benchmarking are made before a single call is billed:
comparing models at incomparable settings, running too few tasks to detect the
difference you care about, or measuring a prompt when you meant to measure a
model. This subskill exists to get those decided deliberately.

## 1. Name the decision the study is meant to inform

Write it down first, in one sentence. It determines everything else.

| The decision | The design it needs |
| --- | --- |
| "Which model do we route security review to?" | One suite, deep effort sweep, iso-cost frontier, high trial count |
| "Is the new generation worth migrating to?" | Two models, all suites, paired comparison, generalization gap |
| "Does our code graph actually help?" | One model, uplift ladder, matched budget points |
| "Can we drop to a cheaper tier?" | Frontier over the tier ladder, `pass^k` rather than mean |
| "Is our prompt or the model the bottleneck?" | Parity **and** Optimized lanes, same tasks |

That last row is the one people skip. Running only the Optimized lane and finding
model A ahead of model B tells you nothing about whether A is better or whether
A's adapter is better. If the study is meant to inform a model choice, run Parity
too and report the gap between the lanes — that gap *is* the adapter's value.

## 2. Choose lanes

```
Parity      identical rendering, documented defaults, no sweep
Optimized   per-model adapter rendering, full effort sweep     ← headline lane
Production  optimized prompting inside the full platform
```

Parity is deliberately unflattering to every model and will understate all of
them, unevenly. Never publish it alone. Its job is to make Optimized-lane gains
attributable.

## 3. Choose models

`mb.py models list` shows the roster. Three flags change how a result must be read
and should be decided consciously, not discovered in the footnotes:

- **`derived`** — no upstream template exists; the adapter profile is inherited
  from a sibling model. Fine for a trend line, risky as the basis of a decision.
- **`retired`** — disabled by default. Include it only for historical continuity,
  and expect `PROVIDER_ERROR`.
- **`retention_posture: mandatory-30d`** — the provider will retain the corpus and
  offers no zero-data-retention arrangement. If the corpus contains proprietary
  code or seeded vulnerabilities, this is a compliance decision before it is a
  benchmarking one. See `references/security.md`.

## 4. Set effort policy — sweep, don't pick

```yaml
effort:
  policy: sweep
  spend_cap_usd_per_model: 40.00
```

`policy: fixed_default` is a trap that looks like fairness. Anthropic
`output_config.effort: "high"`, OpenAI `reasoning.effort: "high"` and Google
`thinking_level: "high"` are three unrelated scales, and the ladder shifts between
generations of the same family. Running everyone at `"high"` compares strings, not
capability.

The sweeper walks each ladder **cheapest-first**, so the spend cap truncates the
expensive end. That is deliberate: every model then has points at the low-cost end
of the frontier, which is where the `$0.05/task` iso-cost comparison actually
lands.

For GPT-5.6 Sol, `reasoning.mode` is a second, independent axis — declare it in
`effort.extra_axes`. It is not documented for Terra or Luna, and the adapter
refuses to set it there rather than risk a silent behavioural difference.

## 5. Size the study for the difference you care about

Trial count is the wrong knob to reach for first. Because the unit of statistical
resampling is the **task**, adding trials to a five-task suite barely moves the
detectable difference; adding tasks does.

Rules of thumb before running `mb.py plan`:

- **5 trials per configuration** is the floor. Sampling parameters no longer exist
  on any current generation, so run-to-run variance is irreducible and cannot be
  dialled down. That raises the value of repeated trials rather than lowering it.
- **20–50 tasks per suite** is where paired comparisons start to detect the
  differences that matter (a few points of quality index). Below ~15 tasks, expect
  most comparisons to come back "not distinguishable from zero" — which is a
  statement about your design, not about the models.
- The report prints a **minimum detectable effect** per comparison. Read it before
  the p-values. If the MDE is 12 points and you care about a 4-point difference,
  the study cannot answer your question no matter what it returns.

## 6. Estimate before committing

```bash
python3 mb.py plan --benchmark config/my-study.yaml --estimate
```

This expands the full trial matrix and prices it cold. Two things to check:

- **The total against `guards.max_total_spend_usd`.** A full sweep across eleven
  models multiplies fast: models × lanes × tasks × effort points × trials.
- **The flags column.** `imputed` means the price is inherited, not published.
  `promotional` means it expires. Both are footnoted in the report, but it is
  better to know before the run than after.

Then dry-run the fairness contract, which costs nothing:

```bash
python3 mb.py compile --suite suites/security-v1.yaml --all-models --dry-run
```

If the models do not share one `semantic_digest`, the study is not a comparison.
Fix that before spending anything.

## 7. Decide the iso-cost comparison points

```yaml
iso_cost_points_usd_per_task: [0.05, 0.25, 1.00]
```

Pick points that match real operating budgets rather than round numbers for their
own sake. A model whose frontier does not reach a point is reported **absent**
there — never extrapolated, because extrapolating past the measured range invents
a capability nobody observed.

## 8. Pre-flight

`mb.py plan` prints these; read them rather than scrolling past:

- missing credentials (a run will disposition as `HARNESS_ERROR`, not as a model failure)
- derived profiles in the roster
- retired models in the roster
- retention posture that needs a decision
- a stale pricing table
- the tribunal enabled before the human calibration set exists

That last one deserves care: enabling the judge panel before measuring
inter-rater reliability among your own experts produces numbers that look
rigorous and cannot be defended. `skills/judge-tribunal/SKILL.md` explains the
order.

## Output of this stage

A study YAML in version control next to the results, because the study definition
is part of the reproducibility record. Copy `config/benchmark.example.yaml` and
edit — it is annotated with the reasoning behind every field.

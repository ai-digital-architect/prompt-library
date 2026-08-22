---
name: reporting-and-routing
description: >
  Produce Pareto frontiers, iso-budget comparisons, code-graph uplift analysis and
  a model-routing policy from measured results. Covers what must appear beside
  every ranking, and how the benchmark becomes the routing control plane.
parent: model-benchmark
---

# Reporting and routing

A report that renders a ranking and nothing else is worse than no report: it
invites a decision the data may not support. Every rendering carries, in order,
the comparability statement, the exclusions, the frontiers, the separate axes, the
version block, and the footnotes.

## The order is not decoration

**1. Comparability.** Is this round comparable to the last one? A change to
scoring, matching, resolution or the response schema invalidates cross-version
comparison until a backfill runs. `mb.py report` refuses to render such a
comparison unless `--allow-incompatible` is passed, and then labels it.

**2. Exclusions, before the scores.** A model that declines 30% of the security
suite has a decision-relevant property that a ranking alone hides. Above 10%
exclusion the suite is flagged `LOW_CONFIDENCE`: the surviving trials are a biased
sample and the ranking over them is not clean.

**3. Quality and reliability together.** `pass^3` is the production number. A model
at pass@1 0.90 and pass^3 0.40 is not a reliable pipeline component, and the mean
conceals it entirely.

**4. Iso-budget, not effort labels.** Vendor effort names are three unrelated
scales. Headline comparisons are made at declared spend points on each model's
measured cost/quality frontier. A model whose frontier does not reach a point is
reported **absent** — never extrapolated, because extrapolating past the measured
range invents a capability nobody observed.

**5. Economics with cold cost as the headline.** Cold is the honest marginal cost
of a genuinely new task. Warm (cached) cost is an operational secondary number;
leading with warm makes every model look cheaper than it is for novel work.
**Cost per correct finding** is the primary operational metric.

**6. Calibration and abstention as their own axes.** Never blended into quality.

**7. Paired comparisons with the minimum detectable effect.** Read the MDE before
the p-values: "not significant" with an MDE of 12 points on a 4-point question
means the design could not answer, not that the models are equal.

## Reading a frontier

```
QUALITY
  ^
  |            ● A@xhigh
  |      ● A@high
  |   ● A@medium         ● B@high
  | ● A@low        ● B@medium
  +--------------------------------> COST
```

Three questions the frontier answers that a single number cannot:

- **Where does a model stop improving?** A flat top means paying for more effort
  buys nothing — the most actionable single fact in a benchmark round.
- **Where do two models cross?** Often a cheaper model wins below a budget and
  loses above it, which is a routing rule rather than a ranking.
- **Which points exist at all?** Absence at `$0.05/task` is information: that model
  cannot operate at that budget.

## Code-graph uplift

The strategically most valuable experiment this harness supports, and the one that
benchmarks your architecture rather than your vendors:

```
model only
model + raw repository / naive RAG
model + semantic code graph
model + graph + multi-agent orchestration
```

The result to look for is the shape, not the winner:

```
Model A + graph = 92        Model A alone = 69
Model B + graph = 90        The platform contributes +23; model choice +2.
```

**Uplift must be measured at matched budget points**, or the richer configuration
wins simply by spending more, and the number tells you nothing.

## From leaderboard to routing control plane

```bash
python3 mb.py route --run-dir runs/<run_id>
```

The routing policy is derived from measured frontiers rather than from effort
labels or overall rank:

```yaml
routing_policy_version: "1.0.0"
derived_from_round: "2026-08-R3"
rules:
  - budget_usd_per_task: 0.25
    primary: <best on this suite's frontier at $0.25>
    escalate_when: "calibrated confidence below 0.55"
    escalate_to: <best at $1.00>
    abstain_route: human_review
```

Three properties of the measurement make this policy specific rather than
hand-wavy:

- **Calibration** gives a defensible escalation threshold. Without it, "escalate
  on low confidence" is meaningless because raw confidences are not comparable
  across models.
- **Abstention precision** tells you whether a model's "I don't know" is
  trustworthy enough to route to a human rather than to a bigger model.
- **`pass^k`** tells you whether the primary model is reliable enough to run
  unattended at all.

Re-derive the policy whenever scoring, matching, resolution or the response schema
changes. A policy derived under one scoring version is not valid under another.

## What to say when the result is inconclusive

Report it as inconclusive, with the MDE. A benchmark that always produces a
ranking is a benchmark that produces rankings from noise, and the first time
someone acts on one and it does not hold, the whole programme loses its standing.

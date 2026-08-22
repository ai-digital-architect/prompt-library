# Statistics

## The error that matters most

Treating repeated trials as independent samples. Five trials of the same task on
the same model are correlated; pooling them inflates the effective sample size and
therefore the apparent significance of every difference.

So: **the unit of resampling is the task.** Trials are averaged within a task
first, and the bootstrap resamples tasks with replacement.

## Paired cluster bootstrap

Every model sees the same tasks, so the comparison is paired — both more honest
and far more powerful than treating two score sets as independent samples.

```
for each task t:  d_t = mean(A scores on t) - mean(B scores on t)
resample tasks with replacement, 10,000 times
report: mean difference, 95% CI, P(A > B), n_tasks
```

Reported as:

```
Model A vs Model B
mean difference: +4.7
95% CI: [+3.2, +6.1]
P(A > B): 0.978
tasks: 42
```

rather than `A = 91, B = 87`, which asserts a difference the data may not support.

## Minimum detectable effect

Published per comparison. **Read it before the p-values.**

```
MDE ≈ 2.8 * sd(paired differences) / sqrt(n_tasks)
```

"Not significant" with an MDE of 12 points on a question you care about at 4
points means the study could not answer it. That is a design fact, not a finding,
and reporting it as "the models are equivalent" is the most common way a benchmark
misleads its own sponsors.

The practical implication: **add tasks, not trials.** Trials reduce within-task
noise; tasks reduce the standard error of the comparison. Going from 3 to 10
trials on a 5-task suite barely moves the MDE.

## Trial count

Five per configuration is the floor. Because sampling parameters no longer exist
on any current generation, run-to-run variance is irreducible and cannot be dialled
down — which raises the value of repeated trials rather than lowering it, and
makes `seed` useless as a reproducibility lever. The run manifest records
`sampling: "not-applicable"` rather than implying determinism the platform cannot
deliver.

## pass@k and pass^k

| Metric | Question | Use |
| --- | --- | --- |
| `pass@k` | Can it succeed within k attempts? | Optimistic; the number usually quoted |
| `pass^k` | Does it succeed on all k attempts? | **Production-relevant** |

A model at pass@1 0.90 and pass^3 0.40 is not a reliable pipeline component. The
mean conceals this entirely: 93, 92, 45, 94, 91 averages to 83, and the 45 is what
pages someone at 3am. The variance profile also reports the minimum and p10 trial
for the same reason.

A trial counts as a success only if it completed cleanly (`disposition: OK`) **and**
cleared the quality threshold. A truncated or schema-invalid response is unusable
in production regardless of what survived in the fragment.

## Multiple comparisons

A leaderboard runs dozens of simultaneous comparisons; at the 5% level a few look
significant by chance. Benjamini–Hochberg FDR control is applied across the
model × suite grid, with uncorrected values still available. The correction is
reported, not substituted — a reader should be able to see both.

## Item analysis

Per item, after each round:

- **observed difficulty** = 1 − mean credited score across models
- **discrimination** = point-biserial correlation between item score and total score

An item every model passes or every model fails separates nothing. It costs money
every round and carries no information. Below ~0.15 discrimination it moves to a
regression set: still run cheaply to catch regressions, excluded from the headline
index.

This is how a suite gets sharper rather than merely longer.

## Generalization gap

```
gap = development score − sealed score
```

Published beside every headline number. A widening gap across rounds is the signal
that prompt and orchestration work is fitting the development set — and it is the
only reliable signal you get, which is why the sealed set is worth its overhead.

| Gap | Reading |
| ---: | --- |
| ≤ 3 | development performance is generalizing |
| 3–8 | moderate; watch the trend |
| > 8 | the programme is fitting its own benchmark |

## What not to do

- **Do not compare token counts across providers.** Tokenizers differ materially —
  Claude Sonnet 5 emits roughly 30% more tokens than Sonnet 4.6 for identical
  text. Compare cost and wall-clock; report tokens only within a family.
- **Do not compare at effort labels.** `high` is three unrelated scales. Compare
  at iso-cost and iso-latency points on a measured frontier.
- **Do not extrapolate a frontier.** A model that cannot reach a budget point is
  reported absent there. Extrapolating past the measured range invents a
  capability nobody observed.
- **Do not average across suites without saying so.** Suites use different betas
  and different oracles; a grand mean is a weighting choice masquerading as a
  measurement.

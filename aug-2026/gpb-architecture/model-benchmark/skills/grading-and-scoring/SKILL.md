---
name: grading-and-scoring
description: >
  Turn raw model responses into defensible scores: normalize, resolve entities,
  verify claims against the code graph, match findings to oracles, and compute
  quality, calibration, abstention, reliability and economics as separate axes.
parent: model-benchmark
---

# Grading and scoring

```
normalize → resolve entities → verify claims → match findings → score → statistics
```

Each stage has one job and one failure mode worth understanding, because each is a
place where a bug looks exactly like a model weakness.

## 1. Normalize

Parse the response and validate it against the findings schema. Recovery from a
markdown fence or a leading sentence is legitimate — that is a transport artifact,
not a capability signal.

The repair path is deliberately narrow: strip fences, take the outermost JSON
object, coerce obvious type slips. It never **adds** content. A repair that
manufactures a finding, an entity or a confidence value would destroy both the
schema-conformance metric and every score it feeds.

**First-pass schema validity is published per model.** It is a real production
property: a model that needs a repair pass on 20% of calls is a different
engineering proposition from one that does not.

## 2. Resolve entities

Every `ref` a model emits is resolved against the evidence provider through a
ladder that is generous about presentation and strict about identity:

| Rung | Rule | Result |
| --- | --- | --- |
| R0 | exact fully-qualified match | EXACT |
| R1 | normalized FQN (separators, signatures stripped) | EXACT |
| R2 | simple name + enclosing type, unique | EXACT |
| R3 | simple name unique in corpus | EXACT |
| R4 | ambiguous name, disambiguated by the finding's evidence file | EXACT |
| R5 | file + line range intersects exactly one symbol | LOCATED |
| R6 | fuzzy match above threshold, single candidate | FUZZY |
| — | anything else | UNRESOLVED |

Two rules keep this honest:

- **More than one FUZZY match in a finding demotes it to UNRESOLVED.** Identity
  resting on several near-misses is not identity.
- **UNRESOLVED is reported separately from WRONG.** A model that names a real
  thing imprecisely, one that invents a symbol, and a resolver bug are three
  different situations. Collapsing them lets our own matcher's failures disappear
  into the model's score, which makes evidence grounding unfalsifiable.

Resolution rate is published per model. A model that names entities loosely is
genuinely less useful in an automated pipeline — but before attributing a low
rate to the model, read `resolution.unresolved_refs` in `grades.jsonl`. It is
often the resolver.

## 3. Verify claims

Relations the model asserted are checked against the evidence provider, which
returns TRUE, FALSE or **UNKNOWN**.

UNKNOWN is excluded from the evidence denominator entirely. A provider that cannot
decide has produced no evidence, and treating "we don't know" as "the model was
wrong" quietly converts every gap in our own graph into an apparent model
weakness. The bundled `local_graph` provider uses UNKNOWN freely and deliberately.

Absence claims (`negated: true` — "no timeout is configured") are verified the
same way, but only for predicates the provider can actually decide. Answering
FALSE from ignorance is the fastest way to make a benchmark lie.

## 4. Match findings

Precision and recall need a defined notion of "the same finding". A reported
finding matches a known one when all three hold:

1. **type compatibility** — same type, or one level apart in the ontology
2. **location overlap** — resolved entity sets intersect, or evidence line ranges
   overlap by at least one line
3. **causal agreement** — the stated root cause matches the oracle's

Assignment is **one-to-one** via maximum-weight bipartite matching. Without that, a
model can report one oracle finding five different ways and harvest five true
positives — a degenerate strategy that would dominate any leaderboard.

Credit tiers:

| Tier | Conditions | Credit |
| --- | --- | ---: |
| full | type + location + cause | 1.0 |
| located | type + location, causal disagreement | 0.6 |
| adjacent | ontology-adjacent type, or type match without confirmed location | 0.3 |
| miss | no match | 0.0 |
| false positive | unmatched **and refuted** by the evidence auditor | −1.0 (−0.5 if `SUSPECTED`) |
| unverifiable | unmatched and not refutable from the corpus | excluded from precision, reported separately |

That last row matters. An unmatched finding that cannot be refuted means **our
oracle is incomplete**, not that the model was wrong. Counting it as a false
positive would punish models for finding things we did not know about — which is
precisely the capability worth having.

### Two degenerate cases the scorer handles explicitly

- **Question-style tasks** (the semantic suite) have no oracle findings at all.
  Detection comes from relation recall penalized by hallucination on the
  deliberately-false relations. A naive F-score would return zero and make the
  whole suite unusable.
- **Clean-file controls** have an empty oracle on purpose. Returning nothing earns
  full credit; inventing a finding earns none.

## 5. Score — separate axes, deliberately

The quality index blends **only** the dimensions describing how well the model
found and explained real problems:

| Dimension | Weight | Grader |
| --- | ---: | --- |
| Detection (F_beta) | 30% | deterministic + graph |
| Evidence grounding | 25% | graph |
| Root-cause reasoning | 15% | tribunal |
| Severity agreement | 10% | deterministic (Spearman vs oracle) |
| Completeness | 10% | deterministic |
| Remediation | 7% | tribunal |
| Communication | 3% | tribunal |

Dimensions with no grader available are **dropped and the remaining weights
renormalized** — a run without judges produces a defensible index over what it
actually measured rather than silently scoring three dimensions zero. The grade
records which dimensions were not graded.

Reported **alongside, never blended in**:

- calibration (Brier, ECE, discrimination AUC)
- abstention precision and over-claim rate
- schema conformance
- refusal rate by category
- reliability (pass@k, pass^k, variance)
- economics

Blending calibration into quality hides the trade-off that matters most for
routing: a slightly less accurate but well-calibrated model is often the better
production choice, because its low-confidence output can be escalated
automatically. A blended index makes that model look simply worse.

## 6. Statistics

- **Resample tasks, not trials.** Five trials of one task are correlated; pooling
  them inflates the effective sample size and therefore significance.
- **Paired cluster bootstrap** — every model sees the same tasks, so the
  comparison is paired, which is both more honest and far more powerful.
- **pass@k and pass^k both.** pass^k is the production number: a model at pass@1
  0.90 and pass^3 0.40 is not a reliable pipeline component and the mean hides it.
- **Minimum detectable effect is published per comparison.** Read it before the
  p-values. "Not significant" with an MDE of 12 points on a 4-point question means
  the study could not answer, not that the models are equal.
- **Benjamini–Hochberg** across the model × suite grid, with uncorrected values
  still available.

## Re-grading after a scoring change

Grades are derived, never edited in place. Re-run in replay mode into a new run
directory and diff the reports:

```bash
python3 mb.py run --benchmark config/my-study.yaml --replay --run-dir runs/regrade-v2
python3 mb.py report --run-dir runs/regrade-v2
```

And note: changing scoring, matching, resolution or the response schema
invalidates comparison against earlier rounds until they are backfilled. The
report refuses to render such a comparison unless `--allow-incompatible` is
passed. See `skills/change-management/`.

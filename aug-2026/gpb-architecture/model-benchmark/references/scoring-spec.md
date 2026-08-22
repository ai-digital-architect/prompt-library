# Scoring specification

Normative. Everything here is versioned as `SCORING_VERSION` / `MATCHER_VERSION` /
`RESOLVER_VERSION`; changing any of it invalidates cross-round comparison until a
backfill runs.

## 1. Dispositions

Every trial ends in exactly one. This table is the most important one in the
document.

| Disposition | Trigger | Scored? | Counts as success? |
| --- | --- | --- | --- |
| `OK` | valid, schema-conformant, within budget | yes | if above threshold |
| `REFUSAL_SAFETY` | provider safety decline, including HTTP 200 with a refusal stop reason | **no — excluded** | no |
| `REFUSAL_POLICY` | scope decline unrelated to safety classifiers | yes | no |
| `SCHEMA_INVALID` | fails validation after declared repair attempts | yes, on what parsed | no |
| `TRUNCATED` | output ceiling reached | yes, after one retry at a higher ceiling | no |
| `BUDGET_EXCEEDED` | evidence or token budget exhausted | yes | no |
| `TIMEOUT` | wall-clock exceeded | yes, after one retry | no |
| `RATE_LIMITED` | throttling | **no — excluded**, retried | no |
| `PROVIDER_ERROR` | 5xx, transport, 404 on a retired model | **no — excluded** | no |
| `HARNESS_ERROR` | our bug, auth failure, HTTP 400 | **no — excluded**, run quarantined | no |

Two rules:

- **Exclusions are always published**, with refusal categories. A 30% refusal rate
  on the security suite is a decision-relevant property; hiding it behind an
  exclusion is as misleading as scoring it zero.
- **Above 10% exclusion, the suite comparison is flagged `LOW_CONFIDENCE`** — the
  surviving trials are a biased sample of the task set.

## 2. Entity resolution

| Rung | Rule | Kind |
| --- | --- | --- |
| R0 | exact node id | EXACT |
| R1 | normalized FQN (separators unified, signature stripped) | EXACT |
| R2 | simple name + enclosing type, unique | EXACT |
| R3 | simple name unique in corpus | EXACT |
| R4 | ambiguous name disambiguated by the finding's evidence file | EXACT |
| R5 | evidence file + line range intersects exactly one symbol | LOCATED |
| R6 | fuzzy ≥ 0.88 with a single candidate | FUZZY |
| — | otherwise | UNRESOLVED |

- More than **one** FUZZY match within a finding demotes it to UNRESOLVED.
- UNRESOLVED is reported separately from wrong.
- `resolution_rate` is published per model, with `unresolved_refs` in the grade so
  a low rate can be attributed to the model or to the resolver rather than assumed.

## 3. Claim verification

Relations return TRUE / FALSE / **UNKNOWN**. UNKNOWN is excluded from the evidence
denominator: a provider that cannot decide has produced no evidence, and counting
it against the model converts a gap in our graph into an apparent hallucination.

Negated relations (absence claims — "no timeout configured") are verified the same
way, and only for predicates the provider can actually decide.

## 4. Finding matching

`r` matches `k` when all three hold:

1. **Type compatibility** — identical, an alias-group member, or one ontology level
   apart (parent ↔ child).
2. **Location overlap** — resolved entity sets intersect (including suffix match),
   or evidence line ranges overlap by ≥ 1 line, or same file when line data is absent.
3. **Causal agreement** — stated root cause matches the oracle's expected causes.
   Lexical by default; overridden by the evidence auditor when the tribunal runs.

Assignment is **one-to-one**, maximum-weight. Without it, one oracle finding
reported five ways yields five true positives.

### Credit tiers

| Tier | Conditions | Credit |
| --- | --- | ---: |
| full | type + location + cause | 1.0 |
| located | type + location, causal disagreement | 0.6 |
| adjacent | ontology-adjacent type + location, or exact type without confirmed location | 0.3 |
| miss | no match | 0.0 |
| false positive | unmatched **and refuted** | −1.0 (−0.5 if `status: SUSPECTED`) |
| unverifiable | unmatched, not refutable from the corpus | excluded from precision |

**Unverifiable is not a false positive.** An unmatched finding that cannot be
refuted means our oracle is incomplete, not that the model was wrong. Counting it
against the model would punish exactly the capability worth having.

`SUSPECTED` costs half a false positive. An honest "I could not confirm this"
should not cost as much as a confident fabrication.

### Degenerate cases

| Case | Handling |
| --- | --- |
| Oracle has findings | standard F_beta |
| Oracle has no findings but has relations (question-style) | detection = F_beta over relation recall, precision = 1 − hallucination rate |
| Oracle empty, model reported nothing (clean-file control) | detection = 1.0 |
| Oracle empty, model reported findings | detection = 0.0 — precision failure |

## 5. F_beta per suite

| Suite | beta | Rationale |
| --- | ---: | --- |
| security | 1.5 | recall-leaning; a missed vulnerability costs more than a false alarm |
| resiliency | 1.2 | mildly recall-leaning |
| semantic, architecture | 1.0 | balanced |
| controls | 0.7 | precision-leaning; a false non-compliance finding pulls a control owner into an investigation that finds nothing |

Declared in the suite manifest and versioned, because one beta everywhere is a
hidden policy choice.

## 6. Abstention

| Oracle | Model answers | Model abstains |
| --- | --- | --- |
| answerable | scored normally | miss, penalized **less** than a confident wrong answer |
| insufficient evidence | **over-claim**, penalized at 1.5× a normal false positive | **full credit** |

Two derived metrics, both required to prevent gaming:

- **over-claim rate** — punishes a model that answers everything
- **abstention precision** — punishes a model that abstains everywhere

`INSUFFICIENT_EVIDENCE` is a first-class correct answer, not a failure to answer.

## 7. Calibration

Reported as its own axis, never blended into quality.

- **Brier score** over per-finding confidence vs. verified correctness
- **ECE** over 10 equal-mass bins (equal-mass, so a model that clusters its
  confidences does not get a flattering number from mostly-empty bins)
- **Discrimination AUC** — because a model can be perfectly calibrated and useless:
  always saying 0.5 on a balanced set is well-calibrated and carries no signal
- **Reliability diagram** per model per suite
- Optional **isotonic recalibration map**, fitted on the development set,
  published for the routing layer. The leaderboard reports raw calibration —
  applying the fit before scoring would let a badly-calibrated model borrow the
  fit's credit.

## 8. Quality index

| Dimension | Weight |
| --- | ---: |
| Detection (F_beta) | 30% |
| Evidence grounding | 25% |
| Root-cause reasoning | 15% |
| Severity agreement | 10% |
| Completeness | 10% |
| Remediation | 7% |
| Communication | 3% |

Dimensions with no grader available are **dropped and the remaining weights
renormalized**, and the grade records which. A run without judges produces a
defensible index over what it measured rather than silently zeroing three
dimensions.

```
EvidenceScore = (0.5 · resolution_rate + 0.4 · verified_fraction
                 − 0.3 · contradicted_fraction) / 0.9
```

with `verified_fraction` and `contradicted_fraction` computed over **decidable**
claims only, and `resolution_rate` corrected by the resolver's own measured miss
rate — which is published rather than applied invisibly.

## 9. Reported separately, never blended

- calibration (Brier, ECE, AUC)
- abstention precision, over-claim rate
- schema conformance (first-pass validity)
- refusal rate by category
- reliability (pass@k, pass^k, variance, worst trial)
- economics (cold cost, cost per correct finding, latency)

Blending calibration into quality hides the trade-off that matters for routing: a
slightly less accurate but well-calibrated model is often the better production
choice, because its low-confidence output can be escalated automatically.

## 10. Iso-budget comparison

Vendor effort labels are three unrelated scales and shift between generations of
the same family. Therefore:

1. sweep the full ladder per model, subject to a spend cap, cheapest-first
2. build the Pareto frontier over (cold cost, quality) and (p50 latency, quality)
3. compare at declared spend points by interpolating each frontier
4. a model that cannot reach a point is reported **absent** — never extrapolated

# Canonical prompt — controls assessment

```yaml
role:
  persona: "a controls assessor producing evidence for an internal audit"
  domain: "engineering controls assessment"

objective: >
  Assess the attached corpus against the controls in the supplied rubric and return
  a compliance status for each, with the evidence that supports it.

scope: >
  Only the controls listed in the rubric, assessed only against the attached
  corpus. Do not assess controls that are not listed.

success_criteria:
  - "Each control receives exactly one of COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE or INSUFFICIENT_EVIDENCE."
  - "Every status cites the specific evidence location that supports it."
  - "Where the corpus does not contain the evidence a control requires, return INSUFFICIENT_EVIDENCE rather than inferring a status."
```

## Why this suite is precision-leaning

`beta = 0.7`. A false non-compliance finding has a real organizational cost: an
engineer investigates, a control owner is pulled in, an audit trail is created,
and nothing is found. Missing a control is bad; manufacturing one is expensive in
a way the security suite's trade-off is not.

## Why abstention matters most here

`INSUFFICIENT_EVIDENCE` is a first-class correct answer. A model that guesses
COMPLIANT rather than admitting the evidence is absent is actively dangerous in a
controls workflow — it puts an unmitigated risk on the accepted list, which is
worse than either a false positive or a miss.

The over-claim penalty (1.5× a normal false positive) exists for exactly this
case, and the two derived metrics keep it from being gamed in either direction:

- **over-claim rate** punishes answering everything
- **abstention precision** punishes abstaining everywhere

A model has to actually know which controls the corpus can speak to.

## The confusion matrix worth reporting

| Model says | Oracle: compliant | Oracle: non-compliant | Oracle: insufficient |
| --- | --- | --- | --- |
| COMPLIANT | TP | **FN — the expensive one** | over-claim |
| NON_COMPLIANT | **FP — the costly one** | TN | over-claim |
| INSUFFICIENT_EVIDENCE | miss | miss | **correct** |

Both diagonals matter, and the bottom-right cell is the one most benchmarks have
no way to score at all.

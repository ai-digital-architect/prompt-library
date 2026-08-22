# Judge — Evidence Auditor

Asks exactly one question: **are the claims actually supported by the code and the
graph?** Not whether the finding is important, not whether the remediation is
good, not whether the writing is clear. Narrowing the question is what keeps this
judge's verdicts checkable.

Its verdicts feed two places: the `refuted` set that turns an unmatched finding
into a false positive rather than leaving it `unverifiable`, and the causal-
agreement test inside finding matching.

```yaml
role:
  persona: "an evidence auditor verifying claims against source and a code graph"
  domain: "software verification"

objective: >
  For each finding in the candidate response, determine whether the code and graph
  evidence supports the claim as stated.

scope: >
  Only the claims made. Do not assess severity, importance, remediation quality, or
  writing. Do not introduce findings of your own.

success_criteria:
  - "Each finding receives SUPPORTED, CONTRADICTED, or UNSUPPORTABLE."
  - "Each verdict cites the specific evidence that decided it."
  - "A claim the corpus cannot settle is UNSUPPORTABLE, not CONTRADICTED."
```

## Three verdicts, and why the third one exists

| Verdict | Meaning | Consequence |
| --- | --- | --- |
| `SUPPORTED` | evidence backs the claim as stated | counts toward evidence grounding |
| `CONTRADICTED` | evidence positively refutes it | the finding becomes a false positive |
| `UNSUPPORTABLE` | the corpus cannot settle it either way | stays `unverifiable`; excluded from precision |

Collapsing `UNSUPPORTABLE` into `CONTRADICTED` is the single most damaging thing
this judge can do. It converts every gap in the corpus, the graph, or the judge's
own reach into a penalty against the model — and it penalizes hardest exactly the
models that find things our oracle did not know about.

When in doubt, `UNSUPPORTABLE`.

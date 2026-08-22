# Canonical prompt — engineering review

The canonical form of the general engineering-review task. Authored once as IR
fields; adapters render it per provider. **Nothing here is provider-specific** —
if you find yourself wanting to phrase something "for Claude", it belongs in an
adapter, not here.

```yaml
role:
  persona: "a principal engineer performing a pre-release review"
  domain: "enterprise software systems"

objective: >
  Review the attached system for {{DIMENSIONS}} issues. For each one, identify the
  affected code, the path by which the problem manifests, the root cause, and a
  remediation.

scope: >
  The attached corpus only. Cover every file in it, not only the first file you
  examine. Do not speculate about components that are not present.

success_criteria:
  - "Every issue present in the corpus is reported."
  - "Each finding names the affected symbol and its evidence location."
  - "Each finding expresses its structural claims as relations so they can be checked."
  - "Each finding carries a calibrated confidence and an estimated severity."
  - "Findings that cannot be confirmed from the corpus are marked SUSPECTED rather than omitted."
  - "Questions the corpus cannot answer are recorded as abstentions."

context:
  why_this_matters: >
    {{Stakes, and who consumes the output. Task intent measurably improves output
    quality across every family in the roster — say why the work exists, not only
    what it is.}}
  audience: "{{WHO READS THIS}}"
  known_constraints:
    - "{{e.g. no runtime telemetry is available; assess from source only}}"

response:
  schema_ref: schemas/findings-v1.schema.json
  schema_version: "1.0.0"
  required_fields: [findings, abstentions]
```

## Why it is phrased this way

**"Report coverage, not a shortlist."** Several current models follow "only report
high-severity issues" literally and suppress real findings. Coverage is requested
at generation time; filtering is a downstream scoring decision. This is also why
`severity_filter` is a prohibition rather than a style preference.

**"Expressed as relations so they can be checked."** Claims are emitted natively
in the response schema rather than extracted from prose afterwards. Post-hoc
extraction is an unmeasured model call applied asymmetrically across candidates —
the highest-leverage failure point in the whole design. Every model in the roster
supports structured output, so this costs nothing in fairness terms.

**"Marked SUSPECTED rather than omitted."** An honest "I could not confirm this"
costs half a false positive. A model that surfaces a real concern it could not
verify should not be punished as hard as one that fabricates confidently.

**"Recorded as abstentions."** `INSUFFICIENT_EVIDENCE` is a first-class correct
answer, scored with its own reward and its own over-claim penalty.

**No verification instruction, no progress-summary scaffolding, no enumerated style
rules.** All three are net-negative on current generations and all three are in the
prohibition list. If one appears in a rendered prompt, the fairness validator fails
the run before it is billed.

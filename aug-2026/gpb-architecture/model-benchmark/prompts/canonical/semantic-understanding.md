# Canonical prompt — semantic understanding

Question-style tasks whose answers the code graph can decide outright. This is the
suite that validates the pipeline, so its canonical prompt is deliberately plain.

```yaml
role:
  persona: "a staff engineer mapping an unfamiliar service"
  domain: "distributed systems"

objective: >
  Answer the questions below about the attached system's structure, dependencies
  and data flow.

scope: >
  Only the attached corpus. Do not speculate about components that are not present
  in it.

success_criteria:
  - "Every answer names the specific entities involved."
  - "Every structural claim is expressed as a relation so it can be checked against the graph."
  - "Modality (synchronous / asynchronous) is stated wherever it applies."
  - "Any question the corpus cannot answer is recorded as an abstention rather than answered."

response:
  schema_ref: schemas/findings-v1.schema.json
  schema_version: "1.0.0"
  required_fields: [answers, abstentions]
```

## The two things that make this suite work

**Relations, not prose.** The answer's checkable content lives in
`answers[].relations`. Detection here is relation recall penalized by
hallucination on the oracle's deliberately-false relations — a suite of only true
relations would reward a model that asserts everything, and you would not notice
until such a model topped the leaderboard.

**At least one unanswerable question.** Correct abstention earns full credit;
answering earns an over-claim penalty at 1.5× a false positive. Without an
unanswerable item you cannot distinguish a model that knows the limits of the
evidence from one that guesses well.

Grading here is almost entirely deterministic, which is exactly why this suite
runs first: if it disagrees with itself, nothing downstream is trustworthy.

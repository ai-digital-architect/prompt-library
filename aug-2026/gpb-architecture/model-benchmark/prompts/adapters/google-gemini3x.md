---
adapter_id: google-gemini3x
version: 1.0.0
models: [gemini-3.6-flash, gemini-3-pro]
derived_from_templates:
  - "26-google-gemini-3-6-flash.md"
  - "04-google-gemini-3-pro.md   (reference only — model is shut down)"
---

# Adapter spec — Google Gemini 3.x

Implemented by `scripts/mbcore/adapters/google.py::GoogleGemini3xAdapter`.

## Rendering — context first, instruction last

This is the clearest example in the whole harness of legitimate free-set
variation. Google's long-context guidance asks for documents and media at the top
and the specific question at the very end; Claude wants the full specification up
front. Both render the same IR.

```text
systemInstruction:
You are {{role.persona}} specializing in {{role.domain}}.

Rules:
- Scope: {{scope}}
- Report coverage, not a shortlist: include uncertain and low-severity findings
  with their own confidence and severity.
- Cite file, symbol and line range for every finding; distinguish confirmed from inferred.
- Where the material does not support a conclusion, record an abstention.
- The current year is 2026. For anything newer than your training data, rely on the
  provided context rather than memory.
- Default to concise output; expand only where the task requires it.
- {{budget line}}

Tool use:                    ← only when the IR's tools declare when_to_use
- {{tools[].when_to_use}}

---
user (the ONLY and FINAL turn):

## Context
{{context.why_this_matters}}
Audience: {{context.audience}}.
- {{context.known_constraints[]}}

### {{label}} ({{kind}})
{{content}}

## Task
{{objective}}

{{questions}}

## Requirements
1. {{success_criteria[]}}

## Output Format
{{response contract}}
```

## Request

```json
{
  "systemInstruction": { "parts": [{ "text": "…" }] },
  "contents": [{ "role": "user", "parts": [{ "text": "…" }] }],
  "generationConfig": {
    "maxOutputTokens": "<min(profile, model default, IR budget)>",
    "thinkingConfig": { "thinkingLevel": "<swept>" },
    "responseMimeType": "application/json",
    "responseSchema": "<findings-v1, reduced>"
  }
}
```

## Three rules that produce errors or silent differences if missed

1. **No sampling parameters.** `temperature`, `topP`, `topK` are deprecated and
   **silently ignored**, with HTTP 400 promised in future versions. Silently
   ignored is the dangerous case: a harness that sets them believes it has control
   it does not have, and the resulting variance looks like model behaviour.
2. **The final turn is always the user's.** A request ending on a model-role turn
   now errors. Prefill-style steering moves into `systemInstruction` or the
   response schema — never a trailing model turn.
3. **Depth is `thinking_level` string values**, not `thinking_budget`.

## Schema reduction

Gemini accepts a narrower JSON Schema subset. `_strip_unsupported()` drops
`$schema`, `$id`, `additionalProperties`, `definitions`, `$ref`, `const`,
`examples`, `pattern`, `minItems`, `maxLength`, `default`.

Dropping rather than passing through is deliberate: an unrecognized keyword can
cause the **whole schema** to be rejected, which surfaces as a `SCHEMA_INVALID`
disposition and is easily misread as the model failing to follow instructions.

Consequence to remember: because some constraints are stripped, the response is
validated more thoroughly downstream by `normalize.py` than by the API. That is
the right direction — measuring conformance is more informative than having the
API silently enforce a reduced version of it.

## Grounding is billed separately

Search grounding is a built-in tool, free for the first 5,000 requests per month
shared across Gemini 3 models, then $14 per 1,000 queries. It is a **line item**,
not folded into token cost — folding it in would make Gemini look cheaper than it
is on any grounded suite.

The model page publishes no knowledge cutoff, so treat anything current-events
adjacent as requiring grounding. Benchmark suites over a fixed corpus generally do
not need it.

## Gemini 3 Pro — retired

Registered for roster completeness and so historical results stay interpretable.
`status: retired`, `enabled: false`; requires `--include-retired`. Expect
404-class errors, dispositioned as `PROVIDER_ERROR` — never as a capability
failure.

The nearest deployable Pro-tier model is Gemini 3.1 Pro
(`gemini-3.1-pro-preview`): still Preview, thinking always on, `thinking_level`
defaults to `high`, `minimal` not supported. Add it to the registry if the study
needs a Pro-tier data point.

## Response handling

- text: concatenate `candidates[].content.parts[].text`
- usage: `promptTokenCount` minus `cachedContentTokenCount` for uncached;
  `thoughtsTokenCount` is exposed and recorded; `candidatesTokenCount` for output
- refusal: `promptFeedback.blockReason`, or `finishReason` in
  `SAFETY` / `BLOCKLIST` / `PROHIBITED_CONTENT`
- truncation: `finishReason == "MAX_TOKENS"`
- resolved model version: `body.modelVersion`

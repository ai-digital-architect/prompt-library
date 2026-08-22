---
adapter_id: openai-gpt56
version: 1.0.0
models: [gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna]
derived_from_templates:
  - "23-openai-gpt-5-6-sol.md"
  - "24-openai-gpt-5-6-terra.md"
  - "25-openai-gpt-5-6-luna.md"
---

# Adapter spec — OpenAI GPT-5.6

Implemented by `scripts/mbcore/adapters/openai.py::OpenAIGpt56Adapter`.

## Rendering

Markdown-sectioned developer/user messages via the Responses API.

```text
developer:
# Identity
You are {{role.persona}}, an expert in {{role.domain}}.

# Instructions
- Scope: {{scope}}
- Report coverage, not a shortlist: include uncertain and low-severity findings,
  each with its own confidence and estimated severity.
- Every finding cites file, symbol and line range, and distinguishes confirmed
  from inferred.
- Autonomy: read and query freely within the evidence budget. Do not stall on
  ambiguity — state the assumption and proceed.
- If the material does not support a conclusion, record an abstention rather than
  producing a low-confidence guess.
- {{budget line, when the IR declares one}}

# Success criteria
1. {{success_criteria[]}}

# Output format
{{response contract}}

# Tool use          ← only when the IR's tools declare when_to_use
- {{tools[].when_to_use}}

---
user:
{{objective}}

{{questions}}

Context:
## {{label}} ({{kind}})
{{content}}
```

**Static content first, dynamic last.** Cached input on this family is up to 10×
cheaper than uncached and cache writes bill at 1.25×, so ordering is worth real
money across a large study. The developer block is identical across tasks in a
suite and stays in the cached prefix.

## Request

```json
{
  "model": "<model id>",
  "input": [
    { "role": "developer", "content": "…" },
    { "role": "user", "content": "…" }
  ],
  "reasoning": { "effort": "<swept>", "mode": "<Sol only>" },
  "text": {
    "verbosity": "<optional>",
    "format": { "type": "json_schema", "name": "engineering_findings_v1",
                "strict": false, "schema": "<findings-v1>" }
  },
  "max_output_tokens": "<min(profile, model default, IR budget)>"
}
```

`strict: false` because the findings schema uses constructs strict mode rejects.
Schema conformance is measured downstream regardless, and measuring it is more
informative than having the API enforce a reduced schema.

## `reasoning.mode` is an independent axis — and Sol-only

`mode` (`standard` / `pro`) is documented for `gpt-5.6-sol` and **not confirmed**
for Terra or Luna. The adapter **refuses to set it** on the unconfirmed tiers
rather than passing it through and hoping.

The reasoning is worth stating: an undocumented parameter that silently changes
behaviour on one tier would appear in the results as a capability difference we
could not attribute to anything. Refusing to set it costs a data point; setting it
costs the interpretability of every Terra and Luna number in the round.

Declare the axis in the study:

```yaml
effort:
  policy: sweep
  extra_axes:
    gpt-5.6-sol:
      reasoning_mode: [standard, pro]
```

The registry drops the axis for models where it is not documented, so the study
file can list it without producing invalid configurations.

## Migrate by shrinking

OpenAI's own testing found leaner prompts raised eval scores roughly 10–15% while
cutting total tokens 41–66% on this generation. Repeated instructions and
elaborate tool descriptions measurably lower scores. This renderer says each thing
once — and that is a fairness property as much as an efficiency one, because
verbosity that helps one family and hurts another is a confound.

Start effort **one rung below** your GPT-5.5 baseline and test upward.

## Cost model

- Above **272K input tokens** the whole **session** bills at 2× input / 1.5×
  output. Session-scoped, not request-scoped; the pricing engine models it that
  way, and a per-request model would understate multi-step agentic runs.
- Cache writes bill at 1.25× uncached input, attributed to the cold run.
- Cached input: $0.50 / $0.25 / $0.10 per MTok for Sol / Terra / Luna.

## Per-model deviations

| Model | Deviation |
| --- | --- |
| Sol | `reasoning.mode` axis available |
| Terra | none; the productive pattern is a Sol planner with Terra workers, not "Terra everywhere with a longer prompt" |
| Luna | lower default output ceiling; the abstain branch in the response schema matters most here — a cheap model that guesses is worse than one that flags |

## Response handling

- text: `output_text`, else concatenate `output[].content[].text`
- usage: `input_tokens` minus `input_tokens_details.cached_tokens` for uncached;
  `output_tokens_details.reasoning_tokens` **is** exposed here and is recorded
- refusal: a content part with `type: "refusal"`
- truncation: `status == "incomplete"` with `incomplete_details.reason == "max_output_tokens"`
- resolved model version: `body.model`

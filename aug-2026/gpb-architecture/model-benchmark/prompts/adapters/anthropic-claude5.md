---
adapter_id: anthropic-claude5
version: 1.0.0
models: [claude-fable-5, claude-opus-5, claude-sonnet-5]
derived_from_templates:
  - "13-anthropic-claude-fable-5.md"
  - "21-anthropic-claude-opus-5.md"
  - "22-anthropic-claude-sonnet-5.md"
upstream: "../../../ (model-prompt-templates) — READ-ONLY"
---

# Adapter spec — Anthropic Claude 5 generation

Implemented by `scripts/mbcore/adapters/anthropic.py::AnthropicClaude5Adapter`.
This file is the human-readable contract; the code is the executable one. If they
disagree, that is a bug in one of them.

## Rendering

```xml
<system>
You are {{role.persona}}, an expert in {{role.domain}}.

<context>
{{context.why_this_matters}}
Audience: {{context.audience}}.
- {{context.known_constraints[]}}
</context>

<objectives>
1. {{success_criteria[0]}}
2. {{success_criteria[1]}}
...
</objectives>

<guidelines>
- Scope: {{scope}}
- Report coverage, not a shortlist. Include findings you are uncertain about, each
  with its own confidence and severity — a separate pass filters them.
- Cite file, symbol and line range for every finding. Distinguish what you confirmed
  from what you inferred.
- Match any code you write to the conventions already present in the reference material.
- {{Sonnet 5 only}}: Apply every requirement above to the whole corpus in scope,
  not only to the first item you examine.
- {{budget line, when the IR declares one}}
</guidelines>

<output_format>
{{response contract — schema ref, required fields, claim-emission instruction,
abstention instruction, confidence semantics}}
</output_format>
</system>

<user>
{{objective}}

{{questions, when the task has them}}

<reference_material>
  <code>…</code> <tests>…</tests> <spec>…</spec> …
</reference_material>
</user>
```

## Request

```json
{
  "model": "<model id>",
  "max_tokens": "<min(profile, model default, IR budget)>",
  "output_config": {
    "effort": "<swept>",
    "format": { "type": "json_schema", "schema": "<findings-v1>" }
  },
  "system": "…",
  "messages": [{ "role": "user", "content": "…" }]
}
```

## What is deliberately absent, and why

| Absent | Reason |
| --- | --- |
| `thinking` | Adaptive and on by default across this generation. On Fable 5 both disabling and `budget_tokens` return a 400. |
| `temperature`, `top_p`, `top_k`, `budget_tokens` | All return a 400. Their presence signals a stale adapter. |
| assistant-turn prefill | Returns a 400. Use `output_config.format`. |
| "double-check your work" | Self-verification is native; adding it costs tokens and triggers over-verification. Prohibited. |
| "summarize progress every N steps" | Narration is native. Prohibited. |
| enumerated style prohibitions | Replaced by judgment framing ("match the conventions already in the reference material"). |
| few-shot examples | Move some families far more than others. If a task needs them they belong in the IR. Prohibited. |

**Governing rule for this generation: delete before you add.** Anthropic removed
over 80% of Claude Code's system prompt with no measurable eval loss. A guardrail
written for Opus 4.x over-constrains Claude 5.

## Per-model deviations

| Model | Deviation |
| --- | --- |
| Sonnet 5 | Adds an explicit scope-of-application line. It follows instructions literally and will not infer that a requirement covers the whole corpus. |
| Fable 5 | No deviation in rendering. Note its mandatory 30-day retention and absence of ZDR — a corpus decision, not a prompt one. |
| Opus 5 | No deviation. |

## Response handling

- text: concatenate `content[].text` where `type == "text"`
- usage: `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`,
  `output_tokens`. `reasoning_tokens` is **`None`** — thinking is counted inside
  `output_tokens`, so a separate figure would double-count.
- refusal: HTTP 200 with `stop_reason == "refusal"`, category in
  `stop_details.category`
- truncation: `stop_reason == "max_tokens"`
- resolved model version: `body.model`

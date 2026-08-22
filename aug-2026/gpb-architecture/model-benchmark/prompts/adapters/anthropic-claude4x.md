---
adapter_id: anthropic-claude4x
version: 1.0.0
models: [claude-opus-4-8, claude-opus-4-7, claude-opus-4-6]
derived_from_templates:
  - "14-anthropic-claude-opus-4-8.md"
  - "12-anthropic-claude-opus-4-6.md"
note: "Opus 4.7 has NO upstream template; its profile is derived from 4.8."
---

# Adapter spec — Anthropic Claude 4.x generation

Implemented by `scripts/mbcore/adapters/anthropic.py::AnthropicClaude4xAdapter`.

This generation wants a *more* explicit prompt than Claude 5, which is why it gets
its own adapter rather than a flag on the Claude 5 one. Collapsing them would
disadvantage 4.x on exactly the axis the Optimized lane exists to remove.

## Rendering

Same XML scaffold as Claude 5, plus two blocks:

```xml
<thinking_instructions>   <!-- Opus 4.6 only -->
Reason through the system's structure before writing findings. Identify assumptions
that would invalidate a conclusion, and acknowledge uncertainty rather than masking it.
</thinking_instructions>

<capability_triggers>     <!-- when the IR's tools declare when_to_use -->
- {{tools[].when_to_use}}
</capability_triggers>
```

And one extra guideline: *"For minor choices, pick a reasonable option and note it
rather than asking."* 4.8 asks before minor decisions more often than 4.7 by
default, and this cuts the ask-rate without increasing over-reach.

## Request

```json
{
  "model": "<model id>",
  "max_tokens": "<min(profile, model default, IR budget)>",
  "thinking": { "type": "adaptive" },
  "output_config": {
    "effort": "<swept>",
    "format": { "type": "json_schema", "schema": "<findings-v1>" }
  },
  "system": "…",
  "messages": [{ "role": "user", "content": "…" }]
}
```

`thinking` is stated explicitly here — unlike Claude 5, where it is omitted.

## Capability triggers are not a fairness leak

This generation is measurably conservative about reaching for search, subagents,
memory and custom tools, and improves with prescriptive "call this when…"
language. That help is legitimate **because it comes from the canonical tool IR's
`when_to_use` field**, so every adapter for every family renders the same trigger
text. What varies is placement, not content.

If a trigger were written into this adapter rather than into the IR, it would be
exactly the kind of smuggled semantic help the fairness contract exists to catch.

## The declared exemption

`anthropic-claude4x` is exempt from the `depth_by_prose` prohibition, because
Opus 4.6 accepts an explicit thinking-instructions block that later generations
penalize. Declared in `config/lanes.yaml`; surfaces as a **warning** in every
fairness verdict so a reviewer sees it.

## API surface

- `budget_tokens` deprecated on 4.6, rejected from 4.7 onward
- sampling parameters deprecated from **4.7 and later**; the adapter omits them on
  4.6 too, so the Parity lane stays comparable
- prefills return a 400 on 4.6 as well as later
- Opus 4.8 supports mid-session system prompts under beta header
  `mid-conversation-system-2026-04-07` (unused here — the benchmark is
  single-turn per trial)

## Opus 4.7

No dedicated upstream template exists. The library states Opus 4.8 has the "same
API surface as Opus 4.7", and that sampling parameters are deprecated on "Opus 4.7
and later". The profile is therefore derived from template 14.

Registered `derived: true` with a `template_note`; the registry validator rejects a
derived profile without one. Every report footnotes it. **Validate against vendor
documentation before treating an Opus 4.7 result as load-bearing.**

# Provider notes

API-surface facts that the adapters depend on. Transcribed from the read-only
`model-prompt-templates/` library in the parent folder, verified there on
**25 July 2026**.

**The templates are the upstream authority. Never edit them.** When one changes,
update the registry and the adapter, bump the adapter version, and record it in
`CHANGELOG.md`.

---

## Facts that hold across all three vendors' current generations

These are the ones that break adapters written for earlier models.

| Fact | Consequence |
| --- | --- |
| **Sampling parameters are gone.** `temperature`, `top_p`, `top_k` return HTTP 400 on the Claude 5 generation and GPT-5.6, and are deprecated + silently ignored on Gemini 3.6. | Run-to-run variance is irreducible; `seed` is not a reproducibility lever. The manifest records `sampling: "not-applicable"` rather than implying determinism the platform cannot deliver. Silently ignored is the more dangerous case — a harness that sets them believes it has control it does not have. |
| **Depth is a parameter, not prose.** | "Think harder" is unevenly effective across families and confounds the axis the effort sweep exists to measure. `depth_by_prose` is prohibited. |
| **Effort labels are not a common scale.** | `high` means three different things. Compare at iso-cost / iso-latency points on a measured frontier. |
| **Structured output is native everywhere.** | Attach the schema through the API rather than describing it in prose: frees prompt budget and removes the most common source of format drift. Costs nothing in fairness terms because every model in the roster supports it. |
| **Variety comes from the prompt.** | With `temperature` gone, ask for variety explicitly ("propose three distinct approaches, then build the one you recommend"). |

---

## Anthropic

### Claude 5 generation — Fable 5, Opus 5, Sonnet 5

| | Fable 5 | Opus 5 | Sonnet 5 |
| --- | --- | --- | --- |
| Model ID | `claude-fable-5` | `claude-opus-5` | `claude-sonnet-5` |
| Context / max output | 1M / 128K | 1M / 128K | 1M / 128K |
| Pricing (in/out per MTok) | $10 / $50 | $5 / $25 | $3 / $15 (intro $2 / $10 through 2026-08-31) |
| Effort | `low`…`max`, default `high` | same | same |
| Thinking | adaptive, **always on**, cannot be disabled or budgeted | adaptive on by default; disable only at effort ≤ `high` | adaptive on by default; disable allowed |
| Retention | **mandatory 30-day, no ZDR** | standard | standard |

- Effort lives in `output_config.effort`, not at the top level.
- `budget_tokens` and assistant-turn prefills return a 400.
- Machine-readable output: `output_config.format`.
- Prompt-cache minimum is 512 tokens. Hold effort constant inside a cached
  conversation — changing it invalidates the cache.
- Beta headers `effort-2025-11-24`, `interleaved-thinking-2025-05-14`,
  `token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`,
  `fine-grained-tool-streaming-2025-05-14` are GA — remove them.
- **Refusals return HTTP 200** with `stop_reason: "refusal"` and a category in
  `stop_details.category`. This is the shape a naive harness misreads as an empty
  answer.
- Raw chain of thought is never returned. Asking a model to reproduce its
  reasoning triggers a `reasoning_extraction` refusal; use
  `thinking: {"display": "summarized"}` and treat it as display text.

**Prompting posture: delete before you add.** Anthropic removed over 80% of Claude
Code's system prompt for this generation with no measurable eval loss. Verification
scaffolding, progress-summary scaffolding, severity filters and enumerated style
prohibitions are all net-negative.

**Sonnet 5 specifics.** It follows instructions literally and does not infer the
scope of a requirement — state it. Its new tokenizer emits roughly **30% more
tokens for the same text** than Sonnet 4.6, which is a budgeting fact and never a
cross-family capability comparison.

### Claude 4.x — Opus 4.8, 4.7, 4.6

All three are delisted from the current models table but remain callable. Same
$5 / $25 pricing, 1M / 128K.

- Thinking is stated explicitly: `thinking: {"type": "adaptive"}`.
- `budget_tokens` is deprecated on 4.6 and rejected from 4.7 onward. Sampling
  parameters are deprecated from **4.7 and later**, not only on Claude 5.
- Prefills return a 400 on 4.6 as well.
- This generation is **conservative about reaching for tools, search, subagents
  and memory**, and improves measurably with explicit "call this when…" triggers.
  Those come from the canonical tool IR so every adapter renders the same trigger.
- Opus 4.6 accepts an explicit thinking-instructions block that later generations
  penalize — hence the declared `depth_by_prose` exemption for
  `anthropic-claude4x`.
- Opus 4.8 supports mid-session system prompts under beta header
  `mid-conversation-system-2026-04-07`.

**Opus 4.7 has no dedicated upstream template.** Its profile is derived from 4.8,
which the library states shares its API surface. Registered `derived: true`; every
report footnotes it. Retires no sooner than 2027-04-16.

---

## OpenAI — GPT-5.6 Sol / Terra / Luna

| | Sol | Terra | Luna |
| --- | --- | --- | --- |
| Model ID | `gpt-5.6-sol` | `gpt-5.6-terra` | `gpt-5.6-luna` |
| Context / max output | 1,050,000 / 128K | same | same |
| Pricing (in/out/cached) | $5 / $30 / $0.50 | $2.50 / $15 / $0.25 | $1 / $6 / $0.10 |
| `reasoning.mode: "pro"` | **documented** | not confirmed | not confirmed |
| Rate limit ceiling (Tier 5) | 15K RPM / 40M TPM | same | **30K RPM / 180M TPM** |

- `gpt-5.6` and `gpt-5` alias to Sol.
- Knowledge cutoff 2026-02-16 across the family.
- `reasoning.effort` accepts a model-dependent subset of `none`, `minimal`, `low`,
  `medium`, `high`, `xhigh`, `max`. `reasoning.mode` (`standard` / `pro`) is an
  **independent axis** — set both.
- The adapter refuses to set `reasoning.mode` on Terra and Luna. An undocumented
  parameter that silently changes behaviour would surface as a capability gap we
  could not attribute.
- `text.verbosity` (`low` / `medium` / `high`) controls length; prefer it to prose.
- **Above 272K input tokens the whole session bills at 2× input / 1.5× output.**
  Session-scoped, not request-scoped — the cost engine models it that way.
- Cache writes bill at 1.25× uncached input.
- Use the Responses API for anything with reasoning or multiple turns; pass
  reasoning items forward with `previous_response_id`.
- **Migrate by shrinking.** OpenAI's testing found leaner prompts raised eval
  scores ~10–15% while cutting tokens 41–66% on this generation. Repeated
  instructions and elaborate tool descriptions measurably lower scores.
- Set effort **one rung below** your GPT-5.5 baseline, then test upward.
- Refusals appear as a content part with `type: "refusal"` inside `output`.

---

## Google — Gemini 3.6 Flash (and Gemini 3 Pro, retired)

| | Gemini 3.6 Flash |
| --- | --- |
| Model ID | `gemini-3.6-flash` |
| Status | Stable — Google's latest and default model |
| Context / max output | 1,048,576 / 65,536 |
| Pricing | $1.50 / $7.50 per MTok; Batch at 50%; caching $0.15/MTok + $1.00/hr storage |
| Thinking | `thinking_level`: `minimal` / `low` / `medium` / `high`, default `medium` |
| Knowledge cutoff | not published on the model page |

Three rules that produce errors or silent differences if missed:

1. **Context first, instruction last.** Documents, code and media at the top; the
   specific question at the very end.
2. **`temperature` / `top_p` / `top_k` are deprecated and silently ignored**, with
   HTTP 400 promised in future versions.
3. **A request may not end on a model-role turn.** Prefill-style steering errors
   out — move it into `system_instruction` or the response schema.

Other notes:

- `thinking_budget` is superseded by `thinking_level` **string** values.
- Native multimodal input: text, image, video, audio, PDF are equal-class.
- Search grounding is a built-in tool billed separately from tokens: 5,000 free
  requests per month shared across Gemini 3 models, then $14 per 1,000 queries.
  Because the model page publishes no knowledge cutoff, treat anything
  current-events adjacent as requiring grounding.
- The response schema must be reduced to Gemini's accepted JSON Schema subset. An
  unsupported keyword can cause the whole schema to be rejected, which surfaces as
  `SCHEMA_INVALID` and is easily misread as a model weakness.
- Refusals: `promptFeedback.blockReason`, or a candidate `finishReason` of
  `SAFETY` / `BLOCKLIST` / `PROHIBITED_CONTENT`.

**Gemini 3 Pro is shut down.** It appears in Google's deprecated list and the
upstream template is reference-only. Registered `status: retired`,
`enabled: false`; requires `--include-retired`. Expect 404-class errors,
dispositioned as `PROVIDER_ERROR`. The nearest deployable Pro-tier model is Gemini
3.1 Pro (`gemini-3.1-pro-preview`, still Preview, thinking always on, `minimal`
not supported) — add it to the registry if a Pro-tier data point is needed.

---

## Quick reference: where each vendor puts the knobs

| Concept | Anthropic | OpenAI | Google |
| --- | --- | --- | --- |
| Reasoning depth | `output_config.effort` | `reasoning.effort` | `thinking_level` |
| Second depth axis | — | `reasoning.mode` (Sol only) | — |
| Output length | prompt language | `text.verbosity` | prompt language |
| Structured output | `output_config.format` | Structured Outputs | `responseMimeType` + `responseSchema` |
| System content | `system` | `developer` role | `systemInstruction` |
| Refusal signal | `stop_reason: "refusal"` @ HTTP 200 | `type: "refusal"` content part | `blockReason` / `finishReason` |
| Truncation signal | `stop_reason: "max_tokens"` | `status: "incomplete"` | `finishReason: "MAX_TOKENS"` |
| Cached tokens | `cache_read_input_tokens` | `input_tokens_details.cached_tokens` | `cachedContentTokenCount` |
| Reasoning tokens | not exposed (inside output) | `output_tokens_details.reasoning_tokens` | `thoughtsTokenCount` |

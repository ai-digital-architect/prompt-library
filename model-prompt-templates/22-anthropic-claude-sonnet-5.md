# General-Purpose Prompt Template — Anthropic Claude Sonnet 5

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Sonnet 5 |
| **Provider** | Anthropic |
| **Tier** | Balanced frontier — best speed-to-intelligence ratio; the everyday production default |
| **API Model ID** | `claude-sonnet-5` |
| **Context Window** | 1M tokens |
| **Max Output** | 128K tokens |
| **Pricing** | $3 / $15 per million input/output tokens (introductory $2 / $10 through Aug 31, 2026) |
| **Thinking** | Adaptive, **on by default**; `thinking: {"type": "disabled"}` is allowed |
| **Effort** | `low` / `medium` / **`high` (default)** / `xhigh` / `max` |
| **Tokenizer** | New — produces **~30% more tokens** for the same text than Sonnet 4.6 |
| **Strengths** | Coding and agentic tool use, literal instruction following, structured extraction, frontend generation, computer use (`computer_20251124`) |
| **Best For** | Production coding agents, multi-tool workflows, predictable API pipelines, interactive assistants, UI/frontend work |

---

## What Sets Sonnet 5 Apart

1. **It follows instructions literally.** Sonnet 5 does not silently generalize an
   instruction or infer unstated requests. That makes it excellent for API pipelines
   and structured extraction — and it means you must state the *scope* of an
   instruction explicitly ("apply this to every section, not just the first").
2. **It is more agentic than Sonnet 4.6.** It reaches for tools more readily,
   especially at `high`/`xhigh` effort. At `low` effort it scopes work tightly to what
   was asked.
3. **It calibrates length to the task.** Short answers on lookups, long ones on
   open-ended analysis — rather than a fixed default verbosity.
4. **The effort ladder shifted down.** Sonnet 5 at `medium` ≈ Sonnet 4.6 at `high`;
   Sonnet 5 at `high` ≈ Sonnet 4.6 at `max`. Carry-over settings overspend.
5. **The API surface tightened.** Sampling parameters and manual thinking budgets both
   return a 400 — new for Sonnet-class models.

---

## Context Engineering for Sonnet 5

The Claude 5 generation is deliberately under-constrained: Anthropic removed over 80%
of Claude Code's system prompt with no measurable eval loss. The same six shifts apply
here as on [Opus 5](./21-anthropic-claude-opus-5.md) — rules → judgment, examples →
tool interface design, everything-upfront → progressive disclosure, repetition →
say-it-once, manual memory → auto-memory, prose specs → rich references.

**The Sonnet 5 caveat:** because it follows instructions literally, deleting a rule
removes exactly that behavior — it will not be silently inferred. Delete
*over-constraining* rules (style prohibitions, "be conservative," progress-summary
scaffolding), but keep genuine requirements, and state their scope.

---

## Template Structure

Sonnet favors action over explanation. Prompts should be direct, structured, and
example-backed. Unlike Opus, it needs no motivational preamble.

```xml
<system>
You are {{ROLE}} with expertise in {{DOMAIN}}.

<task>
{{Direct statement of what to accomplish, and the scope it applies to.}}
</task>

<constraints>
- {{Hard requirement, with explicit scope: "for every endpoint, not just the first"}}
- {{Judgment framing for style: "match the conventions already in <code>"}}
- {{Format or length requirement}}
</constraints>

<examples>
<example>
<input>{{Sample input}}</input>
<output>{{Desired output — one or two of these do more than a page of rules}}</output>
</example>
</examples>
</system>

{{User message — direct and specific. State task, intent, and constraints in this
first turn; progressive clarification costs token efficiency and sometimes quality.}}

<reference_material>
{{Real artifacts — <code>, <tests>, <schema>, <mockup>. Sonnet 5 handles the full
1M-token window.}}
</reference_material>
```

### Key Prompting Principles for Sonnet 5

1. **State the scope of every instruction.** "Apply this formatting to every section,
   not just the first one." Literal following is a feature, but only if you aim it.
2. **Set effort deliberately, one rung lower than you would have.** `medium` is the
   cost-saving default for agentic work; `high` for complex reasoning; `xhigh` for the
   hardest coding; `low` for high-volume or latency-sensitive paths.
3. **Budget `max_tokens` for the new tokenizer.** Re-run token counting — the same
   text costs ~30% more tokens than on Sonnet 4.6, and old `max_tokens` ceilings will
   truncate equivalent output. Leave headroom for thinking at `high` and above.
4. **Use multishot examples.** One or two input→output pairs beat a page of rules,
   and they are the most reliable way to steer format and voice.
5. **Nudge tools explicitly if thinking is off.** With thinking disabled, Sonnet 5 is
   less likely to reach for tools or search. Describe *when* and *why* to use each.
6. **Remove progress-summary scaffolding.** "After every 3 tool calls, summarize
   progress" is obsolete — Sonnet 5 gives regular, higher-quality updates natively.
   If the cadence is wrong for your product, describe the desired one with examples.
7. **Code review: ask for coverage, then filter.** Apparent recall drops on Sonnet 5
   are usually a harness effect — it follows "only report high-severity issues" more
   faithfully. Ask for everything with confidence and severity ratings.
8. **Re-evaluate inherited style prompts.** Prose style shifted; prompts tuned to
   Sonnet 4.6's voice may now overcorrect.

---

## Steering Block Library

**Reduce verbosity:**

```
Provide concise, focused responses. Skip non-essential context, and keep examples
minimal.
```

**Deepen reasoning on hard problems:**

```
This task involves multistep reasoning. Think carefully through the problem before
responding.
```

**Reduce thinking latency** (useful when a large system prompt triggers thinking too
often):

```
Thinking adds latency and should only be used when it will meaningfully improve answer
quality, typically for problems that require multistep reasoning. When in doubt,
respond directly.
```

**Warmer tone:**

```
Use a warm, collaborative tone. Acknowledge the user's framing before answering.
```

**Code review coverage:**

```
Report every issue you find, including ones you are uncertain about or consider
low-severity. Do not filter for importance or confidence at this stage - a separate
verification step will do that. Your goal here is coverage: it is better to surface a
finding that later gets filtered out than to silently drop a real bug. For each
finding, include your confidence level and an estimated severity so a downstream
filter can rank them.
```

For single-pass review, be concrete about the bar instead of using qualitative words:

```
Report any bugs that could cause incorrect behavior, a test failure, or a misleading
result; only omit nits like pure style or naming preferences.
```

**Avoid default AI aesthetics in frontend work:**

```
<frontend_aesthetics>
NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto,
Arial, system fonts), cliched color schemes (particularly purple gradients on white or
dark backgrounds), predictable layouts and component patterns, and cookie-cutter
design that lacks context-specific character. Use unique fonts, cohesive colors and
themes, and animations for effects and micro-interactions.
</frontend_aesthetics>
```

**Break out of a default visual style** — since `temperature` is unavailable, generate
variety with the prompt:

```
Before building, propose 4 distinct visual directions tailored to this brief (each as:
bg hex / accent hex / typeface, plus a one-line rationale). Ask me to pick one, then
implement only that direction.
```

---

## Example 1 — Production API Feature (Coding)

```xml
<system>
You are a senior full-stack engineer. You write production-ready code with proper
error handling, types, and tests.

<constraints>
- TypeScript, strict mode. Zod for input validation on every endpoint below, not just
  the first.
- Unit tests with Vitest for every handler and every validation branch.
- Match the structure, error-handling idiom, and naming already used in <code>.
- Do not introduce new dependencies without stating why.
</constraints>
</system>

Build REST endpoints for user profile management:

1. GET /api/users/:id — fetch profile with Redis caching (5 min TTL).
2. PATCH /api/users/:id — partial update with optimistic locking.
3. DELETE /api/users/:id — soft delete with audit trail.

All three must handle rate limiting (100 req/min per user), request validation,
correct HTTP status codes, and structured errors matching our ApiError format.

Deliver schemas first, then route handlers, then tests.

<reference_material>
<code>[Existing project code and ApiError definition]</code>
<schema>[Database schema]</schema>
<tests>[An existing handler test — match this style]</tests>
</reference_material>
```

---

## Example 2 — Agentic Multi-Tool Workflow

```xml
<system>
You are an on-call SRE assistant with shell, log-query, metrics, and ticketing tools.

<constraints>
- Investigate before acting. Before running a command that changes system state
  (restarts, config edits, scaling changes), state the evidence that supports that
  specific action.
- Make all independent tool calls in parallel.
- Open a ticket for every finding that outlives the incident, not just the root cause.
- Final message: lead with what happened, then the evidence, then what you changed.
</constraints>
</system>

Checkout latency p99 crossed 2s at 14:20 UTC and is still elevated. Diagnose it and
either fix it or hand off with a precise recommendation.

Constraints: no schema changes, no restarts of the payments service without my
approval, and the postmortem draft has to be ready before shift handover at 18:00.

<reference_material>
<runbook>[Checkout latency runbook]</runbook>
<code>[Checkout service source]</code>
</reference_material>
```

---

## Example 3 — Structured Extraction Pipeline

```xml
<system>
You are a document extraction service. You return only the requested structure.

<constraints>
- Extract every party to the agreement, not only the first two.
- If a field is absent, return null — never infer, never fill from context.
- Dates as ISO 8601. Currency amounts as integers in minor units, with a separate
  currency code.
</constraints>

<examples>
<example>
<input>"...between Acme Corp. ('Supplier') and Globex Ltd ('Customer'), dated 3 March 2026, for USD 1,250,000.00..."</input>
<output>{"parties":[{"name":"Acme Corp.","role":"Supplier"},{"name":"Globex Ltd","role":"Customer"}],"effective_date":"2026-03-03","value":{"amount":125000000,"currency":"USD"}}</output>
</example>
</examples>
</system>

Extract the contract metadata from the document below.

<reference_material>
<doc>[Contract text]</doc>
</reference_material>
```

> Pair this with `output_config.format` (JSON schema) at `effort: "low"` for a
> high-volume pipeline. Assistant-turn prefills return a 400.

---

## When to Use Sonnet 5 vs. Other Models

| Scenario | Recommended Model |
|---|---|
| Production coding agents with many tool calls | ✅ Sonnet 5 |
| Frontend and UI generation | ✅ Sonnet 5 |
| Structured extraction and predictable API pipelines | ✅ Sonnet 5 |
| Interactive, latency-sensitive assistants | ✅ Sonnet 5 (at `low`/`medium` effort) |
| Computer use | ✅ Sonnet 5 (`computer_20251124`) |
| Multi-file features, large refactors, production code review | ❌ [Opus 5](./21-anthropic-claude-opus-5.md) |
| Multi-day autonomous runs, hardest novel problems | ❌ [Fable 5](./13-anthropic-claude-fable-5.md) |
| Very high-volume classification and extraction | ❌ [Haiku 4.5](./03-anthropic-claude-haiku.md) |

---

## API Quick Reference

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 32000,
  "output_config": { "effort": "medium" },
  "system": "...",
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

> **Thinking**: adaptive and on by default — omit the field, or pass
> `thinking: {"type": "adaptive", "display": "summarized"}` to surface reasoning.
> `thinking: {"type": "disabled"}` is supported. Manual extended thinking
> (`{"type": "enabled", "budget_tokens": N}`) returns a 400.
>
> **Rejected parameters**: `temperature`, `top_p`, `top_k`, and assistant-turn
> prefills return a 400 — new for Sonnet-class models. Use prompt language for tone
> and variety, and `output_config.format` for machine-readable output.
>
> **Tokenizer**: ~30% more tokens than Sonnet 4.6 for the same text. Re-run token
> counting and raise `max_tokens` (up to 128K) before production.
>
> **Computer use**: `computer_20251124`, up to 2576px / 3.75MP. 1080p is the
> recommended balance; 720p or 1366×768 for cost-sensitive workloads.
>
> **Prompt caching** minimum is 512 tokens. Hold `effort` constant within a cached
> conversation.
>
> **Refusals**: cybersecurity classifiers return `stop_reason: "refusal"` as HTTP 200 —
> check `stop_details.category`.

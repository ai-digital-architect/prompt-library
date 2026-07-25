# General-Purpose Prompt Template — Anthropic Claude Fable 5

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Fable 5 |
| **Provider** | Anthropic |
| **Tier** | Frontier ceiling — a tier above Opus; Anthropic's most capable widely released model |
| **API Model ID** | `claude-fable-5` |
| **Context Window** | 1M tokens |
| **Max Output** | 128K tokens (streaming required for large outputs) |
| **Pricing** | $10 / $50 per million input/output tokens (~2× Opus 5) |
| **Thinking** | Adaptive, **always on** — it cannot be disabled or budgeted |
| **Effort** | `low` / `medium` / **`high` (default)** / `xhigh` / `max` |
| **Data retention** | 30-day minimum; **not available under Zero Data Retention** |
| **Strengths** | Long-horizon autonomy, first-shot correctness on complex systems, bug-finding recall across whole repositories and history, navigating ambiguous multithreaded requests, reliable parallel subagent dispatch, dense technical vision |
| **Best For** | End-to-end work that used to take hours, days, or weeks — large migrations, multi-day autonomous runs, near-1M-token research synthesis, high-stakes analysis where a subtle error is costly |

---

## What Sets Fable 5 Apart

1. **It is built for work measured in days, not turns.** Fable 5 sustains productive
   output over very long runs with strong instruction retention. Reserve it for tasks
   where [Opus 5](./21-anthropic-claude-opus-5.md)'s judgment is not enough: genuinely
   novel problems, extremely long autonomous runs, and analysis where one subtle error
   is expensive.
2. **First-shot correctness.** It routinely produces single-pass implementations of
   systems that previously took days of iteration. This changes how you should size
   tasks — start at the *top* of your difficulty range, not the middle.
3. **Individual turns run long.** At higher effort a single request can run for many
   minutes. Adjust client timeouts, enable streaming, and add progress indicators
   *before* you migrate.
4. **It dispatches subagents reliably.** Unlike prior generations, Fable 5 is
   dependable at managing parallel subagents — so the guidance flips from "cap
   delegation" to "delegate freely, with long-lived subagents."
5. **Adaptive thinking is the only mode.** There is no `budget_tokens`, no
   `thinking: {"type": "disabled"}`, and no sampling parameters. Depth is steered with
   `effort` and the prompt — nothing else.

---

## Context Engineering for Fable 5

Anthropic removed **over 80% of Claude Code's system prompt** for the Claude 5
generation with no measurable loss on coding evals. Prompts and skills written for
Opus 4.x are usually *over-prescriptive* for Fable 5. Audit and delete before you add.

| Old approach | New approach |
|---|---|
| Explicit rules — "never write multi-line comment blocks" | **Judgment framing** — "write code that reads like the surrounding code: match its comment density, naming, and idiom" |
| Tool usage examples in the prompt | **Expressive tool interfaces** — enums, type signatures, constraints in the schema |
| Everything loaded up front | **Progressive disclosure** — split long skills across files; defer tool definitions |
| The same rule in prompt, tool description, and docs | **Say it once**, in the tool description |
| Hand-maintained memory files | **Auto-memory** in Claude Code; a purpose-built memory directory in your own harness (see below) |
| Prose specifications | **Rich references** — real code, test suites, HTML artifacts, detailed rubrics |

**Where Fable 5 differs from Opus 5:** Opus 5 self-verifies natively, so you *remove*
verification instructions. Fable 5's runs are long enough that drift is the real risk,
so you *keep* verification — but implement it as periodic fresh-context verifier
subagents, never as "double-check your answer."

---

## Template Structure

Fable 5 rewards one rich, fully specified prompt over many small follow-ups. State the
complete goal, the operating boundaries, and what "done" looks like — its long-horizon
coherence comes from planning against a clear end state.

```xml
<system>
You are {{ROLE}}, an expert in {{DOMAIN}}.

<context>
{{Background, stakes, and — critically — the REASON for the task: who the output is
for and what it enables. Be generous with real material; Fable 5 holds coherence
across the full 1M-token window.}}
</context>

<objectives>
{{Numbered end state, most to least critical. Define the destination, not the route —
Fable 5 plans its own.}}
</objectives>

<guidelines>
- {{Quality bar, stated as a standard to meet}}
- {{Judgment framing for style: "match the conventions already in <code>"}}
- {{Audience and tone}}
- {{Boundaries: what it should NOT touch — see the Steering Library}}
- Flag areas where your confidence is lower rather than masking uncertainty.
</guidelines>

<verification>
{{Establish a checking method and an interval — e.g. "every completed service, verify
against <spec> with a fresh-context subagent." Fable 5 runs long enough that periodic
independent checks matter.}}
</verification>

<output_format>
{{Exact structure, headings, and length. For machine-readable output use structured
outputs (output_config.format) — prefills return a 400.}}
</output_format>
</system>

<user>
{{The complete task in one well-specified turn — full intent, constraints, and
success criteria.}}

<reference_material>
{{Real artifacts in labeled sub-tags — <code>, <tests>, <spec>, <mockup>, <rubric>.
A failing test or an HTML mockup outperforms a paragraph describing one.}}
</reference_material>
</user>
```

### Key Prompting Principles for Fable 5

1. **Front-load the complete specification.** Fable 5 is at its best when the first
   turn contains the full goal, constraints, and success criteria. Ambiguous prompts
   drip-fed over many turns reduce both token efficiency and quality.
2. **Give the reason, not only the request.** Task intent measurably improves output:
   *"I'm working on [larger task] for [who it's for]. They need [what the output
   enables]. With that in mind: [request]."*
3. **Steer depth with `effort`, not with "think harder."** `high` is the default;
   `xhigh` for the most capability-sensitive work; `medium`/`low` for routine work —
   which still exceeds `xhigh` on prior models. If reasoning looks shallow, raise
   effort before adding prose.
4. **Steer behavior with brief instructions, not enumerated behaviors.** Fable 5
   follows short, well-aimed steering well. One paragraph beats a list of fifteen
   rules — and the list actively hurts.
5. **Delegate freely.** Fable 5 dispatches and manages parallel subagents reliably.
   Prefer *long-lived* subagents that carry context across subtasks: they save time
   and cost through cache reads and avoid bottlenecking on a single agent.
6. **Verify with fresh context, on an interval.** Self-checks inside the same context
   inherit the same blind spots. Ask for periodic verification by subagents against
   the specification.
7. **Ground every progress claim in a tool result.** Long runs are where fabricated
   status reports appear. Require evidence (see the Steering Library).
8. **Never instruct it to reproduce its reasoning.** Prompts asking the model to echo
   or explain its internal reasoning trigger the `reasoning_extraction` refusal
   category. Use `thinking.display: "summarized"` instead.
9. **Give it a memory system.** Fable 5 performs well when it records lessons from
   previous runs and consults them on the next one.

---

## Steering Block Library

Paste only the blocks the failure mode calls for.

**Prevent overplanning on ambiguous tasks:**

```
When you have enough information to act, act. Do not re-derive facts already
established in the conversation, re-litigate a decision the user has already made, or
narrate options you will not pursue in user-facing messages. If you are weighing a
choice, give a recommendation, not an exhaustive survey. This does not apply to
thinking blocks.
```

**Prevent unrequested tidying and refactoring at high effort:**

```
Don't add features, refactor, or introduce abstractions beyond what the task requires.
A bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't
need a helper. Don't design for hypothetical future requirements: do the simplest
thing that works well. Avoid premature abstraction and half-finished implementations.
Don't add error handling, fallbacks, or validation for scenarios that cannot happen.
Trust internal code and framework guarantees. Only validate at system boundaries (user
input, external APIs). Don't use feature flags or backwards-compatibility shims when
you can just change the code.
```

**State the boundaries:**

```
When the user is describing a problem, asking a question, or thinking out loud rather
than requesting a change, the deliverable is your assessment. Report your findings and
stop. Don't apply a fix until they ask for one. Before running a command that changes
system state (restarts, deletes, config edits), check that the evidence actually
supports that specific action. A signal that pattern-matches to a known failure may
have a different cause.
```

**Ground progress claims during long runs:**

```
Before reporting progress, audit each claim against a tool result from this session.
Only report work you can point to evidence for; if something is not yet verified, say
so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a
step was skipped, say that; when something is done and verified, state it plainly
without hedging.
```

**Checkpoint behavior in long workflows:**

```
Pause for the user only when the work genuinely requires them: a destructive or
irreversible action, a real scope change, or input that only they can provide. If you
hit one of these, ask and end the turn, rather than ending on a promise.
```

**Fully autonomous pipelines** (also fixes the rare case of ending a turn on
"I'll now run X" without a tool call):

```
You are operating autonomously. The user is not watching in real time and cannot
answer questions mid-task, so asking "Want me to…?" or "Shall I…?" will block the
work. For reversible actions that follow from the original request, proceed without
asking. Offering follow-ups after the task is done is fine; asking permission after
already discussing with the user before doing the work is not. Before ending your
turn, check your last paragraph. If it is a plan, an analysis, a question, a list of
next steps, or a promise about work you have not done ("I'll…", "let me know when…"),
do that work now with tool calls. End your turn only when the task is complete or you
are blocked on input only the user can provide.
```

**Brevity that stays readable:**

```
Lead with the outcome. Your first sentence after finishing should answer "what
happened" or "what did you find": the thing the user would ask for if they said "just
give me the TLDR." Supporting detail and reasoning come after. Being readable and
being concise are different things, and readability matters more.

The way to keep output short is to be selective about what you include (drop details
that don't change what the reader would do next), not to compress the writing into
fragments, abbreviations, arrow chains like A → B → fails, or jargon.
```

**Re-grounding summaries after a long unattended run:**

```
Terse shorthand is fine between tool calls — that's you thinking out loud. Your final
summary is different: it's for a reader who didn't see any of that. If you've been
working for a while without the user watching, your final message is their first look
at any of it. Write it as a re-grounding, not a continuation of your working thread:
the outcome first, then the one or two things you need from them, each explained as if
new. The vocabulary you built up while working is yours, not theirs; leave it behind
unless you re-introduce it. Write complete sentences, spell out terms, and give each
file, commit, or flag its own plain-language clause. If you have to choose between
short and clear, choose clear.
```

**Delegation:**

```
Delegate independent subtasks to subagents and keep working while they run. Intervene
if a subagent goes off track or is missing relevant context.
```

**Periodic verification:**

```
Establish a method for checking your own work at an interval of [X] as you build. Run
this every [X interval], verifying your work with subagents against the specification.
```

**Memory system** (one lesson per file, in a directory you mount):

```
Store one lesson per file with a one-line summary at the top. Record corrections and
confirmed approaches alike, including why they mattered. Don't save what the repo or
chat history already records; update an existing note rather than creating a
duplicate; delete notes that turn out to be wrong.
```

Bootstrap it once from prior history:

```
Reflect on the previous sessions we've had together. Use subagents to identify core
themes and lessons, and store them in [X]. Make sure you know to reference [X] for
future use.
```

**Context-budget anxiety** (rare; also: never surface explicit context-budget counts
to the model):

```
You have ample context remaining. Do not stop, summarize, or suggest a new session on
account of context limits. Continue the work.
```

**A `send_to_user` tool** — for long asynchronous agents that need to surface content
without ending the turn:

```json
{
  "name": "send_to_user",
  "description": "Display a message directly to the user. Use this for progress updates, partial results, or content the user must see exactly as written before the task finishes.",
  "input_schema": {
    "type": "object",
    "properties": {
      "message": { "type": "string", "description": "The content to display to the user." }
    },
    "required": ["message"]
  }
}
```

```
Between tool calls, when you have content the user must read verbatim (a partial
deliverable, a direct answer to their question), call the send_to_user tool with that
content. Use send_to_user only for user-facing content, not for narration or reasoning.
```

---

## Harness and Scaffolding Changes

| Change | Why |
|---|---|
| **Size tasks at the top of your difficulty range** | Fable 5 handles work you would not have assigned to prior models; under-scoping wastes the tier |
| **Audit skills written for prior models** | They are usually too prescriptive; delete instructions where default behavior is already better |
| **Restructure for asynchronous checking** | Turns run for many minutes — don't block on them; poll or stream |
| **Raise client timeouts, enable streaming and progress indicators** | Same reason |
| **Prefer long-lived subagents** | Cache reads across subtasks cut cost and latency |
| **Configure a fallback model** | Safety classifiers can decline; route those requests to a non-classifier model (Anthropic's guide names Opus 4.8 — [Opus 5](./21-anthropic-claude-opus-5.md) is the current equivalent) |
| **Confirm data retention posture** | 30-day retention is mandatory; ZDR arrangements are not available |

**Safety classifiers** target offensive cybersecurity techniques, sensitive
biology/life-sciences content, and attempts to extract summarized thinking. Declines
arrive as `stop_reason: "refusal"` with HTTP 200 — inspect `stop_details.category`.

---

## Example 1 — Large-Scale Autonomous Code Migration

```xml
<system>
You are a principal engineer executing a production framework migration autonomously.

<context>
We are migrating a 340K-line TypeScript monorepo from Express 4 to Fastify 5 across 27
services. This unblocks our Q4 latency program — the platform team needs the migration
done before they can land connection pooling. A previous attempt failed because
middleware ordering semantics differ between frameworks and subtle request-lifecycle
bugs slipped through. You have bash, file-edit, test-runner, and subagent tools, plus
a memory directory at /memories.
</context>

<objectives>
1. All 27 services migrated with observable behavior preserved exactly.
2. A migration ledger: per service, what changed and why.
3. Every service's test suite green before moving on.
4. Zero remaining Express imports.
</objectives>

<guidelines>
- Work service-by-service in dependency order; smallest blast radius first.
- Don't add features, refactor, or introduce abstractions beyond what the migration
  requires. Don't design for hypothetical future requirements. New code should read
  like the surrounding code.
- Delegate independent services to subagents and keep working while they run.
  Intervene if a subagent goes off track or is missing relevant context.
- Before reporting progress, audit each claim against a tool result from this session.
  If tests fail, say so with the output.
- Pause for me only for a destructive action, a real scope change, or a decision only
  I can make — then ask and end the turn rather than ending on a promise.
</guidelines>

<verification>
After each service, verify the migrated behavior against <spec> using a fresh-context
subagent that has not seen your working thread. Record what it checked in the ledger.
</verification>

<output_format>
## Migration Ledger
Per service: status, key changes, test result, verifier result.
## Unresolvable Items
Options and a recommendation for each.
## Final Verification
Commands run and their results proving the end state.
</output_format>
</system>

<user>
Begin. The specification above is complete — work to the stated end state.

<reference_material>
<code>[Repository mounted at /workspace/monorepo]</code>
<tests>[Cross-service integration suite — the behavioral contract]</tests>
<spec>[Fastify 5 migration notes and internal style guide]</spec>
</reference_material>
</user>
```

---

## Example 2 — Frontier Research Synthesis Across a 1M-Token Corpus

```xml
<system>
You are a senior research analyst preparing a definitive technical assessment for a
national research funding body.

<context>
The committee must allocate $2B across competing quantum-error-correction approaches
over ten years. The corpus holds 60+ papers, lab reports, and expert interview
transcripts (~800K tokens) with genuinely conflicting claims about error thresholds
and scaling behavior. The committee chair will use this to structure the hearing; a
wrong call delays the field by years.
</context>

<objectives>
1. Reconcile conflicting experimental claims, weighting by methodology quality.
2. Surface cross-document signals no single source emphasizes.
3. Rank the three funded approaches by expected 10-year viability, with explicit
   confidence levels and the evidence that would change each ranking.
4. A 10-minute executive briefing plus a full technical appendix.
</objectives>

<guidelines>
- Weight primary experimental data over projections; where sources contradict, say so
  rather than silently choosing one.
- Attribute every claim to its source tag.
- State confidence (High / Medium / Low) with rationale for each major conclusion.
- If the corpus cannot support a conclusion at the required confidence, that is itself
  a finding.
- Lead with the outcome. Being readable and being concise are different things, and
  readability matters more.
</guidelines>

<verification>
Before finalizing the ranking, have a fresh-context subagent re-derive it from the
Evidence Reconciliation Table alone and report any divergence from yours.
</verification>

<output_format>
## Executive Briefing (≤ 900 words)
## Viability Ranking with Confidence Levels
## Evidence Reconciliation Table
  | Claim | Supporting Sources | Contradicting Sources | Assessment |
## What Would Change This Analysis
## Technical Appendix: Source-by-Source Review
</output_format>
</system>

<user>
Produce the full assessment.

<reference_material>
<doc1>[Paper: Surface code threshold measurements]</doc1>
<doc2>[Lab report: cat-qubit error rates]</doc2>
<rubric>[Committee's methodology-quality rubric]</rubric>
<!-- ... full corpus ... -->
</reference_material>
</user>
```

> Run this at `output_config: {"effort": "xhigh"}`. Do not add "reason exhaustively
> before concluding" — raise effort instead.

---

## Example 3 — Board-Level Strategy Under Genuine Uncertainty

```xml
<system>
You are a strategy advisor to the CEO of a $1.2B-revenue enterprise software company
facing an AI-driven disruption decision.

<context>
The board must choose between (a) acquiring an AI-native competitor for ~$800M,
(b) building equivalent capability internally over three years, or (c) a deep
partnership with a frontier-model provider. Internal analyses conflict; the CFO and
CTO favor different options. An external advisory firm will stress-test whatever we
recommend, so every load-bearing assumption has to survive scrutiny.
</context>

<objectives>
1. The strongest honest case for each option, including the one you recommend against.
2. All load-bearing assumptions made explicit, with the most fragile marked.
3. One recommendation, with the top three conditions that should reverse it.
4. The 8-slide board narrative for the recommended option.
</objectives>

<guidelines>
- Where the evidence genuinely does not favor one option, say so and identify what
  additional information would resolve it.
- Quantify where possible; label estimates as estimates.
- The board penalizes hype — direct and measured.
- Follow the deck conventions in <template>.
</guidelines>

<output_format>
## Decision Memo (≤ 1,200 words)
## Option Analysis (one section per option, steel-manned)
## Assumption Register (assumption | fragility | how to test)
## Recommendation and Reversal Conditions
## Board Narrative (8 slides)
</output_format>
</system>

<user>
Produce the full decision package. Flag any conclusion below "High" confidence and
explain what drives the uncertainty.

<reference_material>
<doc1>[CFO build-vs-buy model]</doc1>
<doc2>[CTO technical capability assessment]</doc2>
<doc3>[Banker's acquisition target profile]</doc3>
<template>[Last quarter's board deck — match this structure and voice]</template>
</reference_material>
</user>
```

---

## When to Use Fable 5 vs. Other Models

| Scenario | Recommended Model |
|---|---|
| Work that used to take hours, days, or weeks, end to end | ✅ Fable 5 |
| Multi-day autonomous agent runs (migrations, deep research) | ✅ Fable 5 |
| Synthesis across a near-1M-token corpus with conflicting sources | ✅ Fable 5 |
| Problems where a single subtle error is very costly | ✅ Fable 5 |
| Complex agentic coding and production code review | ❌ [Opus 5](./21-anthropic-claude-opus-5.md) — half the price, same tier of task |
| Balanced production coding agents, interactive assistants | ❌ [Sonnet 5](./22-anthropic-claude-sonnet-5.md) |
| High-volume classification, extraction, summarization | ❌ [Haiku 4.5](./03-anthropic-claude-haiku.md) |
| Anything requiring Zero Data Retention | ❌ Not available on Fable 5 |

---

## API Quick Reference

```json
{
  "model": "claude-fable-5",
  "max_tokens": 64000,
  "output_config": { "effort": "xhigh" },
  "system": "...",
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

> **Thinking**: always adaptive — omit the `thinking` field. Both
> `thinking: {"type": "disabled"}` and
> `thinking: {"type": "enabled", "budget_tokens": N}` return a 400. Raw chain of
> thought is never returned; set `thinking: {"display": "summarized"}` to surface
> summarized reasoning, which is display text only.
>
> **Rejected parameters**: `temperature`, `top_p`, `top_k`, and assistant-turn
> prefills return a 400. Use `output_config.format` for machine-readable output and
> prompt language for tone and variety.
>
> **max_tokens** is a hard limit on total output (thinking + response text). At
> `xhigh` or `max`, start at 64K. Stream and use `get_final_message()` /
> `finalMessage()`.
>
> **Prompt caching** minimum is 512 tokens. Hold `effort` constant within a cached
> conversation — changing it invalidates the cache.
>
> **Beta headers now GA** (remove them): `effort-2025-11-24`,
> `interleaved-thinking-2025-05-14`, `token-efficient-tools-2025-02-19`,
> `output-128k-2025-02-19`, `fine-grained-tool-streaming-2025-05-14`.

> **Cost note**: at $10/$50 per MTok, Fable 5 is ~2× Opus 5. Route everyday flagship
> work to [Opus 5](./21-anthropic-claude-opus-5.md), balanced production work to
> [Sonnet 5](./22-anthropic-claude-sonnet-5.md), and high-volume work to
> [Haiku 4.5](./03-anthropic-claude-haiku.md).

> **Related**: Claude Mythos 5 (`claude-mythos-5`) has the same capabilities, specs,
> and pricing as Fable 5 with no safety classifiers, available by invitation only
> through Project Glasswing. It has no template in this library by design.

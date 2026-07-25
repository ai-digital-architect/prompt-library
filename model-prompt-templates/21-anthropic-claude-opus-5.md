# General-Purpose Prompt Template — Anthropic Claude Opus 5

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Opus 5 |
| **Provider** | Anthropic |
| **Tier** | Flagship — the recommended default for complex agentic coding and enterprise work |
| **API Model ID** | `claude-opus-5` |
| **Context Window** | 1M tokens (default *and* maximum) |
| **Max Output** | 128K tokens (up to 300K via the Message Batches API with beta header `output-300k-2026-03-24`) |
| **Pricing** | $5 / $25 per million input/output tokens |
| **Thinking** | Adaptive, **on by default**. Can only be disabled at effort `high` or below |
| **Effort** | `low` / `medium` / **`high` (default)** / `xhigh` / `max` |
| **Knowledge cutoff** | May 2026 |
| **Strengths** | Multi-file features and large refactors, high-precision code review, long-horizon agentic execution, vision (charts, diagrams, UI replication), multi-sheet spreadsheets and slide decks, subagent coordination |
| **Best For** | End-to-end feature work, production code review, long-horizon agent runs, office/document generation, writer-verifier multi-agent systems |

---

## What Sets Opus 5 Apart

1. **It finishes the job.** Opus 5 completes full tasks rather than leaving stubs or
   placeholders. It performs best when handed a complete task specification up front
   and left to run, rather than steered turn by turn.
2. **It verifies and corrects itself natively.** Self-verification and self-correction
   are default behaviors, not things you prompt for. Legacy "double-check your work"
   scaffolding now *costs* you tokens and triggers over-verification.
3. **`low` and `medium` effort are genuinely strong.** They deliver high quality at a
   fraction of the tokens and latency. Treat effort as your primary cost/latency
   control and re-run your effort sweeps — settings carried over from Opus 4.8 are
   probably wrong.
4. **It talks more.** Responses, narration, and written deliverables all run longer
   than prior Opus models by default. Effort controls *thinking volume, not response
   length* — lowering effort will not shorten the visible answer. Length is a prompt
   lever, not a parameter.
5. **It expands scope and delegates readily.** Both are strengths on open-ended work
   and liabilities on narrow tasks. Constrain them explicitly when the task is small.

---

## Context Engineering for Opus 5

Anthropic removed **over 80% of Claude Code's system prompt** for Opus 5 with no
measurable loss on coding evals. The lesson: guardrails written for earlier models
now *over-constrain* Opus 5. Before you add anything to a prompt, delete first.

### The six shifts

| Old approach (Opus 4.x era) | New approach (Opus 5) |
|---|---|
| Explicit rules — "never write multi-line comment blocks" | **Judgment framing** — "write code that reads like the surrounding code: match its comment density, naming, and idiom" |
| Tool usage examples in the prompt | **Expressive tool interfaces** — enums, type signatures, and constraints in the schema |
| Everything loaded up front | **Progressive disclosure** — skills and deferred tool loading; pull detail only when needed |
| The same rule repeated in prompt, tool description, and docs | **Say it once**, in the tool description |
| Hand-maintained memory files | **Auto-memory** — let the model record what matters; reserve files for gotchas |
| Prose specifications | **Rich references** — real code, test suites, HTML mockups, rubrics |

### Where each kind of context belongs

| Layer | Put here | Keep out |
|---|---|---|
| **System prompt** | Product context, role, operating boundaries, output contract | Anything the model can derive from the repo or the tools |
| **Project memory (`CLAUDE.md`)** | Repository-specific gotchas, non-default conventions, the *why* behind surprising choices | Directory layouts, dependency lists, architecture overviews |
| **Skills** | Domain-specific opinions and procedures, split across files so only the needed part loads | One giant always-on file |
| **References** | Actual code, tests, schemas, mockups, rubrics — `@`-mentioned or attached | Prose restatements of what the code already says |

> For each explicit rule in your current prompt, ask: *would Opus 5 infer this from
> the codebase or the tool schema alone?* If yes, delete it. In Claude Code, run
> `/doctor` to get a proposed set of cuts before you edit by hand.

---

## Template Structure

Keep the scaffold lean. Every line you add competes for attention with the reference
material that actually determines quality.

```xml
<system>
You are {{ROLE}}, an expert in {{DOMAIN}}.

<context>
{{Why this task exists, who consumes the result, and what makes it hard. Opus 5
holds coherence across the full 1M-token window — be generous with real material
and sparing with restated rules.}}
</context>

<objectives>
{{Numbered end state, most to least critical. Define what "done" looks like, not
the steps to get there. For agentic work, give the complete spec in this one turn.}}
</objectives>

<guidelines>
- {{The quality bar, stated as a standard to meet rather than a list of prohibitions}}
- {{Judgment framing for style: "match the conventions already in <code>"}}
- {{Audience and tone}}
- {{Only where the task is narrow}}: Deliver what was asked, at the scope intended.
- {{Only if you need terse output}}: paste a block from the Steering Library below.
</guidelines>

<output_format>
{{Exact structure, headings, and length. For machine-readable output use structured
outputs (output_config.format) — assistant-turn prefills return a 400.}}
</output_format>
</system>

<user>
{{The complete task in one well-specified turn — full intent, constraints, and
success criteria.}}

<reference_material>
{{Real artifacts in labeled sub-tags — <code>, <tests>, <spec>, <mockup>, <rubric>.
Prefer a failing test or an HTML mockup over a paragraph describing one.}}
</reference_material>
</user>
```

### Key Prompting Principles for Opus 5

1. **Delete before you add.** Verification instructions, re-check instructions,
   progress-summary scaffolding, and "be conservative" hedges are all net-negative on
   Opus 5. Removing them reduces cost with no quality loss.
2. **Give the full spec up front, then get out of the way.** Opus 5's long-horizon
   strength compounds with a well-specified end state. Progressive clarification over
   many turns costs efficiency and quality.
3. **Sweep effort from the bottom, not the top.** Start at the `high` default; test
   `low` and `medium` on your own evals before assuming you need more. Step up to
   `xhigh` for demanding coding and agentic work, `max` only when unconstrained
   spending is justified. Hold effort constant inside a cached conversation —
   changing it invalidates the cache.
4. **Control length with prose, not parameters.** Effort governs thinking, not output
   size. Use the conciseness and document-length blocks below.
5. **Frame style as judgment, not prohibition.** "Match the surrounding code" beats
   any list of banned constructs, and it transfers across codebases.
6. **Code review: ask for coverage, filter downstream.** "Only report high-severity
   issues" is followed literally and suppresses real findings. Ask for everything with
   confidence and severity ratings, then filter in a second pass.
7. **Let vision use tools.** Opus 5's vision is strongest when it can crop, zoom, and
   visually verify iteratively. Tool access is a more cost-effective lever than raising
   effort. Re-validate vision workarounds inherited from earlier models — most are no
   longer needed.
8. **Prefer thinking at low effort over thinking disabled.** For most tasks, thinking
   on at `low` beats thinking off at comparable cost, and it avoids the artifacts
   described below.

---

## Steering Block Library

Paste only the blocks you need. Each one targets a specific default behavior.

**Response length** — the single most commonly needed block:

```
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and
spend most of the response on the main answer. When asked to explain something, give
a high-level summary unless an in-depth explanation is specifically requested.
```

In a long system prompt, pair it with a short reminder near the end:

```
<tone_preference>
Keep outputs reasonably concise.
</tone_preference>
```

**Narration cadence in agentic sessions:**

```
Before your first tool call, say in one sentence what you're about to do. While
working, give a brief update only when you find something important or change
direction. When you finish, lead with the outcome: your first sentence should answer
"what happened" or "what did you find," with supporting detail after it for readers
who want it.
```

**Written deliverable length** (files, reports, Markdown written to disk):

```
Match the length of written documents to what the task needs: cover the substance,
but do not pad with filler sections, redundant summaries, or boilerplate.
```

**Scope discipline on narrow tasks:**

```
Deliver what was asked, at the scope intended. Make routine judgment calls yourself,
and check in only when different readings of the request would lead to materially
different work. If the request seems mistaken or a better approach exists, say so in
a sentence and continue with the task as asked rather than quietly narrowing,
widening, or transforming it. Finish the whole task, and stop short of actions that
are clearly beyond what was asked.
```

**Subagent delegation:**

```
Delegate to a subagent only for large tasks that are genuinely independent and
parallelizable, such as a wide multi-file investigation. Do not delegate work you can
finish yourself in a handful of tool calls, and do not use subagents to verify or
double-check your own work. If one subagent can complete the task, use one rather
than several, and keep spawn counts low.
```

**Correction narration** (for user-facing products):

```
Only correct an earlier statement when the error would change the user's code,
conclusions, or decisions. State corrections plainly and briefly, then continue the
task. For slips that change nothing for the user, make the fix and move on without
noting it.
```

**If you must run with thinking disabled** — one combined instruction mitigates both
known artifacts (tool calls leaking into visible text, and internal XML tags in the
response):

```
When you use a tool, you may say a brief sentence first. If no tool can express what
the user asked for, say so instead of guessing. Do not include internal or system XML
tags in your response.
```

> Naming thinking tags explicitly works *worse* than this general form. Also remove
> any system-prompt rule telling the model not to think or reason — those increase
> tag leakage.

---

## Migrating a Prompt from Opus 4.8

| Delete | Why |
|---|---|
| "Double-check your answer" / "re-verify before responding" | Compounds with native self-correction; pure cost |
| "Include a final verification step" / "use a subagent to verify" | Causes over-verification |
| "After every N tool calls, summarize progress" | Opus 5 narrates natively — tune the cadence instead |
| "Only report high-severity issues" / "be conservative" | Followed literally; suppresses real findings |
| Enumerated style prohibitions | Replace with "match the surrounding code" |
| Duplicated rules across prompt + tool descriptions | Say it once, in the tool description |
| Tool usage examples | Improve the tool schema instead |
| `budget_tokens`, `temperature`, `top_p`, `top_k`, prefills | Return a 400 |
| Beta headers `effort-2025-11-24`, `interleaved-thinking-2025-05-14`, `token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`, `fine-grained-tool-streaming-2025-05-14` | Now GA |

| Add | Why |
|---|---|
| A conciseness block | Default responses run longer |
| A document-length block | Files written to disk run longer |
| A scope block *(narrow tasks only)* | Opus 5 expands scope |
| A delegation cap *(if your harness has subagents)* | Opus 5 delegates readily |
| Handling for `stop_reason: "refusal"` | Cybersecurity classifiers return HTTP 200 with a refusal stop reason; inspect `stop_details.category` |

---

## Example 1 — Production Code Review (Coverage-First)

```xml
<system>
You are a principal engineer performing the final security and correctness review
before a production release.

<context>
The service issues OAuth 2.0 tokens for a B2B SaaS platform with 200K enterprise
users. An SSRF incident six months ago drove a validation refactor that has never
been fully audited. Your findings gate the release go/no-go call. A separate
triage pass will rank and filter whatever you produce.
</context>

<objectives>
1. Security vulnerabilities (OWASP Top 10 and beyond).
2. Correctness bugs: race conditions, off-by-one errors, improper error propagation.
3. An assessment of whether the validation changes actually close the prior SSRF.
4. Corrected code for every Critical and High finding.
</objectives>

<guidelines>
- Report every issue you find, including ones you are uncertain about or consider
  low-severity. Do not filter for importance or confidence at this stage — a separate
  verification step will do that. It is better to surface a finding that later gets
  filtered out than to silently drop a real bug. For each finding include your
  confidence level and an estimated severity so a downstream filter can rank them.
- Cite file, function, and line range. Distinguish confirmed exploitability from
  theoretical.
- Corrected code must match the conventions already present in <code> — its error
  handling idiom, naming, and comment density.
</guidelines>

<output_format>
## Summary
Overall assessment (3-4 sentences) and a release recommendation.

## Findings (all, unfiltered)
### [F-01] Title
- **Location**: file:function:line
- **Severity (est.)** / **Confidence**
- **Risk** / **Exploitability**: Confirmed or Theoretical
- **Corrected Code** (Critical/High only)

## SSRF Remediation Assessment
</output_format>
</system>

<user>
Review the OAuth service below. Coverage over filtering — surface everything.

<reference_material>
<code>[Full source files]</code>
<tests>[Existing security test suite — treat gaps here as findings]</tests>
</reference_material>
</user>
```

---

## Example 2 — End-to-End Feature Work (Long-Horizon Agentic)

```xml
<system>
You are a senior engineer implementing a feature end to end. You have bash,
file-edit, and test tools.

<context>
Our Python data platform (~90K lines) mixes three configuration systems: env vars,
YAML, and a homegrown ConfigStore. We are consolidating onto one typed layer
(pydantic-settings) with zero behavior change. CI takes ~12 minutes per full run.
The team is asleep; you have the night.
</context>

<objectives>
1. All configuration access goes through one typed settings module.
2. Every observable default and override-precedence rule is preserved exactly.
3. The full test suite is green at each commit, with new tests covering the
   precedence rules that currently lack coverage.
4. Zero remaining direct env/YAML/ConfigStore reads outside the new module.
</objectives>

<guidelines>
- Deliver what was asked, at the scope intended. Make routine judgment calls yourself
  and record them; check in only when different readings of the request would lead to
  materially different work. Finish the whole task, and stop short of actions that are
  clearly beyond what was asked.
- The new module should read like the rest of the codebase — match its typing style,
  module layout, and comment density.
- Give a brief update only when you find something important or change direction.
- If a behavior cannot be preserved exactly, document it with options and continue
  elsewhere rather than guessing.
- Match the length of written documents to what the task needs; no filler sections.
</guidelines>

<output_format>
## Morning Report
Outcome first: what is done, what remains, test status.
## Decisions Made Autonomously
## Items Needing a Human Decision
## Verification Evidence
Commands run and their results.
</output_format>
</system>

<user>
The specification above is complete. Work to the stated end state.

<reference_material>
<code>[Repository mounted at /workspace/platform]</code>
<tests>[Precedence test suite — the contract you must not break]</tests>
</reference_material>
</user>
```

> Note what is *absent*: no "verify your work before finishing," no "summarize every
> N steps," no enumerated style rules. Opus 5 supplies all three.

---

## Example 3 — Enterprise Document Work

```xml
<system>
You are general counsel's senior technology-transactions analyst.

<context>
We are renegotiating a master services agreement with our largest infrastructure
vendor ($45M/year). The vendor returned a redlined draft with 60+ changes and the
negotiation call is in 48 hours. Several edits look cosmetic but may shift liability
or data-ownership terms. The audience for the brief includes non-lawyers.
</context>

<objectives>
1. Classify every vendor change: cosmetic / substantive-acceptable /
   substantive-negotiate / unacceptable.
2. For each substantive change, the practical business consequence and our
   recommended counter-position.
3. Anything the vendor quietly REMOVED — deletions matter as much as insertions.
4. A one-page negotiation brief: top 5 issues, our positions, walk-away lines.
</objectives>

<guidelines>
- Quote the exact changed language and cite section numbers.
- Confidence-rate any reading that depends on jurisdiction or prior dealings.
- Match the length of the written output to what the task needs — the brief is one
  page and the table is the detail; do not restate one inside the other.
- Follow the formatting conventions in <template>.
</guidelines>

<output_format>
## Negotiation Brief (one page)
## Change-by-Change Analysis
  | # | Section | Change (quoted) | Classification | Consequence | Counter |
## Quiet Deletions
## Open Questions for the GC
</output_format>
</system>

<user>
Analyze the redline and produce both deliverables.

<reference_material>
<doc1>[Original MSA]</doc1>
<doc2>[Vendor redlined draft]</doc2>
<template>[Our standard negotiation brief — match this format exactly]</template>
</reference_material>
</user>
```

---

## When to Use Opus 5 vs. Other Models

| Scenario | Recommended Model |
|---|---|
| Complex agentic coding — multi-file features, large refactors | ✅ Opus 5 |
| Production code review and bug-finding | ✅ Opus 5 |
| Enterprise document and spreadsheet generation | ✅ Opus 5 |
| Long-horizon agent runs with subagent coordination | ✅ Opus 5 |
| Hardest novel problems, multi-day autonomous runs, near-1M-token synthesis | ⚠️ [Fable 5](./13-anthropic-claude-fable-5.md) — 2× the price |
| Balanced production coding agents, interactive assistants | ❌ [Sonnet 5](./22-anthropic-claude-sonnet-5.md) |
| High-volume classification, extraction, subagent workers | ❌ [Haiku 4.5](./03-anthropic-claude-haiku.md) |

---

## API Quick Reference

```json
{
  "model": "claude-opus-5",
  "max_tokens": 64000,
  "output_config": { "effort": "high" },
  "system": "...",
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

> **Thinking**: adaptive and on by default — omit the `thinking` field entirely.
> `thinking: {"type": "disabled"}` is accepted only at effort `high` or below;
> pairing it with `xhigh` or `max` returns a 400. Thinking text is omitted by
> default; set `thinking: {"type": "adaptive", "display": "summarized"}` to surface
> reasoning to users.
>
> **Rejected parameters**: `temperature`, `top_p`, `top_k`, `budget_tokens`, and
> assistant-turn prefills all return a 400. Use `output_config.format` (structured
> outputs) for machine-readable output and prompt language for tone and variety.
>
> **max_tokens** is a hard limit on *total* output — thinking plus response text.
> At `xhigh` or `max`, start at 64K so the model has room to think and act. Stream
> large requests and use `get_final_message()` / `finalMessage()`.
>
> **Prompt caching** minimum drops to 512 tokens (from 1,024). Hold `effort` constant
> within a cached conversation.
>
> **Refusals**: cybersecurity classifiers can return `stop_reason: "refusal"` as an
> HTTP 200 — check `stop_details.category`. Optional server-side fallback via
> `fallbacks: "default"` with beta header `server-side-fallback-2026-07-01`.

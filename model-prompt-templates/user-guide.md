---
post_title: "Model Prompt Templates — User Guide"
author1: "Prompt Library Team"
post_slug: "model-prompt-templates-user-guide"
microsoft_alias: "promptlibrary"
featured_image: "https://learn.microsoft.com/en-us/azure/ai-services/openai/media/overview/openai-overview.png"
categories:
  - "AI"
  - "Developer Tools"
tags:
  - "prompt-engineering"
  - "llm"
  - "anthropic"
  - "openai"
  - "google"
  - "model-templates"
  - "ai-assisted-engineering"
ai_note: "Content created with AI assistance."
summary: >
  A comprehensive guide to using the model prompt templates in this library.
  Covers all 22 templates across Anthropic Claude, Google Gemini, and OpenAI GPT-5
  model families, with selection guidance, template anatomy, and best practices
  for writing effective prompts. Anthropic coverage refreshed July 2026 for the
  Claude 5 generation (Fable 5, Opus 5, Sonnet 5).
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

## Overview

This folder contains 22 general-purpose prompt templates, one per major model
in the Anthropic Claude, Google Gemini, and OpenAI GPT-5 model families — see
[current-model-list.md](current-model-list.md). Each template provides:

- A **model profile** with key attributes, context window, and best-fit scenarios.
- A **template structure** with fill-in-the-blank scaffolding.
- **Prompting principles** specific to that model's behavior.
- **Worked examples** covering coding, architecture analysis, and communication tasks.

The three Claude 5-generation templates (Fable 5, Opus 5, Sonnet 5) additionally
carry a **Steering Block Library** — copy-paste instruction blocks that each fix one
specific default behavior — and a **migration table** listing what to delete from
prompts written for earlier models.

Use these templates as starting points. Adapt them to your domain, task, and
quality requirements.

---

## Template Index

| # | File | Model | Provider | Tier | Status (July 2026) |
|---|------|-------|----------|------|--------|
| 01 | [01-anthropic-claude-opus-4-5-4-6.md](01-anthropic-claude-opus-4-5-4-6.md) | Claude Opus 4.5 / 4.6 | Anthropic | Flagship (prior gen) | Legacy — see 21 |
| 02 | [02-anthropic-claude-sonnet-4-5-4-6.md](02-anthropic-claude-sonnet-4-5-4-6.md) | Claude Sonnet 4.5 / 4.6 | Anthropic | Balanced (prior gen) | Legacy — see 22 |
| 03 | [03-anthropic-claude-haiku.md](03-anthropic-claude-haiku.md) | Claude Haiku 4.5 | Anthropic | Fast frontier | **Current** |
| 04 | [04-google-gemini-3-pro.md](04-google-gemini-3-pro.md) | Gemini 3 Pro | Google DeepMind | Flagship (prior gen) | Legacy — see 18 |
| 05 | [05-google-gemini-3-flash.md](05-google-gemini-3-flash.md) | Gemini 3 Flash | Google DeepMind | Fast frontier | Preview — see 19 |
| 06 | [06-openai-gpt-5-1.md](06-openai-gpt-5-1.md) | GPT-5.1 | OpenAI | Balanced frontier | Deprecated — see 15 |
| 07 | [07-openai-gpt-5-2.md](07-openai-gpt-5-2.md) | GPT-5.2 | OpenAI | Flagship (prior gen) | Deprecated — see 15 |
| 08 | [08-openai-gpt-5-3.md](08-openai-gpt-5-3.md) | GPT-5.3 | OpenAI | Frontier (prior gen) | Deprecated — see 15 |
| 09 | [09-openai-gpt-5-2-codex.md](09-openai-gpt-5-2-codex.md) | GPT-5.2 Codex | OpenAI | Agentic coding | Deprecated — see 15 |
| 10 | [10-openai-gpt-5-3-codex.md](10-openai-gpt-5-3-codex.md) | GPT-5.3 Codex | OpenAI | Agentic coding | Deprecated — see 15 |
| 11 | [11-openai-gpt-5-4.md](11-openai-gpt-5-4.md) | GPT-5.4 | OpenAI | Affordable frontier | **Current** |
| 12 | [12-anthropic-claude-opus-4-6.md](12-anthropic-claude-opus-4-6.md) | Claude Opus 4.6 | Anthropic | Flagship (prior gen) | Legacy — see 21 |
| 13 | [13-anthropic-claude-fable-5.md](13-anthropic-claude-fable-5.md) | Claude Fable 5 | Anthropic | Frontier ceiling (above Opus) | **Current** |
| 14 | [14-anthropic-claude-opus-4-8.md](14-anthropic-claude-opus-4-8.md) | Claude Opus 4.8 | Anthropic | Flagship (prior gen) | Legacy — see 21 |
| 15 | [15-openai-gpt-5-5.md](15-openai-gpt-5-5.md) | GPT-5.5 | OpenAI | Flagship | **Current** |
| 16 | [16-openai-gpt-5-4-mini.md](16-openai-gpt-5-4-mini.md) | GPT-5.4 mini | OpenAI | Balanced / low latency | **Current** |
| 17 | [17-openai-gpt-5-4-nano.md](17-openai-gpt-5-4-nano.md) | GPT-5.4 nano | OpenAI | Fast / lowest cost | **Current** |
| 18 | [18-google-gemini-3-1-pro.md](18-google-gemini-3-1-pro.md) | Gemini 3.1 Pro | Google DeepMind | Flagship | **Current** (Preview) |
| 19 | [19-google-gemini-3-5-flash.md](19-google-gemini-3-5-flash.md) | Gemini 3.5 Flash | Google DeepMind | Fast frontier | **Current** (Stable) |
| 20 | [20-google-gemini-3-1-flash-lite.md](20-google-gemini-3-1-flash-lite.md) | Gemini 3.1 Flash-Lite | Google DeepMind | Fast / lowest cost | **Current** (Stable) |
| 21 | [21-anthropic-claude-opus-5.md](21-anthropic-claude-opus-5.md) | Claude Opus 5 | Anthropic | Flagship | **Current** |
| 22 | [22-anthropic-claude-sonnet-5.md](22-anthropic-claude-sonnet-5.md) | Claude Sonnet 5 | Anthropic | Balanced frontier | **Current** |

> **Intentionally excluded:** Anthropic's Claude Mythos 5 / Mythos Preview
> (limited-availability research models — skipped by design), the Gemini 2.5
> family (previous generation), and all media, realtime-voice, TTS,
> transcription, embedding, and robotics models — this library covers
> general-purpose text/reasoning prompting only.

---

## The Claude 5 Generation: What Changed

Anthropic removed **over 80% of Claude Code's system prompt** for the Claude 5
generation with no measurable loss on coding evaluations. Prompts, skills, and
harness scaffolding written for Claude 4.x models now *over-constrain* these models.
Before you add anything to a Claude 5 prompt, delete.

### The six shifts

| Old approach (Claude 4.x era) | New approach (Claude 5 generation) |
|---|---|
| Explicit rules — "never write multi-line comment blocks" | **Judgment framing** — "write code that reads like the surrounding code: match its comment density, naming, and idiom" |
| Tool usage examples in the prompt | **Expressive tool interfaces** — enums, type signatures, constraints in the schema |
| Everything loaded up front | **Progressive disclosure** — skills split across files, deferred tool loading |
| The same rule repeated in prompt, tool description, and docs | **Say it once**, in the tool description |
| Hand-maintained memory files | **Auto-memory**; reserve files for genuine gotchas |
| Prose specifications | **Rich references** — real code, test suites, HTML mockups, rubrics |

### What to delete from inherited prompts

- "Double-check your answer" / "re-verify before responding" — these models
  self-correct, and the instruction compounds into wasted tokens.
- "Include a final verification step" / "use a subagent to verify your own work" —
  causes over-verification on Opus 5. *(Fable 5 is the exception: its runs are long
  enough that periodic **fresh-context verifier subagents** remain valuable.)*
- "After every N tool calls, summarize progress" — narration is native now; describe
  the desired *cadence* instead.
- "Only report high-severity issues" / "be conservative" — followed literally,
  suppressing real findings. Ask for coverage and filter downstream.
- Enumerated style prohibitions — replace with "match the surrounding code."
- `budget_tokens`, `temperature`, `top_p`, `top_k`, and assistant-turn prefills —
  all return a 400 across the Claude 5 generation.

### Where each kind of context belongs

| Layer | Put here | Keep out |
|---|---|---|
| **System prompt** | Product context, role, operating boundaries, output contract | Anything derivable from the repo or the tool schemas |
| **Project memory (`CLAUDE.md`)** | Repository-specific gotchas, non-default conventions, the *why* behind surprising choices | Directory layouts, dependency lists, architecture overviews |
| **Skills** | Domain-specific opinions and procedures, split so only the needed part loads | One giant always-on file |
| **References** | Real code, tests, schemas, mockups, rubrics | Prose restatements of what the code already says |

> In Claude Code, run `/doctor` to get a proposed set of cuts to your skills and
> `CLAUDE.md` before editing by hand.

---

## Model Families

### Anthropic Claude

Four tiers cover the full range of latency and depth requirements. (Claude
Mythos 5 / Mythos Preview are limited-availability research models and have no
template by design.)

#### Claude Fable 5 — Frontier Ceiling :sparkles:

- **Context window:** 1M tokens | **Max output:** 128K tokens
- **Pricing:** $10 / $50 per million input/output tokens
- **Retention:** 30-day minimum — **not available under Zero Data Retention**
- **Use when:** end-to-end work that used to take hours, days, or weeks — the
  hardest novel problems, multi-day autonomous agent runs, near-1M-token research
  synthesis, work where a subtle error is very costly.
- **Key technique:** One rich, fully specified prompt with the complete end state
  plus the *reason* for the task; adaptive thinking is the only mode (it cannot be
  disabled or budgeted) — steer depth with `output_config.effort` (`high` default,
  `xhigh` for coding/agentic). Delegate freely to long-lived subagents, ground
  progress claims in tool results, and verify on an interval with fresh-context
  subagents. Individual turns can run for many minutes: raise client timeouts and
  stream.

#### Claude Opus 5 — Flagship Daily Driver for Hard Tasks

- **Context window:** 1M tokens (default and maximum) | **Max output:** 128K tokens
  (300K via Message Batches with beta header `output-300k-2026-03-24`)
- **Pricing:** $5 / $25 per million input/output tokens
- **Use when:** complex agentic coding — multi-file features and large refactors,
  production code review and bug-finding, enterprise document and spreadsheet work,
  long-horizon agent runs with subagent coordination.
- **Key technique:** Full task spec up front, then get out of the way. Remove
  verification and re-check instructions — Opus 5 does both natively. Control length
  with prose, not effort (effort governs thinking volume, not response length).
  Constrain scope and cap delegation on *narrow* tasks. Sweep effort from `low`
  upward rather than defaulting to the ceiling.
- **Prior generations:** Opus 4.5/4.6/4.8 remain active — see templates 01, 12, 14.

#### Claude Sonnet 5 — Best Speed-to-Intelligence Ratio

- **Context window:** 1M tokens | **Max output:** 128K tokens
- **Pricing:** $3 / $15 per million input/output tokens (introductory $2 / $10
  through Aug 31, 2026)
- **Use when:** production coding agents, multi-tool workflows, structured
  extraction and predictable API pipelines, frontend generation, computer use,
  latency-sensitive assistants.
- **Key technique:** State the *scope* of every instruction — Sonnet 5 follows
  literally and will not generalize silently. Multishot examples over rules. Set
  effort one rung lower than on Sonnet 4.6 (`medium` on 5 ≈ `high` on 4.6). Re-run
  token counting: the new tokenizer produces ~30% more tokens for the same text.
- **Prior generations:** Sonnet 4.5/4.6 remain active — see template 02.

#### Claude Haiku 4.5 — Speed and Cost Efficiency

- **Context window:** 200K tokens | **Max output:** 64K tokens
- **Pricing:** $1 / $5 per million input/output tokens
- **Use when:** high-volume pipelines, real-time assistants, batch processing,
  classification, extraction, subagent task execution.
- **Key technique:** Lean prompts with explicit output formats; one or two
  few-shot examples; design for pipeline reuse (one unit of work per call).

---

### Google Gemini

All current Gemini models share a **1M token context window** and native
multimodal processing — the primary differentiators from other families.
(Gemini 2.5 and media/TTS/Live models are out of scope for this library.)

#### Gemini 3.1 Pro — Flagship Reasoning + Multimodal (Preview)

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $2 / $12 per million tokens (≤200K prompt); $4 / $18 above 200K
- **Use when:** the deepest reasoning in the Gemini lineup — multi-modal
  analysis, scientific reasoning, agentic coding, long-document processing.
- **Key technique:** Context first, instruction last; thinking is always on
  (defaults to `thinking_level: "high"`, cannot be disabled); keep sampling
  parameters at defaults; ground with Google Search for current facts.

#### Gemini 3.5 Flash — Newest Stable Fast Frontier

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $1.50 / $9.00 per million input/output tokens
- **Use when:** interactive agents, production pipelines, agentic tool use at
  speed — Google reports large agentic-benchmark gains and ~68% better token
  efficiency vs. prior Flash.
- **Key technique:** Defaults to `thinking_level: "medium"` — raise to `high`
  for harder reasoning; keep prompts focused; pair with 3.1 Pro for hybrid
  workflows (Flash inner loop, Pro outer loop).

#### Gemini 3.1 Flash-Lite — Lowest Cost / Highest Throughput (Stable)

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $0.25 / $1.50 per million input/output tokens
- **Use when:** high-volume classification, extraction, routing, and templated
  generation where throughput and cost dominate.
- **Key technique:** Defaults to `thinking_level: "minimal"` for speed —
  escalate selectively; strict output schemas and few-shot examples.

#### Gemini 3 Pro / 3 Flash — Prior Generation

Gemini 3 Pro is superseded by 3.1 Pro; Gemini 3 Flash ($0.50 / $3.00) remains
in Preview alongside the stable 3.5 Flash. Templates 04 and 05 remain valid
for existing deployments.

---

### OpenAI GPT-5

The current lineup is GPT-5.5 (flagship) plus the GPT-5.4 family (standard /
mini / nano). GPT-5.1–5.3 and the Codex variants are deprecated, with
retirements announced for July–August 2026 — their templates (06–10) remain
for existing deployments.

#### GPT-5.5 — Current Flagship for Reasoning and Coding

- **Context window:** 1,050,000 tokens | **Max output:** 128K tokens
- **Pricing:** $5.00 / $30.00 per million input/output tokens
- **Use when:** complex reasoning and coding (OpenAI's recommendation),
  agentic workflows with large tool surfaces, high-stakes professional work.
- **Key technique:** Outcome-first prompts (goal, success criteria, output
  shape — not step-by-step process); `reasoning_effort` `none` → `xhigh`
  (default `medium`); its reasoning efficiency means fewer reasoning tokens
  for equal results, so the flagship can be cheaper end-to-end.

#### GPT-5.4 — Affordable Frontier General Purpose

- **Context window:** 1,050,000 tokens | **Max output:** 128K tokens
- **Pricing:** $2.50 / $15.00 per million input/output tokens
- **Use when:** high-stakes technical work, long-context professional analysis,
  complex coding tasks, and multi-step workflows where success criteria matter.
- **Key technique:** Define the end state, operating rules, and deliverables
  explicitly; separate goals from constraints; ask for verifiable outputs such
  as test plans, risk tables, and acceptance criteria.

#### GPT-5.4 mini — Balanced Cost / Latency

- **Use when:** production pipelines, summarization, mid-complexity coding,
  components of larger systems where GPT-5.4 quality isn't required.
- **Key technique:** More literal than the flagship — provide explicit
  scaffolding, concrete examples, and tight output formats.

#### GPT-5.4 nano — High-Volume / Lowest Cost

- **Use when:** classification, extraction, routing, and other single-step
  tasks at very high volume.
- **Key technique:** One unit of work per call; avoid multi-step orchestration
  (per OpenAI's guidance); strict schemas and few-shot examples.

#### GPT-5.1 / 5.2 / 5.3 and Codex Variants — Deprecated

No longer listed in OpenAI's model docs; announced retirements July 23 –
August 10, 2026, with GPT-5.5 as the designated replacement (including for
coding/Codex workloads). See templates 06–10 for migration banners.

---

## Choosing the Right Model

Use this decision tree as a starting point.

```
Is the task code-focused and multi-file / long-horizon?
├── Yes → Claude Opus 5 (agentic coding) or GPT-5.5 (complex coding)
│         └── Multi-day autonomous runs / hardest novel problems → Claude Fable 5
│             └── ...but Zero Data Retention required → stay on Opus 5
└── No
    ├── Does it involve images, audio, video, or PDFs?
    │   ├── Need speed → Gemini 3.5 Flash
    │   └── Need depth → Gemini 3.1 Pro
    ├── Is cost or latency the primary constraint?
    │   ├── Very high volume, simple tasks → Claude Haiku 4.5,
    │   │   Gemini 3.1 Flash-Lite, or GPT-5.4 nano
    │   └── Moderate volume, balanced tasks → Claude Sonnet 5,
    │       Gemini 3.5 Flash, or GPT-5.4 mini
    └── Is this professional / high-stakes work?
        ├── Deep nuance / judgment required → Claude Opus 5 (or Fable 5)
        └── Expert-level professional → GPT-5.5 or GPT-5.4
```

### Quick Reference: Model vs. Use Case

| Use Case | Recommended Model |
|----------|------------------|
| Production coding agent (multi-tool) | Claude Sonnet 5 |
| Multi-file feature work or a large refactor | Claude Opus 5 |
| Code review — production release | Claude Opus 5 |
| Hardest novel problems / multi-day autonomous runs | Claude Fable 5 |
| High-volume extraction / classification | Claude Haiku 4.5, Gemini 3.1 Flash-Lite, or GPT-5.4 nano |
| Multi-modal document analysis | Gemini 3.1 Pro |
| Real-time interactive assistant | Claude Sonnet 5, Gemini 3.5 Flash, or Claude Haiku 4.5 |
| Frontend / UI generation, computer use | Claude Sonnet 5 |
| Financial modeling / legal analysis | GPT-5.5 |
| Cross-functional technical strategy with clear deliverables | GPT-5.4 |
| Production summarization pipelines | GPT-5.4 mini or Gemini 3.5 Flash |
| Full-stack app from scratch / large codebase migration | Claude Opus 5 or GPT-5.5 |
| Architecture strategy — board level | Claude Opus 5 or GPT-5.5 |

---

## Template Anatomy

Every template in this library follows the same structure. Here is how to read
and fill in each section.

### Model Profile Table

A quick-reference table covering attributes, context window, pricing, and
best-fit scenarios. Read this first to confirm you have the right model.

### Template Structure

A scaffold with `{{PLACEHOLDER}}` variables. Replace each placeholder with
your actual content:

- `{{ROLE}}` — the persona the model should adopt (e.g., "a senior Go engineer").
- `{{DOMAIN}}` — the subject area (e.g., "distributed systems").
- `{{TASK}}` — a concise, direct description of what to accomplish.
- `{{CONSTRAINTS}}` — hard limits on what the model may or may not do.
- `{{OUTPUT_FORMAT}}` — the exact structure, sections, and length expected.

### Key Prompting Principles

Model-specific guidance derived from how that model responds differently from
others. Always read this section — the same instruction phrased differently
can produce markedly different output quality depending on the model.

### Steering Block Library *(Claude 5 generation only)*

Copy-paste instruction blocks, each targeting one specific default behavior:
response length, narration cadence, scope discipline, delegation, progress
grounding, memory, and so on. Paste only the blocks your failure mode calls for —
adding all of them recreates the over-constraint problem these models were built
to escape.

### Worked Examples

Three categories of examples appear across the templates:

1. **Coding activity** — implementation tasks with specific technical requirements.
2. **Deep analysis and research** — architecture comparisons, technology
   assessments, strategic recommendations.
3. **Executive communication** — presentations, keynote narratives, stakeholder
   documents.

Use examples as copy-paste starting points. Adapt the requirements section to
your actual task.

---

## Prompting Best Practices

The following practices apply across all models in this library.

### Be Explicit About Quality Bars

Vague quality signals produce vague output. Use concrete frames:

- :white_check_mark: "Production-ready with proper error handling and tests."
- :white_check_mark: "Investment-grade analysis with sourced assumptions."
- :x: "Make it good."

### Use Structured Output Formats

Specify the exact format you need, especially for downstream consumption:

```
Output format:
- Section 1: Executive Summary (3-4 sentences)
- Section 2: Findings table (Severity | Finding | Affected Code | Fix)
- Section 3: Corrected code snippets (fenced, language-tagged)
```

### Provide Context Proportional to Task Complexity

- **Simple tasks:** one or two sentences of context is sufficient.
- **Complex tasks:** include architecture overviews, existing code, constraints,
  and the reason the task matters.
- **Agentic tasks:** provide full repository structure, success criteria with
  testable conditions, and explicit scope boundaries.

### Prefer References Over Descriptions

On the Claude 5 generation especially, a failing test, an HTML mockup, or a
rubric outperforms a paragraph describing what you want. Attach the artifact.

### Few-Shot Examples Dramatically Improve Consistency

For extraction, classification, or structured generation tasks, always include
at least one example of the desired input → output pair before the actual task.

### Separate Concerns with Structure

Use XML tags (Anthropic), system vs. user roles (OpenAI), or section headers
(Google) to clearly separate:

- Role and persona
- Background context
- Task instructions
- Constraints and rules
- Output format specification

### Enable Reasoning Explicitly When Needed

| Model | How to enable deeper reasoning |
|-------|-------------------------------|
| Claude Fable 5 | Adaptive thinking is always on and cannot be disabled or budgeted; depth via `output_config.effort` (`low` → `max`, `xhigh` for coding/agentic) |
| Claude Opus 5 / Sonnet 5 | Adaptive thinking on by default; depth via `output_config.effort` (default `high`). Disabling thinking is allowed on Sonnet 5, and on Opus 5 only at effort `high` or below |
| Claude Opus 4.8 / 4.7 / 4.6, Sonnet 4.6 | Adaptive thinking recommended (`budget_tokens` deprecated); `output_config.effort` supported |
| Claude Haiku 4.5 / Sonnet 4.5 | Extended thinking with `budget_tokens`; "think step by step" |
| GPT-5.5 / 5.4 family | `reasoning_effort: none / low / medium / high / xhigh` |
| Gemini 3.1 Pro | Thinking always on; `thinking_level` defaults to `high` (no `minimal`) |
| Gemini 3.5 Flash / 3.1 Flash-Lite | `thinking_level: minimal / low / medium / high` (defaults: medium / minimal) |

> On the Claude 5 generation, do **not** raise depth with prose ("think harder",
> "reason exhaustively"). Raise `effort` instead.

---

## Adding New Templates

When adding a template for a new model, follow this checklist:

1. Name the file `NN-provider-model-name.md` (zero-padded two-digit prefix), and
   include the model number in the filename so successive versions stay distinct.
2. Include a **Model Profile** table with at minimum: model name, provider,
   tier, context window, strengths, and best-fit scenarios.
3. Include the **Template Structure** scaffold with `{{PLACEHOLDER}}` variables.
4. Add at least **3 Key Prompting Principles** specific to the model.
5. Add at least **1 Worked Example** — coding activity preferred.
6. For a Claude 5-generation model, add a **Steering Block Library** and a
   **migration table** of what to delete from prior-model prompts.
7. Update the [Template Index](#template-index) table in this guide.
8. Update the [README.md](README.md) index and Model Selection Rules.

---

## Related Resources

- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- [Claude model migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library)
- [Google Gemini API — System Instructions](https://ai.google.dev/gemini-api/docs/system-instructions)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Workspace Copilot Instructions](../copilot-instructions.md)

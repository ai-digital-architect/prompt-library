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
  Covers all 27 templates across Anthropic Claude, Google Gemini, and OpenAI GPT
  model families, with selection guidance, template anatomy, and best practices
  for writing effective prompts. Refreshed July 2026 for the Claude 5 generation
  (Fable 5, Opus 5, Sonnet 5), the OpenAI GPT-5.6 family (Sol, Terra, Luna), and
  the newest Gemini models (3.6 Flash, 3.5 Flash-Lite).
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

## Overview

This folder contains 27 general-purpose prompt templates, one per major model
in the Anthropic Claude, Google Gemini, and OpenAI GPT model families — see
[current-model-list.md](current-model-list.md). Each template provides:

- A **model profile** with key attributes, context window, and best-fit scenarios.
- A **template structure** with fill-in-the-blank scaffolding.
- **Prompting principles** specific to that model's behavior.
- **Worked examples** covering coding, architecture analysis, and communication tasks.

The three Claude 5-generation templates (Fable 5, Opus 5, Sonnet 5) additionally
carry a **Steering Block Library** — copy-paste instruction blocks that each fix one
specific default behavior — and a **migration table** listing what to delete from
prompts written for earlier models.

Templates for the newest generations also open with a **spec-notes line** stating
where their numbers came from and the date they were verified, so a stale template
is easy to spot.

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
| 05 | [05-google-gemini-3-flash.md](05-google-gemini-3-flash.md) | Gemini 3 Flash | Google DeepMind | Fast frontier | Preview — see 26 |
| 06 | [06-openai-gpt-5-1.md](06-openai-gpt-5-1.md) | GPT-5.1 | OpenAI | Balanced frontier | Deprecated — see 23 |
| 07 | [07-openai-gpt-5-2.md](07-openai-gpt-5-2.md) | GPT-5.2 | OpenAI | Flagship (prior gen) | Deprecated — see 23 |
| 08 | [08-openai-gpt-5-3.md](08-openai-gpt-5-3.md) | GPT-5.3 | OpenAI | Frontier (prior gen) | Deprecated — see 23 |
| 09 | [09-openai-gpt-5-2-codex.md](09-openai-gpt-5-2-codex.md) | GPT-5.2 Codex | OpenAI | Agentic coding | Deprecated — see 23 |
| 10 | [10-openai-gpt-5-3-codex.md](10-openai-gpt-5-3-codex.md) | GPT-5.3 Codex | OpenAI | Agentic coding | Deprecated — see 23 |
| 11 | [11-openai-gpt-5-4.md](11-openai-gpt-5-4.md) | GPT-5.4 | OpenAI | Affordable frontier | Legacy — see 24 |
| 12 | [12-anthropic-claude-opus-4-6.md](12-anthropic-claude-opus-4-6.md) | Claude Opus 4.6 | Anthropic | Flagship (prior gen) | Legacy — see 21 |
| 13 | [13-anthropic-claude-fable-5.md](13-anthropic-claude-fable-5.md) | Claude Fable 5 | Anthropic | Frontier ceiling (above Opus) | **Current** |
| 14 | [14-anthropic-claude-opus-4-8.md](14-anthropic-claude-opus-4-8.md) | Claude Opus 4.8 | Anthropic | Flagship (prior gen) | Legacy — see 21 |
| 15 | [15-openai-gpt-5-5.md](15-openai-gpt-5-5.md) | GPT-5.5 | OpenAI | Flagship (prior gen) | Legacy — see 23 |
| 16 | [16-openai-gpt-5-4-mini.md](16-openai-gpt-5-4-mini.md) | GPT-5.4 mini | OpenAI | Balanced / low latency | Legacy — see 24 |
| 17 | [17-openai-gpt-5-4-nano.md](17-openai-gpt-5-4-nano.md) | GPT-5.4 nano | OpenAI | Fast / lowest cost | Legacy — see 25 |
| 18 | [18-google-gemini-3-1-pro.md](18-google-gemini-3-1-pro.md) | Gemini 3.1 Pro | Google DeepMind | Flagship | **Current** (Preview) |
| 19 | [19-google-gemini-3-5-flash.md](19-google-gemini-3-5-flash.md) | Gemini 3.5 Flash | Google DeepMind | Fast frontier (prior gen) | Legacy — see 26 |
| 20 | [20-google-gemini-3-1-flash-lite.md](20-google-gemini-3-1-flash-lite.md) | Gemini 3.1 Flash-Lite | Google DeepMind | Fast / lowest cost (prior gen) | Legacy — see 27 |
| 21 | [21-anthropic-claude-opus-5.md](21-anthropic-claude-opus-5.md) | Claude Opus 5 | Anthropic | Flagship | **Current** |
| 22 | [22-anthropic-claude-sonnet-5.md](22-anthropic-claude-sonnet-5.md) | Claude Sonnet 5 | Anthropic | Balanced frontier | **Current** |
| 23 | [23-openai-gpt-5-6-sol.md](23-openai-gpt-5-6-sol.md) | GPT-5.6 Sol | OpenAI | Flagship | **Current** |
| 24 | [24-openai-gpt-5-6-terra.md](24-openai-gpt-5-6-terra.md) | GPT-5.6 Terra | OpenAI | Balanced / mid-tier | **Current** |
| 25 | [25-openai-gpt-5-6-luna.md](25-openai-gpt-5-6-luna.md) | GPT-5.6 Luna | OpenAI | Fast / lowest cost | **Current** |
| 26 | [26-google-gemini-3-6-flash.md](26-google-gemini-3-6-flash.md) | Gemini 3.6 Flash | Google DeepMind | Fast frontier workhorse | **Current** (Stable) |
| 27 | [27-google-gemini-3-5-flash-lite.md](27-google-gemini-3-5-flash-lite.md) | Gemini 3.5 Flash-Lite | Google DeepMind | Fast / lowest cost | **Current** (Stable) |

> **Intentionally excluded:** Anthropic's Claude Mythos 5 / Mythos Preview
> (limited-availability research models — skipped by design), Gemini 3.5 Flash
> Cyber (limited-access pilot for governments and trusted partners), the
> Gemini 2.5 family (previous generation), and all media, realtime-voice, TTS,
> transcription, embedding, and robotics models — this library covers
> general-purpose text/reasoning prompting only.
>
> **Documented but not yet templated:** Gemini 3.5 Pro is testing with partners
> and has no public specification, so the Pro tier remains Gemini 3.1 Pro
> (template 18).

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

## Model Families by Provider

## Anthropic Claude

Four tiers cover the full range of latency and depth requirements. (Claude
Mythos 5 / Mythos Preview are limited-availability research models and have no
template by design.)

### Claude Fable 5 — Frontier Ceiling :sparkles:

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

### Claude Opus 5 — Flagship Daily Driver for Hard Tasks

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

### Claude Sonnet 5 — Best Speed-to-Intelligence Ratio

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

### Claude Haiku 4.5 — Speed and Cost Efficiency

- **Context window:** 200K tokens | **Max output:** 64K tokens
- **Pricing:** $1 / $5 per million input/output tokens
- **Use when:** high-volume pipelines, real-time assistants, batch processing,
  classification, extraction, subagent task execution.
- **Key technique:** Lean prompts with explicit output formats; one or two
  few-shot examples; design for pipeline reuse (one unit of work per call).

---

## Google Gemini

All current Gemini models share a **1M token context window** and native
multimodal processing — the primary differentiators from other families.
(Gemini 2.5 and media/TTS/Live models are out of scope for this library.)

### Gemini 3.1 Pro — Flagship Reasoning + Multimodal (Preview)

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $2 / $12 per million tokens (≤200K prompt); $4 / $18 above 200K
- **Use when:** the deepest reasoning in the Gemini lineup — multi-modal
  analysis, scientific reasoning, agentic coding, long-document processing.
- **Key technique:** Context first, instruction last; thinking is always on
  (defaults to `thinking_level: "high"`, cannot be disabled); keep sampling
  parameters at defaults; ground with Google Search for current facts.

### Gemini 3.6 Flash — Current Workhorse (Stable)

- **Context window:** 1,048,576 input tokens | **Max output:** 65,536 tokens
- **Pricing:** $1.50 / $7.50 per million input/output tokens (Batch API at 50%;
  context caching $0.15/M plus $1.00 per hour of storage)
- **Use when:** balanced production applications, interactive chat, fast code
  generation, computer use, and rapid multimodal tasks — Google positions it as
  the model "designed for the agentic era," with DeepSWE 49% (vs. 37% for 3.5
  Flash) and OSWorld-Verified 83.0% (vs. 78.4%).
- **Key technique:** Defaults to `thinking_level: "medium"` — raise to `high`
  for harder reasoning. Remove `temperature`, `top_p`, and `top_k` (deprecated
  and ignored, HTTP 400 in future versions), replace `thinking_budget` with
  `thinking_level` string values, and never end a request on a model-role turn.
- **Prior generation:** Gemini 3.5 Flash ($1.50 / $9.00) remains available —
  see template 19.

### Gemini 3.5 Flash — Prior Fast Frontier

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $1.50 / $9.00 per million input/output tokens
- **Use when:** existing deployments only. Gemini 3.6 Flash costs less per
  output token and Google reports it uses ~17% fewer output tokens for the same
  work, so there is no cost argument for staying.

### Gemini 3.5 Flash-Lite — Current Lowest Cost / Highest Throughput (Stable)

- **Context window:** 1,048,576 input tokens | **Max output:** 65,536 tokens
- **Pricing:** $0.30 / $2.50 per million input/output tokens (Batch and Flex at
  $0.15 / $1.25; Priority at $0.54 / $4.50; context caching $0.03/M plus $1.00
  per million tokens per hour of storage). Input is priced uniformly across
  text, image, video, and audio.
- **Use when:** high-volume data parsing, document extraction, structured JSON
  pipelines, and autonomous subagent execution — Google cites roughly 350 output
  tokens per second.
- **Key technique:** Defaults to `thinking_level: "minimal"`, which is correct
  for extraction and classification. Raise it to `"medium"` or `"high"` for
  autonomous subagents that make tool calls or need multi-step reasoning, or they
  terminate early. Same API changes as 3.6 Flash: no sampling parameters,
  `thinking_level` strings, no prefilled model turns.
- **Supersedes:** Gemini 3.1 Flash-Lite and Gemini 2.5 Flash. Note it does *not*
  support computer use or the Live API.

### Gemini 3.1 Flash-Lite — Prior Lowest-Cost Tier

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $0.25 / $1.50 per million input/output tokens
- **Use when:** existing deployments, or the rare case where the $0.05/M input
  difference outweighs 3.5 Flash-Lite's speed and capability gains.
- **Key technique:** Defaults to `thinking_level: "minimal"` for speed —
  escalate selectively; strict output schemas and few-shot examples.

### Gemini 3 Pro / 3 Flash — Prior Generation

Gemini 3 Pro is superseded by 3.1 Pro; Gemini 3 Flash ($0.50 / $3.00) remains
in Preview and is two generations behind the stable 3.6 Flash. Templates 04 and
05 remain valid for existing deployments.

### On the Pro tier

Gemini 3.1 Pro (Preview) is still the newest Pro-tier model on Google's model
page. Google has said Gemini 3.5 Pro is testing with partners with broader
availability "as soon as it's ready," and that Gemini 4 pre-training has begun —
neither has a published specification, so neither has a template here.

---

## OpenAI GPT

The current lineup is the three-tier GPT-5.6 family: Sol (flagship), Terra
(mid-tier), and Luna (fast/budget). All three share a 1,050,000-token context
window, a 128K output ceiling, a February 16, 2026 knowledge cutoff, and the same
built-in tool surface — the tiers differ in reasoning depth, price, and
throughput, not in headroom. GPT-5.4 and GPT-5.5 are no longer listed on OpenAI's
models page; GPT-5.1–5.3 and the Codex variants are deprecated. Templates 06–11
and 15–17 remain for existing deployments.

### GPT-5.6 Sol — Current Flagship

- **Context window:** 1,050,000 tokens | **Max output:** 128K tokens
- **Pricing:** $5.00 / $30.00 per million input/output tokens; $0.50/M cached
  input. Above 272K input tokens: 2× input, 1.5× output. Cache writes 1.25×.
- **Use when:** complex professional work, deep reasoning, production coding,
  cybersecurity, and multi-agent workflows.
- **Key technique:** Outcome-first prompts, and *leaner* ones — OpenAI's testing
  found trimmed prompts raised eval scores roughly 10–15% while cutting tokens
  41–66%. `reasoning.mode: "pro"` is documented for Sol and is a separate axis
  from `reasoning.effort`; use it where a wrong answer is expensive and latency
  is tolerable.

### GPT-5.6 Terra — Balanced Mid-Tier

- **Context window:** 1,050,000 tokens | **Max output:** 128K tokens
- **Pricing:** $2.50 / $15.00 per million input/output tokens; $0.25/M cached
  input — exactly half of Sol on every axis.
- **Use when:** general-purpose enterprise tasks and agentic workflows that need
  strong capability at controlled cost; the per-call worker under a Sol planner.
- **Key technique:** Route, don't downgrade — pin the output contract with
  Structured Outputs and define the escalation condition in your harness rather
  than asking the model to self-assess.

### GPT-5.6 Luna — Fast / Budget

- **Context window:** 1,050,000 tokens | **Max output:** 128K tokens
- **Pricing:** $1.00 / $6.00 per million input/output tokens; $0.10/M cached
  input. Highest rate-limit ceiling in the family (Tier 5: 30,000 RPM / 180M TPM).
- **Use when:** high-volume, low-latency, cost-sensitive workloads —
  classification, extraction, routing, summarization pipelines, subagent workers.
- **Key technique:** One unit of work per call, few-shot examples over prose
  rules, a static cached prefix, and an explicit abstain path that routes
  low-confidence items to a higher tier.

### GPT-5.4 / 5.5 — Prior Generation

Neither appears on OpenAI's models page as of July 2026, and no formal retirement
date has been announced for them. The published deprecations name `gpt-5.6-sol`,
`gpt-5.6-terra`, and `gpt-5.6-luna` as the replacements for the `gpt-5`,
`gpt-5-mini`, and `gpt-5-nano` snapshots, which shut down December 11, 2026.

### GPT-5.1 / 5.2 / 5.3 and Codex Variants — Deprecated

No longer listed in OpenAI's model docs; announced retirements July 23 –
August 10, 2026, with the GPT-5.6 family as the designated replacement
(including for coding/Codex workloads). See templates 06–10 for migration
banners.

---

## Choosing the Right Model

Use this decision tree as a starting point.

```
Is the task code-focused and multi-file / long-horizon?
├── Yes → Claude Opus 5 (agentic coding) or GPT-5.6 Sol (complex coding)
│         └── Multi-day autonomous runs / hardest novel problems → Claude Fable 5
│             └── ...but Zero Data Retention required → stay on Opus 5
└── No
    ├── Does it involve images, audio, video, or PDFs?
    │   ├── Need speed and cost → Gemini 3.6 Flash
    │   └── Need depth → Gemini 3.1 Pro
    ├── Is cost or latency the primary constraint?
    │   ├── Very high volume, simple tasks → GPT-5.6 Luna,
    │   │   Claude Haiku 4.5, or Gemini 3.5 Flash-Lite
    │   └── Moderate volume, balanced tasks → Claude Sonnet 5,
    │       GPT-5.6 Terra, or Gemini 3.6 Flash
    └── Is this professional / high-stakes work?
        ├── Deep nuance / judgment required → Claude Opus 5 (or Fable 5)
        └── Expert-level professional → GPT-5.6 Sol (consider reasoning.mode: pro)
```

### Quick Reference: Model vs. Use Case

| Use Case | Recommended Model |
|----------|------------------|
| Production coding agent (multi-tool) | Claude Sonnet 5 or Gemini 3.6 Flash |
| Multi-file feature work or a large refactor | Claude Opus 5 or GPT-5.6 Sol |
| Code review — production release | Claude Opus 5 |
| Hardest novel problems / multi-day autonomous runs | Claude Fable 5 |
| High-volume extraction / classification | GPT-5.6 Luna, Claude Haiku 4.5, or Gemini 3.5 Flash-Lite |
| Multi-modal document analysis | Gemini 3.1 Pro (depth) or Gemini 3.6 Flash (speed) |
| Real-time interactive assistant | Claude Sonnet 5, Gemini 3.6 Flash, or GPT-5.6 Luna |
| Frontend / UI generation | Claude Sonnet 5 or GPT-5.6 Sol |
| Computer use | Claude Sonnet 5 or Gemini 3.6 Flash (Preview) |
| Cybersecurity engineering | GPT-5.6 Sol |
| Financial modeling / legal analysis | GPT-5.6 Sol |
| Cross-functional technical strategy with clear deliverables | GPT-5.6 Terra |
| Production summarization pipelines | GPT-5.6 Luna or Gemini 3.6 Flash |
| Full-stack app from scratch / large codebase migration | Claude Opus 5 or GPT-5.6 Sol |
| Architecture strategy — board level | Claude Opus 5 or GPT-5.6 Sol |

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
| GPT-5.6 Sol / Terra / Luna | `reasoning.effort` (model-dependent subset of `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`) plus `reasoning.mode: standard / pro` — documented for Sol — as an independent axis |
| GPT-5.5 / 5.4 family | `reasoning_effort: none / low / medium / high / xhigh` |
| Gemini 3.1 Pro | Thinking always on; `thinking_level` defaults to `high` (no `minimal`) |
| Gemini 3.6 Flash / 3.5 Flash / 3.5 Flash-Lite / 3.1 Flash-Lite | `thinking_level: minimal / low / medium / high` (defaults: medium / medium / minimal / minimal); `thinking_budget` is superseded by `thinking_level` string values. Raise 3.5 Flash-Lite to `medium` or `high` for autonomous subagents |

> On the Claude 5 generation, do **not** raise depth with prose ("think harder",
> "reason exhaustively"). Raise `effort` instead. The same applies to GPT-5.6 and
> Gemini 3.6 Flash: reach for `reasoning.effort` / `reasoning.mode` and
> `thinking_level` rather than adding instruction text.
>
> Sampling parameters are gone across all three current generations: they return a
> 400 on the Claude 5 generation and on GPT-5.6, and are deprecated and silently
> ignored on Gemini 3.6 Flash. If you were using `temperature` for output variety,
> ask for variety in the prompt instead.

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
7. Add a **spec-notes line** directly under the Model Profile table stating every
   sourced number, the date verified, and the documentation pages it came from.
   If a specification is not published, say so rather than estimating it.
8. Update the [Template Index](#template-index) table in this guide.
9. Update the [README.md](README.md) index and Model Selection Rules.

---

## Related Resources

- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- [Claude model migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library)
- [OpenAI model guidance (GPT-5.6 family)](https://developers.openai.com/api/docs/guides/latest-model)
- [OpenAI reasoning guide (effort and mode)](https://developers.openai.com/api/docs/guides/reasoning)
- [OpenAI models and deprecations](https://developers.openai.com/api/docs/models)
- [Gemini 3.6 Flash model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash)
- [Using the latest Gemini models (migration)](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Google Gemini API — System Instructions](https://ai.google.dev/gemini-api/docs/system-instructions)
- [Workspace Copilot Instructions](../copilot-instructions.md)

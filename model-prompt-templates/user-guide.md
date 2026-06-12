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
  Covers all 20 templates across Anthropic Claude, Google Gemini, and OpenAI GPT-5
  model families, with selection guidance, template anatomy, and best practices
  for writing effective prompts. Refreshed June 2026 against the current model
  lineups of all three providers.
post_date: "2026-03-03"
last_updated: "2026-06-12"
---

## Overview

This folder contains 20 general-purpose prompt templates, one per major model
in the Anthropic Claude, Google Gemini, and OpenAI GPT-5 model families —
refreshed June 2026 against [current-model-list.md](current-model-list.md).
Each template provides:

- A **model profile** with key attributes, context window, and best-fit scenarios.
- A **template structure** with fill-in-the-blank scaffolding.
- **Prompting principles** specific to that model's behavior.
- **Worked examples** covering coding, architecture analysis, and communication tasks.

Use these templates as starting points. Adapt them to your domain, task, and
quality requirements.

---

## Template Index

| # | File | Model | Provider | Tier | Status (June 2026) |
|---|------|-------|----------|------|--------|
| 01 | [01-anthropic-claude-opus.md](01-anthropic-claude-opus.md) | Claude Opus 4.5 / 4.6 | Anthropic | Flagship (prior gen) | Legacy — see 14 |
| 02 | [02-anthropic-claude-sonnet.md](02-anthropic-claude-sonnet.md) | Claude Sonnet 4.6 (4.5 legacy) | Anthropic | Balanced frontier | **Current** |
| 03 | [03-anthropic-claude-haiku.md](03-anthropic-claude-haiku.md) | Claude Haiku 4.5 | Anthropic | Fast frontier | **Current** |
| 04 | [04-google-gemini-3-pro.md](04-google-gemini-3-pro.md) | Gemini 3 Pro | Google DeepMind | Flagship (prior gen) | Legacy — see 18 |
| 05 | [05-google-gemini-3-flash.md](05-google-gemini-3-flash.md) | Gemini 3 Flash | Google DeepMind | Fast frontier | Preview — see 19 |
| 06 | [06-openai-gpt-5-1.md](06-openai-gpt-5-1.md) | GPT-5.1 | OpenAI | Balanced frontier | Deprecated — see 15 |
| 07 | [07-openai-gpt-5-2.md](07-openai-gpt-5-2.md) | GPT-5.2 | OpenAI | Flagship (prior gen) | Deprecated — see 15 |
| 08 | [08-openai-gpt-5-3.md](08-openai-gpt-5-3.md) | GPT-5.3 | OpenAI | Frontier (prior gen) | Deprecated — see 15 |
| 09 | [09-openai-gpt-5-2-codex.md](09-openai-gpt-5-2-codex.md) | GPT-5.2 Codex | OpenAI | Agentic coding | Deprecated — see 15 |
| 10 | [10-openai-gpt-5-3-codex.md](10-openai-gpt-5-3-codex.md) | GPT-5.3 Codex | OpenAI | Agentic coding | Deprecated — see 15 |
| 11 | [11-openai-gpt-5-4.md](11-openai-gpt-5-4.md) | GPT-5.4 | OpenAI | Affordable frontier | **Current** |
| 12 | [12-anthropic-claude-opus-4-6.md](12-anthropic-claude-opus-4-6.md) | Claude Opus 4.6 | Anthropic | Flagship (prior gen) | Legacy — see 14 |
| 13 | [13-anthropic-claude-fable-5.md](13-anthropic-claude-fable-5.md) | Claude Fable 5 | Anthropic | Frontier (above Opus) | **Current** |
| 14 | [14-anthropic-claude-opus-4-8.md](14-anthropic-claude-opus-4-8.md) | Claude Opus 4.8 | Anthropic | Flagship | **Current** |
| 15 | [15-openai-gpt-5-5.md](15-openai-gpt-5-5.md) | GPT-5.5 | OpenAI | Flagship | **Current** |
| 16 | [16-openai-gpt-5-4-mini.md](16-openai-gpt-5-4-mini.md) | GPT-5.4 mini | OpenAI | Balanced / low latency | **Current** |
| 17 | [17-openai-gpt-5-4-nano.md](17-openai-gpt-5-4-nano.md) | GPT-5.4 nano | OpenAI | Fast / lowest cost | **Current** |
| 18 | [18-google-gemini-3-1-pro.md](18-google-gemini-3-1-pro.md) | Gemini 3.1 Pro | Google DeepMind | Flagship | **Current** (Preview) |
| 19 | [19-google-gemini-3-5-flash.md](19-google-gemini-3-5-flash.md) | Gemini 3.5 Flash | Google DeepMind | Fast frontier | **Current** (Stable) |
| 20 | [20-google-gemini-3-1-flash-lite.md](20-google-gemini-3-1-flash-lite.md) | Gemini 3.1 Flash-Lite | Google DeepMind | Fast / lowest cost | **Current** (Stable) |

> **Intentionally excluded:** Anthropic's Claude Mythos 5 / Mythos Preview
> (limited-availability research models — skipped by design), the Gemini 2.5
> family (previous generation), and all media, realtime-voice, TTS,
> transcription, embedding, and robotics models — this library covers
> general-purpose text/reasoning prompting only.

---

## Model Families

### Anthropic Claude

Four tiers cover the full range of latency and depth requirements. (Claude
Mythos 5 / Mythos Preview are limited-availability research models and have no
template by design.)

#### Claude Fable 5 — Frontier Ceiling :sparkles:

- **Context window:** 1M tokens | **Max output:** 128K tokens
- **Pricing:** $10 / $50 per million input/output tokens
- **Use when:** the hardest novel problems, multi-day autonomous agent runs,
  near-1M-token research synthesis, work where a subtle error is very costly.
- **Key technique:** One rich, fully specified prompt with the complete end
  state; adaptive thinking is the only mode — steer depth with
  `output_config.effort` (`high` default, `xhigh` for coding/agentic). No
  sampling parameters, no prefills.

#### Claude Opus 4.8 — Flagship Daily Driver for Hard Tasks

- **Context window:** 1M tokens (no long-context premium) | **Max output:** 128K tokens
- **Pricing:** $5 / $25 per million input/output tokens
- **Use when:** long-horizon agentic work, production code review, deep
  document/knowledge work, high-stakes writing.
- **Key technique:** Full task spec up front at high effort; explicit "call
  this when…" trigger conditions for tools, search, memory, and subagents;
  grant autonomy on minor decisions to reduce ask-rate.
- **Prior generations:** Opus 4.5/4.6 remain active — see templates 01 and 12.

#### Claude Sonnet 4.6 — Best Speed-to-Intelligence Ratio

- **Context window:** 1M tokens | **Max output:** 64K tokens
- **Pricing:** $3 / $15 per million input/output tokens
- **Use when:** production coding agents, multi-tool workflows, architecture
  planning, content creation, subagent orchestration.
- **Key technique:** Direct, action-oriented instructions; multishot examples;
  encourage parallel tool calls explicitly; set `effort` deliberately (4.6
  defaults to `high` — drop to `low`/`medium` on latency-sensitive paths).

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
├── Yes → Claude Opus 4.8 (long-horizon agentic) or GPT-5.5 (complex coding)
│         └── Hardest / multi-day autonomous runs → Claude Fable 5
└── No
    ├── Does it involve images, audio, video, or PDFs?
    │   ├── Need speed → Gemini 3.5 Flash
    │   └── Need depth → Gemini 3.1 Pro
    ├── Is cost or latency the primary constraint?
    │   ├── Very high volume, simple tasks → Claude Haiku 4.5,
    │   │   Gemini 3.1 Flash-Lite, or GPT-5.4 nano
    │   └── Moderate volume, balanced tasks → Claude Sonnet 4.6,
    │       Gemini 3.5 Flash, or GPT-5.4 mini
    └── Is this professional / high-stakes work?
        ├── Deep nuance / judgment required → Claude Opus 4.8 (or Fable 5)
        └── Expert-level professional → GPT-5.5 or GPT-5.4
```

### Quick Reference: Model vs. Use Case

| Use Case | Recommended Model |
|----------|------------------|
| Production coding agent (multi-tool) | Claude Sonnet 4.6 |
| Code review — production release | Claude Opus 4.8 |
| Hardest novel problems / multi-day autonomous runs | Claude Fable 5 |
| High-volume extraction / classification | Claude Haiku 4.5, Gemini 3.1 Flash-Lite, or GPT-5.4 nano |
| Multi-modal document analysis | Gemini 3.1 Pro |
| Real-time interactive assistant | Gemini 3.5 Flash or Claude Haiku 4.5 |
| Financial modeling / legal analysis | GPT-5.5 |
| Cross-functional technical strategy with clear deliverables | GPT-5.4 |
| Production summarization pipelines | GPT-5.4 mini or Gemini 3.5 Flash |
| Full-stack app from scratch / large codebase migration | GPT-5.5 or Claude Opus 4.8 |
| Architecture strategy — board level | Claude Opus 4.8 or GPT-5.5 |

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
- **Agentic tasks (Codex models):** provide full repository structure, success
  criteria with testable conditions, and explicit scope boundaries.

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
| Claude Fable 5 / Opus 4.8 | Adaptive thinking (`thinking: {"type": "adaptive"}`) is the only mode; depth via `output_config.effort` (`low` → `max`, `xhigh` for coding/agentic) |
| Claude Sonnet 4.6 / Opus 4.6 | Adaptive thinking recommended (`budget_tokens` deprecated); `output_config.effort` supported |
| Claude Haiku 4.5 / Sonnet 4.5 | Extended thinking with `budget_tokens`; "think step by step" |
| GPT-5.5 / 5.4 family | `reasoning_effort: none / low / medium / high / xhigh` |
| Gemini 3.1 Pro | Thinking always on; `thinking_level` defaults to `high` (no `minimal`) |
| Gemini 3.5 Flash / 3.1 Flash-Lite | `thinking_level: minimal / low / medium / high` (defaults: medium / minimal) |

---

## Adding New Templates

When adding a template for a new model, follow this checklist:

1. Name the file `NN-provider-model-name.md` (zero-padded two-digit prefix).
2. Include a **Model Profile** table with at minimum: model name, provider,
   tier, context window, strengths, and best-fit scenarios.
3. Include the **Template Structure** scaffold with `{{PLACEHOLDER}}` variables.
4. Add at least **3 Key Prompting Principles** specific to the model.
5. Add at least **1 Worked Example** — coding activity preferred.
6. Update the [Template Index](#template-index) table in this guide.
7. Update the [README.md](README.md) if the folder description needs updating.

---

## Related Resources

- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library)
- [Google Gemini API — System Instructions](https://ai.google.dev/gemini-api/docs/system-instructions)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Workspace Copilot Instructions](../copilot-instructions.md)

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
  Covers all 10 templates across Anthropic Claude, Google Gemini, and OpenAI GPT-5
  model families, with selection guidance, template anatomy, and best practices
  for writing effective prompts.
post_date: "2026-03-03"
---

## Overview

This folder contains 10 general-purpose prompt templates, one per major model
in the Anthropic Claude, Google Gemini 3, and OpenAI GPT-5 model families.
Each template provides:

- A **model profile** with key attributes, context window, and best-fit scenarios.
- A **template structure** with fill-in-the-blank scaffolding.
- **Prompting principles** specific to that model's behavior.
- **Worked examples** covering coding, architecture analysis, and communication tasks.

Use these templates as starting points. Adapt them to your domain, task, and
quality requirements.

---

## Template Index

| # | File | Model | Provider | Tier |
|---|------|-------|----------|------|
| 01 | [01-anthropic-claude-opus.md](01-anthropic-claude-opus.md) | Claude Opus 4.5 / 4.6 | Anthropic | Flagship |
| 02 | [02-anthropic-claude-sonnet.md](02-anthropic-claude-sonnet.md) | Claude Sonnet 4.5 | Anthropic | Balanced frontier |
| 03 | [03-anthropic-claude-haiku.md](03-anthropic-claude-haiku.md) | Claude Haiku 4.5 | Anthropic | Fast frontier |
| 04 | [04-google-gemini-3-pro.md](04-google-gemini-3-pro.md) | Gemini 3 Pro | Google DeepMind | Flagship |
| 05 | [05-google-gemini-3-flash.md](05-google-gemini-3-flash.md) | Gemini 3 Flash | Google DeepMind | Fast frontier |
| 06 | [06-openai-gpt-5-1.md](06-openai-gpt-5-1.md) | GPT-5.1 | OpenAI | Balanced frontier |
| 07 | [07-openai-gpt-5-2.md](07-openai-gpt-5-2.md) | GPT-5.2 | OpenAI | Flagship |
| 08 | [08-openai-gpt-5-3.md](08-openai-gpt-5-3.md) | GPT-5.3 | OpenAI | Next-gen frontier |
| 09 | [09-openai-gpt-5-2-codex.md](09-openai-gpt-5-2-codex.md) | GPT-5.2 Codex | OpenAI | Agentic coding |
| 10 | [10-openai-gpt-5-3-codex.md](10-openai-gpt-5-3-codex.md) | GPT-5.3 Codex | OpenAI | Agentic coding |

---

## Model Families

### Anthropic Claude

Three tiers cover the full range of latency and depth requirements.

#### Claude Opus 4.5 / 4.6 — Maximum Depth

- **Context window:** 200K tokens | **Max output:** 64K tokens (128K with beta)
- **Use when:** correctness and nuance outweigh speed — architecture reviews,
  executive strategy, advanced research, subtle bug detection.
- **Key technique:** Enable extended thinking; use XML-tagged system prompts;
  provide motivational context explaining why quality matters.
- **Unique feature:** `effort` parameter controls token usage vs. thoroughness.

#### Claude Sonnet 4.5 — Best Intelligence-to-Cost Ratio

- **Context window:** 200K tokens (1M in beta) | **Max output:** 64K tokens
- **Pricing:** $3 / $15 per million input/output tokens
- **Use when:** production coding agents, multi-tool workflows, architecture
  planning, content creation, subagent orchestration.
- **Key technique:** Direct, action-oriented instructions; multishot examples;
  encourage parallel tool calls explicitly.

#### Claude Haiku 4.5 — Speed and Cost Efficiency

- **Context window:** 200K tokens | **Max output:** 64K tokens
- **Pricing:** $1 / $5 per million input/output tokens
- **Use when:** high-volume pipelines, real-time assistants, batch processing,
  classification, extraction, subagent task execution.
- **Key technique:** Lean prompts with explicit output formats; one or two
  few-shot examples; design for pipeline reuse (one unit of work per call).

---

### Google Gemini 3

Both Gemini 3 models share a **1M token context window** and native multimodal
processing — the primary differentiators from other families.

#### Gemini 3 Pro — Advanced Reasoning + Multimodal

- **Context window:** 1M tokens
- **Use when:** multi-modal analysis (images, audio, video, PDFs), scientific
  reasoning, long-document processing, complex coding, agentic workflows.
- **Key technique:** Feed entire codebases or document collections; configure
  thinking level (minimal → high) via API; use system instructions for role
  and constraints; connect to Google Search for real-time grounding.

#### Gemini 3 Flash — Frontier Reasoning at Flash Speed

- **Context window:** 1M tokens
- **Pricing:** $0.50 / $3.00 per million input/output tokens
- **Use when:** interactive agents, real-time assistants, rapid prototyping,
  batch data extraction, production pipelines at scale.
- **Key technique:** Keep prompts focused for low latency; batch 100+
  simultaneous function calls; pair with Pro for hybrid workflows (Flash
  for the fast inner loop, Pro for the reasoning-heavy outer loop).

---

### OpenAI GPT-5

Five models span general-purpose chat through specialized autonomous coding.

#### GPT-5.1 — Adaptive Reasoning for General Use

- **Context window:** 200K tokens
- **Use when:** general-purpose chat, fast coding iteration, conversational
  agents, consumer-facing applications, mixed-difficulty pipelines.
- **Key technique:** Trust adaptive reasoning; use `reasoning_effort: none`
  for speed-sensitive paths; leverage 8 customizable personality presets.

#### GPT-5.2 — Professional Knowledge Work

- **Context window:** 400K tokens | **Max output:** 128K tokens
- **Use when:** complex professional tasks (financial modeling, legal analysis,
  research synthesis), long-document processing, high-stakes reasoning.
- **Key technique:** Set explicit professional quality bars ("investment-grade",
  "Big 4 audit standard"); use `reasoning_effort: xhigh` for maximum depth;
  feed entire contracts or codebases at once.

#### GPT-5.3 — Next-Generation Efficiency

- **Context window:** 400K tokens (expected)
- **Status:** General-purpose variant not yet officially released as of March 2026.
  Based on observed patterns from GPT-5.3-Codex.
- **Use when:** tasks that previously required GPT-5.2 Pro but where speed
  matters; long-horizon agentic tasks; multi-modal analysis.
- **Key technique:** Interactive steering mid-task; context compaction for
  large reference material; frame prompts as ongoing collaborations.

#### GPT-5.2 Codex — Long-Horizon Agentic Coding :robot:

- **Context window:** 400K tokens | **Max output:** 128K tokens
- **SWE-Bench Pro:** 56.4% | **Terminal-Bench 2.0:** 64.0%
- **Use when:** multi-file codebase changes, code migrations, large refactors,
  security audits, complex debugging across large repositories.
- **Key technique:** Define end state, not steps; specify what must NOT change;
  set clear success criteria with tests; context compaction sustains long sessions.

#### GPT-5.3 Codex — Full Software Lifecycle :rocket:

- **Context window:** 400K tokens
- **Use when:** full-lifecycle tasks (code + docs + tests + deploy + monitor),
  long-running autonomous sessions, building complete applications from scratch.
- **Key technique:** Describe outcomes not procedures; steer interactively
  mid-task; assign lifecycle deliverables (PRDs, runbooks, metrics reports)
  alongside code; set multi-day milestones.

---

## Choosing the Right Model

Use this decision tree as a starting point.

```
Is the task code-focused and multi-file / long-horizon?
├── Yes → GPT-5.3 Codex (full lifecycle) or GPT-5.2 Codex (security/migration)
└── No
    ├── Does it involve images, audio, video, or PDFs?
    │   ├── Need speed → Gemini 3 Flash
    │   └── Need depth → Gemini 3 Pro
    ├── Is cost or latency the primary constraint?
    │   ├── Very high volume, simple tasks → Claude Haiku 4.5 or Gemini 3 Flash
    │   └── Moderate volume, balanced tasks → Claude Sonnet 4.5 or GPT-5.1
    └── Is this professional / high-stakes work?
        ├── Deep nuance required → Claude Opus 4.5 / 4.6
        └── Expert-level professional → GPT-5.2 or GPT-5.3
```

### Quick Reference: Model vs. Use Case

| Use Case | Recommended Model |
|----------|------------------|
| Production coding agent (multi-tool) | Claude Sonnet 4.5 |
| Code review — production release | Claude Opus 4.5 / 4.6 |
| High-volume extraction / classification | Claude Haiku 4.5 |
| Multi-modal document analysis | Gemini 3 Pro |
| Real-time interactive assistant | Gemini 3 Flash or GPT-5.1 |
| Financial modeling / legal analysis | GPT-5.2 |
| Full-stack app from scratch | GPT-5.3 Codex |
| Large codebase migration | GPT-5.2 Codex |
| Consumer chat / personality-driven | GPT-5.1 |
| Architecture strategy — board level | Claude Opus or GPT-5.2 |

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
| Claude (all) | "Think step by step" / API extended thinking |
| Claude Opus | `effort` parameter; "reason carefully before answering" |
| GPT-5.x | `reasoning_effort: low / medium / high / xhigh` |
| Gemini 3 Pro/Flash | Thinking level: minimal / low / medium / high |

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

---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.6 Sol"
author1: "Prompt Library Team"
post_slug: "23-openai-gpt-5-6-sol"
microsoft_alias: "promptlibrary"
featured_image: "https://learn.microsoft.com/en-us/azure/ai-services/openai/media/overview/openai-overview.png"
categories:
  - "AI"
  - "Developer Tools"
tags:
  - "prompt-engineering"
  - "llm"
  - "model-templates"
  - "ai-assisted-engineering"
  - "openai"
  - "gpt-5-6"
  - "agentic"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for GPT-5.6 Sol, OpenAI's flagship: outcome-first scaffold,
  reasoning mode and effort as independent axes, programmatic tool calling,
  autonomy boundaries, and verified July 2026 specifications.
post_date: "2026-07-25"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.6 Sol (`gpt-5.6-sol`) |
| **Provider** | OpenAI |
| **Tier** | Current flagship — "frontier model for complex professional work" |
| **Aliases** | `gpt-5.6` and `gpt-5` both route to Sol |
| **Context Window** | 1,050,000 tokens (long-prompt pricing applies above 272K input tokens) |
| **Max Output** | 128K tokens |
| **Knowledge Cutoff** | February 16, 2026 |
| **Strengths** | Frontier reasoning at lower output-token cost, state-of-the-art coding, frontend design judgment, intent inference from thin context, large tool surfaces, `pro` reasoning mode for the hardest problems |
| **Best For** | Complex professional work, deep reasoning, production coding, cybersecurity, multi-agent and long-horizon agentic workflows |
| **Key Differentiator** | Reaches frontier performance with fewer output tokens than GPT-5.5, and is the only GPT-5.6 tier documented to support `reasoning.mode: "pro"` |

> **Spec notes (verified 25 July 2026):** context 1,050,000 tokens / 128K max
> output; knowledge cutoff February 16, 2026; pricing $5.00/M input, $30.00/M
> output, $0.50/M cached input, with 2× input and 1.5× output above 272K input
> tokens and cache writes at 1.25× uncached input; `reasoning.effort` accepts
> model-dependent values from `none`, `minimal`, `low`, `medium`, `high`,
> `xhigh`, `max`; `reasoning.mode` accepts `standard` (default) and `pro`;
> `text.verbosity` accepts `low`, `medium`, `high`; tools include web search,
> file search, code interpreter, computer use, image generation, hosted shell,
> apply patch, skills, MCP, and tool search; fine-tuning not supported.
> Source: OpenAI model page for `gpt-5.6-sol`, the API model-guidance page, and
> the reasoning guide.

---

## What Sets GPT-5.6 Sol Apart

1. **Frontier results on fewer output tokens** — OpenAI positions Sol as reaching
   frontier performance with fewer output tokens than GPT-5.5. The savings compound
   across multi-step agentic runs, so the flagship is frequently cheaper end-to-end
   than a cheaper tier that needs retries.
2. **`pro` reasoning mode is a separate axis from effort** — `reasoning.mode: "pro"`
   applies extra model work before returning a final answer. It raises latency and
   improves reliability on genuinely hard problems, and it is independent of
   `reasoning.effort` — you set both.
3. **Better intent inference and design judgment** — OpenAI cites improved inference
   of user goals from thin context, stronger frontend layout and visual hierarchy,
   and preservation of original image detail rather than resizing inputs to patches.

---

## Template Structure

GPT-5.6 Sol follows OpenAI's markdown-sectioned developer/system prompt convention.
State the outcome, success criteria, and output shape; let the model choose its
path. OpenAI's own testing found that *leaner* prompts raised eval scores roughly
10–15% while cutting total tokens 41–66% and cost 33–67% — so start from the
smallest prompt that preserves your product contract and tune parameters, not prose.

```text
System:
# Identity
You are {{ROLE}}, an expert in {{DOMAIN}}.

# Instructions
- {{CONSTRAINTS — rules the response must not violate}}
- {{Autonomy boundary: which actions proceed without asking, and which
  (external writes, scope expansion) require confirmation}}
- {{How to handle ambiguity: ask, proceed with stated assumptions, or abstain}}

# Success criteria
1. {{What the output must achieve}}
2. {{What must be preserved or avoided}}
3. {{How completeness will be judged}}

# Output format
{{OUTPUT_FORMAT — exact sections, schema, length limits. For strict JSON,
prefer Structured Outputs over prose schema descriptions.}}

---

User:
{{TASK}}

Context:
{{Static reference material first (for prompt caching), dynamic content last}}
```

### Key Prompting Principles for GPT-5.6 Sol

1. **Migrate by shrinking, not porting** — Carry your GPT-5.5 prompt over, then
   delete. Repeated instructions and elaborate tool descriptions cost tokens and
   measurably lower scores on this generation. Remove duplication first, then
   re-tune.
2. **Set effort one rung lower than your GPT-5.5 baseline, then test** — OpenAI's
   migration guidance is to preserve your current effort as the baseline and try one
   level below it. `medium` is the balanced default, `low` for latency-sensitive
   work, `max` reserved for the hardest quality-first tasks.
3. **Use `reasoning.mode: "pro"` for reliability, not for depth** — Pro mode is the
   right lever when a wrong answer is expensive and latency is tolerable. It stacks
   with, rather than replaces, `reasoning.effort`.
4. **Control length with `text.verbosity`** — Set the default detail level as a
   parameter (`low` / `medium` / `high`) and override per-task in the prompt where a
   specific section needs more or less. Verbosity is independent of reasoning depth.
5. **Define autonomy boundaries explicitly** — State which actions Sol may take
   without asking (safe local operations) and which require confirmation (external
   writes, anything that widens scope). Vague autonomy produces either stalling or
   over-reach.
6. **Reach for Programmatic Tool Calling on bounded data work** — Sol can write
   JavaScript that orchestrates tool calls, which suits filtering, joining, ranking,
   and aggregation. It is a poor fit where each step needs fresh model judgment. Opt
   individual tools in with `allowed_callers` and benchmark against direct calling.
7. **Move schemas to Structured Outputs** — Define output schemas through the API
   feature rather than describing JSON shape in prose. Frees prompt budget and
   removes a common source of format drift.
8. **Optimize for prompt caching** — Static content first, dynamic last. Cache
   writes now bill at 1.25× uncached input, so track `cached_tokens` and
   `cache_write_tokens` when you cost a workload.
9. **Use the Responses API for anything with reasoning or multiple turns** — Pass
   reasoning items forward via `previous_response_id` (or replay the full history)
   so the model continues its reasoning in the most token-efficient way.

---

## Example 1 — Agentic Coding with Verification

```text
System:
# Identity
You are a staff software engineer working in a production monorepo. You plan
before you code, reuse existing utilities before writing new ones, and verify
your work with tests before declaring completion.

# Instructions
- Reuse existing helpers in packages/shared before introducing new dependencies.
- Do not modify the public API of packages/auth — downstream services depend on it.
- Autonomy: run tests, edit files, and install already-approved dependencies
  without asking. Ask before adding a new external dependency, touching CI
  configuration, or widening scope beyond the payments package.
- If a requirement is ambiguous, state your assumption and proceed; do not stall.

# Success criteria
1. All existing tests pass; new behavior is covered by new tests.
2. No breaking changes to packages/auth public exports.
3. The change is reviewable: small diffs, clear commit-sized units, ADR note
   for any non-obvious design decision.

# Output format
Sections: Plan (brief), Implementation (fenced code blocks with filenames),
Tests, Verification Results, Assumptions & Follow-ups.

---

User:
Add idempotency-key support to our payments service so that retried POST
/charges requests never double-charge.

Context:
- Stack: Node.js 22, TypeScript, Fastify, PostgreSQL (Drizzle ORM), Redis.
- Monorepo: packages/payments (target), packages/shared (utilities),
  packages/auth (do not modify).
- Clients send an Idempotency-Key header; keys expire after 24 hours.
- Concurrent retries with the same key must yield exactly one charge and
  identical responses.
- Existing test suite: vitest, run with `pnpm test --filter payments`.
```

---

## Example 2 — Deep Analysis and Research (Technology Strategy)

```text
System:
# Identity
You are a principal technology analyst producing decision-grade research for a
CTO and CFO audience.

# Instructions
- Distinguish confirmed facts from inference; label estimates with assumptions.
- Quantify wherever possible; no vague qualitative claims.
- If the supplied context is insufficient for a claim, state the gap rather
  than filling it.

# Success criteria
1. The analysis is decision-ready: one recommendation, defended.
2. Every cost figure shows its methodology.
3. Second-order operational consequences are covered, not just architecture.

# Output format
Sections: Executive Summary (≤ 400 words), Option Analysis, 3-Year Cost Model,
Risk Table (likelihood × impact), Recommendation, Phased Roadmap.

---

User:
Evaluate whether we should migrate our AI inference workloads from per-token
API consumption to dedicated capacity (provisioned throughput or self-hosted
open-weight models).

Context:
- Mid-market SaaS, $9M annual inference spend, growing 70% YoY.
- Workload: 60M tokens/day text generation, 250M tokens/day embeddings,
  latency SLO p95 < 800ms for interactive features.
- Constraints: SOC 2 and EU data residency for 40% of traffic; platform team
  of 6 engineers; no existing GPU operations experience.
- Compare three options: (a) stay on per-token frontier APIs with cost-based
  routing, (b) provisioned/dedicated capacity from one provider, (c) hybrid —
  self-hosted open-weight models for embeddings + API for generation.
```

> Run this one at `reasoning: {"mode": "pro", "effort": "high"}` and
> `text: {"verbosity": "medium"}` — the decision is expensive to get wrong and
> latency is not a constraint.

---

## Example 3 — Bounded Data Work via Programmatic Tool Calling

```text
System:
# Identity
You are a revenue operations analyst with read access to our billing and CRM
tools.

# Instructions
- Use programmatic tool calling to filter, join, and aggregate across tool
  results; do not narrate intermediate row-by-row work.
- Every number in the output must trace to a tool result. If a join drops
  records, report the drop count rather than silently reconciling.
- Do not write to any system. Read-only.

# Success criteria
1. The cohort table reconciles to total ARR within $1,000.
2. Every excluded account is explained by a stated rule.
3. Output is a single table plus a short list of caveats.

# Output format
A Markdown table (segment, accounts, ARR, net retention, churn count) followed
by ## Caveats with at most five bullets.

---

User:
Build a net-revenue-retention breakdown by customer segment for FY2026 H1.

Context:
- Tools available: billing_query (invoice lines), crm_query (account records),
  fx_rates (monthly close rates).
- Segment definitions live in the CRM `segment` field; accounts with a null
  segment go to "Unclassified" rather than being dropped.
- Convert all non-USD invoices at the month-of-invoice close rate.
```

---

## When to Use GPT-5.6 Sol vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| Complex coding requiring planning, tool use, and verification | ✅ GPT-5.6 Sol |
| High-stakes professional analysis where errors are expensive | ✅ GPT-5.6 Sol (consider `reasoning.mode: "pro"`) |
| Agentic workflows with large tool surfaces or many subagents | ✅ GPT-5.6 Sol |
| Long-context work approaching the 1M-token window | ✅ GPT-5.6 Sol (mind long-prompt pricing above 272K input tokens) |
| Cybersecurity and security-critical engineering work | ✅ GPT-5.6 Sol |
| General enterprise and agentic work at lower cost | ❌ [GPT-5.6 Terra](./24-openai-gpt-5-6-terra.md) — half the price |
| High-volume, latency-sensitive, cost-critical workloads | ❌ [GPT-5.6 Luna](./25-openai-gpt-5-6-luna.md) |
| Native multimodal input (audio, video, PDF) | ❌ [Gemini 3.6 Flash](./26-google-gemini-3-6-flash.md) or Gemini 3.1 Pro |

---

## API Quick Reference

```json
{
  "model": "gpt-5.6-sol",
  "input": [
    { "role": "developer", "content": "# Identity\nYou are {{ROLE}}...\n\n# Instructions\n...\n\n# Output format\n..." },
    { "role": "user", "content": "{{TASK}}" }
  ],
  "reasoning": { "mode": "standard", "effort": "medium" },
  "text": { "verbosity": "low" },
  "max_output_tokens": 16000
}
```

> **Cost note (July 2026):** $5.00/M input, $30.00/M output, $0.50/M cached
> input. Prompts above 272K input tokens bill at 2× input and 1.5× output for
> the session, and cache writes bill at 1.25× uncached input. Start from your
> GPT-5.5 effort baseline and test one level lower before escalating. Use the
> Responses API for reasoning, tool-calling, and multi-turn work.
>
> **Rate limits:** Tier 1 starts at 500 RPM / 500K TPM and Tier 5 reaches
> 15K RPM / 40M TPM.
>
> **Migration:** `gpt-5-2025-08-07` is scheduled for shutdown on December 11,
> 2026, with `gpt-5.6-sol` named as its replacement.

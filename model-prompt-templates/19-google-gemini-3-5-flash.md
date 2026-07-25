---
post_title: "General-Purpose Prompt Template — Google Gemini 3.5 Flash"
author1: "Prompt Library Team"
post_slug: "19-google-gemini-3-5-flash"
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
  - "google"
  - "gemini"
  - "legacy"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Gemini 3.5 Flash: agentic coding loops and multimodal
  work at Flash latency. Superseded by Gemini 3.6 Flash.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status (July 2026):** Gemini 3.5 Flash is still listed as Stable but is no
> longer the newest Flash-tier model. **Gemini 3.6 Flash**
> ([template 26](./26-google-gemini-3-6-flash.md)) supersedes it, costs less per
> output token ($7.50/M vs. $9.00/M), and Google reports it uses roughly 17%
> fewer output tokens for the same work — there is no cost argument for staying.
> Note that 3.6 Flash also drops sampling parameters and prefilled model turns.

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3.5 Flash (`gemini-3.5-flash`) |
| **Provider** | Google DeepMind |
| **Tier** | Fast frontier (prior generation) — superseded by Gemini 3.6 Flash |
| **Status** | Stable (as of June 2026) |
| **Context Window** | 1M input tokens / 64K output tokens |
| **Knowledge Cutoff** | January 2025 |
| **Strengths** | Agentic coding, multi-step tool workflows, advanced reasoning at Flash latency, multimodal input (text, images, audio, video, PDFs), long-context understanding, token efficiency |
| **Best For** | Production agents, agentic coding loops, everyday reasoning tasks at scale, interactive assistants, multimodal extraction with reasoning |
| **Pricing** | $1.50 / $9.00 per 1M input/output tokens |

---

## What Sets Gemini 3.5 Flash Apart

1. **Frontier agentic performance at Flash latency** — Google reports Terminal-bench 2.1 76.2% (vs. 58.0% for Gemini 3 Flash), SWE-Bench Pro 55.1%, and MCP Atlas 83.6% (vs. 62.0%) — large generational jumps on agentic coding and multi-step tool workflows.
2. **Dramatically better token efficiency** — Google cites a 68% improvement in token efficiency over the prior generation, so equivalent tasks consume fewer output tokens and cost less despite the higher per-token price than 3 Flash.
3. **Stable, not preview** — Unlike Gemini 3.1 Pro (Preview) and Gemini 3 Flash (Preview), 3.5 Flash is a GA/stable model, making it the default choice for production workloads in the current Gemini lineup.

---

## Template Structure

Gemini 3.5 Flash follows the Gemini 3.x prompting conventions: direct goal statements, clear Markdown delimiters (not XML tags), large context before the instruction, and default sampling parameters. It defaults to `thinking_level: "medium"` — tune the level per task rather than padding the prompt with "think harder" language.

```
system_instruction:
You are {{ROLE}} specializing in {{DOMAIN}}.

Rules:
- {{CONSTRAINTS}}
- The current year is 2026. Your knowledge cutoff is January 2025 — use provided
  context or grounding for anything newer.
- Default to concise output; expand only when the task requires it.

---

User content:

## Context
{{Inputs: text, code, images, audio, video, PDFs — all large context first}}

## Task
{{TASK}}

## Requirements
1. {{Requirement 1}}
2. {{Requirement 2}}

## Output Format
{{OUTPUT_FORMAT — exact specification: JSON schema, Markdown sections, code-only}}
```

### Key Prompting Principles for Gemini 3.5 Flash

1. **Tune `thinking_level` per task** — Default is `medium` ("balanced thinking for most tasks"). Drop to `low` or `minimal` for chat, simple instruction-following, and high-throughput pipelines; raise to `high` for hard reasoning. This is the primary cost/latency/quality dial.
2. **Design for agentic loops** — 3.5 Flash is explicitly positioned for sustained agentic work (long-horizon tasks, multi-step tool use). Give it function declarations and let it orchestrate; it benchmarks strongly on multi-step MCP-style workflows.
3. **Context first, instruction last** — Per Google's long-context guidance, place documents/code/media at the top and the specific question at the very end.
4. **Keep sampling parameters at defaults** — Google strongly recommends default temperature/topP/topK for Gemini 3.x; the model is tuned around them.
5. **Exploit native multimodality** — Images, audio, video, and PDFs are equal-class inputs at Flash speed — ideal for real-time visual Q&A, meeting-audio analysis, and document extraction with reasoning.
6. **Ground time-sensitive answers with Google Search** — Supported as a built-in tool; use it for current events and post-cutoff facts instead of trusting memory.
7. **Request structured output with explicit schemas** — Native structured output / JSON mode makes 3.5 Flash a reliable pipeline component; specify the schema rather than describing it loosely.

---

## Example 1 — Coding Activity (Agentic Bug Hunt)

```
system_instruction:
You are a pragmatic senior engineer. Write clean, working code; minimize prose.
When using tools, state your plan in one line, then execute. Stop and report if a
fix would change public API behavior.

---

User content:

## Context
[Repository attached. Failing CI run log:]
- test_checkout_concurrent_inventory FAILED (flaky, ~30% of runs)
- test_refund_idempotency FAILED (deterministic)
[Function tools available: read_file, run_tests, apply_patch]

## Task
Diagnose and fix both failing tests.

## Requirements
1. For the flaky test: identify the race condition, don't just add retries or
   sleeps. Explain the interleaving that causes the failure in 3 lines.
2. For the deterministic failure: find the root cause in the refund handler.
3. Apply minimal patches; do not refactor unrelated code.
4. Re-run the test suite after each patch and report results.

## Output Format
Per bug: ## Root Cause (≤ 3 lines), ## Patch (diff), ## Verification (test output
summary). End with a one-line risk note for the release manager.
```

---

## Example 2 — Deep Analysis and Research (Multimodal Long-Context)

```
system_instruction:
You are a technical due-diligence analyst. You produce structured, decision-ready
comparisons. State confidence levels and call out gaps explicitly. Prioritize
actionable findings over exhaustive coverage.

---

User content:

## Context
[Attached: 6 vendor security whitepapers (PDF), 2 hours of recorded vendor demo
videos, and our 400-page internal security requirements document.]

## Task
Evaluate the three SIEM vendors against our internal requirements and produce a
shortlist recommendation.

## Requirements
1. Build a requirements-coverage matrix: each mandatory requirement × each vendor,
   marked Met / Partial / Not Met / Unverified, citing the whitepaper page or demo
   video timestamp as evidence.
2. Flag every claim made in a demo video that is NOT backed by the vendor's
   written documentation.
3. Identify the top 3 differentiators and top 3 risks per vendor.
4. Recommend a shortlist of 2 with rationale and a confidence level.

## Output Format
## Recommendation (with confidence: High/Medium/Low)
## Coverage Matrix (table)
## Demo-vs-Documentation Discrepancies
## Per-Vendor Risk Notes
```

---

## Example 3 — Executive Communication

```
system_instruction:
You write crisp executive communications. One message per section, data over
adjectives, no unsupported claims. Audience: C-suite, 3 minutes of reading time.

---

User content:

## Context
- Quarterly engineering review for the CTO of a fintech scale-up (1,200 staff).
- Key data: deploy frequency up 2.1x after platform migration; incident count flat;
  two Sev-1 outages traced to a legacy payments module; AI coding assistants now
  used by 78% of engineers, cycle time down 19%; attrition in platform team at 14%.

## Task
Draft the CTO's 1-page quarterly engineering update to the executive committee.

## Requirements
1. Lead with the single most important takeaway of the quarter.
2. Cover: delivery velocity, reliability (including the Sev-1s honestly), AI
   adoption impact, and the platform-team attrition risk.
3. End with two asks: budget for legacy payments remediation, and a retention
   package for platform engineers.

## Output Format
One page, Markdown: ## Headline, ## What Went Well, ## What Needs Attention,
## Asks. Bullet-first style, every bullet carries a number.
```

---

## When to Use Gemini 3.5 Flash vs. Other Models

| Scenario | Use Gemini 3.5 Flash? |
|---|---|
| Production agentic workflows and coding agents | ✅ Top agentic benchmarks in the Flash tier (Terminal-bench 2.1: 76.2%) |
| Stable GA model required for production | ✅ Stable, unlike 3.1 Pro / 3 Flash (Preview) |
| Interactive assistants needing speed + reasoning | ✅ Advanced reasoning at Flash latency |
| Multimodal extraction with reasoning (PDF, video, audio) | ✅ Native multimodal, 1M context |
| Absolute hardest reasoning problems | ⚠️ Consider Gemini 3.1 Pro (Preview) |
| Massive-volume classification/labeling at lowest cost | ❌ Use Gemini 3.1 Flash-Lite ($0.25/$1.50) |
| Cheapest possible Flash-tier inference | ❌ Gemini 3 Flash (Preview) is cheaper ($0.50/$3.00) but a generation behind |
| Long-document synthesis up to 1M tokens | ✅ Strong long-context understanding |

---

## API Quick Reference

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a pragmatic senior engineer...",
        thinking_config=types.ThinkingConfig(
            thinking_level="medium"  # default; "low"/"minimal" for throughput, "high" for hard reasoning
        ),
        response_mime_type="application/json",  # optional structured output
    ),
    contents="## Context\n...\n\n## Task\n...",
)
print(response.text)
```

> **Cost note:** $1.50 / $9.00 per 1M input/output tokens — pricier per token than
> Gemini 3 Flash, but Google cites 68% better token efficiency, which narrows the
> real cost gap on reasoning-heavy tasks. For pure high-volume extraction, step
> down to Gemini 3.1 Flash-Lite.

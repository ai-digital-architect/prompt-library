---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.6 Terra"
author1: "Prompt Library Team"
post_slug: "24-openai-gpt-5-6-terra"
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
  Prompt template for GPT-5.6 Terra, the balanced mid-tier at half the
  flagship price: routing rather than downgrading, hard output contracts,
  harness-level escalation, and verified July 2026 specifications.
post_date: "2026-07-25"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.6 Terra (`gpt-5.6-terra`) |
| **Provider** | OpenAI |
| **Tier** | Mid-tier — "balances capability and expense"; strong performance at lower cost |
| **Context Window** | 1,050,000 tokens (long-prompt pricing applies above 272K input tokens) |
| **Max Output** | 128K tokens |
| **Knowledge Cutoff** | February 16, 2026 |
| **Strengths** | Full flagship context and tool surface at half the flagship price, agentic tool workflows, general-purpose enterprise reasoning, structured outputs |
| **Best For** | General-purpose enterprise tasks and agentic workflows that need strong capability at lower operational cost |
| **Key Differentiator** | Same 1,050,000-token window, same 128K output ceiling, and the same built-in tool surface as GPT-5.6 Sol, at exactly half Sol's per-token price |

> **Spec notes (verified 25 July 2026):** context 1,050,000 tokens / 128K max
> output; knowledge cutoff February 16, 2026; pricing $2.50/M input, $15.00/M
> output, $0.25/M cached input, with 2× input and 1.5× output above 272K input
> tokens and cache writes at 1.25× uncached input; reasoning-token support
> enabled, documented capability level "Higher"; `text.verbosity` accepts `low`,
> `medium`, `high`; tools include web search, file search, image generation,
> code interpreter, hosted shell, apply patch, skills, computer use, MCP, and
> tool search; streaming, function calling, and structured outputs supported;
> fine-tuning not supported. `reasoning.mode: "pro"` is documented for
> `gpt-5.6-sol` and is **not** confirmed for Terra. Source: OpenAI model page
> for `gpt-5.6-terra`, the API model-guidance page, and the reasoning guide.

---

## What Sets GPT-5.6 Terra Apart

1. **No capability cliff on context or tools** — Terra is not a cut-down context
   window. It carries the same 1,050,000-token input limit, the same 128K output
   ceiling, and the same built-in tool surface as Sol. What you trade is depth per
   token, not headroom.
2. **Exactly half of Sol's price** — $2.50/$15.00 against Sol's $5.00/$30.00, with
   cached input at $0.25/M. On workloads that are tool-bound rather than
   reasoning-bound, that is close to a straight 50% saving.
3. **The natural default tier for agentic fleets** — When a workflow spawns many
   similar calls, Terra is usually the right per-call model with Sol reserved for the
   planning or adjudication step that actually needs frontier depth.

---

## Template Structure

Terra uses the same markdown-sectioned developer/system convention as the rest of
the GPT-5.6 family. Because it is the tier most often deployed at volume, be
stricter about output shape than you would be with Sol: pin the format, bound the
length, and let Structured Outputs carry the schema.

```text
System:
# Identity
You are {{ROLE}}, an expert in {{DOMAIN}}.

# Instructions
- {{CONSTRAINTS — rules the response must not violate}}
- {{Autonomy boundary: what proceeds without asking, what needs confirmation}}
- {{Escalation rule: when to stop and hand off rather than guess}}

# Success criteria
1. {{What the output must achieve}}
2. {{What must be preserved or avoided}}
3. {{How completeness will be judged}}

# Output format
{{OUTPUT_FORMAT — exact sections, schema, length limits. Prefer Structured
Outputs for anything a downstream system parses.}}

---

User:
{{TASK}}

Context:
{{Static reference material first (for prompt caching), dynamic content last}}
```

### Key Prompting Principles for GPT-5.6 Terra

1. **Route, don't downgrade** — The productive pattern is a Sol planner with Terra
   workers, not "Terra everywhere with a longer prompt." Adding prose to compensate
   for a cheaper tier costs tokens and, on this generation, tends to lower scores.
2. **Set effort one rung below your GPT-5.5 baseline, then test** — Same migration
   guidance as the rest of the family: preserve the current effort as a baseline,
   try one level lower, and only escalate when evals show a measurable gain.
3. **Pin the output contract hard** — At volume, format drift is the expensive
   failure. Use Structured Outputs for machine-consumed results and explicit section
   plus length limits for human-read ones.
4. **Control length with `text.verbosity`** — Set it as a parameter rather than
   asking for brevity in prose, and override per-task only where a section genuinely
   needs more detail.
5. **Escalate deliberately, in the harness** — Define the condition under which a
   Terra call is retried on Sol (low confidence, failed validation, contested
   decision) rather than asking Terra to self-assess whether it is good enough.
6. **Exploit caching aggressively** — Cached input at $0.25/M is the single biggest
   lever on a high-volume Terra workload. Order content static-first, dynamic-last,
   and track `cached_tokens` and `cache_write_tokens` (cache writes bill at 1.25×).
7. **Use the Responses API for reasoning and multi-turn work** — Pass reasoning
   items forward with `previous_response_id` so multi-step tool loops stay
   token-efficient.

---

## Example 1 — Coding Activity (Scoped Implementation Worker)

```text
System:
# Identity
You are a senior backend engineer implementing a well-specified ticket. The
design decisions have already been made; your job is a correct, reviewable
implementation.

# Instructions
- Implement exactly the ticket scope. Do not refactor adjacent code.
- Follow the conventions already present in the target package.
- Autonomy: edit files and run the package test suite freely. Stop and report
  if the ticket cannot be implemented without changing a public interface.

# Success criteria
1. The acceptance criteria in the ticket are each satisfied and each covered
   by a test.
2. The package test suite passes.
3. The diff touches only files listed in the ticket's scope section.

# Output format
Sections: Implementation (fenced blocks with filenames), Tests,
Verification Results, Out-of-Scope Observations (max 3 bullets).

---

User:
Implement TICKET-4821: add cursor-based pagination to the /v1/events list
endpoint.

Context:
- Stack: Python 3.13, FastAPI, SQLAlchemy 2.x, PostgreSQL.
- Scope: services/events/api.py, services/events/repo.py, and their tests.
- Acceptance criteria: opaque cursor, stable ordering under concurrent
  inserts, `limit` capped at 200, existing offset params continue to work for
  two releases.
- Test suite: `pytest services/events -q`.
```

---

## Example 2 — Deep Analysis and Research (Vendor Assessment at Volume)

```text
System:
# Identity
You are a procurement analyst producing standardized vendor assessments that
feed a comparison dashboard.

# Instructions
- Assess only against the supplied rubric. Do not introduce new criteria.
- Every score must cite the source section it came from.
- Where the documentation does not address a criterion, score it "Unverified"
  rather than inferring.

# Success criteria
1. Every rubric criterion receives a score and a citation or an explicit
   "Unverified".
2. The summary is decision-useful in under 200 words.
3. Output validates against the supplied schema.

# Output format
Structured Outputs schema `vendor_assessment_v3`. No prose outside the schema.

---

User:
Assess the attached vendor security documentation against our rubric.

Context:
- Rubric: 24 criteria across access control, data residency, incident
  response, subprocessors, and audit posture.
- This is one of 60 vendor assessments in this batch; consistency across the
  batch matters more than depth on any single one.
```

---

## Example 3 — Executive Communication (Recurring Report)

```text
System:
# Identity
You write the weekly operations digest for a distribution leadership team.

# Instructions
- Lead with what changed since last week, not with a status recap.
- Every claim carries a number and a direction of travel.
- If a metric is missing from the context, say so — do not carry last week's
  value forward.

# Success criteria
1. A reader who skipped last week still understands the current position.
2. Exceptions and risks are surfaced, not buried under green status.
3. The whole digest fits on one screen.

# Output format
## Headline (one sentence)
## What Changed (max 5 bullets, each with a number)
## Watch List (max 3 bullets, each with an owner)
Verbosity: low.

---

User:
Draft this week's operations digest.

Context:
- On-time delivery 94.2% (prior week 96.1%); two depots below 90%.
- Inbound backlog 3,400 units (prior 2,150); cause attributed to a carrier
  strike entering week two.
- Headcount: 12 open roles, 4 offers out.
- Cost per shipment $8.14 (prior $8.09).
```

---

## When to Use GPT-5.6 Terra vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| General enterprise reasoning and knowledge work | ✅ GPT-5.6 Terra |
| Agentic workflows that need capability at controlled cost | ✅ GPT-5.6 Terra |
| Per-call worker model under a Sol planner | ✅ GPT-5.6 Terra |
| Long-context analysis on a budget | ✅ GPT-5.6 Terra — full 1M-class window at half Sol's price |
| Hardest reasoning, security-critical work, or `pro` mode | ❌ [GPT-5.6 Sol](./23-openai-gpt-5-6-sol.md) |
| Very high volume or strict latency budgets | ❌ [GPT-5.6 Luna](./25-openai-gpt-5-6-luna.md) |
| Native audio, video, or PDF input | ❌ [Gemini 3.6 Flash](./26-google-gemini-3-6-flash.md) |
| Deepest multimodal reasoning | ❌ [Gemini 3.1 Pro](./18-google-gemini-3-1-pro.md) |

---

## API Quick Reference

```json
{
  "model": "gpt-5.6-terra",
  "input": [
    { "role": "developer", "content": "# Identity\nYou are {{ROLE}}...\n\n# Instructions\n...\n\n# Output format\n..." },
    { "role": "user", "content": "{{TASK}}" }
  ],
  "reasoning": { "effort": "medium" },
  "text": { "verbosity": "low" },
  "max_output_tokens": 8000
}
```

> **Cost note (July 2026):** $2.50/M input, $15.00/M output, $0.25/M cached
> input — half of GPT-5.6 Sol on every axis. Prompts above 272K input tokens
> bill at 2× input and 1.5× output for the session; cache writes bill at 1.25×
> uncached input.
>
> **Rate limits:** Tier 1 starts at 500 RPM / 500K TPM and Tier 5 reaches
> 15K RPM / 40M TPM.
>
> **Migration:** `gpt-5-mini-2025-08-07` is scheduled for shutdown on
> December 11, 2026, with `gpt-5.6-terra` named as its replacement.

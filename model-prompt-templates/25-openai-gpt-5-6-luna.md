---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.6 Luna"
author1: "Prompt Library Team"
post_slug: "25-openai-gpt-5-6-luna"
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
  - "high-volume"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for GPT-5.6 Luna, the fast budget tier: one-unit-of-work-
  per-call pipeline design, cached static prefixes, abstain paths, and
  verified July 2026 specifications.
post_date: "2026-07-25"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.6 Luna (`gpt-5.6-luna`) |
| **Provider** | OpenAI |
| **Tier** | Fast / budget — "optimized for budget-conscious applications"; efficient, high-volume workloads |
| **Context Window** | 1,050,000 tokens (long-prompt pricing applies above 272K input tokens) |
| **Max Output** | 128K tokens |
| **Knowledge Cutoff** | February 16, 2026 |
| **Strengths** | Lowest cost and latency in the GPT-5.6 family, highest throughput ceiling, full built-in tool surface, structured outputs |
| **Best For** | High-volume, low-latency, cost-sensitive workloads — classification, extraction, routing, summarization pipelines, subagent workers |
| **Key Differentiator** | Documented as "Fast" with the family's highest rate-limit ceiling (Tier 5 at 30,000 RPM / 180M TPM, roughly double Sol's and Terra's), at $1.00/$6.00 per million tokens |

> **Spec notes (verified 25 July 2026):** context 1,050,000 tokens / 128K max
> output; knowledge cutoff February 16, 2026; pricing $1.00/M input, $6.00/M
> output, $0.10/M cached input, with 2× input and 1.5× output above 272K input
> tokens and cache writes at 1.25× uncached input; reasoning supported at
> documented capability level "High", speed documented as "Fast"; modalities
> text and image in, text out (no audio or video); tools include web search,
> file search, image generation, code interpreter, hosted shell, apply patch,
> skills, computer use, MCP, and tool search; streaming, function calling, and
> structured outputs supported; fine-tuning not supported. `reasoning.mode:
> "pro"` is documented for `gpt-5.6-sol` and is **not** confirmed for Luna.
> Source: OpenAI model page for `gpt-5.6-luna`, the API model-guidance page,
> and the reasoning guide.

---

## What Sets GPT-5.6 Luna Apart

1. **Throughput headroom, not just a lower price** — Luna's Tier 5 ceiling is
   30,000 RPM / 180M TPM against 15,000 RPM / 40M TPM for Sol and Terra. For fleet
   workloads the rate limit is often the real constraint, and Luna is the only tier
   in the family that lifts it.
2. **Budget tier without a context penalty** — Luna keeps the full 1,050,000-token
   window and 128K output ceiling. A cheap model that can still read an entire
   document set is unusual, and it removes most chunking machinery from pipelines.
3. **Cheapest cached input in the family** — $0.10/M cached input makes a
   static-prefix design (long shared instructions + short variable suffix)
   dramatically cheaper than it looks on the headline rate.

---

## Template Structure

Luna is the tier most often deployed as a pipeline component, so treat the prompt
as an interface contract: one unit of work per call, a fixed output schema, and no
open-ended latitude. Few-shot examples do more here than added prose instructions.

```text
System:
# Identity
You are {{ROLE}} performing {{SINGLE UNIT OF WORK}}.

# Instructions
- {{CONSTRAINTS — the two or three rules that actually matter}}
- If the input does not support a confident answer, return the schema's
  "insufficient" branch rather than guessing.

# Output format
{{Structured Outputs schema name. No prose outside the schema.}}

# Examples
Input: {{sample input}}
Output: {{exact desired output}}

Input: {{edge-case input}}
Output: {{exact desired output for the edge case}}

---

User:
{{THE SINGLE ITEM TO PROCESS}}
```

### Key Prompting Principles for GPT-5.6 Luna

1. **One unit of work per call** — Luna is a pipeline component. Multi-step
   orchestration belongs in your harness (or a Terra/Sol planner), not inside a
   single Luna prompt.
2. **Examples beat instructions** — Two or three input/output pairs, including one
   edge case, produce more consistency than a paragraph of rules — and cost fewer
   tokens per call at volume.
3. **Set `reasoning.effort` low and prove you need more** — Start at `low` (or
   `none` where the task genuinely has no reasoning content, such as routing or
   classification) and escalate only where evals show a measurable gain. On a
   million-call workload, one effort rung is a budget line item.
4. **Design a static prefix for caching** — Put the whole instruction block and all
   examples first, and the variable item last. At $0.10/M cached input this is the
   dominant cost lever; track `cached_tokens` and remember cache writes bill at
   1.25×.
5. **Always use Structured Outputs** — At volume, unparseable responses are the
   failure mode that actually hurts. Define the schema through the API, including an
   explicit branch for "cannot determine."
6. **Give it an abstain path** — A cheap model that guesses is worse than one that
   flags. Make "insufficient evidence" a first-class output value and route those
   items to a higher tier.
7. **Cap output length deliberately** — Set `max_output_tokens` to the real ceiling
   for the task and `text.verbosity` to `low`. Luna inherits the family's 128K
   output limit, which is far more than a pipeline call should ever emit.

---

## Example 1 — Coding Activity (High-Volume Diff Triage)

```text
System:
# Identity
You classify pull-request diffs for an automated review router.

# Instructions
- Classify the diff into exactly one risk category.
- Base the classification on what the diff changes, not on the PR title.
- If the diff touches files you cannot categorize, return "needs_human".

# Output format
Structured Outputs schema `pr_triage_v2`:
{ risk: "low" | "medium" | "high" | "needs_human",
  reason: string (max 140 chars),
  suggested_reviewers: string[] }

# Examples
Input: diff touching only *.test.ts, additions only
Output: { "risk": "low", "reason": "Test-only additions, no production code paths changed.", "suggested_reviewers": [] }

Input: diff modifying auth/session.ts token expiry logic
Output: { "risk": "high", "reason": "Changes session token expiry in the auth path; affects all logged-in users.", "suggested_reviewers": ["security-team"] }

---

User:
[diff]
```

---

## Example 2 — Deep Analysis at Scale (Document Field Extraction)

```text
System:
# Identity
You extract structured contract metadata for a downstream obligations database.

# Instructions
- Extract only fields present in the document. Never infer a missing value
  from context or convention.
- Dates as ISO 8601. Money as integer minor units plus a separate ISO 4217
  currency code.
- If the document is not a contract, return the "not_a_contract" branch.

# Output format
Structured Outputs schema `contract_metadata_v5`. No prose outside the schema.

# Examples
Input: "...between Acme Corp. ('Supplier') and Globex Ltd ('Customer'), dated 3 March 2026, for USD 1,250,000.00..."
Output: { "parties": [{"name": "Acme Corp.", "role": "Supplier"}, {"name": "Globex Ltd", "role": "Customer"}], "effective_date": "2026-03-03", "value": {"amount": 125000000, "currency": "USD"} }

Input: an invoice PDF with no counterparty obligations
Output: { "not_a_contract": true, "document_type_guess": "invoice" }

---

User:
[document text]
```

> This is the shape Luna is built for: the entire instruction block and both
> examples form a cached static prefix, and only the document varies per call.

---

## Example 3 — Executive Communication (Templated Summarization)

```text
System:
# Identity
You compress incident reports into a fixed executive summary format.

# Instructions
- Preserve every number and timestamp exactly as written in the source.
- Never characterize severity beyond what the source states.
- If root cause is listed as undetermined, say undetermined.

# Output format
## Incident (one sentence: what broke, for whom, for how long)
## Impact (one sentence with the customer-facing number)
## Root Cause (one sentence, or "Undetermined")
## Status (one sentence)
Verbosity: low. Never exceed four sentences total.

---

User:
[full incident report]
```

---

## When to Use GPT-5.6 Luna vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| Classification, extraction, routing at very high volume | ✅ GPT-5.6 Luna |
| Latency-critical interactive paths | ✅ GPT-5.6 Luna |
| Subagent workers under a higher-tier planner | ✅ GPT-5.6 Luna |
| Long documents on a tight budget | ✅ GPT-5.6 Luna — full 1M-class window at $1.00/M input |
| Workloads constrained by rate limits, not by cost | ✅ GPT-5.6 Luna — highest ceiling in the family |
| Multi-step agentic orchestration in a single call | ❌ [GPT-5.6 Terra](./24-openai-gpt-5-6-terra.md) |
| Hard reasoning, production coding, security-critical work | ❌ [GPT-5.6 Sol](./23-openai-gpt-5-6-sol.md) |
| Native audio, video, or PDF input | ❌ [Gemini 3.6 Flash](./26-google-gemini-3-6-flash.md) |
| Absolute lowest cost per token | ❌ [Gemini 3.5 Flash-Lite](./27-google-gemini-3-5-flash-lite.md) ($0.30/$2.50) or [Claude Haiku 4.5](./03-anthropic-claude-haiku.md) |

---

## API Quick Reference

```json
{
  "model": "gpt-5.6-luna",
  "input": [
    { "role": "developer", "content": "# Identity\n...\n\n# Output format\n...\n\n# Examples\n..." },
    { "role": "user", "content": "{{SINGLE ITEM}}" }
  ],
  "reasoning": { "effort": "low" },
  "text": { "verbosity": "low" },
  "max_output_tokens": 1000
}
```

> **Cost note (July 2026):** $1.00/M input, $6.00/M output, $0.10/M cached
> input. Prompts above 272K input tokens bill at 2× input and 1.5× output for
> the session; cache writes bill at 1.25× uncached input. Structure prompts
> static-first so the instruction block and examples stay cached.
>
> **Rate limits:** Tier 1 starts at 500 RPM / 500K TPM and Tier 5 reaches
> 30,000 RPM / 180M TPM — the highest ceiling in the GPT-5.6 family.
>
> **Migration:** `gpt-5-nano-2025-08-07` is scheduled for shutdown on
> December 11, 2026, with `gpt-5.6-luna` named as its replacement.

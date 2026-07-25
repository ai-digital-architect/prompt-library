---
post_title: "General-Purpose Prompt Template — Google Gemini 3.6 Flash"
author1: "Prompt Library Team"
post_slug: "26-google-gemini-3-6-flash"
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
  - "agentic"
  - "multimodal"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Gemini 3.6 Flash, Google's agentic workhorse: thinking-
  level tuning, the sampling-parameter and prefill migration changes, native
  multimodal input, and verified July 2026 specifications.
post_date: "2026-07-25"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3.6 Flash (`gemini-3.6-flash`) |
| **Provider** | Google DeepMind |
| **Tier** | High-performance general workhorse — Google's latest model, "designed for the agentic era" |
| **Status** | Stable (latest update July 2026) |
| **Context Window** | 1,048,576 input tokens / 65,536 output tokens |
| **Knowledge Cutoff** | Not stated on the model page — see the Gemini 3.6 Flash model card |
| **Strengths** | Code generation, agentic execution, spatial reasoning, rapid multi-step tool loops, native multimodal input (text, image, video, audio, PDF), token efficiency |
| **Best For** | Balanced production applications, interactive chat, fast code generation, rapid multimodal tasks, agentic loops with tight iteration cycles |
| **Pricing** | $1.50 / $7.50 per 1M input/output tokens (Batch API: $0.75 / $3.75) |

> **Spec notes (verified 25 July 2026):** model code `gemini-3.6-flash`; stable,
> latest update July 2026; 1,048,576 input / 65,536 output tokens; input
> modalities text, image, video, audio, PDF, output text only; supports code
> execution, computer use (Preview), file search, function calling, grounding
> with Google Search, grounding with Google Maps, structured outputs, thinking,
> URL context, Batch API, context caching, flex inference, and priority
> inference; does not support audio generation, image generation, or the Live
> API; pricing $1.50/M input and $7.50/M output, batch at 50%, context caching
> $0.15/M plus $1.00 per hour storage; grounding with Google Search allows 5,000
> free requests per month shared across Gemini 3 models, then $14 per 1,000
> queries. Source: Gemini API model page for Gemini 3.6 Flash, the Gemini API
> pricing page, the "using the latest Gemini models" migration page, and
> Google's launch announcement.

---

## What Sets Gemini 3.6 Flash Apart

1. **Cheaper output than the model it replaces** — At $7.50/M output against Gemini
   3.5 Flash's $9.00/M, with input unchanged at $1.50/M, this is the rare
   generational step that lowers the headline price rather than raising it.
2. **Materially fewer tokens for the same work** — Google reports a 17% reduction in
   output tokens versus 3.5 Flash on the Artificial Analysis Index, and up to 65%
   fewer tokens on DeepSWE specifically, attributing it to reduced "execution loop
   spiraling" — fewer reasoning steps, conversational turns, and tool calls to reach
   the same end state. Combined with the lower output price, real agentic workloads
   get cheaper twice over.
3. **Agentic and computer-use gains are the headline, not chat quality** — Google
   cites DeepSWE 49% (vs. 37% for 3.5 Flash), OSWorld-Verified 83.0% (vs. 78.4%), and
   GDPval-AA v2 1421 (vs. 1349). Position it as an agent runtime first.

---

## Template Structure

Gemini 3.6 Flash follows the Gemini 3.x conventions: direct goal statements,
Markdown delimiters rather than XML tags, all large context before the instruction,
and `thinking_level` as the primary quality/latency dial. Two API-shape changes
arrived with this model — sampling parameters are ignored, and you may no longer
end a request on a model-role turn — so prefill-style steering must move into the
system instruction or a structured output schema.

```text
system_instruction:
You are {{ROLE}} specializing in {{DOMAIN}}.

Rules:
- {{CONSTRAINTS}}
- The current year is 2026. For facts newer than your training data, rely on
  the provided context or Google Search grounding rather than memory.
- Default to concise output; expand only where the task requires it.

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

### Key Prompting Principles for Gemini 3.6 Flash

1. **Tune `thinking_level`, and use the string values** — The default is `medium`,
   carried over from 3.5 Flash. `thinking_budget` is superseded by `thinking_level`
   with string values; drop to `low` or `minimal` for chat and high-throughput
   pipelines, raise to `high` for hard reasoning. This is the primary cost, latency,
   and quality dial.
2. **Delete `temperature`, `top_p`, and `top_k`** — They are deprecated and silently
   ignored on this model, and future versions will return HTTP 400. If you were
   using temperature for output variety, ask for variety in the prompt instead
   ("propose three distinct approaches, then build the one you recommend").
3. **Remove prefilled model turns** — A request ending on a model-role turn now
   errors. Move that steering into `system_instruction`, or pin the shape with a
   structured output schema.
4. **Context first, instruction last** — Google's long-context guidance is unchanged:
   documents, code, and media at the top, the specific question at the very end.
5. **Design for tight agent loops** — The generational gain is in agentic execution,
   so give it function declarations and let it orchestrate rather than scripting each
   step. Fewer turns to the same end state is the behavior you are paying for.
6. **Exploit native multimodality** — Text, image, video, audio, and PDF are all
   equal-class inputs. There is no separate vision pathway to design around.
7. **Ground time-sensitive answers** — Google Search grounding is a built-in tool and
   the model page does not publish a knowledge cutoff; treat anything current-events
   adjacent as requiring grounding. Budget for it: 5,000 free requests per month
   shared across Gemini 3 models, then $14 per 1,000 queries.
8. **Use context caching on repeated prefixes** — $0.15/M cached plus $1.00 per hour
   of storage; worth it whenever the same corpus or instruction block is reused
   across many calls.

---

## Example 1 — Coding Activity (Agentic Bug Hunt)

```text
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

```text
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

> Run this one at `thinking_level: "high"` and cache the requirements document
> if you are evaluating vendors in batches.

---

## Example 3 — Executive Communication

```text
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

## When to Use Gemini 3.6 Flash vs. Other Models

| Scenario | Use Gemini 3.6 Flash? |
|---|---|
| Production agentic workflows and coding agents | ✅ DeepSWE 49% and OSWorld-Verified 83.0%, both ahead of 3.5 Flash |
| Computer-use and spatial-reasoning tasks | ✅ Computer use supported (Preview); OSWorld-Verified 83.0% |
| Stable GA model required for production | ✅ Stable, unlike Gemini 3.1 Pro (Preview) |
| Multimodal extraction with reasoning (PDF, video, audio) | ✅ Native multimodal, ~1M-token context |
| Cost-sensitive agentic loops | ✅ Cheaper output than 3.5 Flash and ~17% fewer output tokens |
| Deepest reasoning on the hardest problems | ⚠️ Consider [Gemini 3.1 Pro](./18-google-gemini-3-1-pro.md) (Preview) |
| Real-time audio conversation | ❌ No Live API and no audio generation on this model |
| Image generation | ❌ Not supported — use a Google image model |
| Massive-volume classification at lowest cost | ❌ [Gemini 3.5 Flash-Lite](./27-google-gemini-3-5-flash-lite.md) ($0.30/$2.50) |

---

## API Quick Reference

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.6-flash",
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

> **Cost note (July 2026):** $1.50 / $7.50 per 1M input/output tokens, with the
> Batch API at 50% ($0.75 / $3.75) and context caching at $0.15/M plus $1.00 per
> hour of storage. Grounding with Google Search is free for the first 5,000
> requests per month across Gemini 3 models, then $14 per 1,000 queries.
>
> **Migration from Gemini 3.5 Flash:** `temperature`, `top_p`, and `top_k` are
> deprecated and ignored, and will return HTTP 400 in future versions — remove
> them. `thinking_budget` gives way to `thinking_level` string values, with the
> `medium` default unchanged. Requests may no longer end on a model-role turn;
> move prefill-style steering into `system_instruction` or structured outputs.

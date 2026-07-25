---
post_title: "General-Purpose Prompt Template — Google Gemini 3.5 Flash-Lite"
author1: "Prompt Library Team"
post_slug: "27-google-gemini-3-5-flash-lite"
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
  - "high-volume"
  - "multimodal"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Gemini 3.5 Flash-Lite, Google's highest-throughput tier:
  minimal-thinking extraction pipelines, when to raise thinking level for
  autonomous subagents, and verified July 2026 specifications.
post_date: "2026-07-25"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) |
| **Provider** | Google DeepMind |
| **Tier** | Fast / lowest cost — "the fastest, lowest-cost model in the 3.5 family" |
| **Status** | Stable (latest update July 2026) |
| **Context Window** | 1,048,576 input tokens / 65,536 output tokens |
| **Knowledge Cutoff** | Not stated on the model page — see the Gemini 3.5 Flash-Lite model card |
| **Strengths** | Throughput (Google cites ~350 output tokens/second), high-volume data parsing, document extraction, structured JSON output, autonomous subagent execution, native multimodal input |
| **Best For** | High-volume classification, extraction, routing, document parsing, and subagent workers where cost and throughput dominate |
| **Pricing** | $0.30 / $2.50 per 1M input/output tokens (Batch and Flex: $0.15 / $1.25) |

> **Spec notes (verified 25 July 2026):** model code `gemini-3.5-flash-lite`;
> stable, latest update July 2026; 1,048,576 input / 65,536 output tokens; input
> modalities text, image, video, audio, PDF, output text only; supports grounding
> with Google Search and Google Maps, code execution, file search, function
> calling, structured outputs, thinking, URL context, context caching, the Batch
> API, and flex and priority inference; does **not** support computer use, the
> Live API, audio generation, or image generation; `thinking_level` defaults to
> `"minimal"`; pricing $0.30/M input (uniform across text, image, video, and
> audio) and $2.50/M output, Batch and Flex at $0.15 / $1.25, Priority at
> $0.54 / $4.50, context caching $0.03/M standard plus $1.00 per million tokens
> per hour of storage. Source: Gemini API model page for Gemini 3.5 Flash-Lite,
> the Gemini API pricing page, the "using the latest Gemini models" migration
> page, and Google's launch announcement.

---

## What Sets Gemini 3.5 Flash-Lite Apart

1. **Throughput is the product** — Google cites roughly 350 output tokens per second,
   which is the reason to pick this model over a cheaper-per-token alternative. On
   bulk jobs, wall-clock time to finish the queue usually matters more than the
   headline rate.
2. **A full-size context window at Flash-Lite prices** — 1,048,576 input tokens for
   $0.30/M means whole documents go in without a chunking layer. That removes more
   pipeline machinery than the price alone suggests.
3. **`thinking_level` defaults to `"minimal"`, deliberately** — Unlike Gemini 3.6
   Flash (`"medium"`), this model is tuned to answer immediately. That is correct for
   extraction and classification and wrong for autonomous subagents, which is the one
   place you should raise it.

---

## Template Structure

Treat a Flash-Lite prompt as an interface contract: one unit of work per call, a
fixed schema, and no open-ended latitude. Gemini 3.x conventions still apply —
Markdown delimiters rather than XML tags, all context before the instruction — and
the 3.5/3.6-generation API changes apply here too: sampling parameters are gone,
`thinking_budget` is replaced by `thinking_level` strings, and a request may not end
on a model-role turn.

```text
system_instruction:
You are {{ROLE}} performing {{SINGLE UNIT OF WORK}}.

Rules:
- {{The two or three constraints that actually matter}}
- Extract or classify only what is present. If the input does not support a
  confident answer, return the schema's "insufficient" branch rather than
  inferring.
- Output must validate against the schema. No prose outside it.

---

User content:

## Context
{{The single item to process — text, image, video, audio, or PDF}}

## Task
{{TASK — one sentence}}

## Output Format
{{Explicit JSON schema, including the "cannot determine" branch}}
```

### Key Prompting Principles for Gemini 3.5 Flash-Lite

1. **Keep `thinking_level: "minimal"` for extraction and classification** — It is the
   default and it is the right one for throughput work. Raising it on a bulk parsing
   job buys latency you did not need.
2. **Raise it to `"medium"` or `"high"` for autonomous subagents** — Google's specific
   guidance: subagents that make tool calls or need multi-step reasoning terminate
   early at `"minimal"`. This is the single most consequential setting on this model.
3. **One unit of work per call** — Orchestration belongs in your harness or in a
   Gemini 3.6 Flash / 3.1 Pro outer loop, not inside a Flash-Lite prompt.
4. **Always specify an explicit schema** — Structured output is the reason this model
   works as a pipeline component. Describe the schema exactly, and include a branch
   for "cannot determine" so the model has somewhere to go other than guessing.
5. **Remove `temperature`, `top_p`, and `top_k`** — Deprecated and ignored on this
   generation, with HTTP 400 coming in future versions. Ask for variety in the prompt
   if you need it.
6. **Never end a request on a model-role turn** — Prefilled model turns now error.
   Move that steering into `system_instruction` or the output schema.
7. **Cache the static prefix** — At $0.03/M cached versus $0.30/M standard input,
   a shared instruction block plus examples pays for itself quickly across a batch.
8. **Use Batch or Flex for anything not interactive** — Both halve the rate to
   $0.15 / $1.25. Reserve the standard tier for latency-sensitive paths and Priority
   ($0.54 / $4.50) for the few that genuinely need it.
9. **Exploit native multimodality** — Image, video, audio, and PDF are equal-class
   inputs at the same $0.30/M rate, which makes bulk document and media extraction
   unusually cheap here.

---

## Example 1 — Coding Activity (Bulk Repository Labeling)

```text
system_instruction:
You label source files for a code-ownership dashboard. You emit JSON only.

Rules:
- Classify by what the file does, not by its directory name.
- If the file is generated, vendored, or a lockfile, return "excluded" with the
  matching reason.
- Never invent an owning team. If no rule matches, return "unassigned".

---

User content:

## Context
[Single source file contents]

## Task
Classify this file for the ownership dashboard.

## Output Format
{
  "category": "service" | "library" | "infrastructure" | "test" | "excluded" | "unassigned",
  "owning_team": string | null,
  "reason": string,
  "excluded_reason": "generated" | "vendored" | "lockfile" | null
}
```

> Run at `thinking_level: "minimal"` through the Batch API. This is the shape
> Flash-Lite is built for: a cached instruction block and one variable file.

---

## Example 2 — High-Volume Document Extraction

```text
system_instruction:
You extract structured claim data from scanned insurance documents for a
downstream adjudication system.

Rules:
- Extract only fields visibly present in the document. Never infer a value from
  convention or from other fields.
- Dates as ISO 8601. Money as integer minor units with a separate ISO 4217 code.
- If the scan is illegible for a field, mark that field "unreadable" rather than
  guessing.
- If the document is not a claim form, return the "not_a_claim" branch.

---

## Context
[Scanned PDF or image of the claim form]

## Task
Extract the claim record.

## Output Format
{
  "not_a_claim": boolean,
  "document_type_guess": string | null,
  "claim_number": string | null,
  "date_of_loss": string | null,
  "claimant": { "name": string | null, "policy_number": string | null },
  "amount": { "value": integer, "currency": string } | null,
  "unreadable_fields": string[]
}
```

---

## Example 3 — Autonomous Subagent Worker

```text
system_instruction:
You are a research subagent. You are given one question and a set of tools. You
answer the question and return, then stop.

Rules:
- Use the search and fetch tools as needed; do not ask for permission.
- Complete the full question before returning. Do not return a plan or a partial
  answer.
- Cite every claim with the URL it came from.
- If the question cannot be answered from available sources, say so explicitly
  and list what you checked.

---

User content:

## Context
[Function tools available: web_search, fetch_url]

## Task
{{The single sub-question assigned to this agent}}

## Output Format
{ "answer": string, "citations": string[], "unresolved": string | null }
```

> Raise this one to `thinking_level: "medium"` or `"high"`. At the `"minimal"`
> default, subagents that need tool calls and multi-step reasoning terminate
> early — this is Google's explicit guidance for the model.

---

## When to Use Gemini 3.5 Flash-Lite vs. Other Models

| Scenario | Use Gemini 3.5 Flash-Lite? |
|---|---|
| High-volume data parsing and document extraction | ✅ The model's stated purpose |
| Structured JSON pipelines at scale | ✅ Structured outputs plus `"minimal"` thinking |
| Autonomous subagent execution | ✅ But raise `thinking_level` to `"medium"` or `"high"` |
| Bulk multimodal extraction (image, video, audio, PDF) | ✅ Uniform $0.30/M input across all modalities |
| Throughput-bound batch jobs | ✅ ~350 output tokens/second; Batch and Flex at half price |
| Balanced production apps and agentic coding loops | ❌ [Gemini 3.6 Flash](./26-google-gemini-3-6-flash.md) |
| Computer use | ❌ Not supported — use Gemini 3.6 Flash (Preview) |
| Real-time audio conversation | ❌ No Live API on this model |
| Deepest reasoning on hard problems | ❌ [Gemini 3.1 Pro](./18-google-gemini-3-1-pro.md) (Preview) |
| Absolute lowest input price | ⚠️ [Gemini 3.1 Flash-Lite](./20-google-gemini-3-1-flash-lite.md) is $0.25/M input, but a generation behind and slower |

---

## API Quick Reference

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction="You extract structured claim data...",
        thinking_config=types.ThinkingConfig(
            thinking_level="minimal"  # default; raise to "medium"/"high" for subagents
        ),
        response_mime_type="application/json",
    ),
    contents="## Context\n...\n\n## Task\n...",
)
print(response.text)
```

> **Cost note (July 2026):** $0.30 / $2.50 per 1M input/output tokens on the
> standard tier, with input priced uniformly across text, image, video, and
> audio. Batch and Flex are $0.15 / $1.25; Priority is $0.54 / $4.50. Context
> caching is $0.03/M standard plus $1.00 per million tokens per hour of storage.
>
> **Migration:** supersedes Gemini 3.1 Flash-Lite and Gemini 2.5 Flash. The
> 3.5/3.6-generation API changes apply — remove `temperature`, `top_p`, and
> `top_k` (deprecated and ignored, HTTP 400 in future versions), replace
> `thinking_budget` with `thinking_level` string values, and stop ending
> requests on a model-role turn.

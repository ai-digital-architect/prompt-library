---
post_title: "General-Purpose Prompt Template — Google Gemini 3.1 Flash-Lite"
author1: "Prompt Library Team"
post_slug: "20-google-gemini-3-1-flash-lite"
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
  Prompt template for Gemini 3.1 Flash-Lite: strict schemas and minimal
  thinking for bulk processing. Superseded by Gemini 3.5 Flash-Lite.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`) |
| **Provider** | Google DeepMind |
| **Tier** | Economy — lowest-cost, lowest-latency tier for high-volume tasks |
| **Status** | Stable (as of June 2026) |
| **Context Window** | 1M input tokens / 64K output tokens |
| **Knowledge Cutoff** | January 2025 |
| **Strengths** | Throughput (~363 tokens/sec output per Google), low cost, flexible reasoning levels, multimodal input (text, images, video, audio, PDFs), surprisingly strong quality for the tier (GPQA Diamond 86.9%, LiveCodeBench 72.0%) |
| **Best For** | High-volume classification, data labeling, extraction pipelines, e-commerce categorization, translation, real-time content generation, latency-sensitive reasoning at scale |
| **Pricing** | $0.25 input (text/image/video), $0.50 input (audio) / $1.50 output per 1M tokens |

---

## What Sets Gemini 3.1 Flash-Lite Apart

1. **Lowest cost and latency in the current Gemini lineup** — $0.25/$1.50 per 1M tokens with ~363 tokens/sec output speed, built for "high-volume, latency-sensitive reasoning tasks" (e-commerce categorization, data labeling, real-time generation).
2. **Thinking off by default, on demand when needed** — Defaults to `thinking_level: "minimal"` for raw speed, but offers flexible reasoning levels — escalate to `low`/`medium`/`high` for the subset of items that need it, instead of routing to a bigger model.
3. **Frontier-class quality for an economy tier** — Google reports GPQA Diamond 86.9%, MMMU-Pro 76.8%, and LiveCodeBench 72.0% — quality that previously required a Pro-tier model, at Lite prices, with the full 1M-token window.

---

## Template Structure

Flash-Lite prompts should be machine-like: short system instruction, rigid output contract, few-shot examples (Google's guidance: "always include few-shot examples"), and large input batches placed before the instruction. Reserve every output token — the output is the expensive part of the pipeline.

```
system_instruction:
You are {{ROLE}} performing {{DOMAIN}} processing at scale.

Rules:
- {{CONSTRAINTS}}
- Output ONLY the specified format. No preamble, no explanation, no markdown fences.
- If an item cannot be processed, output {{ERROR_SENTINEL}} for that item.

---

User content:

## Examples
Input: {{Example input 1}}
Output: {{Example output 1}}

Input: {{Example input 2}}
Output: {{Example output 2}}

## Items
{{TASK input items — batch of records, documents, or images}}

## Task
{{TASK}}

## Output Format
{{OUTPUT_FORMAT — exact JSON schema or delimited format, one record per item}}
```

### Key Prompting Principles for Gemini 3.1 Flash-Lite

1. **Leave thinking at `minimal` for pipelines** — The default `thinking_level: "minimal"` minimizes latency and is right for classification, extraction, and formatting. Only raise it (`low`/`medium`/`high`) for items that genuinely need reasoning — and consider a two-pass design: minimal for all, retry hard cases at a higher level.
2. **Always include few-shot examples** — Per Google's prompting guidance, few-shot examples are the highest-leverage tool for output consistency, which matters most in high-volume pipelines where one format drift breaks the parser.
3. **Enforce a strict output contract** — Use structured output (JSON mode with an explicit schema) or a rigid delimited format, define an error sentinel for unprocessable items, and forbid prose. Downstream code, not a human, reads the output.
4. **Batch inputs into the 1M window** — Amortize per-request overhead by packing many records per call; place all items first and the instruction last, per Google's long-context guidance. Use the Batch API for non-interactive volume.
5. **Use multimodal inputs for document/image pipelines** — Flash-Lite accepts images, video, audio, and PDFs natively at $0.25 per 1M tokens (text/image/video) — invoice extraction, product-photo tagging, and screenshot triage are squarely in-tier.
6. **Keep sampling parameters at defaults** — Like all Gemini 3.x models, do not tune temperature/topP/topK; rely on the prompt and schema for determinism.
7. **Function calling for routing, not orchestration** — Flash-Lite handles simple tool calls (lookup, validate, route) well; leave multi-step agentic orchestration to Gemini 3.5 Flash.

---

## Example 1 — Coding Activity (High-Volume Code Triage)

```
system_instruction:
You classify static-analysis findings. Output ONLY JSON lines, one per finding.
No explanation. If a finding cannot be classified, output
{"id": "<id>", "verdict": "UNPROCESSABLE"}.

---

User content:

## Examples
Input: {"id": "F-101", "rule": "sql-injection", "snippet": "query(`SELECT * FROM users WHERE id=${req.params.id}`)"}
Output: {"id": "F-101", "verdict": "TRUE_POSITIVE", "severity": "critical", "reason": "unsanitized request param in SQL template"}

Input: {"id": "F-102", "rule": "hardcoded-secret", "snippet": "const API_KEY = process.env.API_KEY"}
Output: {"id": "F-102", "verdict": "FALSE_POSITIVE", "severity": "none", "reason": "env var reference, not a literal secret"}

## Items
[Batch of 500 static-analysis findings as JSON lines]

## Task
For each finding: verdict (TRUE_POSITIVE / FALSE_POSITIVE / NEEDS_HUMAN),
severity (critical/high/medium/low/none), and a reason under 15 words.

## Output Format
JSON lines, one object per finding: {"id", "verdict", "severity", "reason"}.
Same order as input. No other text.
```

---

## Example 2 — Extraction Pipeline (Multimodal Documents)

```
system_instruction:
You extract structured data from supplier invoices (PDF images). Output ONLY the
JSON array. Use null for missing fields — never guess values. Amounts as numbers
without currency symbols; dates as ISO 8601.

---

User content:

## Examples
[Example invoice image 1]
Output: {"invoice_number": "INV-2031", "supplier": "Acme GmbH", "date": "2026-05-02", "currency": "EUR", "line_items": [{"sku": "A-100", "qty": 12, "unit_price": 4.50}], "total": 54.00, "vat_id": "DE811234567"}

## Items
[Batch of 40 invoice PDFs attached]

## Task
Extract the schema fields from every invoice. If a field is unreadable or absent,
use null. If an entire document is not an invoice, output
{"invoice_number": null, "error": "NOT_AN_INVOICE"} for it.

## Output Format
A single JSON array with one object per document, in input order:
{"invoice_number", "supplier", "date", "currency", "line_items": [{"sku", "qty",
"unit_price"}], "total", "vat_id", "error"}.
```

---

## Example 3 — Executive Communication (Templated at Volume)

```
system_instruction:
You generate short, factual customer-status summaries for account executives.
Plain business English, no jargon, no speculation beyond the provided data.
Exactly the format specified — these are inserted into a CRM automatically.

---

User content:

## Examples
Input: {"account": "Northwind", "arr": 240000, "renewal": "2026-09-30", "health": 62, "open_tickets": 7, "last_qbr": "2026-03-12", "note": "champion left in April"}
Output:
ACCOUNT: Northwind | ARR: $240K | RENEWAL: Sep 30, 2026
RISK: Elevated — health 62/100, 7 open tickets, champion departed in April.
ACTION: Schedule exec sponsor call before renewal cycle; re-establish champion.

## Items
[Batch of 200 account records as JSON]

## Task
Produce one three-line summary per account: status line, risk line (with the
single biggest risk factor), action line (one concrete next step).

## Output Format
Plain text blocks separated by "---", in input order. Exactly 3 lines per block,
labeled ACCOUNT/RISK/ACTION as in the example. No extra commentary.
```

---

## When to Use Gemini 3.1 Flash-Lite vs. Other Models

| Scenario | Use Flash-Lite? |
|---|---|
| High-volume classification, labeling, categorization | ✅ Built for it — lowest cost, ~363 tok/s |
| Document/invoice/image extraction pipelines | ✅ Native multimodal at $0.25 per 1M input tokens |
| Real-time, latency-sensitive generation (autocomplete, tagging) | ✅ Lowest latency tier |
| Translation and templated content at scale | ✅ Cited use case ("coding, UI generation and translation with high quality") |
| Multi-step agentic workflows with tool orchestration | ❌ Use Gemini 3.5 Flash |
| Hardest reasoning or research synthesis | ❌ Use Gemini 3.1 Pro (Preview) |
| Occasional hard items inside a high-volume stream | ⚠️ Raise `thinking_level` per request, or escalate failures to 3.5 Flash |
| Long-document processing on a budget | ✅ Full 1M-token window at Lite pricing |

---

## API Quick Reference

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction="You classify static-analysis findings...",
        thinking_config=types.ThinkingConfig(
            thinking_level="minimal"  # default for Flash-Lite; raise only for hard items
        ),
        response_mime_type="application/json",  # structured output for pipelines
    ),
    contents="## Examples\n...\n\n## Items\n...\n\n## Task\n...",
)
print(response.text)
```

> **Cost note:** $0.25 / $1.50 per 1M input/output tokens (audio input $0.50).
> Output tokens cost 6x input — keep output contracts terse (codes, short JSON)
> and let the input carry the context. Use the Batch API for non-interactive jobs.

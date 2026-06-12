# General-Purpose Prompt Template — OpenAI GPT-5.4 nano

> **Provenance note:** Model specs and positioning are sourced from OpenAI's model
> docs and prompt-guidance pages (June 2026). The exact `reasoning_effort` levels
> exposed on nano are inferred from the GPT-5.4 family documentation — verify
> against the official gpt-5.4-nano model page for your deployment.

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.4 nano |
| **Provider** | OpenAI |
| **Tier** | Smallest/fastest — cheapest model in the GPT-5.4 family |
| **Context Window** | 400K tokens |
| **Max Output** | 128K tokens |
| **Strengths** | Speed, cost, classification, data extraction, ranking, routing, narrow closed-output tasks, sub-agent execution units |
| **Best For** | High-volume simple tasks where speed and cost matter most: labeling, entity extraction, intent routing, enum/JSON outputs, lightweight sub-agents |
| **Key Differentiator** | OpenAI positions nano "for tasks where speed and cost matter most like classification, data extraction, ranking, and sub-agents." Avoid multi-step orchestration on nano — route planning and ambiguity to larger models. |

> **Spec notes (sourced June 2026):** knowledge cutoff Aug 31, 2025; pricing
> $0.20/M input, $0.02/M cached input, $1.25/M output; supports streaming,
> function calling, Structured Outputs, web search, file search, image generation,
> code interpreter, and MCP. Computer use and tool search are **not** supported.

---

## What Sets GPT-5.4 nano Apart

1. **Lowest cost per call in the lineup** — At $0.20/M input and $1.25/M output
   with $0.02/M cached input, nano makes per-event LLM calls economical at
   volumes where even mini's pricing adds up.
2. **Closed-output specialist** — Designed for tasks with a small, well-defined
   answer space: labels, enums, scores, extracted fields, routing decisions.
   Paired with Structured Outputs, it produces strict machine-parseable results.
3. **Deliberately narrow** — No computer use, no tool search, and OpenAI's own
   guidance says to avoid multi-step orchestration on nano. Its reliability comes
   from doing one bounded thing per call.

---

## Template Structure

GPT-5.4 nano prompts should read like a function specification: one task per call,
an enumerated answer space, explicit tie-breaking rules, and a fallback label for
inputs that don't fit. Keep prompts short, static, and cache-friendly — nano is
usually deployed at volume where cached-input pricing dominates cost.

```text
System:
# Identity
You are {{ROLE}} performing {{DOMAIN}} {{TASK — one bounded operation, e.g.
"ticket intent classification"}}.

# Instructions
- Choose exactly one value per field from the allowed values below.
- {{CONSTRAINTS — decision rules, stated as if/then}}
- If the input matches none of the categories, use "other".
- If the input is empty or unreadable, use "invalid_input".
- Output the answer only — no explanation, no preamble.

# Allowed values
- category: {{enum values}}
- priority: {{enum values}}

# Output format
{{OUTPUT_FORMAT — exact JSON schema or single-token label. Enforce via
Structured Outputs.}}

---

User:
{{Single input item to classify / extract from / route}}
```

### Key Prompting Principles for GPT-5.4 nano

1. **One bounded task per call** — Nano is built for narrow, closed-output tasks
   (labels, enums, JSON fields). Avoid multi-step orchestration; if a workflow
   needs planning or ambiguity resolution, route that to GPT-5.4 or GPT-5.5 and
   give nano only the atomic decision.
2. **Enumerate the answer space** — List every allowed value explicitly and always
   include fallback labels ("other", "invalid_input"). Nano should never have to
   invent a category.
3. **Write decision rules, not goals** — Use explicit if/then rules and
   tie-breakers ("if both refund and complaint apply, choose refund"). Structural
   scaffolding beats loose imperative language on small models.
4. **Enforce format with Structured Outputs, suppress prose** — Combine a strict
   JSON schema with "output the answer only" and `verbosity: low`. Nano at volume
   should never spend output tokens on explanation.
5. **Keep `reasoning_effort` minimal** — For speed- and cost-sensitive
   execution tasks, run at the lowest reasoning setting. If a nano task seems to
   need more thinking, that's a signal to move it up a tier, not to add effort.
6. **Design for prompt caching** — Keep the system prompt static (identity, rules,
   enums first) and put only the per-item input in the user message. At nano's
   $0.02/M cached-input rate, a stable prefix makes high-volume pipelines nearly
   free on the input side.

---

## Example 1 — Coding-Adjacent Activity (Log Triage Classification)

```text
System:
# Identity
You are a log-line triage classifier in a CI failure-routing pipeline.

# Instructions
- Classify each log excerpt into exactly one failure_type and one owner_team.
- If/then rules:
  - If the excerpt contains a compiler or type error → failure_type
    "build_error", owner_team "owning_service_team".
  - If a test assertion failed → "test_failure", "owning_service_team".
  - If a dependency download, registry, or network error → "infra_flake",
    "platform_team".
  - If an out-of-memory or timeout kill → "resource_limit", "platform_team".
  - If both a test failure and an infra error appear, choose "infra_flake".
- If nothing matches, use "other" / "triage_queue".
- Output the answer only.

# Allowed values
- failure_type: build_error | test_failure | infra_flake | resource_limit | other
- owner_team: owning_service_team | platform_team | triage_queue

# Output format
JSON: { "failure_type": "...", "owner_team": "...", "retry_recommended": boolean }
(retry_recommended is true only for infra_flake and resource_limit.)

---

User:
[2026-06-12T08:14:22Z] ERROR: connect ETIMEDOUT registry.internal:443
npm ERR! network request to https://registry.internal/lodash failed
```

---

## Example 2 — High-Volume Data Extraction

```text
System:
# Identity
You are a field extractor for inbound vendor invoices.

# Instructions
- Extract only the fields in the schema; never add fields.
- Copy values exactly as written, then normalize: dates to YYYY-MM-DD,
  amounts to a number with no currency symbol, currency to ISO 4217.
- If a field is absent or illegible, set it to null — never guess.
- If the document is not an invoice, set "is_invoice" to false and all other
  fields to null.
- Output the answer only.

# Output format
JSON: { "is_invoice": boolean, "vendor_name": string|null,
"invoice_number": string|null, "invoice_date": string|null,
"due_date": string|null, "total_amount": number|null,
"currency": string|null, "po_reference": string|null }

---

User:
[OCR text of one invoice document]
```

---

## Example 3 — Executive Communication Routing (Inbox Triage)

```text
System:
# Identity
You are an inbox triage router for a CEO's executive assistant team.

# Instructions
- Assign exactly one route and one urgency per message.
- If/then rules:
  - Board members, named investors, or regulators → route "principal",
    urgency at least "today".
  - Press or analyst requests → "comms_team".
  - Sales, vendor pitches, or event invitations → "ea_queue".
  - Internal escalations mentioning "legal", "security incident", or
    "resignation" → "principal", urgency "now".
- If both principal and comms rules match, choose "principal".
- If the sender or intent is unclear, use "ea_queue" / "this_week".
- Output the answer only.

# Allowed values
- route: principal | comms_team | ea_queue
- urgency: now | today | this_week

# Output format
JSON: { "route": "...", "urgency": "...", "one_line_reason": string (≤ 12 words) }

---

User:
From: jmorrison@sequoiacap.example
Subject: Q2 numbers ahead of Thursday's board call
Body: Hi — before Thursday, can we get 30 minutes on the revised Q2
forecast? A few of us have questions on the EMEA miss.
```

---

## When to Use GPT-5.4 nano vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| Classification, labeling, ranking at high volume | ✅ GPT-5.4 nano |
| Field extraction into a strict JSON schema | ✅ GPT-5.4 nano |
| Intent detection and message routing | ✅ GPT-5.4 nano |
| Atomic sub-agent decisions inside a larger system | ✅ GPT-5.4 nano |
| Latency-critical per-event calls (cost-dominated pipelines) | ✅ GPT-5.4 nano |
| Multi-step orchestration or planning | ❌ GPT-5.4 or GPT-5.5 |
| Summarization pipelines and mid-complexity coding | ❌ GPT-5.4 mini |
| Computer use or tool search workflows | ❌ GPT-5.4 mini (nano does not support them) |
| Ambiguous inputs requiring judgment | ❌ GPT-5.4 or GPT-5.5 |

---

## API Quick Reference

```json
{
  "model": "gpt-5.4-nano",
  "input": [
    { "role": "developer", "content": "# Identity\nYou are {{ROLE}}...\n\n# Instructions\n...\n\n# Allowed values\n...\n\n# Output format\n..." },
    { "role": "user", "content": "{{Single item to classify}}" }
  ],
  "reasoning": { "effort": "none" },
  "text": {
    "verbosity": "low",
    "format": {
      "type": "json_schema",
      "name": "triage_result",
      "schema": { "type": "object", "properties": { "route": { "type": "string" } }, "required": ["route"], "additionalProperties": false }
    }
  },
  "max_output_tokens": 200
}
```

> **Cost note**: $0.20/M input, $0.02/M cached input, $1.25/M output (June 2026).
> Keep the system prompt static to maximize cache hits, cap `max_output_tokens`
> aggressively, and use the Batch API for non-interactive volume.

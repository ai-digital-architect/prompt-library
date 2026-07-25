---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.4 mini"
author1: "Prompt Library Team"
post_slug: "16-openai-gpt-5-4-mini"
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
  - "gpt-5"
  - "legacy"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for GPT-5.4 mini: explicit scaffolding, concrete examples,
  and tight output formats for production pipelines. No longer listed by
  OpenAI — prefer GPT-5.6 Terra or Luna.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Provenance note:** Model specs and positioning are sourced from OpenAI's model
> docs and prompt-guidance pages (June 2026). The exact `reasoning_effort` levels
> exposed on mini are inferred from the GPT-5.4 family documentation — verify
> against the official gpt-5.4-mini model page for your deployment.

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.4 mini |
| **Provider** | OpenAI |
| **Tier** | Mid-tier — faster, lower-cost sibling of GPT-5.4 for high-volume workloads |
| **Context Window** | 400K tokens |
| **Max Output** | 128K tokens |
| **Strengths** | Strong coding for its tier, computer use, subagent execution, structured well-bounded tasks, function calling, full tool support (including computer use and tool search) |
| **Best For** | Production pipelines, summarization at scale, mid-complexity coding, subagents inside larger agent systems, computer-use automation where flagship cost is unjustified |
| **Key Differentiator** | OpenAI positions it as "our strongest mini model yet for coding, computer use, and subagents." It is more literal than GPT-5.4: it performs best when ambiguity is low and step order is explicit. |

> **Spec notes (sourced June 2026):** knowledge cutoff Aug 31, 2025; pricing
> $0.75/M input, $0.075/M cached input, $4.50/M output; supports streaming,
> function calling, Structured Outputs, web search, file search, image generation,
> code interpreter, computer use, MCP, and tool search. Fine-tuning not currently
> supported.

---

## What Sets GPT-5.4 mini Apart

1. **Mini-tier price with near-frontier tooling** — Unlike most small models,
   mini supports the full tool surface including computer use and tool search,
   making it viable as the executor inside agent systems at 30% of GPT-5.4's
   input price.
2. **Built for subagents** — OpenAI explicitly positions mini for subagent roles:
   a larger model plans and routes, mini executes well-bounded subtasks reliably
   and cheaply.
3. **Literal, scaffold-loving execution** — Mini is more literal than GPT-5.4. It
   is strongest when ambiguity is low, steps are numbered, and decision rules are
   explicit. Show it the correct flow, not just the final format.

---

## Template Structure

GPT-5.4 mini rewards structural scaffolding over loose imperative language. Give
it numbered steps, explicit decision rules, and a locked output contract. Route
genuinely ambiguous or open-ended planning to GPT-5.4 or GPT-5.5 and hand mini the
well-bounded execution.

```text
System:
# Identity
You are {{ROLE}}, working in {{DOMAIN}}.

# Instructions
Follow these steps in order:
1. {{Step 1 — explicit, bounded}}
2. {{Step 2}}
3. {{Step 3 — include the verification step explicitly}}

Rules:
- {{CONSTRAINTS — hard rules, stated individually, not bundled}}
- If required input is missing or ambiguous: {{ask / mark as blocked with the
  exact missing field / proceed with a stated default}}.

# Output format
{{OUTPUT_FORMAT — exact sections in exact order, with length limits attached to
the specific section they govern. Prefer Structured Outputs for JSON.}}

---

User:
{{TASK}}

Context:
{{Input data, code, or documents — clearly delimited}}
```

### Key Prompting Principles for GPT-5.4 mini

1. **Scaffold the flow, don't just describe the goal** — Mini is more literal than
   GPT-5.4. Use numbered steps and explicit decision rules ("if X, do A; otherwise
   B") rather than outcome-only prompts. Show the correct flow, not just the final
   format.
2. **Keep ambiguity out of the prompt** — Mini is strongest when ambiguity is low.
   Define exactly what to do when inputs are missing: ask, proceed with a stated
   default, or mark the item blocked with the exact missing data.
3. **Start `reasoning_effort` low** — For execution-heavy pipeline work, start in
   the `none`-to-`medium` range and treat reasoning effort as a last-mile tuning
   knob. Before escalating, add explicit completeness checks and verification
   steps to the prompt — that usually fixes more than extra thinking does.
4. **Lock the output contract** — Use the `verbosity` parameter plus prompt-level
   structure: "Return exactly the sections requested, in the requested order,"
   with length limits applied only to the sections they're intended for. For
   machine-consumed output, use Structured Outputs.
5. **Use it as the executor, not the planner** — In multi-agent systems, have
   GPT-5.4 or GPT-5.5 do planning, decomposition, and ambiguity resolution, then
   delegate bounded subtasks (file edits, lookups, summarization units, computer-use
   actions) to mini with persistence rules: when to retry, when to parallelize
   independent lookups, and to verify before finalizing.
6. **Maintain completeness checklists for batch work** — For list/batch tasks,
   instruct mini to keep an internal checklist and confirm full coverage before
   finishing; have it mark blocked items with the exact missing data.

---

## Example 1 — Mid-Complexity Coding (Pipeline Component)

```text
System:
# Identity
You are a backend engineer implementing well-specified components in a Python
data platform.

# Instructions
Follow these steps in order:
1. Restate the component's input/output contract in 3 bullets.
2. Implement the component exactly as specified — do not redesign the interface.
3. Write pytest tests covering the happy path and every listed failure mode.
4. Run through each acceptance criterion and confirm it is met.

Rules:
- Python 3.12, type hints required, no new third-party dependencies.
- All errors must raise the typed exceptions defined in errors.py — never bare
  Exception.
- If a requirement conflicts with the existing interface, stop and report the
  conflict instead of choosing silently.

# Output format
Sections in order: Contract Summary, Implementation (fenced block with
filename), Tests (fenced block with filename), Acceptance Check (table:
criterion | met? | evidence).

---

User:
Implement a `BatchDeduplicator` class for our ingestion pipeline.

Context:
- Interface (already defined in pipeline/interfaces.py):
  `dedupe(records: list[Record], window_hours: int) -> DedupeResult`
- A record is a duplicate if (source_id, payload_hash) was seen within the
  window. Seen-set is provided via the injected `SeenStore` protocol.
- Failure modes to handle: SeenStore timeout (retry once, then raise
  StoreUnavailableError), malformed record (skip, count in
  DedupeResult.skipped), empty input (return empty result, no store calls).
- Acceptance criteria: O(n) store lookups via batch get, no mutation of input
  list, deterministic output order.
```

---

## Example 2 — Production Summarization Pipeline

```text
System:
# Identity
You are a summarization engine inside a customer-intelligence pipeline. Your
output is machine-parsed and shown to account managers.

# Instructions
Follow these steps in order:
1. Read the full ticket thread.
2. Classify overall sentiment: positive | neutral | negative | escalating.
3. Extract every distinct customer request or complaint (no duplicates).
4. Write the summary to the output contract.
5. Verify: every extracted item must be traceable to a specific message —
   drop anything you cannot trace.

Rules:
- Never include personally identifying information beyond first name and role.
- Never infer intent that is not stated; mark uncertain items "unconfirmed".
- If the thread is empty or unreadable, return status "no_content" and stop.

# Output format
JSON only, matching the provided schema: { "status", "sentiment",
"summary" (≤ 80 words), "requests": [ { "text", "message_ref",
"confirmed" } ], "escalation_recommended": boolean }.

---

User:
Summarize the following support thread.

Context:
[Ticket #48211 — full message thread pasted here]
```

---

## Example 3 — Executive Communication (Operational Brief)

```text
System:
# Identity
You are a communications specialist who turns operational data into weekly
executive briefs.

# Instructions
Follow these steps in order:
1. Identify the 3 most decision-relevant changes vs. last week.
2. For each, state the change, the number behind it, and the action needed
   (or "no action — monitoring").
3. List risks that crossed a threshold this week, with the threshold named.
4. Verify every figure against the supplied data — do not carry over numbers
   from prior briefs.

Rules:
- 300 words maximum, total.
- Plain declarative sentences; no adjectives without a number attached.
- If data for a standing section is missing, write "Data unavailable this
  week" — do not estimate.

# Output format
Sections in order: Top 3 Changes, Risk Threshold Alerts, Decisions Needed
(table: decision | owner | needed by).

---

User:
Produce this week's engineering operations brief for the VP of Engineering.

Context:
- Deploy frequency: 41/week (prev 44). Change failure rate: 4.1% (prev 2.8%,
  threshold 4%). MTTR: 31 min (prev 29). On-call pages: 18 (prev 9).
- Incident INC-291 (payments latency, Sev2) consumed 3 engineer-days.
- Hiring: 2 backend offers accepted; platform team still 1 short.
- Cloud spend: $412K month-to-date, tracking 6% over budget.
```

---

## When to Use GPT-5.4 mini vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| High-volume production pipelines (summarization, transformation) | ✅ GPT-5.4 mini |
| Well-bounded, structured tasks with low ambiguity | ✅ GPT-5.4 mini |
| Subagent executor inside a larger agent system | ✅ GPT-5.4 mini |
| Computer-use automation on a budget | ✅ GPT-5.4 mini |
| Mid-complexity coding against a clear spec | ✅ GPT-5.4 mini |
| Open-ended planning, decomposition, or ambiguous requirements | ❌ GPT-5.4 or GPT-5.5 |
| Complex multi-step reasoning and frontier coding | ❌ GPT-5.5 |
| Pure classification/extraction/routing at maximum volume | ❌ GPT-5.4 nano (cheaper) |
| Contexts beyond 400K tokens | ❌ GPT-5.4 or GPT-5.5 (1M window) |

---

## API Quick Reference

```json
{
  "model": "gpt-5.4-mini",
  "input": [
    { "role": "developer", "content": "# Identity\nYou are {{ROLE}}...\n\n# Instructions\nFollow these steps in order:\n1. ...\n\n# Output format\n..." },
    { "role": "user", "content": "{{TASK}}" }
  ],
  "reasoning": { "effort": "low" },
  "text": { "verbosity": "low" },
  "max_output_tokens": 4000
}
```

> **Cost note**: $0.75/M input, $0.075/M cached input, $4.50/M output (June 2026) —
> 30% of GPT-5.4's price. For execution-heavy pipelines, start at
> `reasoning.effort` in the `none`-to-`low` range and escalate only when evals
> show measurable gains.

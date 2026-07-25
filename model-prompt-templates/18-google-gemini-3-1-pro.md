---
post_title: "General-Purpose Prompt Template — Google Gemini 3.1 Pro"
author1: "Prompt Library Team"
post_slug: "18-google-gemini-3-1-pro"
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
  - "multimodal"
  - "reasoning"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Gemini 3.1 Pro, the deepest reasoner in the Gemini
  lineup: always-on thinking, context-first instruction-last ordering, and
  multimodal research synthesis examples.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3.1 Pro (`gemini-3.1-pro-preview`) |
| **Provider** | Google DeepMind |
| **Tier** | Flagship — advanced reasoning, agentic coding, and multimodal understanding |
| **Status** | Preview (as of June 2026) |
| **Context Window** | 1M input tokens / 64K output tokens |
| **Knowledge Cutoff** | January 2025 |
| **Strengths** | Deepest reasoning in the Gemini lineup, agentic and "vibe" coding, native multimodal input (text, images, audio, video, PDFs), long-context coherence, tool use |
| **Best For** | Complex problem-solving, long-horizon agentic workflows, full-codebase analysis, scientific reasoning, multimodal research synthesis |
| **Pricing** | $2.00 / $12.00 per 1M input/output tokens (prompts ≤ 200K); $4.00 / $18.00 (prompts > 200K) |

> **Note:** Preview model — specifications and pricing may change before general availability. Confirm against the current Gemini API model page: https://ai.google.dev/gemini-api/docs/models

---

## What Sets Gemini 3.1 Pro Apart

1. **A step-change in abstract reasoning** — Google reports 77.1% on ARC-AGI-2 (vs. 31.1% for Gemini 3 Pro) and 51.4% on Humanity's Last Exam with search tools (vs. 45.8%), making it the deepest reasoner in the Gemini family.
2. **Always-on thinking** — Thinking cannot be disabled on Gemini 3.1 Pro. It defaults to `thinking_level: "high"` with dynamic adjustment; `minimal` is not supported. Design prompts assuming the model will reason before answering.
3. **Meaningfully improved tool use and agentic coding** — Google highlights stronger multi-step tool orchestration and agentic coding versus Gemini 3 Pro, positioning it for long-horizon agent loops with the full 1M-token window.

---

## Template Structure

Gemini 3.1 Pro responds best to direct, concisely stated goals with clear
section delimiters (Markdown headings, not XML tags). Per Google's official
prompting guidance for Gemini 3.x: place large context first and the specific
instruction at the very end, keep generation parameters at their defaults, and
explicitly request verbosity if you want a detailed response — by default the
model answers efficiently.

```
system_instruction:
You are {{ROLE}} specializing in {{DOMAIN}}.

Capabilities and standards:
- {{Relevant capability or quality standard 1}}
- {{Relevant capability or quality standard 2}}

Behavioral rules:
- {{CONSTRAINTS}}
- The current year is 2026. Your knowledge cutoff is January 2025 — for facts after
  that date, rely on provided context or grounding rather than memory.

---

User content:

## Context
{{Background, documents, code, or multimodal inputs — images, audio, video, PDFs.
Place ALL large context here, before the task.}}

## Task
{{TASK}}

## Requirements
1. {{Requirement 1}}
2. {{Requirement 2}}
3. {{Requirement 3}}

## Output Format
{{OUTPUT_FORMAT — e.g., JSON schema, Markdown report structure, code-only}}
```

### Key Prompting Principles for Gemini 3.1 Pro

1. **Plan around always-on thinking** — You cannot disable thinking on 3.1 Pro. Default is `thinking_level: "high"` (dynamic); set `"low"` for simple instruction-following to cut latency and cost. `minimal` is not supported on this model.
2. **Context first, instruction last** — Google's official long-context guidance: supply all documents/code/media first, then place the specific question or instruction at the very end of the prompt.
3. **Be direct; request verbosity explicitly** — Gemini 3.x defaults to efficient answers. Avoid persuasive filler; if you need a conversational or exhaustive response, say so explicitly.
4. **Treat all modalities as equal-class inputs** — Combine text, images, audio, video, and PDFs in one prompt and reference each modality explicitly in your instructions ("In the attached video at 02:14…").
5. **Keep sampling parameters at defaults** — Google strongly recommends not modifying temperature/topP/topK for Gemini 3.x models; altered values can cause unexpected behavior on complex tasks.
6. **Use function calling and Google Search grounding** — 3.1 Pro supports function calling, structured output, code execution, and grounding with Google Search. Ground time-sensitive claims rather than relying on the January 2025 cutoff.
7. **Anchor time and knowledge cutoff in the system instruction** — Add clauses like "The current year is 2026" and "Your knowledge cutoff is January 2025" to prevent stale-date reasoning.

---

## Example 1 — Coding Activity (Agentic Refactor)

```
system_instruction:
You are a principal software engineer leading a high-stakes refactor. You write
production-quality code with rigorous error handling and tests. You explain design
decisions concisely and state trade-offs honestly.

---

User content:

## Context
[Attach or paste the full service codebase — up to 1M tokens. Gemini 3.1 Pro
maintains coherence across the entire window.]

## Task
Refactor this monolithic order-processing service into a modular hexagonal
architecture while preserving exact external behavior.

## Requirements
1. Identify and document every external behavior (API contracts, side effects,
   event emissions) before proposing changes.
2. Propose the target module boundaries (domain, ports, adapters) with a Mermaid
   diagram.
3. Produce the refactored code for the two highest-risk modules in full.
4. Generate characterization tests that lock in current behavior before refactor.
5. Provide a step-by-step migration plan that keeps the service deployable at
   every step.

## Output Format
Markdown report: ## Behavior Inventory, ## Target Architecture (with Mermaid),
## Refactored Modules (fenced code), ## Characterization Tests, ## Migration Plan.
```

---

## Example 2 — Deep Analysis and Research (Multimodal, Long-Context)

```
system_instruction:
You are a senior research analyst producing evidence-based assessments for an
investment committee. You weight primary data over projections, reconcile
conflicting sources explicitly, and flag claims with insufficient evidence.

---

User content:

## Context
[Attach: 12 PDF analyst reports, 3 recorded expert-interview audio files, and a
45-minute factory-tour video. Gemini 3.1 Pro processes all of these natively in
a single request.]

## Task
Assess whether the target company's claimed manufacturing-automation advantage is
real and durable, synthesizing across all attached materials.

## Requirements
1. Cross-reference automation claims in the PDFs against what is visible in the
   factory-tour video — cite video timestamps for each observation.
2. Extract and reconcile conflicting throughput figures across the analyst reports.
3. From the interview audio, identify any expert hedging or caveats that the
   written reports omit.
4. Surface insights mentioned in multiple independent sources but emphasized in
   none (cross-source signal).
5. Rate each major claim High/Medium/Low confidence with sourcing rationale.

## Output Format
## Executive Assessment (≤ 600 words)
## Claim-by-Claim Verification Table | Claim | Evidence | Video Timestamp | Confidence |
## Cross-Source Insights
## Gaps and Unverifiable Claims
```

---

## Example 3 — Executive Communication

```
system_instruction:
You are a strategy consultant who writes board-ready communications using the
pyramid principle: answer first, then supporting evidence. Every section carries a
single "so what." You write for time-poor executives who skim.

---

User content:

## Context
- Global logistics company, $12B revenue, evaluating an AI-driven route
  optimization program.
- Pilot across 2 regional hubs cut fuel cost 9% and late deliveries 22%.
- Board concerns: data quality across 40 legacy TMS instances, union response to
  algorithmic dispatch, and a competitor's failed $80M AI program last year.

## Task
Draft a 2-page board memo recommending a $30M, 3-year enterprise rollout.

## Requirements
1. Open with the recommendation and the pilot proof points.
2. Address each board concern head-on with a mitigation, including what we will
   do differently from the failed competitor program.
3. Include a phased investment table (Year 1/2/3, spend, expected savings, gates).
4. Close with a specific decision ask for this board meeting.

## Output Format
Board memo in Markdown: TO/FROM/DATE/RE header, ## Recommendation,
## Evidence from Pilot, ## Risks and Mitigations, ## Investment Plan (table),
## Decision Requested. Precise, data-forward tone; no hype.
```

---

## When to Use Gemini 3.1 Pro vs. Other Models

| Scenario | Use Gemini 3.1 Pro? |
|---|---|
| Hardest reasoning problems (abstract, scientific, multi-constraint) | ✅ Strongest Gemini reasoner (ARC-AGI-2 77.1%) |
| Full-codebase or multi-document analysis up to 1M tokens | ✅ 1M context with strong coherence |
| Mixed media research (PDFs + audio + video in one pass) | ✅ Native multimodal |
| Long-horizon agentic coding with heavy tool use | ✅ Improved tool use vs. 3 Pro |
| Latency-sensitive interactive chat | ❌ Use Gemini 3.5 Flash |
| High-volume classification/extraction pipelines | ❌ Use Gemini 3.1 Flash-Lite |
| Stable production workloads requiring a GA model | ⚠️ 3.1 Pro is Preview — use Gemini 3.5 Flash for stability |
| Simple tasks where thinking overhead wastes cost | ❌ Use Gemini 3.5 Flash or 3.1 Flash-Lite |

---

## API Quick Reference

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    config=types.GenerateContentConfig(
        system_instruction="You are a principal software engineer...",
        thinking_config=types.ThinkingConfig(
            thinking_level="high"  # default; "low" for faster/cheaper. "minimal" NOT supported; thinking cannot be disabled on 3.1 Pro
        ),
        tools=[types.Tool(google_search=types.GoogleSearch())],  # optional grounding
    ),
    contents="## Context\n...\n\n## Task\n...",
)
print(response.text)
```

> **Cost note:** Pricing is tiered by prompt length — $2.00/$12.00 per 1M input/output
> tokens at ≤ 200K prompt tokens, rising to $4.00/$18.00 above 200K. For 1M-context
> jobs, batch related questions into one request rather than re-sending the corpus.

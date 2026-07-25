---
post_title: "General-Purpose Prompt Template — Anthropic Claude Haiku 4.5"
author1: "Prompt Library Team"
post_slug: "03-anthropic-claude-haiku"
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
  - "anthropic"
  - "claude-haiku"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Claude Haiku 4.5: lean prompts, explicit output formats,
  and one-unit-of-work-per-call design for high-volume classification,
  extraction, and subagent execution.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Haiku 4.5 |
| **Provider** | Anthropic |
| **Tier** | Fast frontier — speed and cost efficiency at near-frontier quality |
| **API Model ID** | `claude-haiku-4-5` (or pinned: `claude-haiku-4-5-20251001`) |
| **Context Window** | 200K tokens |
| **Max Output** | 64K tokens |
| **Strengths** | Low latency, high throughput, cost efficiency, classification, extraction, lightweight RAG, real-time chat, agentic subtasks |
| **Best For** | High-volume pipelines, real-time assistants, batch processing, subtask execution in multi-agent systems, rapid prototyping |
| **Pricing** | $1 / $5 per million input/output tokens |

---

## Template Structure

Haiku 4.5 is optimized for speed and pragmatic execution. It performs best with tightly scoped, well-structured prompts. Minimize ambiguity — Haiku excels when the problem is well-defined. Use explicit output schemas, few-shot examples, and constrained response formats. Extended thinking is available but should be enabled selectively for genuinely complex tasks.

```
You are {{ROLE}}.

Task: {{One-sentence task description}}

Input: {{The data or content to process}}

Rules:
- {{Rule 1 — keep rules short and concrete}}
- {{Rule 2}}
- Respond only in {{format: JSON / markdown table / bullet list / etc.}}

Example:
Input: {{sample input}}
Output: {{sample output}}
```

### Key Prompting Principles for Haiku 4.5

1. **Keep prompts lean** — Haiku responds well to concise instructions. Remove filler and be precise.
2. **Use structured output formats** — Specify JSON schemas, tables, or strict formats. Haiku's instruction-following is strong when the target format is explicit.
3. **Few-shot examples are critical** — One or two examples improve consistency dramatically, especially for classification and extraction.
4. **Enable extended thinking selectively** — Haiku 4.5 supports extended thinking (a first for Haiku models), but use it only for genuinely hard reasoning tasks to preserve speed advantage.
5. **Design for pipelines** — Haiku is ideal as a worker in multi-model architectures. Sonnet plans, Haiku executes.
6. **Batch aggressively** — Haiku's low cost makes it viable for high-volume processing. Design prompts that handle one unit of work cleanly. (Note: Haiku 4.5 does not accept the `effort` parameter — that is an Opus/Sonnet 4.6+ feature.)

---

## Example 1 — Coding Activity

```
You are a code generator. Produce clean, working code with no explanation.

Task: Generate a Python function that validates and normalizes email addresses.

Requirements:
- Accept a string, return a normalized email or raise ValueError.
- Normalize: lowercase, strip whitespace, remove dots from Gmail local parts,
  handle "+" aliases.
- Validate format using regex (no external libraries).
- Include type hints.
- Include 5 pytest test cases covering: valid email, Gmail dot removal, plus alias,
  invalid format, whitespace handling.

Output format: Two code blocks — function.py and test_function.py. No prose.

Example:
Input: " John.Doe+work@Gmail.com "
Output: "johndoe@gmail.com"
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
You are a solutions architect providing a concise technical comparison.

Task: Compare three API gateway options for a Kubernetes-based microservices
platform and recommend one.

Context:
- 40 microservices, 15K requests/second peak
- Must support: rate limiting, JWT validation, request transformation, gRPC
- Team has 2 platform engineers (limited capacity)
- Budget: infrastructure cost must stay under $2,000/month

Options to compare:
1. Kong (self-hosted on K8s)
2. AWS API Gateway + VPC Link
3. Envoy Gateway (open source)

For each option, evaluate:
- Setup complexity (days to production)
- Operational burden (maintenance hours/month)
- Feature coverage (which requirements are native vs. plugin)
- Monthly cost estimate at stated traffic
- Failure modes and recovery

Enable extended thinking for this task.

Output format: Comparison table, followed by a 3-paragraph recommendation with
the primary trade-off explicitly stated. End with "Risks to monitor" — 2-3 bullets.
```

---

## Example 3 — Executive Communication / Presentation

```
You are a business writer. Write clear, direct content for executive audiences.

Task: Draft a one-page executive briefing on the decision to adopt a zero-trust
security architecture.

Audience: CEO and CFO (non-technical, care about cost and risk).

Structure:
1. **The Problem** (3 sentences): What risk are we exposed to today?
2. **The Solution** (3 sentences): What is zero-trust and what does it change?
3. **Investment Required**: Table with Year 1 and Year 2 costs broken into
   technology, personnel, and training.
4. **Expected Outcomes**: 3 bullet points with quantified impact.
5. **Timeline**: Single-line summary of key milestones.
6. **Recommendation**: One sentence.

Constraints:
- Total length: under 400 words.
- No acronyms without definition.
- No technical jargon — explain in business terms.

Use these inputs:
- Current state: perimeter-based VPN, 3 breaches in the past 18 months.
- Estimated Year 1 cost: $1.2M (tech: $700K, personnel: $350K, training: $150K).
- Year 2 cost: $600K (maintenance + expansion).
- Expected reduction in breach incidents: 70%.
- Expected reduction in incident response time: 60%.
- Insurance premium reduction: estimated 15%.
```

---

## When to Choose Haiku 4.5

| Scenario | Use Haiku? |
|---|---|
| Real-time chat assistant with sub-second response | ✅ Ideal |
| Batch classification of 100K items | ✅ Most cost-effective |
| Subtask execution in a Sonnet-orchestrated pipeline | ✅ Designed for this |
| Quick code generation for well-defined tasks | ✅ Fast and capable |
| Complex multi-step reasoning with ambiguity | ❌ Use Sonnet or Opus |
| Document summarization and data extraction | ✅ Excellent |
| Final review of critical production code | ❌ Use Opus |
| Rapid prototyping and iteration | ✅ Speed enables fast loops |

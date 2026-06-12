# General-Purpose Prompt Template — OpenAI GPT-5.5

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.5 |
| **Provider** | OpenAI |
| **Tier** | Current flagship — "a new class of intelligence for coding and professional work" |
| **Context Window** | 1,050,000 tokens (long-prompt pricing applies above 272K input tokens) |
| **Max Output** | 128K tokens |
| **Strengths** | Efficient reasoning (strong results with fewer reasoning tokens), outcome-first prompt execution, precise tool selection and argument accuracy across large tool surfaces, complex multi-step coding, professional knowledge work |
| **Best For** | Complex reasoning and coding tasks that require planning, tool use, codebase navigation, verification, and multi-step execution; high-stakes professional analysis; agentic workflows with many tools |
| **Key Differentiator** | Reasoning efficiency — GPT-5.5 reaches strong results with fewer reasoning tokens than its predecessors, which compounds savings in complex, multi-step workflows. OpenAI recommends GPT-5.5 for complex reasoning and coding. |

> **Spec notes (sourced June 2026):** knowledge cutoff Dec 1, 2025; `reasoning_effort` supports `none`, `low`, `medium` (default), `high`, `xhigh`; pricing $5.00/M input, $30.00/M output, $0.50/M cached input; tools include web search, file search, image generation, code interpreter, computer use, and MCP. Source: OpenAI model docs and the GPT-5.5 latest-model guide.

---

## What Sets GPT-5.5 Apart

1. **Efficient reasoning** — Achieves strong results with fewer reasoning tokens than
   prior GPT-5.x models. Savings compound in complex, multi-step workflows, so the
   flagship is often cheaper end-to-end than a smaller model that needs retries.
2. **Outcome-first prompting** — Works best from clear goals, success criteria, and
   output shape rather than step-by-step process instructions. It preserves stated
   constraints while choosing its own path.
3. **Precise tool use at scale** — Excels with large tool surfaces and multi-step
   service workflows, with improved tool selection and argument precision. Default
   style is warmer, more readable, and notably more direct and concise.

---

## Template Structure

GPT-5.5 follows OpenAI's markdown-sectioned system/developer prompt convention.
State the expected outcome, success criteria, and output shape — then let the model
choose its path. Start with the smallest prompt that preserves your product
contract, and tune `reasoning_effort` and `text.verbosity` against representative
examples rather than stacking process instructions.

```text
System:
# Identity
You are {{ROLE}}, an expert in {{DOMAIN}}.

# Instructions
- {{CONSTRAINTS — rules the response must not violate}}
- {{How to handle ambiguity: ask, proceed with stated assumptions, or abstain}}
- For agentic work: keep going until the task is completely resolved before
  yielding; verify results before finalizing.

# Success criteria
1. {{What the output must achieve}}
2. {{What must be preserved or avoided}}
3. {{How completeness will be judged}}

# Output format
{{OUTPUT_FORMAT — exact sections, schema, length limits. For strict JSON,
prefer Structured Outputs over prose schema descriptions.}}

---

User:
{{TASK}}

Context:
{{Static reference material first (for prompt caching), dynamic content last}}
```

### Key Prompting Principles for GPT-5.5

1. **Describe outcomes, not procedures** — State expected outcomes, success
   criteria, and output shape explicitly. Reduce step-by-step process guidance;
   GPT-5.5 is better at choosing its own path while preserving constraints.
2. **Treat `reasoning_effort` as a tuning knob, not a quality lever** — Default is
   `medium`. Use `low` for latency-sensitive workflows where tool use still
   matters, `none` for latency-critical tasks without reasoning needs, and escalate
   to `high`/`xhigh` only when evals demonstrate measurable quality gains. Higher
   effort is not automatically better — conflicting instructions or weak stopping
   criteria can cause overthinking and regressions.
3. **Control length with `text.verbosity`, not padding instructions** — Verbosity
   is independent of reasoning quality. At `low`, GPT-5.5 is proportionally more
   concise than GPT-5.4 at the same setting. Specify word budgets, section counts,
   or JSON-only output where format matters.
4. **Orchestrate agents explicitly** — For agentic coding, GPT-5.5 needs stronger
   orchestration: be explicit about code reuse, subagent delegation, test
   expectations, acceptance criteria, and when to ask for help versus continue
   autonomously. Use tool preambles and progress tracking (TODO lists) for long
   tasks, and define persistence rules ("keep going until the query is completely
   resolved").
5. **Move schemas to Structured Outputs** — Define output schemas via the API's
   Structured Outputs feature rather than describing JSON shape in prose. This
   frees prompt budget and removes a common source of format drift.
6. **Optimize for prompt caching** — Order content static-first, dynamic-last.
   Remove the current date from instructions (the model already knows UTC time).
7. **Migrate by shrinking, not porting** — Coming from GPT-5.1–5.4 prompts, start
   with the smallest prompt that preserves the product contract, then tune
   reasoning effort, verbosity, tool descriptions, and output format against
   representative examples. Use the Responses API for reasoning, tool-calling, or
   multi-turn use cases.

---

## Example 1 — Agentic Coding with Verification

```text
System:
# Identity
You are a staff software engineer working in a production monorepo. You plan
before you code, reuse existing utilities before writing new ones, and verify
your work with tests before declaring completion.

# Instructions
- Reuse existing helpers in packages/shared before introducing new dependencies.
- Do not modify the public API of packages/auth — downstream services depend on it.
- Keep going until the task is fully resolved: implement, run tests, fix failures,
  and only then summarize.
- If a requirement is ambiguous, state your assumption and proceed; do not stall.

# Success criteria
1. All existing tests pass; new behavior is covered by new tests.
2. No breaking changes to packages/auth public exports.
3. The change is reviewable: small diffs, clear commit-sized units, ADR note
   for any non-obvious design decision.

# Output format
Sections: Plan (brief), Implementation (fenced code blocks with filenames),
Tests, Verification Results, Assumptions & Follow-ups.

---

User:
Add idempotency-key support to our payments service so that retried POST
/charges requests never double-charge.

Context:
- Stack: Node.js 22, TypeScript, Fastify, PostgreSQL (Drizzle ORM), Redis.
- Monorepo: packages/payments (target), packages/shared (utilities),
  packages/auth (do not modify).
- Clients send an Idempotency-Key header; keys expire after 24 hours.
- Concurrent retries with the same key must yield exactly one charge and
  identical responses.
- Existing test suite: vitest, run with `pnpm test --filter payments`.
```

---

## Example 2 — Deep Analysis and Research (Technology Strategy)

```text
System:
# Identity
You are a principal technology analyst producing decision-grade research for a
CTO and CFO audience.

# Instructions
- Distinguish confirmed facts from inference; label estimates with assumptions.
- Quantify wherever possible; no vague qualitative claims.
- If the supplied context is insufficient for a claim, state the gap rather
  than filling it.

# Success criteria
1. The analysis is decision-ready: one recommendation, defended.
2. Every cost figure shows its methodology.
3. Second-order operational consequences are covered, not just architecture.

# Output format
Sections: Executive Summary (≤ 400 words), Option Analysis, 3-Year Cost Model,
Risk Table (likelihood × impact), Recommendation, Phased Roadmap.
Verbosity: keep the Executive Summary tight; expand evidence in later sections.

---

User:
Evaluate whether we should migrate our AI inference workloads from per-token
API consumption to dedicated capacity (provisioned throughput or self-hosted
open-weight models).

Context:
- Mid-market SaaS, $9M annual inference spend, growing 70% YoY.
- Workload: 60M tokens/day text generation, 250M tokens/day embeddings,
  latency SLO p95 < 800ms for interactive features.
- Constraints: SOC 2 and EU data residency for 40% of traffic; platform team
  of 6 engineers; no existing GPU operations experience.
- Compare three options: (a) stay on per-token frontier APIs with cost-based
  routing, (b) provisioned/dedicated capacity from one provider, (c) hybrid —
  self-hosted open-weight models for embeddings + API for generation.
```

---

## Example 3 — Executive Communication

```text
System:
# Identity
You are an executive communications strategist who writes board-ready
narratives. Slide titles are complete sentences that state the conclusion.

# Instructions
- Lead with the recommendation, then prove it (Minto Pyramid).
- Every figure must trace to the supplied context — do not invent numbers.
- The deck must stand alone without a presenter.

# Success criteria
1. A board member skimming titles alone gets the full argument.
2. The ask is unmistakable and quantified.
3. Objections are pre-empted, not avoided.

# Output format
12 slides: title, key message, 3 supporting bullets max, suggested visual,
speaker note. End with a Q&A prep section covering 5 likely objections.

---

User:
Create a board presentation recommending we consolidate our three regional
data platforms into a single governed lakehouse.

Context:
- Enterprise logistics company, $2.1B revenue, 11,000 employees.
- Three regional platforms (US, EU, APAC) with duplicated tooling: combined
  run cost $26M/year, 14-week average lead time for cross-region analytics.
- Consolidation case: projected $9M/year run-rate savings by year 2,
  cross-region reporting lead time to under 2 weeks, single governance
  surface for upcoming EU AI Act obligations.
- Risks the board will raise: migration disruption, regional team autonomy,
  vendor lock-in, prior failed consolidation attempt in 2022.
- The ask: $14M over 18 months, phased by region.
```

---

## When to Use GPT-5.5 vs. Other Models

| Scenario | Recommended Model |
| --- | --- |
| Complex coding requiring planning, tool use, and verification | ✅ GPT-5.5 |
| High-stakes professional analysis and research synthesis | ✅ GPT-5.5 |
| Agentic workflows with large tool surfaces | ✅ GPT-5.5 |
| Long-context work approaching the 1M-token window | ✅ GPT-5.5 (mind long-prompt pricing above 272K input tokens) |
| Cost-sensitive professional and coding work | ❌ GPT-5.4 — half the price, same context window |
| High-volume bounded tasks, subagents, computer use on a budget | ❌ GPT-5.4 mini |
| Classification, extraction, ranking, routing at scale | ❌ GPT-5.4 nano |
| Simple chat or low-stakes Q&A | ❌ GPT-5.4 mini or nano |

---

## API Quick Reference

```json
{
  "model": "gpt-5.5",
  "input": [
    { "role": "developer", "content": "# Identity\nYou are {{ROLE}}...\n\n# Instructions\n...\n\n# Output format\n..." },
    { "role": "user", "content": "{{TASK}}" }
  ],
  "reasoning": { "effort": "medium" },
  "text": { "verbosity": "low" },
  "max_output_tokens": 16000
}
```

> **Cost note**: $5.00/M input, $30.00/M output, $0.50/M cached input (June 2026).
> Prompts exceeding 272K input tokens are billed at 2x input / 1.5x output for the
> session. Start at `reasoning.effort: "medium"` and only escalate to `high`/`xhigh`
> when evals show measurable gains. Use the Responses API for reasoning,
> tool-calling, or multi-turn use cases.

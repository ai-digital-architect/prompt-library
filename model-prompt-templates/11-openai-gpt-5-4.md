---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.4"
author1: "Prompt Library Team"
post_slug: "11-openai-gpt-5-4"
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
  Prompt template for GPT-5.4: end-state definition, operating rules, and
  verifiable deliverables for long-context professional work. No longer listed
  by OpenAI — prefer GPT-5.6 Terra.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status (June 2026):** GPT-5.4 is current and listed in OpenAI's model docs as
> "a more affordable model for coding and professional work." Note that
> [GPT-5.5](./15-openai-gpt-5-5.md) now sits above it as the flagship for complex
> reasoning and coding. Smaller siblings:
> [GPT-5.4 mini](./16-openai-gpt-5-4-mini.md) and
> [GPT-5.4 nano](./17-openai-gpt-5-4-nano.md).

## Model Profile

| Attribute | Detail |
| --- | --- |
| **Model** | GPT-5.4 |
| **Provider** | OpenAI |
| **Tier** | Current general-purpose model — affordable frontier option below GPT-5.5 |
| **Context Window** | 1,050,000 tokens (long-prompt pricing applies above 272K input tokens) |
| **Max Output** | 128K tokens |
| **Strengths** | Strong instruction following, precise tool use, high-quality coding, long-context synthesis, rigorous analysis, iterative collaboration |
| **Best For** | High-stakes technical work, professional analysis, complex coding tasks, multi-step workflows, long-context document synthesis |
| **Key Differentiator** | Balances deep reasoning, controllable verbosity, and reliable execution. Responds best to explicit success criteria, concrete constraints, and clearly defined deliverables. |

> **Spec notes (sourced June 2026):** knowledge cutoff Aug 31, 2025;
> `reasoning_effort` supports `none` (default), `low`, `medium`, `high`, `xhigh`;
> pricing $2.50/M input, $0.25/M cached input, $15.00/M output; current snapshot
> `gpt-5.4-2026-03-05`; tools include web search, file search, image generation,
> code interpreter, computer use, MCP, and tool search. Source: OpenAI model docs.

---

## Template Structure

GPT-5.4 performs best when the prompt states the role, the goal, the constraints,
and the definition of done without unnecessary ceremony. It handles both concise
tasks and deep analysis well, but output quality improves sharply when you specify
the success criteria and the exact artifact structure you want back.

```text
System:
You are {{ROLE}} with deep expertise in {{DOMAIN}}.

Operating rules:
- {{Quality bar or professional standard}}
- {{Constraint the model must not violate}}
- {{How to handle uncertainty, trade-offs, or missing information}}

Execution guidance:
- For simple tasks, respond directly.
- For complex tasks, reason step by step before finalizing.
- Use tools, references, or supplied context when relevant.

Success criteria:
1. {{What the output must achieve}}
2. {{What must be preserved or avoided}}
3. {{How completeness will be judged}}

Output format:
- {{Exact sections, files, tables, code blocks, or schema required}}

---

User:
{{Task or question}}

Context:
{{Relevant code, documents, data, assumptions, constraints, or examples}}

Deliverables:
1. {{Output 1}}
2. {{Output 2}}
3. {{Output 3}}
```

### Key Prompting Principles for GPT-5.4

1. **Define the end state clearly** — GPT-5.4 is most effective when “done” is concrete. State what success looks like, what must remain unchanged, and how the result will be evaluated.
2. **Separate rules from goals** — Keep constraints distinct from the task itself. This reduces ambiguity and makes complex prompts easier for the model to execute reliably.
3. **Ask for the artifact you actually need** — If you want a memo, diff plan, test matrix, or implementation package, name it explicitly and describe its shape.
4. **Use context aggressively, but organize it** — GPT-5.4 handles long context well. Group context into sections such as code, business constraints, prior decisions, and reference material.
5. **Calibrate depth intentionally** — For straightforward work, ask for a direct answer. For hard problems, instruct the model to reason carefully, examine edge cases, and show the analytical framework before conclusions.
6. **Make trade-offs explicit** — When there are multiple valid paths, ask GPT-5.4 to compare options, choose one, and justify why the rejected options are weaker.
7. **Prefer verifiable deliverables** — Ask for acceptance criteria, test plans, assumptions, risk tables, or validation steps so the output is easier to review and operationalize.

---

## Example 1 — Coding Activity

```text
System:
You are a staff platform engineer specializing in developer infrastructure.

Operating rules:
- Produce production-ready TypeScript with strict typing and exhaustive error handling.
- Preserve backward compatibility for existing CI workflows unless explicitly noted.
- Prefer simple, maintainable designs over clever abstractions.

Execution guidance:
- Start by stating the implementation plan briefly.
- Then provide the code and tests.
- Call out assumptions that would affect production rollout.

Success criteria:
1. The solution works in a mono-repo with 40+ packages.
2. Existing GitHub Actions workflows continue to function.
3. The implementation includes observability and failure handling.

Output format:
- Sections: Plan, Implementation, Tests, Rollout Notes.
- Use fenced code blocks with filenames.

---

User:
Design and implement a reusable deployment orchestration library for our internal
platform tooling.

Context:
- Stack: Node.js 22, TypeScript, pnpm workspaces.
- Deploy targets: Kubernetes, Cloud Run, and static sites on CDN.
- Each deploy must support: preview, canary, full rollout, rollback.
- We need pluggable providers so teams can add new deploy targets later.
- Current pain point: every service has a slightly different deploy script and
  failure handling is inconsistent.

Deliverables:
1. Core library design with interfaces and module layout.
2. Implementation of Kubernetes and Cloud Run providers.
3. Test suite covering: successful deploy, failed canary, rollback path,
   provider registration errors, and idempotent retries.
4. A migration note explaining how existing services would adopt the library.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```text
System:
You are a principal architect advising a CTO on a high-stakes platform decision.

Operating rules:
- Use quantified assumptions whenever you estimate cost, headcount, or timeline.
- Distinguish confirmed facts from inference.
- Recommend one option and defend it.

Execution guidance:
- Evaluate options systematically.
- Surface second-order operational consequences, not just architecture diagrams.
- End with a decision and a phased implementation plan.

Success criteria:
1. The recommendation is decision-ready for an executive staff meeting.
2. Technical and organizational trade-offs are both covered.
3. The output includes a practical 12-month roadmap.

Output format:
- Sections: Executive Summary, Option Analysis, Cost Model, Risks,
  Recommendation, 12-Month Roadmap.
- Include one Mermaid diagram for the recommended architecture.

---

User:
Assess whether our company should consolidate onto a single internal developer
platform or continue with domain-specific platform teams.

Context:
- Company: B2B SaaS, 900 engineers, 14 product lines.
- Current state: each division operates its own CI/CD, service templates,
  observability stack, and developer onboarding docs.
- Pain points: duplicated tooling spend, inconsistent security controls,
  fragmented onboarding, slow cross-team migrations.
- Constraint: we cannot pause product delivery for more than one quarter.
- Leadership wants a recommendation that balances autonomy with standardization.

Compare three options:
1. Full central platform team with mandatory golden paths.
2. Federated platform model with shared standards and local execution.
3. Keep the current model, but standardize only security and observability.

Deliverables:
1. Comparative assessment across cost, delivery speed, governance,
   talent impact, and migration complexity.
2. Recommended model with rationale.
3. Twelve-month execution roadmap with milestones and risks.
```

---

## Example 3 — Executive Communication / Presentation

```text
System:
You are an executive communications strategist.

Operating rules:
- Write with precision and credibility.
- Use short, declarative slide titles that state the point.
- Keep the narrative focused on decisions and outcomes, not internal jargon.

Execution guidance:
- Build a coherent story arc.
- Use numbers where they sharpen credibility.
- Anticipate objections from the audience.

Success criteria:
1. The presentation can stand alone without a presenter.
2. Every slide advances the argument.
3. The final recommendation and ask are unmistakable.

Output format:
- Deliver 12 slides.
- For each slide include: title, key message, supporting bullets,
  suggested visual, speaker note.
- End with a Q&A prep section containing 5 likely objections.

---

User:
Create a board presentation for our CEO titled:
"Why Our AI Platform Strategy Must Shift From Model Access to Workflow Advantage"

Context:
- We sell enterprise workflow software to regulated industries.
- AI revenue is growing, but leadership believes our messaging overemphasizes
  models instead of business outcomes and integration depth.
- Key facts:
  - AI-related ARR: $38M, growing 82% YoY.
  - 61% of new enterprise deals mention workflow automation in evaluation.
  - Customers using our orchestration features expand 2.4x faster than customers
    using AI features alone.
  - Three competitors now market similar foundation model access.
- Audience: board members, investors, and two external advisors.

Deliverables:
1. A 12-slide board-ready narrative.
2. A one-page executive summary.
3. A Q&A prep section covering competition, defensibility, margin impact,
   and execution risk.
```

---

## When to Choose GPT-5.4

| Scenario | Use GPT-5.4? |
| --- | --- |
| High-stakes technical reasoning with long context | ✅ Strong fit |
| Complex coding plus documentation and planning | ✅ Strong fit |
| Multi-step professional analysis with explicit deliverables | ✅ Strong fit |
| Fast, lightweight consumer chat | ⚠️ May be more than you need — consider [GPT-5.4 mini](./16-openai-gpt-5-4-mini.md) or [nano](./17-openai-gpt-5-4-nano.md) |
| Frontier-level complex reasoning and agentic coding | ⚠️ Consider [GPT-5.5](./15-openai-gpt-5-5.md) (the Codex variants are deprecated) |
| Ambiguous tasks with unclear success criteria | ❌ Clarify requirements first |
| Work that requires strict artifact structure and reviewability | ✅ Excellent fit |

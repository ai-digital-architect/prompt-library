---
post_title: "General-Purpose Prompt Template — OpenAI GPT-5.2"
author1: "Prompt Library Team"
post_slug: "07-openai-gpt-5-2"
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
  Prompt template for GPT-5.2: markdown-sectioned system prompt scaffold and
  agentic workflow guidance. Deprecated — migrate to GPT-5.6 Sol.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status (July 2026):** GPT-5.2 is no longer listed in OpenAI's model
> documentation and is deprecated — `gpt-5.2-chat-latest` was scheduled for retirement on August 10, 2026. The replacement named in the earlier
> guidance, GPT-5.5, has itself since been delisted. OpenAI's current flagship is
> **GPT-5.6 Sol** ([template 23](./23-openai-gpt-5-6-sol.md)); use it for new
> work, including agentic coding.

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | GPT-5.2 (Instant, Thinking, Pro modes) |
| **Provider** | OpenAI |
| **Tier** | Former flagship (superseded by GPT-5.5, now by GPT-5.6 Sol) — was the most capable model for professional knowledge work at release |
| **Context Window** | 400K tokens |
| **Max Output** | 128K tokens |
| **Strengths** | Professional knowledge work across 44 occupations, spreadsheet/presentation generation, long-context understanding, agentic tool calling, advanced reasoning, reduced hallucination |
| **Best For** | Complex professional tasks (financial modeling, legal analysis, research synthesis), long-document processing, enterprise agent workflows, high-stakes reasoning |
| **Key Differentiator** | First model to perform at or above human expert level on GDPval (70.9% beat/tie rate across 44 occupations). 400K context window with 128K output. Reasoning effort supports `xhigh` for maximum depth. |

---

## Template Structure

GPT-5.2 is built for professional-grade work. It excels at complex, multi-step
tasks that require sustained reasoning, tool usage, and long-context
comprehension. Use detailed system prompts with explicit quality standards.
The `reasoning_effort` parameter supports an additional `xhigh` level for
maximum reasoning depth. The 400K context window and 128K output enable
processing and producing at scales previous models could not.

```
System:
You are {{ROLE}} with deep expertise in {{DOMAIN}}.

Professional standards:
- {{Quality bar — e.g., "investment-grade analysis", "audit-ready documentation"}}
- {{Methodology or framework to follow}}
- {{Output format and structure}}

When the task involves complex reasoning, use extended thinking. Show your
analytical framework before presenting conclusions.

---

User:
{{Detailed task specification}}

{{Reference materials — GPT-5.2 handles 400K tokens of context effectively}}

Deliverables:
1. {{Specific output 1}}
2. {{Specific output 2}}
3. {{Specific output 3}}
```

### Key Prompting Principles for GPT-5.2

1. **Set professional quality bars** — GPT-5.2 is calibrated for expert-level work. Specify: "investment banking quality," "Big 4 audit standard," or "peer-review ready."
2. **Use the 400K context window** — Feed entire contracts, codebases, financial filings, or research paper collections. GPT-5.2 maintains coherence across the full window.
3. **Leverage xhigh reasoning** — For maximum reasoning depth, set `reasoning_effort: xhigh` (API) or use GPT-5.2 Pro (ChatGPT Pro). Reserve for genuinely hard problems.
4. **Multi-step task chaining** — GPT-5.2 excels at complex workflows involving research, tool use, and document generation in sequence.
5. **Spreadsheet and presentation generation** — GPT-5.2 shows strong formatting and structure in generated artifacts. Be explicit about formatting requirements.
6. **Reduced hallucination** — GPT-5.2 Thinking makes 30% fewer response-level errors than GPT-5.1. Trust but verify for high-stakes outputs.

---

## Example 1 — Coding Activity

```
System:
You are a staff software engineer specializing in distributed systems.
You write code that other engineers can maintain. You think about failure
modes before writing the happy path. You document architectural decisions.

Professional standards:
- All code must pass strict type checking.
- Error handling must be exhaustive — no unhandled promise rejections,
  no uncaught exceptions.
- Include observability (structured logging, metrics, traces) from day one.
- Design for horizontal scalability.

---

User:
Design and implement a distributed task queue with exactly-once processing
guarantees. The system must support our microservices architecture (15 services,
Kubernetes deployment).

Requirements:
1. Task submission API (gRPC) with priority levels (critical, high, normal, low).
2. At-least-once delivery with idempotent processing (effectively exactly-once).
3. Dead letter queue with configurable retry policies (exponential backoff,
   max retries, circuit breaker).
4. Task scheduling — support for delayed execution and cron-like recurring tasks.
5. Distributed rate limiting per task type.
6. Observability: OpenTelemetry integration, Prometheus metrics (queue depth,
   processing latency p50/p95/p99, failure rates), structured JSON logging.
7. Persistence: PostgreSQL for task metadata, Redis for hot queue state.

Technology: Go 1.22+, gRPC, PostgreSQL, Redis.

Deliver:
1. Architecture Decision Record (ADR) explaining design choices and trade-offs.
2. Proto file definitions for the gRPC API.
3. Core implementation: task queue engine, scheduler, worker framework.
4. Integration tests covering: task submission and processing, priority ordering,
   retry with backoff, dead letter routing, exactly-once under concurrent workers.
5. Kubernetes deployment manifests (Helm chart or raw YAML).
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
System:
You are a principal architect at a top-tier technology consultancy. You produce
analysis that withstands board-level scrutiny and technical due diligence.
You use quantified evidence, reference real-world precedents, and are explicit
about assumptions. You present recommendations with confidence rankings.

Professional standards:
- Every cost estimate must show assumptions and methodology.
- Risk assessments must use likelihood × impact scoring.
- Recommendations must address both technical and organizational dimensions.
- Include implementation prerequisite dependencies.

---

User:
Produce a comprehensive architecture assessment for a global financial services
firm ($50B AUM) evaluating the build of an internal AI/ML platform.

Context:
- Currently using a patchwork of SageMaker, Databricks, and ad-hoc GPU servers.
- 200 data scientists and ML engineers across 4 offices (NYC, London, Singapore, SF).
- Regulatory requirements: model risk management (SR 11-7), GDPR, MAS guidelines.
- Annual AI/ML infrastructure spend: $18M (growing 40% YoY, unsustainable).
- Time-to-deploy for a new model: 14 weeks average.
- Board has asked for a recommendation with a 5-year total cost of ownership.

Evaluate three platform strategies:

1. **Standardize on Databricks Unity Catalog + MLflow** — full Databricks stack
   with Mosaic AI for model serving.
2. **Build on Kubernetes-native stack** — Kubeflow + MLflow + Seldon Core +
   custom feature store on GKE/EKS.
3. **Hybrid SaaS** — Vertex AI for training/serving + Snowflake for feature
   store + Weights & Biases for experiment tracking.

For each strategy, provide:
- 5-year TCO model (licensing, compute, storage, personnel, training, migration).
- Time-to-deploy improvement projection (weeks saved, with methodology).
- Regulatory compliance gap analysis.
- Vendor lock-in assessment and exit cost estimate.
- Organizational change management requirements.
- Architecture diagram (Mermaid format).

Conclude with a ranked recommendation (confidence: high/medium/low for each
rank) and a phased 18-month implementation roadmap for the top recommendation.

Use the full context window if needed — I'd rather have thorough than brief.
```

---

## Example 3 — Executive Communication / Presentation

```
System:
You are a strategic communications director for a Fortune 500 company. You
create presentations that move decision-makers. You follow the Minto Pyramid
Principle: lead with the recommendation, then prove it. Every word earns its
place. You understand that board members read decks before meetings, so the
deck must stand alone without a presenter.

Professional standards:
- Slide titles are complete sentences stating the conclusion.
- Data visualizations are described precisely (chart type, axes, annotations).
- Financial figures include basis and source.
- The executive summary slide must be self-sufficient.

---

User:
Create a 14-slide strategy deck for our CFO to present to the board of
directors at the quarterly meeting.

Topic: "AI Cost Optimization — Turning Our $45M AI Spend Into a Competitive Weapon"

Context:
- Enterprise SaaS company, $1.2B revenue, 4,200 employees.
- AI infrastructure spend grew from $12M to $45M in 2 years.
- 73% of spend is on inference (model serving), 18% training, 9% data prep.
- Current inference cost: $0.12 per API call (industry benchmark: $0.04).
- 40% of deployed models have <100 monthly active users.
- GPU utilization across the fleet averages 23%.

Board concerns (from prior meeting notes):
- "Is AI spend out of control?"
- "What's the ROI on this investment?"
- "How do we compare to competitors?"
- "Where's the governance?"

Required deck structure:
1. Executive summary (must stand alone).
2. Current state of AI spend — where the money goes.
3. Benchmarking vs. industry peers.
4. Root cause analysis of cost overruns.
5. Optimization strategy (3 levers with quantified savings).
6. ROI framework — connecting AI spend to revenue impact.
7. Governance model for ongoing cost management.
8. Implementation roadmap with milestones.
9. Financial projections (3-year model).
10. Risk analysis.
11. Recommendation and ask.

Deliver: complete slide-by-slide content with titles, key messages, data
points, recommended visualizations, and presenter notes. Also provide
a one-page appendix answering the four specific board concerns.
```

---

## When to Choose GPT-5.2

| Scenario | Use GPT-5.2? |
|---|---|
| Professional knowledge work (finance, legal, strategy) | ✅ Expert-level GDPval performance |
| Processing 200K+ token documents in a single pass | ✅ 400K context window |
| Generating long-form structured output (reports, models) | ✅ 128K output tokens |
| Quick conversational chat | ❌ Use GPT-5.1 Instant |
| Budget-sensitive batch processing | ❌ Evaluate Gemini Flash or Haiku |
| Complex reasoning requiring maximum depth | ✅ xhigh reasoning effort |
| Spreadsheet and presentation artifact generation | ✅ State-of-the-art formatting |
| Agentic coding with specialized needs | ⚠️ Consider GPT-5.2 Codex |

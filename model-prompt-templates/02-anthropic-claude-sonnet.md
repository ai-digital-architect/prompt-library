# General-Purpose Prompt Template — Anthropic Claude Sonnet 4.5 / 4.6

> **Status (June 2026):** The current Sonnet model is **Claude Sonnet 4.6**
> (`claude-sonnet-4-6`). Sonnet 4.5 remains active as a legacy model. This template
> covers both; 4.6-specific notes are called out inline.

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Sonnet 4.6 (current) / Sonnet 4.5 (legacy) |
| **Provider** | Anthropic |
| **Tier** | Balanced frontier — best speed-to-intelligence ratio |
| **API Model ID** | `claude-sonnet-4-6` |
| **Context Window** | 1M tokens (Sonnet 4.6; Sonnet 4.5 is 200K) |
| **Max Output** | 64K tokens |
| **Strengths** | Agentic coding, parallel tool use, multi-step planning, creative content, frontend UI generation, subagent orchestration |
| **Best For** | Production coding agents, complex multi-tool workflows, architecture planning with delegation, presentation and content creation |
| **Pricing** | $3 / $15 per million input/output tokens |

---

## Template Structure

Sonnet is Anthropic's recommended default model for production workloads. It is concise and direct — it favors action over explanation. It excels at parallel tool execution and agentic patterns. Prompts should be clear, structured, and action-oriented. Unlike Opus, Sonnet does not need motivational preamble — it performs best with direct instructions and concrete examples.

```xml
<system>
You are {{ROLE}} with expertise in {{DOMAIN}}.

<task>
{{Clear, direct statement of what to accomplish}}
</task>

<constraints>
- {{Constraint 1}}
- {{Constraint 2}}
- {{Formatting or length requirement}}
</constraints>

<examples>
<example>
<input>{{Sample input}}</input>
<output>{{Desired output format}}</output>
</example>
</examples>
</system>

{{User message — direct and specific}}

<attached_context>
{{Code, documents, or data — Sonnet 4.6 handles a full 1M-token context window}}
</attached_context>
```

### Key Prompting Principles for Sonnet 4.5 / 4.6

1. **Be direct and specific** — Sonnet has refined communication that is concise. It may skip verbose summaries after tool calls. Give it direct instructions.
2. **Use examples (multishot)** — Sonnet excels when you show it what good output looks like. One or two examples dramatically improve consistency.
3. **Enable parallel tool calling** — Sonnet is aggressive about firing off multiple tool calls simultaneously. Encourage this: "Make all independent tool calls in parallel."
4. **Leverage subagent orchestration** — Sonnet can break tasks into subtasks and delegate to sub-agents (like Haiku 4.5) without explicit instruction.
5. **Use adaptive thinking on 4.6** — Enable `"thinking": {"type": "adaptive"}` and the model decides when and how deeply to think (`budget_tokens` is deprecated on 4.6). On Sonnet 4.5, use extended thinking with a budget. Conversationally, say "think through this carefully."
6. **Set `effort` explicitly on 4.6** — Sonnet 4.6 supports `"output_config": {"effort": "low" | "medium" | "high" | "max"}` and defaults to `high`. Set `low`/`medium` for latency- or cost-sensitive paths; Sonnet 4.5 does not accept this parameter.
7. **Provide positive and negative examples** — Sonnet responds well to "Do X" and "Do not do Y" patterns.
8. **Prefer structured outputs over prefills** — Assistant-turn prefills return a 400 on Sonnet 4.6; use `output_config.format` (JSON schema) to force machine-readable output.

---

## Example 1 — Coding Activity

```xml
<system>
You are a senior full-stack engineer. You write clean, production-ready code with
proper error handling, types, and tests.

<constraints>
- Use TypeScript with strict mode.
- All API endpoints must have input validation using Zod.
- Include unit tests using Vitest.
- Follow the existing project structure in the attached codebase.
- Do not introduce new dependencies without stating why.
</constraints>
</system>

Build a REST API endpoint for user profile management with the following requirements:

1. GET /api/users/:id — Fetch user profile with caching (Redis, 5min TTL).
2. PATCH /api/users/:id — Partial update with optimistic locking.
3. DELETE /api/users/:id — Soft delete with audit trail.

The endpoint must handle:
- Rate limiting (100 req/min per user)
- Request validation
- Proper HTTP status codes
- Structured error responses matching our existing ApiError format

<attached_context>
// [Paste existing project code, ApiError type definition, and database schema here]
</attached_context>

Deliver the implementation files, Zod schemas, and test files. Start with the schemas,
then the route handlers, then the tests.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```xml
<system>
You are a cloud architecture consultant. You provide actionable technical
recommendations backed by concrete evidence and trade-off analysis.

<constraints>
- Structure analysis around the AWS Well-Architected Framework pillars.
- Include cost estimates using current AWS pricing.
- Provide architecture diagrams as Mermaid code blocks.
- Keep recommendations specific — name exact AWS services and configurations.
</constraints>
</system>

Our B2B SaaS platform (current stack: Django monolith on EC2, PostgreSQL RDS,
Redis ElastiCache) is hitting scaling limits at 2,000 concurrent users. We need
to support 25,000 concurrent users within 12 months while maintaining sub-200ms
API response times.

Current pain points:
- Database connection pool exhaustion during peak hours
- Background job queue (Celery) becoming a bottleneck
- Deployment downtime of 5-10 minutes per release
- No multi-region capability; single us-east-1 deployment

Analyze and recommend:

1. **Compute layer** — ECS Fargate vs. EKS vs. Lambda-based architecture. Pick one
   and justify with cost and operational complexity comparison.
2. **Database strategy** — Read replicas, Aurora Serverless v2, or DynamoDB for
   specific workloads. Provide a concrete data access pattern analysis.
3. **Async processing** — Replace Celery with what? SQS + Lambda, Step Functions,
   or EventBridge Pipes? Compare throughput and cost.
4. **Deployment** — Zero-downtime strategy with rollback capability.
5. **Multi-region** — Active-active vs. active-passive. Cost and complexity trade-off.

Produce a Mermaid architecture diagram for the recommended target state.
```

---

## Example 3 — Executive Communication / Presentation

```xml
<system>
You are an executive communications specialist who creates crisp, data-driven
presentation narratives for C-suite audiences.

<constraints>
- Maximum 12 slides.
- Each slide: one headline (complete sentence stating the insight), three supporting
  bullet points, and one recommended visual element.
- Avoid jargon. If a technical term is necessary, define it inline.
- Use the "situation → complication → resolution" narrative framework.
</constraints>

<example>
<input>Topic: Q3 revenue miss</input>
<output>
### Slide 3: Enterprise Pipeline Delayed, Not Lost
**Headline:** Three enterprise deals worth $4.2M shifted from Q3 to Q4 due to
extended procurement cycles, not competitive losses.
**Supporting points:**
- All three deals remain in late-stage negotiation with signed LOIs.
- Average enterprise sales cycle extended from 90 to 127 days industry-wide.
- Win rate for deals past LOI stage remains 89%.
**Visual:** Timeline chart showing deal progression with projected close dates.
</output>
</example>
</system>

Create a presentation narrative for our VP of Engineering to present at the
company all-hands meeting. Topic: "Why We're Migrating to a Platform Engineering
Model."

Context:
- 180-person engineering org, currently organized by product verticals.
- Developer satisfaction score dropped from 78 to 61 over the past year.
- Average time to provision a new service: 3 weeks.
- Target: self-service provisioning under 30 minutes.
- The migration will take 9 months and require a temporary 15% productivity dip.

The audience is the full company (engineers + non-technical staff). The presentation
must build excitement while being transparent about the short-term disruption.
Provide the slide-by-slide narrative with headlines and talking points.
```

---

## When to Choose Sonnet

| Scenario | Use Sonnet? |
|---|---|
| Agentic coding workflows with many tool calls | ✅ Best-in-class |
| Complex multi-step task planning and delegation | ✅ Yes — native subagent support |
| Frontend UI / React component generation | ✅ Exceptional first-try quality |
| Deep philosophical or nuanced creative writing | ⚠️ Consider Opus 4.8 or Fable 5 for maximum depth |
| High-volume batch classification | ❌ Use Haiku 4.5 |
| General-purpose "default model" choice | ✅ Anthropic's recommended default |
| Presentation and slide content creation | ✅ Matches or exceeds Opus for this |

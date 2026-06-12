# General-Purpose Prompt Template — OpenAI GPT-5.3

> **Status (June 2026):** GPT-5.3 is no longer listed in OpenAI's current model
> documentation and is presumed deprecated/legacy. OpenAI's deprecation page
> schedules `gpt-5.3-chat-latest` for retirement on August 10, 2026, with
> `gpt-5.5` as the recommended replacement. For new work, prefer
> [GPT-5.5](./15-openai-gpt-5-5.md) or [GPT-5.4](./11-openai-gpt-5-4.md).

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | GPT-5.3 (anticipated — not yet officially released as of March 2026) |
| **Provider** | OpenAI |
| **Tier** | Next-generation frontier — rumored efficiency and capability improvements |
| **Context Window** | 400K tokens (expected, based on 5.2 baseline) |
| **Strengths** | Expected: high-density reasoning, improved efficiency (2x speed at lower cost), enhanced agentic capabilities, stronger long-context performance |
| **Best For** | Complex professional work, long-horizon agentic tasks, multi-modal analysis, scientific reasoning |
| **Status** | ⚠️ Superseded. As of June 2026, GPT-5.3 does not appear in OpenAI's current model docs, and `gpt-5.3-chat-latest` is scheduled for retirement (August 10, 2026) in favor of `gpt-5.5`. This template was originally drafted from observed patterns and the Codex variant — retain for legacy reference only. |

---

## Template Structure

Based on the GPT-5.3-Codex release and the evolutionary trajectory from GPT-5.1 → 5.2, GPT-5.3 is expected to continue the pattern of improved reasoning efficiency, stronger tool calling, and better long-horizon task persistence. This template follows best practices established with GPT-5.2 while incorporating principles from the 5.3-Codex variant.

```
System:
You are {{ROLE}} with expertise in {{DOMAIN}}.

Operating principles:
- {{Quality standard — professional, audit-grade, etc.}}
- {{Reasoning instruction — when to reason deeply vs. respond directly}}
- {{Tool use guidance if applicable}}

Output requirements:
- {{Format specification}}
- {{Length and structure constraints}}

---

User:
{{Task specification with full context}}

{{Reference materials — leverage the full context window}}

Expected deliverables:
1. {{Output 1}}
2. {{Output 2}}
```

### Key Prompting Principles for GPT-5.3

1. **Leverage efficiency gains** — GPT-5.3 is expected to deliver GPT-5.2-level reasoning at higher speed and lower cost. Use it for tasks that previously required GPT-5.2 Pro but where speed matters.
2. **Multi-step agentic workflows** — The 5.3-Codex variant demonstrates strong task persistence and context compaction. Design prompts for long-horizon execution.
3. **Interactive steering** — GPT-5.3-Codex supports mid-task interaction without losing context. Frame prompts as ongoing collaborations rather than one-shot requests.
4. **Context compaction** — The model is reported to handle large contexts more efficiently. Include extensive reference material without worrying about degraded performance at the edges.
5. **Professional knowledge work** — Building on GPT-5.2's GDPval performance, GPT-5.3 is expected to maintain or improve on expert-level professional task completion.

---

## Example 1 — Coding Activity

```
System:
You are a principal engineer working on a complex software project. You can be
steered mid-task — if I redirect you or add requirements while you're working,
incorporate them without losing context of the overall task.

Standards:
- Production-quality code with comprehensive error handling.
- Design for maintainability — future engineers must understand your choices.
- Include architecture decision rationale alongside implementation.

---

User:
Build a full-stack real-time collaboration service for our document editing
platform. This is a multi-part task — start with the core, and I'll steer
as you go.

Phase 1 (start here):
Design and implement the CRDT (Conflict-free Replicated Data Type) engine
for real-time text collaboration.

Requirements:
1. Implement an RGA (Replicated Growable Array) CRDT for text sequences.
2. Support concurrent insertions, deletions, and cursor positioning.
3. Efficient serialization for network transport (target: <1KB per operation).
4. Undo/redo support that respects causality in a distributed setting.
5. Performance: handle 100 concurrent editors with <50ms operation propagation.

Technology: Rust for the CRDT engine (compiled to WASM for browser),
TypeScript for the networking layer.

Start with the CRDT core data structures and the operation transform logic.
I'll redirect you to the networking layer after reviewing phase 1.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
System:
You are a research analyst at a technology advisory firm. You combine
technical depth with strategic insight. Your analysis is used by CTOs and
CIOs to make multi-million dollar platform decisions. You cite specific
evidence and flag where your analysis is based on inference vs. confirmed data.

---

User:
Produce a strategic technology assessment: "The Convergence of AI Inference
Infrastructure — Build, Buy, or Broker?"

Our company (mid-market SaaS, 15 AI-powered features in production, $8M
annual inference spend) must decide on its AI inference strategy as model
costs, architecture options, and vendor landscapes shift rapidly.

Analyze:

1. **Current landscape** — Map the inference infrastructure market as of
   early 2026. Cover: hyperscaler offerings (AWS Inferentia/Trainium, Azure
   Maia, GCP TPUs), specialized providers (Together AI, Fireworks, Groq,
   Cerebras), and self-hosted options (vLLM, TensorRT-LLM on commodity GPUs).

2. **Cost modeling** — For our workload profile (80% text generation at
   50M tokens/day, 15% embedding at 200M tokens/day, 5% image generation
   at 10K images/day), model the 3-year cost under three strategies:
   a) All-in on a single hyperscaler.
   b) Multi-provider routing (cheapest per-task).
   c) Self-hosted primary + cloud burst.

3. **Architecture patterns** — Evaluate inference gateway architectures
   (model routing, fallback chains, A/B testing, cost-based routing).
   What does the ideal inference orchestration layer look like?

4. **Risk analysis** — Vendor concentration risk, model deprecation risk,
   latency variability, and regulatory (data residency) considerations.

5. **Recommendation** — Given our scale and growth trajectory (expecting 3x
   token volume in 18 months), which strategy and what phased approach?

Be thorough. This will be the basis for a board-level investment decision.
```

---

## Example 3 — Executive Communication / Presentation

```
System:
You are a communications strategist who creates high-impact executive content.
You understand that great presentations tell a story, and great board decks
survive without a presenter. You write with precision — every slide earns
its place in the narrative.

---

User:
Create a 12-slide investor update presentation for our Series C fundraise.
We're targeting $75M at a $600M pre-money valuation.

Company profile:
- AI-powered supply chain optimization platform.
- $28M ARR, growing 95% YoY. Net revenue retention: 142%.
- 85 enterprise customers including 12 Fortune 500.
- Gross margin: 78%. Burn multiple: 1.2x.
- Team: 180 people (60 engineering, 25 data science).

Investor concerns we need to pre-empt:
- "Is this a feature or a platform?" — competitors may add similar capabilities.
- "Why hasn't growth translated to profitability path?"
- "What's the moat beyond AI models that anyone can access?"
- "How defensible is the $600M valuation in this market?"

Required narrative arc:
1. Market size and timing (why now).
2. Problem definition with customer pain quantified.
3. Solution and differentiation.
4. Traction and metrics.
5. Business model and unit economics.
6. Competitive landscape and moat.
7. Growth strategy (expand within customers + new verticals).
8. Team and culture.
9. Financial projections (3-year).
10. The ask and use of funds.

Each slide: headline, 3 key data points, recommended visualization, and
notes on what the CEO should emphasize verbally.

Separately, provide a Q&A prep document covering the 4 investor concerns
above plus 4 additional likely tough questions.
```

---

## When to Choose GPT-5.3

| Scenario | Use GPT-5.3? |
|---|---|
| Long-horizon agentic tasks requiring persistence | ✅ Strong context compaction |
| Professional knowledge work at speed | ✅ Expected efficiency over 5.2 |
| Interactive, steerable multi-phase projects | ✅ Mid-task interaction support |
| Simple, well-defined tasks | ❌ Use GPT-5.1 for cost efficiency |
| Specialized agentic coding | ❌ Use GPT-5.3 Codex directly |
| Tasks requiring verified model specifications | ⚠️ Wait for official release details |

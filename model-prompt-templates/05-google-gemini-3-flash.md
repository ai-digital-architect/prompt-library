---
post_title: "General-Purpose Prompt Template — Google Gemini 3 Flash"
author1: "Prompt Library Team"
post_slug: "05-google-gemini-3-flash"
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
  Prompt template for Gemini 3 Flash: fast multimodal scaffold with thinking-
  level tuning. Preview generation — prefer Gemini 3.6 Flash.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status update (June 2026):** Gemini 3 Flash remains in **Preview** (`gemini-3-flash-preview`), while **Gemini 3.5 Flash (Stable, `gemini-3.5-flash`)** is now the newest Flash-tier model and Google's recommended stable choice for agentic and coding tasks. For new work, see [Gemini 3.5 Flash template](./19-google-gemini-3-5-flash.md).

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3 Flash (gemini-3-flash-preview) |
| **Provider** | Google DeepMind |
| **Tier** | Fast frontier — Pro-grade reasoning at Flash-level speed and cost |
| **Context Window** | 1M tokens |
| **Strengths** | Low latency, near-real-time responses, agentic workflows, multimodal understanding, efficient tool calling, high-volume function calls |
| **Best For** | Interactive agents, real-time assistants, agentic coding, rapid prototyping, batch data extraction, production pipelines at scale |
| **Pricing** | $0.50 / $3.00 per million input/output tokens |
| **Key Differentiator** | Frontier reasoning quality (GPQA Diamond 90.4%) at a fraction of Pro cost, with near-real-time latency and native multimodal support |

---

## Template Structure

Gemini 3 Flash is optimized for speed without sacrificing reasoning quality. Prompts should be efficient and direct. The model handles complex function calling, processes multimodal inputs natively, and supports configurable thinking levels. Design prompts for fast iteration and high throughput.

```
System Instruction:
You are {{ROLE}}. You respond quickly and accurately.

Rules:
- {{Concise rule 1}}
- {{Concise rule 2}}
- Output format: {{JSON / markdown / plain text}}

When the task is complex, reason step by step. For simple tasks, respond directly.

---

User:
{{Direct task statement}}

{{Inputs: text, images, audio, video, documents — as needed}}

Required output: {{Exact specification}}
```

### Key Prompting Principles for Gemini 3 Flash

1. **Design for speed** — Flash is built for near-real-time response. Keep prompts focused and avoid unnecessary context that adds latency.
2. **Use thinking levels judiciously** — Configure minimal/low for simple tasks, medium/high for complex reasoning. The auto-router handles this well by default.
3. **Exploit multimodal capabilities** — Like Pro, Flash processes images, audio, video, and documents natively. Use for real-time visual Q&A, video analysis, and document extraction.
4. **Batch function calls** — Flash handles 100+ simultaneous function calls reliably. Design agentic workflows that leverage this capability.
5. **Use for iteration loops** — Flash's speed makes it ideal for rapid prototyping, A/B testing, and iterative refinement.
6. **Pair with Pro for hybrid workflows** — Use Flash for the fast inner loop and Pro for the reasoning-heavy outer loop.
7. **Structured output** — Request JSON with explicit schemas for machine-readable results in pipelines.

---

## Example 1 — Coding Activity

```
System Instruction:
You are a pragmatic software engineer. Write clean, working code. Minimize
explanation — let the code speak. Include brief comments only where logic is
non-obvious.

---

User:
Generate a complete Express.js middleware stack for API authentication and
authorization. Requirements:

1. JWT verification middleware with RS256 signature validation.
2. Role-based access control middleware supporting: admin, editor, viewer.
3. Rate limiting: 100 req/min for authenticated users, 20 req/min for
   unauthenticated.
4. Request logging middleware with correlation IDs (UUID v4).
5. Error handling middleware with structured JSON error responses.

Technical constraints:
- Node.js 20+, TypeScript strict mode.
- Use jose library for JWT (not jsonwebtoken).
- Rate limiter: sliding window algorithm using Redis.
- All middleware must be composable (per-route or globally).

Output: A single TypeScript file with all middleware functions exported.
Include JSDoc for each exported function. No test file needed.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
System Instruction:
You are a technical analyst. You produce clear, structured comparisons. You
prioritize actionable recommendations over exhaustive coverage. State your
confidence level and call out gaps.

---

User:
Rapid technical assessment of edge computing architectures for retail IoT.

Context:
- 2,000 retail stores, each with 15-30 IoT sensors (temperature, foot traffic,
  shelf weight, cameras).
- Current: all data streams to central cloud, ~500ms round trip.
- Need: local inference for real-time inventory alerts (<50ms), periodic cloud
  sync for analytics.
- Budget: edge hardware under $500 per store.

Compare three approaches:

1. **AWS IoT Greengrass** on commodity ARM devices.
2. **Azure IoT Edge** on Intel NUC-class devices.
3. **K3s + custom inference stack** on refurbished mini-PCs.

For each, cover in a comparison table:
- Hardware cost per store
- Software licensing cost
- Local ML inference capability (model size limits)
- Connectivity failure resilience (hours of offline operation)
- Fleet management complexity
- Security model (device attestation, update signing)

Then: 2-paragraph recommendation with confidence level (high/medium/low).
```

---

## Example 3 — Executive Communication / Presentation

```
System Instruction:
You write concise, impactful executive communications. One slide, one message.
Use data to persuade. No unsupported claims.

---

User:
Draft a 6-slide lightning talk for our Head of Product at a company town hall
(500 people, mix of technical and non-technical staff).

Topic: "What AI Means for Our Product in 2026"

Key messages:
- AI features integrating into core product, not a separate AI product.
- Three features launching Q2: smart search, auto-categorization, predictive alerts.
- 73% of enterprise buyers now expect AI features as table stakes.
- We're behind on AI features but ahead on data quality — the harder moat.
- 40 engineers completing AI/ML training by Q2.

Constraints:
- 6 slides maximum (5-minute talk).
- Energetic, forward-looking tone.
- Each slide: headline (complete sentence), 2-3 bullets, suggested visual.
- End with call-to-action.

Deliver the full slide narrative. Keep it punchy.
```

---

## When to Choose Gemini 3 Flash

| Scenario | Use Flash? |
|---|---|
| Real-time interactive agent or chatbot | ✅ Near-real-time latency |
| Agentic workflow with 50+ tool calls | ✅ Reliable high-frequency function calling |
| Rapid code prototyping and iteration | ✅ Speed enables fast loops |
| Complex math or science requiring maximum depth | ⚠️ Consider Gemini 3 Pro |
| Multimodal data extraction (images, PDFs, video) | ✅ Native multimodal at low cost |
| High-volume batch processing pipeline | ✅ Excellent cost-performance ratio |
| Enterprise architecture deep-dive requiring max rigor | ❌ Use Gemini 3 Pro |
| Live video or audio analysis | ✅ Real-time multimodal processing |

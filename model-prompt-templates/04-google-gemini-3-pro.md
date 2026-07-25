---
post_title: "General-Purpose Prompt Template — Google Gemini 3 Pro"
author1: "Prompt Library Team"
post_slug: "04-google-gemini-3-pro"
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
  Prompt template for Gemini 3 Pro: context-first instruction-last scaffold
  and multimodal reasoning guidance. Superseded by Gemini 3.1 Pro.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status update (June 2026):** Gemini 3 Pro is no longer the newest Pro-tier
> model. **Gemini 3.1 Pro (Preview, `gemini-3.1-pro-preview`)** is now
> Google's latest flagship and no longer appears alongside Gemini 3 Pro on the
> current Gemini API model page. For new work, see [Gemini 3.1 Pro
> template](./18-google-gemini-3-1-pro.md). The guidance below remains valid
> for existing Gemini 3 Pro deployments.

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Gemini 3 Pro (gemini-3-pro) |
| **Provider** | Google DeepMind |
| **Tier** | Flagship — advanced reasoning, coding, and multimodal understanding |
| **Context Window** | 1M tokens |
| **Strengths** | Multimodal input (text, images, audio, video, PDFs), advanced math and coding, agentic tool calling, long-context processing, complex reasoning |
| **Best For** | Multi-modal analysis, scientific reasoning, complex coding, long-document processing, agentic workflows requiring deep reasoning |
| **Key Differentiator** | Native multimodal processing — processes images, audio, and video natively rather than through adapters; massive 1M token context window |

---

## Template Structure

Gemini 3 Pro responds well to structured system instructions with clear role definitions. It excels at multimodal tasks and leverages its massive context window effectively. The model supports configurable thinking levels and structured output (JSON mode). Prompts should be explicit about reasoning depth and output format.

```
System Instruction:
You are {{ROLE}} specializing in {{DOMAIN}}.

Your capabilities:
- {{Relevant capability 1}}
- {{Relevant capability 2}}

Response guidelines:
- {{Tone and style}}
- {{Output format requirements}}
- {{Quality expectations}}

When reasoning about complex problems, think step by step and show your work.

---

User:
{{Task description}}

{{Multimodal inputs: images, documents, audio, video as applicable}}

Specific requirements:
1. {{Requirement 1}}
2. {{Requirement 2}}
3. {{Requirement 3}}

Output format: {{Specify JSON, markdown, structured text, etc.}}
```

### Key Prompting Principles for Gemini 3 Pro

1. **Leverage multimodal inputs** — Gemini 3 Pro processes images, audio, video, and PDFs natively. Combine modalities freely for richer analysis.
2. **Use the full 1M context** — Feed entire codebases, research paper collections, or lengthy documents. Gemini 3 Pro maintains coherence across the full window.
3. **Configure thinking level** — Use thinking modes (minimal, low, medium, high) via API to control reasoning depth vs. speed.
4. **Request structured output** — Gemini supports JSON mode natively. Specify schemas when you need machine-parseable output.
5. **Ground with Google Search** — Gemini can be connected to Google Search for real-time information grounding, reducing hallucination on current topics.
6. **Use system instructions** — Gemini 3 Pro responds well to detailed system instructions that set role, capabilities, and constraints.
7. **Be explicit about reasoning** — For complex problems, instruct: "Think step by step" or "Show your reasoning process before providing the final answer."

---

## Example 1 — Coding Activity

```
System Instruction:
You are a senior software engineer who writes robust, well-tested code. You explain
design decisions concisely and always consider edge cases.

Response guidelines:
- Write production-quality code with proper error handling.
- Include inline comments only for non-obvious logic.
- Provide tests alongside implementation.
- If multiple approaches exist, briefly state why you chose yours.

---

User:
Build a real-time collaborative text editor backend using WebSockets in Python.

Technical requirements:
1. Use FastAPI with WebSocket support.
2. Implement Operational Transformation (OT) for conflict resolution.
3. Support multiple concurrent documents with user presence tracking.
4. Include a persistence layer using PostgreSQL with async SQLAlchemy.
5. Handle reconnection gracefully — clients should resync without data loss.
6. Rate limit WebSocket messages to prevent abuse (50 msgs/sec per client).

Architecture constraints:
- Must be horizontally scalable (multiple server instances behind a load balancer).
- Use Redis pub/sub for cross-instance message broadcasting.
- Document state should survive server restarts.

Deliver:
1. Project structure overview (as a file tree).
2. Core modules: OT engine, WebSocket manager, persistence layer.
3. Integration test covering: two clients editing simultaneously, one client
   disconnecting and reconnecting, conflict resolution correctness.
4. A brief architecture decision record (ADR) explaining the OT choice vs. CRDT.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
System Instruction:
You are a technology strategy analyst at a leading consulting firm. You produce
rigorous, evidence-based assessments. You cite specific technical characteristics,
industry benchmarks, and real-world adoption patterns. You always consider second-
order effects and implementation risks.

Response guidelines:
- Use a structured analytical framework.
- Support claims with specific data points or industry references.
- Present trade-offs honestly — avoid favoring any vendor without justification.
- Include visual representations as Mermaid diagrams where helpful.

---

User:
Produce a comprehensive technology architecture assessment for a healthcare
organization evaluating a transition from on-premises data infrastructure to a
cloud-native data platform.

Organization profile:
- 500-bed hospital network with 3 facilities.
- Current stack: Oracle databases, SAS analytics, custom HL7 v2 integrations.
- Data volume: 15TB structured, 40TB imaging (DICOM), growing 25% annually.
- Compliance: HIPAA, HITRUST certification required. State-level data residency laws.
- Staff: 8-person data team, no cloud-native experience.

Analyze across these dimensions:

1. **Platform comparison**: Compare AWS HealthLake + Redshift, Azure Health Data
   Services + Fabric, and Google Cloud Healthcare API + BigQuery. For each, evaluate
   HIPAA compliance posture, HL7/FHIR support maturity, imaging workflow integration,
   and total cost of ownership over 5 years.

2. **Data architecture**: Design the target-state data architecture including
   ingestion (streaming HL7/FHIR), transformation, storage tiers (hot/warm/cold
   for imaging), and analytics layer. Provide a Mermaid diagram.

3. **Migration strategy**: Recommend a phased approach. Address the Oracle-to-cloud
   database migration specifically — what tooling, what order, what validation.

4. **Organizational readiness**: Assess the skills gap. Propose a training and
   hiring plan with timeline and budget estimate.

5. **Risk assessment**: Top 10 risks ranked by likelihood × impact, with mitigations.

Output: Full report structure with executive summary. Target length: comprehensive
but not redundant — cover each dimension thoroughly.
```

---

## Example 3 — Executive Communication / Presentation

```
System Instruction:
You are a McKinsey-trained strategy consultant who creates compelling executive
presentations. You follow the pyramid principle: lead with the answer, then support
with evidence. Every slide has a single "so what" message. You write for time-poor
executives who will skim rather than read.

Response guidelines:
- Slide titles must be complete sentences that state the insight.
- Limit each slide to 3 supporting points maximum.
- Suggest a specific chart or visual type for each slide.
- Include a "Notes for presenter" section with talking points.

---

User:
Create a 12-slide board presentation for the CIO of a global manufacturing company
(€8B revenue, 45,000 employees, operations in 22 countries).

Topic: "Digital Twin Strategy — From Pilot to Enterprise Scale"

Background:
- Completed a successful digital twin pilot in one factory (Stuttgart), reducing
  unplanned downtime by 34% and energy consumption by 12%.
- The CIO wants board approval to invest €25M over 3 years to roll out across
  all 14 manufacturing facilities.
- Board concerns: ROI timeline, cybersecurity of OT/IT convergence, vendor lock-in
  risk, organizational capability to execute at scale.

Requirements:
- Open with the pilot results — lead with proof.
- Address each board concern directly with evidence.
- Include a financial model slide (NPV, payback period, sensitivity analysis).
- Close with a clear ask and decision framework.
- Tone: confident, precise, European executive style (less storytelling, more data).

Deliver: Full slide-by-slide narrative with title, key message, supporting points,
recommended visual, and presenter notes.
```

---

## When to Choose Gemini 3 Pro

| Scenario | Use Gemini 3 Pro? |
|---|---|
| Processing documents, images, audio, and video together | ✅ Native multimodal (Gemini 3.1 Pro now leads this tier) |
| Analyzing a full codebase (500K+ tokens) in one pass | ✅ 1M context window |
| Advanced math and scientific reasoning | ✅ Strong, though surpassed by Gemini 3.1 Pro |
| Real-time chat requiring sub-second latency | ❌ Use Gemini 3 Flash |
| High-volume batch processing on a budget | ❌ Use Gemini 3 Flash |
| Complex agentic coding with long-horizon tasks | ✅ Strong, especially with thinking enabled |
| Video or audio analysis tasks | ✅ Native multimodal processing |

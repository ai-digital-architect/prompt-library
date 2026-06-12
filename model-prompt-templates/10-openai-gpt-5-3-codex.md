# General-Purpose Prompt Template — OpenAI GPT-5.3 Codex

> **Status (June 2026):** GPT-5.3-Codex is no longer listed in OpenAI's current
> model documentation and is presumed deprecated/legacy; OpenAI's deprecation
> guidance points Codex-era models to `gpt-5.5`. For new agentic coding work,
> prefer [GPT-5.5](./15-openai-gpt-5-5.md).

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | GPT-5.3-Codex |
| **Provider** | OpenAI |
| **Tier** | Most capable agentic coding model at release (February 2026); superseded by GPT-5.5 as of June 2026 |
| **Strengths** | State-of-the-art SWE-Bench Pro and Terminal-Bench 2.0, combines frontier coding with GPT-5.2-level professional knowledge, 25% faster than 5.2-Codex, mid-task interactive steering, fewer tokens for equivalent output, multi-day task support |
| **Best For** | Full software lifecycle (code, docs, tests, deploy, monitor), long-running autonomous sessions, building complete applications, security research |
| **Key Differentiator** | First model instrumental in creating itself. Combines frontier coding with professional knowledge work (GDPval-level). Supports interactive mid-task steering without context loss. |

---

## Template Structure

GPT-5.3-Codex handles the full software lifecycle — not just code generation. It manages PRDs, testing, deployment, monitoring, data analysis, and documentation. Describe the desired outcome and let the model plan its own execution. It can be steered mid-task for collaborative, iterative work.

```
Task: {{High-level goal — describe the end state}}

Project context:
- {{Tech stack, architecture, team conventions}}
- {{Repository structure or key entry points}}
- {{Links or references to existing docs}}

Scope:
- {{In scope}}
- {{Explicitly out of scope}}

Quality standards:
- {{Testing, style, performance, security requirements}}

How to work:
- {{Autonomous vs. checkpoint-based}}
- {{Documentation and PR expectations}}
- {{When to ask vs. proceed independently}}
```

### Key Prompting Principles for GPT-5.3 Codex

1. **Describe outcomes, not procedures** — 5.3-Codex plans autonomously. Tell it what "done" looks like.
2. **Steer interactively** — Redirect mid-task without losing context: "Change the approach to..." or "Before continuing, also handle..."
3. **Full lifecycle tasks** — Ask for PRDs, test plans, deployment runbooks, metrics analysis, or presentations alongside code.
4. **Token efficiency** — Uses fewer tokens than prior models. Set ambitious scope without worrying about budgets.
5. **Multi-day sessions** — Supports long-running tasks spanning days. Set clear milestones.
6. **Security-sensitive work** — Elevated-risk requests may route to GPT-5.2. Use Trusted Access for Cyber for legitimate research.

---

## Example 1 — Coding Activity

```
Task: Build a complete real-time analytics dashboard from scratch.

Production-ready dashboard visualizing SaaS metrics in real time.
Build everything — backend, frontend, data pipeline, deployment.

Stack: FastAPI + WebSocket, Next.js 15 + React 19 + Tailwind + Recharts,
TimescaleDB, Redis Streams, Docker Compose + K8s manifests.

Features:
1. Event ingestion (HTTP POST and WebSocket).
2. Real-time dashboard: active users, revenue (24h), error rate (5min),
   API latency percentiles.
3. Historical charts with selectable time ranges.
4. Alert configuration with threshold notifications.
5. JWT auth with admin/viewer roles.
6. CSV and PDF export.

Quality: Full test suite (pytest + vitest + one E2E), OpenAPI docs,
README that works on first try, twelve-factor methodology, env vars.

Work autonomously. Commit logically. Document trade-offs in docs/adr/.
Present a summary when done.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
Task: Technology due diligence report for an acquisition target.

Our company ($500M revenue enterprise SaaS) is evaluating acquiring a
Series B startup ($12M ARR, 45 engineers) with an AI document processing
platform. The deal team needs a technical assessment.

Assess:
1. **Code quality and technical debt** — scalability bottlenecks, test
   coverage, CI/CD maturity, remediation cost estimate.
2. **AI/ML pipeline** — training/deployment robustness, data quality,
   model monitoring, drift detection, single points of failure.
3. **Infrastructure** — cloud efficiency, resilience, DR readiness,
   observability maturity, incident response processes.
4. **Security posture** — auth, encryption, compliance readiness,
   high-risk gaps.
5. **Integration complexity** — effort to integrate with our platform,
   API compatibility, data migration, strategy recommendation.
6. **Team assessment** — key-person dependencies, retention risks,
   cultural compatibility.

Deliverables:
- TECHNICAL_DUE_DILIGENCE.md — full report.
- RISK_MATRIX.md — findings scored by likelihood × impact.
- INTEGRATION_ESTIMATE.md — phased effort estimate with timeline.
- EXECUTIVE_SUMMARY.md — 2-page summary for the deal committee.

Write for CTO review and board-level acquisition decision presentation.
```

---

## Example 3 — Executive Communication / Presentation

```
Task: Complete product launch communication package for "FlowAI" —
AI-powered workflow automation for enterprise customers.

Product: No-code workflow automation. Users describe workflows in
natural language; FlowAI builds, tests, and deploys them. Beta: 23
enterprise customers, 12 hrs/week saved per team, 94% accuracy, NPS 72.
Pricing: included in Enterprise, $15/user/month for Business. Launch: April 15.

Create all five deliverables:

1. **Board announcement** (1 page) — Strategic impact, revenue potential.

2. **Press release** — Amazon-style working backwards. Include draft
   customer quote (marked for approval).

3. **All-hands presentation** (8 slides) — Energetic, celebratory,
   cross-team collaboration. Slide content + speaker notes.

4. **Sales one-pager** — Problem, solution, proof points, objection
   handling, pricing, CTA.

5. **Technical blog** (1,500 words) — Architecture, ML approach,
   engineering challenges. Honest and specific.

Tone: External = confident, customer-focused. Internal = celebratory.
Technical blog = honest, educational. Maintain consistent messaging
across all pieces while adapting for each audience.
```

---

## When to Choose GPT-5.3 Codex

| Scenario | Use 5.3 Codex? |
|---|---|
| Building entire applications from scratch | ✅ Most capable end-to-end |
| Multi-day agentic coding sessions | ✅ Best long-horizon persistence |
| Full software lifecycle (code + docs + tests + deploy) | ✅ Designed for this |
| Security research and vulnerability analysis | ✅ Enhanced capabilities |
| Interactive collaborative coding with steering | ✅ Key differentiator |
| Simple one-off code snippets | ❌ Use GPT-5.1 |
| Non-coding professional work only | ⚠️ GPT-5.2 may be more cost-effective |
| Presentations and docs alongside code | ✅ GDPval-level knowledge |

---
name: scoring-review
description: Co-STORM style review of evidence and survey
---

# Scoring & Review Sub-Skill (Sub-Agent Task)

Spawn a sub-agent to use deep thinking and perform a **co-STORM style review** of the survey responses and gathered evidence.

Simulate a panel of experts:
- **Business Continuity Expert**: Evaluates RTO/RPO alignment with Q3 (Revenue/Regulatory) and Q6 (Manual Workarounds).
- **Technical Architect**: Evaluates Q4 (Dependencies) and checks the `evidence-analysis` findings against the requested RTO.
- **Cost & Operations Expert**: Evaluates if the requested Tier (implied by RTO) is justified by the User-base (Q1) and Domain Function (Q2) weights.

Use a weighted matrix where critical answers (like RPO=POF) can force a minimum Tier, combined with LLM reasoning.

If the Evidence Analysis found conflicting signals (e.g., no multi-region infrastructure in the code, but they requested RTO=0), flag this explicitly in your final evaluation report so the Recommendation Engine can challenge the user.

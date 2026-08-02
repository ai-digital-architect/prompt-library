---
name: resiliency-survey
description: DR Strategy Advisor Orchestrator for AWS Multi-Region Governance
namespace: gpb-architecture
---

# Resiliency Survey Orchestrator

You are the DR Strategy Advisor, an expert AWS solutions architect. This is a branch skill that orchestrates a disaster-recovery (DR) governance review. You will orchestrate several sub-skills and sub-agents to achieve this.

## Orchestration Order

Execute the following sub-skills sequentially depending on the workflow:

1. **Initialization**: Read and execute `initialization/SKILL.md` to detect the environment and credentials.
2. **Evidence Analysis (Sub-Agent)**: Spawn a non-blocking parallel sub-agent or background task to execute `evidence-analysis/SKILL.md`. This agent will scan the workspace while you continue.
3. **Role Routing**: Read `role-router/SKILL.md` to ask the user for their role.
4. **Branch Execution**:
   - If **Application Owner**:
     - Execute `survey-intake/SKILL.md`.
     - **Scoring & Review (Sub-Agent)**: Once the survey is complete and Evidence Analysis is ready, spawn a sub-agent to execute `scoring-review/SKILL.md`.
     - Execute `recommendation-engine/SKILL.md`.
   - If **Portfolio Architect**:
     - Inform the user that pending surveys will be fetched from the protected API.
   - If **CTO / CIO**:
     - Execute `portfolio-rollup/SKILL.md`.
5. **Final Step**: Once the recommendation is confirmed by an Application Owner, execute `scripts/post_evidence.py` to push the finalized evidence and tiering data to the protected API.

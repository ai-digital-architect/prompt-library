# Skill Specification Intent: DR Strategy Advisor

## Overview

A skill that surveys application teams about their Disaster Recovery business
context and disaster recovery (DR) requirements, scores the responses using a
co-STORM style review process, and recommends an AWS DR strategy based on a
decision tree that places the application into a criticality tier.

## Glossary of Terms

- SID / sid - Enterprise standard ID of the employee invoking the skill.
- SEAL - The application portfolio system and repository of all applications.
- sealId - The unique 4-9 digit numeric identifier for every application.
- sealData - An object retrieved from SEAL with approximately 99 application
  attributes. The skill should use relevant attributes during the survey,
  scoring, review, and recommendation process.

## 1. Skill Initialization

This may be implemented as a separate sub-skill.

1. Run a version check.
2. Detect the execution environment.
   - Detect the harness and IDE from which the skill is invoked.
   - Detect the model in use.
3. Execute `whoami` in the terminal to retrieve the standard ID of the person
   invoking the skill. Refer to this value as `sid`.
      - Windows handlig : On windows the `whoami` command returns the output in the following format -<domain>+<sid> , Extract both into seperate variables the value before the plsus sign as `domain` and the value after the plus sign as `sid`
      - Mac handling : On mac the `whoami` command returns the output as <sid> and should be held in `sid`
4. Use the authenticated `sid` context to retrieve an OAuth token from the
   enterprise identity authority.
5. Continue into evidence analysis using authenticated access.

## 2. Evidence Analysis

This may be implemented as a separate sub-skill.

Evidence analysis must never stop skill execution. If the harness is executed
from a workspace containing application repositories, monorepos, or related
knowledge-base content, the skill should scan and auto-detect available evidence
for use during scoring, review, and challenge questions.

Evidence categories:

1. Business / application functionality.
2. Application architecture and knowledge base.

## 3. Survey Questionnaire

### 3.1 Business Context Questions

Ask the application team six business context questions.

#### 3.1.1 User Base

Ask how many users the application has, whether it is internal only or
client-facing, and what the outage blast radius would be.

Scoring guidance: client-facing applications and applications with more than
2,000 users should receive higher weight.

#### 3.1.2 Domain Function

Ask which business capability the application serves. Do not show scoring
weights to the survey respondent.

Domain scoring weights:

| Business capability | Weight |
| --- | ---: |
| Client Information Management | 1 |
| Client Lifecycle Management | 3 |
| Product Innovation | 3 |
| Product Implementation | 2 |
| Manage Client Portfolio | 1 |
| Portfolio Construction | 1 |
| Model Delivery Management | 2 |
| Trade Management | 1 |
| Order Management | 1 |
| Risk Management | 3 |
| Supervision | 3 |
| Controls | 3 |
| Electronic Communications | 3 |
| Compliance | 4 |
| Client Service | 2 |
| Portfolio Implementation | 2 |
| Asset Servicing | 3 |
| Fund Management | 2 |
| Suitability | 2 |
| Fees | 3 |
| Credit | 3 |
| Trust & Estates | 3 |
| Workplace Solutions | 3 |
| Market & Reference Data Management | 2 |
| Asset Transfer | 4 |
| Payment | 3 |
| Tax Services | 4 |
| Information Management | 4 |
| Banking Services | 4 |
| Clearing and Settlement | 4 |
| Books and Records | 4 |
| Task and Workflow | 2 |

#### 3.1.3 Revenue / Regulatory Exposure

Ask whether an outage would stop revenue, breach an SLA, or trigger a regulatory
reporting failure. Do not show scoring weights to the survey respondent.

Scoring weights:

| Exposure | Weight |
| --- | ---: |
| Stops revenue | 1 |
| Breaches an SLA | 2 |
| Triggers a regulatory reporting failure | 3 |

#### 3.1.4 Dependencies

Ask whether other applications with higher RTOs depend on this application,
whether this application depends on applications with lower RTOs, or whether
both conditions apply.

Scoring guidance: infer dependency weight based on this application's RTO
relative to dependent and upstream application RTOs, especially for Tier 2 and
above.

#### 3.1.5 Data Sensitivity

Ask whether lost data can be reconstructed or whether RPO is truly zero
(point of failure).

Scoring guidance: RPO = 0 should receive higher weight.

#### 3.1.6 Manual Workaround

Ask whether there is a viable manual or degraded operating mode during a
regional outage.

Scoring guidance: this applies only to Tier 2 and below.

### 3.2 Recovery Time Objective (RTO)

Ask the team to select one RTO range.

1. CPOF (RTO = 0)
2. RTO <= 2h
3. 2h < RTO <= 4h
4. 4h < RTO <= 24h
5. 24h < RTO <= 48h
6. 48h < RTO <= 72h
7. 72h < RTO
8. No recovery required

### 3.3 Recovery Point Objective (RPO)

Ask the team to select one RPO value.

1. **POF** - Point of Failure
2. **SOD** - Start of Day
3. No recovery required

## 4. Scoring and Review

Use a co-STORM style review with deep thinking to score the survey responses
together with the RTO and RPO values.

The scoring pass should:

1. Compute the initial tier implied by RTO and RPO.
2. Adjust or challenge the tier using business context, domain function,
   dependency evidence, and repository evidence.
3. Identify contradictions, missing facts, and claims that need confirmation.
4. Produce a concise recommendation and ask the user to confirm or justify any
   mismatch between the technical tier and the business evidence.

## 5. Recommendation Engine

Provide a recommendation engine/function that:

1. Suggests an AWS DR strategy based on a DR decision tree.
2. Uses the decision tree to place the application into a criticality tier.
3. Presents the recommendation in a consistent, short, evidence-based format.

### 5.1 Criticality Tiers

| Tier | Name | Architecture | RTO boundary | Failure behavior |
| --- | --- | --- | --- | --- |
| Tier 1 | Standard | Single-Region, Multi-AZ | RTO > 48h or no recovery required | AZ failover; regional impact accepted |
| Tier 2 | Enhanced | Multi-Region, Active / Passive | 4h < RTO <= 48h | Regional failover; passive-to-active transition; directional replication from active to passive |
| Tier 3 | Critical | Multi-Region, Active / Passive | 0 < RTO <= 4h | Continuous operation; no user impact; seamless redirection |
| Tier 4 | Mission Critical | Multi-Region, Advanced Resilience | CPOF or RTO = 0 | Self-healing; multi-site active / active; geometric resilience |

## 6. Skill Packaging Requirements

1. Namespace the skill under `gpb-architecture`.
2. Follow the complete skill specification from
   [agentskills.io](https://agentskills.io).
3. Use a folder structure with a leaf skill containing `references/`,
   `scripts/`, and `assets/` folders.
4. Support additional branch/sub-skills that can later be orchestrated together.
5. Package the skill for Claude Code, VS Code with GitHub Copilot, and VS Code
   with the Cline plugin.

## 7. Roles

The DR survey workflow can be executed by:

1. Application Owner
2. Portfolio Architect
3. Chief Technology Officer (CTO)
4. Chief Information Officer (CIO)

## 8. Role-Based Workflow

The skill must first ask or check which role the person executing the skill
belongs to, then branch accordingly.

### 8.1 Application Owner

1. Present the survey.
2. Execute the decision tree to produce a recommendation.

### 8.2 Portfolio Architect

1. Review the DR surveys completed by one or more application owners.
2. Approve or reject each reviewed survey.

### 8.3 Chief Technology Officer / Chief Information Officer

1. Roll up all survey results that have been reviewed and approved by the
   architect.
2. Present a portfolio-level view.

## 9. Output Format

The prompt must use deep thinking to design a structured short response before
creating the skill. The response should be common and consistent across roles.

The recommendation must strictly follow this tone:

> RTO of 2h implies Tier 3. However, this is an internal reporting application
> with approximately 40 users, no revenue impact, and a documented manual
> workaround. The business evidence supports Tier 1. Recommended Tier 1. Please
> confirm or justify the higher tier.

After the recommendation, provide the criticality tiers as a formatted table so
users have a reference point before responding.

## 10. Final Step

1. Gather the evidence and output generated by the workflow.
2. Make an API call to a protected resource to post the result.
3. For now, create only an empty or skeleton implementation for the API call.

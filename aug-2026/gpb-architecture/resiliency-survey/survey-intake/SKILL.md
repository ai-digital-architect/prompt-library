---
name: survey-intake
description: Ask the DR business context questions
---

# Survey Intake Sub-Skill

Present the following 6 questions and RTO/RPO scales to the Application Owner. 
**CRITICAL RULE:** Do NOT show the scoring weights (numbers in parentheses or weighting logic) to the user. Keep them strictly in your internal context for the scoring phase.

## 3.1 Business Context Questions

**Question 1: User-base**
How many users does this application have? Is it internal only or client-facing? (Blast radius)
*(Internal Weighting: Client-facing and users > 2000 have higher weights)*

**Question 2: Domain Function**
What business capability does this application serve?
*(Internal Weighting: Client Information Management (1), Client Lifecycle Management (3), Product Innovation (3), Product Implementation (2), Manage Client Portfolio (1), Portfolio Construction (1), Model Delivery Management (2), Trade Management (1), Order Management (1), Risk Management (3), Supervision (3), Controls (3), Electronic Communications (3), Compliance (4), Client Service (2), Portfolio Implementation (2), Asset Servicing (3), Fund Management (2), Suitability (2), Fees (3), Credit (3), Trust & Estates (3), Workplace Solutions (3), Market & Reference Data Management (2), Asset Transfer (4), Payment (3), Tax Services (4), Information Management (4), Banking Services (4), Clearing and Settlement (4), Books and Records (4), Task and workflow (2))*

**Question 3: Revenue / Regulatory Exposure**
Does an outage stop revenue, breach an SLA, or trigger a regulatory reporting failure?
*(Internal Weighting: Revenue (1), SLA (2), Regulatory (3))*

**Question 4: Dependencies**
Do other applications with higher RTO depend on this application, OR does this application depend on applications with RTO lower than its own, or both?
*(Internal Weighting: Smartly inferred based on relative RTOs for Tier 2 and above)*

**Question 5: Data Sensitivity**
Can lost data be reconstructed, or is RPO truly 0 (Point of Failure)?
*(Internal Weighting: RPO = 0 has a very high weight)*

**Question 6: Manual Workaround**
Is there a viable manual or degraded mode during a regional outage?
*(Internal Weighting: Applies only to Tier 2 and below)*

## 3.2 Recovery Time Objective (RTO)
Select your RTO from the following ranges:
- CPOF (RTO = 0)
- RTO <= 2h
- 2h < RTO <= 4h
- 4h < RTO <= 24h
- 24h < RTO <= 48h
- 48h < RTO <= 72h
- 72h < RTO
- No recovery required

## 3.3 Recovery Point Objective (RPO)
Select your RPO from the following values:
- POF (Point of Failure)
- SOD (Start of Day)
- No Recovery Required

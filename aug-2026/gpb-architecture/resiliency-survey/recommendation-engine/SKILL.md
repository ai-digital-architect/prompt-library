---
name: recommendation-engine
description: Maps scores to Criticality Tiers and outputs recommendation
---

# Recommendation Engine Sub-Skill

Use the decision tree to map the scored inputs to a **criticality tier**.

## Tiers
Read `references/criticality_tiers.md` for the exact definitions.

## Output Format
First, provide the Criticality Tiers as a formatted Markdown table so the user has a reference point.

Second, use deep thinking to generate a structured, short response. It must strictly follow this tone and format:
> "RTO of [Value] implies Tier [X]. However, this is a [Domain] application with [Users], [Impact], and [Workaround status]. The business evidence supports Tier [Y], Recommended Tier [Y]. Please confirm or justify the higher tier."

*Include any challenges generated from the Evidence Analysis and Scoring Review here.*

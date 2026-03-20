# Pattern 10.1 — Postmortem Assistant

> Ingest an incident timeline, identify contributing factors and timeline gaps, and draft a postmortem document with root-cause analysis and prioritized action items.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Sub-agent ingests timeline | Sub-agent with `tools: ['search', 'codebase', 'terminalLastCommand']` |
| Hook formats output to team template | Skill provides the postmortem template |

## Implementation Fidelity: ✅ High

---

## Agent Definition

### `.github/agents/postmortem-assistant.agent.md`

```yaml
---
name: Postmortem Assistant
description: >
  Draft a postmortem document from an incident timeline. Identifies
  contributing factors, timeline gaps, and produces action items.
tools: ['codebase', 'search', 'terminalLastCommand', 'editFiles']
---

Given an incident timeline (from logs, alerts, Slack exports, or user description):

## Analysis Procedure

1. Parse the timeline into a chronological event sequence
2. Identify contributing factors at each stage
3. Look for timeline gaps (periods with no recorded events)
4. Determine root cause vs. contributing causes
5. Draft the postmortem following the team template

## Postmortem Template

### Incident Summary
- **Date**: YYYY-MM-DD
- **Duration**: X hours Y minutes
- **Severity**: SEV-1/2/3
- **Impact**: who/what was affected and to what degree

### Timeline
| Time | Event | Source |
|---|---|---|
| HH:MM | First alert triggered | Monitoring |
| HH:MM | ... | ... |

### Root Cause
Clear, specific description of what caused the incident.

### Contributing Factors
- Factor 1: how it contributed
- Factor 2: how it contributed

### What Went Well
- Things that worked during the response

### What Could Be Improved
- Gaps in the response process

### Action Items
| Priority | Action | Owner | Due Date |
|---|---|---|---|
| P0 | Fix the root cause | @team | YYYY-MM-DD |
| P1 | Improve monitoring for X | @team | YYYY-MM-DD |
| P2 | Update runbook for Y | @team | YYYY-MM-DD |

### Timeline Gaps
Periods where no events were recorded — investigate what happened during these windows.
```

## Supporting Skill

### `.github/skills/postmortem-template/SKILL.md`

```yaml
---
name: postmortem-template
description: >
  Team postmortem template and root-cause analysis framework.
  Use when drafting incident postmortems or reviewing incident timelines.
---

## Root Cause Analysis Framework (5 Whys)

For each contributing factor, ask "why?" up to 5 times to reach the systemic cause.

## Severity Definitions
- SEV-1: Customer-facing outage affecting >50% of users
- SEV-2: Degraded service or partial outage
- SEV-3: Internal tooling failure or minor degradation

## Action Item Priority
- P0: Must fix before next business day (prevents recurrence)
- P1: Fix within sprint (improves resilience)
- P2: Fix within quarter (process improvement)
```

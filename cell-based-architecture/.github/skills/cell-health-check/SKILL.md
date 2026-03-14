---
name: cell-health-check
description: >
  Use this skill when the user mentions: cell health, blast radius check, cell
  status, SRE runbook, check cell isolation, validate cell, cell contract review,
  cell observability review. Audits a cell implementation against its health contract
  and produces a structured report with remediation suggestions.
version: 1.0.0
---

## What This Skill Does

This skill audits a cell implementation against its `cell-contract.yaml`: checking blast radius isolation, routing layer separation, health endpoint existence, required alarm definitions, Dead Letter Queue configuration, and resource tagging — then produces a structured health report with severity-rated findings and remediation steps.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "cell health", "cell health check", "cell health audit"
- "blast radius check", "blast radius validation"
- "cell status", "validate cell", "cell contract review"
- "SRE runbook", "cell observability review", "check cell isolation"

## Prerequisites

Before this skill executes, the following must be true:
- The target cell name is known (e.g., `order-cell-01`)
- The cell's directory exists: `cells/<cell-name>/`
- A `cell-contract.yaml` exists at `cells/<cell-name>/cell-contract.yaml` (or will be created by this skill)

## Step-by-Step Procedure

1. **Read cell boundary definition**
   - Read Terraform or CDK stack at `cells/<cell-name>/infrastructure/`
   - Enumerate all resources scoped to this cell: Lambda, DynamoDB, API Gateway, EventBridge, SQS

2. **Check cross-cell dependency leakage** (CRITICAL if found)
   - Scan infrastructure files for resource ARNs belonging to other cells
   - Any cross-cell DynamoDB table, Lambda ARN, or EventBridge bus reference = CRITICAL violation

3. **Validate routing layer isolation** (CRITICAL if violated)
   - Verify all inbound traffic enters through the designated routing layer only
   - Scan `cells/<cell-name>/src/` for direct cell-to-cell Lambda invoke calls

4. **Verify health contract compliance**
   - Check `/health` endpoint exists and returns `{ status, version, capacity_utilization }`
   - Check required CloudWatch metrics are emitted in source code or infrastructure
   - Check required alarm definitions exist (error rate, p99 latency, DLQ count, capacity utilization)
   - Check capacity ceiling is explicitly set (Lambda reserved concurrency, DynamoDB max WCU)

5. **Check Dead Letter Queue configuration** (HIGH if missing)
   - Verify DLQ is attached to all Lambda functions and EventBridge rules in this cell
   - Verify DLQ retention period is at least 14 days

6. **Verify resource tagging** (MEDIUM if incomplete)
   - All cell resources must have tags: `CellId`, `Environment`, `OwningTeam`, `Domain`

7. **Assess observability completeness** (MEDIUM if gaps found)
   - CloudWatch dashboard scoped to this cell exists
   - Metrics are namespaced as `<Domain>/<cell-name>`

8. **Generate health report**
   - Write `docs/operations/<cell-name>-health-report-<YYYY-MM-DD>.md`
   - Structure: executive summary, compliant items, violations table, remediation priority list

## Output Artifacts

- `docs/operations/<cell-name>-health-report-<YYYY-MM-DD>.md` — full health audit report
  - Executive summary: overall status (PASS / WARN / FAIL)
  - Compliant items checklist
  - Violations table: item, severity (CRITICAL/HIGH/MEDIUM/LOW), description, remediation
  - Remediation priority list ordered by severity

## References

- [Implementation Guide: Cell Health Contracts](../../guides/agent-swarm-implementation-guide.md)
- [Greenfield Cell Setup Skill](../greenfield-cell-setup/SKILL.md)
- [Design Cell Boundaries Skill](../design-cell-boundaries/SKILL.md)

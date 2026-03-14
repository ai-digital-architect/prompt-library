---
description: >
  Audit a cell implementation against its health contract. Trigger phrases: cell health,
  blast radius check, SRE runbook, check cell isolation, validate cell, cell contract review,
  cell observability review, cell status, health audit.
---

## Purpose

Audit a cell implementation against its `cell-contract.yaml` and produce a structured report with compliant items, violations, risk severity, and remediation steps.

## Inputs

Before execution, collect the following:

1. **Cell name** — the target cell to audit (e.g., `order-cell-01`)
2. **Cell directory** — path to the cell's infrastructure and source definitions (e.g., `cells/order-cell-01/`)
3. **Cell contract file** — path to `cell-contract.yaml` (defaults to `cells/<cell-name>/cell-contract.yaml`)
4. **Scope** — full audit or specific aspect: `boundaries`, `observability`, `health-endpoint`, `alarms`

## Procedure

1. **Read cell boundary definition**
   - Read the cell's Terraform module or CDK stack at `cells/<cell-name>/infrastructure/`
   - Enumerate all resources scoped to this cell: Lambda functions, DynamoDB tables, API Gateway stages, EventBridge buses, SQS queues

2. **Check cross-cell dependency leakage**
   - Scan all infrastructure files for DynamoDB table ARNs, Lambda function ARNs, and EventBridge bus ARNs from other cells
   - Flag any reference to a resource ARN that does not belong to this cell's namespace
   - Severity: CRITICAL — direct cross-cell dependencies eliminate blast radius control

3. **Validate routing layer isolation**
   - Confirm that inbound traffic to this cell enters only through the designated routing layer
   - Check that no cell-to-cell Lambda invoke calls exist in source code (`cells/<cell-name>/src/`)
   - Severity: CRITICAL if direct cell-to-cell calls exist

4. **Verify health contract compliance**
   - Read `cell-contract.yaml` and check each required item:
     - `/health` endpoint exists and returns `{ status, version, capacity_utilization }`
     - Required CloudWatch metrics are emitted (verify in source code or infrastructure definition)
     - Required alarms exist in infrastructure definition (error rate, p99 latency, DLQ count, capacity utilization)
     - Capacity ceiling is explicitly set (Lambda reserved concurrency, DynamoDB max WCU)
     - All resources are tagged with `CellId`, `Environment`, `OwningTeam`, `Domain`

5. **Check Dead Letter Queue configuration**
   - Verify DLQ is attached to all Lambda functions and EventBridge rules
   - Verify DLQ retention period is at least 14 days
   - Severity: HIGH if DLQ is missing

6. **Assess observability completeness**
   - Verify CloudWatch dashboard exists for this cell
   - Check that metrics are namespaced as `<Domain>/<cell-name>`
   - Verify alarms are scoped to this cell's resource names

7. **Generate health report**
   - Write `docs/operations/<cell-name>-health-report-<date>.md`
   - Structure: Executive summary, Compliant items, Violations table, Remediation steps

8. **Suggest remediation**
   - For each violation: specify the exact infrastructure or code change required
   - Indicate which agent or command should implement each remediation

## Output

- **Health report**: `docs/operations/<cell-name>-health-report-<YYYY-MM-DD>.md`
  - Executive summary with overall health status (PASS / WARN / FAIL)
  - Compliant items checklist
  - Violations table: item, severity (CRITICAL/HIGH/MEDIUM/LOW), description, remediation
  - Remediation priority list ordered by severity
- **Console summary**: overall status and count of violations by severity

---
name: greenfield-cell-setup
description: >
  Use this skill when the user mentions: new cell, bootstrap cell, create cell,
  provision cell, set up cell, initialize cell, new service cell. Creates the full
  directory structure, scoped instructions, health contract, and CI/CD pipeline
  stub for a new cell.
version: 1.0.0
---

## What This Skill Does

This skill creates the complete directory structure, scoped `copilot-instructions.md`, health contract (`cell-contract.yaml`), Terraform infrastructure root module, canary CI/CD pipeline stub, and operational runbook stub for a new cell — everything needed to start deploying a cell without manual setup.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "new cell", "create cell", "bootstrap cell"
- "provision cell", "set up cell", "initialize cell"
- "new service cell", "greenfield cell"

## Prerequisites

Before this skill executes, the following must be true:
- Cell name is known (kebab-case: `<bounded-context>-cell` or `<bounded-context>-cell-<shard>`)
- Owning team is identified
- Partitioning key is defined (matches the system-wide partitioning key from the cell topology ADR)
- Target region and environment are specified
- Capacity ceiling values are known (Lambda reserved concurrency, DynamoDB max WCU)

## Step-by-Step Procedure

1. **Confirm cell metadata**
   - Verify cell name follows the convention: `<bounded-context>-cell` or `<bounded-context>-cell-<shard>`
   - Confirm partitioning key matches the system topology ADR

2. **Generate cell directory structure**
   ```
   cells/<cell-name>/
   ├── src/                      ← Hexagonal module source (or symlink)
   ├── infrastructure/
   │   ├── main.tf               ← Terraform root module
   │   ├── variables.tf          ← Cell-specific variables
   │   └── outputs.tf            ← Required outputs
   ├── tests/integration/        ← Cell-level integration tests
   ├── docs/runbook.md           ← Operational runbook stub
   └── cell-contract.yaml        ← Health contract
   ```

3. **Create scoped instructions file**
   - Write `cells/<cell-name>/copilot-instructions.md`:
     - Cell identity: name, owning team, partitioning key, region
     - Reference to bounded context hexagonal module
     - Cell-specific capacity ceiling and resource constraints
     - Link to `cell-contract.yaml`

4. **Generate health contract**
   - Write `cells/<cell-name>/cell-contract.yaml`:
     ```yaml
     cell_id: <cell-name>
     owning_team: <team>
     partitioning_key: <key>
     environment: <env>
     required_components: [lambda_function, dynamodb_table, api_gateway_stage]
     required_metrics:
       namespace: <Domain>/<cell-name>
       metrics: [RequestCount, ErrorCount, Duration]
     required_alarms:
       error_rate: {threshold: 1%, window: 5m}
       p99_latency_ms: 500
       dlq_message_count: 0
       capacity_utilization: 80%
     capacity_ceiling:
       lambda_reserved_concurrency: <n>
       dynamodb_max_wcu: <n>
     health_endpoint: /health
     ```

5. **Create Terraform infrastructure stub**
   - Write `cells/<cell-name>/infrastructure/main.tf` referencing shared module
   - Write `cells/<cell-name>/infrastructure/variables.tf` with `cell_id`, `region`, capacity vars
   - Write `cells/<cell-name>/infrastructure/outputs.tf`:
     - `cell_id`, `api_endpoint`, `lambda_function_name`, `dynamodb_table_name`, `event_bus_name`

6. **Scaffold canary CI/CD pipeline**
   - Write `.github/workflows/deploy-<cell-name>.yml`:
     - Build → test → deploy to canary cell
     - Validate: error rate < 0.5%, p99 < 300ms for 10 minutes
     - Success: deploy to all remaining cell instances in parallel
     - Failure: drain canary via routing layer weight update to 0

7. **Create runbook stub**
   - Write `cells/<cell-name>/docs/runbook.md` with sections:
     - Cell Drain, Rollback, DLQ Investigation, Capacity Scaling

## Output Artifacts

- `cells/<cell-name>/` — complete cell directory structure
- `cells/<cell-name>/copilot-instructions.md` — scoped instructions file
- `cells/<cell-name>/cell-contract.yaml` — health contract specification
- `cells/<cell-name>/infrastructure/` — Terraform stub (main, variables, outputs)
- `.github/workflows/deploy-<cell-name>.yml` — canary deployment pipeline
- `cells/<cell-name>/docs/runbook.md` — operational runbook stub

## References

- [Implementation Guide: Greenfield Cell Setup](../../guides/agent-swarm-implementation-guide.md)
- [Cell Health Check Skill](../cell-health-check/SKILL.md)
- [Design Cell Boundaries Skill](../design-cell-boundaries/SKILL.md)

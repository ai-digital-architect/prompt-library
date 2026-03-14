---
description: >
  Create the complete directory structure, health contract, and CI/CD pipeline stub for a new cell.
  Trigger phrases: new cell, bootstrap cell, provision cell, set up cell, initialize cell,
  new service cell, create cell, greenfield cell.
---

## Purpose

Create the full directory structure, scoped instructions file, health contract, and CI/CD pipeline stub for a new cell in the cell-based architecture.

## Inputs

Before execution, collect the following:

1. **Cell name** — kebab-case identifier for the cell (e.g., `order-cell`)
2. **Owning team** — the team responsible for this cell
3. **Partitioning key** — what value determines assignment to this cell (e.g., Customer ID, region, hash shard)
4. **Target region** — AWS region or geographic location (e.g., `us-east-1`)
5. **Environment** — `development`, `staging`, `production`
6. **Bounded context** — the domain this cell serves (matches the hexagonal module name)
7. **Capacity ceiling** — Lambda reserved concurrency and DynamoDB max WCU limits

## Procedure

1. **Confirm cell metadata**
   - Verify the cell name follows the convention: `<bounded-context>-cell` or `<bounded-context>-cell-<shard>`
   - Confirm the partitioning key is the same as the system-wide partitioning key decided in the cell topology ADR

2. **Generate cell directory structure**
   - Create the standard layout:
     ```
     cells/<cell-name>/
     ├── src/                    ← Hexagonal module source (symlink or copy from shared module)
     ├── infrastructure/
     │   ├── main.tf             ← Terraform root module for this cell
     │   ├── variables.tf        ← Cell-specific variables (cell_id, region, capacity)
     │   └── outputs.tf          ← Required outputs: cell_id, api_endpoint, lambda_function_name
     ├── tests/
     │   └── integration/        ← Cell-level integration tests
     ├── docs/
     │   └── runbook.md          ← Cell operational runbook stub
     └── cell-contract.yaml      ← Health contract for this cell
     ```

3. **Create scoped CLAUDE.md**
   - Write `cells/<cell-name>/CLAUDE.md` with:
     - Cell identity (name, owning team, partitioning key, region)
     - Link to the bounded context hexagonal module
     - Cell-specific operational rules and capacity ceiling
     - Reference to the cell's `cell-contract.yaml`

4. **Generate health contract**
   - Write `cells/<cell-name>/cell-contract.yaml` with:
     - `cell_id`, `owning_team`, `partitioning_key`, `environment`
     - Required components: Lambda function, DynamoDB table, API Gateway stage
     - Required metrics namespace: `<Domain>/<cell-name>`
     - Required alarms: error rate, p99 latency, DLQ count, capacity utilization
     - Capacity ceiling: `lambda_reserved_concurrency`, `dynamodb_max_wcu`
     - Health endpoint: `/health`

5. **Create Terraform root module**
   - Write `cells/<cell-name>/infrastructure/main.tf` with:
     - Module reference to shared infrastructure module
     - Cell-specific variable overrides
     - All resources tagged with `CellId`, `Environment`, `OwningTeam`, `Domain`

6. **Generate Terraform outputs**
   - Write `cells/<cell-name>/infrastructure/outputs.tf` with required outputs:
     - `cell_id`, `api_endpoint`, `lambda_function_name`, `dynamodb_table_name`, `event_bus_name`

7. **Scaffold CI/CD pipeline**
   - Write `.github/workflows/deploy-<cell-name>.yml` with canary deployment:
     - Build and test
     - Deploy to canary cell instance
     - Validate: error rate < 0.5%, p99 < 300ms for 10 minutes
     - On success: deploy to all remaining cell instances in parallel
     - On failure: drain canary cell via routing layer weight update

8. **Create runbook stub**
   - Write `cells/<cell-name>/docs/runbook.md` with section stubs for:
     - Cell drain procedure
     - Rollback via routing layer
     - DLQ investigation
     - Capacity scaling

## Output

- **Cell directory**: `cells/<cell-name>/` with full standard structure
- **CLAUDE.md**: `cells/<cell-name>/CLAUDE.md` scoped to this cell
- **Health contract**: `cells/<cell-name>/cell-contract.yaml`
- **Terraform module**: `cells/<cell-name>/infrastructure/` with main, variables, and outputs
- **CI/CD pipeline**: `.github/workflows/deploy-<cell-name>.yml` with canary deployment
- **Runbook stub**: `cells/<cell-name>/docs/runbook.md`

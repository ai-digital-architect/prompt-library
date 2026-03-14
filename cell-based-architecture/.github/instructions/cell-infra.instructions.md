---
applyTo: "**/*.cell.{yml,yaml,tf}"
---

# Cell Infrastructure Standards

These rules apply to all cell infrastructure definition files matching `**/*.cell.{yml,yaml,tf}`. Cell infrastructure files define the deployment boundary and operational contract of a single cell. Violations in these files eliminate blast radius control — the primary value of cell-based architecture.

## Rules

1. **Health endpoint required** — Every cell infrastructure definition must include a `/health` endpoint that returns the cell's current status, version, and capacity utilization percentage in the format `{ status: "healthy"|"degraded"|"unhealthy", version: string, capacity_utilization: number }`.

2. **No cross-cell resource ARN references** — Cell infrastructure must not reference resource ARNs (DynamoDB table ARNs, Lambda function ARNs, EventBridge bus ARNs) that belong to other cells. All cross-cell dependencies must route through the global routing layer. A direct ARN reference from one cell to another's resource eliminates blast radius isolation.

3. **Explicit capacity ceiling required** — The cell capacity ceiling must be explicitly set. Unlimited Lambda concurrency and auto-scaling-without-ceiling DynamoDB are prohibited — they eliminate blast radius control by allowing one cell's failure to consume all capacity.

4. **Four required CloudWatch alarms per cell** — Each cell must have CloudWatch alarms for: (a) error rate exceeding 1% in a 5-minute window, (b) p99 latency exceeding 500ms, (c) Dead Letter Queue message count exceeding 0, and (d) capacity utilization exceeding 80% of the ceiling.

5. **Required Terraform outputs** — Cell Terraform modules must expose outputs for: `cell_id`, `api_endpoint`, `lambda_function_name`, `dynamodb_table_name`, `event_bus_name`. These outputs are required by the routing layer and monitoring infrastructure.

6. **Dead Letter Queues mandatory** — Dead Letter Queues are mandatory for all Lambda functions and EventBridge rules within a cell. Messages must be retained in the DLQ for at least 14 days. Missing DLQs eliminate the ability to investigate and replay failed operations.

7. **Required resource tagging** — All cell resources must be tagged with: `CellId` (the cell's unique identifier), `Environment` (development/staging/production), `OwningTeam` (the team responsible for this cell), and `Domain` (the bounded context this cell serves). Untagged resources fail cost allocation and compliance checks.

8. **Cell-scoped metric namespace** — All CloudWatch metrics emitted by a cell must use the namespace format `<Domain>/<cell-id>`. Metrics sharing a namespace across cells make it impossible to isolate failure signals to a single cell.

## Examples

### Rule 2: No cross-cell resource ARN references

✅ Compliant:
```yaml
# order-cell-01.cell.yml
resources:
  dynamodb_table: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/order-cell-01-orders"
  # ✅ References only this cell's own resources
routing_layer_endpoint: !ImportValue GlobalRoutingLayerEndpoint
  # ✅ Cross-cell communication through routing layer only
```

❌ Non-compliant:
```yaml
# order-cell-01.cell.yml
resources:
  # ❌ Direct reference to another cell's DynamoDB table — blast radius violation
  inventory_table: "arn:aws:dynamodb:us-east-1:123456789:table/inventory-cell-03-stock"
```

### Rule 3: Explicit capacity ceiling required

✅ Compliant:
```hcl
# order-cell-01.cell.tf
resource "aws_lambda_function" "handler" {
  reserved_concurrent_executions = 100  # ✅ Explicit ceiling — blast radius bounded
}

resource "aws_dynamodb_table" "orders" {
  billing_mode   = "PROVISIONED"
  read_capacity  = 50   # ✅ Explicit ceiling
  write_capacity = 50   # ✅ Explicit ceiling
}
```

❌ Non-compliant:
```hcl
resource "aws_lambda_function" "handler" {
  reserved_concurrent_executions = -1  # ❌ Unlimited concurrency — eliminates blast radius control
}
```

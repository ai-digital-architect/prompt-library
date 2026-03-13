# Cell-Based Architecture: Developer Guide

This guide covers implementation patterns, Terraform modules, and practical techniques for developers building cell-based systems on AWS.

## Table of Contents

1. [Terraform Project Structure](#terraform-project-structure)
2. [Cell Module Implementation](#cell-module-implementation)
3. [Multi-Region Deployment](#multi-region-deployment)
4. [Routing Layer Implementation](#routing-layer-implementation)
5. [Cell Assignment Service](#cell-assignment-service)
6. [Cell-Aware Application Code](#cell-aware-application-code)
7. [Cross-Cell Event Replication](#cross-cell-event-replication)
8. [Observability Implementation](#observability-implementation)
9. [Testing Cell Isolation](#testing-cell-isolation)
10. [Deployment Automation](#deployment-automation)

---

## Terraform Project Structure

### Recommended Directory Layout

```
infrastructure/
├── modules/
│   ├── cell/                      # Reusable cell module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── api_gateway.tf
│   │   ├── lambda.tf
│   │   ├── dynamodb.tf
│   │   ├── eventbridge.tf
│   │   └── observability.tf
│   ├── routing/                   # Global routing layer
│   │   ├── main.tf
│   │   ├── cloudfront.tf
│   │   ├── route53.tf
│   │   └── lambda_edge.tf
│   └── cell-assignment/           # Cell assignment service
│       ├── main.tf
│       ├── dynamodb_global.tf
│       └── lambda.tf
│
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── cells.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── ...
│   └── prod/
│       └── ...
│
├── global/                        # Global resources (Route 53, IAM)
│   ├── main.tf
│   ├── route53.tf
│   └── iam.tf
│
└── scripts/
    ├── deploy-cell.sh
    ├── rollback-cell.sh
    └── migrate-customer.sh
```

### Workspace Strategy

Use Terraform workspaces for environment isolation, but deploy cells as separate module instances:

```hcl
# environments/prod/main.tf

terraform {
  required_version = ">= 1.5.0"
  
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "prod/cells/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Provider for primary region
provider "aws" {
  region = "us-east-1"
  alias  = "us_east_1"
  
  default_tags {
    tags = {
      Environment = "prod"
      ManagedBy   = "terraform"
      Project     = "payments"
    }
  }
}

# Provider for secondary region
provider "aws" {
  region = "eu-west-1"
  alias  = "eu_west_1"
  
  default_tags {
    tags = {
      Environment = "prod"
      ManagedBy   = "terraform"
      Project     = "payments"
    }
  }
}
```

---

## Cell Module Implementation

### Core Cell Module

```hcl
# modules/cell/variables.tf

variable "cell_id" {
  description = "Unique identifier for this cell (e.g., cell-01, cell-02)"
  type        = string
  
  validation {
    condition     = can(regex("^cell-[0-9]{2}$", var.cell_id))
    error_message = "Cell ID must match pattern cell-XX (e.g., cell-01)."
  }
}

variable "domain_name" {
  description = "Domain/service name (e.g., payments, orders)"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "lambda_source_path" {
  description = "Path to Lambda deployment package"
  type        = string
}

variable "capacity_config" {
  description = "Cell capacity configuration"
  type = object({
    max_concurrent_executions = number
    dynamodb_read_capacity    = optional(number)
    dynamodb_write_capacity   = optional(number)
  })
  default = {
    max_concurrent_executions = 100
    dynamodb_read_capacity    = null  # On-demand
    dynamodb_write_capacity   = null  # On-demand
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
```

```hcl
# modules/cell/main.tf

locals {
  cell_prefix = "${var.domain_name}-${var.environment}-${var.cell_id}"
  
  common_tags = merge(var.tags, {
    CellId      = var.cell_id
    Domain      = var.domain_name
    Environment = var.environment
  })
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = "${local.cell_prefix}-dlq"
  message_retention_seconds = 1209600  # 14 days
  
  tags = local.common_tags
}

resource "aws_sqs_queue" "dlq_alarm_topic" {
  name = "${local.cell_prefix}-dlq-alarm"
  tags = local.common_tags
}
```

```hcl
# modules/cell/dynamodb.tf

resource "aws_dynamodb_table" "main" {
  name         = "${local.cell_prefix}-data"
  billing_mode = var.capacity_config.dynamodb_read_capacity != null ? "PROVISIONED" : "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.common_tags
}
```

```hcl
# modules/cell/eventbridge.tf

resource "aws_cloudwatch_event_bus" "main" {
  name = "${local.cell_prefix}-events"
  tags = local.common_tags
}

# Archive for replay capability
resource "aws_cloudwatch_event_archive" "main" {
  name             = "${local.cell_prefix}-archive"
  event_source_arn = aws_cloudwatch_event_bus.main.arn
  retention_days   = 30
}

# DLQ for failed events
resource "aws_cloudwatch_event_rule" "dlq_rule" {
  name           = "${local.cell_prefix}-failed-events"
  event_bus_name = aws_cloudwatch_event_bus.main.name
  
  event_pattern = jsonencode({
    "detail-type" = ["Error"]
  })
}

resource "aws_cloudwatch_event_target" "dlq_target" {
  rule           = aws_cloudwatch_event_rule.dlq_rule.name
  event_bus_name = aws_cloudwatch_event_bus.main.name
  target_id      = "send-to-dlq"
  arn            = aws_sqs_queue.dlq.arn
}
```

```hcl
# modules/cell/lambda.tf

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "${local.cell_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${local.cell_prefix}-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.main.arn,
          "${aws_dynamodb_table.main.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["events:PutEvents"]
        Resource = aws_cloudwatch_event_bus.main.arn
      },
      {
        Effect = "Allow"
        Action = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.dlq.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "handler" {
  function_name = "${local.cell_prefix}-handler"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  timeout       = 30
  memory_size   = 256

  filename         = var.lambda_source_path
  source_code_hash = filebase64sha256(var.lambda_source_path)

  reserved_concurrent_executions = var.capacity_config.max_concurrent_executions

  environment {
    variables = {
      CELL_ID         = var.cell_id
      ENVIRONMENT     = var.environment
      TABLE_NAME      = aws_dynamodb_table.main.name
      EVENT_BUS_NAME  = aws_cloudwatch_event_bus.main.name
      DLQ_URL         = aws_sqs_queue.dlq.url
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  tracing_config {
    mode = "Active"
  }

  tags = local.common_tags
}

# CloudWatch Log Group with retention
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.handler.function_name}"
  retention_in_days = 30
  tags              = local.common_tags
}
```

```hcl
# modules/cell/api_gateway.tf

resource "aws_apigatewayv2_api" "main" {
  name          = "${local.cell_prefix}-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Cell-Id", "X-Correlation-Id"]
    max_age       = 300
  }

  tags = local.common_tags
}

resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "v1"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId        = "$context.requestId"
      ip               = "$context.identity.sourceIp"
      httpMethod       = "$context.httpMethod"
      status           = "$context.status"
      cellId           = var.cell_id
    })
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.cell_prefix}"
  retention_in_days = 30
  tags              = local.common_tags
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
```

```hcl
# modules/cell/outputs.tf

output "cell_id" {
  description = "Cell identifier"
  value       = var.cell_id
}

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.handler.function_name
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.main.name
}

output "event_bus_name" {
  description = "EventBridge event bus name"
  value       = aws_cloudwatch_event_bus.main.name
}

output "dlq_url" {
  description = "Dead letter queue URL"
  value       = aws_sqs_queue.dlq.url
}
```

---

## Multi-Region Deployment

### Deploying Cells Across Regions

```hcl
# environments/prod/cells.tf

module "cell_us_east_1_01" {
  source = "../../modules/cell"
  providers = { aws = aws.us_east_1 }

  cell_id            = "cell-01"
  domain_name        = "payments"
  environment        = "prod"
  lambda_source_path = "${path.module}/../../dist/lambda.zip"
  
  capacity_config = {
    max_concurrent_executions = 100
  }
}

module "cell_us_east_1_02" {
  source = "../../modules/cell"
  providers = { aws = aws.us_east_1 }

  cell_id            = "cell-02"
  domain_name        = "payments"
  environment        = "prod"
  lambda_source_path = "${path.module}/../../dist/lambda.zip"
  
  capacity_config = {
    max_concurrent_executions = 100
  }
}

module "cell_eu_west_1_01" {
  source = "../../modules/cell"
  providers = { aws = aws.eu_west_1 }

  cell_id            = "cell-01"
  domain_name        = "payments"
  environment        = "prod"
  lambda_source_path = "${path.module}/../../dist/lambda.zip"
  
  capacity_config = {
    max_concurrent_executions = 50
  }
}

output "cell_endpoints" {
  value = {
    "us-east-1-cell-01" = module.cell_us_east_1_01.api_endpoint
    "us-east-1-cell-02" = module.cell_us_east_1_02.api_endpoint
    "eu-west-1-cell-01" = module.cell_eu_west_1_01.api_endpoint
  }
}
```

---

## Routing Layer Implementation

### Lambda@Edge Router

```typescript
// modules/routing/edge-router/src/index.ts
import { CloudFrontRequestEvent, CloudFrontRequestResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand } from '@aws-sdk/lib-dynamodb';

const CELL_ENDPOINTS = JSON.parse(process.env.CELL_ENDPOINTS || '{}');
const DEFAULT_CELL = process.env.DEFAULT_CELL || 'us-east-1-cell-01';
const CELL_ASSIGNMENT_TABLE = process.env.CELL_ASSIGNMENT_TABLE!;

const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);

export const handler = async (
  event: CloudFrontRequestEvent
): Promise<CloudFrontRequestResult> => {
  const request = event.Records[0].cf.request;
  
  const customerId = extractCustomerId(request);
  const cellId = await getCellAssignment(customerId);
  const endpoint = CELL_ENDPOINTS[cellId] || CELL_ENDPOINTS[DEFAULT_CELL];
  const url = new URL(endpoint);
  
  request.origin = {
    custom: {
      domainName: url.hostname,
      port: 443,
      protocol: 'https',
      path: url.pathname.replace(/\/$/, ''),
      sslProtocols: ['TLSv1.2'],
      readTimeout: 30,
      keepaliveTimeout: 5,
    },
  };

  request.headers['host'] = [{ key: 'Host', value: url.hostname }];
  request.headers['x-cell-id'] = [{ key: 'X-Cell-Id', value: cellId }];
  
  return request;
};

function extractCustomerId(request: any): string {
  const customerHeader = request.headers['x-customer-id'];
  if (customerHeader?.[0]) return customerHeader[0].value;
  return 'anonymous';
}

async function getCellAssignment(customerId: string): Promise<string> {
  if (customerId === 'anonymous') return DEFAULT_CELL;

  try {
    const result = await docClient.send(new GetCommand({
      TableName: CELL_ASSIGNMENT_TABLE,
      Key: { PK: `CUSTOMER#${customerId}` },
    }));
    return result.Item?.cellId || DEFAULT_CELL;
  } catch {
    return DEFAULT_CELL;
  }
}
```

---

## Cell Assignment Service

### DynamoDB Global Table

```hcl
# modules/cell-assignment/dynamodb_global.tf

resource "aws_dynamodb_table" "cell_assignment" {
  provider     = aws.us_east_1
  name         = "cell-assignment"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "cellId"
    type = "S"
  }

  global_secondary_index {
    name            = "by-cell"
    hash_key        = "cellId"
    projection_type = "ALL"
  }

  replica {
    region_name = "eu-west-1"
  }

  point_in_time_recovery {
    enabled = true
  }
}
```

---

## Cell-Aware Application Code

### Context and Logging

```typescript
// src/context/cell-context.ts
import { AsyncLocalStorage } from 'async_hooks';

export interface CellContext {
  cellId: string;
  region: string;
  correlationId: string;
}

const storage = new AsyncLocalStorage<CellContext>();

export const runWithCellContext = <T>(ctx: CellContext, fn: () => T): T => 
  storage.run(ctx, fn);

export const getCellContext = (): CellContext => {
  const ctx = storage.getStore();
  if (!ctx) throw new Error('Cell context not initialized');
  return ctx;
};

// src/logging/logger.ts
import { getCellContext } from '../context/cell-context';

export const logger = {
  info: (message: string, data?: Record<string, any>) => {
    const ctx = getCellContext();
    console.log(JSON.stringify({
      level: 'info',
      message,
      cellId: ctx.cellId,
      correlationId: ctx.correlationId,
      timestamp: new Date().toISOString(),
      ...data,
    }));
  },
};
```

---

## Deployment Automation

### GitHub Actions Pipeline

```yaml
# .github/workflows/deploy-cells.yml
name: Deploy Cells

on:
  push:
    branches: [main]

jobs:
  deploy-canary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Deploy Canary Cell
        working-directory: infrastructure/environments/prod
        run: |
          terraform init
          terraform apply -target=module.cell_us_east_1_01 -auto-approve

  deploy-remaining:
    needs: deploy-canary
    runs-on: ubuntu-latest
    strategy:
      matrix:
        cell: [cell_us_east_1_02, cell_eu_west_1_01]
      max-parallel: 1
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Deploy Cell
        working-directory: infrastructure/environments/prod
        run: |
          terraform init
          terraform apply -target=module.${{ matrix.cell }} -auto-approve
```

---

## Quick Reference: Terraform Cell Implementation Checklist

- [ ] Cell module created with all required resources
- [ ] Variables defined with proper validation
- [ ] Outputs expose cell ID, endpoints, and ARNs
- [ ] Multi-region providers configured
- [ ] Cells deployed via module instances
- [ ] Cell assignment DynamoDB Global Table deployed
- [ ] Routing layer (CloudFront + Lambda@Edge) deployed
- [ ] CloudWatch dashboards per cell
- [ ] Alarms configured for errors, latency, DLQ
- [ ] GitHub Actions pipeline with canary deployment
- [ ] Rollback script tested

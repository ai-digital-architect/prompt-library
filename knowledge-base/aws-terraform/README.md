# AWS & Terraform Development Guidelines

## Project Structure

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
├── modules/
│   ├── networking/
│   ├── compute/
│   ├── database/
│   └── security/
└── shared/
    ├── outputs.tf
    └── variables.tf
```

## Best Practices

### Module Organization

```hcl
# Example module structure
module "vpc" {
  source = "../../modules/networking"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  
  tags = local.common_tags
}
```

### Resource Naming

```hcl
# Use consistent naming conventions
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
  
  name_prefix = "${var.project_name}-${var.environment}"
}
```

### State Management

- Use remote state (S3 + DynamoDB)
- Implement state locking
- Use workspaces for environments
- Proper backend configuration
- State file backup strategy

### Security

- Use KMS encryption
- Implement least privilege
- Secure secrets management
- Network security groups
- IAM best practices

### AWS Best Practices

- Region strategy
- High availability design
- Disaster recovery
- Cost optimization
- Performance efficiency

## Common Patterns

### VPC Setup

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${local.name_prefix}-vpc"
  cidr = var.vpc_cidr
  
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  enable_nat_gateway = true
  single_nat_gateway = var.environment != "prod"
  
  tags = local.common_tags
}
```

### ECS Cluster

```hcl
module "ecs_cluster" {
  source = "../../modules/compute/ecs"
  
  cluster_name = "${local.name_prefix}-cluster"
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
  
  tags = local.common_tags
}
```

### RDS Database

```hcl
module "rds" {
  source = "../../modules/database"
  
  identifier = "${local.name_prefix}-db"
  engine     = "postgres"
  
  vpc_security_group_ids = [module.security_groups.rds_sg_id]
  subnet_ids            = module.vpc.database_subnets
  
  backup_retention_period = var.environment == "prod" ? 30 : 7
  
  tags = local.common_tags
}
```

## Variables and Outputs

### variables.tf

```hcl
variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones"
}
```

### outputs.tf

```hcl
output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "ID of the created VPC"
}

output "private_subnets" {
  value       = module.vpc.private_subnets
  description = "List of private subnet IDs"
}
```

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Terraform

on:
  pull_request:
    paths:
      - 'infrastructure/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1
      
      - name: Terraform Format
        run: terraform fmt -check
      
      - name: Terraform Plan
        run: |
          terraform init
          terraform plan
```

## Development Workflow

1. Use terraform workspaces
2. Follow Git workflow
3. Run terraform fmt
4. Validate changes
5. Plan before apply
6. Use proper documentation

## Security Controls

- Enable AWS CloudTrail
- Implement AWS Config
- Use Security Hub
- Enable GuardDuty
- Implement WAF rules

## Cost Management

- Use cost allocation tags
- Implement auto-scaling
- Use spot instances
- Proper resource sizing
- Cost monitoring tools

## Monitoring & Logging

- CloudWatch setup
- Proper log retention
- Metrics configuration
- Alerting setup
- Dashboard creation

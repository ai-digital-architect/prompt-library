# AWS Infrastructure Analysis & Well-Architected Review

## Claude Code Customization Architecture — Applied to Multi-Repo Terraform Analysis

---

## Executive Summary

This document defines the complete Claude Code architecture for analyzing 30+ Terraform IaC
repositories, producing a unified AWS architecture diagram in draw.io XML format (with AWS
stencils, importable to Lucidchart), and applying the AWS Well-Architected Framework to
identify weaknesses and resilience enhancement opportunities — including multi-region posture.

The workflow is a **five-phase pipeline** using a **map-reduce** pattern across repositories,
with specialized sub-agents for extraction, synthesis, diagramming, and analysis.

---

## Table of Contents

1. [Why This Architecture](#1-why-this-architecture)
2. [Prerequisites and Preparation](#2-prerequisites-and-preparation)
3. [Project Structure](#3-project-structure)
4. [Phase 1: Repository Extraction (Map)](#4-phase-1-repository-extraction-map)
5. [Phase 2: Architecture Synthesis (Reduce)](#5-phase-2-architecture-synthesis-reduce)
6. [Phase 3: Diagram Generation](#6-phase-3-diagram-generation)
7. [Phase 4: Well-Architected Analysis](#7-phase-4-well-architected-analysis)
8. [Phase 5: Enhancement Overlay & Recommendations](#8-phase-5-enhancement-overlay--recommendations)
9. [Complete File Implementations](#9-complete-file-implementations)
10. [Execution Playbook](#10-execution-playbook)
11. [Token Cost Strategy](#11-token-cost-strategy)

---

## 1. Why This Architecture

The core challenge is **scale and context management**. Thirty-plus Terraform repositories
collectively contain tens of thousands of lines of HCL. No single Claude Code context window
can hold all of it simultaneously. The architecture must:

- **Fan out** across repositories so each is analyzed in isolation (sub-agent per repo)
- **Produce structured intermediate artifacts** (JSON) that compress the signal from each repo
- **Merge** those artifacts into a unified architecture model without context overflow
- **Separate concerns** so the diagramming specialist doesn't need to understand Terraform and the Terraform analyst doesn't need to know draw.io XML

This maps directly to the Claude Code customization architecture:

| Concern | Component | Why |
|---------|-----------|-----|
| Per-repo Terraform analysis | **Sub-agent** (read-only, isolated context) | Each repo gets a fresh context; no cross-contamination |
| Unified architecture model | **Skill** (coordinator) | Orchestrates map-reduce; holds the intermediate model |
| draw.io XML generation | **Sub-agent** (write-capable, isolated) | Specialized XML knowledge; doesn't need Terraform context |
| Well-Architected analysis | **Sub-agent** (read-only, isolated) | Needs the unified model, not the raw Terraform |
| Validation after each phase | **PostToolUse Hook** | Deterministic JSON schema validation between phases |
| Draw.io XML well-formedness | **PostToolUse Hook** | Validates XML after generation |

---

## 2. Prerequisites and Preparation

### 2.1 Existing Repository Inventory

All 30+ Terraform repositories are already cloned locally. Before running the pipeline,
Claude Code needs to discover them and prepare the workspace.

The **first step of Phase 1** is an automated discovery skill (`/discover-repos`) that:
1. Scans the `repos/` directory to find all Terraform repositories
2. Validates each repo contains `.tf` files
3. Detects the repo structure (flat, monorepo with modules, workspace-based)
4. Generates `repo-manifest.json` with metadata for every repo
5. Creates the `extractions/` and `output/` directories

This means the only manual step before starting is confirming the repos path:

```bash
# Verify repos are in place
ls repos/

# Then open Claude Code and run the pipeline
# Claude Code handles everything from here
```

### 2.2 No Terraform CLI Required

This pipeline operates entirely by reading `.tf` files from disk. It does **not** require:
- `terraform init` (no provider downloads, no module registry access)
- `terraform plan` or `terraform apply` (no AWS credentials)
- `terraform graph` (no initialized backend)
- Any network access to Terraform registries (public or private)

The extraction agent parses HCL directly — reading `resource`, `data`, `module`, `variable`,
`output`, `provider`, `locals`, and `terraform` blocks from the raw `.tf` files. This captures
the full architectural intent: what resources are declared, how they reference each other,
what modules are used, what regions are targeted, and how repos depend on each other via
remote state.

### 2.3 What HCL-Only Extraction Captures

| What It Captures | How |
|-----------------|-----|
| All AWS resources and their attributes | Reads `resource "aws_*"` blocks |
| Resource-to-resource dependencies | Parses HCL references like `aws_subnet.main.id` |
| Module usage and inputs | Reads `module` blocks; infers created resources from source name |
| Multi-region patterns | Reads `provider "aws"` blocks with `alias` and `region` |
| Cross-repo dependencies | Reads `terraform_remote_state` data sources and `aws_ssm_parameter` lookups |
| Security posture | Reads security group rules, encryption attributes, IAM policies |
| Networking topology | Reads VPC, subnet, NAT GW, IGW, peering, transit gateway resources |
| Backup/DR configuration | Reads backup, replication, and multi-AZ attributes |

| What It Cannot Capture | Workaround |
|------------------------|------------|
| Computed values (dynamic CIDR, AMI IDs) | Agent notes these as `"<computed>"` in extraction |
| Resources created inside private registry modules | Agent infers from module source name and inputs |
| Actual resource counts from `count`/`for_each` with variables | Agent notes the expression; synthesis estimates |
| Live drift from declared state | Out of scope — this analyzes intent, not runtime |

### 2.4 Private Module Handling

Since we are not running `terraform init`, private modules from registries (e.g.,
`app.terraform.io/yourorg/vpc/aws`) are **not downloaded**. The extraction agent handles
this by:

1. Reading the `module` block's `source` and `version` attributes
2. Inferring the resource types created based on the module name:
   - `*/vpc/*` → `aws_vpc`, `aws_subnet`, `aws_internet_gateway`, `aws_nat_gateway`
   - `*/ecs/*` → `aws_ecs_cluster`, `aws_ecs_service`, `aws_ecs_task_definition`
   - `*/rds/*` → `aws_rds_cluster` or `aws_db_instance`
   - `*/alb/*` or `*/elb/*` → `aws_lb`, `aws_lb_target_group`, `aws_lb_listener`
3. Reading the input variables passed to the module for additional context
   (e.g., `multi_az = true`, `engine = "aurora-mysql"`)
4. If the module source is a **relative path** (e.g., `source = "../../modules/vpc"`),
   the agent reads the module's `.tf` files directly from disk — these are fully analyzable
5. If the module source is a **git URL** and that repo is also in `repos/`, the agent
   cross-references it

The agent marks unresolvable modules with `"resolution": "inferred"` in the extraction JSON
so the synthesis phase knows which data is exact vs estimated.

### 2.5 Tool Requirements

The only tools needed on the host machine:

| Tool | Required? | Purpose |
|------|-----------|---------|
| `jq` | **Yes** | Hooks use it to validate extraction JSON |
| `python3` | **Yes** | Draw.io XML validation hook (uses `xml.etree.ElementTree`) |
| `grep`, `find`, `cat`, `sort` | **Yes** (standard Unix) | Extraction agent uses these for HCL parsing |

```bash
# Verify tools
jq --version
python3 -c "import xml.etree.ElementTree; print('XML validation available')"
```

---

## 3. Project Structure

```
aws-architecture-analysis/
├── CLAUDE.md                                    ← Project memory: conventions, schemas, AWS context
├── .claude/
│   ├── settings.json                            ← Hooks and permissions
│   ├── agents/
│   │   ├── tf-repo-extractor.md                 ← Phase 1: per-repo HCL analyzer (read-only)
│   │   ├── architecture-synthesizer.md          ← Phase 2: merges all extractions (read-only)
│   │   ├── drawio-generator.md                  ← Phase 3: produces draw.io XML (write-capable)
│   │   ├── well-architected-analyzer.md         ← Phase 4: WAF analysis (read-only)
│   │   └── enhancement-overlayer.md             ← Phase 5: overlays findings on diagram (write-capable)
│   ├── skills/
│   │   ├── analyze-aws-infra/
│   │   │   └── SKILL.md                         ← Master orchestrator (full pipeline)
│   │   ├── discover-repos/
│   │   │   └── SKILL.md                         ← Phase 0: scans repos/, builds manifest
│   │   ├── extract-repo/
│   │   │   └── SKILL.md                         ← Single-repo extraction (for testing/reruns)
│   │   ├── generate-diagram/
│   │   │   └── SKILL.md                         ← Diagram generation only
│   │   └── well-architected-review/
│   │       └── SKILL.md                         ← WAF analysis only
│   └── hooks/
│       ├── validate-extraction-json.sh          ← PostToolUse: validates extraction output schema
│       └── validate-drawio-xml.sh               ← PostToolUse: validates draw.io XML well-formedness
├── repos/                                       ← EXISTING: your 30+ Terraform repositories (read-only)
│   ├── networking-core/
│   ├── compute-platform/
│   ├── data-services/
│   └── ...                                      ← Whatever your actual repo names are
├── repo-manifest.json                           ← Phase 0 output: auto-discovered repo metadata
├── extractions/                                 ← Phase 1 output: one JSON per repo
│   ├── networking-core.json
│   ├── compute-platform.json
│   └── ...
└── output/
    ├── unified-architecture.json                ← Phase 2 output: merged model
    ├── aws-architecture.drawio.xml              ← Phase 3 output: importable diagram
    ├── well-architected-report.md               ← Phase 4 output: findings
    ├── aws-architecture-annotated.drawio.xml    ← Phase 5 output: diagram with findings
    └── enhancement-roadmap.md                   ← Phase 5 output: prioritized recommendations
```

---

## 4. Phase 1: Repository Extraction (Map)

### 4.1 Strategy

Fan out one **read-only sub-agent** per repository. Each agent:
1. Reads all `.tf` files in the repo (using `find`, `cat`, `grep`)
2. Parses every `resource`, `data`, `module`, `variable`, `output`, and `provider` block
3. Extracts every AWS resource, data source, module reference, and variable
4. Maps inter-resource relationships by parsing HCL references (e.g., `aws_vpc.main.id`)
5. Identifies networking topology (VPCs, subnets, peering, transit gateways)
6. Detects multi-region patterns (provider aliases, region variables)
7. Produces a structured JSON extraction file

### 4.2 Extraction Schema

Every extraction MUST conform to this schema. The synthesis phase depends on it.

```json
{
  "repo_name": "repo-01-networking",
  "repo_path": "repos/repo-01-networking",
  "extracted_at": "2026-03-26T12:00:00Z",
  "terraform_version": "1.7.0",
  "providers": [
    {
      "name": "aws",
      "alias": "us-east-1",
      "region": "us-east-1",
      "version_constraint": "~> 5.0"
    },
    {
      "name": "aws",
      "alias": "us-west-2",
      "region": "us-west-2",
      "version_constraint": "~> 5.0"
    }
  ],
  "regions_used": ["us-east-1", "us-west-2"],
  "resources": [
    {
      "type": "aws_vpc",
      "name": "main",
      "address": "aws_vpc.main",
      "provider_alias": "us-east-1",
      "region": "us-east-1",
      "attributes": {
        "cidr_block": "10.0.0.0/16",
        "enable_dns_support": true,
        "enable_dns_hostnames": true
      },
      "tags": {
        "Name": "production-vpc",
        "Environment": "production"
      },
      "references_to": [],
      "referenced_by": ["aws_subnet.public_a", "aws_subnet.private_a"]
    }
  ],
  "data_sources": [
    {
      "type": "aws_ami",
      "name": "amazon_linux",
      "address": "data.aws_ami.amazon_linux",
      "filters": {"name": "amzn2-ami-hvm-*"}
    }
  ],
  "modules": [
    {
      "name": "vpc",
      "source": "terraform-aws-modules/vpc/aws",
      "version": "5.1.0",
      "resources_created": ["aws_vpc", "aws_subnet", "aws_internet_gateway"],
      "input_variables": {"cidr": "10.0.0.0/16", "azs": ["us-east-1a", "us-east-1b"]}
    }
  ],
  "outputs": [
    {
      "name": "vpc_id",
      "value_reference": "aws_vpc.main.id",
      "description": "ID of the production VPC"
    }
  ],
  "networking": {
    "vpcs": [
      {
        "resource_address": "aws_vpc.main",
        "cidr": "10.0.0.0/16",
        "region": "us-east-1",
        "subnets": {
          "public": ["10.0.1.0/24", "10.0.2.0/24"],
          "private": ["10.0.10.0/24", "10.0.11.0/24"]
        },
        "nat_gateways": 2,
        "internet_gateway": true
      }
    ],
    "peering_connections": [],
    "transit_gateways": [],
    "vpn_connections": [],
    "route53_zones": []
  },
  "compute": {
    "ec2_instances": [],
    "autoscaling_groups": [],
    "ecs_clusters": [],
    "ecs_services": [],
    "eks_clusters": [],
    "lambda_functions": [],
    "fargate_services": []
  },
  "data_stores": {
    "rds_instances": [],
    "rds_clusters": [],
    "dynamodb_tables": [],
    "elasticache_clusters": [],
    "s3_buckets": [],
    "redshift_clusters": []
  },
  "security": {
    "iam_roles": [],
    "iam_policies": [],
    "security_groups": [],
    "nacls": [],
    "kms_keys": [],
    "waf_web_acls": [],
    "secrets_manager_secrets": [],
    "certificate_manager_certs": []
  },
  "integration": {
    "api_gateways": [],
    "load_balancers": [],
    "cloudfront_distributions": [],
    "sqs_queues": [],
    "sns_topics": [],
    "eventbridge_rules": [],
    "step_functions": []
  },
  "monitoring": {
    "cloudwatch_alarms": [],
    "cloudwatch_dashboards": [],
    "cloudtrail_trails": [],
    "config_rules": [],
    "guardduty_detectors": []
  },
  "cross_repo_references": {
    "remote_state_reads": [
      {
        "backend": "s3",
        "config": {"bucket": "terraform-state", "key": "networking/terraform.tfstate"},
        "outputs_consumed": ["vpc_id", "private_subnet_ids"]
      }
    ],
    "ssm_parameter_reads": [
      {
        "name": "/infrastructure/vpc/id",
        "consumed_by": "aws_instance.app_server"
      }
    ],
    "shared_resource_arns": []
  },
  "resilience_indicators": {
    "multi_az": false,
    "multi_region": false,
    "backup_configured": false,
    "dr_pattern": "none",
    "health_checks": [],
    "circuit_breakers": []
  }
}
```

### 4.3 Why This Schema Matters

The schema is designed around **what the synthesis and diagramming phases need**, not what
Terraform natively exposes. Key design decisions:

- **`cross_repo_references`** captures how repos depend on each other via remote state, SSM
  parameters, or shared ARNs. This is critical for building the unified view.
- **`networking`** is a denormalized summary of the VPC topology — the diagram generator needs
  this to draw network boundaries correctly.
- **`resilience_indicators`** are pre-computed flags that the Well-Architected analyzer reads
  directly, avoiding redundant re-analysis.
- **`resources[].references_to` / `referenced_by`** capture the dependency graph at extraction
  time. The synthesis phase uses these to draw connections between resources across repos.

---

## 5. Phase 2: Architecture Synthesis (Reduce)

### 5.1 Strategy

A single **read-only sub-agent** reads all extraction JSON files and produces a unified
architecture model. This is the most intellectually complex phase — it must:

1. Resolve cross-repo dependencies (repo A's remote state → repo B's outputs)
2. Deduplicate resources referenced from multiple repos
3. Build a global VPC topology with cross-VPC relationships
4. Identify shared services (shared ALBs, centralized logging, common IAM roles)
5. Map the complete request flow from edge (CloudFront/ALB) to data stores
6. Determine the blast radius of each component (what fails if this fails?)
7. Classify resources into architectural tiers (edge, compute, data, management)

### 5.2 Unified Architecture Model Schema

```json
{
  "metadata": {
    "generated_at": "2026-03-26T14:00:00Z",
    "repos_analyzed": 32,
    "total_resources": 847,
    "regions": ["us-east-1", "us-west-2", "eu-west-1"],
    "accounts": ["production", "staging", "shared-services"]
  },
  "topology": {
    "regions": [
      {
        "name": "us-east-1",
        "is_primary": true,
        "vpcs": [
          {
            "id": "production-vpc",
            "cidr": "10.0.0.0/16",
            "source_repo": "repo-01-networking",
            "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"],
            "subnets": {
              "public": [{"cidr": "10.0.1.0/24", "az": "us-east-1a"}],
              "private": [{"cidr": "10.0.10.0/24", "az": "us-east-1a"}],
              "data": [{"cidr": "10.0.20.0/24", "az": "us-east-1a"}]
            },
            "resources": ["aws_ecs_cluster.main", "aws_rds_cluster.primary"],
            "connections": {
              "peering": ["shared-services-vpc"],
              "transit_gateway": [],
              "internet": true,
              "nat": true
            }
          }
        ]
      }
    ],
    "cross_region_connections": [
      {
        "type": "rds_read_replica",
        "from": {"region": "us-east-1", "resource": "aws_rds_cluster.primary"},
        "to": {"region": "us-west-2", "resource": "aws_rds_cluster.replica"}
      }
    ]
  },
  "service_map": {
    "tiers": {
      "edge": {
        "resources": [
          {"address": "aws_cloudfront_distribution.main", "repo": "repo-05-cdn", "region": "global"},
          {"address": "aws_waf_web_acl.global", "repo": "repo-12-security", "region": "global"}
        ]
      },
      "ingress": {
        "resources": [
          {"address": "aws_lb.api", "repo": "repo-03-compute", "region": "us-east-1"}
        ]
      },
      "compute": {
        "resources": [
          {"address": "aws_ecs_service.api", "repo": "repo-03-compute", "region": "us-east-1"},
          {"address": "aws_lambda_function.processor", "repo": "repo-07-events", "region": "us-east-1"}
        ]
      },
      "data": {
        "resources": [
          {"address": "aws_rds_cluster.primary", "repo": "repo-04-data", "region": "us-east-1"},
          {"address": "aws_dynamodb_table.sessions", "repo": "repo-04-data", "region": "us-east-1"}
        ]
      },
      "integration": {
        "resources": [
          {"address": "aws_sqs_queue.events", "repo": "repo-07-events", "region": "us-east-1"}
        ]
      },
      "management": {
        "resources": [
          {"address": "aws_cloudwatch_dashboard.main", "repo": "repo-10-monitoring", "region": "us-east-1"},
          {"address": "aws_cloudtrail.org", "repo": "repo-12-security", "region": "us-east-1"}
        ]
      }
    },
    "request_flows": [
      {
        "name": "API request flow",
        "path": [
          "aws_cloudfront_distribution.main",
          "aws_lb.api",
          "aws_ecs_service.api",
          "aws_rds_cluster.primary"
        ]
      }
    ],
    "event_flows": [
      {
        "name": "Async event processing",
        "path": [
          "aws_sqs_queue.events",
          "aws_lambda_function.processor",
          "aws_dynamodb_table.results"
        ]
      }
    ]
  },
  "dependency_graph": {
    "nodes": [],
    "edges": [
      {
        "from": "aws_ecs_service.api",
        "to": "aws_rds_cluster.primary",
        "type": "data_dependency",
        "criticality": "high"
      }
    ]
  },
  "blast_radius_map": {
    "aws_rds_cluster.primary": {
      "direct_dependents": ["aws_ecs_service.api", "aws_lambda_function.reports"],
      "transitive_dependents": ["aws_cloudfront_distribution.main"],
      "blast_radius": "critical",
      "users_affected": "all"
    }
  }
}
```

---

## 6. Phase 3: Diagram Generation

### 6.1 Strategy

A **write-capable sub-agent** reads the unified architecture model and produces a draw.io
XML file using AWS architecture stencils. The diagram must be importable into both draw.io
and Lucidchart.

### 6.2 Draw.io XML Structure with AWS Stencils

Draw.io uses `mxGraphModel` XML. AWS stencils are referenced via shape styles. The key
insight is that Lucidchart imports draw.io XML natively — you just need to use the
standard `mxGraphModel` format.

**Critical draw.io conventions:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="AWS Architecture" id="aws-arch-001">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="3300" pageHeight="2540" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- AWS Cloud boundary -->
        <mxCell id="aws-cloud" value="AWS Cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=1;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;" vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="3260" height="2500" as="geometry"/>
        </mxCell>

        <!-- Region boundary -->
        <mxCell id="region-use1" value="us-east-1" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=1;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=1;" vertex="1" parent="aws-cloud">
          <mxGeometry x="20" y="40" width="1560" height="2400" as="geometry"/>
        </mxCell>

        <!-- VPC boundary -->
        <mxCell id="vpc-prod" value="Production VPC&#xa;10.0.0.0/16" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=1;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;" vertex="1" parent="region-use1">
          <mxGeometry x="20" y="40" width="1500" height="1200" as="geometry"/>
        </mxCell>

        <!-- Individual resource example (EC2) -->
        <mxCell id="ec2-api" value="API Server" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2" vertex="1" parent="vpc-prod">
          <mxGeometry x="200" y="300" width="60" height="60" as="geometry"/>
        </mxCell>

        <!-- Connection arrow -->
        <mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" source="ec2-api" target="rds-primary" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 6.3 AWS Stencil Style Reference

The diagram generator agent needs this reference. These are the draw.io style strings
for common AWS services (AWS Architecture 2024 icon set):

```
## Grouping Containers
AWS Cloud:        shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E
Region:           shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6
VPC:              shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF
Availability Zone:shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_availability_zone;strokeColor=#00A4A6
Public Subnet:    shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#7AA116;fillColor=#E9F3E6
Private Subnet:   shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7
Security Group:   shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#DD3522

## Compute (fillColor=#ED7100)
EC2:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;fillColor=#ED7100
Lambda:           shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda;fillColor=#ED7100
ECS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs;fillColor=#ED7100
EKS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eks;fillColor=#ED7100
Fargate:          shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.fargate;fillColor=#ED7100
Auto Scaling:     shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.auto_scaling2;fillColor=#ED7100

## Networking (fillColor=#8C4FFF)
VPC:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.vpc;fillColor=#8C4FFF
CloudFront:       shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudfront;fillColor=#8C4FFF
Route 53:         shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.route_53;fillColor=#8C4FFF
ALB/NLB:          shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_load_balancing;fillColor=#8C4FFF
API Gateway:      shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway;fillColor=#E7157B
NAT Gateway:      shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.nat_gateway;fillColor=#8C4FFF
Transit Gateway:  shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.transit_gateway;fillColor=#8C4FFF
Internet Gateway: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.internet_gateway;fillColor=#8C4FFF

## Database (fillColor=#C925D1)
RDS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;fillColor=#C925D1
Aurora:           shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.aurora;fillColor=#C925D1
DynamoDB:         shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;fillColor=#C925D1
ElastiCache:      shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elasticache;fillColor=#C925D1
Redshift:         shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.redshift;fillColor=#8C4FFF

## Storage (fillColor=#3F8624)
S3:               shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;fillColor=#3F8624
EFS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.efs;fillColor=#3F8624
EBS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ebs;fillColor=#3F8624

## Integration (fillColor=#E7157B)
SQS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sqs;fillColor=#E7157B
SNS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sns;fillColor=#E7157B
EventBridge:      shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eventbridge;fillColor=#E7157B
Step Functions:   shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.step_functions;fillColor=#E7157B

## Security (fillColor=#DD344C)
IAM:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.identity_and_access_management;fillColor=#DD344C
WAF:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.waf;fillColor=#DD344C
Shield:           shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.shield;fillColor=#DD344C
KMS:              shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.key_management_service;fillColor=#DD344C
Secrets Manager:  shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.secrets_manager;fillColor=#DD344C
Certificate Mgr:  shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.certificate_manager;fillColor=#DD344C
GuardDuty:        shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.guardduty;fillColor=#DD344C

## Management (fillColor=#E7157B)
CloudWatch:       shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;fillColor=#E7157B
CloudTrail:       shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudtrail;fillColor=#E7157B
Config:           shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.config;fillColor=#E7157B

## Well-Architected Overlay (custom annotation styles)
Finding-Critical: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.general_AWS_cloud;fillColor=#FF0000;fontColor=#FF0000;strokeColor=#FF0000;dashed=1;dashPattern=5 5
Finding-High:     shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.general_AWS_cloud;fillColor=#FF8C00;fontColor=#FF8C00;strokeColor=#FF8C00;dashed=1;dashPattern=5 5
Finding-Medium:   shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.general_AWS_cloud;fillColor=#FFD700;fontColor=#FFD700;strokeColor=#FFD700;dashed=1;dashPattern=3 3
```

### 6.4 Diagram Layout Strategy

The diagram should be organized as nested containers:

```
┌─ AWS Cloud ──────────────────────────────────────────────────────────────┐
│ ┌─ Region: us-east-1 (PRIMARY) ────────┐  ┌─ Region: us-west-2 (DR) ──┐ │
│ │ ┌─ VPC: Production ───────────────┐  │  │ ┌─ VPC: DR ────────────┐  │ │
│ │ │ ┌─ Public Subnet ──┐            │  │  │ │                      │  │ │
│ │ │ │  ALB  CloudFront  │            │  │  │ │   Read Replica       │  │ │
│ │ │ └──────────────────┘            │  │  │ │   Standby ECS        │  │ │
│ │ │ ┌─ Private Subnet ─┐            │  │  │ └──────────────────────┘  │ │
│ │ │ │  ECS  Lambda      │            │  │  └──────────────────────────┘ │
│ │ │ └──────────────────┘            │  │                                │
│ │ │ ┌─ Data Subnet ────┐            │  │  Global Services:              │
│ │ │ │  RDS  DynamoDB    │            │  │    Route 53                    │
│ │ │ └──────────────────┘            │  │    CloudFront                  │
│ │ └─────────────────────────────────┘  │    WAF                         │
│ └──────────────────────────────────────┘    IAM                         │
│                                                                          │
│ Cross-region connections shown as dashed arrows                          │
│ Data flows shown as solid arrows                                         │
│ Well-Architected findings shown as colored annotation boxes              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Phase 4: Well-Architected Analysis

### 7.1 Strategy

A **read-only sub-agent** using `claude-opus-4-5` reads the unified architecture model
and evaluates it against all six pillars of the AWS Well-Architected Framework.

### 7.2 Six Pillars Evaluation Checklist

The analysis agent checks for:

**Pillar 1: Operational Excellence**
- Are CloudWatch alarms defined for key metrics?
- Is CloudTrail enabled for audit logging?
- Are there automated deployment pipelines (CodePipeline, CodeDeploy)?
- Is AWS Config enabled for configuration compliance?
- Are runbooks or SSM documents defined for incident response?
- Are tags consistent across resources for cost allocation and automation?

**Pillar 2: Security**
- Are security groups following least-privilege (no 0.0.0.0/0 ingress on sensitive ports)?
- Is encryption at rest enabled (RDS, S3, EBS, DynamoDB)?
- Is encryption in transit enforced (TLS, HTTPS-only)?
- Are IAM roles scoped to minimum necessary permissions?
- Is WAF deployed on public-facing endpoints?
- Are secrets in Secrets Manager (not hardcoded or in SSM plaintext)?
- Is GuardDuty enabled?
- Are VPC flow logs enabled?
- Is MFA enforced on IAM users with console access?

**Pillar 3: Reliability**
- Are databases Multi-AZ?
- Are compute services spread across multiple AZs?
- Are Auto Scaling groups configured with appropriate min/max?
- Is there a cross-region DR strategy (read replicas, S3 replication, Route 53 failover)?
- Are health checks configured on load balancers and Route 53?
- Are backups configured (RDS snapshots, DynamoDB PITR, S3 versioning)?
- Are there circuit breakers or retry mechanisms in the application layer?
- What is the Recovery Time Objective (RTO) and Recovery Point Objective (RPO)?

**Pillar 4: Performance Efficiency**
- Are instance types right-sized (not over-provisioned)?
- Is caching used appropriately (ElastiCache, CloudFront, DynamoDB DAX)?
- Are read replicas used to offload read traffic?
- Is the correct compute type used (Lambda vs ECS vs EC2 for the workload)?
- Are S3 storage classes optimized (lifecycle policies)?

**Pillar 5: Cost Optimization**
- Are Reserved Instances or Savings Plans in use?
- Are there resources with no tags (untrackable costs)?
- Are development/staging environments scaled down?
- Is S3 Intelligent-Tiering or lifecycle management configured?
- Are idle resources identifiable (stopped EC2, unused EBS volumes)?
- Is NAT Gateway the right choice vs VPC endpoints for S3/DynamoDB?

**Pillar 6: Sustainability**
- Are Graviton (ARM) instances used where possible?
- Are Lambda functions configured with appropriate memory/timeout?
- Are data retention policies defined?
- Is the architecture designed to minimize data transfer?

### 7.3 Findings Schema

```json
{
  "analysis_date": "2026-03-26T16:00:00Z",
  "overall_score": {
    "operational_excellence": "3/5",
    "security": "2/5",
    "reliability": "2/5",
    "performance_efficiency": "4/5",
    "cost_optimization": "3/5",
    "sustainability": "3/5"
  },
  "findings": [
    {
      "id": "WAF-SEC-001",
      "pillar": "security",
      "severity": "critical",
      "title": "RDS cluster lacks encryption at rest",
      "resource": "aws_rds_cluster.primary",
      "repo": "repo-04-data",
      "region": "us-east-1",
      "description": "The primary RDS Aurora cluster does not have storage_encrypted = true.",
      "impact": "Data at rest is unencrypted; violates compliance requirements.",
      "recommendation": "Enable storage encryption. Requires recreating the cluster with encryption enabled.",
      "effort": "high",
      "aws_doc_reference": "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Overview.Encryption.html",
      "diagram_overlay": {
        "target_cell_id": "rds-primary",
        "annotation_color": "#FF0000",
        "annotation_text": "WAF-SEC-001: No encryption at rest"
      }
    },
    {
      "id": "WAF-REL-001",
      "pillar": "reliability",
      "severity": "high",
      "title": "No cross-region disaster recovery",
      "resource": "global",
      "region": "all",
      "description": "All compute and data resources are in us-east-1 only. No DR region configured.",
      "impact": "A us-east-1 regional outage would cause complete service unavailability.",
      "recommendation": "Implement pilot-light or warm-standby DR in us-west-2.",
      "effort": "very_high",
      "resilience_enhancement": {
        "pattern": "warm-standby",
        "target_region": "us-west-2",
        "components_to_replicate": [
          "aws_rds_cluster.primary (read replica)",
          "aws_ecs_cluster.main (minimal capacity)",
          "aws_lb.api (standby)",
          "Route 53 health check + failover routing"
        ],
        "estimated_additional_cost_monthly": "$2,000-5,000",
        "rto_improvement": "4h → 15min",
        "rpo_improvement": "24h → <1min (Aurora global database)"
      }
    }
  ],
  "resilience_posture": {
    "current_state": {
      "single_region": true,
      "multi_az": "partial",
      "backup_coverage": "60%",
      "estimated_rto": "4-8 hours",
      "estimated_rpo": "24 hours",
      "single_points_of_failure": [
        "aws_rds_cluster.primary (single region)",
        "aws_nat_gateway.main (single AZ)",
        "aws_elasticache_cluster.sessions (no replication)"
      ]
    },
    "target_state": {
      "multi_region": true,
      "multi_az": "full",
      "backup_coverage": "100%",
      "target_rto": "15 minutes",
      "target_rpo": "<1 minute",
      "dr_pattern": "warm-standby"
    },
    "enhancement_phases": [
      {
        "phase": 1,
        "name": "Foundation",
        "effort": "2-4 weeks",
        "actions": [
          "Enable encryption at rest on all data stores",
          "Enable Multi-AZ on RDS and ElastiCache",
          "Add NAT Gateway redundancy (one per AZ)",
          "Enable automated backups with cross-region copy"
        ]
      },
      {
        "phase": 2,
        "name": "Cross-Region DR",
        "effort": "4-8 weeks",
        "actions": [
          "Deploy Aurora Global Database to us-west-2",
          "Configure S3 cross-region replication",
          "Deploy minimal ECS capacity in us-west-2",
          "Configure Route 53 health checks and failover"
        ]
      },
      {
        "phase": 3,
        "name": "Active-Active",
        "effort": "8-12 weeks",
        "actions": [
          "Scale us-west-2 to handle production traffic",
          "Implement DynamoDB Global Tables",
          "Deploy CloudFront with multi-origin failover",
          "Implement cross-region SQS message routing"
        ]
      }
    ]
  }
}
```

---

## 8. Phase 5: Enhancement Overlay & Recommendations

### 8.1 Strategy

A **write-capable sub-agent** reads the Well-Architected findings and the original
draw.io XML. It adds annotation layers to the diagram:

1. **Finding markers**: Colored badges on resources with findings (red=critical, orange=high, yellow=medium)
2. **DR architecture overlay**: Dashed outlines showing where DR resources should be added
3. **Missing connections**: Dashed arrows showing recommended cross-region replication
4. **Enhancement callouts**: Text boxes with phase-numbered improvement recommendations

The agent also produces a standalone `enhancement-roadmap.md` document.

---

## 9. Complete File Implementations

### 9.1 Project Memory — `CLAUDE.md`

```markdown
# AWS Infrastructure Analysis Project

## Purpose
Analyze 30+ Terraform IaC repositories to produce a unified AWS architecture diagram
and Well-Architected Framework assessment.

## Pipeline Phases
1. Extract: one sub-agent per repo → extraction JSON
2. Synthesize: merge all extractions → unified architecture model
3. Diagram: produce draw.io XML with AWS stencils
4. Analyze: Well-Architected Framework review
5. Enhance: overlay findings + resilience roadmap

## Critical Conventions
- All extraction JSONs go to `extractions/<repo-name>.json`
- The unified model goes to `output/unified-architecture.json`
- The diagram goes to `output/aws-architecture.drawio.xml`
- The annotated diagram goes to `output/aws-architecture-annotated.drawio.xml`
- NEVER modify files inside `repos/` — they are read-only source material
- All intermediate artifacts use the schemas defined in the skill files

## Terraform Reading Rules
- Read .tf files directly from disk — this is the ONLY extraction method
- Parse resource, data, module, variable, output, provider, locals, and terraform blocks
- Use grep, find, cat, and Read tool for HCL analysis
- Do NOT attempt to run any terraform CLI commands (init, plan, apply, graph, etc.)
- For private registry modules: infer resources from module name and input variables
- For local-path modules (source = "../modules/..."): read the module's .tf files directly
- Mark inferred data with `"resolution": "inferred"` in the extraction JSON

## AWS Service Taxonomy
When categorizing resources, use these tiers:
- **Edge**: CloudFront, WAF, Shield, Route 53
- **Ingress**: ALB, NLB, API Gateway
- **Compute**: EC2, ECS, EKS, Lambda, Fargate
- **Data**: RDS, Aurora, DynamoDB, ElastiCache, Redshift
- **Storage**: S3, EFS, EBS
- **Integration**: SQS, SNS, EventBridge, Step Functions
- **Security**: IAM, KMS, Secrets Manager, GuardDuty, Security Hub
- **Management**: CloudWatch, CloudTrail, Config, Systems Manager
```

### 9.2 Master Orchestrator Skill — `.claude/skills/analyze-aws-infra/SKILL.md`

```yaml
---
name: analyze-aws-infra
description: >
  Master orchestrator for AWS infrastructure analysis. Runs the full 5-phase pipeline:
  extract all repos, synthesize unified model, generate draw.io diagram, apply
  Well-Architected Framework, and overlay findings with enhancement roadmap.
argument-hint: "[phase: all|extract|synthesize|diagram|analyze|enhance] [repo-filter: all|repo-name]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash
---

Execute AWS infrastructure analysis pipeline: $ARGUMENTS

## Phase 0: Discover Repositories

1. Scan the `repos/` directory to find all Terraform repositories
2. For each subdirectory, check if it contains `.tf` files
3. Detect per-repo metadata:
   - Repo name (directory name)
   - Number of .tf files
   - Provider blocks found (AWS regions used)
   - Whether repo uses local modules (fully analyzable) or registry modules (inferred)
   - Whether repo reads remote state from other repos (cross-repo dependency)
   - Approximate complexity (file count + resource count via grep)
4. Write `repo-manifest.json`:
   ```json
   {
     "discovered_at": "...",
     "repos_path": "repos/",
     "total_repos": 32,
     "repos": [
       {
         "name": "networking-core",
         "path": "repos/networking-core",
         "tf_file_count": 12,
         "estimated_resource_count": 45,
         "detected_regions": ["us-east-1", "us-west-2"],
         "has_remote_state": true,
         "has_local_modules": true,
         "has_registry_modules": true
       }
     ]
   }
   ```
5. Create `extractions/` and `output/` directories if they don't exist
6. Report: discovered N repos, estimated total resources, detected AWS regions

## Phase 1: Extract (Map across repos)

7. Read `repo-manifest.json` to get the list of repositories
8. For each repo in the manifest:
   a. Check if `extractions/<repo-name>.json` already exists (skip if present and $1 != "extract")
   b. Invoke the `tf-repo-extractor` sub-agent with:
      - Repo path from manifest
      - Output path: `extractions/<repo-name>.json`
   c. After each extraction, the PostToolUse hook validates the JSON schema
9. Report: X of N repos extracted successfully

## Phase 2: Synthesize (Reduce)

10. Invoke the `architecture-synthesizer` sub-agent with:
   - Input: all files in `extractions/`
   - Repo manifest: `repo-manifest.json` (for cross-reference resolution)
   - Output: `output/unified-architecture.json`
11. The synthesizer resolves cross-repo references, deduplicates, and builds
   the service map, dependency graph, and blast radius map

## Phase 3: Diagram

12. Invoke the `drawio-generator` sub-agent with:
   - Input: `output/unified-architecture.json`
   - Output: `output/aws-architecture.drawio.xml`
   - Reference: AWS stencil styles from `.claude/skills/analyze-aws-infra/aws-stencils.md`
13. PostToolUse hook validates XML well-formedness

## Phase 4: Analyze

14. Invoke the `well-architected-analyzer` sub-agent with:
   - Input: `output/unified-architecture.json`
   - Output: `output/well-architected-report.md` and `output/well-architected-findings.json`
15. The analyzer evaluates all 6 pillars and produces scored findings

## Phase 5: Enhance

16. Invoke the `enhancement-overlayer` sub-agent with:
    - Inputs: `output/aws-architecture.drawio.xml` + `output/well-architected-findings.json`
    - Outputs: `output/aws-architecture-annotated.drawio.xml` + `output/enhancement-roadmap.md`
17. Present the complete results to the user:
    - Link to diagram file (importable to draw.io and Lucidchart)
    - Well-Architected score summary
    - Top 5 critical findings
    - Resilience enhancement roadmap (phased)
```

### 9.3 Discovery Skill — `.claude/skills/discover-repos/SKILL.md`

```yaml
---
name: discover-repos
description: >
  Scans the repos/ directory to discover all Terraform repositories, validates
  them, detects initialization status, and generates repo-manifest.json.
  Run this before the first extraction, or after adding new repositories.
argument-hint: "[repos-path: default repos/]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Discover Terraform repositories in: $ARGUMENTS

Default path: `repos/` if no argument provided.

## Discovery Steps

1. List all subdirectories in the repos path:
   `find repos/ -maxdepth 1 -mindepth 1 -type d | sort`

2. For each subdirectory, validate it is a Terraform repo:
   `find <dir> -name "*.tf" -maxdepth 2 | head -1`
   Skip directories with no .tf files.

3. For each valid repo, gather metadata:
   - `tf_file_count`: `find <dir> -name "*.tf" | wc -l`
   - `estimated_resource_count`: `grep -rc "^resource " <dir>/*.tf 2>/dev/null | awk -F: '{s+=$2} END {print s}'`
   - `detected_regions`: `grep -h "region" <dir>/*.tf | grep -oP '"[a-z]{2}-[a-z]+-\d+"' | sort -u`
   - `has_remote_state`: `grep -l "terraform_remote_state" <dir>/*.tf` (indicates cross-repo deps)
   - `has_modules`: `grep -l "^module " <dir>/*.tf` (indicates module usage)
   - `has_local_modules`: check if any module source starts with `./` or `../` (fully analyzable)
   - `has_registry_modules`: check if any module source references a registry (inferred only)
   - `detected_backends`: `grep -A5 'backend "' <dir>/*.tf` (S3, remote, etc.)

4. Write `repo-manifest.json` with all discovered metadata.

5. Create directories: `mkdir -p extractions output`

6. Report summary:
   - Total repos discovered
   - Repos with cross-repo dependencies (remote state)
   - Repos with local modules (fully analyzable) vs registry modules (inferred)
   - Estimated total resource count across all repos
   - Detected AWS regions
```

### 9.4 Sub-agent — `.claude/agents/tf-repo-extractor.md`

```yaml
---
name: tf-repo-extractor
description: >
  Analyzes a single Terraform repository by reading .tf files directly from disk.
  Extracts all AWS resources, networking topology, cross-repo references, and
  resilience indicators into a structured JSON file. Read-only — never modifies
  the repository. Does not use the Terraform CLI.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 25
---

You are a Terraform HCL analyst. Extract the complete AWS architecture from
the repository at the provided path by reading .tf files directly.

You do NOT have access to the Terraform CLI. Do not attempt to run terraform
commands. All analysis is done by reading HCL files and using grep/find/cat.

## Extraction Procedure

### Step 1: Inventory
- Run `find <repo-path> -name "*.tf" -type f | sort` to list all Terraform files
- Run `find <repo-path> -name "*.tfvars" -type f | sort` for variable files
- Run `wc -l <repo-path>/*.tf` to gauge complexity
- If the repo has subdirectories with .tf files, include those too:
  `find <repo-path> -name "*.tf" -type f`

### Step 2: Provider Analysis
- Read files likely to contain providers: `versions.tf`, `providers.tf`, `main.tf`
- `grep -n "provider\s*\"aws\"" <repo-path>/*.tf` to find all AWS provider blocks
- For each provider block, extract: region, alias, version constraint
- If region is set via variable (e.g., `region = var.aws_region`), check
  `variables.tf` and `.tfvars` files for the default value

### Step 3: Resource Extraction
Read every .tf file. For each `resource "aws_*"` block:
- Record the resource type, name, and full address (e.g., `aws_vpc.main`)
- Map it to the correct provider alias (and thus region) via the `provider` argument
- Extract key attributes: CIDR blocks, instance types, encryption settings,
  engine versions, storage sizes, multi-AZ flags
- Extract tags
- Parse HCL references to other resources:
  - `aws_subnet.main.id` → this resource depends on `aws_subnet.main`
  - `module.vpc.vpc_id` → this resource depends on module "vpc"
  - `data.aws_ami.latest.id` → this resource depends on data source "aws_ami.latest"
  - `var.vpc_id` → dependency via variable (note but cannot resolve across repos)

### Step 4: Module Analysis
For each `module` block:
- Record `source` and `version`
- If source is a **relative path** (starts with `./` or `../`):
  Read the module's .tf files from that path and extract its resources recursively
- If source is a **registry path** (e.g., `terraform-aws-modules/vpc/aws` or
  `app.terraform.io/org/module/aws`):
  Infer resources from the module name using these conventions:
  - `*/vpc/*` → aws_vpc, aws_subnet, aws_internet_gateway, aws_nat_gateway, aws_route_table
  - `*/ecs/*` → aws_ecs_cluster, aws_ecs_service, aws_ecs_task_definition
  - `*/rds/*` → aws_rds_cluster or aws_db_instance (check inputs for `engine`)
  - `*/eks/*` → aws_eks_cluster, aws_eks_node_group
  - `*/alb/*` or `*/elb/*` → aws_lb, aws_lb_target_group, aws_lb_listener
  - `*/s3/*` → aws_s3_bucket, aws_s3_bucket_policy
  - `*/lambda/*` → aws_lambda_function, aws_lambda_permission
  - `*/cloudfront/*` → aws_cloudfront_distribution
  Mark inferred modules with `"resolution": "inferred"` in the output
- Record all input variables passed to the module (these reveal configuration intent)

### Step 5: Data Source Analysis
For each `data` block:
- Record type, name, and what it looks up
- Pay special attention to:
  - `data.terraform_remote_state.*` → cross-repo dependency (extract backend config)
  - `data.aws_ssm_parameter.*` → cross-repo data sharing (extract parameter name)
  - `data.aws_caller_identity.*` → account context
  - `data.aws_region.*` → region context

### Step 6: Networking Topology
Build a denormalized view of the VPC topology:
- VPCs with CIDR blocks
- Subnets grouped by public/private/data (infer from tags, names, or route table associations)
- NAT Gateways, Internet Gateways
- VPC Peering connections, Transit Gateways
- Route 53 zones and records
- VPN connections, Direct Connect

### Step 7: Cross-repo References
Identify how this repo depends on or is depended upon by others:
- `terraform_remote_state` data sources → extract backend bucket/key to identify source repo
- `aws_ssm_parameter` data sources → extract parameter name path
- Output values → what does this repo export for others to consume?
- Shared resource ARNs referenced via variables or data sources

### Step 8: Resilience Indicators
Pre-compute these flags by checking resource attributes:
- `multi_az`: Look for `multi_az = true`, `availability_zones` with 2+ entries,
  subnet spread across AZs
- `multi_region`: Multiple provider aliases with different regions
- `backup_configured`: `backup_retention_period > 0`, `point_in_time_recovery` enabled,
  S3 versioning enabled
- `health_checks`: `health_check` blocks in LB target groups, Route 53 health checks
- `encryption_at_rest`: `storage_encrypted = true`, `kms_key_id` present,
  `server_side_encryption_configuration` on S3

### Step 9: Write Output
Write the extraction to the provided output path using the schema defined
in the project documentation. Validate JSON is well-formed before writing.

## Important Rules
- NEVER attempt to run terraform CLI commands — you do not have access
- NEVER modify any file in the repository
- If a .tf file is too large to read fully, use grep to extract resource blocks first:
  `grep -n "^resource\|^data\|^module\|^output\|^variable" <file>`
  Then read specific sections with line ranges
- When an attribute references a variable with no default, record it as `"<variable>"`
- When a count/for_each uses a variable, note the expression (e.g., `"count": "var.instance_count"`)
- When in doubt about a resource attribute, include it with a "?" suffix in the value
```

### 9.5 Sub-agent — `.claude/agents/architecture-synthesizer.md`

```yaml
---
name: architecture-synthesizer
description: >
  Reads all per-repo extraction JSON files and produces a unified AWS architecture
  model. Resolves cross-repo dependencies, deduplicates resources, and builds
  the service map, dependency graph, and blast radius map. Read-only.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 30
---

You are an AWS solutions architect synthesizing a unified view from multiple
Terraform repository analyses.

## Synthesis Procedure

### Step 1: Load All Extractions
Read every `.json` file in `extractions/`. Parse each into the extraction schema.
Create an in-memory inventory of all resources across all repos.

### Step 2: Resolve Cross-Repo Dependencies
For each `remote_state_reads` entry, find the matching repo's `outputs`.
For each `ssm_parameter_reads`, find which repo writes that parameter.
Build a repo-to-repo dependency graph.

### Step 3: Deduplicate
The same resource may appear in multiple extractions (if repos share modules
or reference the same remote state). Deduplicate by resource address.
Keep the most complete version (most attributes extracted).

### Step 4: Build Topology
Organize all resources into the region → VPC → subnet hierarchy.
Map cross-VPC connections (peering, transit gateway).
Map cross-region connections (replication, read replicas, Route 53 failover).

### Step 5: Build Service Map
Classify every resource into an architectural tier (edge/ingress/compute/data/
integration/security/management). Identify request flows by tracing from
edge resources through load balancers to compute to data stores.

### Step 6: Dependency Graph
Build a complete dependency graph where edges represent:
- Network dependency (resource in subnet of VPC)
- Data dependency (service reads from database)
- Security dependency (resource uses IAM role/security group)
- Integration dependency (Lambda triggered by SQS)

### Step 7: Blast Radius Analysis
For each critical resource, compute:
- Direct dependents (what fails immediately if this resource fails?)
- Transitive dependents (what fails as a consequence?)
- Blast radius classification: critical / high / medium / low

### Step 8: Write Unified Model
Write the unified model to `output/unified-architecture.json`.
This is the SINGLE SOURCE OF TRUTH for all downstream phases.
```

### 9.6 Sub-agent — `.claude/agents/drawio-generator.md`

```yaml
---
name: drawio-generator
description: >
  Produces a draw.io XML diagram from the unified AWS architecture model.
  Uses AWS Architecture 2024 stencils. The diagram must be importable into
  both draw.io and Lucidchart.
model: claude-opus-4-5
tools:
  - Read
  - Write
  - Bash
disallowedTools:
  - Edit
  - MultiEdit
maxTurns: 30
---

You are a diagram generation specialist. Produce a draw.io XML file
representing the complete AWS architecture.

## Layout Rules

1. **Outermost container**: AWS Cloud boundary (grIcon=group_aws_cloud)
2. **Second level**: One Region container per region, arranged left-to-right.
   Primary region is largest and leftmost.
3. **Third level**: VPC containers within each region.
4. **Fourth level**: Subnet containers (public=green tint, private=blue tint,
   data=purple tint) within each VPC, arranged top-to-bottom by tier.
5. **Resources**: Placed inside their containing subnet/VPC using the correct
   AWS stencil style from `.claude/skills/analyze-aws-infra/aws-stencils.md`
6. **Global services** (CloudFront, Route 53, WAF, IAM): Placed outside
   region containers but inside the AWS Cloud boundary, in a "Global Services"
   area at the top.
7. **Connections**: Solid arrows for data flow, dashed arrows for cross-region
   replication, dotted arrows for async messaging.

## Sizing Guidelines
- Page size: 3300 x 2540 (landscape, fits well in draw.io and Lucidchart)
- Resource icons: 60x60 px
- Group containers: calculated based on content
- Minimum spacing: 40px between resources, 20px padding inside containers
- Font: 12px for resource labels, 14px bold for container labels

## ID Convention
Every mxCell id should be the resource address with dots replaced by dashes:
- `aws_vpc.main` → id="aws-vpc-main"
- `aws_rds_cluster.primary` → id="aws-rds-cluster-primary"
This enables the enhancement overlay phase to find cells by resource address.

## Connection Edges
For each edge in the dependency graph:
- Create an mxCell with `edge="1"`
- Set source and target to the resource cell IDs
- Use `edgeStyle=orthogonalEdgeStyle;rounded=1` for clean routing
- Label critical connections with the dependency type

## Output
Write the complete XML to `output/aws-architecture.drawio.xml`.
The file must be valid XML and importable into draw.io and Lucidchart.

Verify the XML is well-formed by reading it back and checking for syntax errors.
```

### 9.7 Sub-agent — `.claude/agents/well-architected-analyzer.md`

```yaml
---
name: well-architected-analyzer
description: >
  Evaluates the unified AWS architecture against all six pillars of the
  AWS Well-Architected Framework. Produces scored findings with specific
  remediation recommendations. Read-only.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 25
---

You are an AWS Well-Architected Framework specialist. Analyze the unified
architecture model and produce a comprehensive assessment.

Read `output/unified-architecture.json` and evaluate against all 6 pillars.

## For Each Pillar

Score 1-5 based on:
- 5: Exemplary. All best practices followed. No findings.
- 4: Good. Minor findings only. Low risk.
- 3: Acceptable. Some gaps. Medium risk.
- 2: Concerning. Significant gaps. High risk.
- 1: Critical. Major architectural weaknesses. Immediate action required.

## For Each Finding

Produce a finding with:
- Unique ID (WAF-<PILLAR>-<NNN>)
- Severity (critical/high/medium/low)
- Affected resource(s) with addresses matching the diagram cell IDs
- Description of the issue
- Business impact
- Specific remediation steps
- Effort estimate (low/medium/high/very_high)
- Link to relevant AWS documentation

## Resilience Posture Assessment

Specifically assess:
1. What is the current RTO/RPO?
2. What are the single points of failure?
3. What would happen in a single-AZ failure? Single-region failure?
4. What is the recommended DR pattern (backup-restore / pilot-light / warm-standby / active-active)?
5. Produce a phased enhancement roadmap from current state to target resilience posture

## Multi-Region Analysis

If the architecture is single-region:
- Identify which components MUST be replicated for DR
- Identify which can use passive replication vs active-active
- Estimate additional cost for each DR tier
- Recommend the minimum viable DR configuration

If already multi-region:
- Assess whether the multi-region strategy is complete
- Identify gaps (e.g., database replicated but cache not)
- Evaluate failover mechanisms (Route 53 health checks, Global Accelerator)

## Output

Write two files:
1. `output/well-architected-report.md` — Human-readable report with executive summary
2. `output/well-architected-findings.json` — Machine-readable findings for diagram overlay
```

### 9.8 Sub-agent — `.claude/agents/enhancement-overlayer.md`

```yaml
---
name: enhancement-overlayer
description: >
  Reads Well-Architected findings and overlays them on the draw.io diagram
  as colored annotations. Also produces the final enhancement roadmap document.
model: claude-opus-4-5
tools:
  - Read
  - Write
  - Bash
disallowedTools:
  - MultiEdit
maxTurns: 20
---

Overlay Well-Architected findings on the architecture diagram.

## Step 1: Read Inputs
- Read `output/aws-architecture.drawio.xml` (base diagram)
- Read `output/well-architected-findings.json` (findings with resource references)

## Step 2: Add Finding Annotations
For each finding:
1. Find the target mxCell by matching the resource address to the cell ID
   (dots replaced by dashes: `aws_rds_cluster.primary` → `aws-rds-cluster-primary`)
2. Add an annotation mxCell adjacent to the resource:
   - Critical: red border, red text, finding ID
   - High: orange border, orange text
   - Medium: yellow border, yellow text
3. Add a tooltip (via `tooltip` attribute) with the finding description

## Step 3: Add DR Overlay
If the findings recommend cross-region DR:
1. Add a dashed-outline region container for the DR region
2. Add ghost resources (dashed borders) showing what should be deployed
3. Add dashed arrows for replication connections
4. Label each ghost resource with the enhancement phase number

## Step 4: Add Legend
Add a legend box in the bottom-right corner:
- Red badge = Critical finding
- Orange badge = High finding
- Yellow badge = Medium finding
- Dashed resource = Recommended addition
- Phase numbers = Enhancement roadmap phase

## Step 5: Write Outputs
1. `output/aws-architecture-annotated.drawio.xml` — Diagram with all overlays
2. `output/enhancement-roadmap.md` — Prioritized roadmap document with:
   - Executive summary
   - Current vs target resilience posture
   - Phase 1: Quick wins (1-2 weeks)
   - Phase 2: Foundation (2-4 weeks)
   - Phase 3: Cross-region DR (4-8 weeks)
   - Phase 4: Active-active (8-12 weeks)
   - Cost estimates per phase
   - Risk reduction per phase
```

### 9.9 Hooks

**`.claude/hooks/validate-extraction-json.sh`**
```bash
#!/usr/bin/env bash
# PostToolUse: validates extraction JSON schema after Write to extractions/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only validate extraction files
if [[ "$file_path" != extractions/*.json ]]; then
  exit 0
fi

# Check JSON is valid
if ! jq empty "$file_path" 2>/dev/null; then
  echo '{"reason": "Invalid JSON in '"$file_path"'. Fix syntax before proceeding."}' >&2
  exit 2
fi

# Check required top-level fields
required_fields=("repo_name" "providers" "resources" "networking" "cross_repo_references")
for field in "${required_fields[@]}"; do
  if ! jq -e ".$field" "$file_path" > /dev/null 2>&1; then
    echo "{\"reason\": \"Missing required field '$field' in $file_path\"}" >&2
    exit 2
  fi
done

exit 0
```

**`.claude/hooks/validate-drawio-xml.sh`**
```bash
#!/usr/bin/env bash
# PostToolUse: validates draw.io XML well-formedness after Write to output/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

if [[ "$file_path" != output/*.drawio.xml ]]; then
  exit 0
fi

# Check XML is well-formed using python3
if ! python3 -c "import xml.etree.ElementTree as ET; ET.parse('$file_path')" 2>/dev/null; then
  echo '{"reason": "Malformed XML in '"$file_path"'. Fix before proceeding."}' >&2
  exit 2
fi

exit 0
```

### 9.10 Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(find repos/*)",
      "Bash(find repos/* -name *.tf)",
      "Bash(find repos/* -name *.tfvars)",
      "Bash(find repos/* -maxdepth 1 -mindepth 1 -type d)",
      "Bash(cat repos/*)",
      "Bash(grep * repos/*)",
      "Bash(grep -rn * repos/)",
      "Bash(grep -rc * repos/)",
      "Bash(grep -rh * repos/)",
      "Bash(grep -rl * repos/)",
      "Bash(grep -l * repos/)",
      "Bash(grep -h * repos/)",
      "Bash(wc -l *)",
      "Bash(sort *)",
      "Bash(ls repos/)",
      "Bash(ls extractions/)",
      "Bash(cat extractions/*)",
      "Bash(cat output/*)",
      "Bash(cat repo-manifest.json)",
      "Bash(jq * extractions/*)",
      "Bash(jq * output/*)",
      "Bash(jq * repo-manifest.json)",
      "Bash(mkdir -p extractions)",
      "Bash(mkdir -p output)",
      "Bash(python3 -c *)"
    ],
    "deny": [
      "Bash(terraform *)",
      "Bash(rm -rf repos/*)",
      "Bash(rm -rf /:*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-extraction-json.sh"
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-drawio-xml.sh"
          }
        ]
      }
    ]
  }
}
```

---

## 10. Execution Playbook

### 10.1 First Run: Complete Pipeline

```
1. cd ~/aws-architecture-analysis  (or wherever your repos/ directory is)
2. Verify repos are in place: ls repos/
3. Open Claude Code in this directory
4. Run: /discover-repos
   → Generates repo-manifest.json with all discovered repo metadata
   → Review the summary: number of repos, regions detected, estimated complexity
5. Run: /analyze-aws-infra all
   → Runs phases 1-5 automatically (~30-60 minutes for 30+ repos)
6. Open output/aws-architecture-annotated.drawio.xml in draw.io or import to Lucidchart
7. Review output/well-architected-report.md
8. Review output/enhancement-roadmap.md
```

### 10.2 Running Individual Phases

You can run any phase independently:

```
# Re-discover repos (e.g., after adding new repos to repos/)
/discover-repos

# Re-extract a single repo (e.g., after it changed)
/extract-repo networking-core

# Re-run phases 2-5 with existing extractions (e.g., after re-extracting one repo)
/analyze-aws-infra synthesize

# Just regenerate the diagram (e.g., after tweaking layout preferences)
/generate-diagram

# Just re-run Well-Architected review (e.g., after updating the architecture)
/well-architected-review
```

### 10.3 Adding New Repositories

When new repos are added to the `repos/` directory:

```
1. Clone or copy the new repo into repos/
2. Run: /discover-repos         (updates repo-manifest.json)
3. Run: /extract-repo <new-repo-name>
4. Run: /analyze-aws-infra synthesize   (re-runs phases 2-5 with the new extraction)
```

### 10.4 Handling Large Repos

If a repo has 100+ .tf files and overwhelms the extraction agent's context:

1. The extraction agent should use Bash preprocessing:
   ```bash
   # Extract just resource blocks with their types
   grep -rn "^resource\|^data\|^module" repos/<repo>/*.tf
   ```
2. Then read individual files for detail on the most important resources
3. The `maxTurns: 25` limit ensures the agent doesn't spin indefinitely

### 10.5 Handling Private Modules

If repos use private Terraform modules (e.g., from a private registry):
- The extraction agent reads the module source path and version
- It infers created resources from the module name (e.g., `terraform-aws-modules/vpc/aws` → VPC, subnets, NAT GW)
- For custom internal modules, it reads the module's source directory if available
- Unresolvable modules are logged with `"resources_created": ["unknown"]`

---

## 11. Token Cost Strategy

| Component | Token Cost | Frequency | Total for 30 Repos |
|-----------|-----------|-----------|---------------------|
| `CLAUDE.md` | ~500 tokens | Always-on | 500 (fixed) |
| Master skill description | ~60 tokens | Always in context | 60 (fixed) |
| Per-repo extraction agent | ~800 tokens per invocation | 30× (one per repo) | 24,000 |
| Synthesis agent | ~600 tokens + reads all JSONs | 1× | ~5,000 (varies by total resource count) |
| Diagram generator | ~600 tokens + reads unified model | 1× | ~4,000 |
| Well-Architected analyzer | ~800 tokens + reads unified model | 1× | ~5,000 |
| Enhancement overlayer | ~600 tokens + reads diagram + findings | 1× | ~4,000 |
| Hooks | 0 tokens | Every tool call | 0 |
| **Estimated total** | | | **~40,000 tokens** |

The key cost optimization: **each extraction agent starts fresh**. It doesn't accumulate
context from previous repos. This is the fundamental advantage of the sub-agent isolation
model — repo #30 costs the same as repo #1.

---

## Appendix: Quick-Start Checklist

- [ ] Verify all repos are in the `repos/` directory: `ls repos/`
- [ ] Install `jq` (required for hooks): `jq --version`
- [ ] Verify `python3` is available (for XML validation hook): `python3 --version`
- [ ] Copy all `.claude/` files into place
- [ ] Run `/discover-repos` to generate `repo-manifest.json`
- [ ] Review manifest: number of repos, detected regions, estimated complexity
- [ ] Run `/analyze-aws-infra all` to execute the full pipeline
- [ ] Import `output/aws-architecture-annotated.drawio.xml` into draw.io or Lucidchart
- [ ] Review `output/well-architected-report.md`
- [ ] Review `output/enhancement-roadmap.md` with your team
- [ ] Prioritize Phase 1 quick wins from the roadmap

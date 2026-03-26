# AWS Infrastructure Analysis & Well-Architected Review

## GitHub Copilot Customization Architecture — Applied to Multi-Repo Terraform Analysis

---

## Executive Summary

This document defines the complete **GitHub Copilot customization architecture** for analyzing
30+ Terraform IaC repositories, producing a unified AWS architecture diagram in draw.io XML
format (with AWS stencils, importable to Lucidchart), and applying the AWS Well-Architected
Framework to identify weaknesses and resilience enhancement opportunities — including
multi-region posture.

The workflow is a **five-phase pipeline** using a **map-reduce** pattern across repositories,
implemented with GitHub Copilot's Custom Agents (sub-agent pattern), Agent Skills, Prompt Files,
and Hooks — each playing the role it was designed for.

### Component Mapping: Claude Code → GitHub Copilot

| Claude Code Component | GitHub Copilot Equivalent | Notes |
|---|---|---|
| `CLAUDE.md` (global rules) | `.github/copilot-instructions.md` | Always-on; keep to 5–15 rules |
| `CLAUDE.md` (operational procedures) | `AGENTS.md` | Agent-scoped operational guidance |
| `.claude/agents/*.md` | `.github/agents/*.agent.md` | Sub-agent invocation pattern |
| `disallowedTools: [Write, Edit]` | Omit write tools from `tools:` whitelist | GitHub Copilot is whitelist-only |
| `tools: [Read, Bash]` | `tools: ['codebase', 'terminalLastCommand']` | Different tool naming |
| `maxTurns: N` | No direct equivalent | Rely on agent prompt design |
| `permissionMode: bypassPermissions` | No equivalent; use sub-agent isolation | Sub-agents run in isolated contexts |
| `.claude/skills/` | `.github/skills/` | Same SKILL.md format (open standard) |
| `.claude/commands/*.md` | `.github/prompts/*.prompt.md` | User-triggered via `#file:` or `/` |
| `.claude/settings.json` (hooks) | `.vscode/settings.json` | Hook configuration location |
| `exit 2` to block a tool | Hook command returns non-zero exit code | Blocking mechanism |
| `PostToolUse` hook | `postToolUse` hook | Same concept; different config format |

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
collectively contain tens of thousands of lines of HCL. No single context window can hold
all of it simultaneously. The GitHub Copilot architecture solves this through its sub-agent
isolation model.

**Why sub-agents and not handoffs?** The five pipeline phases are fully automated — no human
review checkpoint is needed between extraction and synthesis, or between synthesis and
diagramming. The sub-agent pattern (parent delegates programmatically; user sees only the
final result) is the correct mechanism. Handoffs are for pipelines where a human must
approve each stage before proceeding.

| Concern | Component | Why |
|---|---|---|
| Per-repo Terraform analysis | **Sub-agent** (read-only tools only) | Each repo gets an isolated context; no cross-contamination |
| Full pipeline orchestration | **Parent Custom Agent** (`tools: ['agent']`) | Delegates to sub-agents programmatically |
| draw.io XML generation | **Sub-agent** (write-capable, isolated) | Specialized XML knowledge; doesn't need Terraform context |
| Well-Architected analysis | **Sub-agent** (read-only, isolated) | Needs the unified model, not the raw Terraform |
| Detailed task procedures | **Agent Skills** (on-demand) | Loaded only when the orchestrator matches the task; saves tokens |
| User-triggered pipeline execution | **Prompt Files** (`/analyze-aws-infra`) | Explicitly invoked; not always-on |
| JSON/XML schema validation | **`postToolUse` Hooks** | Deterministic code; zero tokens; runs unconditionally |
| Project conventions + taxonomy | **`copilot-instructions.md`** | Always-on; ≤15 rules |
| Operational build/test steps | **`AGENTS.md`** | Loaded when a coding agent operates |

> **Architectural anti-pattern avoided:** The workflow orchestration logic (invoke extractor
> for each repo → synthesize → diagram → analyze → enhance) lives entirely in the parent
> Custom Agent's prompt — not in `copilot-instructions.md`. The instructions file contains
> only stable, always-relevant project standards. See section 6.1 of the reference
> architecture for why this matters.

---

## 2. Prerequisites and Preparation

### 2.1 Repository Layout

All 30+ Terraform repositories must be cloned locally under a `repos/` directory before
running the pipeline. The parent orchestrator's first sub-task (Phase 0) scans this
directory and builds `repo-manifest.json`. No manual steps are required beyond confirming
the repos are present:

```bash
ls repos/
```

### 2.2 No Terraform CLI Required

This pipeline operates entirely by reading `.tf` files from disk via the agent's
`codebase` and `terminalLastCommand` tools. It does **not** require `terraform init`,
`terraform plan`, or network access to Terraform registries.

### 2.3 Tool Requirements on Host

| Tool | Required | Purpose |
|---|---|---|
| `jq` | **Yes** | `postToolUse` hook validates extraction JSON |
| `python3` | **Yes** | `postToolUse` hook validates draw.io XML well-formedness |
| `grep`, `find`, `cat`, `sort` | **Yes** (standard Unix) | Extraction sub-agent uses these via `terminalLastCommand` |

### 2.4 GitHub Copilot Sub-agent Constraints (Architecture Reference)

Per the GitHub Copilot sub-agent design:

- Sub-agents run in **isolated contexts** — they do not see the parent agent's full
  conversation history, only the instructions passed to them. This is the mechanism
  that prevents context overflow across 30+ repos.
- Sub-agents **cannot invoke other sub-agents** (single-level depth only). The parent
  orchestrator must invoke each specialist sub-agent directly; sub-agents cannot
  chain invocations.
- Sub-agents can use **different models** — the extraction workers can use a lighter
  model while the synthesis and analysis agents use a more capable one.

---

## 3. Project Structure

```
aws-architecture-analysis/
├── .github/
│   ├── copilot-instructions.md             ← Always-on: project standards (≤15 rules)
│   ├── agents/
│   │   ├── aws-pipeline-orchestrator.agent.md  ← Parent agent: tools=['agent']; owns full pipeline
│   │   ├── tf-repo-extractor.agent.md          ← Sub-agent: read-only Terraform HCL analyst
│   │   ├── architecture-synthesizer.agent.md   ← Sub-agent: read-only synthesis/reduce
│   │   ├── drawio-generator.agent.md            ← Sub-agent: write-capable XML diagram producer
│   │   ├── well-architected-analyzer.agent.md  ← Sub-agent: read-only WAF reviewer
│   │   └── enhancement-overlayer.agent.md      ← Sub-agent: write-capable findings overlay
│   ├── skills/
│   │   ├── analyze-aws-infra/
│   │   │   ├── SKILL.md                    ← Full pipeline skill (loaded by orchestrator)
│   │   │   └── references/
│   │   │       └── aws-stencils.md         ← draw.io stencil reference (on-demand)
│   │   ├── discover-repos/
│   │   │   └── SKILL.md                    ← Phase 0: repo discovery skill
│   │   ├── extract-single-repo/
│   │   │   └── SKILL.md                    ← Single-repo extraction (for reruns)
│   │   ├── generate-diagram/
│   │   │   └── SKILL.md                    ← Diagram generation only
│   │   └── well-architected-review/
│   │       └── SKILL.md                    ← WAF analysis only
│   └── prompts/
│       ├── analyze-aws-infra.prompt.md     ← /analyze-aws-infra slash command (full pipeline)
│       ├── discover-repos.prompt.md        ← /discover-repos
│       ├── extract-repo.prompt.md          ← /extract-repo [repo-name]
│       ├── generate-diagram.prompt.md      ← /generate-diagram
│       └── well-architected-review.prompt.md  ← /well-architected-review
├── .vscode/
│   └── settings.json                       ← Hooks configuration + Copilot settings
├── .github/
│   └── hooks/
│       ├── validate-extraction-json.sh     ← postToolUse: validates extraction JSON schema
│       └── validate-drawio-xml.sh          ← postToolUse: validates draw.io XML well-formedness
├── AGENTS.md                               ← Operational guidance for autonomous agent operation
├── repos/                                  ← EXISTING: your 30+ Terraform repos (read-only source)
│   ├── networking-core/
│   ├── compute-platform/
│   └── ...
├── repo-manifest.json                      ← Phase 0 output: discovered repo metadata
├── extractions/                            ← Phase 1 output: one JSON per repo
│   ├── networking-core.json
│   └── ...
└── output/
    ├── unified-architecture.json           ← Phase 2 output: merged model
    ├── aws-architecture.drawio.xml         ← Phase 3 output: importable diagram
    ├── well-architected-report.md          ← Phase 4 output: WAF findings
    ├── well-architected-findings.json      ← Phase 4 output: machine-readable findings
    ├── aws-architecture-annotated.drawio.xml  ← Phase 5 output: diagram with overlays
    └── enhancement-roadmap.md              ← Phase 5 output: phased recommendations
```

---

## 4. Phase 1: Repository Extraction (Map)

### 4.1 Strategy

The parent orchestrator fans out one **read-only sub-agent** invocation per repository.
Because each sub-agent runs in an **isolated context**, repo #30 costs the same as repo #1 —
there is no context accumulation across extractions. This is the fundamental advantage of
the sub-agent isolation model.

Each `tf-repo-extractor` sub-agent:

1. Uses `terminalLastCommand` to run `find`, `grep`, `cat` against the repo's `.tf` files
2. Parses every `resource`, `data`, `module`, `variable`, `output`, and `provider` block
3. Extracts AWS resources, data sources, module references, and inter-resource relationships
4. Identifies networking topology, multi-region patterns, and cross-repo references
5. Writes a structured JSON extraction file to `extractions/<repo-name>.json`

### 4.2 Extraction JSON Schema

Every extraction MUST conform to this schema. The synthesis sub-agent depends on it,
and the `postToolUse` hook validates it on every write.

```json
{
  "repo_name": "networking-core",
  "repo_path": "repos/networking-core",
  "extracted_at": "2026-03-26T12:00:00Z",
  "terraform_version": "1.7.0",
  "providers": [
    {
      "name": "aws",
      "alias": "us-east-1",
      "region": "us-east-1",
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
        "enable_dns_support": true
      },
      "tags": { "Name": "production-vpc", "Environment": "production" },
      "references_to": [],
      "referenced_by": ["aws_subnet.public_a", "aws_subnet.private_a"]
    }
  ],
  "data_sources": [],
  "modules": [
    {
      "name": "vpc",
      "source": "terraform-aws-modules/vpc/aws",
      "version": "5.1.0",
      "resolution": "inferred",
      "resources_created": ["aws_vpc", "aws_subnet", "aws_internet_gateway", "aws_nat_gateway"],
      "input_variables": { "cidr": "10.0.0.0/16", "azs": ["us-east-1a", "us-east-1b"] }
    }
  ],
  "outputs": [],
  "networking": {
    "vpcs": [
      {
        "resource_address": "aws_vpc.main",
        "cidr": "10.0.0.0/16",
        "region": "us-east-1",
        "subnets": {
          "public": ["10.0.1.0/24"],
          "private": ["10.0.10.0/24"],
          "data": []
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
  "compute": { "ec2_instances": [], "autoscaling_groups": [], "ecs_clusters": [], "ecs_services": [], "eks_clusters": [], "lambda_functions": [], "fargate_services": [] },
  "data_stores": { "rds_instances": [], "rds_clusters": [], "dynamodb_tables": [], "elasticache_clusters": [], "s3_buckets": [], "redshift_clusters": [] },
  "security": { "iam_roles": [], "iam_policies": [], "security_groups": [], "nacls": [], "kms_keys": [], "waf_web_acls": [], "secrets_manager_secrets": [], "certificate_manager_certs": [] },
  "integration": { "api_gateways": [], "load_balancers": [], "cloudfront_distributions": [], "sqs_queues": [], "sns_topics": [], "eventbridge_rules": [], "step_functions": [] },
  "monitoring": { "cloudwatch_alarms": [], "cloudwatch_dashboards": [], "cloudtrail_trails": [], "config_rules": [], "guardduty_detectors": [] },
  "cross_repo_references": {
    "remote_state_reads": [
      {
        "backend": "s3",
        "config": { "bucket": "terraform-state", "key": "networking/terraform.tfstate" },
        "outputs_consumed": ["vpc_id", "private_subnet_ids"]
      }
    ],
    "ssm_parameter_reads": [],
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

---

## 5. Phase 2: Architecture Synthesis (Reduce)

A single **read-only sub-agent** invocation (`architecture-synthesizer`) reads all extraction
JSON files from `extractions/` and produces `output/unified-architecture.json`. This is the
most intellectually complex phase — it must resolve cross-repo dependencies, deduplicate
shared resources, build the global VPC topology, trace request flows from edge to data stores,
and compute blast radius per component.

Because the sub-agent runs in an isolated context, it receives only the task instructions and
the files it reads — it does not inherit the orchestrator's accumulated conversation history.
This keeps the synthesis context clean and focused.

### Unified Architecture Model Schema (key structure)

```json
{
  "metadata": {
    "generated_at": "2026-03-26T14:00:00Z",
    "repos_analyzed": 32,
    "total_resources": 847,
    "regions": ["us-east-1", "us-west-2"],
    "accounts": ["production", "shared-services"]
  },
  "topology": {
    "regions": [
      {
        "name": "us-east-1",
        "is_primary": true,
        "vpcs": [ { "id": "production-vpc", "cidr": "10.0.0.0/16", "source_repo": "networking-core" } ]
      }
    ],
    "cross_region_connections": []
  },
  "service_map": {
    "tiers": {
      "edge": { "resources": [] },
      "ingress": { "resources": [] },
      "compute": { "resources": [] },
      "data": { "resources": [] },
      "integration": { "resources": [] },
      "management": { "resources": [] }
    },
    "request_flows": [],
    "event_flows": []
  },
  "dependency_graph": { "nodes": [], "edges": [] },
  "blast_radius_map": {
    "aws_rds_cluster.primary": {
      "direct_dependents": ["aws_ecs_service.api"],
      "transitive_dependents": ["aws_cloudfront_distribution.main"],
      "blast_radius": "critical"
    }
  }
}
```

---

## 6. Phase 3: Diagram Generation

A **write-capable sub-agent** (`drawio-generator`) reads the unified architecture model and
produces a draw.io XML file using AWS Architecture 2024 stencils. The diagram is importable
into both draw.io desktop and Lucidchart.

### draw.io XML Structure with AWS Stencils

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
        <mxCell id="aws-cloud" value="AWS Cloud"
          style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;"
          vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="3260" height="2500" as="geometry"/>
        </mxCell>

        <!-- Region boundary (primary) -->
        <mxCell id="region-use1" value="us-east-1"
          style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=1;"
          vertex="1" parent="aws-cloud">
          <mxGeometry x="20" y="40" width="1560" height="2400" as="geometry"/>
        </mxCell>

        <!-- VPC boundary -->
        <mxCell id="vpc-prod" value="Production VPC&#xa;10.0.0.0/16"
          style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;"
          vertex="1" parent="region-use1">
          <mxGeometry x="20" y="40" width="1500" height="1200" as="geometry"/>
        </mxCell>

        <!-- ECS Service example -->
        <mxCell id="aws-ecs-service-api" value="API Service"
          style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs"
          vertex="1" parent="vpc-prod">
          <mxGeometry x="300" y="300" width="60" height="60" as="geometry"/>
        </mxCell>

        <!-- Connection arrow: ID convention = resource address with dots→dashes -->
        <mxCell id="edge-api-to-rds" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
          edge="1" source="aws-ecs-service-api" target="aws-rds-cluster-primary" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### AWS Stencil Quick Reference

```
# Grouping Containers
AWS Cloud:          shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E
Region:             shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6
VPC:                shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF
Availability Zone:  shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_availability_zone;strokeColor=#00A4A6
Public Subnet:      shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#7AA116;fillColor=#E9F3E6
Private Subnet:     shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7

# Compute (fillColor=#ED7100)
EC2:    shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;fillColor=#ED7100
Lambda: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda;fillColor=#ED7100
ECS:    shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs;fillColor=#ED7100
EKS:    shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eks;fillColor=#ED7100

# Networking (fillColor=#8C4FFF)
ALB/NLB:        shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_load_balancing;fillColor=#8C4FFF
CloudFront:     shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudfront;fillColor=#8C4FFF
Route 53:       shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.route_53;fillColor=#8C4FFF
NAT Gateway:    shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.nat_gateway;fillColor=#8C4FFF
Transit Gateway:shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.transit_gateway;fillColor=#8C4FFF
API Gateway:    shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway;fillColor=#E7157B

# Database (fillColor=#C925D1)
RDS:        shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;fillColor=#C925D1
Aurora:     shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.aurora;fillColor=#C925D1
DynamoDB:   shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;fillColor=#C925D1
ElastiCache:shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elasticache;fillColor=#C925D1

# Storage (fillColor=#3F8624)
S3:  shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;fillColor=#3F8624
EFS: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.efs;fillColor=#3F8624

# Integration (fillColor=#E7157B)
SQS:         shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sqs;fillColor=#E7157B
SNS:         shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sns;fillColor=#E7157B
EventBridge: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eventbridge;fillColor=#E7157B

# Security (fillColor=#DD344C)
IAM:             shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.identity_and_access_management;fillColor=#DD344C
WAF:             shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.waf;fillColor=#DD344C
KMS:             shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.key_management_service;fillColor=#DD344C
Secrets Manager: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.secrets_manager;fillColor=#DD344C
GuardDuty:       shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.guardduty;fillColor=#DD344C

# Management (fillColor=#E7157B)
CloudWatch: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;fillColor=#E7157B
CloudTrail: shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudtrail;fillColor=#E7157B

# Well-Architected Finding Overlays
Critical: strokeColor=#FF0000;fontColor=#FF0000;dashed=1;dashPattern=5 5
High:     strokeColor=#FF8C00;fontColor=#FF8C00;dashed=1;dashPattern=5 5
Medium:   strokeColor=#FFD700;fontColor=#FFD700;dashed=1;dashPattern=3 3
```

**Cell ID convention:** Every `mxCell` id is the resource address with dots replaced by
dashes. `aws_rds_cluster.primary` → `id="aws-rds-cluster-primary"`. The enhancement
overlay sub-agent relies on this to locate cells by resource address.

---

## 7. Phase 4: Well-Architected Analysis

A **read-only sub-agent** (`well-architected-analyzer`) reads `output/unified-architecture.json`
and evaluates it against all six AWS Well-Architected Framework pillars, scoring each 1–5
and producing structured findings with remediation steps, effort estimates, and resilience
posture assessment including phased enhancement roadmap.

See Section 9.6 for the complete agent configuration. The findings JSON includes a
`diagram_overlay` field per finding so Phase 5 can locate and annotate the correct diagram
cells.

---

## 8. Phase 5: Enhancement Overlay & Recommendations

A **write-capable sub-agent** (`enhancement-overlayer`) reads the Well-Architected findings
and the base diagram XML, then adds colored annotation layers, DR architecture ghost overlays,
and a phased enhancement legend. It also produces `output/enhancement-roadmap.md`.

---

## 9. Complete File Implementations

### 9.1 Always-On Standards — `.github/copilot-instructions.md`

> This file is injected in every chat, every agent run, and every code review.
> It must contain only what is relevant to **nearly every interaction** — ≤15 rules.
> Workflow orchestration logic does NOT belong here.

```markdown
# AWS Infrastructure Analysis — Project Standards

## Pipeline Conventions
- All Terraform source repos are under `repos/` and are **read-only** — never modify them
- Extraction outputs go to `extractions/<repo-name>.json`
- Unified model goes to `output/unified-architecture.json`
- Diagrams go to `output/aws-architecture.drawio.xml` and `output/aws-architecture-annotated.drawio.xml`
- WAF report goes to `output/well-architected-report.md` and `output/well-architected-findings.json`

## Terraform Reading Rules
- Read `.tf` files directly — do NOT run `terraform init`, `terraform plan`, or any Terraform CLI commands
- For private registry modules: infer created resources from the module name and input variables
- For local-path modules (`source = "../../modules/..."`): read the module's `.tf` files directly
- Mark inferred data with `"resolution": "inferred"` in extraction JSON

## AWS Service Taxonomy
- **Edge**: CloudFront, WAF, Shield, Route 53
- **Ingress**: ALB, NLB, API Gateway
- **Compute**: EC2, ECS, EKS, Lambda, Fargate
- **Data**: RDS, Aurora, DynamoDB, ElastiCache, Redshift
- **Storage**: S3, EFS, EBS
- **Integration**: SQS, SNS, EventBridge, Step Functions
- **Security**: IAM, KMS, Secrets Manager, GuardDuty
- **Management**: CloudWatch, CloudTrail, Config, SSM

## JSON/XML Integrity
- All extraction JSONs must pass schema validation (required fields: `repo_name`, `providers`, `resources`, `networking`, `cross_repo_references`)
- All `.drawio.xml` files must be well-formed XML before being considered complete
```

### 9.2 Operational Guidance — `AGENTS.md`

> This file is loaded when a coding agent operates autonomously.
> It contains the operational procedures an agent needs to do its work —
> build commands, directory conventions, and simple linear steps.

```markdown
# Operational Guidance for Coding Agents

## Directory Setup
- Verify repos are present: `find repos/ -maxdepth 1 -mindepth 1 -type d | sort`
- Create working directories: `mkdir -p extractions output`

## Phase 0: Repo Discovery
1. `find repos/ -maxdepth 1 -mindepth 1 -type d | sort`
2. For each directory: `find <dir> -name "*.tf" | head -1` (skip if empty)
3. Gather metadata via grep; write `repo-manifest.json`

## JSON Validation
- Validate JSON: `jq empty <file>` (exits non-zero if invalid)
- Check required fields: `jq -e '.repo_name, .providers, .resources, .networking, .cross_repo_references' <file>`

## XML Validation
- Validate draw.io XML: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('<file>')"`

## Before Completing Any Phase
- Verify the output file exists and is non-empty
- Run the appropriate validation command above
```

### 9.3 Parent Orchestrator — `.github/agents/aws-pipeline-orchestrator.agent.md`

```yaml
---
name: aws-pipeline-orchestrator
description: >
  Orchestrates the full 5-phase AWS infrastructure analysis pipeline across 30+
  Terraform repositories. Uses sub-agents for each specialist phase: extraction,
  synthesis, diagram generation, Well-Architected analysis, and enhancement overlay.
  Invoke when asked to analyze AWS infrastructure, run the full pipeline, or
  produce an architecture diagram and Well-Architected review from Terraform repos.
tools: ['agent', 'codebase', 'terminalLastCommand']
agents:
  - tf-repo-extractor
  - architecture-synthesizer
  - drawio-generator
  - well-architected-analyzer
  - enhancement-overlayer
model: Claude Opus 4.5
---

You are the AWS infrastructure analysis pipeline orchestrator. You coordinate
a map-reduce workflow across 30+ Terraform repositories using specialist sub-agents.

## Orchestration Rules

- NEVER modify any file inside `repos/` — it is read-only source material
- Invoke sub-agents for ALL specialist work; do not attempt extraction or diagramming yourself
- Pass clear, self-contained instructions to each sub-agent (they have isolated contexts and
  cannot see this conversation)
- After each sub-agent completes, verify its output file exists before proceeding

## Phase 0: Discover Repositories

Before invoking any extraction sub-agents:

1. Run: `find repos/ -maxdepth 1 -mindepth 1 -type d | sort`
2. For each directory, verify it contains `.tf` files:
   `find <dir> -name "*.tf" | head -1` (skip if no output)
3. For each valid repo, gather:
   - `find <dir> -name "*.tf" | wc -l` (tf_file_count)
   - `grep -rc "^resource " <dir>/*.tf 2>/dev/null | awk -F: '{s+=$2} END {print s}'` (estimated_resource_count)
   - `grep -rh "region" <dir>/*.tf | grep -oP '"[a-z]{2}-[a-z]+-\d+"' | sort -u` (detected_regions)
   - `grep -l "terraform_remote_state" <dir>/*.tf 2>/dev/null` (has_remote_state)
4. Write `repo-manifest.json` with all discovered metadata
5. Run: `mkdir -p extractions output`
6. Report: N repos discovered, detected regions, estimated total resource count

## Phase 1: Repository Extraction (Map)

For each repo in `repo-manifest.json`:

1. Check if `extractions/<repo-name>.json` already exists — skip if present
2. Invoke the `tf-repo-extractor` sub-agent with these instructions:
   ```
   Analyze the Terraform repository at: repos/<repo-name>
   Write the extraction JSON to: extractions/<repo-name>.json
   Follow the extraction schema defined in the project standards.
   ```
3. After each extraction, verify: `jq empty extractions/<repo-name>.json`
4. If validation fails, re-invoke the sub-agent with the error details

After all extractions: report X of N repos extracted successfully.

## Phase 2: Architecture Synthesis (Reduce)

Invoke the `architecture-synthesizer` sub-agent with:
```
Read all JSON files in extractions/ and repo-manifest.json.
Resolve cross-repo dependencies, deduplicate resources, build the unified
topology, service map, dependency graph, and blast radius map.
Write output to: output/unified-architecture.json
```

Verify output exists before proceeding.

## Phase 3: Diagram Generation

Invoke the `drawio-generator` sub-agent with:
```
Read: output/unified-architecture.json
Reference: .github/skills/analyze-aws-infra/references/aws-stencils.md
Produce a draw.io XML diagram with AWS Architecture 2024 stencils.
Cell ID convention: resource address with dots replaced by dashes
  (e.g., aws_rds_cluster.primary → id="aws-rds-cluster-primary")
Write output to: output/aws-architecture.drawio.xml
```

Verify XML is well-formed: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('output/aws-architecture.drawio.xml')"`

## Phase 4: Well-Architected Analysis

Invoke the `well-architected-analyzer` sub-agent with:
```
Read: output/unified-architecture.json
Evaluate against all 6 AWS Well-Architected Framework pillars.
Score each pillar 1-5. Produce structured findings with resource addresses,
severity, remediation steps, effort estimates, and diagram_overlay metadata.
Write: output/well-architected-report.md (human-readable)
Write: output/well-architected-findings.json (machine-readable for diagram overlay)
```

## Phase 5: Enhancement Overlay

Invoke the `enhancement-overlayer` sub-agent with:
```
Read: output/aws-architecture.drawio.xml
Read: output/well-architected-findings.json
Add finding annotations to each affected resource cell (use cell ID = resource
address with dots→dashes). Add DR architecture ghost overlay for missing components.
Write: output/aws-architecture-annotated.drawio.xml
Write: output/enhancement-roadmap.md
```

## Final Report to User

Present:
1. Pipeline completion summary (N repos analyzed, total resources discovered)
2. Architecture overview (regions, VPCs, service tiers)
3. Well-Architected scores per pillar
4. Top 5 critical findings with resource addresses and impact
5. Resilience posture: current RTO/RPO → target RTO/RPO
6. Files produced:
   - `output/aws-architecture-annotated.drawio.xml` (importable to draw.io and Lucidchart)
   - `output/well-architected-report.md`
   - `output/enhancement-roadmap.md`
```

### 9.4 Sub-agent — `.github/agents/tf-repo-extractor.agent.md`

> **Sub-agent design note:** This agent uses only read-capable tools (`codebase`,
> `terminalLastCommand`). Write tools are omitted from the `tools` whitelist —
> the GitHub Copilot sub-agent model is whitelist-only; omitting a tool is
> equivalent to Claude Code's `disallowedTools`.

```yaml
---
name: tf-repo-extractor
description: >
  Analyzes a single Terraform repository by reading .tf files directly from disk.
  Extracts all AWS resources, networking topology, cross-repo references, and
  resilience indicators into a structured JSON extraction file.
  Read-only: never modifies the repository. Does not use the Terraform CLI.
tools: ['codebase', 'terminalLastCommand']
model: Claude Sonnet 4.5
---

You are a Terraform HCL analyst. Extract the complete AWS architecture from
the Terraform repository at the path provided by the orchestrator.

You do NOT have access to the Terraform CLI. All analysis is done by reading
HCL files using codebase search and terminal commands (find, grep, cat).

NEVER modify any file in repos/.

## Extraction Procedure

### Step 1: Inventory
```bash
find <repo-path> -name "*.tf" -type f | sort
find <repo-path> -name "*.tfvars" -type f | sort
```

### Step 2: Provider Analysis
```bash
grep -n 'provider\s*"aws"' <repo-path>/*.tf
```
Extract: region, alias, version constraint for each provider block.
If region is a variable reference, check `variables.tf` and `.tfvars` for the default.

### Step 3: Resource Extraction
For each `resource "aws_*"` block:
- Record: type, name, full address (e.g., `aws_vpc.main`)
- Map to provider alias → region
- Extract key attributes: CIDR blocks, instance types, encryption settings, multi_az flags
- Parse HCL references to map `references_to` and `referenced_by`

### Step 4: Module Analysis
For each `module` block:
- If source is a relative path (`./` or `../`): read the module .tf files directly (fully analyzable)
- If source is a registry path: infer resources from module name convention:
  - `*/vpc/*` → aws_vpc, aws_subnet, aws_internet_gateway, aws_nat_gateway
  - `*/ecs/*` → aws_ecs_cluster, aws_ecs_service, aws_ecs_task_definition
  - `*/rds/*` → aws_rds_cluster or aws_db_instance
  - `*/eks/*` → aws_eks_cluster, aws_eks_node_group
  - `*/alb/*` or `*/elb/*` → aws_lb, aws_lb_target_group, aws_lb_listener
- Mark registry modules with `"resolution": "inferred"`

### Step 5: Cross-Repo References
- `data "terraform_remote_state"` → extract backend bucket/key; maps to another repo's outputs
- `data "aws_ssm_parameter"` → extract parameter path
- `output` blocks → what does this repo export for other repos to consume?

### Step 6: Resilience Pre-computation
- `multi_az`: `multi_az = true` or subnets spread across 2+ AZs
- `backup_configured`: `backup_retention_period > 0`, PITR enabled, S3 versioning
- `encryption_at_rest`: `storage_encrypted = true` or `kms_key_id` present

### Step 7: Write Output
Write the extraction JSON to the path specified by the orchestrator.
Validate JSON syntax before writing:
```bash
echo '<json>' | jq empty
```

## When a .tf File Is Too Large
Use grep to extract block headers first:
```bash
grep -n "^resource\|^data\|^module\|^output\|^variable" <file>
```
Then read specific line ranges for the most important blocks.
```

### 9.5 Sub-agent — `.github/agents/architecture-synthesizer.agent.md`

```yaml
---
name: architecture-synthesizer
description: >
  Reads all per-repo extraction JSON files and produces a unified AWS architecture
  model. Resolves cross-repo dependencies via remote state and SSM parameter
  references, deduplicates shared resources, builds the topology hierarchy,
  service tier map, dependency graph, and blast radius analysis.
  Read-only: does not write to extractions/ or repos/.
tools: ['codebase', 'terminalLastCommand']
model: Claude Opus 4.5
---

You are an AWS solutions architect synthesizing a unified infrastructure view
from multiple Terraform repository extraction files.

## Synthesis Procedure

1. **Load All Extractions**: Read every `.json` file in `extractions/` and `repo-manifest.json`

2. **Resolve Cross-Repo Dependencies**:
   - Match each `remote_state_reads` entry to the source repo's `outputs` using the S3 key path
   - Match each `ssm_parameter_reads` to the repo that writes that parameter
   - Build a repo-to-repo dependency graph

3. **Deduplicate**: Resources appearing in multiple extractions (shared modules, remote state
   references) are deduplicated. Keep the most complete version.

4. **Build Topology**: Organize resources into region → VPC → subnet hierarchy.
   Map cross-VPC connections (peering, transit gateway).
   Map cross-region connections (replication, read replicas, Route 53 failover).

5. **Build Service Map**: Classify every resource into the architectural tier taxonomy
   defined in `copilot-instructions.md`. Trace request flows from edge → ingress → compute → data.

6. **Dependency Graph**: Build edges for:
   - Network dependency (resource lives in subnet/VPC)
   - Data dependency (service reads from database)
   - Integration dependency (Lambda triggered by SQS)

7. **Blast Radius**: For each critical resource, compute direct dependents,
   transitive dependents, and blast radius classification (critical/high/medium/low).

8. **Write Output**: Write `output/unified-architecture.json` using the unified model schema.
   This is the single source of truth for all downstream sub-agents.
```

### 9.6 Sub-agent — `.github/agents/drawio-generator.agent.md`

```yaml
---
name: drawio-generator
description: >
  Produces a draw.io XML diagram from the unified AWS architecture model using
  AWS Architecture 2024 stencils. The output must be importable into both
  draw.io desktop and Lucidchart without modification.
tools: ['codebase', 'editFiles']
model: Claude Opus 4.5
---

You are a diagram generation specialist. Produce a draw.io XML file representing
the complete AWS architecture from the unified model at `output/unified-architecture.json`.

Reference stencil styles from `.github/skills/analyze-aws-infra/references/aws-stencils.md`.

## Layout Rules

1. **Outermost**: AWS Cloud boundary
2. **Second level**: One Region container per region, left-to-right. Primary region is largest.
3. **Third level**: VPC containers within each region.
4. **Fourth level**: Subnet containers (public=green tint, private=blue tint, data=purple tint), top-to-bottom.
5. **Resources**: Placed inside their subnet with the correct AWS stencil style.
6. **Global services** (CloudFront, Route 53, WAF, IAM): Outside region containers, in a "Global Services" area at the top.
7. **Connections**: Solid arrows = data flow; dashed arrows = cross-region replication; dotted = async messaging.

## Cell ID Convention
Every mxCell id = resource address with dots replaced by dashes:
- `aws_rds_cluster.primary` → `id="aws-rds-cluster-primary"`
- `aws_ecs_service.api` → `id="aws-ecs-service-api"`
This is mandatory — the enhancement-overlayer sub-agent depends on it to locate cells.

## Page Size
3300 × 2540 (landscape). Resource icons: 60×60 px. Minimum 40px spacing between resources.

## Output
Write: `output/aws-architecture.drawio.xml`
After writing, read the file back and verify it starts with `<?xml` and contains `mxGraphModel`.
```

### 9.7 Sub-agent — `.github/agents/well-architected-analyzer.agent.md`

```yaml
---
name: well-architected-analyzer
description: >
  Evaluates the unified AWS architecture model against all six pillars of the
  AWS Well-Architected Framework. Produces scored findings with specific resource
  addresses, severity ratings, remediation steps, effort estimates, and a phased
  resilience enhancement roadmap. Read-only.
tools: ['codebase']
model: Claude Opus 4.5
---

You are an AWS Well-Architected Framework specialist. Read `output/unified-architecture.json`
and evaluate against all 6 WAF pillars.

## Scoring Scale (1–5 per pillar)
- 5: All best practices followed. No findings.
- 4: Minor findings only. Low risk.
- 3: Acceptable. Some gaps. Medium risk.
- 2: Concerning. Significant gaps. High risk.
- 1: Critical. Major architectural weaknesses. Immediate action required.

## Six Pillars Evaluation Checklist

**Operational Excellence**: CloudWatch alarms on key metrics; CloudTrail enabled; automated deployment pipelines; AWS Config enabled; consistent resource tagging.

**Security**: Security groups follow least-privilege (no 0.0.0.0/0 on sensitive ports); encryption at rest (RDS, S3, EBS, DynamoDB); encryption in transit; IAM minimum-privilege; WAF on public endpoints; secrets in Secrets Manager; GuardDuty enabled; VPC flow logs.

**Reliability**: Databases Multi-AZ; compute across multiple AZs; Auto Scaling configured; cross-region DR strategy; Route 53 health checks; automated backups; RTO/RPO defined.

**Performance Efficiency**: Right-sized instances; caching (ElastiCache, CloudFront, DAX); read replicas for read-heavy workloads; S3 lifecycle policies.

**Cost Optimization**: Reserved Instances/Savings Plans; resources tagged for cost tracking; dev/staging scaled down; S3 Intelligent-Tiering; VPC endpoints vs NAT Gateway for S3/DynamoDB.

**Sustainability**: Graviton instances where possible; Lambda memory/timeout tuned; data retention policies; minimal data transfer architecture.

## Findings Schema
Each finding must include:
```json
{
  "id": "WAF-SEC-001",
  "pillar": "security",
  "severity": "critical",
  "title": "RDS cluster lacks encryption at rest",
  "resource": "aws_rds_cluster.primary",
  "repo": "data-services",
  "region": "us-east-1",
  "description": "...",
  "impact": "...",
  "recommendation": "...",
  "effort": "high",
  "diagram_overlay": {
    "target_cell_id": "aws-rds-cluster-primary",
    "annotation_color": "#FF0000",
    "annotation_text": "WAF-SEC-001: No encryption at rest"
  }
}
```

## Resilience Posture
Assess: current RTO/RPO, single points of failure, single-AZ and single-region failure scenarios.
Recommend: DR pattern (backup-restore / pilot-light / warm-standby / active-active).
If single-region: identify components requiring replication and estimate cost per DR tier.

## Output Files
Write: `output/well-architected-report.md` (human-readable executive summary + findings)
Write: `output/well-architected-findings.json` (machine-readable array of finding objects)
```

### 9.8 Sub-agent — `.github/agents/enhancement-overlayer.agent.md`

```yaml
---
name: enhancement-overlayer
description: >
  Reads Well-Architected findings and overlays them on the draw.io diagram as
  colored annotations. Adds DR architecture ghost overlays showing recommended
  additions. Produces the final enhancement roadmap document.
tools: ['codebase', 'editFiles']
model: Claude Opus 4.5
---

You produce the final annotated diagram and enhancement roadmap.

## Inputs
Read: `output/aws-architecture.drawio.xml`
Read: `output/well-architected-findings.json`

## Step 1: Add Finding Annotations
For each finding, locate the mxCell using `target_cell_id` from `diagram_overlay`.
Add an adjacent annotation mxCell:
- Critical (severity=critical): red border + red text label with finding ID
- High: orange border + orange text
- Medium: yellow border + yellow text
Add `tooltip` attribute with the finding description.

## Step 2: Add DR Ghost Overlay
If findings recommend cross-region DR:
1. Add a dashed-outline region container for the recommended DR region
2. Add ghost resources (dashed borders) showing what should be added
3. Add dashed arrows for replication connections
4. Label each ghost resource with the enhancement phase number (Phase 1/2/3)

## Step 3: Add Legend
Bottom-right corner legend box:
- Red badge = Critical finding
- Orange badge = High finding
- Yellow badge = Medium finding
- Dashed outline resource = Recommended addition
- Phase numbers = Enhancement roadmap phase

## Step 4: Write Outputs
Write: `output/aws-architecture-annotated.drawio.xml`
Write: `output/enhancement-roadmap.md` with:
  - Executive summary
  - Current vs target resilience posture (RTO/RPO)
  - Phase 1: Quick wins (1-2 weeks, low effort)
  - Phase 2: Foundation reliability (2-4 weeks)
  - Phase 3: Cross-region DR (4-8 weeks)
  - Phase 4: Active-active (8-12 weeks)
  - Cost estimates per phase
  - Risk reduction per phase
```

### 9.9 Master Pipeline Skill — `.github/skills/analyze-aws-infra/SKILL.md`

```yaml
---
name: analyze-aws-infra
description: >
  Full AWS infrastructure analysis pipeline across 30+ Terraform repositories.
  Produces a unified architecture diagram (draw.io XML with AWS stencils,
  importable to Lucidchart) and a Well-Architected Framework assessment with
  phased resilience enhancement roadmap. Use when asked to analyze AWS
  infrastructure, review IaC repos, produce architecture diagrams from Terraform,
  or assess multi-region resilience posture.
---

## Pipeline Overview

This skill orchestrates a 5-phase map-reduce workflow:
1. **Phase 0**: Discover all repos under `repos/` → `repo-manifest.json`
2. **Phase 1 (Map)**: Extract each repo via `tf-repo-extractor` sub-agent → `extractions/`
3. **Phase 2 (Reduce)**: Synthesize all extractions via `architecture-synthesizer` → `output/unified-architecture.json`
4. **Phase 3**: Generate diagram via `drawio-generator` → `output/aws-architecture.drawio.xml`
5. **Phase 4**: Well-Architected review via `well-architected-analyzer` → `output/well-architected-findings.json`
6. **Phase 5**: Overlay findings via `enhancement-overlayer` → `output/aws-architecture-annotated.drawio.xml`

## Invoking the Pipeline

Select the **@aws-pipeline-orchestrator** agent, then provide:
- Optional phase filter: `all` (default), `extract`, `synthesize`, `diagram`, `analyze`, `enhance`
- Optional repo filter: `all` (default) or a specific repo name for targeted reprocessing

## Output Files

| File | Phase | Purpose |
|---|---|---|
| `repo-manifest.json` | 0 | Discovered repo metadata |
| `extractions/<repo>.json` | 1 | Per-repo HCL extraction |
| `output/unified-architecture.json` | 2 | Merged architecture model (source of truth) |
| `output/aws-architecture.drawio.xml` | 3 | Importable draw.io diagram |
| `output/well-architected-report.md` | 4 | Human-readable WAF assessment |
| `output/well-architected-findings.json` | 4 | Machine-readable findings for overlay |
| `output/aws-architecture-annotated.drawio.xml` | 5 | Diagram with findings overlay |
| `output/enhancement-roadmap.md` | 5 | Phased resilience roadmap |

For stencil style reference, see [references/aws-stencils.md](./references/aws-stencils.md).
```

### 9.10 Prompt Files — `.github/prompts/`

**`.github/prompts/analyze-aws-infra.prompt.md`**

```markdown
---
mode: agent
agent: aws-pipeline-orchestrator
description: Run the full AWS infrastructure analysis pipeline across all Terraform repos
---

Run the full AWS infrastructure analysis pipeline.

Phase: all
Repo filter: all

Start with Phase 0 (repository discovery), proceed through all phases sequentially,
and present the final results when complete.
```

**`.github/prompts/extract-repo.prompt.md`**

```markdown
---
mode: agent
agent: aws-pipeline-orchestrator
description: Re-extract a single Terraform repository (use after a repo changes)
---

Re-extract a single repository from the pipeline.

Phase: extract
Repo: $REPO_NAME

Delete the existing extraction file if present and re-run the tf-repo-extractor
sub-agent for this repo only. After extraction, re-run phases 2-5 to update
all downstream outputs.
```

**`.github/prompts/well-architected-review.prompt.md`**

```markdown
---
mode: agent
agent: aws-pipeline-orchestrator
description: Run only the Well-Architected review on an existing unified architecture model
---

Run Well-Architected review only.

Phase: analyze

Requires `output/unified-architecture.json` to already exist.
Re-run the well-architected-analyzer sub-agent, then the enhancement-overlayer
sub-agent to produce updated findings and annotated diagram.
```

### 9.11 Validation Hooks — `.github/hooks/`

**`.github/hooks/validate-extraction-json.sh`**

```bash
#!/usr/bin/env bash
# postToolUse: validates extraction JSON schema after a write to extractions/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only validate extraction files
if [[ "$file_path" != extractions/*.json ]]; then
  exit 0
fi

# Check JSON is valid
if ! jq empty "$file_path" 2>/dev/null; then
  echo "Validation failed: Invalid JSON in $file_path. Fix syntax before proceeding." >&2
  exit 1
fi

# Check required top-level fields
required_fields=("repo_name" "providers" "resources" "networking" "cross_repo_references")
for field in "${required_fields[@]}"; do
  if ! jq -e ".$field" "$file_path" > /dev/null 2>&1; then
    echo "Validation failed: Missing required field '$field' in $file_path" >&2
    exit 1
  fi
done

echo "Extraction JSON validated: $file_path"
exit 0
```

**`.github/hooks/validate-drawio-xml.sh`**

```bash
#!/usr/bin/env bash
# postToolUse: validates draw.io XML well-formedness after a write to output/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

if [[ "$file_path" != output/*.drawio.xml ]]; then
  exit 0
fi

# Check XML is well-formed using python3's standard library
if ! python3 -c "import xml.etree.ElementTree as ET; ET.parse('$file_path')" 2>/dev/null; then
  echo "Validation failed: Malformed XML in $file_path. Fix before proceeding." >&2
  exit 1
fi

echo "draw.io XML validated: $file_path"
exit 0
```

### 9.12 Settings — `.vscode/settings.json`

```json
{
  "github.copilot.agent.hooks": {
    "postToolUse": [
      {
        "matcher": {
          "tool": "editFiles",
          "pathPattern": "extractions/**/*.json"
        },
        "command": "bash .github/hooks/validate-extraction-json.sh"
      },
      {
        "matcher": {
          "tool": "editFiles",
          "pathPattern": "output/*.drawio.xml"
        },
        "command": "bash .github/hooks/validate-drawio-xml.sh"
      }
    ]
  },
  "github.copilot.chat.agent.thinkingEnabled": true
}
```

> **Token impact reminder:** Hooks execute as shell scripts at the code level and bypass the
> LLM entirely — they consume **zero tokens**. This is their fundamental distinction from
> instructions and skills. Using a hook for JSON/XML validation instead of an instruction
> ("always validate your JSON output") saves tokens on every invocation and provides
> deterministic enforcement rather than LLM best-effort compliance.

---

## 10. Execution Playbook

### 10.1 First Run — Complete Pipeline

```
1. cd ~/aws-architecture-analysis
2. Verify repos: ls repos/
3. Verify tools: jq --version && python3 --version
4. Open VS Code in this directory with GitHub Copilot enabled
5. Select @aws-pipeline-orchestrator agent
6. Run: /analyze-aws-infra  (or type "run the full AWS analysis pipeline")
   → Phase 0: discovers repos, generates repo-manifest.json
   → Phase 1: extracts each repo (sub-agent per repo, ~30-60 min for 30+ repos)
   → Phase 2: synthesizes unified model
   → Phase 3: generates draw.io diagram
   → Phase 4: runs Well-Architected review
   → Phase 5: overlays findings and produces roadmap
7. Import output/aws-architecture-annotated.drawio.xml into draw.io or Lucidchart
8. Review output/well-architected-report.md
9. Review output/enhancement-roadmap.md
```

### 10.2 Running Individual Phases

```
# Re-discover repos (after adding new repos to repos/)
/discover-repos

# Re-extract a single repo (after it changed)
/extract-repo  →  provide repo name when prompted

# Regenerate diagram only (existing unified model)
/generate-diagram

# Re-run Well-Architected review only (existing unified model)
/well-architected-review
```

### 10.3 Adding New Repositories

```
1. Clone/copy new repo into repos/
2. /discover-repos  (updates repo-manifest.json)
3. /extract-repo <new-repo-name>  (extracts the new repo)
4. Select @aws-pipeline-orchestrator → "Re-run phases 2-5"
   → Synthesizes updated model, regenerates diagram, re-runs WAF analysis
```

### 10.4 Handoff Option: Present Results to Team

After the pipeline completes, the orchestrator can offer a **handoff** to a reporting agent
if you want to produce a stakeholder presentation from the findings. This is the correct
use of the handoff mechanism — the automated pipeline completes, then the user decides
whether to hand off to a documentation or presentation specialist.

```yaml
# Optional addition to aws-pipeline-orchestrator.agent.md frontmatter:
handoffs:
  - label: Generate Stakeholder Report
    agent: documentation-writer
    prompt: "Produce a stakeholder-ready architecture review document from the Well-Architected findings."
    send: false
```

---

## 11. Token Cost Strategy

| Component | Loading Mechanism | Token Cost | Optimization |
|---|---|---|---|
| `copilot-instructions.md` | Always-on | ~300 tokens | ≤15 rules; stable content |
| `AGENTS.md` | During agent operation | ~200 tokens | Focus on operational commands only |
| Skill metadata (all skills) | Always-on | ~60 tokens/skill × 5 = ~300 tokens | Precise descriptions = accurate triggering |
| `analyze-aws-infra` skill body | On-demand (description match) | ~400 tokens | Detailed steps in `references/` |
| `aws-stencils.md` reference | On-demand (when referenced by skill) | ~800 tokens | Only loaded during diagram generation |
| Parent orchestrator prompt | Always-on once selected | ~1,200 tokens | Focused on delegation; not procedural |
| Sub-agent per-repo extraction | Isolated context per invocation | ~600 tokens + repo files read | Each repo starts fresh — no accumulation |
| Synthesis sub-agent | Isolated context | ~600 tokens + all extractions read | Reads compressed JSON, not raw HCL |
| Diagram sub-agent | Isolated context | ~600 tokens + unified model | Doesn't need Terraform knowledge |
| WAF analysis sub-agent | Isolated context | ~800 tokens + unified model | Reads model, not raw HCL |
| Enhancement sub-agent | Isolated context | ~600 tokens + diagram + findings | Focused XML editing task |
| **Hooks** | Event-triggered shell scripts | **0 tokens** | No limit; deterministic enforcement |
| **Estimated total (30 repos)** | | **~38,000 tokens** | |

### Why Sub-agent Isolation Is the Key Cost Driver

The per-repo extraction cost (~600 tokens) is **flat** regardless of which repo is being
processed. Repo #30 does not pay for the context accumulated from repos #1–29. This is the
sub-agent isolation guarantee in GitHub Copilot's architecture — each sub-agent runs in a
clean context, receiving only the instructions the parent passes to it.

### Strategic Principles (from GitHub Copilot reference architecture)

| Principle | Application to This Pipeline |
|---|---|
| Never always-on what can be loaded on-demand | Stencil reference lives in `references/` (Tier 3); only loaded during Phase 3 |
| Never use Instructions when Hooks (zero tokens) suffice | JSON/XML validation is a hook, not an instruction |
| Never put in Instructions what belongs in a Skill | Workflow orchestration logic lives in the orchestrator agent, not `copilot-instructions.md` |
| Write precise Skill descriptions | Each skill description names both what it does and when it should trigger |
| Keep global Instructions stable | `copilot-instructions.md` changes rarely; avoids cache invalidation |

---

## Appendix: Component Placement Quick Reference

| Concern | Correct Location | Why |
|---|---|---|
| Always-on project standards and taxonomy | `.github/copilot-instructions.md` | Needed in nearly every interaction |
| Operational build/discovery commands | `AGENTS.md` | Loaded when coding agent operates autonomously |
| Full pipeline orchestration logic | `aws-pipeline-orchestrator.agent.md` | Handoff/sub-agent orchestration belongs in `.agent.md` |
| Specialist task execution (extract, synthesize, diagram, review) | Sub-agents (`.github/agents/`) | Isolated context per task; no cross-contamination |
| User-triggered pipeline invocation | Prompt files (`.github/prompts/`) | Explicitly invoked; not always-on |
| Detailed task procedures + stencil reference | Skill SKILL.md + `references/` | On-demand; only loaded when relevant |
| Unconditional schema/XML validation | `postToolUse` hooks (`.vscode/settings.json`) | Zero tokens; deterministic; runs unconditionally |
| External tool access (future: GitHub API, AWS Cost Explorer) | MCP server configuration | Tool descriptions loaded once per session |

---

*This plan was produced using the GitHub Copilot customization architecture as defined in*
*the principal engineer reference guide (February 2026). All component placements follow*
*the layered model: Instructions → AGENTS.md → Custom Agents (sub-agents) → Skills → Hooks.*

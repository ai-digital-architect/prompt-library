# CI/CD & Runtime Enrichment Enhancement

## Claude Code Customization Architecture — Enriching AWS Infrastructure Diagrams

---

## Executive Summary

This enhancement extends the AWS infrastructure analysis pipeline to extract deployment
topology, runtime service connections, monitoring coverage, and team ownership from CI/CD
pipelines, container configs, application settings, and documentation files — then overlays
this operational context onto the architecture diagram.

The enhancement is designed for **Claude Code's customization architecture**: Skills in
`.claude/skills/`, Sub-agents in `.claude/agents/`, PostToolUse Hooks for validation,
project memory in `CLAUDE.md`, and cross-platform conventions in `AGENTS.md`.

### What This Enhancement Adds to the Diagram

| Before (Terraform only) | After (with enrichment) |
|-------------------------|------------------------|
| AWS resource boxes with dependency arrows | + Deployment flow arrows showing CI/CD promotion path |
| Static infrastructure topology | + Runtime data flow (service → database via connection string) |
| Resources grouped by VPC/subnet | + Resources grouped by owning team and business domain |
| No operational context | + Monitoring coverage overlay (monitored vs unmonitored) |
| No deployment information | + CI/CD quality gate badges (security scan, integration tests) |
| Inferred service relationships | + Verified runtime connections from config and env vars |

---

## Table of Contents

1. [Architecture Mapping to Claude Code](#1-architecture-mapping-to-claude-code)
2. [Enrichment Sources](#2-enrichment-sources)
3. [Project Structure](#3-project-structure)
4. [Phase 1b: Context Enrichment](#4-phase-1b-context-enrichment)
5. [Enrichment Schema](#5-enrichment-schema)
6. [Updated Synthesis Phase](#6-updated-synthesis-phase)
7. [Updated Diagram Phase](#7-updated-diagram-phase)
8. [Updated Well-Architected Analysis](#8-updated-well-architected-analysis)
9. [Complete File Implementations](#9-complete-file-implementations)
10. [Execution Playbook](#10-execution-playbook)
11. [Token Cost Strategy](#11-token-cost-strategy)

---

## 1. Architecture Mapping to Claude Code

Each enrichment concern maps to a specific Claude Code component:

| Concern | Component | File Location | Why This Component |
|---------|-----------|---------------|-------------------|
| Enrichment conventions and schemas | `CLAUDE.md` (project memory) | Project root | Always-on; every agent reads it |
| Cross-platform conventions | `AGENTS.md` | Project root | Shared with Copilot, Cursor, and other tools |
| Per-repo enrichment orchestration | **Skill**: `enrich-repo` | `.claude/skills/enrich-repo/SKILL.md` | User + Claude auto-invocable; orchestrates sub-agents per repo |
| Full-pipeline enrichment | **Skill**: `enrich-infrastructure` | `.claude/skills/enrich-infrastructure/SKILL.md` | User-invoked; maps across all repos |
| CI/CD pipeline analysis | **Sub-agent**: `cicd-analyzer` | `.claude/agents/cicd-analyzer.md` | Read-only; isolated context per repo; specialist knowledge |
| Runtime connection discovery | **Sub-agent**: `runtime-mapper` | `.claude/agents/runtime-mapper.md` | Read-only; isolated context; parses config/env/taskdef files |
| Monitoring coverage audit | **Sub-agent**: `monitoring-auditor` | `.claude/agents/monitoring-auditor.md` | Read-only; isolated context; specialist in observability tooling |
| Enriched synthesis | **Sub-agent**: `enriched-synthesizer` | `.claude/agents/enriched-synthesizer.md` | Read-only; merges Terraform + enrichment data |
| Operational WAF review | **Sub-agent**: `operational-reviewer` | `.claude/agents/operational-reviewer.md` | Read-only; evaluates CI/CD and ops posture |
| Enrichment JSON validation | **PostToolUse Hook** | `.claude/hooks/validate-enrichment-json.sh` | Deterministic; zero tokens; blocks on malformed JSON |
| Extraction progress tracking | **SubagentStop Hook** | `.claude/hooks/track-enrichment-progress.sh` | Logs per-repo completion |

### Why This Component Mapping

**Sub-agents instead of a single skill with inline instructions.** The CI/CD analyzer,
runtime mapper, and monitoring auditor are separate sub-agents because they each need:
- **Isolated context** — the CI/CD analyzer doesn't need monitoring configs polluting its context window
- **Enforced read-only** — `disallowedTools: [Write, Edit, MultiEdit]` physically prevents any agent from modifying the repos it analyzes
- **Specialist focus** — each agent is prompted with deep knowledge of its domain (pipeline formats, connection string patterns, observability tooling)

**Skills for orchestration, sub-agents for execution.** The `enrich-repo` skill is the
coordinator — it inventories non-TF files, invokes the right specialists, and merges
results. The sub-agents are the workers with isolated contexts and restricted tool access.
This follows the architecture doc's principle: *"the role layer (Sub-agents) defines
who does specialized work"*.

**PostToolUse hook for validation.** Every enrichment JSON written to `enrichments/` is
validated by a hook that checks JSON well-formedness and required top-level fields. The
model cannot skip this check — it fires deterministically on every Write to that directory.

---

## 2. Enrichment Sources

### 2.1 CI/CD Pipeline Files

The CI/CD analyzer sub-agent scans for all common pipeline configuration formats:

| Platform | Files to Scan | Key Data Extracted |
|----------|--------------|-------------------|
| **GitHub Actions** | `.github/workflows/*.yml` | Jobs, steps, environment targets, secrets, deployment triggers, approval gates |
| **AWS CodePipeline/CodeBuild** | `buildspec.yml`, `pipeline.json`, `codepipeline.tf` | Build stages, deployment actions, artifact stores |
| **GitLab CI** | `.gitlab-ci.yml` | Stages, environments, rules, deployment jobs |
| **Jenkins** | `Jenkinsfile`, `Jenkinsfile.*` | Pipeline stages, agent labels, deployment steps |
| **CircleCI** | `.circleci/config.yml` | Workflows, jobs, orbs, deployment contexts |
| **Azure DevOps** | `azure-pipelines.yml` | Stages, environments, approvals, deployment jobs |
| **ArgoCD** | `argocd/`, `argo-application.yml` | Application definitions, sync policies, target clusters |
| **Terraform Cloud** | `.terraform-cloud.yml`, workspace configs | Run triggers, workspace chaining, VCS connections |

### 2.2 Container and Service Configuration

| Source | Files to Scan | Key Data Extracted |
|--------|--------------|-------------------|
| **ECS Task Definitions** | `taskdef.json`, `task-definition.json`, `*-taskdef.json` | Container images, port mappings, environment variables, sidecar containers, resource limits |
| **Docker Compose** | `docker-compose*.yml` | Service dependencies, port mappings, volume mounts, network definitions |
| **Dockerfile** | `Dockerfile`, `Dockerfile.*` | Base image, exposed ports, health check commands |
| **Kubernetes** | `k8s/`, `helm/`, `kustomize/`, `*.yaml` in k8s dirs | Services, ingress rules, network policies, ConfigMaps, Secrets references |
| **Lambda** | `serverless.yml`, `sam-template.yaml`, `template.yaml` | Function configs, event sources, environment variables, layers |

### 2.3 Application Configuration

| Source | Files to Scan | Key Data Extracted |
|--------|--------------|-------------------|
| **Environment files** | `.env.example`, `.env.template`, `.env.production` | Database URLs, API endpoints, queue names, cache endpoints |
| **App config** | `config/`, `appsettings*.json`, `application*.yml` | Connection strings, service endpoints, feature flags |
| **Parameter references** | Any file referencing SSM, Secrets Manager | Runtime secret paths, parameter store keys |

### 2.4 Monitoring and Observability

| Source | Files to Scan | Key Data Extracted |
|--------|--------------|-------------------|
| **CloudWatch** | `dashboards/*.json`, `alarms.tf`, `monitoring.tf` | Dashboard definitions, alarm thresholds, monitored metrics |
| **Grafana** | `grafana/dashboards/*.json` | Dashboard panels, data sources, alert rules |
| **DataDog** | `datadog/`, `monitors/*.json` | Monitor definitions, SLO targets, service maps |
| **Alert configs** | `alerts.yml`, `pagerduty.tf`, `opsgenie.tf` | Alert routing, escalation policies, on-call schedules |

### 2.5 Documentation

| Source | Files to Scan | Key Data Extracted |
|--------|--------------|-------------------|
| **README** | `README.md`, `README.rst` | Service description, architecture notes, team ownership |
| **ADRs** | `docs/adr/`, `adr/` | Architecture decisions, trade-offs, context |
| **Runbooks** | `runbooks/`, `docs/operations/` | Incident response procedures, failover steps |
| **CODEOWNERS** | `CODEOWNERS`, `.github/CODEOWNERS` | File-to-team ownership mapping |

---

## 3. Project Structure

The enhancement adds new sub-agents, skills, and a validation hook alongside the existing
Terraform analysis infrastructure:

```
aws-architecture-analysis/
├── CLAUDE.md                                           ← UPDATED: adds enrichment schemas and rules
├── AGENTS.md                                           ← UPDATED: adds enrichment source conventions
├── .claude/
│   ├── settings.json                                   ← UPDATED: adds enrichment validation hook
│   ├── agents/
│   │   ├── tf-repo-extractor.md                        ← EXISTING: Terraform HCL extraction
│   │   ├── architecture-synthesizer.md                 ← EXISTING: merge Terraform extractions
│   │   ├── drawio-generator.md                         ← EXISTING: base diagram
│   │   ├── well-architected-analyzer.md                ← EXISTING: WAF analysis
│   │   ├── enhancement-overlayer.md                    ← EXISTING: overlay WAF findings
│   │   │
│   │   ├── cicd-analyzer.md                            ← NEW: CI/CD pipeline specialist (read-only)
│   │   ├── runtime-mapper.md                           ← NEW: runtime connection discovery (read-only)
│   │   ├── monitoring-auditor.md                       ← NEW: monitoring coverage audit (read-only)
│   │   ├── enriched-synthesizer.md                     ← NEW: merges Terraform + enrichment (read-only)
│   │   └── operational-reviewer.md                     ← NEW: CI/CD and ops WAF review (read-only)
│   ├── skills/
│   │   ├── analyze-aws-infra/
│   │   │   └── SKILL.md                                ← EXISTING: master Terraform pipeline
│   │   ├── discover-repos/
│   │   │   └── SKILL.md                                ← EXISTING: repo discovery
│   │   ├── enrich-infrastructure/
│   │   │   └── SKILL.md                                ← NEW: enrichment across all repos
│   │   ├── enrich-repo/
│   │   │   └── SKILL.md                                ← NEW: single-repo enrichment
│   │   └── operational-review/
│   │       └── SKILL.md                                ← NEW: CI/CD focused WAF review
│   └── hooks/
│       ├── validate-extraction-json.sh                 ← EXISTING: validates Terraform extraction
│       ├── validate-drawio-xml.sh                      ← EXISTING: validates draw.io XML
│       └── validate-enrichment-json.sh                 ← NEW: validates enrichment JSON
├── repos/                                               ← Your 30+ repositories (read-only)
├── extractions/                                         ← Terraform extraction JSONs
├── enrichments/                                         ← NEW: enrichment JSONs (one per repo)
│   ├── networking-core.enrichment.json
│   ├── compute-platform.enrichment.json
│   └── ...
└── output/
    ├── unified-architecture.json                        ← UPDATED: includes enrichment data
    ├── aws-architecture.drawio.xml                      ← Base diagram (infrastructure only)
    ├── aws-architecture-enriched.drawio.xml             ← NEW: diagram with CI/CD + runtime overlays
    ├── well-architected-report.md                       ← UPDATED: includes operational findings
    ├── operational-posture-report.md                    ← NEW: CI/CD and monitoring assessment
    └── enhancement-roadmap.md                           ← UPDATED: includes operational recommendations
```

---

## 4. Phase 1b: Context Enrichment

### 4.1 Strategy

After Phase 1a (Terraform extraction), a **second map pass** runs enrichment across all
repos. The `enrich-infrastructure` skill orchestrates the fan-out. For each repo, it
invokes the `enrich-repo` skill, which in turn invokes three specialist sub-agents.

The specialists run in **isolated contexts** — the CI/CD analyzer never sees monitoring
configs, and the runtime mapper never sees pipeline files. This isolation ensures each
specialist uses its full context window on its domain.

### 4.2 Architecture Diagram

```
User invokes /enrich-infrastructure
        │
        ▼
┌────────────────────────────────┐
│  enrich-infrastructure Skill    │
│  - Reads repo-manifest.json     │
│  - For each repo:               │
│      invokes /enrich-repo       │
│  - Reports summary              │
└───────────┬────────────────────┘
            │ (per repo)
            ▼
┌────────────────────────────────┐
│  enrich-repo Skill              │
│  (inline execution)             │
│  - Inventories non-TF files     │
│  - Invokes specialist agents    │
│  - Reads README + CODEOWNERS    │
│  - Identifies operational risks │
│  - Merges all outputs           │
│  - Writes enrichment JSON       │
└──┬──────┬──────┬───────────────┘
   │      │      │      Parent invokes sub-agents
   ▼      ▼      ▼      (single-level delegation)
┌──────┐┌──────┐┌──────────┐
│ cicd ││runtme││monitoring│  Read-only sub-agents
│analyz││mapper││ auditor  │  (isolated contexts)
│(R/O) ││(R/O) ││ (R/O)    │  disallowedTools: [Write,Edit,MultiEdit]
└──┬───┘└──┬───┘└──┬───────┘
   │       │       │
   │       │       │  Results returned to parent skill
   ▼       ▼       ▼
  enrich-repo merges → enrichments/<repo>.enrichment.json
                              │
                       PostToolUse Hook
                       (validate-enrichment-json.sh)
```

### 4.3 Why Sub-agents and Not a Single Skill

The three specialists must be separate sub-agents (not inline skill instructions) because:

1. **Context isolation prevents cross-contamination.** A CI/CD pipeline file for a complex
   GitHub Actions workflow can be 200+ lines. If the runtime mapper had to share context
   with the CI/CD analyzer, both would have less room for their actual work.

2. **Read-only enforcement is physical, not instructional.** Each specialist has
   `disallowedTools: [Write, Edit, MultiEdit]` in its frontmatter. This means the model
   physically cannot modify repo files during analysis — it's enforced at the tool level,
   not by a "please don't write" instruction that could be ignored.

3. **Specialist prompting produces better results.** The CI/CD analyzer's entire prompt
   is focused on pipeline file formats. It knows GitHub Actions syntax, Jenkins pipeline
   stages, and CodeBuild buildspec structure. A generalist agent trying to do all three
   jobs would produce shallower analysis across the board.

---

## 5. Enrichment Schema

Every enrichment JSON conforms to this schema. The synthesis phase merges it with the
corresponding Terraform extraction JSON.

```json
{
  "repo_name": "compute-platform",
  "enriched_at": "2026-03-26T15:00:00Z",
  "enrichment_sources": [
    ".github/workflows/deploy.yml",
    ".github/workflows/pr-check.yml",
    "taskdef.json",
    ".env.example",
    "monitoring/dashboards/api.json",
    "README.md",
    "CODEOWNERS"
  ],

  "ci_cd": {
    "platform": "github_actions",
    "pipeline_files": [".github/workflows/deploy.yml", ".github/workflows/pr-check.yml"],
    "environments": [
      {
        "name": "dev",
        "region": "us-east-1",
        "auto_deploy": true,
        "branch_filter": "develop"
      },
      {
        "name": "staging",
        "region": "us-east-1",
        "auto_deploy": true,
        "branch_filter": "main",
        "requires_approval": false
      },
      {
        "name": "production",
        "region": "us-east-1",
        "auto_deploy": false,
        "branch_filter": "main",
        "requires_approval": true,
        "required_reviewers": ["platform-team"],
        "wait_timer_minutes": 30
      }
    ],
    "promotion_path": [
      {"from": "dev", "to": "staging", "gate": "automated_tests", "auto": true},
      {"from": "staging", "to": "production", "gate": "manual_approval", "auto": false}
    ],
    "deployment_targets": [
      {
        "service_name": "api-service",
        "target_type": "ecs",
        "cluster_reference": "aws_ecs_cluster.main",
        "regions_deployed_to": ["us-east-1"],
        "deployment_strategy": "rolling",
        "rollback_mechanism": "ecs_circuit_breaker",
        "health_check_grace_period": "300s",
        "desired_count_expression": "var.api_desired_count"
      }
    ],
    "artifact_stores": [
      {
        "type": "ecr",
        "uri": "123456789.dkr.ecr.us-east-1.amazonaws.com/api-service",
        "region": "us-east-1"
      },
      {
        "type": "s3",
        "bucket": "deploy-artifacts-prod",
        "region": "us-east-1",
        "purpose": "lambda_deployment_packages"
      }
    ],
    "secrets_referenced": [
      {
        "source": "aws_secrets_manager",
        "path": "/prod/api/database-url",
        "consumed_by": "api-service",
        "discovered_in": ".github/workflows/deploy.yml"
      },
      {
        "source": "aws_ssm_parameter",
        "path": "/prod/api/redis-endpoint",
        "consumed_by": "api-service",
        "discovered_in": "taskdef.json"
      },
      {
        "source": "github_actions_secret",
        "name": "AWS_ACCESS_KEY_ID",
        "purpose": "deployment_credentials",
        "discovered_in": ".github/workflows/deploy.yml"
      }
    ],
    "quality_gates": [
      {"stage": "pre_merge", "type": "unit_tests", "tool": "jest", "required": true},
      {"stage": "pre_merge", "type": "linting", "tool": "eslint", "required": true},
      {"stage": "pre_merge", "type": "security_scan", "tool": "snyk", "required": true},
      {"stage": "pre_deploy", "type": "build", "tool": "docker_build", "required": true},
      {"stage": "post_deploy_staging", "type": "smoke_tests", "tool": "newman", "required": true},
      {"stage": "post_deploy_staging", "type": "integration_tests", "tool": "jest", "required": true},
      {"stage": "post_deploy_production", "type": "smoke_tests", "tool": "newman", "required": true}
    ],
    "notifications": {
      "on_failure": [{"channel": "slack", "target": "#deploy-failures"}],
      "on_success": [{"channel": "slack", "target": "#deployments"}],
      "on_approval_needed": [{"channel": "slack", "target": "#deploy-approvals"}]
    },
    "deployment_frequency_indicators": {
      "has_automated_tests": true,
      "has_staging_environment": true,
      "has_production_approval_gate": true,
      "has_rollback_mechanism": true,
      "has_canary_or_blue_green": false,
      "estimated_dora_deploy_frequency": "daily_to_weekly"
    }
  },

  "runtime_connections": [
    {
      "from_service": "api-service",
      "to_resource": "aws_rds_cluster.primary",
      "connection_type": "database",
      "protocol": "postgresql",
      "port": 5432,
      "discovered_in": "taskdef.json",
      "env_var": "DATABASE_URL",
      "secret_path": "/prod/api/database-url",
      "connection_pooling": "pgbouncer_sidecar"
    },
    {
      "from_service": "api-service",
      "to_resource": "aws_elasticache_cluster.sessions",
      "connection_type": "cache",
      "protocol": "redis",
      "port": 6379,
      "discovered_in": ".env.example",
      "env_var": "REDIS_URL",
      "secret_path": "/prod/api/redis-endpoint"
    },
    {
      "from_service": "api-service",
      "to_resource": "aws_sqs_queue.events",
      "connection_type": "message_producer",
      "protocol": "sqs",
      "discovered_in": "config/production.yml",
      "env_var": "EVENT_QUEUE_URL"
    },
    {
      "from_service": "api-service",
      "to_resource": "aws_s3_bucket.uploads",
      "connection_type": "object_store",
      "protocol": "s3",
      "discovered_in": "config/production.yml",
      "env_var": "UPLOAD_BUCKET"
    }
  ],

  "container_config": {
    "dockerfile_path": "Dockerfile",
    "base_image": "node:20-alpine",
    "multi_stage_build": true,
    "exposed_ports": [8080],
    "health_check": {
      "path": "/health",
      "interval": "30s",
      "timeout": "5s",
      "retries": 3
    },
    "sidecar_containers": [
      {"name": "datadog-agent", "purpose": "monitoring", "image": "datadog/agent:latest"},
      {"name": "envoy-proxy", "purpose": "service_mesh", "image": "envoyproxy/envoy:v1.28"}
    ],
    "resource_limits": {
      "cpu": "512",
      "memory": "1024"
    }
  },

  "monitoring": {
    "coverage": {
      "has_cloudwatch_alarms": true,
      "has_dashboards": true,
      "has_custom_metrics": true,
      "has_distributed_tracing": true,
      "has_log_aggregation": true,
      "has_alerting_rules": true,
      "has_on_call_rotation": true,
      "has_runbooks": false,
      "has_slo_definitions": true
    },
    "dashboards": [
      {"tool": "grafana", "file": "monitoring/dashboards/api.json", "name": "API Service Overview"}
    ],
    "alert_rules": [
      {
        "name": "High Error Rate",
        "metric": "5xx_count",
        "threshold": "> 10 per minute",
        "severity": "critical",
        "notifies": "pagerduty:platform-team"
      },
      {
        "name": "High Latency",
        "metric": "p99_response_time",
        "threshold": "> 2000ms",
        "severity": "warning",
        "notifies": "slack:#alerts"
      }
    ],
    "slo_targets": [
      {"metric": "availability", "target": "99.9%", "window": "30d"},
      {"metric": "p99_latency", "target": "500ms", "window": "30d"}
    ],
    "on_call": {
      "team": "platform-engineering",
      "tool": "pagerduty",
      "escalation_policy": "platform-engineering-escalation"
    },
    "unmonitored_resources": []
  },

  "documentation": {
    "readme_summary": "Core API service handling user authentication, data access, and event publishing.",
    "architecture_notes": "Uses CQRS pattern with SQS for event sourcing. Read models served from ElastiCache.",
    "team_owner": "platform-engineering",
    "codeowners": {
      "default": "@org/platform-engineering",
      "infra/": "@org/infrastructure",
      "monitoring/": "@org/sre-team"
    },
    "domain": "core-platform",
    "criticality": "tier-1",
    "runbook_exists": false,
    "adr_count": 3,
    "last_updated": "2026-03-15"
  },

  "operational_risks": [
    {
      "id": "OPS-RISK-001",
      "type": "missing_runbook",
      "description": "No runbook exists for this tier-1 service",
      "impact": "Incident response depends on tribal knowledge",
      "recommendation": "Create runbooks for common failure scenarios"
    },
    {
      "id": "OPS-RISK-002",
      "type": "no_canary_deployment",
      "description": "Deployment uses rolling update, not canary or blue-green",
      "impact": "Bad deploys affect all traffic before detection",
      "recommendation": "Implement canary deployment with automatic rollback"
    }
  ]
}
```

---

## 6. Updated Synthesis Phase

The `enriched-synthesizer` sub-agent reads both Terraform extractions and enrichment
JSONs, producing an updated unified model with deployment, runtime, and monitoring data.

### 6.1 What Enrichment Adds to the Unified Model

The unified architecture model (`output/unified-architecture.json`) gains four new sections:

```json
{
  "existing_sections": "... (topology, service_map, dependency_graph, blast_radius_map) ...",

  "deployment_topology": {
    "environments": ["dev", "staging", "production"],
    "promotion_path": [
      {"from": "dev", "to": "staging", "gate": "automated_tests"},
      {"from": "staging", "to": "production", "gate": "manual_approval"}
    ],
    "services": [
      {
        "name": "api-service",
        "repo": "compute-platform",
        "deploy_target": "aws_ecs_cluster.main",
        "regions": ["us-east-1"],
        "strategy": "rolling",
        "has_rollback": true,
        "quality_gates": ["unit_tests", "security_scan", "smoke_tests", "integration_tests"]
      }
    ],
    "deployment_coupling": [
      {
        "services": ["api-service", "worker-service"],
        "reason": "shared_pipeline",
        "risk": "Deploying one may require deploying both"
      }
    ]
  },

  "runtime_service_mesh": {
    "connections": [
      {
        "from": "api-service",
        "to": "aws_rds_cluster.primary",
        "type": "database",
        "protocol": "postgresql",
        "discovered_via": "environment_variable",
        "verified": true
      }
    ],
    "unverified_connections": [
      {
        "from": "aws_ecs_service.api",
        "to": "aws_rds_cluster.primary",
        "type": "data_dependency",
        "source": "terraform_reference",
        "note": "Terraform reference exists but no runtime connection string found"
      }
    ]
  },

  "monitoring_coverage": {
    "monitored_resources": [
      {"resource": "aws_ecs_service.api", "alarms": 3, "dashboards": 1, "slo_defined": true}
    ],
    "unmonitored_resources": [
      {"resource": "aws_nat_gateway.main", "criticality": "high", "recommendation": "Add bandwidth and error alarms"}
    ],
    "coverage_percentage": 72,
    "slo_coverage_percentage": 40
  },

  "team_ownership": {
    "teams": [
      {
        "name": "platform-engineering",
        "repos": ["compute-platform", "networking-core"],
        "resources_owned": 145,
        "on_call": true,
        "criticality": "tier-1"
      }
    ],
    "unowned_resources": [
      {"resource": "aws_s3_bucket.legacy_data", "repo": "data-migration", "note": "No CODEOWNERS entry"}
    ]
  }
}
```

### 6.2 Cross-referencing Terraform and Enrichment Data

The enriched synthesizer performs four critical cross-references:

1. **Runtime connections validate Terraform dependencies.** If the Terraform extraction says
   `aws_ecs_service.api` references `aws_rds_cluster.primary`, and the enrichment confirms
   a `DATABASE_URL` environment variable pointing to that cluster, the connection is marked
   `"verified": true`. Connections in only one source are flagged as `"unverified"`.

2. **Deployment targets map to Terraform resources.** The CI/CD analysis says "api-service
   deploys to ECS in us-east-1." The synthesizer matches this to `aws_ecs_cluster.main`
   from the Terraform extraction, linking deployment flow to infrastructure.

3. **Monitoring coverage maps to resource inventory.** For each resource in the Terraform
   extraction, the synthesizer checks whether enrichment data includes alarms, dashboards,
   or SLOs referencing that resource. Unmonitored critical resources are flagged.

4. **Team ownership maps to blast radius.** CODEOWNERS data combined with blast radius
   analysis reveals which teams are affected when a shared resource fails.

---

## 7. Updated Diagram Phase

### 7.1 New Diagram Layers

The enriched diagram adds four visual layers on top of the base infrastructure diagram:

**Layer 1: Deployment Flow**
```
Dashed arrows showing CI/CD promotion path, colored by environment:
- Blue dashed: dev deployment
- Yellow dashed: staging deployment
- Green dashed: production deployment
- Lock icon at manual approval gates

Style: edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=8 4;strokeColor=#0066CC
```

**Layer 2: Runtime Data Flow**
```
Colored solid arrows showing verified runtime connections:
- Purple: database connections (postgresql, mysql)
- Orange: cache connections (redis, memcached)
- Green: message queue (producer → queue → consumer)
- Blue: HTTP/API calls between services

Each arrow labeled with protocol and port.

Style: edgeStyle=orthogonalEdgeStyle;strokeColor=#9933CC;strokeWidth=2
```

**Layer 3: Monitoring Coverage**
```
Halo effect around resources based on monitoring state:
- Green halo: fully monitored (alarms + dashboard + SLO)
- Yellow halo: partially monitored (some alarms, no SLO)
- Red halo: unmonitored critical resource

Style (green): shadow=1;shadowColor=#00CC00;shadowOffsetX=0;shadowOffsetY=0;shadowBlur=10
```

**Layer 4: Team Ownership**
```
Lightweight grouped boundary around team-owned resources:
- Rounded rectangle with team name and domain label
- Color-coded by business domain
- Dashed border to distinguish from VPC/subnet infrastructure boundaries

Style: rounded=1;dashed=1;dashPattern=4 4;strokeColor=#666666;fillColor=#F5F5F5;opacity=30
```

### 7.2 Diagram Legend Additions

```
── ── ──  Blue dashed    = Dev deployment flow
── ── ──  Yellow dashed  = Staging deployment flow
── ── ──  Green dashed   = Production deployment flow
────────  Purple solid   = Database connection (verified)
────────  Orange solid   = Cache connection (verified)
────────  Green solid    = Message queue flow (verified)
⬡ Green halo             = Fully monitored (alarms + dashboard + SLO)
⬡ Yellow halo            = Partially monitored
⬡ Red halo               = Unmonitored (critical)
┌ ─ ─ ─ ┐               = Team ownership boundary
└ ─ ─ ─ ┘
🔒                        = Manual approval gate
✓ sec                     = Security scan gate
✓ test                    = Integration test gate
```

---

## 8. Updated Well-Architected Analysis

The enrichment data enables three new assessment areas that the base Terraform analysis
cannot evaluate.

### 8.1 Operational Excellence — CI/CD Assessment

| Check | Source | Finding if Missing |
|-------|--------|--------------------|
| Automated testing in pipeline | `ci_cd.quality_gates` | "No automated tests before production deployment" |
| Security scanning in pipeline | `ci_cd.quality_gates` (type: security_scan) | "No security scanning in CI/CD pipeline" |
| Staging environment exists | `ci_cd.environments` | "No staging environment — deploys directly to production" |
| Production approval gate | `ci_cd.environments[production].requires_approval` | "Production deploys have no approval gate" |
| Rollback mechanism | `ci_cd.deployment_targets[].rollback_mechanism` | "No automated rollback on failed deployment" |
| Deployment notifications | `ci_cd.notifications` | "No deployment failure notifications configured" |
| Canary or blue-green deployment | `ci_cd.deployment_targets[].deployment_strategy` | "Rolling updates only — no canary or blue-green" |
| Infrastructure as Code for pipeline | Pipeline file existence | "Pipeline configuration not version-controlled" |

### 8.2 Reliability — Runtime Resilience Assessment

| Check | Source | Finding if Missing |
|-------|--------|--------------------|
| Health check endpoints | `container_config.health_check` | "No health check endpoint defined" |
| Connection pooling | `runtime_connections[].connection_pooling` | "No connection pooling — risk of connection exhaustion" |
| Circuit breaker / retry | `runtime_connections`, sidecar analysis | "No circuit breaker for inter-service calls" |
| Graceful shutdown | Dockerfile `STOPSIGNAL`, ECS `stopTimeout` | "No graceful shutdown configuration" |
| Resource limits | `container_config.resource_limits` | "No CPU/memory limits — risk of noisy neighbor" |

### 8.3 Operational Excellence — Monitoring Assessment

| Check | Source | Finding if Missing |
|-------|--------|--------------------|
| Alarms on critical resources | `monitoring.coverage` | "5 critical resources have no CloudWatch alarms" |
| Dashboards exist | `monitoring.dashboards` | "No operational dashboard for this service" |
| SLO targets defined | `monitoring.slo_targets` | "No SLO targets — cannot measure reliability objectively" |
| On-call rotation | `monitoring.on_call` | "No on-call rotation for this tier-1 service" |
| Runbooks exist | `documentation.runbook_exists` | "No runbook — incident response depends on tribal knowledge" |
| Alert routing configured | `monitoring.alert_rules[].notifies` | "Alerts not routed to any notification channel" |

---

## 9. Complete File Implementations

### 9.1 CLAUDE.md Additions

Add these sections to the existing project `CLAUDE.md`:

```markdown
## Enrichment Pipeline

Phase 1b enriches the Terraform analysis with CI/CD, runtime, and monitoring data.
- Enrichment JSONs go to `enrichments/<repo-name>.enrichment.json`
- The enriched synthesizer merges Terraform + enrichment into the unified model
- The enriched diagram generator adds deployment, runtime, monitoring, and ownership layers
- All enrichment sub-agents are READ-ONLY — they never modify repos

## Enrichment Rules
- Scan CI/CD pipelines for deployment targets and match them to Terraform resource addresses
- Extract runtime connections from env vars and match to Terraform resources by type:
  - URLs with port 5432/3306 → RDS
  - URLs with port 6379 → ElastiCache
  - URLs with "sqs" or queue names → SQS
  - URLs with "s3" or bucket names → S3
- Mark connections as "verified" ONLY when BOTH Terraform reference AND runtime config confirm them
- Mark connections as "inferred" when only one source confirms them
- Do NOT extract actual secret values — only names and paths
```

### 9.2 Enrichment Pipeline Skill — `.claude/skills/enrich-infrastructure/SKILL.md`

```yaml
---
name: enrich-infrastructure
description: >
  Enriches AWS infrastructure analysis with CI/CD, runtime, and monitoring data
  from all repositories. Runs a map pass invoking /enrich-repo per repo, then
  re-synthesizes the unified model and regenerates the enriched diagram.
argument-hint: "[scope: all | repo-name]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash
---

Run context enrichment: $ARGUMENTS

## Phase 1b: Enrich All Repos

1. Read `repo-manifest.json` to get the list of repositories
2. Create `enrichments/` directory: `mkdir -p enrichments`
3. For each repo in the manifest:
   a. Check if `enrichments/<repo-name>.enrichment.json` already exists (skip if present)
   b. Invoke the `/enrich-repo` skill with the repo name
   c. The PostToolUse hook validates the output JSON automatically
4. Report: X of N repos enriched

## Phase 2b: Enriched Synthesis

5. Invoke the `enriched-synthesizer` sub-agent with:
   - Input: all `extractions/*.json` AND all `enrichments/*.enrichment.json`
   - Repo manifest: `repo-manifest.json`
   - Output: `output/unified-architecture.json` (updated with enrichment sections)

## Phase 3b: Enriched Diagram

6. Invoke the `drawio-generator` sub-agent with:
   - Input: `output/unified-architecture.json` (now includes enrichment data)
   - Output: `output/aws-architecture-enriched.drawio.xml`
   - Instructions: include deployment flow, runtime connections, monitoring coverage,
     and team ownership layers

## Phase 4b: Operational Review

7. Invoke the `operational-reviewer` sub-agent with:
   - Input: `output/unified-architecture.json`
   - Output: `output/operational-posture-report.md`

8. Present summary:
   - Repos enriched: X of N
   - Runtime connections discovered: Y (Z verified, W inferred)
   - Monitoring coverage: P%
   - CI/CD quality gate coverage across services
   - Top operational risks
```

### 9.3 Single-Repo Enrichment Skill — `.claude/skills/enrich-repo/SKILL.md`

```yaml
---
name: enrich-repo
description: >
  Enriches a single repository with CI/CD, runtime, and monitoring data.
  Invokes specialist sub-agents for each domain, then merges results.
  Use for testing enrichment on one repo or for incremental updates.
argument-hint: "[repo-name]"
disable-model-invocation: false
allowed-tools: Read, Write, Bash
---

Enrich repository: $ARGUMENTS

## Step 1: Inventory Non-TF Files

Scan `repos/$1/` for enrichment-relevant files:
```bash
# CI/CD pipelines
find repos/$1 -name "*.yml" -path "*workflow*" -o -name "buildspec.yml" -o \
  -name "Jenkinsfile*" -o -name ".gitlab-ci.yml" -o -name "azure-pipelines.yml" \
  -o -name "*circleci*" 2>/dev/null

# Container configs
find repos/$1 -name "taskdef*" -o -name "docker-compose*" -o -name "Dockerfile*" \
  -o -name "serverless.yml" -o -name "sam-template*" 2>/dev/null

# App config
find repos/$1 -name ".env*" -o -name "appsettings*" -o -name "application*.yml" 2>/dev/null
find repos/$1 -type d -name "config" 2>/dev/null

# Monitoring
find repos/$1 -type d -name "monitoring" -o -type d -name "dashboards" -o \
  -name "alerts*" -o -name "*alarms*" 2>/dev/null

# Documentation
find repos/$1 -name "README*" -o -name "CODEOWNERS" -o -type d -name "runbooks" \
  -o -type d -name "adr" 2>/dev/null
```

## Step 2: Invoke Specialists

Based on what files exist:

- If CI/CD pipeline files found:
  Invoke the `cicd-analyzer` sub-agent with repo path `repos/$1`
  
- If container/config/env files found:
  Invoke the `runtime-mapper` sub-agent with repo path `repos/$1`
  
- If monitoring/dashboard/alert files found:
  Invoke the `monitoring-auditor` sub-agent with repo path `repos/$1`

## Step 3: Read Documentation Directly

Read `repos/$1/README.md` and `repos/$1/CODEOWNERS` directly (small files).
Extract: service description, team ownership, domain, criticality.

## Step 4: Identify Operational Risks

Based on all enrichment data, flag risks:
- Tier-1 service with no runbook → OPS-RISK
- Production deployment with no approval gate → OPS-RISK
- No canary/blue-green deployment strategy → OPS-RISK
- No SLO targets defined → OPS-RISK
- No on-call rotation for critical service → OPS-RISK

## Step 5: Merge and Write

Combine all specialist outputs + documentation + risks into the enrichment schema.
Write to `enrichments/$1.enrichment.json`.
```

### 9.4 Sub-agent — `.claude/agents/cicd-analyzer.md`

```yaml
---
name: cicd-analyzer
description: >
  Analyzes CI/CD pipeline configurations to extract deployment topology,
  environment promotion paths, quality gates, artifact stores, and deployment
  strategies. Read-only — never modifies repo files. Invoke when a repository
  contains CI/CD pipeline files.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

You are a CI/CD pipeline analyst. Analyze all pipeline configuration files
in the provided repository path and extract the deployment topology.

## What to Scan

Scan for these files (in priority order):
1. `.github/workflows/*.yml` — GitHub Actions
2. `buildspec.yml` — AWS CodeBuild
3. `.gitlab-ci.yml` — GitLab CI
4. `Jenkinsfile` / `Jenkinsfile.*` — Jenkins
5. `.circleci/config.yml` — CircleCI
6. `azure-pipelines.yml` — Azure DevOps
7. `argocd/` / `argo-application.yml` — ArgoCD
8. Any `.tf` files containing `aws_codepipeline` or `aws_codebuild` resources

## Extraction Rules

For each pipeline file found:

### Environments
- Extract every environment/stage that represents a deployment target
- Identify the region for each (from env vars, AWS account IDs, or explicit config)
- Note whether deployment is automatic or requires approval
- Extract branch filters and trigger conditions

### Promotion Path
- Map the sequential flow from first environment to last
- Identify gates between stages (tests, approvals, wait timers)
- Note if any stages can be skipped or run in parallel

### Deployment Targets
- Identify WHAT is deployed (Docker image, Lambda zip, static assets)
- Identify WHERE it deploys (ECS service, Lambda function, S3 bucket, CloudFront)
- Extract the deployment strategy (rolling, blue-green, canary, all-at-once)
- Check for rollback configuration

### Quality Gates
- List every test/scan/check that runs before or after deployment
- Categorize: unit_tests, integration_tests, security_scan, linting, smoke_tests, load_tests
- Note which are required (blocking) vs optional (informational)

### Secrets and Artifacts
- List all secrets referenced (GitHub secrets, AWS Secrets Manager, SSM)
- List artifact stores (ECR repos, S3 buckets, package registries)
- Do NOT extract secret values — only names and paths

## Output

Return the `ci_cd` section of the enrichment schema with all fields populated.
If a field cannot be determined, set it to `null` with a brief explanation.
```

### 9.5 Sub-agent — `.claude/agents/runtime-mapper.md`

```yaml
---
name: runtime-mapper
description: >
  Discovers runtime service-to-service and service-to-resource connections
  by reading container configs, environment variables, application settings,
  and task definitions. Read-only. Invoke when a repository contains
  container configs, env files, or application settings.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

You are a runtime connection analyst. Discover how the service in this
repository connects to other services and AWS resources at runtime.

## What to Scan

1. **ECS Task Definitions**: `taskdef.json`, `*-taskdef.json`
   - Environment variables → connection strings, endpoints, queue URLs
   - Secrets → Secrets Manager ARNs, SSM parameter paths
   - Sidecar containers → service mesh, monitoring agents

2. **Docker Compose**: `docker-compose*.yml`
   - Service dependencies (`depends_on`)
   - Environment variables pointing to other services
   - Port mappings revealing exposed interfaces

3. **Dockerfiles**: `Dockerfile`, `Dockerfile.*`
   - Base image, exposed ports, health check configuration

4. **Application Config Files**:
   - `.env.example`, `.env.template` → all env vars with example values
   - `config/production.yml`, `config/default.yml` → connection endpoints
   - `appsettings.json`, `appsettings.Production.json` → .NET connection strings
   - `application.yml`, `application-prod.yml` → Spring Boot configs

5. **Kubernetes Manifests** (if present):
   - `k8s/`, `helm/values*.yaml`, `kustomize/`
   - Service definitions, ingress rules, ConfigMaps, Secret references

## Connection Discovery Rules

For each discovered connection:
1. Identify the **source service** (the application in this repo)
2. Match the **target resource** to Terraform resource types:
   - URLs with port 5432/3306 or `rds`/`aurora` → RDS
   - URLs with port 6379 or `redis`/`elasticache` → ElastiCache
   - URLs with `sqs` or queue names → SQS
   - URLs with `s3` or bucket names → S3
   - URLs with `dynamodb` → DynamoDB
   - URLs with `sns` → SNS
3. Record the discovery location (file and field)
4. Record the environment variable name and secret path
5. Identify the protocol and port

## Output

Return the `runtime_connections` and `container_config` sections of the enrichment schema.
```

### 9.6 Sub-agent — `.claude/agents/monitoring-auditor.md`

```yaml
---
name: monitoring-auditor
description: >
  Assesses monitoring and observability coverage by reading dashboard configs,
  alert rules, SLO definitions, and on-call configurations. Read-only.
  Invoke when a repository contains monitoring, dashboard, or alert files.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 12
---

You are a monitoring and observability auditor. Assess the monitoring
coverage for the services defined in this repository.

## What to Scan

1. **CloudWatch**: `*.tf` files with `aws_cloudwatch_metric_alarm` or
   `aws_cloudwatch_dashboard` — extract alarm names, thresholds, metrics
2. **Grafana**: `monitoring/dashboards/*.json`, `grafana/*.json`
3. **DataDog**: `datadog/monitors/*.json`, `datadog.yml`
4. **Alert configs**: `alerts.yml`, `alert-rules.yml`
5. **PagerDuty/OpsGenie**: `*.tf` files with `pagerduty_*` or `opsgenie_*`
6. **SLO definitions**: Any file containing SLO/SLA targets
7. **Runbooks**: `runbooks/`, `docs/operations/`, `docs/incident-response/`

## Assessment

For each service in the repo, determine:
- Does it have CloudWatch alarms on key metrics?
- Does it have an operational dashboard?
- Are SLO targets defined and measurable?
- Is there an on-call rotation?
- Do runbooks exist for common failure scenarios?
- Are alerts routed to notification channels?

## Output

Return the `monitoring` section of the enrichment schema. Include `unmonitored_resources`
for any resources that should have monitoring based on type and criticality.
```

### 9.7 Sub-agent — `.claude/agents/enriched-synthesizer.md`

```yaml
---
name: enriched-synthesizer
description: >
  Merges Terraform extraction data with CI/CD and runtime enrichment data
  to produce the unified architecture model with deployment topology,
  runtime service mesh, monitoring coverage, and team ownership. Read-only.
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

You are an architecture synthesizer. Merge Terraform infrastructure data
with operational enrichment data.

## Inputs
- All files in `extractions/*.json` (Terraform data)
- All files in `enrichments/*.enrichment.json` (CI/CD, runtime, monitoring data)
- `repo-manifest.json` (repo metadata)

## Synthesis Steps

### Step 1: Load and Pair
For each repo, load its extraction JSON and enrichment JSON as a pair.
Some repos may have extraction but no enrichment (no CI/CD files found) — that is normal.

### Step 2: Cross-reference Runtime Connections
For each runtime connection in enrichment data:
- Find the corresponding Terraform resource by address or type matching
- If both Terraform reference AND runtime config confirm the connection → `"verified": true`
- If only one source confirms → `"inferred"` with a note

### Step 3: Map Deployment to Infrastructure
For each CI/CD deployment target:
- Match the target (ECS cluster, Lambda function, S3 bucket) to a Terraform resource
- Record the deployment strategy, rollback mechanism, and quality gates

### Step 4: Compute Monitoring Coverage
For each resource in the Terraform extraction:
- Check if the enrichment data includes alarms, dashboards, or SLOs for it
- Compute coverage percentage: monitored resources / total critical resources

### Step 5: Aggregate Team Ownership
From CODEOWNERS and README data across all repos:
- Build a team → repos → resources map
- Cross-reference with blast radius data to identify team-level risk

### Step 6: Write Unified Model
Update `output/unified-architecture.json` with the four new sections:
deployment_topology, runtime_service_mesh, monitoring_coverage, team_ownership.
```

### 9.8 Sub-agent — `.claude/agents/operational-reviewer.md`

```yaml
---
name: operational-reviewer
description: >
  Evaluates CI/CD practices, runtime resilience, and monitoring coverage
  against the Well-Architected Framework operational excellence and
  reliability pillars. Read-only.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 20
---

You are a Well-Architected operational excellence reviewer. Evaluate the
enriched unified architecture model for CI/CD, runtime, and monitoring gaps.

Read `output/unified-architecture.json` and evaluate:

## CI/CD Assessment
For each service in `deployment_topology.services`:
- Has automated tests? Missing → finding
- Has security scanning? Missing → finding
- Has staging environment? Missing → finding
- Has production approval gate? Missing → finding
- Has rollback mechanism? Missing → finding
- Has deployment notifications? Missing → finding
- Uses canary or blue-green? Missing → recommendation (not finding)

## Runtime Resilience Assessment
For each service with `runtime_connections`:
- Health check endpoint defined? Missing → finding
- Connection pooling for databases? Missing → finding
- Resource limits configured? Missing → finding
- Graceful shutdown configured? Missing → recommendation

## Monitoring Assessment
For each resource in `monitoring_coverage`:
- Unmonitored critical resources → finding per resource
- Missing SLO targets → finding
- Missing on-call rotation for tier-1 services → finding
- Missing runbooks for tier-1 services → finding

## Output
Write `output/operational-posture-report.md` with:
- Operational Excellence score (1-5)
- Per-service CI/CD maturity assessment
- Monitoring coverage summary
- Prioritized operational improvement roadmap
```

### 9.9 Enrichment Validation Hook — `.claude/hooks/validate-enrichment-json.sh`

```bash
#!/usr/bin/env bash
# PostToolUse: validates enrichment JSON schema after Write to enrichments/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only validate enrichment files
if [[ "$file_path" != enrichments/*.enrichment.json ]]; then
  exit 0
fi

# Check JSON is valid
if ! jq empty "$file_path" 2>/dev/null; then
  echo '{"reason": "Invalid JSON in '"$file_path"'. Fix syntax before proceeding."}' >&2
  exit 2
fi

# Check required top-level fields
required_fields=("repo_name" "enrichment_sources" "ci_cd" "runtime_connections" "monitoring" "documentation")
for field in "${required_fields[@]}"; do
  if ! jq -e ".$field" "$file_path" > /dev/null 2>&1; then
    echo "{\"reason\": \"Missing required field '$field' in $file_path\"}" >&2
    exit 2
  fi
done

exit 0
```

### 9.10 Updated Settings — `.claude/settings.json` Additions

Add these to the existing `settings.json`:

```json
{
  "permissions": {
    "allow": [
      "... existing permissions ...",
      "Bash(find repos/* -name *.yml)",
      "Bash(find repos/* -name Dockerfile*)",
      "Bash(find repos/* -name taskdef*)",
      "Bash(find repos/* -name docker-compose*)",
      "Bash(find repos/* -name .env*)",
      "Bash(find repos/* -name CODEOWNERS)",
      "Bash(find repos/* -name README*)",
      "Bash(find repos/* -type d -name monitoring)",
      "Bash(find repos/* -type d -name dashboards)",
      "Bash(find repos/* -type d -name runbooks)",
      "Bash(find repos/* -type d -name config)",
      "Bash(find repos/* -type d -name k8s)",
      "Bash(find repos/* -type d -name helm)",
      "Bash(ls enrichments/)",
      "Bash(cat enrichments/*)",
      "Bash(jq * enrichments/*)",
      "Bash(mkdir -p enrichments)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          "... existing hooks ...",
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-enrichment-json.sh"
          }
        ]
      }
    ]
  }
}
```

---

## 10. Execution Playbook

### 10.1 Full Enrichment Pipeline

Run after the base Terraform analysis (`/analyze-aws-infra all`) is complete:

```
1. cd ~/aws-architecture-analysis
2. Open Claude Code
3. Run: /enrich-infrastructure all
4. Wait for enrichment across all repos (~20-40 minutes)
5. Open output/aws-architecture-enriched.drawio.xml in draw.io or Lucidchart
6. Review output/operational-posture-report.md
```

### 10.2 Single-Repo Testing

Test enrichment on one repo first:

```
1. Run: /enrich-repo compute-platform
2. Review: cat enrichments/compute-platform.enrichment.json | jq .
3. Verify CI/CD extraction matches your pipeline
4. Verify runtime connections match known service dependencies
5. If correct: /enrich-infrastructure all
```

### 10.3 Incremental Updates

When a repo's pipeline or config changes:

```
1. rm enrichments/<repo-name>.enrichment.json
2. /enrich-repo <repo-name>
3. /enrich-infrastructure synthesize   (re-runs synthesis + diagram + review)
```

### 10.4 End-to-End Pipeline

Run everything from scratch:

```
1. /discover-repos                     ← Phase 0: build manifest
2. /analyze-aws-infra all              ← Phases 1-5: Terraform analysis + base diagram + WAF
3. /enrich-infrastructure all          ← Phase 1b-4b: CI/CD + runtime + monitoring enrichment
```

All outputs coexist:
- `output/aws-architecture.drawio.xml` — Infrastructure only
- `output/aws-architecture-enriched.drawio.xml` — Infrastructure + operational context
- `output/aws-architecture-annotated.drawio.xml` — Infrastructure + WAF findings
- `output/well-architected-report.md` — Infrastructure WAF review
- `output/operational-posture-report.md` — CI/CD and monitoring review

---

## 11. Token Cost Strategy

| Component | Token Cost | Frequency | Total for 30 Repos |
|-----------|-----------|-----------|---------------------|
| Enrichment skill description | ~50 tokens | Always in context | 50 (fixed) |
| CI/CD analyzer per repo | ~600 tokens per invocation | 30× | 18,000 |
| Runtime mapper per repo | ~500 tokens per invocation | 30× | 15,000 |
| Monitoring auditor per repo | ~400 tokens per invocation | 30× | 12,000 |
| Enriched synthesizer | ~600 tokens + reads all JSONs | 1× | ~6,000 |
| Operational reviewer | ~600 tokens + reads unified model | 1× | ~5,000 |
| Enrichment validation hook | 0 tokens | Every Write | 0 |
| **Enrichment total** | | | **~56,000 tokens** |
| **Combined with base pipeline** | | | **~96,000 tokens** |

Key optimization: each specialist sub-agent starts with an **isolated, fresh context**.
The CI/CD analyzer for repo #30 doesn't carry context from repos #1–29. And each
specialist within a repo doesn't carry context from sibling specialists — the CI/CD
analyzer never sees monitoring configs, and vice versa.

The `disable-model-invocation: true` on the `enrich-infrastructure` skill means its
description doesn't consume tokens when idle. Only the `enrich-repo` skill's description
(~50 tokens) is always in context — and it's there so Claude can auto-invoke it when
the conversation context suggests enrichment would be useful.

---

## Appendix: Component Inventory

| File | Type | New/Updated | Read-only? |
|------|------|-------------|------------|
| `CLAUDE.md` | Project memory | Updated | N/A (always-on context) |
| `AGENTS.md` | Cross-platform conventions | Updated | N/A (always-on context) |
| `.claude/settings.json` | Hooks + permissions | Updated | N/A (configuration) |
| `.claude/skills/enrich-infrastructure/SKILL.md` | Skill | New | N/A (orchestrator) |
| `.claude/skills/enrich-repo/SKILL.md` | Skill | New | N/A (orchestrator) |
| `.claude/skills/operational-review/SKILL.md` | Skill | New | N/A (orchestrator) |
| `.claude/agents/cicd-analyzer.md` | Sub-agent | New | **Yes** — `disallowedTools: [Write, Edit, MultiEdit]` |
| `.claude/agents/runtime-mapper.md` | Sub-agent | New | **Yes** — `disallowedTools: [Write, Edit, MultiEdit]` |
| `.claude/agents/monitoring-auditor.md` | Sub-agent | New | **Yes** — `disallowedTools: [Write, Edit, MultiEdit]` |
| `.claude/agents/enriched-synthesizer.md` | Sub-agent | New | **Yes** — `disallowedTools: [Write, Edit, MultiEdit]` |
| `.claude/agents/operational-reviewer.md` | Sub-agent | New | **Yes** — `disallowedTools: [Write, Edit, MultiEdit]` |
| `.claude/hooks/validate-enrichment-json.sh` | PostToolUse Hook | New | N/A (deterministic script) |

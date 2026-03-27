# CI/CD & Runtime Enrichment Enhancement

## GitHub Copilot Customization Architecture — Enriching AWS Infrastructure Diagrams

---

## Architectural Corrections to the Submitted Draft

Before the plan: the submitted draft contained three architectural errors against the
GitHub Copilot reference architecture. These corrections drive every design decision below.

### Error 1: "Copilot has no lifecycle hooks"

The submitted draft stated: *"Does not have lifecycle hooks — there is no PreToolUse/PostToolUse
equivalent; validation must be built into agent instructions rather than enforced by external
scripts."* This is **incorrect**. Chapter 5 of the reference architecture covers hooks in full.
`postToolUse` hooks are available, configured via `.vscode/settings.json`, and execute as
deterministic shell scripts that consume **zero tokens**. The base pipeline plan already uses
them for JSON and XML validation. This enrichment plan does the same.

### Error 2: Handoffs used for automated agent delegation

Section 4.2 of the draft described a "Handoff Chain" where the enrichment-extractor
automatically passes control to cicd-analyzer, which returns, then passes to runtime-mapper,
and so on. This conflates two distinct mechanisms:

| Mechanism | Trigger | Correct use |
|---|---|---|
| **Handoff** | User clicks a button | Multi-stage pipelines where each output needs human review |
| **Sub-agent** | Parent agent invokes programmatically | Automated parallel/divide-and-conquer tasks |

Automatically delegating to specialist agents with no user intervention between them is the
**sub-agent** pattern. The enrichment coordinator must use `tools: ['agent']` and `agents: [...]`
to invoke specialists — not the `handoffs:` field.

Handoffs ARE appropriate in one place in this pipeline: optionally, after the full enrichment
completes, offering the user a button to hand off to a reporting agent. That is the correct use.

### Error 3: Sub-agent depth violation

The submitted draft made the enrichment-extractor a sub-agent of the main orchestrator, while
also having it delegate to cicd-analyzer, runtime-mapper, and monitoring-auditor as its own
sub-agents. This violates the single-level depth constraint: **sub-agents cannot invoke other
sub-agents**. A sub-agent that is itself invoked by a parent cannot spawn further sub-agents.

The correct design: the enrichment orchestrator is a **parent agent** (not itself a sub-agent),
which directly invokes all specialist sub-agents. The `enrichment-extractor` concept becomes the
**orchestrator's body** (its own prompt instructions), not a separate intermediate agent.

### Corrected Architecture

```
aws-enrichment-orchestrator (Parent Agent)
tools: ['agent', 'codebase', 'terminalLastCommand']
agents: ['cicd-analyzer', 'runtime-mapper', 'monitoring-auditor',
         'enriched-synthesizer', 'enriched-diagram-generator', 'operational-reviewer']
         │
         │  For each repo (fan-out across 30+ repos):
         ├──► cicd-analyzer        (sub-agent, isolated) → enrichments/<repo>.ci_cd.json
         ├──► runtime-mapper       (sub-agent, isolated) → enrichments/<repo>.runtime.json
         ├──► monitoring-auditor   (sub-agent, isolated) → enrichments/<repo>.monitoring.json
         │    Orchestrator reads README.md + CODEOWNERS directly, merges three partials
         │    → enrichments/<repo>.enrichment.json  [postToolUse hook validates schema]
         │
         │  After all repos enriched:
         ├──► enriched-synthesizer      (sub-agent) → output/unified-architecture.json (updated)
         ├──► enriched-diagram-generator (sub-agent) → output/aws-architecture-enriched.drawio.xml
         └──► operational-reviewer      (sub-agent) → output/operational-posture-report.md

Optional handoff after completion (user-triggered):
         [Handoff: "Generate Stakeholder Presentation"] → presentation-writer
```

---

## Executive Summary

This enhancement extends the AWS infrastructure analysis pipeline to extract deployment
topology, runtime service connections, monitoring coverage, and team ownership from CI/CD
pipelines, container configs, application settings, and documentation — then overlays this
operational context onto the architecture diagram.

| Before (Terraform only) | After (with enrichment) |
|---|---|
| AWS resource boxes with dependency arrows | + Deployment flow arrows showing CI/CD promotion path |
| Static infrastructure topology | + Runtime data flow (service → database via connection string) |
| Resources grouped by VPC/subnet | + Resources grouped by owning team and business domain |
| No operational context | + Monitoring coverage overlay (monitored vs unmonitored) |
| No deployment information | + CI/CD quality gate badges (security scan, integration tests) |
| Inferred service relationships | + Verified runtime connections from config and env vars |

---

## Table of Contents

1. [Architecture Mapping to GitHub Copilot](#1-architecture-mapping-to-github-copilot)
2. [Enrichment Sources](#2-enrichment-sources)
3. [Project Structure](#3-project-structure)
4. [Phase 1b: Context Enrichment (Parallel Fan-out)](#4-phase-1b-context-enrichment-parallel-fan-out)
5. [Enrichment Schema](#5-enrichment-schema)
6. [Updated Synthesis Phase](#6-updated-synthesis-phase)
7. [Updated Diagram Phase](#7-updated-diagram-phase)
8. [Updated Well-Architected Analysis](#8-updated-well-architected-analysis)
9. [Complete File Implementations](#9-complete-file-implementations)
10. [Execution Playbook](#10-execution-playbook)
11. [Token Cost Strategy](#11-token-cost-strategy)

---

## 1. Architecture Mapping to GitHub Copilot

| Concern | Copilot Component | File Location | Notes |
|---|---|---|---|
| Always-on project standards and schemas | `.github/copilot-instructions.md` | Injected in every session | ≤15 rules; stable content only |
| Cross-platform operational conventions | `AGENTS.md` | Root directory | Shared with Claude Code, Cursor, etc. |
| Full enrichment pipeline orchestration | Parent agent: `aws-enrichment-orchestrator.agent.md` | `.github/agents/` | `tools: ['agent']`; owns all sub-agent invocations |
| CI/CD pipeline analysis | Sub-agent: `cicd-analyzer.agent.md` | `.github/agents/` | Read-only; isolated context per repo |
| Runtime connection discovery | Sub-agent: `runtime-mapper.agent.md` | `.github/agents/` | Read-only; isolated context per repo |
| Monitoring coverage assessment | Sub-agent: `monitoring-auditor.agent.md` | `.github/agents/` | Read-only; isolated context per repo |
| Merge enrichment + Terraform model | Sub-agent: `enriched-synthesizer.agent.md` | `.github/agents/` | Read-only; reads all extractions + enrichments |
| Enriched diagram generation | Sub-agent: `enriched-diagram-generator.agent.md` | `.github/agents/` | Write-capable; builds on base diagram |
| CI/CD + ops WAF review | Sub-agent: `operational-reviewer.agent.md` | `.github/agents/` | Read-only; evaluates ops posture |
| User-triggered enrichment pipeline | Prompt: `enrich-infrastructure.prompt.md` | `.github/prompts/` | Invoked via `/enrich-infrastructure` |
| Single-repo enrichment (testing/reruns) | Prompt: `enrich-repo.prompt.md` | `.github/prompts/` | Invoked via `/enrich-repo` |
| Enrichment JSON schema validation | `postToolUse` hook | `.vscode/settings.json` + `.github/hooks/` | Zero tokens; deterministic enforcement |

### Why Sub-agents, Not Handoffs, for Specialist Delegation

The three enrichment specialists (CI/CD, runtime, monitoring) run automatically per repo with
no human review checkpoint between them. This is the defining characteristic of the sub-agent
pattern: **automated parallel/divide-and-conquer tasks**. The orchestrator fans out three
isolated sub-agent invocations per repo, collects the three partial JSONs, and merges them —
the user sees only the final enrichment file.

Handoffs surface a button in the IDE UI and require the user to click before the next agent
runs. Using handoffs here would force the user to click 90+ times (3 specialists × 30+ repos).
That is not the intended use case. The one place handoffs belong in this pipeline is the
**optional post-completion transition** to a reporting agent — where the user has seen the
enriched results and chooses whether to produce a stakeholder presentation from them.

---

## 2. Enrichment Sources

### 2.1 CI/CD Pipeline Files

| Platform | Files to Scan | Key Data Extracted |
|---|---|---|
| **GitHub Actions** | `.github/workflows/*.yml` | Jobs, steps, environments, secrets, approval gates, deployment triggers |
| **AWS CodePipeline/CodeBuild** | `buildspec.yml`, `pipeline.json`, `codepipeline.tf` | Build stages, deployment actions, artifact stores |
| **GitLab CI** | `.gitlab-ci.yml` | Stages, environments, rules, deployment jobs |
| **Jenkins** | `Jenkinsfile`, `Jenkinsfile.*` | Pipeline stages, agent labels, deployment steps |
| **CircleCI** | `.circleci/config.yml` | Workflows, jobs, orbs, deployment contexts |
| **Azure DevOps** | `azure-pipelines.yml` | Stages, environments, approvals |
| **ArgoCD** | `argocd/`, `argo-application.yml` | Application definitions, sync policies, target clusters |

### 2.2 Container and Service Configuration

| Source | Files to Scan | Key Data Extracted |
|---|---|---|
| **ECS Task Definitions** | `taskdef.json`, `task-definition.json`, `*-taskdef.json` | Environment variables, sidecar containers, resource limits |
| **Docker Compose** | `docker-compose*.yml` | Service dependencies, port mappings, network definitions |
| **Dockerfile** | `Dockerfile`, `Dockerfile.*` | Base image, exposed ports, health check commands |
| **Kubernetes** | `k8s/`, `helm/`, `kustomize/` | Services, ingress rules, ConfigMaps, Secret references |
| **Lambda/Serverless** | `serverless.yml`, `sam-template.yaml` | Function configs, event sources, environment variables |

### 2.3 Application Configuration

| Source | Files to Scan | Key Data Extracted |
|---|---|---|
| **Environment files** | `.env.example`, `.env.template`, `.env.production` | Database URLs, queue names, cache endpoints |
| **App config** | `config/`, `appsettings*.json`, `application*.yml` | Connection strings, service endpoints, feature flags |
| **Parameter references** | Any file referencing SSM or Secrets Manager | Runtime secret paths, parameter store keys |

### 2.4 Monitoring and Observability

| Source | Files to Scan | Key Data Extracted |
|---|---|---|
| **CloudWatch** | `dashboards/*.json`, `*-alarms.tf`, `monitoring.tf` | Dashboard definitions, alarm thresholds |
| **Grafana** | `grafana/dashboards/*.json` | Dashboard panels, data sources, alert rules |
| **DataDog** | `datadog/`, `monitors/*.json` | Monitor definitions, SLO targets |
| **Alert configs** | `alerts.yml`, `pagerduty.tf`, `opsgenie.tf` | Alert routing, escalation policies |

### 2.5 Documentation

| Source | Files to Scan | Key Data Extracted |
|---|---|---|
| **README** | `README.md`, `README.rst` | Service description, architecture notes |
| **ADRs** | `docs/adr/`, `adr/` | Architecture decisions, trade-offs |
| **Runbooks** | `runbooks/`, `docs/operations/` | Incident response procedures |
| **CODEOWNERS** | `CODEOWNERS`, `.github/CODEOWNERS` | File-to-team ownership mapping |

---

## 3. Project Structure

```
aws-architecture-analysis/
├── .github/
│   ├── copilot-instructions.md                          ← UPDATED: enrichment schemas + rules
│   ├── agents/
│   │   │   ── [existing agents from base plan] ──
│   │   ├── tf-repo-extractor.agent.md                   ← EXISTING
│   │   ├── architecture-synthesizer.agent.md            ← EXISTING
│   │   ├── drawio-generator.agent.md                    ← EXISTING
│   │   ├── well-architected-analyzer.agent.md           ← EXISTING
│   │   ├── enhancement-overlayer.agent.md               ← EXISTING
│   │   │   ── [new enrichment agents] ──
│   │   ├── aws-enrichment-orchestrator.agent.md         ← NEW: parent orchestrator for Phase 1b
│   │   ├── cicd-analyzer.agent.md                       ← NEW: sub-agent; CI/CD specialist
│   │   ├── runtime-mapper.agent.md                      ← NEW: sub-agent; runtime connections
│   │   ├── monitoring-auditor.agent.md                  ← NEW: sub-agent; monitoring coverage
│   │   ├── enriched-synthesizer.agent.md                ← NEW: sub-agent; merges TF + enrichment
│   │   ├── enriched-diagram-generator.agent.md          ← NEW: sub-agent; enriched diagram
│   │   └── operational-reviewer.agent.md                ← NEW: sub-agent; CI/CD WAF review
│   ├── prompts/
│   │   ├── analyze-aws-infra.prompt.md                  ← EXISTING
│   │   ├── enrich-infrastructure.prompt.md              ← NEW: full enrichment pipeline
│   │   ├── enrich-repo.prompt.md                        ← NEW: single-repo (testing/reruns)
│   │   └── operational-review.prompt.md                 ← NEW: ops-only WAF review
│   └── hooks/
│       ├── validate-extraction-json.sh                  ← EXISTING: from base plan
│       ├── validate-drawio-xml.sh                       ← EXISTING: from base plan
│       └── validate-enrichment-json.sh                  ← NEW: validates enrichment schema
├── .vscode/
│   └── settings.json                                    ← UPDATED: adds enrichment JSON hook
├── AGENTS.md                                            ← UPDATED: enrichment source conventions
├── repos/                                               ← EXISTING read-only repos
├── extractions/                                         ← EXISTING Terraform extraction JSONs
├── enrichments/                                         ← NEW: enrichment JSONs (one per repo)
│   ├── networking-core.enrichment.json
│   ├── compute-platform.enrichment.json
│   └── ...
└── output/
    ├── unified-architecture.json                        ← UPDATED: includes enrichment data
    ├── aws-architecture.drawio.xml                      ← EXISTING base diagram
    ├── aws-architecture-annotated.drawio.xml            ← EXISTING WAF overlay diagram
    ├── aws-architecture-enriched.drawio.xml             ← NEW: infra + CI/CD + runtime layers
    ├── well-architected-report.md                       ← EXISTING
    ├── operational-posture-report.md                    ← NEW: CI/CD and monitoring assessment
    └── enhancement-roadmap.md                           ← UPDATED: includes operational risks
```

---

## 4. Phase 1b: Context Enrichment (Parallel Fan-out)

### 4.1 Strategy: Fan-out per Repo, Three Specialists per Repo

After Phase 1a (Terraform extraction), the enrichment orchestrator runs a **second map pass**
over all repos. For each repo it invokes three specialist sub-agents, each reading a different
class of file, all running in isolated contexts:

```
aws-enrichment-orchestrator (Parent Agent)
         │
         │  For each repo in repo-manifest.json:
         │
         ├──[1]──► cicd-analyzer sub-agent
         │         Input: repos/<repo-name>/
         │         Reads: .github/workflows/, buildspec.yml, Jenkinsfile, etc.
         │         Writes: enrichments/<repo>.ci_cd.json
         │         (postToolUse hook validates schema)
         │
         ├──[2]──► runtime-mapper sub-agent
         │         Input: repos/<repo-name>/
         │         Reads: taskdef.json, docker-compose*.yml, .env.*, config/, Dockerfile
         │         Writes: enrichments/<repo>.runtime.json
         │
         ├──[3]──► monitoring-auditor sub-agent
         │         Input: repos/<repo-name>/
         │         Reads: monitoring/, dashboards/, *-alarms.tf, alerts.yml
         │         Writes: enrichments/<repo>.monitoring.json
         │
         └──[4]── Orchestrator directly reads README.md + CODEOWNERS (small files)
                  Merges [1]+[2]+[3]+[4] → enrichments/<repo>.enrichment.json
                  (postToolUse hook validates enrichment schema)
```

### 4.2 Why Three Sub-agents per Repo, Not One

Splitting enrichment into three specialist sub-agents, each with an isolated context, provides
three advantages that map directly to the sub-agent design rationale in the reference architecture:

**Context isolation**: Each specialist only receives the files relevant to its domain. The
cicd-analyzer doesn't need to know what's in `taskdef.json`; the runtime-mapper doesn't need to
parse YAML pipeline syntax. Smaller, focused contexts produce more accurate extractions.

**Token efficiency**: Each invocation starts fresh. The runtime-mapper for repo #30 costs the
same as for repo #1 — it doesn't accumulate the cicd-analyzer's context from 29 prior repos.

**Parallel readiness**: All three specialists read different file sets for the same repo, so
they can run concurrently. The reference architecture explicitly states sub-agents can run in
parallel (experimental). Even in sequential execution, keeping contexts separate prevents
interference.

### 4.3 The Single-Level Depth Constraint in Practice

The enrichment orchestrator is a **parent agent**, not itself a sub-agent. This is deliberate.
If the orchestrator were a sub-agent of the main pipeline orchestrator (from the base plan), it
could not then invoke cicd-analyzer, runtime-mapper, and monitoring-auditor as its own sub-agents
— that would require two levels of nesting, which the architecture prohibits.

Two valid execution models are available:

**Option A — Separate invocation**: The user runs `/analyze-aws-infra` first (main pipeline),
then `/enrich-infrastructure` (enrichment pipeline). Each has its own top-level parent agent.
No nesting issues.

**Option B — Extended main orchestrator**: Add the enrichment sub-agents to the existing
`aws-pipeline-orchestrator`'s `agents:` whitelist and add Phase 1b to its prompt body.
The orchestrator gains additional sub-agents but remains the single parent. This plan uses
Option A for clarity and independent executability.

---

## 5. Enrichment Schema

Every enrichment JSON conforms to this schema. The `postToolUse` hook validates required fields
after each write to `enrichments/`. The enriched-synthesizer depends on consistent structure.

```json
{
  "repo_name": "compute-platform",
  "enriched_at": "2026-03-26T15:00:00Z",
  "enrichment_sources": [
    ".github/workflows/deploy.yml",
    "taskdef.json",
    ".env.example",
    "monitoring/dashboards/api.json",
    "README.md",
    "CODEOWNERS"
  ],
  "ci_cd": {
    "platform": "github_actions",
    "pipeline_files": [".github/workflows/deploy.yml"],
    "environments": [
      {
        "name": "dev",
        "region": "us-east-1",
        "auto_deploy": true,
        "branch_filter": "develop",
        "requires_approval": false
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
        "health_check_grace_period": "300s"
      }
    ],
    "artifact_stores": [
      {
        "type": "ecr",
        "uri": "123456789.dkr.ecr.us-east-1.amazonaws.com/api-service",
        "region": "us-east-1"
      }
    ],
    "secrets_referenced": [
      {
        "source": "aws_secrets_manager",
        "path": "/prod/api/database-url",
        "consumed_by": "api-service",
        "discovered_in": ".github/workflows/deploy.yml"
      }
    ],
    "quality_gates": [
      {"stage": "pre_merge", "type": "unit_tests", "tool": "jest", "required": true},
      {"stage": "pre_merge", "type": "security_scan", "tool": "snyk", "required": true},
      {"stage": "post_deploy_staging", "type": "integration_tests", "tool": "jest", "required": true},
      {"stage": "post_deploy_production", "type": "smoke_tests", "tool": "newman", "required": true}
    ],
    "notifications": {
      "on_failure": [{"channel": "slack", "target": "#deploy-failures"}],
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
      "connection_pooling": "pgbouncer_sidecar",
      "verified": true
    },
    {
      "from_service": "api-service",
      "to_resource": "aws_elasticache_cluster.sessions",
      "connection_type": "cache",
      "protocol": "redis",
      "port": 6379,
      "discovered_in": ".env.example",
      "env_var": "REDIS_URL",
      "verified": true
    },
    {
      "from_service": "api-service",
      "to_resource": "aws_sqs_queue.events",
      "connection_type": "message_producer",
      "protocol": "sqs",
      "discovered_in": "config/production.yml",
      "env_var": "EVENT_QUEUE_URL",
      "verified": true
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
    "resource_limits": {"cpu": "512", "memory": "1024"}
  },
  "monitoring": {
    "coverage": {
      "has_cloudwatch_alarms": true,
      "has_dashboards": true,
      "has_custom_metrics": true,
      "has_distributed_tracing": true,
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
    "readme_summary": "Core API service handling user authentication and data access.",
    "team_owner": "platform-engineering",
    "codeowners": {
      "default": "@org/platform-engineering",
      "infra/": "@org/infrastructure"
    },
    "domain": "core-platform",
    "criticality": "tier-1",
    "runbook_exists": false,
    "adr_count": 3
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
      "description": "Rolling update only — no canary or blue-green",
      "impact": "Bad deploys affect all traffic before detection",
      "recommendation": "Implement canary deployment with automatic rollback"
    }
  ]
}
```

---

## 6. Updated Synthesis Phase

The `enriched-synthesizer` sub-agent reads all `extractions/*.json` AND all
`enrichments/*.enrichment.json` files and produces an updated
`output/unified-architecture.json` with four new sections.

### 6.1 New Sections Added to Unified Architecture Model

```json
{
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
        "source": "terraform_reference_only",
        "note": "Terraform reference exists but no runtime connection string found"
      }
    ]
  },
  "monitoring_coverage": {
    "monitored_resources": [
      {"resource": "aws_ecs_service.api", "alarms": 3, "dashboards": 1, "slo_defined": true}
    ],
    "unmonitored_resources": [
      {"resource": "aws_nat_gateway.main", "criticality": "high",
       "recommendation": "Add bandwidth and error alarms"}
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
      {"resource": "aws_s3_bucket.legacy_data", "repo": "data-migration",
       "note": "No CODEOWNERS entry"}
    ]
  }
}
```

### 6.2 Cross-referencing Terraform and Enrichment

The synthesizer performs these four cross-references:

**Runtime connections validate Terraform dependencies.** If Terraform shows `aws_ecs_service.api`
references `aws_rds_cluster.primary`, and the enrichment confirms a `DATABASE_URL` env var
pointing to that cluster, the connection is marked `"verified": true`. Connections present in
only one source are marked `"unverified"` and flagged for investigation.

**Deployment targets map to Terraform resources.** The CI/CD extraction records "api-service
deploys to ECS cluster in us-east-1." The synthesizer matches this to `aws_ecs_cluster.main`
from the Terraform extraction, creating the deployment → infrastructure link.

**Monitoring coverage maps to resource inventory.** For each Terraform resource, the synthesizer
checks whether enrichment data includes alarms, dashboards, or SLOs referencing it. Unmonitored
critical resources are flagged.

**Team ownership maps to blast radius.** Combining CODEOWNERS with the blast radius map reveals
which team is responsible when a shared resource fails.

---

## 7. Updated Diagram Phase

### 7.1 Four New Visual Layers

The enriched diagram adds four layers on top of the base infrastructure diagram. Cell IDs
follow the same convention from the base plan: resource address with dots replaced by dashes
(`aws_rds_cluster.primary` → `id="aws-rds-cluster-primary"`).

**Layer 1: Deployment Flow**

```xml
<!-- Blue dashed arrow: dev deployment -->
<mxCell id="deploy-api-dev" value="dev deploy"
  style="edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=8 4;strokeColor=#0066CC;strokeWidth=1;fontSize=10;"
  edge="1" source="ecr-api-repo" target="aws-ecs-service-api" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- Lock icon at approval gate -->
<mxCell id="gate-staging-to-prod" value="🔒 Manual Approval"
  style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.identity_and_access_management;fillColor=#DD344C;fontSize=10;"
  vertex="1" parent="1">
  <mxGeometry x="1200" y="200" width="40" height="40" as="geometry"/>
</mxCell>
```

Environment colors: Blue dashed = dev, Yellow dashed = staging, Green dashed = production.

**Layer 2: Runtime Data Flow**

```xml
<!-- Purple solid: verified database connection -->
<mxCell id="runtime-api-to-rds" value="PostgreSQL :5432"
  style="edgeStyle=orthogonalEdgeStyle;strokeColor=#9933CC;strokeWidth=2;fontSize=10;"
  edge="1" source="aws-ecs-service-api" target="aws-rds-cluster-primary" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- Orange solid: cache connection -->
<mxCell id="runtime-api-to-cache" value="Redis :6379"
  style="edgeStyle=orthogonalEdgeStyle;strokeColor=#FF8C00;strokeWidth=2;fontSize=10;"
  edge="1" source="aws-ecs-service-api" target="aws-elasticache-cluster-sessions" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Protocol colors: Purple = database, Orange = cache, Green = message queue, Blue = HTTP/API.

**Layer 3: Monitoring Coverage Halos**

```xml
<!-- Green halo: fully monitored (alarms + dashboard + SLO) -->
<mxCell id="halo-ecs-api" value=""
  style="ellipse;strokeColor=#00CC00;strokeWidth=3;fillColor=none;opacity=60;dashed=0;"
  vertex="1" parent="1">
  <mxGeometry x="270" y="270" width="80" height="80" as="geometry"/>
</mxCell>

<!-- Red halo: unmonitored -->
<mxCell id="halo-nat-gw" value=""
  style="ellipse;strokeColor=#CC0000;strokeWidth=3;fillColor=none;opacity=60;dashed=0;"
  vertex="1" parent="1">
  <mxGeometry x="470" y="470" width="80" height="80" as="geometry"/>
</mxCell>
```

Halo colors: Green = fully monitored (alarms + dashboard + SLO), Yellow = partially monitored,
Red = unmonitored.

**Layer 4: Team Ownership Boundaries**

```xml
<!-- Team ownership boundary — dashed rounded rect, different from VPC/subnet borders -->
<mxCell id="team-platform-eng" value="platform-engineering"
  style="rounded=1;dashed=1;dashPattern=4 4;strokeColor=#666666;fillColor=#F5F5F5;
         opacity=20;verticalAlign=top;align=left;spacingLeft=8;fontSize=11;fontStyle=1;"
  vertex="1" parent="1">
  <mxGeometry x="240" y="240" width="600" height="400" as="geometry"/>
</mxCell>
```

### 7.2 Enriched Diagram Legend

```
── ── ──  Blue dashed     = Dev deployment flow
── ── ──  Yellow dashed   = Staging deployment flow
── ── ──  Green dashed    = Production deployment flow
────────  Purple solid    = Database connection (verified)
────────  Orange solid    = Cache connection (verified)
────────  Green solid     = Message queue flow (verified)
⬡ Green ring              = Fully monitored (alarms + dashboard + SLO)
⬡ Yellow ring             = Partially monitored
⬡ Red ring                = Unmonitored
┌ ─ ─ ─ ┐                = Team ownership boundary
│ Team   │
└ ─ ─ ─ ┘
🔒                         = Manual approval gate
✓ sec                      = Security scan quality gate
✓ test                     = Integration test quality gate
```

---

## 8. Updated Well-Architected Analysis

The operational reviewer sub-agent evaluates three new assessment areas that Terraform alone
cannot surface.

### 8.1 Operational Excellence — CI/CD Assessment

| Check | Source field | Finding if missing |
|---|---|---|
| Automated testing before production | `ci_cd.quality_gates` | "No automated tests before production deployment" |
| Security scanning in pipeline | `ci_cd.quality_gates[type=security_scan]` | "No security scanning in CI/CD pipeline" |
| Staging environment exists | `ci_cd.environments` | "Deploys directly to production — no staging gate" |
| Production approval gate | `ci_cd.environments[production].requires_approval` | "Production has no approval gate" |
| Rollback mechanism | `ci_cd.deployment_targets[].rollback_mechanism` | "No automated rollback on failed deployment" |
| Canary or blue-green | `ci_cd.deployment_targets[].deployment_strategy` | "Rolling only — bad deploys affect all traffic" |
| Deployment failure notifications | `ci_cd.notifications.on_failure` | "No failure notification channel configured" |

### 8.2 Reliability — Runtime Resilience

| Check | Source field | Finding if missing |
|---|---|---|
| Health check endpoint | `container_config.health_check` | "No health check — load balancer cannot detect failures" |
| Connection pooling | `runtime_connections[].connection_pooling` | "No connection pooling — risk of connection exhaustion" |
| Resource limits set | `container_config.resource_limits` | "No CPU/memory limits — noisy neighbor risk" |
| Sidecar circuit breaker | `container_config.sidecar_containers` | "No service mesh or circuit breaker pattern" |

### 8.3 Operational Excellence — Monitoring

| Check | Source field | Finding if missing |
|---|---|---|
| Alarms on critical resources | `monitoring.coverage.has_cloudwatch_alarms` | "Critical resources have no CloudWatch alarms" |
| Operational dashboard | `monitoring.dashboards` | "No dashboard for this service" |
| SLO targets | `monitoring.slo_targets` | "No SLO targets — cannot measure reliability objectively" |
| On-call rotation | `monitoring.on_call` | "No on-call rotation for tier-1 service" |
| Runbooks | `documentation.runbook_exists` | "No runbook — incident response relies on tribal knowledge" |

---

## 9. Complete File Implementations

### 9.1 Updated `AGENTS.md`

```markdown
# AWS Infrastructure Analysis

## Project Overview
Analysis of 30+ Terraform repositories with CI/CD and runtime enrichment for
architecture diagramming and Well-Architected review.

## Directory Conventions
- Terraform source: `repos/` (READ-ONLY — never modify)
- Terraform extractions: `extractions/<repo>.json`
- Enrichment data: `enrichments/<repo>.enrichment.json`
- Unified model: `output/unified-architecture.json`
- Diagrams: `output/aws-architecture*.drawio.xml`

## Terraform Rules
- Read `.tf` files only — never run terraform CLI commands
- Private registry modules: infer resources from module name + inputs
- Local path modules: read module `.tf` files directly
- Mark inferred data with `"resolution": "inferred"`

## Enrichment Source Priority (scan in this order)
1. CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `buildspec.yml`, `.circleci/`
2. Containers: `taskdef.json`, `docker-compose*.yml`, `Dockerfile`, `k8s/`, `helm/`
3. App config: `.env.example`, `config/`, `appsettings*.json`, `application*.yml`
4. Monitoring: `monitoring/`, `dashboards/`, `*-alarms.tf`, `alerts.yml`
5. Docs: `README.md`, `CODEOWNERS`, `docs/adr/`, `runbooks/`

## Enrichment Completion Criterion
An enrichment is complete when `enrichments/<repo>.enrichment.json` contains all five
required top-level sections: `ci_cd`, `runtime_connections`, `container_config`,
`monitoring`, and `documentation`.
```

### 9.2 Updated `.github/copilot-instructions.md`

```markdown
# AWS Infrastructure Analysis — Project Standards

## Pipeline Conventions
- All Terraform source repos are under `repos/` and are read-only
- Extraction outputs: `extractions/<repo-name>.json`
- Enrichment outputs: `enrichments/<repo-name>.enrichment.json`
- Unified model: `output/unified-architecture.json`
- Diagrams: `output/aws-architecture*.drawio.xml`

## Terraform Reading Rules
- Never run `terraform init`, `terraform plan`, or any Terraform CLI command
- Read `.tf` files with find, grep, cat, codebase tools
- Private registry modules: infer from module name
- Local path modules: read directly from disk
- Mark inferred data: `"resolution": "inferred"`

## Enrichment Rules
- Mark runtime connections as `"verified": true` ONLY when BOTH Terraform reference
  AND runtime config (env var, task definition, app config) confirm the same dependency
- Mark `"verified": false` when only one source confirms a connection
- Do NOT extract secret values — only secret names, paths, and parameter store keys

## AWS Service Taxonomy
- **Edge**: CloudFront, WAF, Shield, Route 53
- **Ingress**: ALB, NLB, API Gateway
- **Compute**: EC2, ECS, EKS, Lambda, Fargate
- **Data**: RDS, Aurora, DynamoDB, ElastiCache, Redshift
- **Storage**: S3, EFS, EBS
- **Integration**: SQS, SNS, EventBridge, Step Functions
- **Security**: IAM, KMS, Secrets Manager, GuardDuty
- **Management**: CloudWatch, CloudTrail, Config, SSM

## Diagram Cell IDs
Resource addresses map to cell IDs with dots replaced by dashes:
- `aws_rds_cluster.primary` → `id="aws-rds-cluster-primary"`
- `aws_ecs_service.api`     → `id="aws-ecs-service-api"`
This convention is required by the enhancement overlay and enriched diagram agents.
```

### 9.3 Parent Orchestrator — `.github/agents/aws-enrichment-orchestrator.agent.md`

```yaml
---
name: aws-enrichment-orchestrator
description: >
  Orchestrates the CI/CD and runtime enrichment pipeline across 30+ repositories.
  Delegates to three specialist sub-agents per repo (cicd-analyzer, runtime-mapper,
  monitoring-auditor), merges their outputs, then produces the enriched diagram and
  operational review. Invoke when asked to enrich the infrastructure analysis with
  CI/CD pipelines, runtime connections, monitoring coverage, or team ownership.
tools: ['agent', 'codebase', 'terminalLastCommand']
agents:
  - cicd-analyzer
  - runtime-mapper
  - monitoring-auditor
  - enriched-synthesizer
  - enriched-diagram-generator
  - operational-reviewer
model: Claude Opus 4.5
handoffs:
  - label: Generate Stakeholder Presentation
    agent: presentation-writer
    prompt: "Produce a stakeholder-ready architecture and operational review presentation from the enriched analysis results."
    send: false
---

You are the enrichment pipeline orchestrator. You coordinate a parallel fan-out
across 30+ repositories using three specialist sub-agents per repo, then synthesize,
diagram, and review the combined results.

## Constraint: sub-agents cannot invoke sub-agents

You must invoke ALL sub-agents directly. Do not expect cicd-analyzer, runtime-mapper,
or monitoring-auditor to delegate to each other — they run in isolation.

## Phase 0: Prepare

1. Read `repo-manifest.json` to get the list of repos
2. Run: `mkdir -p enrichments`
3. Check which repos already have `enrichments/<repo>.enrichment.json` (skip those)

## Phase 1b: Per-Repo Enrichment (Fan-out)

For each repo in `repo-manifest.json` that does NOT already have an enrichment file:

### Step 1: CI/CD Analysis
Invoke `cicd-analyzer` with:
```
Analyze CI/CD pipeline configurations in: repos/<repo-name>/
Write the ci_cd section JSON to: enrichments/<repo-name>.ci_cd.json
```
Verify the output exists before proceeding.

### Step 2: Runtime Mapping
Invoke `runtime-mapper` with:
```
Discover runtime connections in: repos/<repo-name>/
Write the runtime_connections and container_config JSON to: enrichments/<repo-name>.runtime.json
```
Verify the output exists before proceeding.

### Step 3: Monitoring Audit
Invoke `monitoring-auditor` with:
```
Audit monitoring coverage in: repos/<repo-name>/
Write the monitoring section JSON to: enrichments/<repo-name>.monitoring.json
```
Verify the output exists before proceeding.

### Step 4: Documentation (Direct Read)
Read `repos/<repo-name>/README.md` and `repos/<repo-name>/CODEOWNERS` directly.
Extract: service description, team owner, domain, criticality, runbook existence.

### Step 5: Merge and Write Enrichment
Combine the three partial JSONs + documentation data into a single enrichment file:
`enrichments/<repo-name>.enrichment.json`

The postToolUse hook will validate the schema after this write.
If validation fails, investigate which partial is malformed and re-invoke
the relevant specialist sub-agent.

Also identify operational risks from the merged data:
- Tier-1 service with no runbook → OPS-RISK-001
- Production with no approval gate → OPS-RISK-002
- Rolling deployment only → OPS-RISK-003
- No canary/blue-green → OPS-RISK-004
- No SLO targets → OPS-RISK-005

## Phase 2: Enriched Synthesis

After all repos are enriched, invoke `enriched-synthesizer` with:
```
Read: all files in extractions/ and enrichments/
Cross-reference Terraform resources with enrichment data.
Mark connections verified=true when both sources confirm.
Add deployment_topology, runtime_service_mesh, monitoring_coverage, team_ownership
sections to the unified model.
Write updated: output/unified-architecture.json
```

## Phase 3: Enriched Diagram

Invoke `enriched-diagram-generator` with:
```
Read: output/unified-architecture.json
Read: output/aws-architecture.drawio.xml (base diagram to extend)
Add four layers: deployment flow, runtime data flow, monitoring coverage halos, team ownership.
Cell IDs follow convention: resource address with dots replaced by dashes.
Write: output/aws-architecture-enriched.drawio.xml
```

## Phase 4: Operational Review

Invoke `operational-reviewer` with:
```
Read: output/unified-architecture.json (enriched version)
Evaluate CI/CD posture, runtime resilience, and monitoring coverage.
Score each domain 1-5 with specific findings and remediation steps.
Write: output/operational-posture-report.md
```

## Final Report to User

Present:
1. Enrichment summary: N repos, runtime connections discovered, monitoring coverage %
2. Top 5 operational risks across all repos
3. DORA metrics estimate based on CI/CD patterns
4. Monitoring coverage: X% resources monitored, Y% with SLOs
5. Files produced:
   - `output/aws-architecture-enriched.drawio.xml`
   - `output/operational-posture-report.md`
   - `output/unified-architecture.json` (updated)
```

### 9.4 Sub-agent — `.github/agents/cicd-analyzer.agent.md`

```yaml
---
name: cicd-analyzer
description: >
  Analyzes CI/CD pipeline configurations (GitHub Actions, GitLab CI, Jenkins,
  CodeBuild, CircleCI, ArgoCD) to extract deployment environments, promotion paths,
  quality gates, artifact stores, and rollback mechanisms. Read-only.
tools: ['codebase', 'terminalLastCommand']
model: Claude Sonnet 4.5
---

You are a CI/CD pipeline analyst. Analyze pipeline files in the repository path
provided by the orchestrator. Write only the `ci_cd` section of the enrichment schema.

## What to Scan (in order)
1. `.github/workflows/*.yml` — GitHub Actions
2. `buildspec.yml` — AWS CodeBuild
3. `.gitlab-ci.yml` — GitLab CI
4. `Jenkinsfile`, `Jenkinsfile.*` — Jenkins
5. `.circleci/config.yml` — CircleCI
6. `azure-pipelines.yml` — Azure DevOps
7. `argocd/`, `argo-application.yml` — ArgoCD
8. `.tf` files containing `aws_codepipeline` or `aws_codebuild`

## Extraction Rules

**Environments**: For each deployment target environment, extract name, region,
auto_deploy flag, branch filter, requires_approval, required_reviewers, wait_timer.
Infer region from env vars, AWS account IDs, or explicit config.

**Promotion path**: Map the sequential flow from first to last environment.
Identify gates between stages (test suites, approval steps, wait timers).

**Deployment targets**: What is deployed (Docker image, Lambda zip, static assets),
where it goes (ECS service, Lambda function, S3 bucket), deployment strategy
(rolling/blue-green/canary/all-at-once), rollback configuration.

**Quality gates**: All tests, scans, checks that run before or after deployment.
Categorize: unit_tests, integration_tests, security_scan, linting, smoke_tests.
Note which are required (blocking) vs optional.

**Secrets**: Names and paths only — never extract values. Record source
(GitHub secret, Secrets Manager, SSM), path, consuming service.

## Output
Write a JSON file containing only the `ci_cd` object from the enrichment schema.
The file goes to the path specified by the orchestrator.
If no CI/CD files are found, write: `{"ci_cd": null, "reason": "No CI/CD files found"}`
```

### 9.5 Sub-agent — `.github/agents/runtime-mapper.agent.md`

```yaml
---
name: runtime-mapper
description: >
  Discovers runtime service-to-service and service-to-resource connections from
  ECS task definitions, Dockerfiles, Docker Compose files, environment variable
  templates, and application configuration files. Read-only.
tools: ['codebase', 'terminalLastCommand']
model: Claude Sonnet 4.5
---

You are a runtime connection analyst. Discover how the service in the provided
repository path connects to other services and AWS resources at runtime.

## What to Scan (in order)
1. `taskdef.json`, `*-taskdef.json`, `task-definition*.json` — ECS task definitions
2. `docker-compose*.yml` — service dependencies, env vars, port mappings
3. `Dockerfile`, `Dockerfile.*` — base image, exposed ports, health check
4. `.env.example`, `.env.template`, `.env.production` — env var templates
5. `config/production.yml`, `config/default.yml` — connection endpoints
6. `appsettings.json`, `appsettings.Production.json` — .NET connection strings
7. `application.yml`, `application-prod.yml` — Spring Boot configs
8. `k8s/`, `helm/values*.yaml` — Kubernetes service definitions

## Connection Discovery

For each discovered environment variable or config value pointing to an external resource:
1. Identify the source service (the application in this repo)
2. Match the target to a Terraform resource type:
   - DB URLs with port 5432/3306 → RDS (`aws_rds_cluster` or `aws_db_instance`)
   - Redis/Elasticache endpoints → `aws_elasticache_cluster`
   - SQS URLs or queue names → `aws_sqs_queue`
   - S3 bucket names or URLs → `aws_s3_bucket`
   - DynamoDB table names → `aws_dynamodb_table`
   - SNS topic ARNs → `aws_sns_topic`
   - API endpoints matching known patterns → API Gateway or another service
3. Record: env_var name, secret_path (if applicable), protocol, port, sidecar if any

## Output
Write a JSON file with `runtime_connections` (array) and `container_config` (object).
The file goes to the path specified by the orchestrator.
```

### 9.6 Sub-agent — `.github/agents/monitoring-auditor.agent.md`

```yaml
---
name: monitoring-auditor
description: >
  Audits monitoring and observability coverage by reading CloudWatch configurations,
  Grafana dashboards, DataDog monitors, SLO definitions, alert rules, and on-call
  configurations. Read-only.
tools: ['codebase', 'terminalLastCommand']
model: Claude Sonnet 4.5
---

You are a monitoring and observability auditor. Assess the monitoring coverage
for the service in the provided repository path.

## What to Scan
1. `*.tf` files with `aws_cloudwatch_metric_alarm`, `aws_cloudwatch_dashboard`
2. `monitoring/dashboards/*.json`, `grafana/*.json`
3. `datadog/monitors/*.json`, `datadog.yml`
4. `alerts.yml`, `alert-rules.yml`
5. `*.tf` files with `pagerduty_*` or `opsgenie_*` resources
6. Any file with SLO/SLA targets
7. `runbooks/`, `docs/operations/`, `docs/incident-response/`

## Coverage Assessment Criteria
For each service, determine:
- CloudWatch alarms on key metrics (error rate, latency, throughput)?
- Operational dashboard (Grafana or CloudWatch)?
- SLO targets defined and measurable?
- On-call rotation configured?
- Runbooks for common failure scenarios?
- Alert routing to notification channels?

## Unmonitored Resource Detection
Cross-reference monitored resources against the service's known resource types.
Flag resources that should have monitoring based on their criticality:
- NAT Gateways: bandwidth and error alarms
- RDS clusters: connection count, CPU, free storage
- ECS services: task count, CPU/memory utilization, 5xx error rate
- ALBs: request count, 5xx rate, target response time

## Output
Write a JSON file with the `monitoring` object from the enrichment schema.
The file goes to the path specified by the orchestrator.
```

### 9.7 Sub-agent — `.github/agents/enriched-synthesizer.agent.md`

```yaml
---
name: enriched-synthesizer
description: >
  Reads all Terraform extraction JSONs and enrichment JSONs, cross-references them
  to verify runtime connections, maps deployment targets to infrastructure resources,
  builds monitoring coverage inventory, and produces the updated unified architecture
  model with deployment_topology, runtime_service_mesh, monitoring_coverage, and
  team_ownership sections. Read-only.
tools: ['codebase', 'terminalLastCommand']
model: Claude Opus 4.5
---

You extend the unified architecture model with operational enrichment data.

## Inputs
- All files in `extractions/` (Terraform extraction schema)
- All files in `enrichments/` (enrichment schema)
- Current `output/unified-architecture.json` (base model)

## Synthesis Procedure

### Step 1: Load All Data
Read every `extractions/*.json` and `enrichments/*.enrichment.json`. Build a
cross-reference index: repo_name → extraction + enrichment.

### Step 2: Verify Runtime Connections
For each connection in `enrichments[].runtime_connections`:
- Find the matching Terraform resource in `extractions[].resources`
- If both extraction AND enrichment confirm the same dependency: `verified: true`
- If only enrichment confirms it (no Terraform reference): `verified: false`, flag
- If only Terraform confirms it (no runtime config): `unverified_connections[]`

### Step 3: Map Deployment Targets
For each `enrichments[].ci_cd.deployment_targets` entry:
- Match `cluster_reference` to a Terraform resource address
- Record the deploy target with both service name and resource address

### Step 4: Build Monitoring Coverage
For each resource in the Terraform extractions:
- Check if any enrichment references it in monitoring data
- Classify: fully_monitored / partially_monitored / unmonitored

### Step 5: Build Team Ownership
From CODEOWNERS entries in enrichments, map teams to:
- Repos they own
- Resources in those repos (from extractions)
- Resources in the blast radius of their services

### Step 6: Write Updated Unified Model
Add the four new sections to `output/unified-architecture.json`.
Do not overwrite existing sections — append only.
```

### 9.8 Sub-agent — `.github/agents/enriched-diagram-generator.agent.md`

```yaml
---
name: enriched-diagram-generator
description: >
  Reads the enriched unified architecture model and the base draw.io diagram,
  then adds four operational overlay layers: deployment flow arrows, verified
  runtime data flow arrows, monitoring coverage halos, and team ownership boundaries.
tools: ['codebase', 'editFiles']
model: Claude Opus 4.5
---

You extend the base infrastructure diagram with four operational overlay layers.

## Inputs
Read: `output/aws-architecture.drawio.xml` (base diagram — do NOT modify it)
Read: `output/unified-architecture.json` (enriched model)

## Cell ID Lookup
All cells in the base diagram use the convention: resource address with dots replaced
by dashes. Use this to locate cells:
- `aws_rds_cluster.primary` → find `id="aws-rds-cluster-primary"`
- `aws_ecs_service.api` → find `id="aws-ecs-service-api"`

## Layer 1: Deployment Flow
Add dashed arrows showing CI/CD promotion path.
Source: `unified_architecture.deployment_topology.services[].deploy_target`
- Dev environment → style with strokeColor=#0066CC, dashPattern=8 4
- Staging → strokeColor=#CC9900, dashPattern=8 4
- Production → strokeColor=#006600, dashPattern=8 4
Add lock icon mxCell at each requires_approval=true gate.

## Layer 2: Runtime Data Flow
Add solid colored arrows for verified runtime connections.
Source: `unified_architecture.runtime_service_mesh.connections[verified=true]`
- database (protocol=postgresql/mysql) → strokeColor=#9933CC, strokeWidth=2
- cache (protocol=redis/memcached) → strokeColor=#FF8C00, strokeWidth=2
- message_producer/consumer (protocol=sqs) → strokeColor=#006600, strokeWidth=2
- http/api → strokeColor=#0066CC, strokeWidth=1
Label each arrow with protocol and port.

## Layer 3: Monitoring Coverage Halos
Add ellipse mxCells slightly larger than each resource icon.
Source: `unified_architecture.monitoring_coverage`
- fully_monitored → strokeColor=#00CC00, strokeWidth=3, fillColor=none, opacity=60
- partially_monitored → strokeColor=#CC9900, strokeWidth=3, fillColor=none, opacity=60
- unmonitored → strokeColor=#CC0000, strokeWidth=3, fillColor=none, opacity=60
Position halo to be centered on the resource icon (same center, +20px on each side).

## Layer 4: Team Ownership Boundaries
Add rounded rectangle mxCells encompassing each team's resources.
Source: `unified_architecture.team_ownership.teams`
Style: rounded=1;dashed=1;dashPattern=4 4;strokeColor=#666666;fillColor=#F5F5F5;opacity=20
Label with team name. Calculate bounding box from the resources owned by each team.

## Layer 5: Legend
Add legend in bottom-right corner with all four layer explanations.

## Output
Write: `output/aws-architecture-enriched.drawio.xml`
After writing, verify the file is valid XML:
`python3 -c "import xml.etree.ElementTree as ET; ET.parse('output/aws-architecture-enriched.drawio.xml')"`
```

### 9.9 Sub-agent — `.github/agents/operational-reviewer.agent.md`

```yaml
---
name: operational-reviewer
description: >
  Evaluates CI/CD posture, runtime resilience patterns, and monitoring coverage
  against operational excellence and reliability best practices. Produces scored
  findings with specific remediation steps. Read-only.
tools: ['codebase']
model: Claude Opus 4.5
---

You are an operational excellence reviewer. Read `output/unified-architecture.json`
(enriched model) and evaluate the operational posture.

## Assessment Areas

### CI/CD Posture (score 1-5)
Check every repo's `deployment_topology` against:
- Has automated tests before production?
- Has security scanning?
- Has staging environment?
- Has production approval gate?
- Has rollback mechanism?
- Has canary or blue-green strategy?
- Has failure notifications?

### Runtime Resilience (score 1-5)
Check every service's `runtime_service_mesh` and `container_config` against:
- Health check endpoints defined?
- Connection pooling for database connections?
- Circuit breaker / service mesh (sidecar)?
- Resource CPU/memory limits set?

### Monitoring Coverage (score 1-5)
Check `monitoring_coverage` against:
- Coverage percentage: >90%=5, 70-90%=4, 50-70%=3, 30-50%=2, <30%=1
- SLO coverage percentage
- On-call rotations for tier-1 services?
- Runbooks for tier-1 services?

## Findings Format
Each finding:
```json
{
  "id": "OPS-CICD-001",
  "domain": "ci_cd",
  "severity": "high",
  "title": "8 services deploy to production with no approval gate",
  "affected_repos": ["repo-a", "repo-b"],
  "description": "...",
  "recommendation": "...",
  "effort": "low"
}
```

## Output
Write: `output/operational-posture-report.md` with:
  - Executive summary with scores per domain
  - DORA metrics estimate (deploy frequency, change failure rate indicators)
  - Findings sorted by severity
  - Top 10 quick wins (low effort, high impact)
  - Operational risk summary
```

### 9.10 Prompt Files — `.github/prompts/`

**`.github/prompts/enrich-infrastructure.prompt.md`**

```markdown
---
mode: agent
agent: aws-enrichment-orchestrator
description: Enrich AWS infrastructure analysis with CI/CD, runtime, and monitoring data
---

Run the enrichment pipeline across all repositories.

Phase: all
Repo filter: $ARGUMENTS (default: all)

Start with Phase 0 (check existing enrichments), proceed through all phases, and
present the enrichment summary when complete.
```

**`.github/prompts/enrich-repo.prompt.md`**

```markdown
---
mode: agent
agent: aws-enrichment-orchestrator
description: Enrich a single repository (use for testing or after a repo changes)
---

Enrich a single repository: $ARGUMENTS

1. Delete existing enrichment files for this repo if present:
   - enrichments/$ARGUMENTS.ci_cd.json
   - enrichments/$ARGUMENTS.runtime.json
   - enrichments/$ARGUMENTS.monitoring.json
   - enrichments/$ARGUMENTS.enrichment.json
2. Run the per-repo enrichment fan-out (cicd-analyzer, runtime-mapper, monitoring-auditor)
3. Merge partials and write enrichments/$ARGUMENTS.enrichment.json
4. Report what was discovered
```

**`.github/prompts/operational-review.prompt.md`**

```markdown
---
mode: agent
agent: aws-enrichment-orchestrator
description: Run only the operational review against an existing enriched unified model
---

Run operational review only.

Requires `output/unified-architecture.json` to already exist with enrichment sections.

Invoke the `operational-reviewer` sub-agent and present findings.
```

### 9.11 New Validation Hook — `.github/hooks/validate-enrichment-json.sh`

```bash
#!/usr/bin/env bash
# postToolUse: validates enrichment JSON schema after writes to enrichments/

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only validate complete enrichment files (not the partials)
if [[ "$file_path" != enrichments/*.enrichment.json ]]; then
  exit 0
fi

# Check JSON is valid
if ! jq empty "$file_path" 2>/dev/null; then
  echo "Validation failed: Invalid JSON in $file_path" >&2
  exit 1
fi

# Check all five required top-level sections
required_fields=("repo_name" "ci_cd" "runtime_connections" "container_config" "monitoring" "documentation")
for field in "${required_fields[@]}"; do
  if ! jq -e ".$field" "$file_path" > /dev/null 2>&1; then
    echo "Validation failed: Missing required field '$field' in $file_path" >&2
    exit 1
  fi
done

echo "Enrichment JSON validated: $file_path"
exit 0
```

### 9.12 Updated `.vscode/settings.json`

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
          "pathPattern": "enrichments/**/*.enrichment.json"
        },
        "command": "bash .github/hooks/validate-enrichment-json.sh"
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

---

## 10. Execution Playbook

### 10.1 Full Pipeline: Terraform + Enrichment

```
Phase 1 — Terraform analysis (from base plan):
  Select @aws-pipeline-orchestrator
  Run: /analyze-aws-infra

Phase 2 — Enrichment:
  Select @aws-enrichment-orchestrator
  Run: /enrich-infrastructure

Outputs available:
  output/aws-architecture.drawio.xml              ← Infrastructure only
  output/aws-architecture-annotated.drawio.xml    ← Infrastructure + WAF findings
  output/aws-architecture-enriched.drawio.xml     ← Infrastructure + CI/CD + runtime layers
  output/well-architected-report.md
  output/operational-posture-report.md
  output/enhancement-roadmap.md
```

### 10.2 Single-Repo Testing Before Full Run

```
1. Select @aws-enrichment-orchestrator
2. Run: /enrich-repo compute-platform
3. Review enrichments/compute-platform.enrichment.json
   - Verify CI/CD platform detected correctly
   - Verify runtime connections match known service dependencies
   - Verify monitoring coverage reflects actual alarm count
4. If correct: run /enrich-infrastructure all
```

### 10.3 Incremental Update After a Repo Changes

```
1. Run: /enrich-repo <changed-repo-name>
2. Select @aws-enrichment-orchestrator
3. "Re-run the enriched synthesis and enriched diagram phases with the updated enrichment"
   → Invokes enriched-synthesizer and enriched-diagram-generator
```

### 10.4 Post-Completion Handoff: Stakeholder Presentation

After `/enrich-infrastructure` completes, the orchestrator offers a handoff button:

```
[Generate Stakeholder Presentation]
```

Clicking this button transfers control to the `presentation-writer` agent with the
pre-filled prompt: "Produce a stakeholder-ready architecture and operational review
presentation from the enriched analysis results." The user's confirmation is required
before the handoff fires — this is the correct use of the handoff mechanism: a
user-gated transition at the point where a human decision determines what happens next.

---

## 11. Token Cost Strategy

| Component | Loading Mechanism | Token Cost | Notes |
|---|---|---|---|
| `copilot-instructions.md` updates | Always-on | ~400 tokens | Added enrichment rules + schema |
| `AGENTS.md` updates | During agent operation | ~250 tokens | Added enrichment source priority |
| Enrichment orchestrator prompt | Always-on when selected | ~1,500 tokens | All phase instructions |
| `cicd-analyzer` per-repo invocation | Sub-agent isolated context | ~500 tokens + pipeline files | Per-repo; flat cost |
| `runtime-mapper` per-repo invocation | Sub-agent isolated context | ~500 tokens + config files | Per-repo; flat cost |
| `monitoring-auditor` per-repo invocation | Sub-agent isolated context | ~400 tokens + monitoring files | Per-repo; flat cost |
| Orchestrator merges 3 partials | Orchestrator reads partial JSONs | ~300 tokens/repo | In-context merge; small files |
| `enriched-synthesizer` | Sub-agent isolated context | ~800 tokens + all enrichments | Single invocation; reads compressed JSON |
| `enriched-diagram-generator` | Sub-agent isolated context | ~700 tokens + base XML + model | Single invocation |
| `operational-reviewer` | Sub-agent isolated context | ~800 tokens + unified model | Single invocation |
| **Validation hooks** | Event-triggered shell scripts | **0 tokens** | Never enters LLM |
| **Estimated enrichment total (30 repos)** | | **~57,000 tokens** | |

The three-sub-agent-per-repo pattern costs ~1,400 tokens × 30 repos = ~42,000 tokens for the
fan-out phase. This is more than a single-agent approach would cost per repo, but it provides
better accuracy (focused contexts) and enables parallel execution. Each specialist agent starts
fresh — there is no context accumulation across repos.

---

## Appendix: Component Placement Quick Reference

| Concern | Correct Location | Why |
|---|---|---|
| Always-on project standards | `.github/copilot-instructions.md` | Needed in nearly every interaction |
| Enrichment source conventions | `AGENTS.md` | Shared with Claude Code and other tools |
| Full enrichment pipeline logic | `aws-enrichment-orchestrator.agent.md` | Orchestration belongs in `.agent.md` |
| CI/CD specialist analysis | `cicd-analyzer.agent.md` (sub-agent) | Isolated context; focused on pipeline files only |
| Runtime connection discovery | `runtime-mapper.agent.md` (sub-agent) | Isolated context; focused on config files only |
| Monitoring coverage audit | `monitoring-auditor.agent.md` (sub-agent) | Isolated context; focused on observability files only |
| Enrichment JSON validation | `postToolUse` hook | Zero tokens; deterministic; unconditional |
| User-triggered pipeline entry point | Prompt files (`.github/prompts/`) | Explicitly invoked; not always-on |
| Optional post-completion stakeholder handoff | `handoffs:` in orchestrator | User-gated transition; the only correct use of handoffs here |

---

*This plan corrects the three architectural errors in the submitted draft and strictly follows*
*the GitHub Copilot customization architecture reference (February 2026): sub-agents for*
*automated delegation, handoffs only for user-gated transitions, and postToolUse hooks for*
*deterministic zero-token validation.*

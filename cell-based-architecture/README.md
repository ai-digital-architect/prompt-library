# Cell-Based & Hexagonal Architecture Reference

A reference library of guides, skills, and analysis for two complementary architecture patterns: **Cell-Based Architecture** and **Hexagonal Architecture** (Ports and Adapters). Materials are role-stratified into architect-level strategy guides and developer-level implementation guides, targeting AWS serverless workloads.

---

## What's Inside

```
.
├── architecture-analysis-summary.md       # Deep-dive analysis: both patterns + integration gaps
├── guides/
│   ├── cellbasedarchitecture/
│   │   ├── architect-guide.md             # Cell topology, routing, trade-offs, migration
│   │   └── developer-guide.md             # Terraform modules, routing layer, observability
│   └── hexagonalarchitecture/
│       ├── architect-guide.md             # Bounded contexts, port taxonomy, team org
│       └── developer-guide.md             # Port/adapter code, DI, testing, Terraform
└── skills/
    ├── cellbasedarchitecture/SKILL.md     # Claude skill definition for cell-based pattern
    └── hexagonalarchitecture/SKILL.md     # Claude skill definition for hexagonal pattern
```

---

## Architecture Patterns

### Cell-Based Architecture

Organizes a system into isolated, self-contained deployment units called **cells**. Each cell contains everything needed to serve its assigned traffic slice — compute, storage, events, and queues — with a thin global routing layer directing requests to the correct cell.

```
┌─────────────────────────────────────────────────────────┐
│                      GLOBAL LAYER                       │
│  • Routing (Route 53, CloudFront, Global Accelerator)   │
│  • Cell Assignment Service                              │
│  • Shared Auth (Cognito)                                │
│  • Global Observability Dashboards                      │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     CELL A      │ │     CELL B      │ │     CELL C      │
│  (us-east-1)    │ │  (us-east-1)    │ │  (eu-west-1)    │
│  • Compute      │ │  • Compute      │ │  • Compute      │
│  • Storage      │ │  • Storage      │ │  • Storage      │
│  • Events       │ │  • Events       │ │  • Events       │
│  • Queues       │ │  • Queues       │ │  • Queues       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

| Concept | Description |
|---------|-------------|
| **Cell** | Self-contained deployment unit serving a fixed subset of traffic |
| **Routing Layer** | Global component directing requests to the correct cell |
| **Cell Assignment** | Service/data mapping customers to their assigned cell |
| **Blast Radius** | Scope of failure impact — bounded to the affected cell |
| **Cell Capacity** | Fixed upper bound; scale by adding cells, not by resizing |

**Key properties**: fault isolation, independent deployments, canary rollouts, horizontal scaling by cell addition.

**When it makes sense**: highly resilient distributed systems, multi-region AWS deployments, tenant isolation, reducing blast radius for bad deploys.

**Industry adoption**: AWS, Slack, DoorDash.

---

### Hexagonal Architecture (Ports and Adapters)

Introduced by Alistair Cockburn. The domain sits at the center with zero dependencies on frameworks, databases, or infrastructure. All dependencies point inward.

```
                ┌─────────────────────────────────────┐
                │          INBOUND ADAPTERS            │
                │  REST Handler │ GraphQL │ Lambda      │
                └──────────────┬──────────────────────┘
                               ▼
                ┌─────────────────────────────────────┐
                │          INBOUND PORTS               │
                │   (Use Cases / Application Services) │
                ├─────────────────────────────────────┤
                │           DOMAIN CORE                │
                │  Entities · Value Objects · Events   │
                ├─────────────────────────────────────┤
                │          OUTBOUND PORTS              │
                │   (Repository · Publisher · Client)  │
                └──────────────┬──────────────────────┘
                               ▼
                ┌─────────────────────────────────────┐
                │         OUTBOUND ADAPTERS            │
                │  DynamoDB │ EventBridge │ HTTP Client │
                └─────────────────────────────────────┘
```

| Concept | Description |
|---------|-------------|
| **Domain** | Pure business logic with no infrastructure imports |
| **Inbound Port** | Interface defining how the outside calls the domain (use cases) |
| **Outbound Port** | Interface defining what the domain needs from outside (repositories, event publishers) |
| **Inbound Adapter** | Receives external calls and invokes inbound ports (Lambda handler, REST controller) |
| **Outbound Adapter** | Implements outbound ports against real infrastructure (DynamoDB, EventBridge) |

**Dependency direction**: `DynamoDBAdapter → OrderRepository (port) ← Domain` — infrastructure depends on domain, never the reverse.

**Validation**: implementation is correct when you can answer "yes" to all five:
1. Domain tests run with no running infrastructure
2. Database can be swapped by changing only adapter code
3. Domain code imports zero infrastructure libraries
4. Use cases are explicit interfaces, not buried in controllers
5. A CLI adapter could be added without touching the domain

---

## How the Two Patterns Integrate

- **Hexagonal** defines *what runs inside* each cell — domain logic, ports, adapters
- **Cell-based** defines *how cells are deployed and coordinated* — routing, assignment, isolation

The hexagonal domain is **identical across all cells**. Only adapter configurations change per cell (region-specific endpoints, cell-specific DynamoDB table names). The domain remains pure and portable.

---

## Guide Map

| Guide | Audience | Contents |
|-------|----------|----------|
| [guides/cellbasedarchitecture/architect-guide.md](guides/cellbasedarchitecture/architect-guide.md) | Architects | Cell topology, partitioning strategies, global layer design, cross-cell coordination, cost/resilience trade-offs, greenfield and brownfield migration |
| [guides/cellbasedarchitecture/developer-guide.md](guides/cellbasedarchitecture/developer-guide.md) | Developers | Terraform cell modules, multi-region workspace strategy, Lambda@Edge routing, cell assignment via DynamoDB Global Tables, GitHub Actions canary deployment pipeline |
| [guides/hexagonalarchitecture/architect-guide.md](guides/hexagonalarchitecture/architect-guide.md) | Architects | Bounded context alignment, port taxonomy (inbound/outbound), layering strategies, team organization, context mapping patterns, strangler fig migration |
| [guides/hexagonalarchitecture/developer-guide.md](guides/hexagonalarchitecture/developer-guide.md) | Developers | TypeScript and Java/Kotlin project structure, domain entities, port interfaces, Lambda/DynamoDB/EventBridge adapters, InversifyJS DI, unit and integration testing, CDK/Terraform modules |
| [architecture-analysis-summary.md](architecture-analysis-summary.md) | Both | Full comparative analysis, integration gaps, reference architecture, agent swarm pattern |

---

## Technology Coverage

| Layer | Technologies |
|-------|-------------|
| **Languages** | TypeScript, Java, Kotlin |
| **Compute** | AWS Lambda, Lambda@Edge |
| **Storage** | DynamoDB, DynamoDB Global Tables, S3 |
| **Messaging** | EventBridge, SQS |
| **Routing** | Route 53, CloudFront, AWS Global Accelerator, API Gateway |
| **Auth** | Amazon Cognito |
| **IaC** | Terraform, AWS CDK |
| **CI/CD** | GitHub Actions (canary deployment pipeline) |
| **DI** | InversifyJS |

---

## Skills (Claude Integration)

The `skills/` directory contains Claude skill definitions that trigger contextual guidance:

- **[skills/cellbasedarchitecture/SKILL.md](skills/cellbasedarchitecture/SKILL.md)** — activates on mentions of: cell-based architecture, blast radius, fault isolation, cellular deployment, multi-tenant isolation, multi-region AWS, horizontal scaling via cells
- **[skills/hexagonalarchitecture/SKILL.md](skills/hexagonalarchitecture/SKILL.md)** — activates on mentions of: hexagonal architecture, ports and adapters, clean architecture, onion architecture, DDD boundaries, domain isolation, framework-agnostic code

Each skill routes to role-appropriate guides (architect vs. developer) and provides a core-concepts quick reference.

---

## Key Decision Points

**Before adopting cell-based architecture:**
1. What is your partitioning key? (Customer ID, geography, tenant, shard key)
2. One cell per region, or multiple cells per region?
3. Which services must stay global? (Auth, billing, onboarding)
4. Does any data need to span cells?
5. Do events need to flow between cells?

**Before adopting hexagonal architecture:**
1. Is bounded context scope well-defined?
2. Are port interfaces granular enough to be meaningful but not so fine-grained they create indirection overhead?
3. Does the team understand the strict inward-only dependency rule?
4. Is there a plan for dependency injection wiring?
5. Are integration tests scoped to adapter boundaries, not domain logic?

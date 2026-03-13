# Cell-Based and Hexagonal Architecture: Analysis Summary

> A comprehensive analysis of cell-based architecture characteristics, hexagonal architecture principles, and how they integrate when deploying business domains on AWS serverless infrastructure.

---

## Table of Contents

1. [Cell-Based Architecture Characteristics](#cell-based-architecture-characteristics)
2. [Hexagonal Architecture Characteristics](#hexagonal-architecture-characteristics)
3. [Mapping Hexagonal to Cell-Based Architecture](#mapping-hexagonal-to-cell-based-architecture)
4. [Integration Gaps and Considerations](#integration-gaps-and-considerations)
5. [Reference Architecture](#reference-architecture)

---

## Cell-Based Architecture Characteristics

Cell-based architecture is a software design pattern that organizes systems into isolated, self-contained units called "cells."

### Core Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Isolation and Independence** | Each cell operates independently with its own resources, data stores, and dependencies. Failures in one cell don't cascade to others, creating natural fault boundaries. |
| **Complete Functionality** | A cell contains everything needed to serve a subset of users or requests—compute, storage, networking, and application logic. It's essentially a miniature version of the entire system. |
| **Routing Layer** | A thin routing layer directs traffic to the appropriate cell, typically based on customer ID, geographic region, or some other partitioning key. This layer must be highly available since it's a shared component. |
| **Blast Radius Reduction** | If something goes wrong (bad deployment, infrastructure failure, data corruption), only users assigned to that cell are affected. This limits the "blast radius" of any incident. |
| **Horizontal Scaling** | You scale by adding more cells rather than making existing infrastructure larger. Each cell has a fixed capacity ceiling, and growth means provisioning new cells. |
| **Independent Deployments** | Cells can be updated independently, enabling canary deployments where changes roll out to one cell first before broader release. |

### Trade-offs to Consider

- Higher infrastructure overhead (duplicated resources across cells)
- Cross-cell operations become complex
- The routing layer is a critical shared dependency
- Data that must span cells requires careful coordination

### Industry Adoption

This pattern is popular at companies like AWS, Slack, and DoorDash for building highly resilient systems at scale.

---

## Hexagonal Architecture Characteristics

Hexagonal architecture (also called Ports and Adapters) was introduced by Alistair Cockburn.

### Core Principle

**The domain is at the center and knows nothing about the outside world.** All dependencies point inward toward the business logic, never outward.

### Key Characteristics

#### 1. Domain Isolation

The business logic has zero dependencies on frameworks, databases, UI, or infrastructure. You could delete your entire AWS stack and the domain code would still compile and run in a unit test.

#### 2. Ports (Interfaces)

Ports are abstractions defined by the domain that describe what it needs or offers:

- **Inbound ports** — how the outside world interacts with the domain (use cases, commands, queries)
- **Outbound ports** — what the domain needs from the outside world (repository interfaces, event publishers, external service contracts)

The domain defines these interfaces in its own language, not in terms of specific technologies.

#### 3. Adapters (Implementations)

Adapters are the concrete implementations that connect ports to real infrastructure:

- **Inbound adapters** — REST controllers, GraphQL resolvers, CLI handlers, message consumers, Lambda handlers
- **Outbound adapters** — DynamoDB repository implementation, S3 storage adapter, HTTP client for external APIs, EventBridge publisher

Adapters are replaceable. Swap DynamoDB for PostgreSQL by writing a new adapter—domain unchanged.

#### 4. Dependency Inversion

The domain defines the interfaces (ports). Infrastructure implements them (adapters). This inverts the traditional dependency where business logic calls database libraries directly.

```
Traditional:    Domain → Database Library
Hexagonal:      Domain ← DatabasePort ← DynamoDBAdapter
```

#### 5. Testability

Since the domain has no infrastructure dependencies, you can test it with simple in-memory fakes:

```java
// Test with fake adapter
OrderService service = new OrderService(new InMemoryOrderRepository());
service.placeOrder(...);
```

No Docker containers, no LocalStack, no mocking frameworks required for domain logic tests.

#### 6. Use Case Driven

Inbound ports typically represent use cases—discrete operations the system performs. This makes the domain's capabilities explicit and discoverable.

### Visual Structure

```
                    ┌─────────────────────────────────────┐
                    │           INBOUND ADAPTERS          │
                    │  ┌─────────┐ ┌─────────┐ ┌───────┐  │
                    │  │  REST   │ │ GraphQL │ │ Lambda│  │
                    │  │Controller│ │Resolver │ │Handler│  │
                    │  └────┬────┘ └────┬────┘ └───┬───┘  │
                    └───────┼───────────┼─────────┼───────┘
                            │           │         │
                            ▼           ▼         ▼
                    ┌─────────────────────────────────────┐
                    │         INBOUND PORTS               │
                    │   (Use Cases / Application Services)│
                    │  ┌──────────────────────────────┐   │
                    │  │  PlaceOrderUseCase           │   │
                    │  │  CancelOrderUseCase          │   │
                    │  │  GetOrderStatusQuery         │   │
                    │  └──────────────────────────────┘   │
                    ├─────────────────────────────────────┤
                    │            DOMAIN CORE              │
                    │  ┌──────────────────────────────┐   │
                    │  │  Entities (Order, Customer)  │   │
                    │  │  Value Objects (Money, SKU)  │   │
                    │  │  Domain Services             │   │
                    │  │  Domain Events               │   │
                    │  └──────────────────────────────┘   │
                    ├─────────────────────────────────────┤
                    │         OUTBOUND PORTS              │
                    │      (Interfaces/Contracts)         │
                    │  ┌──────────────────────────────┐   │
                    │  │  OrderRepository             │   │
                    │  │  PaymentGateway              │   │
                    │  │  EventPublisher              │   │
                    │  │  InventoryService            │   │
                    │  └──────────────────────────────┘   │
                    └───────┬───────────┬─────────┬───────┘
                            │           │         │
                            ▼           ▼         ▼
                    ┌─────────────────────────────────────┐
                    │          OUTBOUND ADAPTERS          │
                    │  ┌─────────┐ ┌─────────┐ ┌───────┐  │
                    │  │DynamoDB │ │ Stripe  │ │Event  │  │
                    │  │ Adapter │ │ Adapter │ │Bridge │  │
                    │  └─────────┘ └─────────┘ └───────┘  │
                    └─────────────────────────────────────┘
```

### Benefits Summary

| Benefit | How Hexagonal Delivers It |
|---------|---------------------------|
| **Testability** | Domain tests need no infrastructure |
| **Flexibility** | Swap adapters without touching domain |
| **Framework independence** | Framework is just an adapter detail |
| **Delay decisions** | Build domain first, pick database later |
| **Clear boundaries** | Ports make contracts explicit |
| **Parallel development** | Teams can work on adapters independently |

### What Hexagonal Architecture Doesn't Address

Hexagonal architecture is silent on:

- How to deploy (that's where cell architecture comes in)
- How to scale
- How to handle distributed systems concerns
- How to structure multiple bounded contexts
- Operational concerns (monitoring, resilience)

It's purely about **code organization and dependency management** within a single deployable unit.

### Validation Heuristic

If you're doing hexagonal right, you should be able to answer "yes" to:

1. Can I run my domain tests with `gradle test` and no running services?
2. Could I swap my database technology by only changing adapter code?
3. Does my domain code import zero infrastructure libraries?
4. Are my use cases explicit classes/methods, not buried in controllers?

---

## Mapping Hexagonal to Cell-Based Architecture

### Context: AWS Serverless Deployment

When a business domain implemented as hexagonal architecture (with encapsulated business functionality, well-defined inbound/outbound ports, and adapters) is deployed into AWS across multiple regions using managed serverless infrastructure like Lambda, DynamoDB, and EventBridge—all regional services—how cleanly does it map to cell-based architecture constructs?

### What Maps Cleanly

#### Adapter Layer = Cell-Specific Infrastructure Bindings

Your outbound adapters (DynamoDB adapter, EventBridge adapter) naturally encapsulate the cell-specific infrastructure. The core domain remains pure and identical across cells. This is elegant—you deploy the same business logic everywhere, and only the adapter configuration changes per cell.

#### Ports Provide Clean Cell Boundaries

Inbound ports define how traffic enters the cell. Outbound ports define dependencies. This maps well to cell isolation—each cell has its own implementations behind those ports.

#### Serverless Regional Services Fit the Model

Lambda, DynamoDB, and EventBridge being regional means each region can be a self-contained deployment unit with no shared compute or storage.

---

## Integration Gaps and Considerations

### 1. The Routing Layer Problem

Cell architecture requires a routing layer to direct requests to the correct cell. Regional services alone don't provide this—the router must be *global*:

- Route 53 (latency/geolocation routing)
- Global Accelerator
- CloudFront with origin selection logic

**Key Question:** Where does the "customer X → cell Y" decision happen? This component sits *outside* your hexagonal domain and is a shared dependency across all cells. It's often the hardest part to get right.

### 2. Region ≠ Cell (Necessarily)

Equating one region = one cell is valid, but consider:

- What if you want finer blast radius control? (Multiple cells per region)
- What if a region has too many customers? (You'd need to split)
- Cells are typically partitioned by *tenant/customer*, not geography

**A more flexible model:** Cells are logical partitions, and each cell *happens* to be deployed in a region. You might have:
- `us-east-1-cell-1`
- `us-east-1-cell-2`
- `eu-west-1-cell-1`

### 3. Cell Assignment Service

Something needs to maintain the mapping of "customer → cell." This is typically:

- A lightweight global lookup service
- Stored in a global data store (DynamoDB Global Tables, or a simple Route 53 record per customer)
- Called by the routing layer

This is *outside* your hexagonal domain but critical to cell architecture.

### 4. Cross-Cell Concerns

Hexagonal architecture doesn't address these, but cell architecture forces you to decide:

| Concern | Per-Cell or Shared? |
|---------|---------------------|
| Authentication/AuthZ | Often shared (Cognito is global-ish) |
| Customer onboarding | Shared (assigns to cell) |
| Billing/metering | Often aggregated centrally |
| Observability | Per-cell data, global dashboards |

### 5. EventBridge Regional Isolation

Events don't cross regions automatically. If your domain emits events that other systems consume, you need to decide:

- Are consumers in the same cell? (Fine, regional EventBridge works)
- Do events need to reach a central system? (Need cross-region event replication)
- What about event ordering across cells?

### 6. Data That Spans Cells

Hexagonal architecture treats "the database" as an outbound port. But cell architecture forces harder questions:

- Can a customer's data ever need to move between cells?
- Is there any data that must be globally consistent?
- How do you handle a customer querying "all my data" if it's partitioned?

---

## Reference Architecture

### Mental Model: Layered Integration

```
┌─────────────────────────────────────────────────────────┐
│                   GLOBAL LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Route 53  │  │Cell Assignment│ │ Auth (Cognito) │  │
│  │  /CloudFront│  │   Service    │  │                │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────────┘  │
└─────────┼────────────────┼──────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     CELL A      │  │     CELL B      │  │     CELL C      │
│  (us-east-1)    │  │  (us-east-1)    │  │  (eu-west-1)    │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │  Hexagonal  │ │  │ │  Hexagonal  │ │  │ │  Hexagonal  │ │
│ │   Domain    │ │  │ │   Domain    │ │  │ │   Domain    │ │
│ │ ┌─────────┐ │ │  │ │ ┌─────────┐ │ │  │ │ ┌─────────┐ │ │
│ │ │ Lambda  │ │ │  │ │ │ Lambda  │ │ │  │ │ │ Lambda  │ │ │
│ │ │ DynamoDB│ │ │  │ │ │ DynamoDB│ │ │  │ │ │ DynamoDB│ │ │
│ │ │ EvBridge│ │ │  │ │ │ EvBridge│ │ │  │ │ │ EvBridge│ │ │
│ │ └─────────┘ │ │  │ │ └─────────┘ │ │  │ │ └─────────┘ │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Key Insight

Your hexagonal domain maps cleanly to *what runs inside a cell*. What's potentially missing is the *cell orchestration layer*—the global components that make multiple cells function as a coherent system:

1. **Global router** (Route 53 / CloudFront / Global Accelerator)
2. **Cell assignment service** (customer → cell mapping)
3. **Cross-cell event strategy** (if needed)
4. **Shared services decisions** (auth, billing, onboarding)

### Complementary Relationship

The hexagonal architecture gives you excellent portability and testability of business logic. Cell architecture gives you operational resilience. They compose well—but the glue between them needs explicit design.

| Architecture | Scope | Addresses |
|--------------|-------|-----------|
| **Hexagonal** | Code organization | How to structure business logic, ports, adapters |
| **Cell-Based** | Deployment & operations | How to deploy, scale, isolate, and route |

**The hexagonal domain is identical across all cells.** Only adapter configurations change per cell (region-specific endpoints, cell-specific table names).

---

## Summary

The mapping between hexagonal architecture and cell-based architecture is largely complementary:

- **Hexagonal architecture** defines the internal structure of your business domain—pure domain logic at the center, surrounded by ports and adapters
- **Cell-based architecture** defines how that domain gets deployed and operated across isolated, fault-tolerant units

The gaps to address are primarily in the **global layer**:
- Routing and cell assignment
- Cross-cell coordination
- Shared services placement
- Event replication strategies

When designed together, these patterns create systems that are both well-structured (hexagonal) and operationally resilient (cell-based).

---

## Practical Implementation with Agent Swarms and Skills

This section describes how to implement cell-based and hexagonal architecture using a coordinated swarm of AI agents, each equipped with specialized skills. The architectural principles themselves become the blueprint for organizing the agent ecosystem.

### The Meta-Pattern: Agents as Cells, Skills as Adapters

The same architectural patterns we use for software systems apply elegantly to agent organization:

| Software Concept | Agent Swarm Equivalent |
|------------------|------------------------|
| **Cell** | Specialized agent with isolated responsibilities |
| **Hexagonal Domain** | Agent's core reasoning and decision-making logic |
| **Inbound Port** | Task/prompt interface the agent exposes |
| **Outbound Port** | Dependencies the agent needs (other agents, tools, skills) |
| **Adapter** | Skills that provide concrete capabilities |
| **Routing Layer** | Orchestrator agent that delegates to specialized agents |
| **Cell Assignment** | Task classification and agent selection logic |
| **Event Bus** | Inter-agent communication channel |

### Agent Swarm Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │   Task Router   │  │  Agent Registry │  │  Conversation Context  │  │
│  │  (Classifies &  │  │  (Available     │  │  (Shared state across  │  │
│  │   delegates)    │  │   agents/skills)│  │   agent interactions)  │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────────────┘  │
└───────────┼────────────────────┼────────────────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SPECIALIZED AGENT CELLS                          │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  ARCHITECT      │  │  DEVELOPER      │  │  INFRASTRUCTURE         │  │
│  │  AGENT          │  │  AGENT          │  │  AGENT                  │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────────────┐ │  │
│  │ │ Core Logic  │ │  │ │ Core Logic  │ │  │ │ Core Logic          │ │  │
│  │ │ - Decisions │ │  │ │ - Implement │ │  │ │ - Provision         │ │  │
│  │ │ - Trade-offs│ │  │ │ - Code      │ │  │ │ - Deploy            │ │  │
│  │ │ - Patterns  │ │  │ │ - Test      │ │  │ │ - Monitor           │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────────────┘ │  │
│  │ Skills:         │  │ Skills:         │  │ Skills:                 │  │
│  │ • cell-arch     │  │ • hexagonal     │  │ • cell-arch             │  │
│  │ • hexagonal     │  │ • typescript    │  │ • terraform             │  │
│  │ • ddd-patterns  │  │ • testing       │  │ • aws-serverless        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  DOMAIN         │  │  INTEGRATION    │  │  QUALITY                │  │
│  │  AGENT          │  │  AGENT          │  │  AGENT                  │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────────────┐ │  │
│  │ │ Core Logic  │ │  │ │ Core Logic  │ │  │ │ Core Logic          │ │  │
│  │ │ - Entities  │ │  │ │ - Events    │ │  │ │ - Review            │ │  │
│  │ │ - Rules     │ │  │ │ - APIs      │ │  │ │ - Validate          │ │  │
│  │ │ - Events    │ │  │ │ - ACLs      │ │  │ │ - Test              │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────────────┘ │  │
│  │ Skills:         │  │ Skills:         │  │ Skills:                 │  │
│  │ • hexagonal     │  │ • eventbridge   │  │ • code-review           │  │
│  │ • ddd-patterns  │  │ • api-design    │  │ • testing               │  │
│  │ • domain-specific│ │ • cell-arch     │  │ • security-audit        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Definitions and Responsibilities

#### 1. Orchestrator Agent (Global Router)

The orchestrator is analogous to the routing layer in cell-based architecture. It receives tasks and delegates to specialized agents.

**Responsibilities:**
- Classify incoming tasks by type and complexity
- Select appropriate agent(s) based on task requirements
- Maintain conversation context across agent handoffs
- Aggregate results from multiple agents
- Handle failures and escalations

**Skills Required:**
- Task classification
- Agent capability registry
- Context management

**Routing Logic Example:**
```
Task: "Design the cell topology for our payment system"
  → Route to: Architect Agent (primary)
  → Skills needed: cell-based-architecture, hexagonal-architecture

Task: "Implement the DynamoDB repository adapter"
  → Route to: Developer Agent (primary)
  → Skills needed: hexagonal-architecture, aws-serverless

Task: "Deploy a new cell to eu-west-1"
  → Route to: Infrastructure Agent (primary)
  → Skills needed: cell-based-architecture, terraform
```

#### 2. Architect Agent

Makes strategic decisions about system structure, following the architect guides.

**Inbound Ports (Tasks it handles):**
- Define cell topology and partitioning strategy
- Design bounded context boundaries
- Specify port and adapter contracts
- Make build-vs-buy decisions
- Create architecture decision records (ADRs)

**Outbound Ports (What it needs):**
- Cell-based architecture skill (for topology decisions)
- Hexagonal architecture skill (for domain structure)
- DDD patterns skill (for bounded contexts)
- Developer Agent (for feasibility checks)

**Example Interaction:**
```
Input: "We need to handle EU data residency requirements"

Architect Agent Process:
1. Load cell-based-architecture skill → references/architect-guide.md
2. Consult "Cell Topology Decisions" → Geographic partitioning
3. Load hexagonal-architecture skill → references/architect-guide.md
4. Consult "Bounded Context Alignment" → ACL for EU-specific rules
5. Output: Cell topology recommendation with EU-specific cells
```

#### 3. Developer Agent

Implements code following hexagonal patterns, using the developer guides.

**Inbound Ports:**
- Implement domain entities and value objects
- Create port interfaces
- Build adapter implementations
- Write unit and integration tests
- Refactor existing code

**Outbound Ports:**
- Hexagonal architecture skill (for patterns)
- Language-specific skills (TypeScript, Java, Python)
- Testing skill
- Quality Agent (for review)

**Hexagonal Structure of the Agent Itself:**
```
Developer Agent
├── Core Logic (Domain)
│   ├── Understands code structure
│   ├── Applies design patterns
│   └── Makes implementation decisions
│
├── Inbound Adapters
│   ├── Natural language task parser
│   ├── Code review request handler
│   └── Refactoring request handler
│
└── Outbound Adapters (Skills)
    ├── hexagonal-architecture skill
    ├── typescript skill
    ├── testing skill
    └── file-system tools
```

#### 4. Infrastructure Agent

Provisions and manages cell infrastructure using Terraform/CDK.

**Inbound Ports:**
- Provision new cells
- Deploy application updates
- Scale cell capacity
- Configure routing rules
- Set up observability

**Outbound Ports:**
- Cell-based architecture skill (for cell contracts)
- Terraform/CDK skill
- AWS serverless skill
- CI/CD skill

#### 5. Domain Agent (Per Bounded Context)

Specialized agents for specific business domains. You might have separate agents for Orders, Payments, Shipping, etc.

**Inbound Ports:**
- Model domain entities
- Define business rules
- Specify domain events
- Validate domain logic

**Outbound Ports:**
- Hexagonal architecture skill
- Domain-specific skill (e.g., payments-domain, banking-regulations)
- Developer Agent (for implementation)

#### 6. Integration Agent

Handles cross-cell and cross-context communication patterns.

**Inbound Ports:**
- Design event schemas
- Define API contracts
- Implement ACLs
- Configure event routing

**Outbound Ports:**
- Cell-based architecture skill (for cross-cell patterns)
- EventBridge skill
- API design skill

#### 7. Quality Agent

Reviews and validates outputs from other agents.

**Inbound Ports:**
- Review architecture decisions
- Validate code quality
- Check security compliance
- Verify test coverage

**Outbound Ports:**
- Code review skill
- Security audit skill
- Testing patterns skill

### Skills as Adapters

Skills function as adapters in the hexagonal sense—they provide concrete capabilities without polluting the agent's core reasoning logic.

#### Skill Structure (Hexagonal Pattern)

```
skill/
├── SKILL.md                    # Inbound port: describes when/how to use
├── references/
│   ├── architect-guide.md      # Adapter: architect-specific knowledge
│   └── developer-guide.md      # Adapter: developer-specific knowledge
└── templates/                  # Adapter: reusable code templates
    ├── cell-module.tf
    └── hexagonal-structure/
```

#### Skill Loading Strategy

Skills use progressive disclosure, matching the hexagonal layering:

| Layer | Content | When Loaded |
|-------|---------|-------------|
| **Metadata** | Skill name + description | Always in context |
| **SKILL.md** | Core concepts, decision trees | When skill triggered |
| **References** | Deep implementation details | On-demand per section |
| **Templates** | Concrete code/config | When generating output |

### Inter-Agent Communication (Event-Driven)

Agents communicate through events, mirroring EventBridge patterns:

```typescript
// Agent event schema
interface AgentEvent {
  eventType: string;           // e.g., "ArchitectureDecisionMade"
  sourceAgent: string;         // e.g., "architect-agent"
  targetAgent?: string;        // Optional: for directed messages
  correlationId: string;       // Track conversation flow
  payload: {
    decision?: string;
    artifacts?: string[];
    nextSteps?: string[];
  };
}

// Example event flow
{
  eventType: "CellTopologyDefined",
  sourceAgent: "architect-agent",
  correlationId: "conv-123",
  payload: {
    decision: "Geographic partitioning with 3 cells",
    artifacts: ["cell-topology.md", "routing-design.md"],
    nextSteps: ["Implement cell Terraform module", "Design routing layer"]
  }
}
// → Orchestrator routes to Infrastructure Agent and Developer Agent
```

### Workflow Example: Implementing a New Bounded Context

**Task:** "Add a new KYC (Know Your Customer) bounded context to our banking platform"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 1: Orchestrator receives task                                      │
│         → Classifies as: Architecture + Implementation                  │
│         → Primary: Architect Agent                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: Architect Agent                                                 │
│         → Loads: hexagonal-architecture skill                           │
│         → Consults: Bounded Context Alignment                           │
│         → Loads: cell-based-architecture skill                          │
│         → Consults: Cell Topology Decisions                             │
│         → Output: KYC context design, cell placement decision           │
│         → Emits: BoundedContextDesigned event                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Domain Agent (KYC-specific)                                     │
│         → Loads: hexagonal-architecture skill                           │
│         → Consults: Implementing the Domain Layer                       │
│         → Loads: banking-regulations skill (domain-specific)            │
│         → Output: KYC entities, value objects, domain events            │
│         → Emits: DomainModelDefined event                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: Developer Agent                                                 │
│         → Loads: hexagonal-architecture skill                           │
│         → Consults: Implementing Ports, Implementing Adapters           │
│         → Output: Port interfaces, adapter implementations, tests       │
│         → Emits: ImplementationComplete event                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 5: Infrastructure Agent                                            │
│         → Loads: cell-based-architecture skill                          │
│         → Consults: Cell Module Implementation                          │
│         → Output: Terraform module for KYC cell                         │
│         → Emits: InfrastructureProvisioned event                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 6: Integration Agent                                               │
│         → Loads: cell-based-architecture skill                          │
│         → Consults: Cross-Cell Coordination                             │
│         → Output: Event schemas, ACL for legacy screening system        │
│         → Emits: IntegrationConfigured event                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 7: Quality Agent                                                   │
│         → Reviews all artifacts                                         │
│         → Validates against cell contracts                              │
│         → Checks hexagonal dependency rules                             │
│         → Output: Approval or revision requests                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Blast Radius and Fault Isolation for Agents

Applying cell-based principles to the agent swarm itself:

| Principle | Application to Agent Swarm |
|-----------|---------------------------|
| **Isolation** | Each agent operates independently; failure in one doesn't crash others |
| **Blast Radius** | Errors in Domain Agent affect only that bounded context |
| **Independent Deployment** | Skills can be updated without redeploying all agents |
| **Capacity Limits** | Each agent has defined scope; complex tasks spawn multiple agents |
| **Health Checks** | Agents can validate their skill availability before accepting tasks |

### Skill Catalog for This Architecture

Based on the guides created, here's the recommended skill catalog:

#### Core Architecture Skills

| Skill | Primary User | Purpose |
|-------|--------------|---------|
| `cell-based-architecture` | Architect, Infrastructure | Cell topology, routing, cross-cell patterns |
| `hexagonal-architecture` | Architect, Developer, Domain | Ports, adapters, domain structure |
| `ddd-patterns` | Architect, Domain | Bounded contexts, aggregates, events |

#### Implementation Skills

| Skill | Primary User | Purpose |
|-------|--------------|---------|
| `typescript-hexagonal` | Developer | TypeScript implementation patterns |
| `terraform-cells` | Infrastructure | Terraform modules for cells |
| `aws-serverless` | Developer, Infrastructure | Lambda, DynamoDB, EventBridge |
| `testing-patterns` | Developer, Quality | Unit, integration, e2e testing |

#### Integration Skills

| Skill | Primary User | Purpose |
|-------|--------------|---------|
| `eventbridge-patterns` | Integration | Event schemas, routing rules |
| `api-design` | Integration, Developer | REST/GraphQL API contracts |
| `acl-patterns` | Integration | Anti-corruption layer implementation |

#### Domain-Specific Skills (Examples)

| Skill | Primary User | Purpose |
|-------|--------------|---------|
| `banking-domain` | Domain Agent | Banking entities, regulations |
| `payments-domain` | Domain Agent | Payment processing rules |
| `kyc-domain` | Domain Agent | KYC/AML requirements |

### Implementation Checklist

To implement this agent swarm architecture:

- [ ] **Define Agent Roster**: Identify all specialized agents needed
- [ ] **Create Core Skills**: Build cell-based and hexagonal architecture skills
- [ ] **Design Orchestrator Logic**: Task classification and routing rules
- [ ] **Establish Event Schema**: Inter-agent communication contracts
- [ ] **Build Agent Templates**: Hexagonal structure for each agent type
- [ ] **Configure Skill Loading**: Progressive disclosure strategy
- [ ] **Implement Quality Gates**: Review checkpoints in workflow
- [ ] **Set Up Observability**: Track agent interactions and outcomes
- [ ] **Define Escalation Paths**: Human-in-the-loop for edge cases
- [ ] **Test Agent Isolation**: Verify blast radius containment

### Key Insight

The agent swarm itself becomes a demonstration of the architectural principles it implements:

- **Hexagonal agents** with clean separation between core reasoning and skill-provided capabilities
- **Cell-like isolation** where each agent has bounded responsibilities and independent operation
- **Event-driven coordination** mirroring the EventBridge patterns used in the target architecture
- **Skills as adapters** that can be swapped, updated, or extended without changing agent core logic

This recursive application of the patterns validates their generality and provides a practical framework for AI-assisted architecture and development workflows.


---

## Architecture Benefits Comparison

This section provides a structured comparison of the tangible benefits each architecture delivers,
mapped to the phase where that benefit is most impactful and the persona who gains the most from it.

### Cell-Based Architecture Benefits

| Benefit | Description | Phase Most Impacted | Persona Primarily Served |
| --- | --- | --- | --- |
| **Blast Radius Reduction** | Failures are scoped to a single cell and its assigned traffic slice. A bad deployment or infrastructure failure in Cell A leaves Cells B and C fully operational, limiting customer impact to 1-5% per incident. | Operations | SRE |
| **Independent Horizontal Scaling** | Each cell scales independently by adjusting its own Lambda concurrency or DynamoDB capacity. Teams add new cells when existing cells approach capacity ceilings (70-80%), avoiding shared resource contention. | Scaling | Architect |
| **Canary and Progressive Deployments** | Changes are deployed to a single canary cell first. If error rates stay within bounds, the deployment continues cell by cell. Rollback is instantaneous — redirect traffic away from the affected cell without redeployment. | Development | Developer |
| **Failure Isolation and Fast Recovery** | Each cell has its own DLQs, alarms, and circuit patterns. MTTR for a cell-scope incident is dramatically lower than a system-wide incident. Operators drain a single cell, remediate, and re-enable without affecting other cells. | Operations | SRE |
| **Team Autonomy and Independent Ownership** | Each cell can be owned end-to-end by a single team — infrastructure, deployment pipeline, on-call rotation, and SLO ownership. Teams deploy without coordinating with other cell owners. Conway's Law works in your favor. | Development | Architect |
| **Operational Observability Per Cell** | Every cell emits its own CloudWatch dashboards, X-Ray traces, and error budgets. Operators identify which cell is degraded without filtering through system-wide noise. Cell-local data aggregates to global dashboards for cross-cell visibility. | Operations | SRE |

### Hexagonal Architecture Benefits

| Benefit | Description | Phase Most Impacted | Persona Primarily Served |
| --- | --- | --- | --- |
| **Domain Purity — Zero Framework Coupling** | The domain layer imports nothing from AWS SDKs, Express, Spring, or any infrastructure library. Business rules compile and run with only the language standard library. Infrastructure upgrades cannot break business logic. | Development | Architect |
| **Adapter Replaceability Without Domain Change** | Swapping DynamoDB for Aurora Serverless requires implementing a new `OrderRepository` adapter. The domain, use cases, and inbound adapters are untouched. The port contract (interface) is the stability guarantee that makes this safe. | Development | Developer |
| **In-Memory Testability — No Infrastructure Required** | Domain tests and use-case tests run with `InMemoryOrderRepository` and `InMemoryEventPublisher`. No Docker Compose, no LocalStack, no mocking framework for domain-layer tests. A full domain test suite executes in under 90 seconds. | Testing | Developer |
| **Use-Case-Driven API Surface** | Inbound ports are explicit interfaces — `PlaceOrderUseCase`, `CancelOrderUseCase`, `GetOrderStatusQuery`. New engineers read the port layer and immediately understand every operation the domain supports, without reading controllers or infrastructure code. | Development | Architect |
| **Parallel Team Development via Port Contracts** | Once port interfaces are agreed upon, the domain team and adapter team develop independently. The adapter team implements against the port contract; the domain team implements the logic. CI validates both against the same interface. | Development | Developer |
| **Technology Upgrade Path Safety** | When migrating infrastructure — Lambda runtime, EventBridge API changes, database engine — only adapter code changes. The domain remains frozen during migration, reducing regression surface area and enabling dual-write validation strategies before cutover. | Operations | SRE |

---

## Measurable Outcomes — OKR Framework

This section frames the expected outcomes of adopting cell-based and hexagonal architecture using
the OKR (Objectives and Key Results) model. Each Key Result includes a baseline (before) and
target (after) to anchor investment decisions.

### Cell-Based Architecture OKRs

**Objective:** Reduce the business impact of any single production incident to a bounded, recoverable scope.

| Key Result | Baseline (Before) | Target (After) | Measurement Method |
| --- | --- | --- | --- |
| Blast radius of incidents (% of users affected per incident) | 60-100% of users | 5% or fewer users per incident | CloudWatch cell-level error rate vs. global user count |
| Mean time to recovery (MTTR) from production incidents | 45-90 minutes | 15 minutes or less | Incident management platform (PagerDuty / OpsGenie MTTR metric) |
| Deployment frequency (deployments per week per team) | 1-2 per week, gated by coordination | 5-10 per week per cell, independent | CI/CD pipeline deploy counts per cell per team |
| Percentage of teams deploying without cross-team coordination | 20% | 90% or more | Deployment dependency tracking in CI/CD platform |
| Infrastructure cost per feature shipped | High — single shared fleet scales vertically | Declining — cells scale independently, no overprovisioning | AWS Cost Explorer tag-based cost per cell divided by feature count |
| New developer time-to-first-commit (days) | 5-10 days with monolith orientation | 3 days or fewer with cell-scoped onboarding + CLAUDE.md | Onboarding tracker from hire date to first merged PR |

**Objective:** Achieve engineering team autonomy where each cell team operates as an independent unit with its own deployment cadence.

| Key Result | Baseline (Before) | Target (After) | Measurement Method |
| --- | --- | --- | --- |
| Canary deployment adoption (% of deploys using canary strategy) | 0% — big-bang releases only | 100% of production deploys via canary cell first | GitHub Actions pipeline deployment type tagging |
| Cell-level rollback time (minutes from decision to traffic redirect) | 30-60 minutes, requires redeployment | 2 minutes or fewer via routing layer redirect | Routing layer operation logs |

---

### Hexagonal Architecture OKRs

**Objective:** Achieve a domain layer that is infrastructure-independent, fully testable, and durable across technology migrations.

| Key Result | Baseline (Before) | Target (After) | Measurement Method |
| --- | --- | --- | --- |
| Unit test execution time for full domain suite | 8-15 minutes with LocalStack integration tests | 90 seconds or less with in-memory adapters only | CI pipeline test step duration |
| Test coverage on core business logic | 40-55% with logic buried in controllers and lambdas | 90% or more with domain layer fully unit-testable | Jest/JUnit coverage report on domain/ and application/ packages |
| Domain code infrastructure import count | 15-40 infrastructure imports across domain files | Zero — domain imports only language stdlib | Automated import scanner in CI checking for aws-sdk, dynamodb, etc. |
| Adapter swap time when changing infrastructure (days) | 20-40 days with rewrite and domain regression risk | 3-5 days with new adapter only, domain unchanged | Engineering estimate tracking in issue management |

**Objective:** Enable new engineers to contribute to business logic within their first week without infrastructure knowledge.

| Key Result | Baseline (Before) | Target (After) | Measurement Method |
| --- | --- | --- | --- |
| New developer time-to-first-domain-commit (days) | 7-14 days requiring full stack understanding | 2 days or fewer with ports providing clear entry points | Onboarding tracker from hire date to first domain-layer PR |
| Percentage of use cases discoverable by reading port interfaces alone | 20% scattered across controllers | 100% with every use case as an explicit inbound port | Architecture review checklist score |
| Deployment frequency (deployments per week per team) | 1-2 per week slowed by infrastructure fear | 5-8 per week with domain changes being low-risk and fast-tested | CI/CD pipeline deploy counts per service per team |
| Independent deployment capability (% of teams without coordination) | 30% | 85% or more with adapter isolation removing deployment coupling | Deployment dependency tracking in CI/CD platform |

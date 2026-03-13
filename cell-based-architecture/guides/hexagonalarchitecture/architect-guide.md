# Hexagonal Architecture: Architect Guide

This guide covers strategic decisions, patterns, and trade-offs for architects designing hexagonal systems.

## Table of Contents

1. [Strategic Positioning](#strategic-positioning)
2. [Bounded Context Alignment](#bounded-context-alignment)
3. [Port Taxonomy](#port-taxonomy)
4. [Layering Strategies](#layering-strategies)
5. [Team Organization](#team-organization)
6. [Integration Patterns](#integration-patterns)
7. [Trade-Off Analysis](#trade-off-analysis)
8. [Evolution and Migration](#evolution-and-migration)

---

## Strategic Positioning

### When Hexagonal Architecture Adds Value

Hexagonal architecture adds structure and ceremony. Justify it when:

- **Domain complexity is high**: Rich business rules that change independently of infrastructure
- **Longevity matters**: System will be maintained for years; infrastructure will evolve
- **Testability is critical**: Business logic must be verifiable without infrastructure
- **Multiple interfaces exist**: Same domain served via API, events, CLI, scheduled jobs
- **Team boundaries align**: Different teams own infrastructure vs. domain

### When to Simplify

- **CRUD-heavy applications**: If business logic is just data validation, full hexagonal may be overkill
- **Prototypes and MVPs**: Speed matters more than structure
- **Glue code**: Systems that primarily transform and route data between other systems
- **Single-developer projects**: Overhead may not justify benefits

### Hybrid Approach

You don't have to go all-in. Apply hexagonal principles where domain complexity exists, and use simpler patterns elsewhere:

```
┌─────────────────────────────────────────────┐
│               Application                    │
├─────────────────┬───────────────────────────┤
│  Order Domain   │    Reporting Module       │
│  (Hexagonal)    │    (Simple/Direct)        │
│                 │                           │
│  Rich business  │  Query-only, no domain    │
│  rules, events, │  logic, direct DB access  │
│  multiple ports │  is fine                  │
└─────────────────┴───────────────────────────┘
```

---

## Bounded Context Alignment

### One Hexagon per Bounded Context

Each bounded context should have its own hexagonal structure. Don't create one giant hexagon for the entire system.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Order Context  │    │ Payment Context │    │Shipping Context │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │  Domain   │  │    │  │  Domain   │  │    │  │  Domain   │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│  Ports/Adapters │    │  Ports/Adapters │    │  Ports/Adapters │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┴──────────────────────┘
                    Integration Layer
                (Events, APIs, Shared DB?)
```

### Context Mapping

Define how bounded contexts integrate:

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Shared Kernel** | Shared code between contexts | Tightly coupled teams, same release cycle |
| **Customer-Supplier** | Upstream provides what downstream needs | Clear dependency direction |
| **Conformist** | Downstream conforms to upstream model | No leverage to request changes |
| **Anti-Corruption Layer (ACL)** | Translation layer between contexts | Protect domain from external models |
| **Published Language** | Shared schema (events, APIs) | Multiple consumers, stable contracts |

### Anti-Corruption Layer Design

When integrating with external systems or legacy code, the ACL is an outbound adapter that translates between your domain model and the external model:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Domain                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ OrderRepository (Outbound Port)                 │    │
│  │   findById(orderId: OrderId): Order             │    │
│  │   save(order: Order): void                      │    │
│  └─────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────┘
                            │ implements
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Anti-Corruption Layer                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │ LegacyOrderRepositoryAdapter                    │    │
│  │   - Translates Order ↔ LegacyOrderRecord        │    │
│  │   - Handles legacy field mappings               │    │
│  │   - Manages legacy-specific quirks              │    │
│  └─────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────┘
                            │ calls
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Legacy System / External API               │
└─────────────────────────────────────────────────────────┘
```

---

## Port Taxonomy

### Inbound Ports: Use Case Classification

Organize inbound ports by intent:

| Category | Pattern | Example |
|----------|---------|---------|
| **Commands** | Change state, return void or ID | `PlaceOrderCommand`, `CancelOrderCommand` |
| **Queries** | Read state, no side effects | `GetOrderByIdQuery`, `ListOrdersQuery` |
| **Events** | React to external events | `OnPaymentReceivedHandler` |

**CQRS consideration**: If using CQRS, commands and queries may have entirely separate hexagons (write model vs. read model).

### Outbound Ports: Dependency Classification

Organize outbound ports by what they provide:

| Category | Purpose | Examples |
|----------|---------|----------|
| **Repositories** | Aggregate persistence | `OrderRepository`, `CustomerRepository` |
| **Domain Services** | Cross-aggregate operations | `PricingService`, `InventoryChecker` |
| **Event Publishers** | Domain event distribution | `DomainEventPublisher` |
| **External Services** | Third-party integrations | `PaymentGateway`, `ShippingProvider` |
| **Infrastructure** | Technical concerns | `Clock`, `IdGenerator`, `Logger` |

### Port Granularity

**Too granular** (one method per interface):
```java
// Avoid: Creates interface explosion
interface FindOrderById { Order find(OrderId id); }
interface SaveOrder { void save(Order order); }
interface DeleteOrder { void delete(OrderId id); }
```

**Right granularity** (cohesive operations per aggregate):
```java
// Prefer: Cohesive interface per aggregate
interface OrderRepository {
    Order findById(OrderId id);
    List<Order> findByCustomer(CustomerId customerId);
    void save(Order order);
    void delete(OrderId id);
}
```

**Principle**: Group operations that change together. Repository per aggregate is usually the right level.

---

## Layering Strategies

### Standard Three Layers

```
┌─────────────────────────────────────────┐
│              Adapters                   │  ← Infrastructure code
│   (Controllers, Repositories, Clients)  │
├─────────────────────────────────────────┤
│            Application                  │  ← Use cases, orchestration
│      (Use Cases, Event Handlers)        │
├─────────────────────────────────────────┤
│              Domain                     │  ← Pure business logic
│   (Entities, Value Objects, Services)   │
└─────────────────────────────────────────┘
```

### Dependency Rules

| Layer | Can Depend On | Cannot Depend On |
|-------|---------------|------------------|
| Domain | Nothing (maybe language stdlib) | Application, Adapters |
| Application | Domain | Adapters |
| Adapters | Application, Domain | - |

### Package/Module Structure

```
src/
├── domain/                    # Pure domain logic
│   ├── model/
│   │   ├── Order.ts
│   │   ├── OrderLine.ts
│   │   └── Money.ts
│   ├── service/
│   │   └── PricingService.ts
│   ├── event/
│   │   └── OrderPlaced.ts
│   └── port/
│       └── outbound/
│           ├── OrderRepository.ts
│           └── PaymentGateway.ts
│
├── application/               # Use cases
│   ├── command/
│   │   ├── PlaceOrderCommand.ts
│   │   └── PlaceOrderHandler.ts
│   ├── query/
│   │   ├── GetOrderQuery.ts
│   │   └── GetOrderHandler.ts
│   └── port/
│       └── inbound/
│           └── OrderUseCases.ts
│
└── adapter/                   # Infrastructure
    ├── inbound/
    │   ├── rest/
    │   │   └── OrderController.ts
    │   └── lambda/
    │       └── OrderHandler.ts
    └── outbound/
        ├── persistence/
        │   └── DynamoOrderRepository.ts
        └── payment/
            └── StripePaymentGateway.ts
```

---

## Team Organization

### Aligning Teams with Hexagonal Boundaries

**Option 1: Full-Stack Domain Teams**
Each team owns a bounded context end-to-end (domain + adapters).

```
Team Order: Order domain + all Order adapters
Team Payment: Payment domain + all Payment adapters
```

- Pros: Full ownership, fast iteration
- Cons: Duplicated infrastructure expertise

**Option 2: Horizontal Platform Teams**
Domain teams own domain + application layers. Platform team owns adapters.

```
Domain Teams: Business logic, use cases
Platform Team: Adapter implementations, infrastructure
```

- Pros: Infrastructure expertise concentrated
- Cons: Coordination overhead, potential bottleneck

**Option 3: Inner Source Model**
Platform team provides adapter templates/libraries. Domain teams implement and own adapters using templates.

```
Platform Team: Adapter libraries, best practices, code review
Domain Teams: Instantiate adapters, own end-to-end
```

- Pros: Balance of ownership and expertise sharing
- Cons: Requires good documentation and support

### Code Ownership Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    Order Service                        │
├─────────────────────────────────────────────────────────┤
│ Domain Layer          │ Application Layer               │
│ ─────────────────────────────────────────────────────── │
│ Owner: Order Team     │ Owner: Order Team               │
├─────────────────────────────────────────────────────────┤
│ Adapter Layer                                           │
│ ───────────────────────────────────────────────────────│
│ REST Adapter: Order Team                                │
│ DynamoDB Adapter: Order Team (templates from Platform)  │
│ EventBridge Adapter: Order Team (templates from Platform)│
└─────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Event-Driven Integration

Domains communicate via events, not direct calls:

```
┌───────────────────┐         ┌───────────────────┐
│   Order Domain    │         │  Payment Domain   │
│                   │         │                   │
│ OrderPlaced ──────┼────────►│ OnOrderPlaced     │
│ (Event Publisher) │  Event  │ (Event Handler)   │
└───────────────────┘   Bus   └───────────────────┘
```

**Event schema ownership**: The publishing domain owns the event schema. Consumers adapt to it (conformist) or use an ACL.

### Synchronous Integration

When synchronous calls are needed (e.g., payment must succeed before order confirmation):

```
Order Domain                          Payment Domain
    │                                       │
    │  PaymentGateway (Outbound Port)       │
    │  ──────────────────────────────────►  │
    │           PaymentAdapter              │
    │  (ACL to Payment Domain or           │
    │   external payment provider)          │
    │                                       │
```

The Order domain defines `PaymentGateway` in its own terms. The adapter translates to whatever Payment actually needs.

### Shared Database Anti-Pattern

**Avoid** sharing a database between bounded contexts:

```
# Anti-pattern
Order Domain ──┐
               ├──► Shared Database
Payment Domain ┘
```

This creates tight coupling and makes it impossible to evolve domains independently.

**Instead**, each domain owns its data, and they integrate via events or APIs.

---

## Trade-Off Analysis

### Benefits

| Benefit | How Hexagonal Delivers It |
|---------|---------------------------|
| Testability | Domain tests need no infrastructure |
| Flexibility | Swap infrastructure via adapters |
| Clarity | Explicit ports show system capabilities |
| Maintainability | Changes isolated to appropriate layer |
| Onboarding | Clear structure aids understanding |

### Costs

| Cost | Mitigation |
|------|------------|
| More code (interfaces, adapters) | Generate boilerplate, use conventions |
| Indirection | Good naming, clear documentation |
| Learning curve | Training, pair programming |
| Over-engineering risk | Apply selectively to complex domains |

### When Indirection Hurts

Hexagonal adds indirection. For simple operations, this can feel like unnecessary ceremony:

```typescript
// Simple CRUD: Hexagonal feels heavy
class CreateUserHandler {
  constructor(private repo: UserRepository) {}
  
  execute(command: CreateUserCommand): UserId {
    const user = User.create(command.name, command.email);
    this.repo.save(user);
    return user.id;
  }
}

// vs. direct approach
async function createUser(name: string, email: string) {
  return await db.users.insert({ name, email });
}
```

**Guideline**: Apply hexagonal where domain logic exists. For pure data shuffling, simpler patterns are fine.

---

## Evolution and Migration

### Introducing Hexagonal to Existing Code

**Strangler Fig Pattern**:

1. Identify a bounded context to extract
2. Define ports based on existing functionality
3. Implement adapters that delegate to legacy code
4. Gradually move logic into the domain
5. Replace legacy adapters with new implementations

```
Phase 1: Wrap legacy
┌──────────────────┐
│ New Hexagonal    │
│ ┌──────────────┐ │
│ │   Domain     │ │
│ └──────┬───────┘ │
│        │         │
│ Legacy Adapter───┼──► Legacy Code
└──────────────────┘

Phase 2: Migrate logic
┌──────────────────┐
│ New Hexagonal    │
│ ┌──────────────┐ │
│ │ Domain       │ │ ← Logic migrated here
│ │ (enriched)   │ │
│ └──────┬───────┘ │
│        │         │
│ New Adapter──────┼──► New Infrastructure
└──────────────────┘
```

### Technology Migration

When migrating infrastructure (e.g., DynamoDB to Aurora):

1. Domain and ports remain **unchanged**
2. Implement new adapter (AuroraOrderRepository)
3. Run both adapters in parallel (dual writes)
4. Validate data consistency
5. Switch reads to new adapter
6. Decommission old adapter

The domain team doesn't need to change anything—only adapter code changes.

### Evolving Port Contracts

When ports need to change:

1. **Additive changes**: Add new methods, keep old ones (backward compatible)
2. **Breaking changes**: Version the port or use adapter pattern internally

```typescript
// Version 1
interface OrderRepository {
  findById(id: OrderId): Order | null;
}

// Version 2: Add new capability without breaking existing adapters
interface OrderRepositoryV2 extends OrderRepository {
  findByCustomer(customerId: CustomerId): Order[];
}

// Adapters can implement V2 gradually
```

---

## Checklist: Architecting a Hexagonal System

Before implementation begins:

- [ ] Bounded context boundaries identified and documented
- [ ] Context map showing integration patterns between contexts
- [ ] Inbound ports (use cases) listed and categorized
- [ ] Outbound ports (dependencies) listed and categorized
- [ ] Layering strategy chosen and communicated
- [ ] Package/module structure defined
- [ ] Team ownership model decided
- [ ] ACL strategy for legacy/external integrations
- [ ] Event schemas owned by publishing domains
- [ ] Testing strategy: unit (domain), integration (adapters), e2e
- [ ] Migration path for existing code (if applicable)

---
name: hexagonal-architecture
description: |
  Guide for designing and implementing hexagonal architecture (Ports and Adapters) patterns. Use this skill whenever the user mentions: hexagonal architecture, ports and adapters, clean architecture, onion architecture, domain-driven design boundaries, inbound/outbound ports, adapters, dependency inversion in domain design, separating business logic from infrastructure, framework-agnostic domain code, or testable domain layers. Also trigger when discussing how to structure Lambda handlers, API controllers, or database repositories to keep business logic pure and infrastructure-independent. This skill provides both architect-level strategic guidance and developer-level implementation patterns.
---

# Hexagonal Architecture Skill

Hexagonal architecture (Ports and Adapters) organizes code so the domain logic sits at the center with zero dependencies on frameworks, databases, or external systems. All dependencies point inward toward the business logic.

## When to Use This Skill

- Designing domain-centric applications
- Separating business logic from infrastructure concerns
- Building testable, framework-agnostic code
- Structuring Lambda functions, API handlers, or event consumers
- Implementing repository patterns
- Preparing code for technology migrations

## Audience-Specific Guides

This skill contains two reference guides tailored to different roles:

### For Architects
Read `references/architect-guide.md` when making strategic decisions about:
- Bounded context boundaries
- Port and adapter taxonomy
- Layering strategies
- Team organization around hexagonal boundaries
- Integration with DDD patterns

### For Developers
Read `references/developer-guide.md` when implementing:
- Port interfaces in TypeScript/Java/Python
- Adapter implementations (Lambda, DynamoDB, EventBridge)
- Dependency injection patterns
- Unit testing with in-memory adapters
- Project structure conventions
- Terraform modules for hexagonal infrastructure

## Core Concepts Quick Reference

| Concept | Definition |
|---------|------------|
| **Domain** | Pure business logic with no infrastructure dependencies |
| **Inbound Port** | Interface defining how the outside world interacts with the domain (use cases) |
| **Outbound Port** | Interface defining what the domain needs from the outside world (repositories, clients) |
| **Inbound Adapter** | Implementation that receives external requests and calls inbound ports (REST controller, Lambda handler) |
| **Outbound Adapter** | Implementation of outbound ports that talks to real infrastructure (DynamoDB adapter, HTTP client) |

## Visual Structure

```
                    ┌─────────────────────────────────────┐
                    │           INBOUND ADAPTERS          │
                    │  ┌─────────┐ ┌─────────┐ ┌───────┐  │
                    │  │  REST   │ │ GraphQL │ │ Lambda│  │
                    │  │ Handler │ │Resolver │ │Handler│  │
                    │  └────┬────┘ └────┬────┘ └───┬───┘  │
                    └───────┼───────────┼─────────┼───────┘
                            │           │         │
                            ▼           ▼         ▼
                    ┌─────────────────────────────────────┐
                    │         INBOUND PORTS               │
                    │   (Use Cases / Application Services)│
                    │  ┌──────────────────────────────┐   │
                    │  │  PlaceOrderUseCase           │   │
                    │  │  GetOrderQuery               │   │
                    │  │  CancelOrderCommand          │   │
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

## Key Principles

### 1. Dependencies Point Inward
Infrastructure depends on domain, never the reverse. The domain defines interfaces (ports); infrastructure implements them (adapters).

### 2. Domain Speaks Its Own Language
Ports use domain terminology, not infrastructure terminology. The domain doesn't know about "DynamoDB items" or "HTTP requests"—only "Orders" and "Customers."

### 3. Adapters Are Replaceable
Swap DynamoDB for PostgreSQL by writing a new adapter. The domain remains unchanged.

### 4. Use Cases Are Explicit
Each inbound port represents a specific use case. The domain's capabilities are discoverable by looking at its ports.

## Validation Heuristic

If you're implementing hexagonal architecture correctly, you should answer "yes" to:

1. Can I run domain tests with no running infrastructure?
2. Could I swap my database by only changing adapter code?
3. Does my domain code import zero infrastructure libraries?
4. Are use cases explicit interfaces, not buried in controllers?
5. Could I add a CLI adapter without touching the domain?

## Integration with Cell-Based Architecture

Hexagonal architecture defines *what runs inside* a cell. Cell-based architecture defines *how cells are deployed and coordinated*.

- The hexagonal domain is **identical across all cells**
- Only **adapter configurations** change per cell (region-specific endpoints, cell-specific table names)
- The domain remains pure and portable

See the `cell-based-architecture` skill for deployment patterns that complement hexagonal design.

## Next Steps

1. Read the appropriate guide based on your role
2. Identify your bounded context boundaries
3. Define your inbound ports (use cases)
4. Define your outbound ports (dependencies)
5. Implement adapters for your chosen infrastructure

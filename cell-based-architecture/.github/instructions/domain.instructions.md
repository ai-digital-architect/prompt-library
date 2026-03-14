---
applyTo: "**/*Domain.{ts,java,py}"
---

# Domain Model Purity Rules

These rules apply to all domain model files matching `**/*Domain.{ts,java,py}`. Violations block merge and must be resolved before any review proceeds.

## Rules

1. **No infrastructure imports** — The domain layer must not import any module from `aws-sdk`, `@aws-sdk/*`, `express`, `fastify`, `spring`, `django`, `flask`, `axios`, `pg`, `mysql`, `redis`, `mongoose`, `typeorm`, `hibernate`, or any HTTP or database library. Infrastructure concerns belong exclusively in adapters.

2. **Factory methods required for entity creation** — All domain entities must be created via factory methods (e.g., `Order.create(...)`) that enforce business invariants at creation time. Direct `new Entity()` calls from outside the domain package are prohibited.

3. **Value objects must be immutable** — All value object fields must be `readonly` (TypeScript) or `final` (Java/Kotlin). Any operation that changes state must return a new value object instance — mutation is prohibited.

4. **Domain events collected, not published** — Domain events must be raised inside aggregate methods and collected via a `pullDomainEvents()` pattern. Events must not be published directly from within domain logic — the adapter layer is responsible for publishing collected events.

5. **Domain services operate on domain types only** — Domain service classes must accept and return only domain types (entities, value objects, domain events). Accepting or returning infrastructure types (SDK response objects, ORM entities, HTTP request/response) is prohibited.

6. **Typed domain exceptions for all business rule violations** — All business rule violations must throw typed domain exceptions (e.g., `OrderNotFoundException`, `InsufficientInventoryException`). Generic `Error`, `RuntimeException`, or `Exception` types are not permitted for domain-level failures.

7. **Domain tests require zero infrastructure** — Domain tests must execute with no running infrastructure. If a test requires a database connection, message queue, or HTTP server to pass, it belongs in the adapter test suite — not the domain test suite.

8. **No persistence annotations on domain models** — JPA `@Entity`, `@Column`, `@Table`, Mongoose schema decorators, SQLAlchemy model inheritance, and similar ORM annotations are prohibited in domain model files. Persistence mapping belongs in the adapter layer.

## Examples

### Rule 1: No infrastructure imports

✅ Compliant:
```typescript
// OrderDomain.ts
import { Money } from './Money';
import { OrderId } from './OrderId';
import { OrderPlacedEvent } from '../event/OrderPlacedEvent';

export class Order {
  private constructor(
    private readonly id: OrderId,
    private readonly total: Money,
  ) {}

  static create(id: OrderId, total: Money): Order {
    if (total.isNegative()) throw new InvalidOrderTotalException(total);
    return new Order(id, total);
  }
}
```

❌ Non-compliant:
```typescript
// OrderDomain.ts — VIOLATION: infrastructure import in domain
import { DynamoDB } from '@aws-sdk/client-dynamodb';  // ❌ infrastructure import
import { Express } from 'express';                      // ❌ framework import

export class Order {
  constructor(private db: DynamoDB) {}                 // ❌ infrastructure dependency
}
```

### Rule 4: Domain events collected, not published

✅ Compliant:
```typescript
export class Order {
  private domainEvents: DomainEvent[] = [];

  placeOrder(): void {
    // business logic...
    this.domainEvents.push(new OrderPlacedEvent(this.id));
  }

  pullDomainEvents(): DomainEvent[] {
    const events = [...this.domainEvents];
    this.domainEvents = [];
    return events;
  }
}
```

❌ Non-compliant:
```typescript
export class Order {
  constructor(private eventBus: EventBridgeClient) {}  // ❌ infrastructure in domain

  async placeOrder(): Promise<void> {
    // business logic...
    await this.eventBus.putEvents({ ... });             // ❌ direct event publication
  }
}
```

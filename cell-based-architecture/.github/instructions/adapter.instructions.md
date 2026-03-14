---
applyTo: "**/*Adapter.{ts,java,py}"
---

# Adapter Implementation Standards

These rules apply to all adapter files matching `**/*Adapter.{ts,java,py}`. Adapters are the translation boundary between the hexagonal domain and external infrastructure. Violations in adapters frequently leak infrastructure concerns into the domain — treat these rules as non-negotiable.

## Rules

1. **One port per adapter** — Each adapter class must implement exactly one port interface. Implementing multiple ports in one class is prohibited — create separate adapter classes for each port interface.

2. **No business logic in adapters** — Adapters must not contain business logic. Conditional logic in an adapter must be based solely on infrastructure concerns (retry decisions, type mapping choices, error code translation) — never on business rules. Business rules belong in the domain layer.

3. **Infrastructure exceptions translated at the adapter boundary** — All infrastructure SDK exceptions (AWS SDK errors, database errors, HTTP client errors) must be caught within the adapter and translated into typed domain exceptions before propagating to the domain or application layer. No SDK exception type should cross the adapter boundary.

4. **Constructor injection for infrastructure clients** — Adapter constructors must accept their infrastructure client as a constructor parameter to enable test injection. Static client instantiation inside adapter methods or constructors is prohibited.

5. **Mappers in separate classes** — Domain ↔ infrastructure type translation (mapping a DynamoDB `Item` to a domain `Order`, or a domain `Order` to a DynamoDB `PutItemInput`) must be in a separate mapper class and must not be inlined in the adapter methods.

6. **Retry with exponential backoff for outbound adapters** — Outbound adapters must include retry logic with exponential backoff for transient infrastructure failures. Maximum retry count must be configurable and must not exceed 3 retries by default.

7. **Adapter method names match port interface method names exactly** — Adapter method names must match the port interface method names exactly. No aliasing, renaming, or wrapper methods at the adapter level.

8. **No outbound adapter may call another outbound adapter** — Adapters must not depend on or call other adapters. If composition is needed, it belongs in the application service layer, not in adapters.

## Examples

### Rule 1: One port per adapter

✅ Compliant:
```typescript
// DynamoOrderAdapter.ts — implements exactly one port
export class DynamoOrderAdapter implements OrderRepository {
  constructor(private readonly client: DynamoDBDocumentClient) {}

  async save(order: Order): Promise<void> { /* ... */ }
  async findById(id: OrderId): Promise<Order | null> { /* ... */ }
}
```

❌ Non-compliant:
```typescript
// DynamoOrderAdapter.ts — VIOLATION: implements two ports
export class DynamoOrderAdapter
  implements OrderRepository, InventoryRepository {  // ❌ two ports in one adapter
  async save(order: Order): Promise<void> { /* ... */ }
  async findByProductId(id: ProductId): Promise<Inventory> { /* ... */ }
}
```

### Rule 3: Infrastructure exceptions translated at adapter boundary

✅ Compliant:
```typescript
async findById(id: OrderId): Promise<Order | null> {
  try {
    const result = await this.client.get({ TableName: this.tableName, Key: { pk: id.value } });
    return result.Item ? this.mapper.toDomain(result.Item) : null;
  } catch (err) {
    if (err instanceof ResourceNotFoundException) {
      return null;  // translated to domain-meaningful null
    }
    throw new OrderRepositoryException(`Failed to retrieve order ${id.value}`, { cause: err });
  }
}
```

❌ Non-compliant:
```typescript
async findById(id: OrderId): Promise<Order | null> {
  const result = await this.client.get({ TableName: this.tableName, Key: { pk: id.value } });
  return result.Item ? this.mapper.toDomain(result.Item) : null;
  // ❌ SDK exception propagates unhandled — AWS SDK error type crosses adapter boundary
}
```

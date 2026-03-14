---
applyTo: "**/ports/**/*.{ts,java,py}"
---

# Port Interface Standards

These rules apply to all port interface files matching `**/ports/**/*.{ts,java,py}`. Ports are the contracts between the domain and the outside world. They define what the domain offers (inbound ports) and what the domain requires (outbound ports). Port contracts must be stable, domain-centric, and free of infrastructure types.

## Rules

1. **Domain terminology exclusively** — Port interface method names, parameter types, and return types must reference domain entities and value objects — never infrastructure types. A repository port must accept an `Order` entity, not a `DynamoDB.PutItemInput`. A service client port must return an `ExternalServiceResult`, not an `AxiosResponse`.

2. **Command/Query Separation (CQS)** — Inbound port methods must follow command/query separation: command methods return `void` or a newly created aggregate ID; query methods are read-only and must not produce side effects.

3. **Typed error declarations required** — Outbound ports must declare error types for all failure modes using typed exceptions or discriminated union result types. Methods that can fail must not return `null` silently. Failure modes must be explicit in the port contract.

4. **No concrete implementations in port files** — Port interface files must not contain any concrete implementation code. Default implementations, helper methods, and utility logic belong in adapter classes.

5. **Repository ports scoped to single aggregate root** — Each repository port interface must be scoped to exactly one aggregate root. A single repository port that manages multiple aggregate types creates tight coupling between bounded contexts.

6. **Breaking changes require an ADR** — Port interface method signatures must be treated as public API. Any breaking change (removing a method, changing parameter types, changing return types) requires an ADR documenting the migration path for all existing adapter implementations. Backwards-compatible additions (new optional methods) do not require an ADR.

7. **Port interface comment required** — Each port file must include a comment or docstring on the interface itself explaining: (a) what domain concept this port represents, (b) whether it is inbound or outbound, and (c) which use cases depend on it.

8. **No infrastructure-specific error types in port signatures** — Port interfaces must not declare infrastructure-specific error types (`AWSError`, `SQLException`, `HttpException`) in their method signatures. Domain-specific exception types must be created to represent failure modes at the port boundary.

## Examples

### Rule 1: Domain terminology exclusively

✅ Compliant:
```typescript
/**
 * Outbound port: OrderRepository
 * Represents the domain's requirement to persist and retrieve Order aggregates.
 * Depended on by: PlaceOrderHandler, CancelOrderHandler, GetOrderStatusHandler
 */
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomerId(customerId: CustomerId): Promise<Order[]>;
}
```

❌ Non-compliant:
```typescript
export interface OrderRepository {
  // ❌ Infrastructure type in port signature
  save(item: DynamoDB.DocumentClient.PutItemInput): Promise<DynamoDB.DocumentClient.PutItemOutput>;
  // ❌ Infrastructure response type in return
  findById(id: string): Promise<AWS.DynamoDB.DocumentClient.GetItemOutput>;
}
```

### Rule 3: Typed error declarations

✅ Compliant:
```typescript
export interface PaymentGatewayClient {
  /**
   * @throws {PaymentDeclinedException} when the payment method is declined
   * @throws {PaymentGatewayUnavailableException} when the gateway is unreachable
   */
  charge(amount: Money, paymentMethod: PaymentMethod): Promise<ChargeResult>;
}
```

❌ Non-compliant:
```typescript
export interface PaymentGatewayClient {
  // ❌ Null return on failure hides failure modes; no typed errors declared
  charge(amount: Money, paymentMethod: PaymentMethod): Promise<ChargeResult | null>;
}
```

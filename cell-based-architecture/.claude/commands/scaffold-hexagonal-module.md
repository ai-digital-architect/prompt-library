---
description: >
  Scaffold a complete hexagonal module with ports, adapters, and test harness. Trigger phrases:
  hexagonal scaffold, ports and adapters skeleton, domain module, clean architecture template,
  create domain service, new bounded context, set up hexagonal structure, scaffold module.
---

## Purpose

Generate a complete hexagonal module structure: inbound and outbound port interfaces, domain skeleton, adapter stubs, and test harness with in-memory adapters.

## Inputs

Before execution, collect the following:

1. **Bounded context name** — the domain concept this module represents (e.g., `Order`, `Payment`, `Inventory`)
2. **Use cases** — list of operations this context must support (e.g., `PlaceOrder`, `CancelOrder`, `GetOrderStatus`)
3. **Outbound dependencies** — what external systems this context depends on (e.g., DynamoDB for orders, EventBridge for order events, PaymentService for charging)
4. **Target language** — TypeScript, Java, or Python
5. **Target directory** — where to place the module (e.g., `src/order/`, `src/bounded-contexts/order/`)

## Procedure

1. **Confirm bounded context name and use cases**
   - Verify the use case list is complete: one use case per distinct business operation
   - Confirm the bounded context name follows the project naming convention

2. **Generate inbound port interfaces**
   - For each use case, create `application/port/inbound/<UseCaseName>UseCase.ts`
   - Each interface has exactly one method following Command/Query separation:
     - Commands: `execute(command: <UseCaseName>Command): Promise<void | AggregateId>`
     - Queries: `query(query: <QueryName>Query): Promise<ReadModel>`

3. **Generate outbound port interfaces**
   - Identify the external dependencies from the Inputs
   - For each dependency, create the appropriate interface in `application/port/outbound/`:
     - Repositories: `<Entity>Repository.ts` with `save()`, `findById()`, `findBy<Criterion>()`
     - Event publishers: `<Domain>EventPublisher.ts` with `publish(event: DomainEvent): Promise<void>`
     - External service clients: `<ServiceName>Client.ts` with typed request/response

4. **Scaffold domain model**
   - Create `domain/model/<Entity>.ts` — aggregate root with factory method `<Entity>.create(...)`
   - Create value objects for each typed primitive (e.g., `OrderId`, `Money`, `Email`)
   - Create `domain/event/<EntityEvent>.ts` for each domain event the aggregate raises

5. **Create adapter stubs**
   - Inbound: `adapter/inbound/<UseCase>Handler.ts` (Lambda handler or HTTP controller stub)
   - Outbound: `adapter/outbound/Dynamo<Entity>Adapter.ts` and `adapter/outbound/EventBridge<Domain>Adapter.ts`
   - Each adapter stub: correct class definition, implements the port, constructor injection, empty method bodies with TODO comments

6. **Generate in-memory test adapters**
   - For each outbound port, create `tests/adapters/InMemory<Port>.ts`
   - Each InMemory adapter uses a `Map` for storage and fulfills the port interface with no external dependencies

7. **Create test file for each use case handler**
   - `tests/<use-case-name>.test.ts` using the InMemory adapters
   - Include: happy path test, business rule violation test, and not-found/edge case test

8. **Wire dependency injection stub**
   - Create `src/<context>/container.ts` showing how ports and adapters are wired together

## Output

- **Inbound ports**: `application/port/inbound/` — one file per use case
- **Outbound ports**: `application/port/outbound/` — one file per dependency
- **Domain model**: `domain/model/` — aggregate root and value objects
- **Domain events**: `domain/event/` — one file per domain event
- **Adapter stubs**: `adapter/inbound/` and `adapter/outbound/` — one file per adapter
- **In-memory adapters**: `tests/adapters/` — one file per outbound port
- **Test files**: `tests/` — one test file per use case handler
- **DI container**: `src/<context>/container.ts` — wiring example

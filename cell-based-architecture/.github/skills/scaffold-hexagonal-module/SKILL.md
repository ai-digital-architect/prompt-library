---
name: scaffold-hexagonal-module
description: >
  Use this skill when the user mentions: hexagonal scaffold, ports and adapters
  skeleton, domain module, clean architecture template, create domain service, new
  bounded context, set up hexagonal structure. Generates a complete hexagonal module
  with port interfaces, domain skeleton, adapter stubs, and test harness.
version: 1.0.0
---

## What This Skill Does

This skill generates a complete hexagonal module: inbound and outbound port interfaces, domain model skeleton with factory methods, adapter stubs with correct constructor injection, and an in-memory test harness — all following the project's naming conventions and directory structure.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "hexagonal scaffold", "scaffold hexagonal module", "ports and adapters skeleton"
- "domain module", "clean architecture template"
- "create domain service", "new bounded context"
- "set up hexagonal structure", "hexagonal boilerplate"

## Prerequisites

Before this skill executes, the following must be true:
- The bounded context name is known (e.g., `Order`, `Payment`, `Inventory`)
- At least one use case has been identified
- The target language is specified (TypeScript, Java, or Python)
- The target directory is confirmed (e.g., `src/<bounded-context>/`)

## Step-by-Step Procedure

1. **Confirm bounded context name and use case list**
   - Verify the use case list is complete: one interface per distinct business operation
   - Confirm naming follows the project convention

2. **Generate inbound port interfaces**
   - For each use case: create `application/port/inbound/<UseCaseName>UseCase.ts`
   - Command ports: `execute(command: <UseCaseName>Command): Promise<void | AggregateId>`
   - Query ports: `query(query: <QueryName>Query): Promise<ReadModel>`

3. **Generate outbound port interfaces**
   - Repository: `application/port/outbound/<Entity>Repository.ts` — `save()`, `findById()`, `findBy<Criterion>()`
   - Event publisher: `application/port/outbound/<Domain>EventPublisher.ts` — `publish(event): Promise<void>`
   - External service: `application/port/outbound/<ServiceName>Client.ts` — typed request/response

4. **Scaffold domain model**
   - Aggregate root: `domain/model/<Entity>.ts` — factory method `<Entity>.create(...)`, `pullDomainEvents()`
   - Value objects: `domain/model/<ValueObject>.ts` — all fields `readonly`; mutation returns new instance
   - Domain events: `domain/event/<EntityAction>Event.ts`

5. **Create adapter stubs**
   - Inbound: `adapter/inbound/<UseCase>Handler.ts` — empty handler with correct import structure
   - Outbound: `adapter/outbound/Dynamo<Entity>Adapter.ts`, `adapter/outbound/EventBridge<Domain>Adapter.ts`
   - Each stub: `implements <Port>`, constructor injection of infrastructure client, TODO-commented method bodies

6. **Generate in-memory test adapters**
   - For each outbound port: `tests/adapters/InMemory<Port>.ts` using a `Map` for storage
   - Each InMemory adapter: fulfills the port interface with no external dependencies or async I/O

7. **Create test files**
   - `tests/<use-case-name>.test.ts` for each use case handler
   - Each test file: wires InMemory adapters, tests happy path, business rule violation, and edge case

8. **Wire dependency injection example**
   - `src/<context>/container.ts` — shows how ports and adapters are wired (not a framework; documentation by example)

## Output Artifacts

- `application/port/inbound/` — one file per use case interface
- `application/port/outbound/` — one file per outbound dependency interface
- `domain/model/` — aggregate root and value objects
- `domain/event/` — one file per domain event
- `adapter/inbound/` and `adapter/outbound/` — one stub file per adapter
- `tests/adapters/` — one InMemory adapter per outbound port
- `tests/` — one test file per use case handler
- `src/<context>/container.ts` — dependency injection wiring example

## References

- [Implementation Guide: Hexagonal Architecture](../../guides/agent-swarm-implementation-guide.md)
- [Port Adapter Review Skill](../port-adapter-review/SKILL.md)
- [Generate ADR Skill](../generate-adr/SKILL.md)

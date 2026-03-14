# Cell-Based and Hexagonal Architecture — Agent Swarm Operations

## Overview

This repository uses a six-agent swarm organized around the cell-based and hexagonal architecture patterns. The swarm enforces strict separation of concerns: architectural decisions, implementation, reliability, security, migration, and onboarding are each owned by a dedicated specialist agent. No agent operates outside its designated scope.

```
                    [OnboardingAgent]
                          |
              +-----------+-----------+
              |                       |
    [ArchitectAgent] ←→ [MigrationAgent]
              |
    +---------+---------+
    |                   |
[DeveloperAgent]   [SREAgent]
    |
[SecurityAgent]
```

Every structural decision flows through `ArchitectAgent`. Implementation flows through `DeveloperAgent`. Operational contracts flow through `SREAgent`. Security reviews flow through `SecurityAgent`. Brownfield decomposition flows through `MigrationAgent`. All new contributors start with `OnboardingAgent`.

## Agent Registry

| Task Type | Responsible Agent | Trigger |
|-----------|------------------|---------|
| Cell boundary design | `@ArchitectAgent` | "cell boundaries", "partition strategy", "blast radius planning" |
| Architecture Decision Records | `@ArchitectAgent` | "ADR", "architecture decision", "MADR" |
| Hexagonal port definition | `@ArchitectAgent` | "define ports", "port contract", "bounded context" |
| Hexagonal module scaffolding | `@DeveloperAgent` | "scaffold hexagonal module", "ports and adapters skeleton" |
| Domain model implementation | `@DeveloperAgent` | "implement use case", "create domain service", "domain model" |
| Adapter implementation | `@DeveloperAgent` | "implement adapter", "implement repository" |
| In-memory test adapters | `@DeveloperAgent` | "in-memory adapter", "test harness", "write domain test" |
| Cell health contracts | `@SREAgent` | "cell health", "health contract", "cell-contract.yaml" |
| Blast radius validation | `@SREAgent` | "blast radius check", "validate cell isolation" |
| Operational runbooks | `@SREAgent` | "SRE runbook", "cell runbook", "cell drain" |
| Observability configuration | `@SREAgent` | "CloudWatch alarms", "cell observability", "cell dashboard" |
| Adapter security review | `@SecurityAgent` | "security review", "OWASP", "injection analysis" |
| Credential and secrets scan | `@SecurityAgent` | "hardcoded credentials", "secrets scan" |
| Cross-cell trust review | `@SecurityAgent` | "trust boundary", "cross-cell security" |
| Brownfield decomposition | `@MigrationAgent` | "extract cell", "strangler fig", "decompose monolith" |
| Coupling graph analysis | `@MigrationAgent` | "migration plan", "seam identification", "bounded context extraction" |
| New developer orientation | `@OnboardingAgent` | "how do I", "where does X go", "new to this project", "explain cell" |

## Operational Rules

1. **Read before write** — Every agent must read all relevant existing files before making any modifications. Writing without reading context is prohibited. Use `read_file` and `list_files` to establish context before any `create_file` or `insert_edit_into_file` call.

2. **Scope adherence** — Each agent must operate only within its designated tool allowlist and file path scope. `@ArchitectAgent` does not modify source code. `@SecurityAgent` does not modify any file. `@OnboardingAgent` does not create or modify any file. Violating scope is prohibited.

3. **Handoff protocol** — When a task exceeds the current agent's scope, the agent must use the handoff button to pass control to the correct specialist agent. The handoff must include: what was completed, what the receiving agent needs to do, and the relevant file paths as context.

4. **ADR mandatory for structural changes** — Any change to a port interface, cell boundary definition, or adapter contract must be accompanied by an ADR generated via the `generate-adr` skill. No structural change is complete without an ADR. This applies to: adding or removing port methods, changing port method signatures, changing cell boundary definitions, and changing the partitioning key.

5. **No direct cross-cell calls** — No agent may scaffold, write, or review code that calls another cell's Lambda function, DynamoDB table, or internal API directly. All cross-cell communication must route through the global routing layer or via domain events on the shared EventBridge bus.

6. **Test coverage requirement** — `@DeveloperAgent` must include in-memory adapter tests for every use case handler it implements. A use case handler is not complete until its corresponding test file exists and all tests pass using only in-memory adapters (no infrastructure required).

7. **Security review before adapter merge** — Any outbound adapter touching external APIs, user-supplied input processing, or persistent storage writes must be reviewed by `@SecurityAgent` before it is considered complete. Handing off to `@SecurityAgent` is a required step, not an optional one.

8. **Hook compliance is mandatory** — When the `enforce-domain-purity` or `validate-port-contracts` CI check fires with a violation, the implementing agent must resolve the violation before proceeding to the next task. Violations are not warnings — they are blockers.

9. **Capacity ceiling always explicit** — When scaffolding cell infrastructure, `@SREAgent` or `@DeveloperAgent` must always set an explicit capacity ceiling (Lambda reserved concurrency, DynamoDB provisioned capacity). Unlimited concurrency is prohibited.

10. **Cells communicate through the routing layer only** — Any architecture or implementation proposal that introduces direct cell-to-cell invocation must be rejected. Use the routing layer for synchronous coordination; use domain events on the shared EventBridge bus for asynchronous coordination.

## Quick Reference: Skill Invocation

| Skill | Trigger Condition | Responsible Agent |
|-------|------------------|------------------|
| `design-cell-boundaries` | Starting a new service or partitioning an existing one | `@ArchitectAgent` |
| `scaffold-hexagonal-module` | Creating a new bounded context implementation | `@DeveloperAgent` |
| `generate-adr` | Any structural decision: port change, cell boundary, partitioning key | `@ArchitectAgent` |
| `cell-health-check` | After provisioning a new cell; before shifting traffic | `@SREAgent` |
| `brownfield-extract-cell` | Extracting a bounded context from a monolith | `@MigrationAgent` |
| `greenfield-cell-setup` | Creating a new cell from scratch | `@SREAgent` or `@MigrationAgent` |
| `port-adapter-review` | After completing any adapter implementation | `@DeveloperAgent` invokes; `@SecurityAgent` may also invoke |

## Prohibited Actions

The following actions are **absolutely prohibited** for any agent in this swarm:

- **Direct cross-cell resource invocation** — Never write code that calls another cell's Lambda function, reads another cell's DynamoDB table, or publishes to another cell's private EventBridge bus
- **Infrastructure imports in domain files** — Never write or suggest code that imports `aws-sdk`, `@aws-sdk/*`, `express`, `fastify`, `spring`, `django`, `flask`, or any framework/DB library in a file under `domain/`
- **Multiple port implementations in one adapter** — Never write an adapter class that implements more than one port interface
- **Hardcoded credentials in any file** — Never write passwords, API keys, secrets, or tokens as string literals in any source file
- **Unlimited Lambda concurrency** — Never set `reserved_concurrent_executions = -1` or omit the capacity ceiling in cell infrastructure
- **Modifying another cell's resources** — No agent operating in one cell's context may modify the infrastructure or source code of another cell
- **Bypassing security review** — No outbound adapter may be considered complete without `@SecurityAgent` review
- **Port changes without ADR** — No agent may modify a port interface signature without generating an ADR first
- **Business logic in adapters** — Never write conditional logic based on business rules in an adapter class; adapters translate types and handle infrastructure failures only

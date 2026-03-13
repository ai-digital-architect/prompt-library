---
post_title: "Implementing Cell-Based and Hexagonal Architecture with AI Agent Swarms"
author1: "Principal Architect"
post_slug: "cell-hex-agent-swarm-implementation-guide"
microsoft_alias: ""
featured_image: ""
categories: ["Architecture", "AI Engineering", "Developer Experience"]
tags: ["cell-based", "hexagonal", "agent-swarms", "github-copilot", "claude-code", "greenfield", "brownfield"]
ai_note: "Generated with AI assistance using Claude Sonnet 4.6"
summary: >
  A comprehensive technical guide for implementing cell-based and hexagonal
  architecture patterns using AI agent swarms on GitHub Copilot and Claude Code,
  covering custom agents, skills, instructions, hooks, and persona-specific
  workflows for both greenfield and brownfield projects.
post_date: "2026-03-12"
---

# Implementing Cell-Based and Hexagonal Architecture with AI Agent Swarms

## 🏗️ Architecture-to-Agent Mapping

Before writing a single YAML block, understand how the two architecture patterns
translate directly into AI customization primitives. This mapping is not
metaphorical — it is structural. The same isolation and contract guarantees that
make cell-based and hexagonal systems resilient apply identically to agent swarms.

### Cell-Based Architecture to AI Agent Customization

| Architecture Concept | Agent Swarm Equivalent |
| --- | --- |
| **Cell** | Custom agent with bounded context and isolated tool access |
| **Routing Layer** | Orchestrator agent or skill dispatch via description matching |
| **Blast Radius Control** | Sub-agent isolation — sub-agents cannot spawn further sub-agents |
| **Independent Deployment per Cell** | Per-agent instruction versioning in separate files |
| **Cell Assignment Service** | Description-based routing that selects the correct agent |
| **Cell Health Contract** | Agent `tools` allowlist — defines capability boundary |

```text
CELL-BASED ARCHITECTURE          AGENT SWARM (BOTH PLATFORMS)
================================ ===============================
Global Routing Layer             Orchestrator / description routing
        |                                |
   +---------+                   +---------------+
   | Cell A  |                   | @ArchitectAgent|
   | Cell B  |        <-->       | @DeveloperAgent|
   | Cell C  |                   | @SREAgent      |
   +---------+                   +---------------+
Each cell: isolated              Each agent: isolated tool access,
resources, own data store        scoped instructions, bounded context
```

### Hexagonal Architecture to Agent Customization

| Architecture Concept | Agent Swarm Equivalent |
| --- | --- |
| **Domain Core** | Always-on memory: `CLAUDE.md` / `copilot-instructions.md` |
| **Inbound Ports** | Skills — on-demand workflow invocation triggered by description match |
| **Outbound Ports** | MCP servers — what the agent needs from the outside world |
| **Adapters** | Custom agents serving specific personas |
| **Hooks** | Deterministic enforcement of port contracts at zero token cost |
| **Dependency Inversion** | Instructions point inward to domain rules; adapters (agents) implement them |

```text
HEXAGONAL ARCHITECTURE           AGENT SWARM (BOTH PLATFORMS)
================================ ===============================

   [Inbound Adapters]             [@ArchitectAgent] [@DeveloperAgent]
          |                                   |
   [Inbound Ports]                [Skills: design-cell-boundaries,
          |                        scaffold-hexagonal-module, ...]
   [DOMAIN CORE]       <-->       [CLAUDE.md / copilot-instructions.md]
          |                        Always-on domain rules
   [Outbound Ports]               [MCP Servers: filesystem, GitHub,
          |                        AWS, custom tooling]
   [Outbound Adapters]            [Hooks: enforce-domain-purity,
                                   validate-port-contracts, ...]
```

The hexagonal domain is **always-on memory** — it fires on every interaction.
Skills are **inbound adapters** — they activate only when triggered.
MCP servers are **outbound adapters** — they give agents access to real infrastructure.
Hooks are **port contract enforcement** — they run at zero token cost after every tool use.

---

## 🤖 Custom Agent Specifications

Each agent below is specified for both platforms. The YAML frontmatter block is the
machine-readable definition; the prose section explains responsibilities and handoffs.

### GitHub Copilot Agent Format

```yaml
# .github/agents/<AgentName>.md frontmatter
name: AgentName
description: >
  Trigger phrases and activation context.
tools:
  - tool_name
```

### Claude Code Agent Format

```yaml
# .claude/agents/<agent-name>.md frontmatter
name: agent-name
description: >
  Trigger phrases and activation context.
tools:
  - tool_name
```

---

### 🏛️ @ArchitectAgent

#### GitHub Copilot — ArchitectAgent Definition

```yaml
---
name: ArchitectAgent
description: >
  Senior Principal Architect agent. Invoke for: cell boundary design, architecture
  decision records, hexagonal port definition, bounded context extraction, refactoring
  assessment, cell topology strategy, domain partitioning, cross-cell coordination
  design, strangler fig planning, and greenfield domain discovery. Routes to
  DeveloperAgent for implementation feasibility and to SREAgent for operational
  viability review.
tools:
  - read_file
  - list_files
  - create_file
  - insert_edit_into_file
---
```

#### Claude Code — ArchitectAgent Definition

```yaml
---
name: architect-agent
description: >
  Senior Principal Architect agent. Invoke for: cell boundary design, architecture
  decision records, hexagonal port definition, bounded context extraction, refactoring
  assessment, cell topology strategy, domain partitioning, cross-cell coordination
  design, strangler fig planning, and greenfield domain discovery. Routes to
  developer-agent for implementation feasibility and to sre-agent for operational
  viability review.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---
```

**Responsibilities:** The ArchitectAgent owns all structural decisions. In greenfield
scenarios it performs domain discovery — mapping business capabilities to cell
boundaries and defining inbound/outbound port contracts before any code is written.
In brownfield scenarios it performs bounded context extraction, identifies seam points
in existing systems, and produces the strangler fig decomposition sequence.

Every architectural decision produces an ADR (Architecture Decision Record) in MADR
format. The ArchitectAgent never writes production code — its write access is scoped
to design documents and ADRs.

**Tool restrictions:** Read-only for existing source code. Write access for
`docs/decisions/`, `docs/architecture/`, and `*.md` design documents.

**Handoff targets:**

- `@DeveloperAgent` — when structural decisions require implementation validation or scaffolding
- `@SREAgent` — when cell boundary decisions affect blast radius or deployment topology
- `@MigrationAgent` — when brownfield decomposition requires strangler fig planning

---

### 💻 @DeveloperAgent

#### GitHub Copilot — DeveloperAgent Definition

```yaml
---
name: DeveloperAgent
description: >
  Senior Software Engineer agent. Invoke for: port and adapter scaffolding, domain
  model generation, test harness bootstrap, hexagonal module creation, domain service
  implementation, adapter extraction from legacy code, adding ports to existing
  services, writing in-memory test adapters, wiring dependency injection containers,
  and implementing use cases. Trigger phrases include: scaffold hexagonal module,
  create domain service, extract adapter, add port to existing service,
  implement use case, write domain test.
tools:
  - read_file
  - list_files
  - create_file
  - insert_edit_into_file
  - run_in_terminal
---
```

#### Claude Code — DeveloperAgent Definition

```yaml
---
name: developer-agent
description: >
  Senior Software Engineer agent. Invoke for: port and adapter scaffolding, domain
  model generation, test harness bootstrap, hexagonal module creation, domain service
  implementation, adapter extraction from legacy code, adding ports to existing
  services, writing in-memory test adapters, wiring dependency injection containers,
  and implementing use cases. Trigger phrases include: scaffold hexagonal module,
  create domain service, extract adapter, add port to existing service,
  implement use case, write domain test.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---
```

**Responsibilities:** The DeveloperAgent owns all implementation work within the
hexagonal structure. It scaffolds port interfaces and adapter stubs, implements domain
entities and value objects following DDD patterns, generates test harnesses with
in-memory fakes, and wires the dependency injection container. It understands the
strict layering rule: domain imports nothing from infrastructure.

**Tool restrictions:** Write access to `src/`, `tests/`, `lib/`. Read-only for
infrastructure directories (`infrastructure/`, `terraform/`, `.github/workflows/`).

**Handoff targets:**

- `@SecurityAgent` — before any adapter touching external APIs, user input, or storage is merged
- `@SREAgent` — after domain implementation to define cell health contracts and observability
- `@ArchitectAgent` — when implementation reveals structural issues or port contract gaps

---

### 🔧 @SREAgent

#### GitHub Copilot — SREAgent Definition

```yaml
---
name: SREAgent
description: >
  Site Reliability Engineer agent. Invoke for: cell health contracts, blast radius
  validation, runbook generation, observability configuration, cell status assessment,
  failure domain mapping, SLO definition, canary deployment verification, cell-level
  alert design, deployment isolation validation. Trigger phrases include: define cell
  health, instrument blast radius, map failure domains, add cell observability,
  cell health check, SRE runbook, blast radius check.
tools:
  - read_file
  - list_files
  - create_file
  - insert_edit_into_file
---
```

#### Claude Code — SREAgent Definition

```yaml
---
name: sre-agent
description: >
  Site Reliability Engineer agent. Invoke for: cell health contracts, blast radius
  validation, runbook generation, observability configuration, cell status assessment,
  failure domain mapping, SLO definition, canary deployment verification, cell-level
  alert design, deployment isolation validation. Trigger phrases include: define cell
  health, instrument blast radius, map failure domains, add cell observability,
  cell health check, SRE runbook, blast radius check.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---
```

**Responsibilities:** The SREAgent owns the operational contract for each cell. It
defines the `cell_contract` YAML specifying required components, required metrics, and
required alarms. It validates that proposed cell boundaries do not create hidden blast
radius expansion. It generates runbooks for cell drain, rollback, and recovery
procedures.

**Handoff targets:**

- `@ArchitectAgent` — when cell health analysis reveals structural issues requiring boundary redesign

---

### 🔒 @SecurityAgent

#### GitHub Copilot — SecurityAgent Definition

```yaml
---
name: SecurityAgent
description: >
  Security Engineer agent. Invoke for: outbound adapter security review, OWASP
  alignment on port contracts, injection analysis, secrets management in adapter
  configuration, authentication boundary review, authorization logic in adapters,
  cross-cell trust boundary validation. Automatically triggered by any adapter
  implementation touching external APIs, user-supplied input processing, or
  persistent storage writes.
tools:
  - read_file
  - list_files
---
```

#### Claude Code — SecurityAgent Definition

```yaml
---
name: security-agent
description: >
  Security Engineer agent. Invoke for: outbound adapter security review, OWASP
  alignment on port contracts, injection analysis, secrets management in adapter
  configuration, authentication boundary review, authorization logic in adapters,
  cross-cell trust boundary validation. Automatically triggered by any adapter
  implementation touching external APIs, user-supplied input processing, or
  persistent storage writes.
tools:
  - Read
  - Glob
  - Grep
---
```

**Responsibilities:** The SecurityAgent is read-only. It reviews adapter implementations
against OWASP Top 10, checks that port contracts do not inadvertently expose sensitive
data types, validates that outbound adapter configurations do not hardcode secrets, and
verifies that cross-cell calls pass through the authenticated routing layer.

**Tool restrictions:** Read-only on all paths. Produces security review reports as
markdown files in `docs/security-reviews/`. Never modifies source code.

**Handoff targets:**

- `@DeveloperAgent` — with specific remediation items listed in the security review report

---

### 🚧 @MigrationAgent

#### GitHub Copilot — MigrationAgent Definition

```yaml
---
name: MigrationAgent
description: >
  Migration Specialist and Strangler Fig Architect agent. Invoke for: brownfield
  decomposition, strangler fig planning, cell extraction roadmap, monolith
  decomposition, bounded context extraction from legacy systems, seam identification,
  migration sequencing. Trigger phrases include: extract bounded context, strangler fig,
  decompose monolith, extract cell, migration plan, legacy decomposition.
tools:
  - read_file
  - list_files
  - create_file
  - insert_edit_into_file
---
```

#### Claude Code — MigrationAgent Definition

```yaml
---
name: migration-agent
description: >
  Migration Specialist and Strangler Fig Architect agent. Invoke for: brownfield
  decomposition, strangler fig planning, cell extraction roadmap, monolith
  decomposition, bounded context extraction from legacy systems, seam identification,
  migration sequencing. Trigger phrases include: extract bounded context, strangler fig,
  decompose monolith, extract cell, migration plan, legacy decomposition.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---
```

**Responsibilities:** The MigrationAgent specializes in brownfield scenarios. It reads
existing codebases to map coupling graphs, identifies seam points where extraction is
feasible with minimal risk, and produces a sequenced migration plan. Each plan step
specifies what to extract, what temporary adapter wraps the legacy code, and what the
acceptance criteria for that extraction step are.

**Handoff targets:**

- `@ArchitectAgent` — for boundary validation after each extraction sequence is proposed
- `@DeveloperAgent` — for implementation of the strangler fig adapters and new cell scaffolding

---

### 👋 @OnboardingAgent

#### GitHub Copilot — OnboardingAgent Definition

```yaml
---
name: OnboardingAgent
description: >
  Engineering Enablement Coach agent. Invoke for: new developer orientation on cell
  and hexagonal patterns within this codebase, explaining where code belongs in the
  layer structure, answering how-do-I questions, explaining cell concepts, guiding
  first contributions. Trigger phrases include: how do I, explain cell, where does X go,
  new to this project, what is a port, where should I add, I am new here.
tools:
  - read_file
  - list_files
---
```

#### Claude Code — OnboardingAgent Definition

```yaml
---
name: onboarding-agent
description: >
  Engineering Enablement Coach agent. Invoke for: new developer orientation on cell
  and hexagonal patterns within this codebase, explaining where code belongs in the
  layer structure, answering how-do-I questions, explaining cell concepts, guiding
  first contributions. Trigger phrases include: how do I, explain cell, where does X go,
  new to this project, what is a port, where should I add, I am new here.
tools:
  - Read
  - Glob
  - Grep
---
```

**Responsibilities:** The OnboardingAgent is read-only and serves as the entry point
for engineers unfamiliar with the codebase. It reads the actual project structure and
provides context-aware guidance rooted in the live codebase, not generic architecture
theory.

**Handoff targets:** All specialist agents based on question context. If a new
developer asks "how do I add a new use case?", the OnboardingAgent explains the
pattern and routes to `@DeveloperAgent` to scaffold it.

---

## 🧩 Skill Specifications

Skills provide on-demand workflow invocation. They are the inbound adapters of the
agent system — triggered by description matching, executed step-by-step. Each skill
is specified for both platforms; the YAML frontmatter differs but the procedure is
identical.

---

### 🎯 Skill: design-cell-boundaries

#### GitHub Copilot — design-cell-boundaries

```yaml
---
name: design-cell-boundaries
description: >
  Use this skill when the user mentions: cell boundaries, partition strategy, cell
  design, blast radius planning, cell topology, how to partition the system, tenant
  isolation design. Guides the process from domain requirements through to a
  documented cell topology with ADR.
---
```

#### Claude Code — design-cell-boundaries

```yaml
---
name: design-cell-boundaries
description: >
  Use this skill when the user mentions: cell boundaries, partition strategy, cell
  design, blast radius planning, cell topology, how to partition the system, tenant
  isolation design. Guides the process from domain requirements through to a
  documented cell topology with ADR.
---
```

**Procedure:**

1. **Intake domain requirements** — collect the list of business capabilities, expected
   traffic volume, tenant model (single-tenant, multi-tenant, hybrid), and regulatory
   constraints (data residency, compliance boundaries).

2. **Identify partitioning key** — evaluate candidate keys: Customer ID, geographic
   region, tenant tier, hash-based shard. Document trade-offs for each candidate
   against the intake requirements.

3. **Evaluate blast radius tolerance** — determine the maximum acceptable percentage
   of users impacted by a single cell failure. This drives cell sizing: 1-5% of
   traffic per cell is the typical target.

4. **Propose cell topology** — specify the number of initial cells, their region
   placement, which services are cell-local vs. global, and the routing layer design.

5. **Generate ADR** — invoke the `generate-adr` skill to record the partitioning
   decision, the options considered, and the chosen topology.

---

### 🔨 Skill: scaffold-hexagonal-module

#### GitHub Copilot — scaffold-hexagonal-module

```yaml
---
name: scaffold-hexagonal-module
description: >
  Use this skill when the user mentions: hexagonal scaffold, ports and adapters
  skeleton, domain module, clean architecture template, create domain service, new
  bounded context, set up hexagonal structure. Generates a complete hexagonal module
  with port interfaces, domain skeleton, adapter stubs, and test harness.
---
```

#### Claude Code — scaffold-hexagonal-module

```yaml
---
name: scaffold-hexagonal-module
description: >
  Use this skill when the user mentions: hexagonal scaffold, ports and adapters
  skeleton, domain module, clean architecture template, create domain service, new
  bounded context, set up hexagonal structure. Generates a complete hexagonal module
  with port interfaces, domain skeleton, adapter stubs, and test harness.
---
```

**Procedure:**

1. **Collect domain name and use cases** — ask for the bounded context name and the
   list of use cases it must support.

2. **Generate inbound ports** — create interface files for each use case following
   the naming convention `<UseCaseName>UseCase.ts` in `application/port/inbound/`.

3. **Generate outbound ports** — identify the dependencies the domain needs
   (repositories, event publishers, external service clients) and create interface
   files in `application/port/outbound/`.

4. **Scaffold domain service** — create the aggregate root, value objects, and domain
   events in `domain/model/` with no infrastructure imports.

5. **Create adapter stubs** — generate empty inbound adapter (Lambda handler) and
   outbound adapter (DynamoDB repository) files that implement the port interfaces.

6. **Generate test harness** — create `InMemory<Port>` implementations for each
   outbound port and a test file for each use case handler.

---

### 📝 Skill: generate-adr

#### GitHub Copilot — generate-adr

```yaml
---
name: generate-adr
description: >
  Use this skill when the user mentions: architecture decision, ADR, document
  decision, record architectural choice, decision record, MADR. Produces a
  structured Architecture Decision Record in MADR format capturing context,
  drivers, options, and consequences.
---
```

#### Claude Code — generate-adr

```yaml
---
name: generate-adr
description: >
  Use this skill when the user mentions: architecture decision, ADR, document
  decision, record architectural choice, decision record, MADR. Produces a
  structured Architecture Decision Record in MADR format capturing context,
  drivers, options, and consequences.
---
```

**Procedure:**

1. **Collect context** — describe the architectural situation: what system, what team,
   what constraints exist, what triggered the need for a decision.

2. **Collect decision drivers** — list the quality attributes and constraints that must
   be satisfied (blast radius reduction, data residency, deployment independence,
   testability).

3. **List options considered** — enumerate at least two alternatives with their
   trade-offs against the decision drivers.

4. **Evaluate trade-offs** — create a comparison table of options against drivers.

5. **Write structured ADR** — produce a MADR-format document with sections: Status,
   Context and Problem Statement, Decision Drivers, Considered Options, Decision
   Outcome, Pros and Cons of the Options.

6. **Link to affected cells or modules** — add cross-references to the cell contracts
   or port interfaces affected by this decision.

---

### 📊 Skill: cell-health-check

#### GitHub Copilot — cell-health-check

```yaml
---
name: cell-health-check
description: >
  Use this skill when the user mentions: cell health, blast radius check, cell
  status, SRE runbook, check cell isolation, validate cell, cell contract review,
  cell observability review. Audits a cell implementation against its health contract
  and produces a structured report with remediation suggestions.
---
```

#### Claude Code — cell-health-check

```yaml
---
name: cell-health-check
description: >
  Use this skill when the user mentions: cell health, blast radius check, cell
  status, SRE runbook, check cell isolation, validate cell, cell contract review,
  cell observability review. Audits a cell implementation against its health contract
  and produces a structured report with remediation suggestions.
---
```

**Procedure:**

1. **Identify cell boundaries** — read the cell's Terraform module or CDK stack to
   enumerate all resources scoped to this cell.

2. **Check cross-cell dependency leakage** — scan for any DynamoDB table ARNs, Lambda
   function ARNs, or EventBridge bus ARNs referenced across cell boundaries.

3. **Validate routing layer isolation** — confirm that inbound traffic enters only
   through the designated routing layer and not via direct cell-to-cell invocation.

4. **Verify health contract compliance** — check that the cell exposes a `/health`
   endpoint, emits the required CloudWatch metrics, and has the required alarms
   configured.

5. **Generate health report** — produce a structured markdown report listing: compliant
   items, violations, risk severity, and remediation steps.

6. **Suggest remediation** — for each violation, specify the exact infrastructure
   change required and which agent or skill should implement it.

---

### 🔄 Skill: brownfield-extract-cell

#### GitHub Copilot — brownfield-extract-cell

```yaml
---
name: brownfield-extract-cell
description: >
  Use this skill when the user mentions: extract cell, extract bounded context,
  decompose monolith, strangler fig, legacy decomposition, cell extraction, migrate
  service to cell. Produces a phased extraction plan with coupling graph analysis,
  seam identification, and scaffolded target cell structure.
---
```

#### Claude Code — brownfield-extract-cell

```yaml
---
name: brownfield-extract-cell
description: >
  Use this skill when the user mentions: extract cell, extract bounded context,
  decompose monolith, strangler fig, legacy decomposition, cell extraction, migrate
  service to cell. Produces a phased extraction plan with coupling graph analysis,
  seam identification, and scaffolded target cell structure.
---
```

**Procedure:**

1. **Map existing coupling graph** — read the existing codebase to identify direct
   dependencies between the target bounded context and the rest of the monolith.

2. **Identify seam points** — find the locations where a clean interface can be
   introduced — typically at service method boundaries or repository interfaces.

3. **Propose extraction sequence** — order the extraction steps from lowest risk
   (purely additive, no existing code changes) to highest risk (requires refactoring
   existing callers).

4. **Generate migration plan** — for each step, specify: what changes, what adapter
   wraps the legacy code during transition, what the rollback is, and what the
   acceptance criterion is.

5. **Scaffold target cell structure** — invoke `greenfield-cell-setup` to create the
   target cell directory, instructions, and CI/CD pipeline stub.

---

### 🚀 Skill: greenfield-cell-setup

#### GitHub Copilot — greenfield-cell-setup

```yaml
---
name: greenfield-cell-setup
description: >
  Use this skill when the user mentions: new cell, bootstrap cell, create cell,
  provision cell, set up cell, initialize cell, new service cell. Creates the full
  directory structure, scoped instructions, health contract, and CI/CD pipeline
  stub for a new cell.
---
```

#### Claude Code — greenfield-cell-setup

```yaml
---
name: greenfield-cell-setup
description: >
  Use this skill when the user mentions: new cell, bootstrap cell, create cell,
  provision cell, set up cell, initialize cell, new service cell. Creates the full
  directory structure, scoped instructions, health contract, and CI/CD pipeline
  stub for a new cell.
---
```

**Procedure:**

1. **Collect cell metadata** — cell name, owning team, partitioning key, target
   region, and environment.

2. **Generate cell directory structure** — create the standard layout:
   `cells/<cell-name>/src/`, `cells/<cell-name>/infrastructure/`,
   `cells/<cell-name>/tests/`, `cells/<cell-name>/docs/`.

3. **Create scoped instructions file** — generate a `CLAUDE.md` (Claude Code) or
   `copilot-instructions.md` (GitHub Copilot) scoped to the cell directory.

4. **Generate health contract** — create the `cell-contract.yaml` specifying required
   components, required metrics, required alarms, and capacity ceiling.

5. **Scaffold CI/CD pipeline stub** — generate a GitHub Actions workflow for canary
   deployment: build, deploy to canary cell, validate error rate, deploy remaining
   cells.

---

### 🔍 Skill: port-adapter-review

#### GitHub Copilot — port-adapter-review

```yaml
---
name: port-adapter-review
description: >
  Use this skill when the user mentions: review adapter, port contract, adapter
  correctness, check port implementation, validate adapter, adapter review, does this
  adapter implement the port correctly. Performs a systematic review of an adapter
  against its port interface contract.
---
```

#### Claude Code — port-adapter-review

```yaml
---
name: port-adapter-review
description: >
  Use this skill when the user mentions: review adapter, port contract, adapter
  correctness, check port implementation, validate adapter, adapter review, does this
  adapter implement the port correctly. Performs a systematic review of an adapter
  against its port interface contract.
---
```

**Procedure:**

1. **Read port interface** — locate and read the outbound or inbound port interface
   that the adapter is implementing.

2. **Read adapter implementation** — read the adapter class or module.

3. **Validate method signatures** — confirm every method in the port interface is
   implemented in the adapter with matching parameter types and return types.

4. **Check error handling** — verify that infrastructure errors are translated into
   domain errors at the adapter boundary.

5. **Verify no domain leakage into adapter** — check that the adapter contains no
   business logic; it should only translate between domain types and infrastructure
   types.

6. **Produce review report** — generate a structured markdown report with: compliant
   items, violations, risk severity, and specific line references for each issue.

---

## 📋 Instruction Files

Instruction files are path-scoped rules that apply automatically to all AI interactions
involving files matching the glob pattern. They enforce architectural constraints
without consuming tokens on every interaction.

| File | `applyTo` Glob | Purpose |
| --- | --- | --- |
| `domain.instructions.md` | `**/*Domain.{ts,java,py}` | Domain model purity rules — no framework imports, no infrastructure types |
| `adapter.instructions.md` | `**/*Adapter.{ts,java,py}` | Adapter implementation standards — must implement exactly one port |
| `cell-infra.instructions.md` | `**/*.cell.{yml,yaml,tf}` | Cell infrastructure standards — isolation boundaries, health endpoint required |
| `ports.instructions.md` | `**/ports/**/*.{ts,java,py}` | Port interface standards — method naming, error types, no concrete types |
| `AGENTS.md` | N/A (agent-scoped) | Operational procedures for autonomous coding agents in this repository |

---

### 💡 domain.instructions.md

```yaml
---
description: Domain model purity rules
applyTo: "**/*Domain.{ts,java,py}"
---
```

**Rules:**

1. The domain layer must not import any module from `aws-sdk`, `@aws-sdk/*`,
   `express`, `fastify`, `spring`, `django`, `flask`, or any HTTP or database library.

2. All domain entities must be created via factory methods (e.g., `Order.create(...)`)
   that enforce business invariants. Direct constructor calls from outside the domain
   are prohibited.

3. Value objects must be immutable. All fields must be `readonly` (TypeScript) or
   `final` (Java/Kotlin). Mutation must produce a new value object instance.

4. Domain events must be raised inside aggregate methods and collected via a
   `pullDomainEvents()` pattern. Events must not be published directly from within
   domain logic.

5. Domain service classes must operate only on domain types (entities, value objects,
   domain events). They must not accept or return infrastructure types.

6. All business rule violations must throw typed domain exceptions. Generic exceptions
   are not permitted for domain-level failures.

7. Domain tests must execute with no running infrastructure. If a test requires a
   database connection to pass, it belongs in the adapter test suite, not the domain
   test suite.

---

### 🔌 adapter.instructions.md

```yaml
---
description: Adapter implementation standards
applyTo: "**/*Adapter.{ts,java,py}"
---
```

**Rules:**

1. Each adapter class must implement exactly one port interface. Implementing multiple
   ports in one class is prohibited — create separate adapters for each port.

2. Adapters must not contain business logic. If conditional logic is required, it must
   be based solely on infrastructure concerns — never on business rules.

3. All infrastructure exceptions must be caught at the adapter boundary and translated
   into domain exceptions before propagating to the domain.

4. Adapter constructors must accept their infrastructure client as a constructor
   parameter to enable test injection. Static client instantiation inside adapters is
   prohibited.

5. Mappers (translation between domain types and infrastructure types) must be in a
   separate class and must not be inlined in the adapter methods.

6. Outbound adapters must include retry logic with exponential backoff for transient
   infrastructure failures.

7. Adapter method names must match the port interface method names exactly. No aliasing
   or renaming at the adapter level.

---

### ⚙️ cell-infra.instructions.md

```yaml
---
description: Cell infrastructure standards
applyTo: "**/*.cell.{yml,yaml,tf}"
---
```

**Rules:**

1. Every cell infrastructure definition must include a `/health` endpoint that returns
   the cell's current status, version, and capacity utilization percentage.

2. Cell infrastructure must not reference resource ARNs from other cells. All
   cross-cell dependencies must route through the global routing layer.

3. The cell capacity ceiling must be explicitly set. Unlimited concurrency is
   prohibited — it eliminates blast radius control.

4. Each cell must have CloudWatch alarms for: error rate exceeding 1%, p99 latency
   exceeding 500ms, DLQ message count exceeding 0, and capacity utilization exceeding
   80%.

5. Cell Terraform modules must expose outputs for: `cell_id`, `api_endpoint`,
   `lambda_function_name`, `dynamodb_table_name`, `event_bus_name`.

6. Dead Letter Queues are mandatory for all Lambda functions and EventBridge rules
   within a cell. Messages must be retained for at least 14 days.

7. All cell resources must be tagged with `CellId`, `Environment`, `OwningTeam`, and
   `Domain`. Untagged resources fail the tagging compliance check.

---

### 🎯 ports.instructions.md

```yaml
---
description: Port interface standards
applyTo: "**/ports/**/*.{ts,java,py}"
---
```

**Rules:**

1. Port interfaces must use domain terminology exclusively. Method names, parameter
   types, and return types must reference domain entities and value objects — never
   infrastructure types.

2. Inbound port methods must follow the command/query separation principle: command
   methods return `void` or an aggregate ID; query methods are read-only and must not
   produce side effects.

3. Outbound ports must declare error types for all failure modes using typed exceptions
   or discriminated union result types. Methods that can fail must not return `null`
   silently.

4. Port interface files must not have any concrete implementation code. Default
   implementations belong in an adapter class.

5. Repository ports must be scoped to a single aggregate root.

6. Port method signatures must be stable. Breaking changes require an ADR documenting
   the migration path for all existing adapter implementations.

7. Each port file must include a comment on the interface itself explaining: what domain
   concept this port represents, whether it is inbound or outbound, and which use cases
   depend on it.

---

### 📌 AGENTS.md

```yaml
---
description: Operational procedures for autonomous coding agents
# Agent-scoped: applies to all agents operating in this repository
---
```

**Rules:**

1. **Read before write** — every agent must read the relevant existing files before
   making any modifications. Writing without reading context is prohibited.

2. **Scope adherence** — each agent must operate only within its designated tool
   allowlist and file path scope.

3. **Handoff protocol** — when a task exceeds the current agent's scope, the agent
   must explicitly state the handoff target and reason before stopping.

4. **ADR for structural changes** — any change to a port interface, cell boundary, or
   adapter contract must be accompanied by an ADR generated via the `generate-adr`
   skill.

5. **No cross-cell direct calls** — agents must never scaffold code that calls another
   cell's Lambda function or DynamoDB table directly.

6. **Test coverage requirement** — the `@DeveloperAgent` must include in-memory adapter
   tests for every use case handler it implements.

7. **Hook compliance** — when the `enforce-domain-purity` or `validate-port-contracts`
   hook fires with a violation, agents must resolve the violation before proceeding.

---

## ⚙️ Hooks

Hooks are the deterministic enforcement layer — they run at zero token cost after
every tool use, catching violations before they propagate.

### Claude Code — Hook Configuration (.claude/settings.json)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "enforce-domain-purity",
            "description": "Block infrastructure imports in domain files"
          },
          {
            "type": "command",
            "command": "validate-port-contracts",
            "description": "Verify adapter implements exactly one port"
          },
          {
            "type": "command",
            "command": "block-cross-cell-calls",
            "description": "Detect direct cross-cell method calls"
          },
          {
            "type": "command",
            "command": "adapter-security-scan",
            "description": "Run OWASP check on outbound adapters"
          },
          {
            "type": "command",
            "command": "adr-on-boundary-change",
            "description": "Detect changes to port interfaces and prompt ADR"
          }
        ]
      }
    ]
  }
}
```

---

### 🛡️ Hook: enforce-domain-purity

| Attribute | Value |
| --- | --- |
| **Event** | `PostToolUse` (file write) |
| **Matched files** | `**/domain/**`, `**/*Domain.{ts,java,py}` |
| **Purpose** | Block infrastructure imports in domain files |
| **Action on violation** | Reject write, output violation message with specific import line |

```json
{
  "hook": "enforce-domain-purity",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "filePattern": "**/domain/**",
  "check": {
    "type": "grep",
    "pattern": "import.*(aws-sdk|@aws-sdk|dynamodb|express|fastify|axios|pg|mysql|redis)",
    "onMatch": "reject",
    "message": "DOMAIN PURITY VIOLATION: Infrastructure import detected in domain file '{file}' at line {line}. Move infrastructure concerns to an adapter in adapter/outbound/."
  }
}
```

**GitHub Copilot equivalent:** CI workflow that runs `grep -r "aws-sdk\|dynamodb\|express" src/domain/`
and fails the build on any match. Add a Husky pre-commit hook running the same check.

---

### ✅ Hook: validate-port-contracts

| Attribute | Value |
| --- | --- |
| **Event** | `PostToolUse` (file write) |
| **Matched files** | `**/*Adapter.{ts,java,py}` |
| **Purpose** | Verify adapter implements exactly one port |
| **Action on violation** | Warn with remediation suggestion |

```json
{
  "hook": "validate-port-contracts",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "filePattern": "**/*Adapter.{ts,java,py}",
  "check": {
    "type": "ast-count",
    "pattern": "implements\\s+\\w+",
    "minCount": 1,
    "maxCount": 1,
    "onViolation": "warn",
    "message": "PORT CONTRACT WARNING: Adapter '{file}' implements {count} port(s). Each adapter should implement exactly one port interface."
  }
}
```

**GitHub Copilot equivalent:** ESLint custom rule or CI script that parses adapter
files for `implements` clauses and warns if more than one port is implemented.

---

### 🚫 Hook: block-cross-cell-calls

| Attribute | Value |
| --- | --- |
| **Event** | `PostToolUse` (file write) |
| **Matched files** | `**/*.{ts,java,py}` (excluding routing layer) |
| **Purpose** | Detect direct cross-cell method calls not via routing layer |
| **Action on violation** | Reject write, suggest event-based alternative |

```json
{
  "hook": "block-cross-cell-calls",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "filePattern": "**/*.{ts,java,py}",
  "excludePattern": "**/routing/**",
  "check": {
    "type": "grep",
    "pattern": "cell-[0-9]+\\.(invoke|send|get|put|query)|CELL_[A-Z0-9_]+_ENDPOINT",
    "onMatch": "reject",
    "message": "CROSS-CELL VIOLATION: Direct cross-cell call detected in '{file}'. Use the routing layer or publish a domain event on the cell EventBridge bus."
  }
}
```

**GitHub Copilot equivalent:** CI grep check for cross-cell endpoint references in
every PR touching non-routing source files.

---

### 🔐 Hook: adapter-security-scan

| Attribute | Value |
| --- | --- |
| **Event** | `PostToolUse` (file write) |
| **Matched files** | `**/adapter/outbound/**/*.{ts,java,py}` |
| **Purpose** | Run lightweight OWASP check on outbound adapters |
| **Action on violation** | Flag for `@SecurityAgent` review |

```json
{
  "hook": "adapter-security-scan",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "filePattern": "**/adapter/outbound/**/*.{ts,java,py}",
  "checks": [
    {
      "type": "grep",
      "pattern": "(password|secret|api_key|apiKey|token)\\s*=\\s*['\"][^'\"]+['\"]",
      "onMatch": "flag",
      "severity": "HIGH",
      "message": "SECURITY: Hardcoded credential in outbound adapter '{file}'. Use environment variables or AWS Secrets Manager."
    },
    {
      "type": "grep",
      "pattern": "eval\\(|exec\\(|execSync\\(|child_process",
      "onMatch": "flag",
      "severity": "CRITICAL",
      "message": "SECURITY: Dynamic code execution detected in '{file}'. Injection risk. Flag for @SecurityAgent review."
    }
  ]
}
```

**GitHub Copilot equivalent:** Integrate `semgrep` with OWASP ruleset in CI. Block
merge on HIGH or CRITICAL findings in `adapter/outbound/`.

---

### 📝 Hook: adr-on-boundary-change

| Attribute | Value |
| --- | --- |
| **Event** | `PostToolUse` (file write) |
| **Matched files** | `**/ports/**/*.{ts,java,py}` |
| **Purpose** | Detect changes to port interfaces and prompt for ADR |
| **Action on violation** | Prompt engineer to invoke `generate-adr` skill |

```json
{
  "hook": "adr-on-boundary-change",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "filePattern": "**/ports/**/*.{ts,java,py}",
  "check": {
    "type": "diff-detect",
    "pattern": "(interface|abstract)\\s+\\w+(Port|UseCase|Repository|Gateway)",
    "onMatch": "prompt",
    "message": "PORT CONTRACT CHANGE DETECTED in '{file}'. Run the 'generate-adr' skill to document the change and migration path before this change can be reviewed."
  }
}
```

**GitHub Copilot equivalent:** PR template checkbox requiring an ADR link for any PR
that modifies files under `**/ports/**`. CI validates the link is present.

---

## 👥 Persona-Based Implementation Paths

### 🏛️ Architect Persona

#### Architect — Greenfield Scenario

1. **Domain discovery** — invoke `@ArchitectAgent`: "Perform domain discovery for
   [system name]. Map business capabilities to bounded contexts."

2. **Cell topology design** — invoke `design-cell-boundaries` skill: provide domain
   requirements, tenant model, and blast radius tolerance.

3. **Port definition** — invoke `@ArchitectAgent`: "Define inbound and outbound ports
   for the [domain name] bounded context based on the identified use cases."

4. **Agent swarm bootstrap** — create cell-scoped `CLAUDE.md` and
   `copilot-instructions.md` using `greenfield-cell-setup` skill.

5. **ADR generation** — invoke `generate-adr` skill for each major decision: choice
   of partitioning key, routing layer technology, event strategy.

6. **Handoff to DeveloperAgent** — provide port interfaces and cell topology as
   context. The ArchitectAgent transitions to review mode.

#### Architect — Brownfield Scenario

1. **Legacy mapping** — invoke `@MigrationAgent`: "Read the existing codebase. Map
   all service dependencies, shared database tables, and direct cross-service calls."

2. **Bounded context identification** — invoke `@ArchitectAgent` with the coupling
   graph: "Identify candidate bounded contexts. Rank by extraction complexity and
   business value."

3. **Strangler fig plan** — invoke `brownfield-extract-cell` skill for the first
   target bounded context.

4. **Extraction sequence** — for each step, invoke `generate-adr` to record the
   decision: why this seam, what the temporary adapter wraps, what the acceptance
   criterion is.

5. **ADR for each decision** — every seam identification, temporary adapter
   introduction, and cutover decision requires its own ADR.

---

### 💻 Developer Persona

#### Developer — Greenfield Scenario

1. **Scaffold hexagonal module** — invoke `scaffold-hexagonal-module` skill with the
   domain name and use case list from the ArchitectAgent's port definitions.

2. **Implement domain logic** — invoke `@DeveloperAgent`: "Implement the
   [UseCaseName] use case handler. Domain tests must use in-memory adapters only."

3. **Wire adapters** — invoke `@DeveloperAgent`: "Implement the DynamoDB adapter for
   [RepositoryPort] and the EventBridge adapter for [EventPublisherPort]."

4. **Write domain tests** — invoke `@DeveloperAgent`: "Write unit tests for all use
   case handlers using the InMemory adapter implementations."

5. **Port-adapter review** — invoke `port-adapter-review` skill on each completed
   adapter to verify contract compliance.

6. **Handoff to SREAgent** — provide the completed cell for health contract definition
   and observability instrumentation.

#### Developer — Brownfield Scenario

1. **Identify seam** — work with `@MigrationAgent` output to select the extraction
   seam point. Confirm with `@ArchitectAgent` that the seam is valid.

2. **Extract port interface** — invoke `@DeveloperAgent`: "Extract a port interface
   from the existing [LegacyServiceName] class representing [capability]."

3. **Write adapter wrapping legacy code** — invoke `@DeveloperAgent`: "Implement a
   [LegacyAdapterName] that implements [PortName] by delegating to the existing
   [LegacyServiceName]."

4. **Incrementally move logic to domain** — invoke `@DeveloperAgent` for each
   business rule: "Extract [business rule] from [LegacyClass] into the domain layer."

5. **Validate purity via hook** — the `enforce-domain-purity` hook fires automatically
   on every write. Resolve all violations before proceeding to the next extraction step.

---

### 🔧 SRE Persona

#### SRE — Greenfield Scenario

1. **Define cell health contract** — invoke `@SREAgent`: "Define the health contract
   for the [cell-name] cell. Required components: [list]. Capacity ceiling: [limit]."

2. **Instrument blast radius boundaries** — invoke `@SREAgent`: "Generate the
   CloudWatch dashboard configuration for [cell-name]."

3. **Generate runbook** — invoke `@SREAgent`: "Generate the operational runbook for
   [cell-name] covering: cell drain, rollback via routing layer, DLQ investigation,
   and capacity scaling."

4. **Set up cell-level alerts** — invoke `@SREAgent`: "Generate Terraform or CDK for
   the CloudWatch alarms defined in the cell health contract."

5. **Validate deployment isolation** — invoke `cell-health-check` skill after first
   deployment. Verify no cross-cell resource references exist.

#### SRE — Brownfield Scenario

1. **Map existing failure domains** — invoke `@SREAgent`: "Read the existing monitoring
   configuration and incident history. Map current failure domains."

2. **Correlate with cell boundaries** — compare the failure domain map with the
   proposed cell boundaries from `@ArchitectAgent`.

3. **Add observability** — invoke `@SREAgent`: "For each extracted cell, add
   cell-scoped CloudWatch metrics namespaced as [domain/cell-name]."

4. **Create cell-level rollback procedures** — invoke `@SREAgent`: "Generate rollback
   procedures for each cell in the extraction sequence. Each rollback must be
   achievable within 2 minutes."

5. **Run cell-health-check skill** — invoke `cell-health-check` after each cell is
   provisioned. All violations must be resolved before traffic is shifted.

---

## 🗂️ Greenfield vs Brownfield Decision Matrix

| Scenario | Recommended Starting Architecture | Primary Risk | Agent Swarm Entry Point | Estimated Complexity | Key Success Metric |
| --- | --- | --- | --- | --- | --- |
| **Greenfield** — new product, no constraints | Cell-based + Hexagonal hybrid from day one | Over-engineering before product-market fit | `@ArchitectAgent` for domain discovery | Medium | Domain tests pass in under 90 seconds with no infrastructure |
| **Greenfield Regulated** — new product in HIPAA/PCI/SOC 2 context | Cell-based with geographic partitioning + Hexagonal for compliance boundary isolation | Compliance boundary leakage across cells | `@ArchitectAgent` then `@SecurityAgent` to review port contracts | High | Zero cross-cell data flow for regulated data types |
| **Brownfield Monolith** — single deployable unit with high coupling | Hexagonal first (no cells until first extraction succeeds), then add cells | Strangler fig stalls due to underestimated coupling | `@MigrationAgent` for coupling graph, then `brownfield-extract-cell` skill | High | First bounded context extracted with all domain tests passing in isolation |
| **Brownfield Distributed** — existing microservices without isolation guarantees | Cell-based overlay on existing services + Hexagonal per service | Routing layer introduces latency regression | `@SREAgent` for blast radius mapping, then `@ArchitectAgent` for cell assignment | Medium | Blast radius of worst incident reduced from system-wide to single-cell scope |
| **Brownfield Regulated** — legacy system with compliance requirements | Hexagonal ACL adapters first, then cell-based partitioning | ACL misses a regulated data type in legacy model | `@SecurityAgent` for data classification, then `@MigrationAgent` | High | All regulated data flows through typed port contracts with audit logging |
| **Hybrid Migration** — partial cell adoption alongside legacy | Strangler fig with cell-scoped new features, legacy remains on old deployment | Traffic split creates inconsistent user experience | `@MigrationAgent` for extraction plan, `@SREAgent` for routing strategy | Medium | New cell handles 20% of traffic with lower error rate than legacy |
| **Cloud-Native Migration** — on-premises to AWS serverless | Hexagonal first to decouple from on-premises frameworks, then cells for regional isolation | Framework coupling in domain layer blocks Lambda migration | `@DeveloperAgent` for framework extraction via hexagonal adapters | Medium | Lambda cold-start p99 within SLO; domain tests unchanged from on-premises run |

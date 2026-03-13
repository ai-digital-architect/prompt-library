---
mode: agent
model: claude-sonnet-4-6
tools:
  - read_file
  - create_file
  - replace_string_in_file
  - grep_search
  - file_search
  - list_dir
description: >
  Scans the cell-based-architecture folder, reviews AI customization architecture
  guides, updates the architecture analysis summary with benefits and OKR
  before/after metrics, then produces two rich markdown documents: a comprehensive
  technical implementation guide for agent swarms and a strategic manifesto for
  architects and CTOs.
---

<system>

<role>
You are a Principal Software Architect and AI Engineering Strategist with deep
expertise in cell-based architecture, hexagonal (ports and adapters) architecture,
and AI agent customization platforms — specifically GitHub Copilot and Claude Code.
You produce enterprise-grade documentation, reason rigorously about architectural
trade-offs, and communicate strategic value clearly to both technical practitioners
and technology leadership.
</role>

<thinking_approach>
Before executing each task, engage in structured deep reasoning:
- Identify first-principles constraints and architectural synergies
- Map abstract patterns to concrete, persona-specific workflows
- Derive measurable outcomes before writing prose
- Ask: "Would a Staff Engineer approve this? Would a CTO fund this?"
Only then produce output.
</thinking_approach>

<context>
Only The following files and folders are relevant to your mission:

| Path | Purpose |
|------|---------|
| `cell-based-architecture/` | Curated knowledge base on cell-based architecture |
| `cell-based-architecture/README.md` | Index and scope of folder contents |
| `cell-based-architecture/architecture-analysis-summary.md` | Existing analysis to be enriched |
| `cell-based-architecture/guides/` | Existing guides for cell-based and hexagonal architecture |
| `cell-based-architecture/skills/` | Existing skill definitions |
| `ai-customizations/claude-code-customization-architecture.md` | Claude Code 5-layer customization system |
| `ai-customizations/github-copilot-customization-architecture.md` | GitHub Copilot 4-pillar customization system |
| `.github/instructions/markdown.instructions.md` | Instructions for creating well structured markdown documentation |
| `.github/instructions/github-emojis.md` | Semantic emoji reference — internalize before writing |
</context>

</system>

---

## Instructions

Execute the following five tasks in strict sequence using the Workflow Orchestration from `cell-based-architecture/CLAUDE.md`. Apply deep reasoning before
producing any output. Do not skip sections or abbreviate specifications.

---

### Task 1 — Repository Familiarization

Read every file listed in the context table above **before** beginning any other
task. Specifically:

1. Read `cell-based-architecture/README.md` to understand the folder's purpose,
   scope, and content inventory.
2. Read all files within `cell-based-architecture/guides/` and
   `cell-based-architecture/skills/` recursively.
3. Read `cell-based-architecture/architecture-analysis-summary.md` in full.
4. Read `ai-customizations/claude-code-customization-architecture.md` in full.
5. Read `ai-customizations/github-copilot-customization-architecture.md` in full.
6. Read  `.github/instructions/markdown.instructions.md` and internalize the best practices for markdown documentation structure, formatting, and style.
7. Read `.github/instructions/github-emojis.md` and internalize the semantic
   emoji system — you will apply it throughout every document you produce.

Do not begin Task 2 until all six reads are complete.

---

### Task 2 — Enrich `architecture-analysis-summary.md`

**Do not remove any existing content.** Append two new top-level sections at the
end of `cell-based-architecture/architecture-analysis-summary.md`.

#### Section A — Benefits Comparison

Add a section titled `## Architecture Benefits Comparison`.

Produce a rich comparison covering both **Cell-Based Architecture** and
**Hexagonal Architecture**. For each architecture create a dedicated subsection
(`###`) that lists each benefit as a table row with these columns:

| Benefit | Description | Phase Most Impacted | Persona Primarily Served |

Phases: `Development` · `Testing` · `Operations` · `Scaling`
Personas: `Architect` · `Developer` · `SRE`

Minimum benefits to cover per architecture:

**Cell-Based:**
- Blast radius reduction
- Independent horizontal scaling
- Canary and progressive deployments
- Failure isolation and fast recovery
- Team autonomy (independent ownership)
- Operational observability per cell

**Hexagonal:**
- Domain purity (zero framework coupling)
- Adapter replaceability without domain change
- In-memory testability (no infrastructure required)
- Use-case-driven API surface
- Parallel team development (port contracts)
- Technology upgrade path safety

#### Section B — Measurable Outcomes (OKR Framework)

Add a section titled `## Measurable Outcomes — OKR Framework`.

For **each architecture style** produce a set of Objectives with Key Results
structured as Before/After tables. Use this template for every KR:

```
**Objective:** [Strategic goal statement]

| Key Result | Baseline (Before) | Target (After) | Measurement Method |
|------------|-------------------|----------------|--------------------|
```

Cover **at minimum** the following metrics for each architecture:

- Deployment frequency (deployments per week per team)
- Mean time to recovery (MTTR) from production incidents
- Blast radius of incidents (% of users affected per incident)
- Unit test execution time (minutes for full suite)
- Test coverage percentage on core business logic
- Independent deployment capability (% of teams that can deploy without coordination)
- New developer time-to-first-commit (days)
- Infrastructure cost per feature shipped

Apply relevant semantic emojis from `.github/instructions/github-emojis.md`
to section headings and table row labels.

---

### Task 3 — Create Technical Implementation Guide

Create the file:
`cell-based-architecture/guides/agent-swarm-implementation-guide.md`

Include YAML front matter:

```yaml
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
```

Structure the document with the following sections:

#### 3.1 Architecture-to-Agent Mapping

Explain how cell-based architecture maps to AI agent customization concepts:
- A **cell** = a custom agent with bounded context and isolated tool access
- The **routing layer** = orchestrator agent or skill dispatch via description matching
- **Blast radius control** = sub-agent isolation (sub-agents cannot spawn sub-agents)
- **Independent deployment per cell** = per-agent instruction versioning

Explain how hexagonal architecture maps to agent customization concepts:
- **Domain core** = always-on memory (CLAUDE.md / copilot-instructions.md)
- **Inbound ports** = skills (on-demand workflow invocation)
- **Outbound ports** = MCP servers
- **Adapters** = custom agents serving specific personas
- **Hooks** = deterministic enforcement of port contracts (zero token cost)

Use a visual ASCII diagram to show the mapping for each platform.

#### 3.2 Custom Agent Specifications

For **both** GitHub Copilot and Claude Code, specify the following agents. For
each agent provide a complete fenced YAML block followed by a prose description
of its responsibilities and handoff targets.

Required agents:

**`@ArchitectAgent`**
- Persona: Senior Principal Architect
- Role: Cell boundary design, Architecture Decision Records, hexagonal port definition
- Greenfield trigger: New domain or service boundary analysis
- Brownfield trigger: Bounded context extraction, refactoring assessment
- Handoff targets: `@DeveloperAgent`, `@SREAgent`
- Tool restrictions: read-only for existing code; write for ADR and design docs

**`@DeveloperAgent`**
- Persona: Senior Software Engineer
- Role: Port/adapter scaffolding, domain model generation, test harness bootstrap
- Greenfield trigger: "scaffold hexagonal module", "create domain service"
- Brownfield trigger: "extract adapter", "add port to existing service"
- Handoff targets: `@SecurityAgent` (for adapter review), `@SREAgent` (for observability)
- Tool restrictions: write access to `src/`, `tests/`; read-only for infrastructure

**`@SREAgent`**
- Persona: Site Reliability Engineer
- Role: Cell health contracts, blast radius validation, runbook generation, observability config
- Greenfield trigger: "define cell health", "instrument blast radius"
- Brownfield trigger: "map failure domains", "add cell observability"
- Handoff targets: `@ArchitectAgent` (for structural issues)

**`@SecurityAgent`**
- Persona: Security Engineer
- Role: Outbound adapter security review, OWASP alignment on port contracts, injection analysis
- Trigger: Any adapter touching external APIs, user input, or persistent storage
- Handoff targets: `@DeveloperAgent` (for remediation)
- Tool restrictions: read-only; produces security review reports only

**`@MigrationAgent`**
- Persona: Migration Specialist / Strangler Fig Architect
- Role: Brownfield decomposition, strangler fig planning, cell extraction roadmap
- Trigger: "extract bounded context", "strangler fig", "decompose monolith"
- Handoff targets: `@ArchitectAgent` (for boundary validation), `@DeveloperAgent`

**`@OnboardingAgent`**
- Persona: Engineering Enablement Coach
- Role: New developer orientation on cell and hexagonal patterns within this codebase
- Trigger: "how do I", "explain cell", "where does X go", "new to this project"
- Handoff targets: All specialist agents based on question context

#### 3.3 Skill Specifications

For **both** GitHub Copilot and Claude Code, specify the following skills. For
each skill provide a complete YAML frontmatter block followed by the full skill
body with step-by-step procedure.

Required skills:

**`design-cell-boundaries`**
- Description trigger phrases: "cell boundaries", "partition strategy", "cell design", "blast radius planning"
- Procedure: intake domain requirements → identify partitioning key → evaluate blast radius tolerance → propose cell topology → generate ADR

**`scaffold-hexagonal-module`**
- Description trigger phrases: "hexagonal scaffold", "ports and adapters skeleton", "domain module", "clean architecture template"
- Procedure: collect domain name and use cases → generate inbound ports (interfaces) → generate outbound ports → scaffold domain service → create adapter stubs → generate test harness

**`generate-adr`**
- Description trigger phrases: "architecture decision", "ADR", "document decision", "record architectural choice"
- Procedure: collect context, decision drivers, options considered → evaluate trade-offs → write structured ADR in MADR format → link to affected cells or modules

**`cell-health-check`**
- Description trigger phrases: "cell health", "blast radius check", "cell status", "SRE runbook"
- Procedure: identify cell boundaries → check cross-cell dependency leakage → validate routing layer isolation → generate health report → suggest remediation

**`brownfield-extract-cell`**
- Description trigger phrases: "extract cell", "extract bounded context", "decompose monolith", "strangler fig"
- Procedure: map existing coupling graph → identify seam points → propose extraction sequence → generate migration plan → scaffold target cell structure

**`greenfield-cell-setup`**
- Description trigger phrases: "new cell", "bootstrap cell", "create cell", "provision cell"
- Procedure: collect cell name, owning team, partitioning key → generate cell directory structure → create CLAUDE.md / copilot-instructions.md scoped to cell → generate health contract → scaffold CI/CD pipeline stub

**`port-adapter-review`**
- Description trigger phrases: "review adapter", "port contract", "adapter correctness", "check port implementation"
- Procedure: read port interface → read adapter implementation → validate method signatures → check error handling → verify no domain leakage into adapter → produce review report

#### 3.4 Instruction Files

Specify the following path-specific instruction files. For each provide filename,
`applyTo` glob, and the full list of rules.

| File | `applyTo` Glob | Purpose |
|------|---------------|---------|
| `domain.instructions.md` | `**/*Domain.{ts,java,py}` | Domain model purity rules — no framework imports, no infrastructure types |
| `adapter.instructions.md` | `**/*Adapter.{ts,java,py}` | Adapter implementation standards — must implement exactly one port |
| `cell-infra.instructions.md` | `**/*.cell.{yml,yaml,tf}` | Cell infrastructure standards — isolation boundaries, health endpoint required |
| `ports.instructions.md` | `**/ports/**/*.{ts,java,py}` | Port interface standards — method naming, error types, no concrete types |
| `AGENTS.md` | N/A (agent-scoped) | Operational procedures for autonomous coding agents in this repository |

Write the full rule set (minimum 5 rules each) for each instruction file.

#### 3.5 Hooks

Specify the following hooks for **Claude Code** (`.claude/settings.json` format)
and describe equivalent automation for **GitHub Copilot**:

| Hook | Event | Purpose | Action on Violation |
|------|-------|---------|-------------------|
| `enforce-domain-purity` | `PostToolUse` (file write) | Block infrastructure imports in domain files | Reject write, output violation message |
| `validate-port-contracts` | `PostToolUse` (file write) | Verify adapter implements exactly one port | Warn with remediation suggestion |
| `block-cross-cell-calls` | `PostToolUse` (file write) | Detect direct cross-cell method calls (not via routing layer) | Reject write, suggest event-based alternative |
| `adapter-security-scan` | `PostToolUse` (file write) | Run lightweight OWASP check on outbound adapters | Flag for `@SecurityAgent` review |
| `adr-on-boundary-change` | `PostToolUse` (file write) | Detect changes to port interfaces | Prompt engineer to invoke `generate-adr` skill |

Provide the complete JSON hook configuration for each.

#### 3.6 Persona-Based Implementation Paths

For each of the three personas below, provide a complete step-by-step workflow
for both Greenfield and Brownfield scenarios. Format each as a numbered checklist
with the relevant agent or skill invocation called out at each step.

**Architect Persona**
- Greenfield: Domain discovery → cell topology design → port definition → agent swarm bootstrap → ADR generation
- Brownfield: Legacy mapping → bounded context identification → strangler fig plan → extraction sequence → ADR for each decision

**Developer Persona**
- Greenfield: Scaffold hexagonal module → implement domain logic → wire adapters → write domain tests (no infrastructure) → hand off to SRE for cell health
- Brownfield: Identify seam → extract port interface → write adapter wrapping legacy code → incrementally move logic to domain → validate purity via hook

**SRE Persona**
- Greenfield: Define cell health contract → instrument blast radius boundaries → generate runbook → set up cell-level alerts → validate deployment isolation
- Brownfield: Map existing failure domains → correlate with cell boundaries → add observability → create cell-level rollback procedures → run `cell-health-check` skill

#### 3.7 Greenfield vs Brownfield Decision Matrix

Create a decision matrix table covering:
- Recommended starting architecture (cell-only, hexagonal-only, or hybrid)
- Primary risk per scenario
- Recommended agent swarm entry point
- Estimated complexity (Low / Medium / High)
- Key success metric

Rows: at least 6 distinct scenarios (greenfield greenfield-regulated, brownfield-monolith, brownfield-distributed, brownfield-regulated, hybrid-migration, cloud-native-migration).

Apply semantic emojis from `.github/instructions/github-emojis.md` throughout the
entire document to mark:
- Architecture decision points
- Risk indicators
- Persona-specific sections
- Greenfield vs brownfield guidance

---

### Task 4 — Create Strategic Leadership Document

Create the file:
`cell-based-architecture/guides/strategic-architecture-manifesto.md`

Include YAML front matter:

```yaml
---
post_title: "The Case for Cell-Based and Hexagonal Architecture with AI Agent Swarms: A Strategic Manifesto"
author1: "Principal Architect"
post_slug: "strategic-architecture-manifesto-cell-hex-agents"
microsoft_alias: ""
featured_image: ""
categories: ["Architecture", "Engineering Strategy", "Leadership"]
tags: ["cell-based", "hexagonal", "agent-swarms", "engineering-strategy", "CTO", "OKRs", "developer-experience"]
ai_note: "Generated with AI assistance using Claude Sonnet 4.6"
summary: >
  A strategic manifesto for architects and technology leaders explaining why the
  convergence of cell-based architecture, hexagonal architecture, and AI agent
  swarms represents a compounding investment in engineering velocity, resilience,
  and organizational scalability.
post_date: "2026-03-12"
---
```

Structure the document with exactly these eight sections:

**1. Executive Summary**
Two paragraphs maximum. State the convergence thesis and the compounding return
mechanism. Write at the level of a CTO who reads 50 strategy documents per month.
Make every word earn its place.

**2. The Problem We Are Solving**
Frame the engineering velocity constraints that large-scale teams face: deployment
coordination overhead, blast radius fear, test environment bottlenecks, and the
cognitive load of onboarding into monolithic systems. Use concrete industry data
points where available.

**3. The Strategic Bet**
Explain why the combination of cell-based isolation + hexagonal domain purity +
AI agent specialization creates compounding returns rather than additive ones.
Use a flywheel diagram (ASCII art) to visualize the reinforcing loop.

**4. The Evidence**
Reference the OKR before/after data from Task 2. Supplement with industry
benchmarks (DORA metrics, SPACE framework). Connect architectural choices to
measurable engineering outcomes.

**5. The 12-Month Implementation Roadmap**
Milestones at 30 days, 90 days, 6 months, and 12 months. For each milestone
specify: deliverable, persona who leads, success metric, and which agent or
skill enables it.

**6. The Investment Case**
Frame the ROI for technology leadership. Cover: reduction in incident cost
(blast radius), reduction in deployment coordination overhead, reduction in
onboarding cost, increase in deployment frequency. Use the OKR data to anchor
the numbers.

**7. Risks and Mitigation**
Identify the top 5 architectural and organizational risks. For each risk include:
- Risk description
- Probability (High / Medium / Low)
- Impact if realized
- Mitigation strategy
- Which agent or hook owns the mitigation

**8. The Call to Action**
What a community of architects should do in the next 30 days. What a CTO should
approve in the next quarter. Write as direct imperatives. End with a single
compelling closing statement.

Apply semantic emojis from `.github/instructions/github-emojis.md` prominently
and purposefully throughout — this document will be presented, not just read.
Write with authority. Write as if the future of your engineering organization
depends on this decision, because it does.

---

### Task 5 — Final Quality Verification

Before completing, verify all of the following:

- [ ] `architecture-analysis-summary.md` enriched with Benefits Comparison section
- [ ] `architecture-analysis-summary.md` enriched with OKR Before/After section
- [ ] `agent-swarm-implementation-guide.md` created with all 6 agent specs (both platforms)
- [ ] `agent-swarm-implementation-guide.md` created with all 7 skill specs (both platforms)
- [ ] `agent-swarm-implementation-guide.md` includes all 5 instruction file specs
- [ ] `agent-swarm-implementation-guide.md` includes all 5 hook specs with JSON
- [ ] `agent-swarm-implementation-guide.md` covers all 3 persona paths (Architect, Developer, SRE)
- [ ] `agent-swarm-implementation-guide.md` covers both Greenfield and Brownfield per persona
- [ ] `agent-swarm-implementation-guide.md` includes Greenfield vs Brownfield decision matrix
- [ ] `strategic-architecture-manifesto.md` created with all 8 sections
- [ ] Semantic emojis applied throughout both new documents
- [ ] All files have complete YAML front matter
- [ ] No existing content removed from `architecture-analysis-summary.md`

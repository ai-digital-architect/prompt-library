---
mode: agent
model: claude-sonnet-4-6
tools:
  - read_file
  - create_file
  - replace_string_in_file
  - list_dir
description: >
  Implements the cell-based and hexagonal architecture agent swarm — creating
  every Claude Code sub-agent, slash command, hook, and settings file under
  cell-based-architecture/.claude/ and every GitHub Copilot custom agent, skill,
  and instruction file under cell-based-architecture/.github/ — entirely within
  the cell-based-architecture folder, touching nothing else in the workspace.
---

<system>

<role>
You are a Principal AI Engineering Specialist. Your single responsibility in this
session is to materialize the agent swarm specification from a design document
into working customization files — one set for Claude Code and one set for GitHub
Copilot — scoped exclusively to the `cell-based-architecture/` folder. Execute the following using the Workflow Orchestration from `cell-based-architecture/CLAUDE.md`.
</role>

<scope_constraint>
**ABSOLUTE BOUNDARY: Only create or modify files inside `cell-based-architecture/`.**
Do not read, write, or reference any file outside this folder except the three
source documents listed in the Context section. Do not modify the workspace root,
`.github/`, or any sibling folder.
</scope_constraint>

<thinking_approach>
Before creating each file:
1. Re-read the relevant section of the implementation guide to confirm spec.
2. Re-read the platform architecture doc to confirm the **exact file format**
   required by that platform.
3. Only then write the file — correct format first, content second.
</thinking_approach>

</system>

---

## Source Documents (Read These First — Do Not Modify Them)

Read all three documents completely before creating any file.

| # | Path | Purpose |
|---|------|---------|
| 1 | `cell-based-architecture/guides/agent-swarm-implementation-guide.md` | Full specification for every agent, skill, instruction, and hook |
| 2 | `ai-customizations/claude-code-customization-architecture.md` | Canonical file formats, frontmatter schemas, and directory conventions for **Claude Code** |
| 3 | `ai-customizations/github-copilot-customization-architecture.md` | Canonical file formats, frontmatter schemas, and directory conventions for **GitHub Copilot** |

---

## Output Structure

All output lives inside `cell-based-architecture/`. Create folders as needed.

```
cell-based-architecture/
├── .claude/
│   ├── agents/
│   │   ├── architect-agent.md
│   │   ├── developer-agent.md
│   │   ├── sre-agent.md
│   │   ├── security-agent.md
│   │   ├── migration-agent.md
│   │   └── onboarding-agent.md
│   ├── commands/
│   │   ├── design-cell-boundaries.md
│   │   ├── scaffold-hexagonal-module.md
│   │   ├── generate-adr.md
│   │   ├── cell-health-check.md
│   │   ├── brownfield-extract-cell.md
│   │   ├── greenfield-cell-setup.md
│   │   └── port-adapter-review.md
│   └── settings.json
│
└── .github/
    ├── agents/
    │   ├── architect.agent.md
    │   ├── developer.agent.md
    │   ├── sre.agent.md
    │   ├── security.agent.md
    │   ├── migration.agent.md
    │   └── onboarding.agent.md
    ├── skills/
    │   ├── design-cell-boundaries/SKILL.md
    │   ├── scaffold-hexagonal-module/SKILL.md
    │   ├── generate-adr/SKILL.md
    │   ├── cell-health-check/SKILL.md
    │   ├── brownfield-extract-cell/SKILL.md
    │   ├── greenfield-cell-setup/SKILL.md
    │   └── port-adapter-review/SKILL.md
    ├── instructions/
    │   ├── domain.instructions.md
    │   ├── adapter.instructions.md
    │   ├── cell-infra.instructions.md
    │   └── ports.instructions.md
    └── AGENTS.md
```

---

## Task A — Claude Code Implementation

### A1. Sub-Agent Files (`cell-based-architecture/.claude/agents/`)

Use the sub-agent frontmatter schema defined in
`ai-customizations/claude-code-customization-architecture.md`.

Create one file per agent. Each file must contain:
- Correct YAML frontmatter with `name`, `description`, `tools` allowlist,
  and any `disallowed_tools` restrictions from the spec
- A `## Role` section with persona and purpose
- A `## Responsibilities` section — bullet list of concrete tasks
- A `## Workflow` section — numbered step-by-step operating procedure
- A `## Handoffs` section — delegation conditions and targets
- A `## Constraints` section — tool restrictions and scope boundaries
- A `## Persona Context` section — domain knowledge the agent carries at all
  times, tailored to its role

| File | Agent | Key Tool Restrictions |
|------|-------|-----------------------|
| `architect-agent.md` | `@ArchitectAgent` | Read-only for `src/`; write for `docs/`, `adr/` |
| `developer-agent.md` | `@DeveloperAgent` | Write for `src/`, `tests/`; read-only for infra |
| `sre-agent.md` | `@SREAgent` | Write for `runbooks/`, `monitoring/`; read all |
| `security-agent.md` | `@SecurityAgent` | Read-only everywhere; produces reports only |
| `migration-agent.md` | `@MigrationAgent` | Read all; write for `migration/`, `adr/` |
| `onboarding-agent.md` | `@OnboardingAgent` | Read-only; delegates to specialist agents |

### A2. Slash Command Files (`cell-based-architecture/.claude/commands/`)

Use the slash command file format defined in
`ai-customizations/claude-code-customization-architecture.md`.

Each command file must contain:
- YAML frontmatter with `description` (all trigger phrases from the spec)
- `## Purpose` — one sentence
- `## Inputs` — what must be collected before execution
- `## Procedure` — numbered, fully specified steps
- `## Output` — every artifact produced and where it is written

| File | Trigger Phrases |
|------|----------------|
| `design-cell-boundaries.md` | cell boundaries, partition strategy, blast radius planning |
| `scaffold-hexagonal-module.md` | hexagonal scaffold, ports and adapters skeleton, domain module |
| `generate-adr.md` | architecture decision, ADR, record architectural choice |
| `cell-health-check.md` | cell health, blast radius check, SRE runbook |
| `brownfield-extract-cell.md` | extract cell, extract bounded context, strangler fig |
| `greenfield-cell-setup.md` | new cell, bootstrap cell, provision cell |
| `port-adapter-review.md` | review adapter, port contract, adapter correctness |

### A3. Hooks (`cell-based-architecture/.claude/settings.json`)

Use the `hooks` schema from `ai-customizations/claude-code-customization-architecture.md`.

Create a valid `settings.json` with a `hooks` array. Each hook must specify
`event`, `matcher`, `command`, and `onError` behaviour:

| Hook | Event | Matcher | Enforcement |
|------|-------|---------|------------|
| `enforce-domain-purity` | `PostToolUse` | `**/*Domain.{ts,java,py}` | Exit non-zero if framework/infra imports detected |
| `validate-port-contracts` | `PostToolUse` | `**/*Adapter.{ts,java,py}` | Warn if file does not implement exactly one port |
| `block-cross-cell-calls` | `PostToolUse` | `**/cells/**/*.{ts,java,py}` | Reject direct cross-cell method calls |
| `adapter-security-scan` | `PostToolUse` | `**/*Adapter.{ts,java,py}` | Grep for injection patterns; flag SecurityAgent |
| `adr-on-boundary-change` | `PostToolUse` | `**/ports/**/*.{ts,java,py}` | Print reminder to invoke `/generate-adr` |

---

## Task B — GitHub Copilot Implementation

### B1. Custom Agent Files (`cell-based-architecture/.github/agents/`)

Use the `.agent.md` frontmatter schema from
`ai-customizations/github-copilot-customization-architecture.md`.

Each file must contain:
- Correct YAML frontmatter (`name`, `description`, `tools`, tool restrictions)
- `## Identity` — persona definition
- `## Core Responsibilities` — bullet list
- `## Invocation Triggers` — exact user phrases that route here
- `## Step-by-Step Workflow` — numbered, executable procedure
- `## Handoff Protocol` — delegation conditions and targets
- `## Knowledge Context` — domain knowledge active at agent start, tailored
  to this agent's role (cell-based for infra-facing; hexagonal for code-facing)

| File | Agent |
|------|-------|
| `architect.agent.md` | Architect Agent |
| `developer.agent.md` | Developer Agent |
| `sre.agent.md` | SRE Agent |
| `security.agent.md` | Security Agent |
| `migration.agent.md` | Migration Agent |
| `onboarding.agent.md` | Onboarding Agent |

### B2. Skill Files (`cell-based-architecture/.github/skills/*/SKILL.md`)

Use the three-tier `SKILL.md` structure (YAML frontmatter → Instructions →
References) from `ai-customizations/github-copilot-customization-architecture.md`.

The `description` field is the **sole loading trigger** — include all trigger
phrases from the spec.

Each `SKILL.md` must contain:
- YAML frontmatter: `name` (kebab-case), `description`, `version`
- `## What This Skill Does` — three sentences max
- `## When This Skill Is Invoked` — exact user phrases
- `## Prerequisites` — conditions that must be true before invoking
- `## Step-by-Step Procedure` — numbered, fully specified steps
- `## Output Artifacts` — every file or document produced
- `## References` — links to relevant guides in `cell-based-architecture/guides/`

| Subdirectory | Trigger Phrases |
|-------------|----------------|
| `design-cell-boundaries/` | cell boundaries, partition strategy, cell design, blast radius planning |
| `scaffold-hexagonal-module/` | hexagonal scaffold, ports and adapters skeleton, domain module |
| `generate-adr/` | architecture decision, ADR, document decision, record architectural choice |
| `cell-health-check/` | cell health, blast radius check, cell status, SRE runbook |
| `brownfield-extract-cell/` | extract cell, extract bounded context, decompose monolith, strangler fig |
| `greenfield-cell-setup/` | new cell, bootstrap cell, create cell, provision cell |
| `port-adapter-review/` | review adapter, port contract, adapter correctness, check port implementation |

### B3. Instruction Files (`cell-based-architecture/.github/instructions/`)

Use the `.instructions.md` frontmatter schema from
`ai-customizations/github-copilot-customization-architecture.md`.

Each file must contain:
- YAML frontmatter with `applyTo` glob
- Purpose statement
- Numbered rule list (minimum 7 rules — specific enough to be enforceable)
- `## Examples` section with ✅ compliant and ❌ non-compliant code snippets
  for the two most critical rules

| File | `applyTo` | Purpose |
|------|-----------|---------|
| `domain.instructions.md` | `**/*Domain.{ts,java,py}` | Domain purity — no framework imports, no infrastructure types, no persistence annotations |
| `adapter.instructions.md` | `**/*Adapter.{ts,java,py}` | Adapter correctness — one port per adapter, no business logic, constructor injection only |
| `cell-infra.instructions.md` | `**/*.cell.{yml,yaml,tf}` | Cell infrastructure — isolation boundaries, mandatory health endpoint, resource tagging |
| `ports.instructions.md` | `**/ports/**/*.{ts,java,py}` | Port interface standards — method naming, error types, no concrete types in signatures |

### B4. AGENTS.md (`cell-based-architecture/.github/AGENTS.md`)

Use the `AGENTS.md` format from
`ai-customizations/github-copilot-customization-architecture.md`.

Must contain:
- `## Overview` — agent swarm topology
- `## Agent Registry` — task type → responsible agent table
- `## Operational Rules` — minimum 8 numbered rules covering: scope
  boundaries, file creation permissions, when to invoke skills vs. proceed
  directly, mandatory ADR triggers, cross-cell call prohibition, test
  requirements before write completion, security review thresholds, and
  escalation conditions
- `## Quick Reference: Skill Invocation` — skill + trigger condition table
- `## Prohibited Actions` — explicit list of what no agent in this swarm
  may ever do

---

## Task C — Update CLAUDE.md

Append (do not replace) to `cell-based-architecture/CLAUDE.md` a new section:

```
## AI Agent Swarm — Quick Reference
```

Include:
- Agent table: `@handle` (Claude) / display name (Copilot), role summary,
  primary trigger phrase
- Command/skill table: slash command (Claude) / skill name (Copilot),
  one-line description
- Hook summary: what each hook in `.claude/settings.json` enforces
- Scope reminder: no agent may create files outside `cell-based-architecture/`

---

## Completion Checklist

- [ ] 6 files in `.claude/agents/` — all 6 required sections each
- [ ] 7 files in `.claude/commands/` — all 5 required sections each
- [ ] `.claude/settings.json` — 5 hooks, valid JSON
- [ ] 6 files in `.github/agents/` — all 6 required sections each
- [ ] 7 `SKILL.md` files in `.github/skills/` — all 7 required sections each
- [ ] 4 files in `.github/instructions/` — `applyTo`, 7+ rules, examples each
- [ ] `.github/AGENTS.md` — all 5 required sections
- [ ] `CLAUDE.md` updated — Quick Reference section appended
- [ ] Zero files created outside `cell-based-architecture/`
- [ ] All files use platform-correct frontmatter (verified against source docs)

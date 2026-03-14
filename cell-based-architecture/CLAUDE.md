## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One tack per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimat Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

---

## AI Agent Swarm — Quick Reference

### Agent Registry

| Claude Handle | Copilot Name | Role Summary | Primary Trigger |
|---------------|-------------|--------------|-----------------|
| `architect-agent` | `@ArchitectAgent` | Cell boundary design, port contracts, ADRs | "cell boundaries", "ADR", "hexagonal port" |
| `developer-agent` | `@DeveloperAgent` | Hexagonal scaffolding, domain implementation, adapters | "scaffold hexagonal module", "implement use case" |
| `sre-agent` | `@SREAgent` | Cell health contracts, blast radius validation, runbooks | "cell health", "SRE runbook", "blast radius check" |
| `security-agent` | `@SecurityAgent` | Read-only adapter security review, OWASP analysis | "security review", "injection analysis", "OWASP" |
| `migration-agent` | `@MigrationAgent` | Brownfield decomposition, strangler fig planning | "extract cell", "strangler fig", "decompose monolith" |
| `onboarding-agent` | `@OnboardingAgent` | Read-only new-developer orientation | "how do I", "where does X go", "I am new here" |

### Command and Skill Reference

| Slash Command (Claude) | Skill Name (Copilot) | Description |
|------------------------|---------------------|-------------|
| `/project:design-cell-boundaries` | `design-cell-boundaries` | Guide cell boundary design from requirements to ADR |
| `/project:scaffold-hexagonal-module` | `scaffold-hexagonal-module` | Generate complete hexagonal module with ports, adapters, tests |
| `/project:generate-adr` | `generate-adr` | Produce MADR-format Architecture Decision Record |
| `/project:cell-health-check` | `cell-health-check` | Audit cell against health contract; produce report |
| `/project:brownfield-extract-cell` | `brownfield-extract-cell` | Coupling graph analysis and phased extraction plan |
| `/project:greenfield-cell-setup` | `greenfield-cell-setup` | Scaffold new cell directory, health contract, CI/CD stub |
| `/project:port-adapter-review` | `port-adapter-review` | Systematic adapter review against port contract |

### Hook Enforcement Summary (`.claude/settings.json`)

| Hook Name | Trigger | Files Matched | Action on Violation |
|-----------|---------|--------------|---------------------|
| `enforce-domain-purity` | PostToolUse (Write/Edit) | `**/*Domain.{ts,java,py}`, `**/domain/**` | Exit 2 (block) — infrastructure import in domain file |
| `validate-port-contracts` | PostToolUse (Write/Edit) | `**/*Adapter.{ts,java,py}` | Exit 1 (warn) — adapter implements more than one port |
| `block-cross-cell-calls` | PostToolUse (Write/Edit) | `**/*.{ts,java,py}` (excl. routing/) | Exit 2 (block) — direct cross-cell method call detected |
| `adapter-security-scan` | PostToolUse (Write/Edit) | `**/*Adapter.{ts,java,py}` | Exit 2 (CRITICAL) or Exit 1 (HIGH) — hardcoded credentials or dynamic code execution |
| `adr-on-boundary-change` | PostToolUse (Write/Edit) | `**/ports/**/*.{ts,java,py}` | Exit 0 with reminder — print ADR requirement for port interface changes |

### Scope Reminder

**ABSOLUTE RULE**: No agent in this swarm may create, modify, or delete files outside `cell-based-architecture/`. This applies equally to Claude Code sub-agents (`.claude/agents/`) and GitHub Copilot custom agents (`.github/agents/`). The blast radius of this swarm is bounded to this directory.
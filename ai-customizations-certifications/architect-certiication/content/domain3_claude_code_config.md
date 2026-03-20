# Domain 3: Claude Code Configuration & Workflows
**Weight: 20% of scored content**

---

## Overview

This domain tests your ability to configure Claude Code for team and enterprise environments — setting up CLAUDE.md hierarchies, creating custom commands and skills, writing path-specific rules, choosing between plan mode and direct execution, and integrating Claude Code into CI/CD pipelines. Many questions hinge on knowing *which configuration file to use* and *why*.

**Source coverage:** The exam guide source list is well-matched to this domain. Key sources: *Claude Code Overview*, *Claude Code Settings*, *Advanced Setup*, *CLI Reference*, and *Enterprise Deployment*.

---

## 3.1 CLAUDE.md Configuration Hierarchy

### The Three Levels

| Level | Location | Scope | Shared via Git? |
|---|---|---|---|
| **User** | `~/.claude/CLAUDE.md` | Applies to this user across all projects | ❌ No |
| **Project** | `CLAUDE.md` or `.claude/CLAUDE.md` at repo root | All team members on this project | ✅ Yes |
| **Directory** | `subdirectory/CLAUDE.md` | Files in that subdirectory and below | ✅ Yes |

### Loading Behavior

Claude Code reads CLAUDE.md files **recursively** starting from the current working directory up toward the root. When editing a file in `packages/frontend/`, all of these load automatically:
- `~/.claude/CLAUDE.md` (user-level)
- `CLAUDE.md` (project root)
- `packages/CLAUDE.md` (if exists)
- `packages/frontend/CLAUDE.md` (if exists)

**Critical exam point:** Instructions placed in `~/.claude/CLAUDE.md` are **not shared with teammates** via version control. If a new team member isn't receiving certain instructions, the most likely cause is that those instructions were placed in user-level config instead of project-level config.

### @import Syntax for Modular Organization

Use `@import` to keep CLAUDE.md files focused while referencing shared standards:

```markdown
# CLAUDE.md — packages/payments/

This package handles all payment processing.

@import ../../docs/standards/api-conventions.md
@import ../../docs/standards/error-handling.md
@import ../../docs/standards/security-requirements.md
```

This keeps each package's CLAUDE.md small and ensures standards updates propagate automatically.

### .claude/rules/ Directory

For large projects, split instructions into focused topic-specific files:

```
.claude/
└── rules/
    ├── testing.md          ← Testing conventions
    ├── api-conventions.md  ← API design standards
    ├── security.md         ← Security requirements
    └── deployment.md       ← Deployment procedures
```

All `.md` files in `.claude/rules/` are discovered and loaded automatically. This is the preferred alternative to a monolithic CLAUDE.md.

### Verifying Configuration

Use the `/memory` command to verify which memory files are loaded and diagnose inconsistent behavior across sessions.

---

## 3.2 Custom Slash Commands and Skills

### Commands vs. Skills: The Distinction

| Feature | Slash Commands | Skills |
|---|---|---|
| Location | `.claude/commands/` | `.claude/skills/<name>/SKILL.md` |
| Invocation | Always manual (`/command-name`) | Manual **or** automatic (Claude decides when relevant) |
| Supporting files | No | Yes — templates, scripts, examples |
| Frontmatter options | Basic | Full: `context`, `allowed-tools`, `argument-hint` |

### When to Choose Commands vs. CLAUDE.md

| Use | Mechanism |
|---|---|
| Standards that apply to **every interaction** | CLAUDE.md (always-loaded) |
| Workflows invoked **on demand** | Skills or slash commands |
| Team-shared workflows | `.claude/commands/` or `.claude/skills/` (version controlled) |
| Personal workflows (not for team) | `~/.claude/commands/` or `~/.claude/skills/` |

### Creating a Project-Scoped Command

```bash
# This command is available to ALL team members after clone/pull
mkdir -p .claude/commands/

cat > .claude/commands/review.md << 'EOF'
Review this code change for:
1. Security vulnerabilities
2. Performance regressions
3. Missing error handling
4. Violations of our API conventions (see @docs/standards/api-conventions.md)

Report findings with: file, line number, severity (critical/high/medium), and suggested fix.
EOF
```

### SKILL.md Frontmatter Options

```yaml
---
name: analyze-codebase
description: "Performs deep structural analysis of a codebase. Use when onboarding to a new project or investigating architectural issues."
context: fork           # Run in isolated sub-agent — output stays separate from main session
allowed-tools:          # Restrict tool access during skill execution
  - Read
  - Glob
  - Grep
  - Bash(find:*)        # Allow only find commands, not arbitrary bash
argument-hint: "Enter the directory path to analyze (default: current directory)"
---

When analyzing a codebase, follow these steps:
1. Map the top-level directory structure
2. Identify key entry points and main modules
3. Trace the three most important data flows
4. Document findings in a structured report
```

### `context: fork` — Isolation Pattern

The `context: fork` option runs the skill in an isolated sub-agent context. This prevents verbose or exploratory output from polluting the main conversation.

**Use `context: fork` when the skill:**
- Produces verbose discovery output (codebase analysis, dependency mapping)
- Explores multiple approaches (brainstorming alternatives)
- Should not influence the main session's direction

**Keep in the main session when the skill:**
- Needs to take direct action (writing files, running tests)
- Should build on existing conversation context

### `allowed-tools` Frontmatter

Restrict which tools a skill can access during execution:

```yaml
allowed-tools:
  - Read          # Allow reads
  - Write         # Allow file writes
  - Bash(git *:*) # Allow only git commands
  # Note: Bash without restrictions would allow arbitrary shell execution
```

This prevents a "document generation" skill from accidentally deleting files.

### Personal Skill Customization

To customize a skill for personal use without affecting teammates:

```bash
# Create a personal variant with a different name
mkdir -p ~/.claude/skills/my-review/
cat > ~/.claude/skills/my-review/SKILL.md << 'EOF'
---
name: my-review
description: My personal code review workflow with custom criteria
---
[Personal customized review instructions]
EOF
```

---

## 3.3 Path-Specific Rules for Conditional Convention Loading

### The Problem Path-Specific Rules Solve

Test files are spread throughout a codebase (e.g., `Button.test.tsx` next to `Button.tsx`). A directory-level CLAUDE.md can only apply to one directory — it can't easily cover test files in dozens of locations.

Path-specific rules with glob patterns solve this elegantly.

### Creating a Path-Specific Rule File

```yaml
# .claude/rules/testing.md
---
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
  - "**/*.spec.ts"
---

# Testing Conventions

All test files must follow these standards:

- Use `describe` blocks to group related tests
- Use `it` (not `test`) for individual test cases
- Mock external dependencies with `jest.mock()`
- Include tests for: happy path, error cases, edge cases, null/undefined inputs
- Do not use `any` type in test files
- Fixtures go in `__fixtures__/` subdirectory
```

```yaml
# .claude/rules/terraform.md
---
paths:
  - "terraform/**/*"
  - "infra/**/*.tf"
---

# Terraform Conventions

- Always specify `required_version` in `terraform` block
- Use `for_each` over `count` for resource creation
- Tag all resources with: Environment, Team, ManagedBy
- Variables without defaults must have descriptions
```

### Key Advantages of Path Rules Over Subdirectory CLAUDE.md

| Aspect | Path-Specific Rules | Directory CLAUDE.md |
|---|---|---|
| Applies to files across multiple directories | ✅ Yes (glob patterns) | ❌ No (directory-bound) |
| Applies to test files scattered throughout codebase | ✅ Yes | ❌ No |
| Reduces irrelevant context/token usage | ✅ Only loads for matching files | ⚠️ Always loads when in directory |
| Best for file-type conventions (e.g., all `.test.tsx`) | ✅ Yes | ❌ No |

**Exam decision rule:** Choose `.claude/rules/` with glob patterns over directory-level CLAUDE.md whenever conventions must apply to files scattered across multiple directories.

---

## 3.4 Plan Mode vs. Direct Execution

### Decision Framework

| Factor | Use Plan Mode | Use Direct Execution |
|---|---|---|
| **Scope** | Many files (10+), multiple modules | Single file or function |
| **Complexity** | Architectural decisions required | Clear, well-understood change |
| **Reversibility** | Costly to undo; risk of rework | Easy to undo; contained |
| **Approaches** | Multiple valid implementation strategies | Single obvious approach |
| **Known dependencies** | Unknown — need exploration first | Known — clear stack trace or spec |

### Plan Mode: Use Cases

```
✅ Microservice restructuring (affects dozens of files)
✅ Library migration affecting 45+ files
✅ Monolith-to-microservices decomposition
✅ Choosing between integration approaches with different infrastructure requirements
✅ Adding a new feature to an unfamiliar codebase
```

### Direct Execution: Use Cases

```
✅ Single-file bug fix with a clear stack trace
✅ Adding a date validation conditional to one function
✅ Renaming a variable consistently within one file
✅ Updating a configuration value
```

### Why Plan Mode Prevents Costly Rework

Plan mode allows Claude to **explore the codebase and design an approach before making any changes**. This is critical when:

- The full scope of change is unknown upfront
- Wrong initial choices propagate through many files
- Multiple valid approaches exist with different tradeoffs

**Exam trap:** "Start with direct execution and switch to plan mode if complexity emerges" — this is wrong when complexity is already stated in the requirements. Plan mode should be chosen proactively, not reactively.

### The Explore Subagent

For verbose discovery phases (mapping a codebase, analyzing all dependencies), use the **Explore subagent**:

```
Main session: Plan the migration approach
  └── Explore subagent: Maps all 120 modules and their dependencies
         ↓ Returns: structured summary of modules and dependency graph
  Main session: Uses summary to design approach (no verbose output in main context)
```

This prevents context window exhaustion during multi-phase tasks.

### Combining Both Modes

For large tasks: use **plan mode** to explore and design, then switch to **direct execution** to implement the planned approach. This gives you the best of both — thorough design upfront, efficient implementation after.

---

## 3.5 Iterative Refinement Techniques

### Concrete Input/Output Examples

When natural language descriptions produce inconsistent results, provide concrete input/output pairs:

```markdown
Transform these date formats to ISO 8601:

Input:  "March 15, 2024"      → Output: "2024-03-15"
Input:  "15/03/24"            → Output: "2024-03-15"
Input:  "3-15-2024"           → Output: "2024-03-15"
Input:  null or empty string  → Output: null (do not fabricate a date)
```

2–3 examples are more effective than lengthy prose descriptions.

### Test-Driven Iteration

1. Write a comprehensive test suite first (happy path, error cases, edge cases, performance)
2. Share the test failures on each iteration — they become the precise specification
3. Each iteration targets specific failing tests

### The Interview Pattern

Before implementing in an unfamiliar domain, have Claude ask clarifying questions:

```
"Before implementing this cache layer, ask me questions about:
- Cache invalidation strategy
- Expected failure modes
- Consistency requirements
- Maximum cache size and eviction policy"
```

This surfaces design considerations the developer may not have anticipated — particularly valuable for infrastructure, security, and distributed systems work.

### Sequential vs. Parallel Issue Resolution

| Situation | Approach |
|---|---|
| Issues **interact** (fix A may break B) | Provide all issues in a single detailed message |
| Issues are **independent** (different modules, different concerns) | Fix sequentially, one at a time |

---

## 3.6 Integrating Claude Code into CI/CD Pipelines

### The `-p` Flag for Non-Interactive Mode

The `-p` (or `--print`) flag runs Claude Code non-interactively — processes the prompt, prints output to stdout, and exits without waiting for user input.

```bash
# ❌ WRONG — Hangs indefinitely waiting for interactive input
claude "Review this PR for security issues"

# ✅ CORRECT — Runs non-interactively, exits when complete
claude -p "Review this PR for security issues"
```

### Structured Output for Machine Parsing

```bash
# Produce machine-parseable JSON for automated PR comment posting
claude -p "Review this PR for security issues" \
       --output-format json \
       --json-schema ./schemas/review_finding.json
```

The JSON output can be parsed by downstream scripts and posted as inline PR comments.

### CI/CD Integration Patterns

```yaml
# GitHub Actions example
- name: Claude Code Review
  run: |
    claude -p "Review the changes in this PR for:
    1. Security vulnerabilities (CRITICAL)
    2. Breaking API changes (HIGH)
    3. Missing error handling (MEDIUM)
    
    Report findings in the format defined in CLAUDE.md.
    If prior review findings are provided, report ONLY new or still-unaddressed issues." \
    --output-format json > review_findings.json
    
    python scripts/post_pr_comments.py review_findings.json
```

### Session Isolation for Independent Review

A Claude session that **generated** the code has retained reasoning context that makes it less likely to question its own decisions. For more effective reviews:

```bash
# ❌ SUBOPTIMAL — Same session that wrote the code reviews it
claude -p "Now review the code you just wrote for security issues"

# ✅ BETTER — Fresh independent review instance (no prior reasoning context)
claude -p "Review the following code for security issues: [code]"
# This is a separate invocation with no knowledge of how the code was written
```

### Avoiding Duplicate Review Comments

When re-running after new commits, include prior findings in context:

```bash
claude -p "Review this PR.
Prior review findings (from the previous commit): $(cat prior_findings.json)
Report ONLY new findings or issues that remain unaddressed.
Do NOT re-report issues already captured in prior findings."
```

### CLAUDE.md for CI Context

CLAUDE.md is the primary mechanism for providing project context to CI-invoked Claude Code. Document:
- Testing standards and available fixtures
- Review criteria (what to flag, what to skip)
- Severity classification definitions
- Output format expectations

```markdown
# CLAUDE.md — CI Review Standards

## Code Review Criteria
Report:
- Security vulnerabilities (injection, auth bypass, data exposure)
- Null pointer dereferences and unhandled exceptions
- Breaking changes to public API contracts

Do NOT report:
- Minor style inconsistencies (handled by linter)
- Personal preference formatting choices
- Code patterns established in this project's existing codebase

## Severity Definitions
CRITICAL: Exploitable security vulnerability or data loss risk
HIGH: Runtime crash possible in production conditions
MEDIUM: Incorrect behavior in edge cases
LOW: Maintainability concern only
```

---

## Exam Practice Questions

**Q1:** A new developer cloned the repo but isn't receiving the team's custom Claude instructions. Where were the instructions most likely placed?
> In `~/.claude/CLAUDE.md` (user-level) instead of the project-level `CLAUDE.md` or `.claude/CLAUDE.md`. User-level config is not shared via version control.

**Q2:** You want all test files (`*.test.tsx`) across the entire codebase to follow the same conventions. What's the most maintainable approach?
> **A** — Create `.claude/rules/` files with YAML frontmatter glob patterns (`**/*.test.tsx`). Directory-level CLAUDE.md files can't handle files scattered across many directories.

**Q3:** Your team wants a `/review` slash command available to every developer after `git pull`. Where should it be created?
> In `.claude/commands/` within the project repository. This is version-controlled and automatically available to all developers.

**Q4:** Your CI pipeline hangs indefinitely when running Claude Code. What's the fix?
> Add the `-p` (or `--print`) flag: `claude -p "your prompt"`. This runs non-interactively.

**Q5:** Should you use plan mode or direct execution for a monolith-to-microservices restructuring?
> **Plan mode** — complex task involving large-scale changes, multiple valid approaches, architectural decisions, and multi-file modifications.

---

## Key Terms Checklist

- [ ] CLAUDE.md hierarchy: user (`~/.claude/CLAUDE.md`) / project / directory
- [ ] User-level config is NOT shared via version control
- [ ] `@import` syntax for modular CLAUDE.md organization
- [ ] `.claude/rules/` for topic-specific rule files
- [ ] `/memory` command — verify which memory files are loaded
- [ ] `.claude/commands/` — project-scoped slash commands (shared)
- [ ] `~/.claude/commands/` — user-scoped commands (personal)
- [ ] `.claude/skills/<name>/SKILL.md` — skill definition
- [ ] `context: fork` — isolated sub-agent execution
- [ ] `allowed-tools` frontmatter — restrict tool access in skills
- [ ] `argument-hint` frontmatter — prompt for required parameters
- [ ] Path-specific rules with glob patterns in `.claude/rules/`
- [ ] Plan mode — complex, multi-file, architectural tasks
- [ ] Direct execution — simple, scoped, well-understood changes
- [ ] Explore subagent — verbose discovery without polluting main context
- [ ] `-p` / `--print` flag — non-interactive CI/CD mode
- [ ] `--output-format json` + `--json-schema` — structured CI output
- [ ] Session isolation for independent code review

---

## Recommended Sources

| Source | Focus |
|---|---|
| [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview) | Core concepts; CLAUDE.md basics |
| [Claude Code Settings](https://docs.anthropic.com/en/docs/claude-code/settings) | Configuration hierarchy; hooks; permissions |
| [Advanced Setup](https://docs.anthropic.com/en/docs/claude-code/advanced-setup) | MCP integration; enterprise config |
| [CLI Reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference) | `-p` flag; `--output-format`; `--resume` |
| [Create Custom Subagents](https://docs.anthropic.com/en/docs/claude-code/subagents) | Skills; context:fork; Explore subagent |
| [Enterprise Deployment](https://docs.anthropic.com/en/docs/claude-code/enterprise-deployment) | MDM deployment; managed settings |
| Exam Guide — Task Statements 3.1–3.6 (Pages 12–16) | Authoritative task definitions |

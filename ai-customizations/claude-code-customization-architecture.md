# Claude Code Customization Architecture
## Memory · Sub-agents · Hooks · MCP · Slash Commands · Skills · AGENTS.md
### Best Practices for Engineers ｜ Principal Engineer Perspective
#### March 2026

---

## Table of Contents

1. [Architecture Overview — Six Core Components and Their Relationships](#chapter-1-architecture-overview)
2. [Memory System — File Types, Layered Model, and AGENTS.md](#chapter-2-memory-system)
3. [Sub-agents — Role Design, Isolation, and Orchestration](#chapter-3-sub-agents)
4. [Hooks — Security Interception and Automation](#chapter-4-hooks)
5. [MCP Servers — Extending Claude Code with External Tools](#chapter-5-mcp-servers)
6. [Slash Commands — User-Triggered Reusable Workflows](#chapter-6-slash-commands)
7. [Skills — Reusable, Invocable Workflows](#chapter-7-skills)
8. [Where Does the Workflow Belong? — Common Anti-Patterns and Correct Placement](#chapter-8-where-does-the-workflow-belong)
9. [Complete Project Structure Example](#chapter-9-complete-project-structure-example)
10. [Token Cost Strategy](#chapter-10-token-cost-strategy)
11. [Security Best Practices](#chapter-11-security-best-practices)
12. [Appendix A — Settings Reference and Permission Model](#appendix-a-settings-reference)
13. [Appendix B — Claude Code vs GitHub Copilot Customization Comparison](#appendix-b-comparison)

---

## Chapter 1: Architecture Overview

Claude Code's customization system is built around six core components. Each serves a distinct purpose within a layered, cooperative architecture. Unlike IDE-based tools, Claude Code operates primarily from the terminal and emphasizes a **file-first, code-native** design philosophy — every customization artifact is a plain text file tracked in version control.

| Component | Analogy | Loading Behavior | Scope | Configuration Location |
|-----------|---------|-----------------|-------|------------------------|
| **Memory Files** | Employee handbook / project wiki | Always-on or directory-scoped | Conventions, stack preferences, project context | `CLAUDE.md`, `AGENTS.md`, `~/.claude/CLAUDE.md` |
| **Sub-agents** | Specialized teammates with defined roles | On-demand (invoked by parent agent or user) | Isolated task execution with distinct personas and tool sets | `~/.claude/agents/*.md` or `.claude/agents/*.md` |
| **Hooks** | Security checkpoints / automation triggers | Lifecycle event triggers | Permission checks, linting, logging, notifications | `.claude/settings.json` → `hooks` key |
| **MCP Servers** | External tool integrations | Session startup | File system, APIs, databases, custom tooling | `.claude/settings.json` → `mcpServers` key |
| **Slash Commands** | Reusable prompt macros (legacy) | User-invoked via `/project:<name>` | Task-specific, user-triggered workflows | `.claude/commands/*.md` |
| **Skills** | Reusable invocable workflows (preferred) | User-invoked or Claude auto-invoked | On-demand workflows; invocable by agents programmatically | `.claude/skills/<name>/SKILL.md` |

> **Architectural Principle:** The memory layer (CLAUDE.md / AGENTS.md) establishes *"who you are and what you know"*; the role layer (Sub-agents) defines *"who does specialized work"*; the safety layer (Hooks) ensures *"it's done safely"*; the tool layer (MCP) decides *"what external capabilities are available"*; and the workflow layer (Skills / Slash Commands) provides *"repeatable task shortcuts"* — with Skills being the modern, preferred mechanism.

---

## Chapter 2: Memory System

Claude Code supports four distinct memory file types, each with different scopes and loading behaviors. This chapter also covers `AGENTS.md` — an open, cross-platform standard that complements `CLAUDE.md` for broader agent compatibility. Understanding the hierarchy is essential for avoiding contradictions and context bloat.

### 2.1 Four Memory File Types

| Type | File Location | Loading Behavior | Scope | Purpose |
|------|--------------|-----------------|-------|---------|
| **Project Memory** | `CLAUDE.md` (repo root) | Always-on when operating in the directory | Entire project | Coding standards, architecture decisions, build commands, shared team conventions |
| **User Memory** | `~/.claude/CLAUDE.md` | Always-on (globally, across all projects) | All projects for this user | Personal preferences, shortcuts, editor habits |
| **Local Project Memory** | `.claude/CLAUDE.md` | Always-on for this project; **not committed** | Local machine only | Machine-specific overrides, secrets references, local path configs |
| **Sub-directory Memory** | `src/CLAUDE.md`, `tests/CLAUDE.md`, etc. | Loaded when Claude operates within that directory | Sub-tree scope | Module-specific rules, subsystem conventions |

### 2.2 Precedence and Composition Rules

When multiple CLAUDE.md files are in scope, Claude Code **merges them all into the context**. Precedence from highest to lowest:

```
Layer 0: ~/.claude/CLAUDE.md (User Memory)             ← Highest precedence; personal prefs
Layer 1: CLAUDE.md (Project Root)                       ← Shared team standards
Layer 2: .claude/CLAUDE.md (Local Project Memory)       ← Machine-local overrides
Layer 3: <subdirectory>/CLAUDE.md (Sub-directory)       ← Module-specific rules
Layer 4: Sub-agent frontmatter prompt                   ← Active sub-agent persona
```

All in-scope files are provided to Claude simultaneously. **Avoid contradictions between layers.** If a sub-directory rule conflicts with the root, the sub-directory wins for files within that tree.

### 2.3 Project CLAUDE.md Best Practices

The project `CLAUDE.md` is the most important customization artifact. It is loaded on every invocation within the project directory.

- ✅ Keep it focused: **5–20 rules** covering the most common interactions (target 200–800 tokens)
- ✅ Include build/test/lint commands so Claude never guesses them
- ✅ Document the tech stack, key architectural decisions, and folder conventions
- ✅ List antipatterns the team has explicitly rejected (and why)
- ❌ **Do not embed lengthy workflow orchestration logic** (see Chapter 7)
- ❌ Do not include content that applies to only one module (put that in a sub-directory `CLAUDE.md`)
- ❌ Do not include secrets, API keys, or machine-local paths (use `.claude/CLAUDE.md` for those, and add it to `.gitignore`)

### 2.4 CLAUDE.md Structure Example

```markdown
# Project: Acme API Platform

## Tech Stack
- Runtime: Node.js 22 with TypeScript strict mode
- Framework: Fastify 5
- Database: PostgreSQL 16 via Drizzle ORM
- Testing: Vitest + Supertest
- Package manager: pnpm

## Build & Test Commands
- Install: `pnpm install`
- Build: `pnpm build`
- Test (all): `pnpm test`
- Test (single file): `pnpm test -- src/auth/auth.service.test.ts`
- Lint: `pnpm lint:fix`
- DB migrations: `pnpm db:migrate`

## Coding Conventions
- All functions must have JSDoc comments with @param and @returns
- Prefer `Result<T, E>` over thrown exceptions for expected errors
- Co-locate tests next to source files: `auth.service.ts` → `auth.service.test.ts`
- Never use `any`; use `unknown` and narrow types explicitly

## Architecture Decisions
- Route handlers are thin — business logic lives in service files
- All DB queries go through the repository layer; never query directly in routes
- Auth is handled by the `src/auth/` module; do not re-implement elsewhere

## Explicit Anti-patterns (Do Not Use)
- `express` (use Fastify instead)
- `moment` (use `date-fns`)
- Class-based services (use plain functions with dependency injection)
```

### 2.5 User Memory (`~/.claude/CLAUDE.md`)

User memory is the right place for personal, cross-project preferences. It is loaded for every Claude Code session regardless of the working directory.

```markdown
# Personal Preferences

## Communication Style
- Be concise. Skip preamble. Get to the answer.
- When uncertain, say so explicitly rather than guessing.
- Prefer code over prose explanations when both would work.

## Default Behaviors
- Always propose tests alongside new feature code
- When editing, show a brief summary of what changed and why
- Prefer `const` + arrow functions over `function` declarations
```

> ⚠️ **Caution:** User memory adds tokens to **every session**. Keep it genuinely universal — project-specific rules belong in the project `CLAUDE.md`, not here.

### 2.6 AGENTS.md — Cross-platform Agent Instructions

`AGENTS.md` is an **open, cross-platform specification** for providing AI coding agents with project-specific guidance. Unlike `CLAUDE.md` (Claude Code-specific), `AGENTS.md` is recognized by GitHub Copilot, Cursor, OpenAI Codex, Google Jules, Factory, and 20+ other AI coding tools. It is stewarded by the Agentic AI Foundation under the Linux Foundation.

**Purpose:** Think of `AGENTS.md` as a README for agents — a dedicated, predictable location that any AI tool knows to read before working on your codebase.

#### When to use AGENTS.md vs CLAUDE.md

| Concern | File | Rationale |
|---------|------|-----------|
| Build/test/lint commands | Both | Universal enough to belong in both |
| Code style, naming conventions | `AGENTS.md` | Applies to any AI tool on the project |
| Architecture decisions | `AGENTS.md` | Tool-agnostic context |
| Claude-specific sub-agent configs | `CLAUDE.md` | Only meaningful to Claude Code |
| Personal editor preferences | `~/.claude/CLAUDE.md` | Claude-specific, user-level |
| Secrets / local paths | `.claude/CLAUDE.md` | Local override, never committed |
| Monorepo package overrides | Nested `AGENTS.md` | Each package gets its own context |

#### AGENTS.md Format

`AGENTS.md` uses plain Markdown with no required frontmatter or fixed structure. Agents parse the natural-language text you provide. Conventional sections include:

```markdown
# AGENTS.md

## Project Overview
Brief description of what this project is and what it does.

## Tech Stack
- Language: TypeScript (strict mode)
- Framework: Fastify 5
- Database: PostgreSQL 16 via Drizzle ORM
- Testing: Vitest + Supertest
- Package manager: pnpm

## Build & Test Commands
- Install: `pnpm install`
- Build: `pnpm build`
- Test (all): `pnpm test`
- Test (single): `pnpm test -- <file>`
- Lint: `pnpm lint:fix`
- Type check: `pnpm typecheck`

## Code Style
- All functions require JSDoc with @param and @returns
- Prefer `Result<T, E>` over thrown exceptions for expected errors
- Co-locate tests with source: `auth.service.ts` → `auth.service.test.ts`
- Never use `any`; use `unknown` and narrow explicitly

## Architecture
- Route handlers are thin — business logic lives in service files
- All DB queries go through the repository layer
- Auth handled by `src/auth/`; do not re-implement elsewhere

## Commit Convention
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation only
- `refactor:` no functional change
- `test:` test changes only

## Security
- No secrets or credentials in source code
- Use environment variables for all configuration
- Validate all inputs at system boundaries
```

#### Hierarchical Placement (Monorepo Support)

Like `CLAUDE.md`, `AGENTS.md` files can be nested. Agents automatically read the nearest file in the directory tree — the closest one takes precedence.

```
your-monorepo/
├── AGENTS.md               ← Root-level: shared conventions
├── packages/
│   ├── frontend/
│   │   └── AGENTS.md       ← Frontend-specific: React, CSS, component patterns
│   └── api/
│       └── AGENTS.md       ← API-specific: endpoint conventions, DB usage
└── infra/
    └── AGENTS.md           ← Infra-specific: Terraform, cloud provider patterns
```

> **Best Practice:** Use `AGENTS.md` for content that should work across *any* AI tool (build commands, code style, architecture). Use `CLAUDE.md` for Claude Code-specific configuration (sub-agent workflows, Claude-specific anti-patterns, hooks documentation).

---

## Chapter 3: Sub-agents

Sub-agents are specialized Claude Code instances with their own persona, tool set, model selection, and permission scope. A parent agent can delegate tasks to sub-agents programmatically, enabling **automated divide-and-conquer workflows** without user intervention.

### 3.1 Sub-agent Definition Format

Sub-agents are defined as Markdown files with YAML frontmatter. They live in `~/.claude/agents/` (user-global) or `.claude/agents/` (project-scoped).

**Complete frontmatter reference:**

```yaml
---
name: security-reviewer            # Unique identifier (used for invocation)
description: >                      # When should this sub-agent be used?
  Analyzes code for security vulnerabilities including injection attacks,
  authentication flaws, insecure dependencies, and secrets exposure.
  Use when reviewing PRs, auditing new modules, or evaluating third-party code.
model: claude-opus-4-5              # Model to use (can differ from parent)
tools:                              # Explicit tool whitelist (principle of least privilege)
  - Read
  - Bash
disallowedTools:                    # Explicit blocklist (belt-and-suspenders)
  - Write
  - Edit
permissionMode: default             # 'default' | 'acceptEdits' | 'bypassPermissions'
maxTurns: 10                        # Maximum agentic turns before stopping
mcpServers:                         # MCP servers available only to this sub-agent
  - semgrep-mcp
---

You are a security specialist focused exclusively on identifying vulnerabilities.

For every code review:
1. Check for injection vulnerabilities (SQL, command, path traversal)
2. Verify authentication and authorization logic
3. Scan for hardcoded secrets or insecure credential handling
4. Check dependency versions against known CVE databases
5. Assess input validation completeness

Return a structured report: severity (Critical/High/Medium/Low), location,
description, and recommended fix for each finding.
```

### 3.2 Frontmatter Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique identifier; used in parent's invocation |
| `description` | string | ✅ | Critical: Claude uses this to decide *when* to invoke the sub-agent |
| `model` | string | ❌ | Override model; useful for cost/quality optimization per task |
| `tools` | list | ❌ | Explicit tool allowlist; defaults to parent's tool set if omitted |
| `disallowedTools` | list | ❌ | Explicit blocklist; takes precedence over `tools` |
| `permissionMode` | enum | ❌ | `default`: normal prompts; `acceptEdits`: auto-accept file edits; `bypassPermissions`: skip all checks |
| `maxTurns` | integer | ❌ | Cap on agentic turns; prevents runaway loops |
| `mcpServers` | list | ❌ | MCP servers this sub-agent can access (by name) |
| `hooks` | object | ❌ | Per-sub-agent hooks (see Chapter 4) |
| `memory` | list | ❌ | Additional CLAUDE.md files to inject at startup |
| `zze` | list | ❌ | Skill content injected at sub-agent startup |

> ⚠️ **Critical:** The `description` field is the **primary criterion** Claude uses to decide whether to invoke a sub-agent autonomously. Write it to describe both *what the sub-agent does* and *when it should be triggered*, using concrete trigger phrases.

### 3.3 Sub-agent Storage Locations

| Location | Scope | Use Case |
|----------|-------|----------|
| `~/.claude/agents/` | All projects for this user | Personal utility sub-agents (test writer, commit formatter) |
| `.claude/agents/` | This project only | Project-specific specialists (domain expert, migration runner) |

### 3.4 Context Isolation: The Core Design Principle

Sub-agents run in an **isolated context**. They do not inherit the parent agent's conversation history — only the specific instructions passed at invocation time. This design has four key implications:

1. **Security**: A sub-agent cannot exfiltrate or act on context it was never given
2. **Focus**: The sub-agent's limited context window is used entirely for the delegated task
3. **Token efficiency**: The parent's accumulated history does not inflate sub-agent costs
4. **Parallelism**: Multiple sub-agents can run concurrently since they share no state

```
Parent Agent (full context)
    │
    ├── delegates task + relevant context snapshot ──→ Sub-agent A (isolated context)
    │                                                     └── returns result
    │
    └── delegates task + relevant context snapshot ──→ Sub-agent B (isolated context)
                                                          └── returns result
```

### 3.5 Nesting Constraint

> ⚠️ **Sub-agents cannot invoke other sub-agents.** The delegation hierarchy is **single-level only**. This prevents infinite recursion, privilege escalation chains, and unbounded token consumption. If your workflow requires multiple specialist layers, the **top-level parent** must invoke each specialist directly.

### 3.6 Example: Automated Quality Loop

One of the most powerful sub-agent patterns is the **automated quality loop** — the parent writes code, invokes a reviewer sub-agent, and iterates until the reviewer approves, with no user intervention required.

**`.claude/agents/code-reviewer.md`**
```yaml
---
name: code-reviewer
description: >
  Reviews code changes for quality, security, test coverage, and adherence
  to project standards. Use after implementing any non-trivial feature or fix.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 8
---

Review the provided code changes. Score 1–5 on each dimension:
- Security: injection safety, auth checks, input validation
- Correctness: edge cases, error handling, type safety
- Maintainability: naming clarity, separation of concerns, comments
- Test coverage: key paths exercised, edge cases covered

Return: overall score (1–5), a list of specific issues with file/line references,
and concrete suggested fixes. Do not approve (score < 4) if any Critical or High
severity issues exist.
```

**Parent agent behavior (in `CLAUDE.md` or inline):**
```markdown
## Quality Workflow
After implementing any feature:
1. Run the `code-reviewer` sub-agent on your changes
2. Fix all issues rated Critical or High
3. Re-run `code-reviewer` to verify fixes
4. Do not present the result to the user until the reviewer scores ≥ 4/5
```

### 3.7 Example: Research-Then-Implement Pattern

Separating research (read-only) from implementation (write-capable) reduces risk and improves focus quality.

**`.claude/agents/researcher.md`**
```yaml
---
name: researcher
description: >
  Researches the existing codebase to gather context, identify patterns, locate
  relevant files, and map dependencies. Use before implementing new features.
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

Research thoroughly using read-only tools. Return:
- Relevant files and their purpose
- Existing patterns and conventions to follow
- Dependencies that will be affected
- Potential conflicts or risks
- Recommended implementation approach
```

**`.claude/agents/implementer.md`**
```yaml
---
name: implementer
description: >
  Implements code changes based on a provided research summary and plan.
  Use when context has been gathered and a plan is ready.
tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Bash
maxTurns: 30
---

Implement the provided plan faithfully. Follow all conventions identified in
the research summary. Write tests alongside implementation code.
```

---

## Chapter 4: Hooks

Hooks are **deterministic scripts** that execute at specific lifecycle points during a Claude Code session. Unlike memory files and sub-agent prompts, hooks are **not LLM instructions** — they are shell commands or scripts that run unconditionally when their trigger fires.

> **Token impact:** Hooks execute at the process level and bypass the model entirely. They consume **zero tokens**. This makes them the most cost-effective mechanism for enforcement, logging, and automation.

### 4.1 Hook Event Types

| Hook Event | Trigger | Typical Use Cases |
|-----------|---------|-------------------|
| `PreToolUse` | Before any tool call | Block dangerous operations, validate parameters, enforce permission policies |
| `PostToolUse` | After any tool call | Run linter/formatter, log tool usage, send notifications |
| `Notification` | When Claude surfaces a notification | Route alerts to Slack, email, or monitoring systems |
| `Stop` | When the agent stops (task complete or error) | Send completion notifications, clean up temp files, trigger CI |
| `SubagentStop` | When a sub-agent stops | Aggregate sub-agent results, log sub-agent output |

### 4.2 Hook Configuration Format

Hooks are defined in `.claude/settings.json` under the `hooks` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "pnpm lint:fix --silent"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/notify-complete.sh"
          }
        ]
      }
    ]
  }
}
```

### 4.3 Hook Interception Mechanism

Claude Code uses a **stdin/stdout protocol** to communicate with hooks. Your hook script receives a JSON payload on stdin and must write a JSON response to stdout.

**Exit codes:**
| Exit Code | Meaning |
|-----------|---------|
| `0` | Allow the operation to proceed |
| `2` | **Block the operation** (Claude sees a permission-denied error) |
| Any other | Non-blocking failure (logged but operation continues) |

**`PreToolUse` payload example (stdin):**
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/build",
    "description": "Clean build artifacts"
  },
  "session_id": "abc123"
}
```

**Hook script that blocks dangerous shell commands:**
```bash
#!/usr/bin/env bash
# ~/.claude/hooks/validate-bash.sh

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Block patterns
if echo "$command" | grep -qE 'rm\s+-rf\s+/|sudo\s+rm|>>\s*/etc|chmod\s+777'; then
  echo '{"decision": "block", "reason": "Dangerous command pattern detected"}' >&2
  exit 2
fi

# Block git force pushes
if echo "$command" | grep -qE 'git push.*--force|git push.*-f'; then
  echo '{"decision": "block", "reason": "Force pushes are not permitted"}' >&2
  exit 2
fi

exit 0
```

### 4.4 PostToolUse: Auto-format on Write

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/auto-format.sh

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

if [[ -z "$file_path" ]]; then
  exit 0
fi

case "$file_path" in
  *.ts|*.tsx)  npx prettier --write "$file_path" 2>/dev/null ;;
  *.py)        ruff format "$file_path" 2>/dev/null ;;
  *.go)        gofmt -w "$file_path" 2>/dev/null ;;
  *.rs)        rustfmt "$file_path" 2>/dev/null ;;
esac

exit 0
```

### 4.5 Per-Sub-agent Hooks

Hooks can be scoped to a specific sub-agent by including a `hooks` key in the sub-agent's frontmatter. This allows different permission policies for different roles:

```yaml
---
name: database-migrator
description: Runs and manages database schema migrations
tools:
  - Bash
  - Read
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash .claude/hooks/require-migration-prefix.sh"
---
```

### 4.6 Hook Security Considerations

| Risk | Mitigation |
|------|-----------|
| Hook scripts themselves becoming attack surface | Version-control hooks; review all changes; prefer simple, single-purpose scripts |
| Hooks with write access modifying important files | Hooks should read tool inputs and emit decisions; avoid side effects beyond logging |
| Hook bypassing via `bypassPermissions` sub-agent mode | Explicitly audit any sub-agent using `bypassPermissions`; document the justification |
| Slow hooks blocking the agent loop | Set timeouts; hooks should complete in < 500ms for interactive sessions |

---

## Chapter 5: MCP Servers

Model Context Protocol (MCP) servers extend Claude Code with external tools — file systems, APIs, databases, custom scripts, and more. Claude Code functions as an MCP client; each connected server provides a set of tools the model can invoke.

### 5.1 MCP Server Configuration

MCP servers are configured in `.claude/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "custom-internal": {
      "type": "stdio",
      "command": "python",
      "args": [".claude/mcp/internal-tools.py"]
    }
  }
}
```

### 5.2 MCP Transport Types

| Type | Use Case | Configuration |
|------|----------|---------------|
| `stdio` | Local processes (npm packages, Python scripts, compiled binaries) | `command` + `args` + optional `env` |
| `http` | Remote services, cloud APIs, shared team servers | `url` + optional `headers` |
| `sse` | Server-sent events streams, real-time data | `url` + optional `headers` |

### 5.3 MCP Scoping: Project vs User-Level

```json
// ~/.claude/settings.json  ← User-global (available in all projects)
{
  "mcpServers": {
    "brave-search": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    }
  }
}

// .claude/settings.json  ← Project-local (only this project)
{
  "mcpServers": {
    "project-db": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "${DEV_DATABASE_URL}" }
    }
  }
}
```

### 5.4 Building a Custom MCP Server

For project-specific tooling, a lightweight Python MCP server is often the right choice:

```python
# .claude/mcp/project-tools.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-tools")

@mcp.tool()
def run_integration_tests(suite: str = "all") -> str:
    """Run integration tests for a specific suite or all suites."""
    import subprocess
    result = subprocess.run(
        ["pytest", f"tests/integration/{suite}", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120
    )
    return result.stdout + result.stderr

@mcp.tool()
def check_feature_flag(flag_name: str, environment: str = "development") -> dict:
    """Check the status of a feature flag in the given environment."""
    # ... your internal feature flag service
    pass

if __name__ == "__main__":
    mcp.run()
```

### 5.5 MCP Security Best Practices

- **Never hard-code credentials** in settings files — use environment variable references (`${VAR_NAME}`)
- **Scope MCP servers to the minimum necessary path/database/API scope**
- **Prefer project-level** `.claude/settings.json` over user-level for project-specific servers, so access is tied to repository checkout
- **Audit tool descriptions** in third-party MCP servers — the tool descriptions enter the model's context and could contain prompt injection payloads
- **Use `disallowedTools`** in sub-agent frontmatter to prevent sub-agents from accessing MCP tools they don't need

---

## Chapter 6: Slash Commands

Slash commands are user-invoked, parameterizable prompt templates stored as Markdown files in `.claude/commands/`. They are the right place for **repeatable, task-specific workflows** that a user intentionally triggers — as opposed to always-on instructions or autonomous sub-agent behaviors.

### 6.1 Command File Structure

```
.claude/
└── commands/
    ├── plan-feature.md          # /project:plan-feature
    ├── generate-endpoint.md     # /project:generate-endpoint
    ├── write-migration.md       # /project:write-migration
    └── summarize-pr.md          # /project:summarize-pr

~/.claude/
└── commands/
    ├── daily-standup.md         # /user:daily-standup  (available globally)
    └── code-explain.md          # /user:code-explain
```

> **Invocation prefix:** Project commands use `/project:<name>`; user commands use `/user:<name>`.

### 6.2 Command File Format

Commands support `$ARGUMENTS` for dynamic input and can reference Claude's built-in tools:

```markdown
---
description: Generate a new REST API endpoint with handler, service, repository, and tests
---

Create a complete REST endpoint for: **$ARGUMENTS**

Follow these steps in order:

1. **Identify the resource** — determine the entity name, HTTP method, and route path
2. **Create the route handler** in `src/routes/<resource>.routes.ts`
   - Thin handler: validate request, call service, return response
   - Include OpenAPI annotations
3. **Create the service** in `src/services/<resource>.service.ts`
   - Business logic lives here
   - Return `Result<T, AppError>` types
4. **Create the repository** in `src/repositories/<resource>.repository.ts`
   - All DB queries use Drizzle ORM
   - Never use raw SQL strings
5. **Write tests** in `src/routes/<resource>.routes.test.ts`
   - Cover happy path, validation errors, and auth failures
6. **Run `pnpm lint && pnpm test`** and fix any issues before finishing

Present a summary of all files created/modified when complete.
```

### 6.3 Advanced: Commands That Invoke Sub-agents

Commands can orchestrate sub-agents by instructing the parent to delegate:

```markdown
---
description: Full feature implementation with automated quality loop
---

Implement the following feature request: **$ARGUMENTS**

Workflow:
1. Invoke the `researcher` sub-agent to gather codebase context for this feature
2. Create an implementation plan based on the research findings
3. Implement the feature following the plan
4. Invoke the `code-reviewer` sub-agent on all changed files
5. Fix all issues rated Critical or High severity
6. Re-invoke `code-reviewer` until overall score is ≥ 4/5
7. Present the final implementation with a summary of reviewer feedback addressed
```

### 6.4 When to Use Slash Commands vs Other Mechanisms

> ⚠️ **Deprecation Notice:** Slash Commands (`.claude/commands/`) are the legacy mechanism. **Skills** (`.claude/skills/`) are the modern replacement and should be preferred for all new work. Skills support a superset of slash command functionality — including auto-invocation by Claude, isolated subagent execution, and cross-platform compatibility. Both formats continue to work; if a name conflict exists, the skill takes precedence.

| Scenario | Use Slash Command? | Preferred Alternative |
|----------|-------------------|-----------------------|
| User intentionally starts a specific workflow | ✅ Yes (legacy) | Skill (`/name`) |
| Workflow runs on every interaction | ❌ No | `CLAUDE.md` instruction |
| Workflow runs after every file write | ❌ No | `PostToolUse` hook |
| Workflow is complex multi-agent pipeline (automated) | ❌ No | Sub-agent in `CLAUDE.md` |
| Workflow has multiple variants / parameters | ✅ Yes (`$ARGUMENTS`) | Skill with `argument-hint` |
| Claude should auto-detect when to run it | ❌ No | Skill (auto-invocation via `description`) |

---

## Chapter 7: Skills

Skills are the **modern, preferred mechanism** for reusable, invocable workflows in Claude Code. They supersede slash commands and follow the open **Agent Skills** standard, making them portable across AI coding tools that adopt the specification.

Unlike slash commands (which are user-triggered prompt templates), skills offer three additional capabilities:
- **Claude auto-invocation**: Claude loads a skill automatically when conversation context matches its `description`
- **Isolated subagent execution**: Skills can spawn a forked subagent context (`context: fork`) for parallelism or isolation
- **Cross-platform compatibility**: The Agent Skills standard is supported by Claude Code, Cursor, and other tools

### 7.1 Skills vs Slash Commands — Key Differences

| Feature | Slash Commands (Legacy) | Skills (Preferred) |
|---------|-------------------------|--------------------|
| Storage location | `.claude/commands/*.md` | `.claude/skills/<name>/SKILL.md` |
| User invocation prefix | `/project:<name>` | `/<name>` |
| Claude auto-invocation | ❌ No | ✅ Yes (via `description` matching) |
| Isolated subagent context | ❌ No | ✅ Yes (`context: fork`) |
| Argument access | `$ARGUMENTS` only | `$ARGUMENTS`, `$1`, `$ARGUMENTS[N]` |
| Cross-platform standard | ❌ No | ✅ Yes (Agent Skills spec) |
| Invocation control | None | `disable-model-invocation`, `user-invocable` |
| Name conflict resolution | N/A | Skill takes precedence over command |

### 7.2 Skill File Format

Every skill lives in its own directory under `.claude/skills/` (project) or `~/.claude/skills/` (user-global). The directory name becomes the skill's invocation name. Each directory requires a `SKILL.md` file.

```
.claude/skills/
├── debug-ci/
│   └── SKILL.md              # invoked as /debug-ci
├── summarize-pr/
│   └── SKILL.md              # invoked as /summarize-pr
└── generate-endpoint/
    ├── SKILL.md              # invoked as /generate-endpoint
    └── template.md           # optional supporting file
```

**`SKILL.md` Frontmatter Fields:**

```yaml
---
name: generate-endpoint                  # display name and slash-command (optional; defaults to dir name)
description: >                           # CRITICAL: used for auto-invocation detection
  Generates a complete REST API endpoint with handler, service, repository,
  and tests. Trigger when user asks to add a new endpoint or API route.
argument-hint: "[resource-name] [method]"  # shown in autocomplete
disable-model-invocation: false          # true = only user can invoke; hides description from context
user-invocable: true                     # false = only Claude can invoke (background knowledge skill)
allowed-tools: Read, Bash, Write, Edit   # tools allowed without permission prompt while skill is active
model: claude-sonnet-4-6                 # optional model override
context: fork                            # run in isolated subagent (omit for inline execution)
agent: general-purpose                   # subagent type when context: fork (Explore, Plan, general-purpose)
---

Skill body — full instructions that Claude follows when this skill is invoked.
Use $ARGUMENTS for the full argument string, $1 for first arg, $ARGUMENTS[N] for Nth arg.
```

**Complete Frontmatter Reference:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Slash-command name (lowercase, numbers, hyphens, max 64 chars). Defaults to directory name. |
| `description` | string | **Critical.** Describes what the skill does and when to auto-trigger. Claude uses this to decide when to load it. |
| `argument-hint` | string | Autocomplete hint showing expected arguments, e.g., `[issue-number]` or `[filename] [format]` |
| `disable-model-invocation` | bool | `true` = only user can invoke; description not injected into context |
| `user-invocable` | bool | `false` = only Claude can auto-invoke; hidden from `/` menu |
| `allowed-tools` | string | Comma-separated tools Claude may use without a permission prompt while the skill is active |
| `model` | string | Model override for this skill's execution |
| `context` | string | `fork` = run in isolated subagent context; omit for inline execution |
| `agent` | string | Subagent type for `context: fork`: `Explore`, `Plan`, or `general-purpose` |

### 7.3 Invocation Modes

Skills support three distinct invocation modes, controlled via frontmatter:

```
Default (no overrides):
  ✅ User can invoke via /<name>
  ✅ Claude auto-invokes when description matches
  ✅ Description is always in context

disable-model-invocation: true:
  ✅ User can invoke via /<name>
  ❌ Claude cannot auto-invoke
  ❌ Description NOT in context (zero token cost when idle)
  → Use for heavy workflows you only want explicitly triggered

user-invocable: false:
  ❌ User cannot invoke via slash command
  ✅ Claude auto-invokes only
  ✅ Description always in context
  → Use for background knowledge skills Claude should apply silently
```

### 7.4 Skills in Sub-agent Frontmatter

The `skills` field in a sub-agent's frontmatter preloads specific skills into that sub-agent at startup. This is the inverse of `context: fork` — instead of a skill defining which subagent to use, the sub-agent specifies which skills it should have available:

```yaml
---
name: full-stack-implementer
description: Implements full-stack features with access to endpoint and migration skills
tools:
  - Read
  - Write
  - Edit
  - Bash
skills:
  - generate-endpoint
  - write-migration
  - write-tests
---
```

### 7.5 Dynamic String Substitutions

| Substitution | Value |
|-------------|-------|
| `$ARGUMENTS` | Full argument string passed at invocation |
| `$1`, `$2`, ... `$N` | Individual arguments by position |
| `$ARGUMENTS[N]` | Nth argument (0-indexed) |
| `${CLAUDE_SESSION_ID}` | Current session ID (useful for logging) |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory |

### 7.6 Example: Research Skill with Isolated Context

```yaml
---
name: research-codebase
description: >
  Researches the codebase to gather context before implementing a feature.
  Auto-trigger when the user describes a new feature or asks how to implement something.
argument-hint: "[feature description]"
context: fork
agent: Explore
allowed-tools: Read, Bash
---

Research the codebase to understand how to implement: $ARGUMENTS

Use read-only tools only. Return:
1. Relevant files and their purpose
2. Existing patterns and conventions to follow
3. Dependencies that will be affected
4. Recommended implementation approach
```

### 7.7 Example: On-demand Workflow Skill

```yaml
---
name: summarize-pr
description: >
  Summarizes a pull request by analyzing the git diff and changed files.
  Use when the user asks for a PR summary or wants to understand recent changes.
argument-hint: "[branch-or-commit-range]"
disable-model-invocation: false
allowed-tools: Bash, Read
---

Summarize the changes in: $ARGUMENTS

Steps:
1. Run `git log --oneline $ARGUMENTS` to see commits
2. Run `git diff $ARGUMENTS` to see all changed lines
3. Identify the primary purpose of the change (feature / fix / refactor / docs)
4. List files changed grouped by type
5. Write a 3-5 sentence summary suitable for a PR description
6. Suggest a PR title following conventional commit format
```

### 7.8 Storage Locations and Priority

| Location | Scope | Priority |
|----------|-------|----------|
| `~/.claude/skills/<name>/SKILL.md` | User-global (all projects) | Medium |
| `.claude/skills/<name>/SKILL.md` | Project-scoped | Medium |
| Enterprise-deployed skills | Organization-wide | Highest |

When skills share the same name across levels: **enterprise > personal > project**. Plugin skills use a `plugin-name:skill-name` namespace to avoid conflicts.

> **Monorepo Note:** Claude Code discovers skills from the nearest `.claude/skills/` directory in the directory tree, enabling per-package skill overrides in monorepos.

---

## Chapter 8: Where Does the Workflow Belong?

**This is the most common architectural anti-pattern.** Engineers instinctively put all instructions into `CLAUDE.md` — the equivalent of writing the entire employee handbook as a single always-on system prompt. This approach wastes tokens and produces unreliable execution.

### 8.1 Why Workflows Do Not Belong in CLAUDE.md

1. **Token waste:** `CLAUDE.md` is always-on. A debugging workflow injected here costs tokens on every simple question.

2. **Separation-of-concerns violation:** Memory files are *standards and context*, not *runbooks*. Complex orchestration instructions dilute the signal of the standards that should always be present.

3. **Unreliable execution:** LLMs become less reliable the more procedural and conditional the instruction. Deterministic hooks, not prose instructions, are the right enforcement mechanism for unconditional behaviors.

4. **Stale on simple tasks:** A user asking "what does this function do?" should not have a 15-step CI debugging workflow consuming context window space.

### 8.2 Correct Placement Reference

| Workflow Type | Correct Location | Rationale |
|--------------|-----------------|-----------|
| Global coding standards, naming conventions, tech stack rules | `CLAUDE.md` / `AGENTS.md` | Must apply to nearly every interaction; `AGENTS.md` for cross-platform |
| Build / test / lint commands | `AGENTS.md` + `CLAUDE.md` | Needed in virtually every session; `AGENTS.md` for portability |
| Module-specific conventions | `src/<module>/CLAUDE.md` | Only needed when working in that subtree |
| Personal editor preferences | `~/.claude/CLAUDE.md` | Personal, not project-specific |
| Complex task-specific procedures (CI debugging, DB migrations) | **Skill** or Sub-agent | On-demand; doesn't consume tokens otherwise |
| Automated parallel/divide-and-conquer tasks | Sub-agent (`.claude/agents/`) | Parent delegates programmatically |
| User-triggered repeatable tasks | **Skill** (`.claude/skills/`) | Explicitly invoked + Claude auto-invoke; preferred over slash commands |
| User-triggered repeatable tasks (legacy) | Slash Command (`.claude/commands/`) | Legacy format; prefer Skills for new work |
| Claude auto-invoked contextual workflows | **Skill** with `description` | Claude loads when description matches context |
| Unconditional enforcement (lint on save, block `rm -rf`) | Hook | Deterministic; zero tokens |
| External tool access (DB, APIs, file systems) | MCP Server | Structured tool interface |

### 8.3 Layered Model Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│  CLAUDE.md (Project Memory)                                           │
│  ✅ Coding standards, naming conventions, tech stack prefs            │
│  ✅ Build/test/lint commands                                           │
│  ✅ Architecture decisions and key anti-patterns                       │
│  ❌ Do NOT include complex workflow orchestration                      │
│  ❌ Do NOT include machine-local paths or secrets                      │
├──────────────────────────────────────────────────────────────────────┤
│  .claude/agents/*.md (Sub-agents)                                    │
│  ✅ Automated divide-and-conquer tasks (research → implement)         │
│  ✅ Quality review loops (implement → review → fix → approve)         │
│  ✅ Role-specific specialists (security auditor, migration runner)     │
│  ✅ Each sub-agent gets minimum necessary tools (least privilege)      │
├──────────────────────────────────────────────────────────────────────┤
│  .claude/skills/<name>/SKILL.md (Skills — preferred)                │
│  ✅ User-triggered workflows via /<name>                              │
│  ✅ Claude auto-invoked when description matches context              │
│  ✅ Parameterized with $ARGUMENTS, $1, $ARGUMENTS[N]                 │
│  ✅ Isolated subagent execution via context: fork                     │
│  ✅ Cross-platform: follows open Agent Skills standard                │
├──────────────────────────────────────────────────────────────────────┤
│  .claude/commands/*.md (Slash Commands — legacy)                     │
│  ✅ Still supported; prefer Skills for new work                       │
│  ✅ User-triggered via /project:<name>                                │
├──────────────────────────────────────────────────────────────────────┤
│  Hooks (PreToolUse / PostToolUse / Stop)                             │
│  ✅ Zero-token unconditional enforcement                               │
│  ✅ "Lint after every write", "Block rm -rf /", "Notify on complete"  │
│  ✅ The only correct mechanism for truly deterministic behavior        │
├──────────────────────────────────────────────────────────────────────┤
│  MCP Servers                                                          │
│  ✅ Structured external tool access (DB, APIs, search, custom tools)  │
│  ✅ Scoped credentials via environment variables                       │
└──────────────────────────────────────────────────────────────────────┘
```

> **General rule:** If the content is relevant to *nearly every interaction* → `CLAUDE.md` / `AGENTS.md`. If it applies to *specific tasks only* → Skill or Sub-agent. If the user or Claude should invoke it on-demand → Skill. If it requires *unconditional enforcement* → Hook. If it provides *external tool access* → MCP Server.

---

## Chapter 9: Complete Project Structure Example

Below is the recommended directory structure for a full-stack project (TypeScript frontend, Python backend):

```
your-project/
├── CLAUDE.md                               ← Claude-specific standards (shared via git)
├── AGENTS.md                               ← Cross-platform agent instructions (shared via git)
├── .claude/
│   ├── CLAUDE.md                           ← Machine-local overrides (gitignored)
│   ├── settings.json                       ← MCP servers, hooks, permissions
│   ├── agents/
│   │   ├── researcher.md                   ← Read-only codebase researcher
│   │   ├── implementer.md                  ← Write-capable code implementer
│   │   ├── code-reviewer.md                ← Read-only quality reviewer
│   │   ├── security-auditor.md             ← Security-focused read-only reviewer
│   │   └── migration-runner.md             ← DB migration specialist
│   ├── skills/
│   │   ├── plan-feature/
│   │   │   └── SKILL.md                    ← /plan-feature (user + auto-invoke)
│   │   ├── generate-endpoint/
│   │   │   └── SKILL.md                    ← /generate-endpoint
│   │   ├── write-migration/
│   │   │   └── SKILL.md                    ← /write-migration
│   │   ├── summarize-pr/
│   │   │   └── SKILL.md                    ← /summarize-pr
│   │   └── full-feature/
│   │       └── SKILL.md                    ← /full-feature (orchestrates sub-agents)
│   ├── commands/                           ← Legacy slash commands (keep for compatibility)
│   │   └── .gitkeep
│   └── hooks/
│       ├── validate-bash.sh                ← PreToolUse: block dangerous commands
│       ├── auto-format.sh                  ← PostToolUse: lint/format on write
│       └── notify-complete.sh              ← Stop: send Slack notification
├── src/
│   ├── CLAUDE.md                           ← Frontend-specific conventions
│   ├── AGENTS.md                           ← Frontend-specific agent instructions
│   └── ...
├── backend/
│   ├── CLAUDE.md                           ← Python/FastAPI-specific conventions
│   ├── AGENTS.md                           ← Backend-specific agent instructions
│   └── ...
└── tests/
    └── CLAUDE.md                           ← Test writing conventions
```

### `.claude/settings.json` — Full Example

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(pnpm test:*)",
      "Bash(pnpm lint:*)",
      "Bash(pytest:*)"
    ],
    "deny": [
      "Bash(git push --force:*)",
      "Bash(rm -rf /:*)",
      "Bash(sudo:*)"
    ]
  },
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-bash.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-format.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/notify-complete.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Chapter 10: Token Cost Strategy

Understanding each component's token consumption pattern is essential for sound architectural decisions at scale.

### 10.1 Token Consumption by Component

| Component | Loading Mechanism | Token Cost | Optimization Guidance |
|-----------|------------------|-----------|----------------------|
| `CLAUDE.md` (project root) | Always-on | 200–800 tokens (recommended) | Limit to essential rules; target < 500 tokens |
| `AGENTS.md` (project root) | Always-on (any agent) | 200–600 tokens (recommended) | Focus on build/test/style; avoid Claude-specific config |
| `~/.claude/CLAUDE.md` (user) | Always-on (globally) | 100–300 tokens (recommended) | Keep genuinely universal; avoid project-specific rules |
| Sub-directory `CLAUDE.md` / `AGENTS.md` | When agent operates in that subtree | 100–400 tokens | Scope tightly to the module |
| Sub-agent frontmatter + body | On-demand (when parent delegates) | Isolated context; does not accumulate parent history | Keep concise; long prompts balloon per-invocation costs |
| Skill body (`disable-model-invocation: false`) | Description always in context; body on invocation | Description: ~20–50 tokens always; body: 100–500 on invoke | Write concise descriptions; body detail is fine |
| Skill body (`disable-model-invocation: true`) | Only on explicit user invocation | **0 tokens when idle** | Use for heavy workflows not needed by Claude auto-invoke |
| Slash command body (legacy) | On-demand (when user invokes) | 100–500 tokens | Prefer Skills for new work |
| MCP tool descriptions | Session startup (once per connection) | ~30–100 tokens per tool | Audit third-party servers for bloated descriptions |
| **Hooks** | **Event-triggered code execution** | **0 tokens** | **No limit; prefer hooks over instructions for enforcement** |

### 10.2 Cost Spectrum

```
Zero cost ────────────────────────────────────────────── High cost

  Hooks     Skills             Sub-directory   Skills          Sub-agent    CLAUDE.md   User CLAUDE.md
  (0 tok)   (disable-model-    CLAUDE.md       (default,       (on-demand,  (always-on) (always-on,
            invocation:true,   (subtree)       desc always     isolated)                all projects)
            0 idle tokens)                     in context)
```

### 10.3 Strategic Principles

| Principle | Explanation |
|-----------|-------------|
| **Never always-on what can be on-demand** | If a rule applies to only one module → sub-directory `CLAUDE.md`, not root |
| **Never use instructions when hooks suffice** | "Always run lint after writing files" → `PostToolUse` hook, not a `CLAUDE.md` rule |
| **Prefer Skills over Slash Commands for new work** | Skills support auto-invocation, isolated contexts, and the open Agent Skills standard |
| **Use `disable-model-invocation: true` for heavy skills** | Prevents description tokens loading on every session; user still invokes explicitly |
| **Sub-agents are cheaper than context accumulation** | A sub-agent starts fresh; delegating from a long parent session saves tokens |
| **Write precise skill and sub-agent descriptions** | Poor descriptions → false positives (wrong skill/agent invoked) or false negatives (never invoked) |
| **Split large CLAUDE.md into subtree files** | A 2,000-token root `CLAUDE.md` costs 2,000 tokens even for unrelated tasks; split into 400-token sub-tree files |
| **Use AGENTS.md for cross-platform conventions** | Build commands, code style → `AGENTS.md` (any tool reads it); Claude-specific config → `CLAUDE.md` |

---

## Chapter 11: Security Best Practices

### 11.1 Security Layer Overview

| Layer | Risk | Mitigation |
|-------|------|------------|
| **CLAUDE.md / AGENTS.md** | Prompt injection: attacker-controlled content reaching memory files | Version control + code review for all changes; never auto-generate from untrusted input |
| **Sub-agents** | Over-permissioning: reviewer sub-agent given write access | `tools` whitelist + `disallowedTools` blocklist per sub-agent; enforce principle of least privilege |
| **Sub-agents** | `bypassPermissions` mode disabling all safety checks | Audit every sub-agent using `bypassPermissions`; document justification; prohibit in production pipelines |
| **Skills** | Skill files containing destructive operations or prompt injection | Code-review all `SKILL.md` files; treat them as production code; audit `allowed-tools` grants |
| **Skills** | `allowed-tools` granting unnecessary permissions | Only list tools the skill genuinely needs; prefer the narrowest set possible |
| **Hooks** | Hook scripts becoming attack surface | Audit and review all hook scripts; keep them simple and deterministic; no dynamic code evaluation |
| **MCP Servers** | Malicious tool descriptions (prompt injection) | Audit tool descriptions for third-party servers; pin server versions |
| **MCP Servers** | Credential exposure | Use `${ENV_VAR}` references; never hard-code tokens; add `.claude/settings.json` with secrets to `.gitignore` |
| **Slash Commands** | Command files containing destructive operations | Code-review command files like production code; test in isolated environments first |
| **settings.json** | Overly broad `allow` patterns | Default deny; explicitly enumerate allowed commands with specific argument patterns |

### 11.2 Security Design Principles

**1. Default Deny for Shell Access**

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm test:*)",
      "Bash(pnpm lint:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(git status:*)"
    ],
    "deny": ["Bash(*)"]
  }
}
```

The `deny` rule at the end acts as a catch-all. Explicitly enumerate every command pattern that should be permitted.

**2. Least Privilege for Sub-agents**

```yaml
# ❌ Anti-pattern: giving a reviewer write access
tools:
  - Read
  - Write   # Reviewers do not write
  - Edit    # Reviewers do not edit
  - Bash

# ✅ Best practice: read-only reviewer
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
```

**3. Container Isolation for Risky Agents**

Any sub-agent or slash command that executes tests, builds, or migrations should run inside a container:

```yaml
---
name: migration-runner
description: Runs database migrations against the development database
permissionMode: acceptEdits
---

You are a database migration specialist.
⚠️ Always run in Docker: `docker compose exec api python manage.py migrate`
Never modify the host database directly.
```

**4. Audit Trail via PostToolUse Hooks**

```bash
#!/usr/bin/env bash
# .claude/hooks/audit-log.sh
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$timestamp | $tool_name | $(echo "$input" | jq -c '.tool_input')" >> ~/.claude/audit.log
exit 0
```

**5. Secrets Management**

```bash
# .gitignore — always include these
.claude/CLAUDE.md          # Local overrides may contain paths/references
.claude/settings.local.json  # Local MCP credentials

# settings.json — reference env vars, never inline values
{
  "mcpServers": {
    "github": {
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"  # ✅ env var reference
        # "Authorization": "Bearer ghp_abc123..."  # ❌ never do this
      }
    }
  }
}
```

---

## Appendix A: Settings Reference and Permission Model

### A.1 `.claude/settings.json` Full Schema Reference

```json
{
  // Model defaults
  "model": "claude-sonnet-4-5",           // Default model for sessions

  // Permission system
  "permissions": {
    "allow": [                              // Allowlist of tool call patterns
      "Bash(git:*)",                        // All git subcommands
      "Bash(pnpm test -- *)",               // pnpm test with any arguments
      "Read(**/*.ts)",                      // Read any TypeScript file
      "Write(src/**/*)"                     // Write only within src/
    ],
    "deny": [                               // Blocklist (takes precedence over allow)
      "Bash(rm -rf *)",
      "Bash(curl * | bash)"
    ]
  },

  // MCP server definitions
  "mcpServers": { /* see Chapter 5 */ },

  // Lifecycle hooks
  "hooks": { /* see Chapter 4 */ },

  // Environment variables passed to all tool executions
  "env": {
    "NODE_ENV": "development",
    "LOG_LEVEL": "debug"
  }
}
```

### A.2 Permission Pattern Syntax

| Pattern | Matches |
|---------|---------|
| `Bash(git:*)` | Any `git` command |
| `Bash(pnpm test -- *)` | `pnpm test` with any trailing arguments |
| `Read(**/*.ts)` | Read any `.ts` file at any depth |
| `Write(src/**/*)`| Write any file under `src/` |
| `Bash(*)` | Any bash command (use only in `deny` as catch-all) |
| `*` | Any tool call (use carefully) |

### A.3 permissionMode Values for Sub-agents

| Value | Behavior | When to Use |
|-------|----------|-------------|
| `default` | Normal prompts for each sensitive operation | Standard sub-agents |
| `acceptEdits` | Automatically accept file edits without prompting | CI/CD pipeline sub-agents |
| `bypassPermissions` | Skip **all** permission checks | Requires explicit justification; high-trust automation only |

---

## Appendix B: Claude Code vs GitHub Copilot Customization Comparison

| Dimension | Claude Code | GitHub Copilot |
|-----------|------------|----------------|
| **Primary config file** | `CLAUDE.md` (Claude-specific) + `AGENTS.md` (cross-platform) | `.github/copilot-instructions.md` |
| **Cross-platform agent instructions** | ✅ `AGENTS.md` (open standard; works with 20+ tools) | ✅ `AGENTS.md` (also reads the open standard) |
| **Sub-directory scoping** | ✅ `src/CLAUDE.md`, `src/AGENTS.md` etc. | ✅ `applyTo` glob in `.instructions.md` |
| **User-level config** | `~/.claude/CLAUDE.md` | VS Code User Settings |
| **Sub-agent definition** | Markdown + YAML frontmatter in `~/.claude/agents/` or `.claude/agents/` | `.agent.md` files in `.github/agents/` |
| **Handoff mechanism** | Not available (use Skills for human-gated stages) | ✅ `handoffs` field in `.agent.md` |
| **Sub-agent nesting** | Single level (sub-agents cannot spawn sub-agents) | Single level (same constraint) |
| **Hook granularity** | Tool-level (`PreToolUse` before each tool call) | Event-level (git, session lifecycle) |
| **Hook interception** | Exit code 2 = block; stdin/stdout JSON protocol | `permissions.allowedCommands` |
| **Skills / reusable workflows** | ✅ `.claude/skills/<name>/SKILL.md` — user + Claude auto-invocation; open Agent Skills standard | `.github/prompts/*.prompt.md` (invoke: `/`) |
| **Slash commands (legacy)** | `.claude/commands/*.md` (invoke: `/project:<name>`) | N/A (use prompts) |
| **Skill auto-invocation** | ✅ Claude auto-loads skills when `description` matches | ❌ User must explicitly invoke |
| **Skill isolated context** | ✅ `context: fork` runs in isolated subagent | ❌ Not supported |
| **MCP integration** | Native; configured in `settings.json` | Native; configured in VS Code settings |
| **Token consumption** | Hooks = 0; skills with `disable-model-invocation` = 0 idle; CLAUDE.md = always-on | Hooks = 0; instructions = always-on; sub-agents = isolated |
| **Permission model** | Allow/deny patterns in `settings.json` + sub-agent `permissionMode` | `tools` whitelist in `.agent.md` |
| **Environment** | Terminal-first (all platforms) | IDE-first (VS Code, JetBrains, etc.) |
| **Version control** | All config files committed to repo (except local overrides) | All config files committed to repo |

---

> **Core design philosophy:** Claude Code is built for engineers who live in the terminal and want their AI tooling to behave like a disciplined, version-controlled member of the team. Every customization is a plain text file, every enforcement mechanism is a script, and every context decision is observable and auditable. The goal is not just to make Claude helpful — it is to make Claude reliably correct within the specific constraints of your project and your team.

---

*— END —*
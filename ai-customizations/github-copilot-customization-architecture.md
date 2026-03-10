# GitHub Copilot Customization Architecture
## Instructions · Skills · Custom Agents · Hooks · SDK
### Best Practices for Engineers ｜ Principal Engineer Perspective
#### February 2026

---

## Table of Contents

1. [Architecture Overview — Five Core Components and Their Relationships](#chapter-1-architecture-overview)
2. [Instructions — Six File Types and the Layered Model](#chapter-2-instructions)
3. [Agent Skills — Progressive Disclosure and Token Management](#chapter-3-agent-skills)
4. [Custom Agents — Role Design, Handoffs, and Sub-agent Orchestration](#chapter-4-custom-agents)
5. [Hooks — Security Interception and Automation](#chapter-5-hooks)
6. [Where Does the Workflow Belong? — Common Anti-Patterns and Correct Placement](#chapter-6-where-does-the-workflow-belong)
7. [Complete Project Structure Example](#chapter-7-complete-project-structure-example)
8. [Token Cost Strategy](#chapter-8-token-cost-strategy)
9. [Security Best Practices](#chapter-9-security-best-practices)
10. [Appendix A — Copilot SDK Integration Patterns and Examples](#appendix-a-copilot-sdk-integration-patterns)

---

## Chapter 1: Architecture Overview

GitHub Copilot's customization system comprises five core components, each serving a distinct purpose within a layered, cooperative architecture. Understanding their relationships is a prerequisite for effective usage.

| Component | Analogy | Loading Behavior | Scope | Origin |
|-----------|---------|-----------------|-------|--------|
| **Instructions** | Company bylaws / employee handbook | Always-on or pattern-matched | Conventions, preferences, standards | GitHub + OpenAI + Anthropic |
| **Agent Skills** | Specialist training manuals | On-demand (description match or /invoke) | Complete workflows + scripts + examples | Anthropic (open standard) |
| **Custom Agents** | Dedicated roles (frontend engineer, security auditor) | User-selected / delegated by a parent agent | Persona + tool restrictions + handoffs + sub-agents | GitHub / VS Code |
| **Hooks** | Security checkpoints / automation triggers | Lifecycle event triggers | Permission checks, linting, notifications | GitHub / Claude Code |
| **Copilot SDK** | Programmatic remote control | Application invocation | Assembles all of the above into your own app | GitHub SDK |

> **Architectural Principle:** The foundation layer (Instructions) establishes *"who you are"*; the capability layer (Skills) provides *"how to do it"*; the role layer (Agents) defines *"who does it"*; and the safety layer (Hooks) ensures *"it's done safely."*

---

## Chapter 2: Instructions

GitHub Copilot currently supports six distinct instruction mechanisms, each with different scopes, loading behaviors, and platform compatibility. [[REF-1]](#references) [[REF-3]](#references) [[REF-4]](#references)

### 2.1 Six Instruction Types

| Type | File Location | Loading Behavior | Supported Platforms | Purpose |
|------|--------------|-----------------|--------------------:|---------|
| **Repository-Wide** | `.github/copilot-instructions.md` | Always-on (injected every time) | VS Code, JetBrains, Eclipse, Xcode, GitHub.com | Global coding standards, tech stack preferences |
| **Path-Specific** | `.github/instructions/*.instructions.md` | File-matched via `applyTo` glob | VS Code, GitHub.com | Language- or framework-specific rules |
| **Agent Instructions** | `AGENTS.md` (any directory) | When a coding agent operates autonomously | VS Code, GitHub.com, Copilot CLI | Autonomous agent operational procedures |
| **Model-Specific** | `CLAUDE.md` / `GEMINI.md` | Always-on (when the corresponding model is active) | GitHub.com | Model-specific guidance |
| **Personal** | VS Code User Settings | Always-on (across workspaces) | VS Code | Individual preferences |
| **Organization** | GitHub Org settings | Always-on (organization-wide) | All platforms | Organization-level standards |

### 2.2 Precedence and Composition Rules

When multiple instruction types coexist, Copilot **merges them into the context**. Precedence from highest to lowest: [[REF-1]](#references)

```
Layer 0: Personal Instructions (VS Code Settings)         ← Highest precedence
Layer 1: copilot-instructions.md (repo-wide)               ← Always-on
Layer 2: *.instructions.md (matched by applyTo glob)       ← Conditionally loaded
Layer 3: AGENTS.md (when a coding agent is operating)      ← Agent-scoped
Layer 4: Skill (if the task matches a skill description)   ← On-demand
Layer 5: Custom Agent prompt (if a specific agent is selected) ← Explicitly selected
```

All applicable instructions are provided to Copilot simultaneously, so **avoid contradictions** between layers.

### 2.3 copilot-instructions.md Best Practices

- ✅ Keep it concise: **5–15 core rules** (200–500 tokens)
- ✅ Include only content that is relevant to *nearly every* interaction
- ❌ **Do not include workflow orchestration logic** (see Chapter 6)
- ❌ Do not duplicate content already covered by path-specific instructions
- ❌ Do not embed lengthy code examples (put those in Skills instead)

### 2.4 Key Difference: `applyTo: "*"` vs `copilot-instructions.md`

| Dimension | `copilot-instructions.md` | `.instructions.md` with `applyTo: "*"` |
|-----------|--------------------------|----------------------------------------|
| Trigger condition | **Unconditional** — included in every chat, agent run, and code review | **Conditional** — requires an active file context |
| Chat-only scenario | ✅ Injected | ❌ May not be injected (no file context) |
| `excludeAgent` support | ❌ Not available | ✅ Can exclude specific agents (e.g., `"code-review"`) |
| Platform support | JetBrains, Eclipse, Xcode, and all other platforms | VS Code and GitHub.com only |

**Practical guidance:**
- Rules that must apply **across all scenarios and all platforms** → `copilot-instructions.md`
- Rules that apply to all files but should **only affect the coding agent, not code review** → use `applyTo: "*"` with `excludeAgent`

---

## Chapter 3: Agent Skills

Agent Skills are an open standard (originally created by Anthropic) that works across VS Code, Copilot CLI, Copilot Coding Agent, and Claude Code. Their core design principle is **progressive disclosure**. [[REF-6]](#references) [[REF-7]](#references)

### 3.1 Three-Tier Loading Model

| Tier | Content | Token Budget | When Loaded |
|------|---------|-------------|-------------|
| **Tier 1: Metadata** | name + description (YAML frontmatter) | ~50–100 tokens/skill | **Always** (metadata for all skills is permanently in context) |
| **Tier 2: Body** | SKILL.md body content | Recommended < 500 tokens (hard limit: 5,000) | When Copilot determines relevance to the current task |
| **Tier 3: References** | Files under `references/` | Recommended < 1,000 tokens/file | When explicitly referenced by a skill instruction |

### 3.2 Directory Structure

```
.github/skills/webapp-testing/
├── SKILL.md              # Required: primary instructions
├── LICENSE.txt            # Recommended: license terms
├── scripts/               # Optional: executable scripts
│   ├── helper.py
│   └── helper.ps1
├── references/            # Optional: on-demand documentation
│   ├── api_reference.md
│   └── workflow-setup.md
├── assets/                # Optional: static resources (images, templates, etc.)
│   └── baseline.png
└── templates/             # Optional: AI-modifiable scaffolds
    └── scaffold.py
```

### 3.3 SKILL.md Structure Example

```markdown
---
name: webapp-testing
description: >
  Toolkit for testing local web applications using Playwright.
  Use when asked to verify frontend functionality, debug UI behavior,
  capture browser screenshots, or check for visual regressions.
  Supports Chrome, Firefox, and WebKit browsers.
---

## Quick Start
1. Run `npx playwright install` to set up browsers
2. Execute test suite: `npx playwright test`

## Detailed Workflows
- For visual regression, see [references/visual-testing.md](./references/visual-testing.md)
- For debugging, see [references/debugging-guide.md](./references/debugging-guide.md)
```

> ⚠️ **Important:** The `description` field is the **sole criterion** Copilot uses to determine whether to load a skill. The more precise the description, the higher the true-positive rate and the lower the false-positive rate. Always describe both *what the skill does* and *when it should be triggered*.

---

## Chapter 4: Custom Agents

Custom Agents are specialized roles that shape Copilot into a particular "teammate." They are defined in `.agent.md` files stored under `.github/agents/`. Understanding the two collaboration modes — **Handoff** and **Sub-agent** — is essential for designing effective multi-agent workflows. [[REF-8]](#references) [[REF-10]](#references)

### 4.1 Configuration Fields

| Frontmatter Field | Purpose | Example |
|--------------------|---------|---------|
| `name` | Display name | `Security Reviewer` |
| `description` | Role description (influences recommendation) | `Reviews code for security vulnerabilities` |
| `tools` | Allowed-tool whitelist | `['read', 'search', 'edit']` |
| `model` | Model selection (supports fallback lists) | `['Claude Opus 4.5', 'GPT-5.2']` |
| `handoffs` | Inter-agent transition configuration | See Section 4.2 |
| `agents` | Invocable sub-agent whitelist | `['Researcher', 'Implementer']` |

### 4.2 Handoffs: User-Guided Agent Transitions

A handoff is a **built-in orchestration mechanism** in GitHub Copilot. When an agent completes its response, a handoff button appears in the UI. The user clicks it to switch to the target agent, carrying over the preset prompt and prior conversation context. [[REF-10]](#references)

**Key characteristic:** Handoffs are **user-driven** — each transition requires explicit human confirmation (unless `send: true` is set). This is a "relay race" model: the previous runner finishes and passes the baton to the next.

```yaml
# .github/agents/planner.agent.md
---
name: Planner
description: Generate implementation plans from requirements
tools: ['search', 'fetch']
handoffs:
  - label: Start Implementation        # Button label shown in the UI
    agent: Implementer                  # Target agent name
    prompt: "Implement the plan above." # Pre-filled prompt
    send: false                         # false = user must click to confirm
---

You are a planning specialist. For each feature request:
1. Research existing patterns in the codebase
2. Identify affected files and dependencies
3. Create a step-by-step implementation plan
4. List test cases that should be written
```

**Handoff workflow example: Planning → Implementation → Review**

```
User selects @Planner → Planner generates plan
    ↓ User clicks [Start Implementation] button
Implementer receives plan context → implements code
    ↓ User clicks [Review Code] button
Reviewer receives implementation → produces review report
    ↓ User clicks [Back to Planning] button (if revision is needed)
Planner receives review feedback → revises plan
```

### 4.3 Sub-agents: Programmatic Agent Delegation

A sub-agent is an entirely different collaboration mode. The parent agent **programmatically invokes** another agent as a subtask. The sub-agent runs in an **isolated context**, and upon completion, returns its results to the parent agent. This process is transparent to the user — no manual switching is required. [[REF-11]](#references) [[REF-12]](#references)

**Key characteristic:** Sub-agents are **agent-driven** — the parent agent autonomously decides when to invoke which sub-agent. This is a "delegation" model: a manager assigns tasks to reports, who deliver results upon completion.

To enable sub-agent invocation, the parent agent must:
1. Include `'agent'` in its `tools` list
2. Enumerate the allowed sub-agent names in the `agents` field

```yaml
# .github/agents/feature-builder.agent.md — Parent agent (orchestrator)
---
name: Feature Builder
description: Build features by researching first, then implementing
tools: ['agent']                         # Must include the 'agent' tool
agents: ['Researcher', 'Implementer']    # Whitelist: only these two may be invoked
---

You are a feature builder. For each task:
1. Use the Researcher agent to gather context and find relevant patterns
2. Create an implementation plan based on research findings
3. Use the Implementer agent to make the actual code changes
4. Review the results and iterate if needed
```

```yaml
# .github/agents/researcher.agent.md — Sub-agent (read-only research)
---
name: Researcher
description: Research codebase patterns and gather context
tools: ['codebase', 'fetch', 'usages']   # Read-only tools; no edit capability
---

Research thoroughly using read-only tools.
Return a summary of: relevant code patterns, file locations, and dependencies.
```

```yaml
# .github/agents/implementer.agent.md — Sub-agent (code implementation)
---
name: Implementer
description: Implement code changes based on provided context
tools: ['editFiles', 'terminalLastCommand']  # Write-capable tools
---

Implement changes based on the research and plan provided.
Follow project coding standards. Write tests for new functionality.
```

**Key constraints of sub-agents:** [[REF-11]](#references)
- ⚠️ **Sub-agents cannot invoke other sub-agents** (single-level depth only, preventing infinite recursion and privilege escalation)
- Sub-agents run in an isolated context — they do not see the parent agent's full conversation history, only the instructions passed to them
- Sub-agents can use **different models** — for example, the parent agent may use GPT-5.2 while the review sub-agent uses Claude Opus 4.5

### 4.4 Handoff vs Sub-agent: Core Comparison

These two mechanisms solve fundamentally different problems. Choosing the wrong one leads to unnatural workflows or reduced efficiency.

| Dimension | Handoff | Sub-agent |
|-----------|---------|-----------|
| **Trigger** | User clicks a button | Parent agent invokes programmatically |
| **Control** | User-driven (human-in-the-loop) | Agent-autonomous |
| **Context** | Shared conversation history (carries prior context) | Isolated context (clean new session) |
| **User experience** | Visible — user sees the agent switch | Transparent — user sees only the final result |
| **Depth limit** | Unlimited (users can switch back and forth) | Single level (sub-agents cannot invoke sub-agents) |
| **Model switching** | Each agent can specify a different model | Each sub-agent can specify a different model |
| **Best suited for** | Multi-stage pipelines requiring human review | Automated parallel/divide-and-conquer tasks |
| **Analogy** | Relay race (baton pass requires confirmation) | Task delegation (manager assigns work to reports) |

### 4.5 When to Use Handoffs vs Sub-agents

| Scenario | Recommended Mechanism | Rationale |
|----------|----------------------|-----------|
| Plan → Implement → Review pipeline | **Handoff** | Each stage's output requires human review before proceeding |
| Research + Implementation (auto-coordinated) | **Sub-agent** | Research is an auxiliary step that does not require user intervention |
| Automated code review feedback loop | **Sub-agent** | Parent writes code → sub-agent reviews → parent fixes → loop until pass |
| Parallel independent tasks (e.g., scanning separate modules) | **Sub-agent** | Isolated contexts prevent cross-contamination; results are aggregated |
| Cross-role collaboration requiring domain expertise | **Handoff** | User can provide feedback at each role's output stage |
| Concurrent security audit + performance testing | **Sub-agent** | Two independent tasks that can run in parallel; results are merged |

### 4.6 Advanced Pattern: Sub-agent Review Loop

One of the most powerful sub-agent applications is the **automated review loop** — the parent agent completes its work, invokes a review sub-agent to evaluate the results, and automatically iterates based on feedback, with no user intervention:

```yaml
# .github/agents/quality-coder.agent.md
---
name: Quality Coder
description: Write code with automatic quality review loop
tools: ['agent', 'editFiles', 'terminalLastCommand', 'search']
agents: ['CodeReviewer']
model: GPT-5.2
---

You are a quality-focused developer. For each coding task:
1. Implement the solution
2. Run the CodeReviewer agent to review your work
3. Read the review feedback carefully
4. Fix any issues the reviewer identified
5. Run the CodeReviewer again to verify fixes
6. Repeat until the reviewer gives a passing score (4/5 or higher)

Do NOT present the result to the user until the reviewer approves.
```

```yaml
# .github/agents/code-reviewer.agent.md
---
name: CodeReviewer
description: Review code for quality, security, and best practices
tools: ['codebase', 'search']     # Read-only — reviewers do not modify code
model: Claude Opus 4.5             # Deliberately uses a different model for review diversity
---

Review the provided code changes. Score on a 1-5 scale across:
- Security: No vulnerabilities, proper input validation
- Performance: No N+1 queries, efficient algorithms
- Maintainability: Clear naming, appropriate comments
- Test coverage: Key paths are tested

Return: overall score, list of issues, and suggested fixes.
```

> ⚠️ **Constraint reminder:** Because sub-agents cannot nest invocations, the CodeReviewer above cannot invoke further sub-agents. If your review pipeline requires multiple agent layers (e.g., CodeReviewer calling SecurityScanner), the top-level parent agent must invoke each one separately rather than having sub-agents call one another.

### 4.7 Cross-Reference: Claude Code Sub-agents

GitHub Copilot's sub-agent design draws inspiration from Claude Code, but notable differences exist: [[REF-10]](#references) [[REF-22]](#references)

| Dimension | Claude Code Sub-agent | GitHub Copilot Sub-agent |
|-----------|----------------------|-------------------------|
| **Definition format** | Markdown + YAML frontmatter (in `~/.claude/agents/`) | `.agent.md` files (in `.github/agents/`) |
| **Activation** | `/agents` command or manual file creation | Include `'agent'` in parent's `tools`; enumerate whitelist in `agents` |
| **Configurable fields** | prompt, tools, disallowedTools, model, permissionMode, mcpServers, hooks, maxTurns, skills, memory | name, description, tools, model, agents, handoffs |
| **Skill injection** | `skills` field injects skill content at startup | Indirect reference via `.agent.md` body |
| **Hook integration** | `PreToolUse` hooks can be defined within a sub-agent | No per-agent hooks (relies on global hook configuration) |
| **Permission model** | `bypassPermissions` can skip all permission checks | Default-deny; authorized via Permission Handler |
| **Nesting limit** | Sub-agents cannot spawn sub-agents | Same constraint — single-level depth only |
| **Parallel execution** | Supported (multiple sub-agents can run concurrently in the background) | Supported (experimental) |

---

## Chapter 5: Hooks

Hooks are **deterministic code** that executes at specific points in the agent execution lifecycle. Unlike Instructions, Skills, and Agents, hooks are **not prompts for the LLM** — they are scripts that run unconditionally when their trigger event fires. [[REF-15]](#references) [[REF-17]](#references)

### 5.1 Hook Types

| Hook Type | Trigger | Typical Use Cases |
|-----------|---------|-------------------|
| `PreToolUse` | Before a tool invocation | Permission checks, parameter validation, blocking dangerous operations |
| `PostToolUse` | After a tool invocation | Lint/format, logging |
| `PermissionRequest` | When a permission dialog appears | Auto-approve/deny |
| `SessionStart` | Session begins | Environment initialization, context loading |
| `SessionEnd` | Session ends | Notifications, log aggregation |
| `OnError` | On error | Automatic retry, graceful degradation |

### 5.2 Claude Code vs GitHub Copilot Hook Differences

| Dimension | Claude Code | GitHub Copilot |
|-----------|------------|----------------|
| **Granularity** | Tool-level (intercept before/after each tool call) | Event-level (git operations, session lifecycle) |
| **Configuration** | YAML frontmatter with matcher + command | `.vscode/settings.json` |
| **Interception mechanism** | Exit code 2 = block the operation | `permissions.allowedCommands` |
| **Best suited for** | Security sandboxing, fine-grained permission control | CI/CD and development workflow automation |

> **ℹ️ Token impact:** Hooks execute at the code level and bypass the LLM entirely, so they **consume zero tokens**. This is their fundamental distinction from Instructions and Skills.

---

## Chapter 6: Where Does the Workflow Belong?

**This is the most common architectural anti-pattern in the community.** Many engineers define workflows and agent dispatch logic inside `copilot-instructions.md`. This is not a best practice.

### 6.1 Why Workflows Do Not Belong in copilot-instructions.md

1. **Token waste:** `copilot-instructions.md` is always-on. When a user asks a simple question, the workflow content still occupies the context window.

2. **Separation-of-concerns violation:** Instructions are *standards*, not *runbooks*. Complex orchestration logic should not be intermixed with code style rules. A useful mental model: Instructions = the agent's "personality"; Prompts = the specific tasks you want it to perform.

3. **Unreliable execution:** The non-deterministic nature of LLMs means that the more complex the procedural instruction, the more likely the agent is to deviate. Handoffs, by contrast, are a deterministic UI mechanism.

### 6.2 Correct Placement Reference

| Workflow Type | Correct Location | Rationale |
|--------------|-----------------|-----------|
| Simple linear operational flows (build → test → lint) | `AGENTS.md` | Operational guidance for autonomous coding agents |
| Multi-stage pipelines requiring human review (Plan → Implement → Review) | `.agent.md` + `handoffs` | Handoffs are a deterministic UI mechanism with human gating at each stage |
| Automated divide-and-conquer / parallel tasks (Research + Implement) | `.agent.md` + `agents` (sub-agent) | Parent agent delegates programmatically; no user intervention required |
| Task-specific detailed procedures (e.g., debugging CI) | `SKILL.md` | Loaded on-demand; does not consume tokens in unrelated scenarios |
| User-triggered repeatable tasks | `.prompt.md` | Explicitly invoked (/command); not always-on |
| Global coding standards | `copilot-instructions.md` | **The only content that should be always-on** |

### 6.3 Layered Model Overview

```
┌──────────────────────────────────────────────────────────────┐
│  copilot-instructions.md                                      │
│  ✅ Coding standards, naming conventions, tech stack prefs     │
│  ✅ "Use TypeScript strict mode"                               │
│  ✅ "Prefer pnpm over npm"                                     │
│  ❌ Do NOT include workflow orchestration logic                 │
│  ❌ Do NOT include "when X happens, call agent Y"              │
├──────────────────────────────────────────────────────────────┤
│  AGENTS.md                                                    │
│  ✅ Build/test/deploy steps for autonomous agent operation     │
│  ✅ "Run tests before committing"                              │
│  ✅ Simple linear operational procedures                       │
├──────────────────────────────────────────────────────────────┤
│  .agent.md (Custom Agents)                                    │
│  ✅ Handoff: multi-stage pipelines with human review           │
│  ✅ Sub-agent: automated divide-and-conquer / review loops     │
│  ✅ "Research → Plan → Implement → Review" orchestration       │
├──────────────────────────────────────────────────────────────┤
│  SKILL.md (Agent Skills)                                      │
│  ✅ Task-specific detailed steps + scripts                     │
│  ✅ "How to debug CI", "How to run DB migrations"              │
├──────────────────────────────────────────────────────────────┤
│  .prompt.md (Prompt Files)                                    │
│  ✅ User-triggered task workflows via /command                 │
│  ✅ "/plan-feature", "/generate-endpoint"                      │
└──────────────────────────────────────────────────────────────┘
```

> **General rule:** If the content is needed in *nearly every interaction* → Instructions. If it is needed *only for specific tasks* → Skill or Prompt. If it involves *inter-agent collaboration* → `.agent.md`, choosing Handoff (human review required) or Sub-agent (fully automated) accordingly.

---

## Chapter 7: Complete Project Structure Example

Below is the recommended directory structure for a full-stack project (TypeScript frontend, Python backend, GitHub Actions CI/CD):

```
your-project/
├── .github/
│   ├── copilot-instructions.md          ← Layer 1: Global standards (5–15 rules)
│   ├── instructions/
│   │   ├── typescript.instructions.md   ← Layer 2: TS file rules (applyTo: "**/*.ts")
│   │   ├── python.instructions.md       ← Layer 2: Python file rules (applyTo: "**/*.py")
│   │   └── security.instructions.md     ← Layer 2: Security-related files
│   ├── agents/
│   │   ├── planner.agent.md             ← Planning role (handoff → Implementer)
│   │   ├── implementer.agent.md         ← Implementation role (handoff → Reviewer)
│   │   └── reviewer.agent.md            ← Review role
│   ├── skills/
│   │   ├── ci-debugging/
│   │   │   ├── SKILL.md                 ← CI debugging skill
│   │   │   └── references/
│   │   │       └── common-errors.md
│   │   └── db-migration/
│   │       ├── SKILL.md                 ← DB migration skill
│   │       └── scripts/
│   │           └── generate-migration.sh
│   └── prompts/
│       ├── plan-feature.prompt.md       ← /plan-feature slash command
│       └── generate-endpoint.prompt.md  ← /generate-endpoint
├── AGENTS.md                            ← Layer 3: Agent operational procedures
├── CLAUDE.md                            ← Claude-specific guidance
└── src/
```

### File Content Examples

**`.github/copilot-instructions.md`** — Concise, global, always-on:

```markdown
# Project Standards
- Use TypeScript strict mode for all .ts/.tsx files
- Use Python 3.12+ with type hints for all .py files
- Prefer pnpm over npm for package management
- All API endpoints must include OpenAPI annotations
- Write unit tests for every new function (pytest / vitest)
- Follow conventional commits format
- Never commit secrets or API keys
```

**`AGENTS.md`** — Coding agent operational guidance:

```markdown
# Build & Test
- Frontend: `pnpm install && pnpm build && pnpm test`
- Backend: `pip install -e . && pytest`
- Lint: `pnpm lint:fix && ruff check --fix`

# Before Committing
1. Run all tests and ensure they pass
2. Run lint and fix any issues
3. Use conventional commit format
```

---

## Chapter 8: Token Cost Strategy

Understanding each component's token consumption pattern is critical to sound architectural decisions.

### 8.1 Token Consumption by Component

| Component | Loading Mechanism | Token Cost per Invocation | Optimization Guidance |
|-----------|------------------|--------------------------|----------------------|
| `copilot-instructions.md` | Always-on | 200–500 tokens (recommended) | Limit to 5–15 rules |
| Path-specific `.instructions.md` | Conditional (glob match) | 100–300 tokens/file | Split by language/framework |
| `AGENTS.md` | During agent operation | 200–500 tokens | Focus on build/test commands |
| Skill metadata | Always-on | ~50–100 tokens/skill | Write precise descriptions |
| Skill body | On-demand | < 500 tokens (recommended) | Move detailed content to `references/` |
| Skill references | On-demand | < 1,000 tokens/file | Split into small files |
| Custom Agent prompt | Always-on once selected | 30,000 character limit | Shorter is better |
| Sub-agent invocation | On-demand (when parent delegates) | Isolated context; does not accumulate parent history | Split research vs implementation; keep each concise |
| **Hooks** | **Event-triggered** | **0 tokens (code-level execution)** | **No limit** |

### 8.2 Cost Spectrum

```
Low cost ──────────────────────────────────────────── High cost

  Hooks        Path-Specific     Repo-Wide       Skills        Agent Prompt
  (0 tokens)   Instructions     Instructions    (on-demand)    (always-on
               (conditional)    (always-on)     (loaded on      when selected)
                                                 match)
```

### 8.3 Strategic Principles

| Principle | Explanation |
|-----------|-------------|
| **Never always-on what can be loaded on-demand** | Skill > Instructions (for non-essential detailed guidance) |
| **Never use Instructions when Hooks (zero tokens) suffice** | Example: "Lint before every commit" → use a Hook, not an Instruction |
| **Never put in Instructions what belongs in a Skill (on-demand)** | Task-specific detailed procedures belong in Skills |
| **Write precise Skill metadata** | Description quality directly affects both trigger accuracy and token efficiency |
| **Keep global Instructions stable** | Avoid frequent changes that invalidate caching |

---

## Chapter 9: Security Best Practices

| Layer | Risk | Mitigation |
|-------|------|------------|
| **Instructions** | Prompt injection: malicious content may be injected into instruction files | Version control + code review for all instruction changes |
| **Skills** | Third-party skills may contain malicious scripts | Audit all shared skills before use; test in sandboxed environments |
| **Custom Agents** | Over-permissioning: overly broad tool whitelists | **Principle of least privilege**: grant only the necessary tools |
| **Hooks** | Security of hook scripts themselves | Audit hook scripts; use simple, deterministic logic |
| **SDK** | Privilege escalation: default tools may be too powerful | Use **Permission Handlers** to explicitly approve each dangerous operation |
| **Organization** | Inconsistent standards, uncontrolled permissions | Organization-level Instructions + MCP permission controls |

### Security Design Principles

1. **Default deny:** In the SDK, agents cannot execute shell commands, read/write files, or fetch URLs by default. Developers must explicitly approve operations via Permission Handlers.

2. **Least privilege:** A custom agent's `tools` field should list only the tools required for its role. Reviewers do not need `edit`; planners do not need `shell`.

3. **Container isolation:** Agents with shell or file permissions should run inside Docker containers or Dev Containers.

4. **Audit trail:** Use `PostToolUse` hooks to log all tool invocations for post-hoc auditing.

---

## Appendix A: Copilot SDK Integration Patterns

The Copilot SDK wraps the Copilot CLI's agent runtime as a programmatically invocable library. The following sections demonstrate how to correctly integrate each component within the SDK.

### A.1 Architecture Overview

The SDK communicates with Copilot CLI (server mode) via JSON-RPC. Your application calls CLI capabilities through the SDK client:

```
Your Application  →  SDK Client  →  JSON-RPC  →  Copilot CLI (Server Mode)
                     |                           |
                     |— Custom Tools              |— Built-in Tools (fs/git/shell)
                     |— Permission Handler        |— MCP Servers
                     |— Custom Agents             |— Skills (auto-discovered)
                     └— Instructions              └— AGENTS.md (auto-discovered)
```

The SDK automatically manages the CLI process lifecycle. Currently supported runtimes: Node.js, Python, Go, and .NET.

---

### A.2 Three Approaches for Injecting Instructions via the SDK

| Approach | Code Example | Use Case |
|----------|-------------|----------|
| **Session parameter** | `session = createSession({ instructions: "..." })` | Programmatic control, no file dependency |
| **Filesystem auto-discovery** | CLI auto-scans `copilot-instructions.md`, `AGENTS.md` | Projects with existing repo-level configuration |
| **Environment variable** | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS=dir1,dir2` | Shared instructions across multiple projects |

#### Example: Session-Level Injection

```typescript
const session = await client.createSession({
    model: "claude-sonnet-4.5",
    instructions: `You are a code analysis specialist.
Follow these standards:
- Use TypeScript strict mode
- All functions must have JSDoc comments
- Prefer functional programming patterns`,
});
```

#### Example: Filesystem Auto-Discovery

```python
# The SDK delegates to Copilot CLI under the hood.
# The CLI automatically scans the working directory for:
#   - .github/copilot-instructions.md
#   - AGENTS.md
#   - .github/instructions/*.instructions.md
#   - CLAUDE.md (when using a Claude model)

session = await client.create_session({
    "model": "claude-sonnet-4.5",
    "working_directory": "/path/to/your/repo"  # CLI scans from here
})
```

---

### A.3 Using Skills in the SDK

The SDK supports specifying skill directories when creating a session:

```python
session = await client.create_session({
    "model": "claude-sonnet-4.5",
    "skill_directories": [
        "./.copilot_skills/pr-analyzer/SKILL.md",
        "./.copilot_skills/code-review/SKILL.md"
    ]
})
```

You can also **dynamically select** skills based on task type:

```python
# Dynamic Skill Selection Pattern
skills = []
if task_type == "code_review":
    skills.append("./.copilot_skills/code-review/SKILL.md")
elif task_type == "migration":
    skills.append("./.copilot_skills/migration/SKILL.md")
elif task_type == "ci_debugging":
    skills.append("./.copilot_skills/ci-debugging/SKILL.md")

session = await client.create_session({
    "model": "claude-sonnet-4.5",
    "skill_directories": skills
})
```

---

### A.4 Defining Custom Agents in the SDK

```typescript
// TypeScript — Register a custom agent within a session
const session = await client.createSession({
    customAgents: [{
        name: "pr-reviewer",
        displayName: "PR Reviewer",
        description: "Reviews pull requests for best practices",
        prompt: `You are an expert code reviewer.
Focus on:
- Security vulnerabilities
- Performance issues  
- Code style consistency
- Test coverage gaps`
    }]
});
```

---

### A.5 Hooks in the SDK: The Permission Handler

The SDK's primary hook mechanism is the **Permission Handler**. By default, agents **cannot** execute shell commands, read/write files, or fetch URLs — each operation must be explicitly approved via the handler:

```python
# Python — Permission Handler Pattern
def permission_handler(request, context):
    # Safe operations: always allow
    if request["kind"] == "read":
        return {"kind": "approved"}

    # Shell commands: allow only specific commands
    if request["kind"] == "shell":
        cmd = context.get("command", "")
        # Allowlist strategy
        allowed_prefixes = ["npm test", "pnpm lint", "pytest", "git status"]
        if any(cmd.startswith(prefix) for prefix in allowed_prefixes):
            return {"kind": "approved"}
        # Blocklist strategy
        if "rm -rf" in cmd or "sudo" in cmd:
            return {"kind": "denied"}

    # Default: deny
    return {"kind": "denied-interactively-by-user"}
```

```csharp
// C# — Permission Handler Pattern
SessionConfig sessionConfig = new() {
    OnPermissionRequest = async (request, invocation) => {
        if (request.Kind == "shell" && invocation.Command.Contains("rm -rf"))
            return new PermissionRequestResult { Kind = "denied" };
        if (request.Kind == "read")
            return new PermissionRequestResult { Kind = "approved" };
        return new PermissionRequestResult { Kind = "approved" };
    }
};
```

---

### A.6 MCP Server Integration

The SDK supports simultaneous connections to local and remote MCP servers:

```typescript
const session = await client.createSession({
    mcpServers: {
        // Local stdio server
        filesystem: {
            type: "stdio",
            command: "npx",
            args: ["-y", "@modelcontextprotocol/server-filesystem", "."]
        },
        // Remote HTTP server
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/"
        },
        // Documentation knowledge base
        "microsoft-learn": {
            type: "http",
            url: "https://learn.microsoft.com/api/mcp"
        }
    }
});
```

---

### A.7 End-to-End Example: Automated PR Analysis System

The following production-grade example combines all components, executed daily via GitHub Actions:

```python
# analyze_prs.py — End-to-end integration example

from copilot import CopilotClient

# ── Permission Handler: read-only operations only ──
def read_only_handler(request, context):
    if request["kind"] in ["read", "search"]:
        return {"kind": "approved"}
    if request["kind"] == "shell":
        cmd = context.get("command", "")
        if cmd.startswith(("git log", "git diff", "git show")):
            return {"kind": "approved"}
    return {"kind": "denied"}


async def main():
    client = CopilotClient()
    await client.start()

    # ── Create session: assemble all components ──
    session = await client.create_session({
        # 1️⃣ Instructions: passed directly as a session parameter
        "model": "claude-sonnet-4.5",
        "instructions": """You are a code analysis specialist.
Follow these rules:
- Focus on security, performance, and maintainability
- Rate each PR on a 1-5 scale
- Provide actionable suggestions""",

        # 2️⃣ Skills: specify skill directories; loaded on-demand
        "skill_directories": [
            "./.copilot_skills/pr-analyzer/SKILL.md"
        ],

        # 3️⃣ MCP: connect to the GitHub API
        "mcp_servers": {
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/"
            }
        },

        # 4️⃣ Permission Handler: restrict to read-only operations
        "on_permission_request": read_only_handler
    })

    # 5️⃣ Execute the task
    result = await session.send_and_wait({
        "prompt": "Analyze all PRs merged yesterday. For each PR, provide: "
                  "1) Summary of changes "
                  "2) Security assessment "
                  "3) Performance impact "
                  "4) Quality score (1-5)"
    })

    print(result.content)
    await client.stop()
```

Corresponding GitHub Actions workflow:

```yaml
# .github/workflows/daily-pr-analysis.yml
name: Daily PR Analysis
on:
  schedule:
    - cron: '0 9 * * 1-5'  # Weekdays at 9:00 AM
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install copilot-sdk
      - run: python analyze_prs.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### A.8 SDK Integration Mechanism Reference

| SDK Mechanism | IDE Counterpart | Injection Method | Token Impact |
|--------------|-----------------|-----------------|-------------|
| `session.instructions` | `copilot-instructions.md` | Included in every invocation | **Consumed every time** |
| `session.skill_directories` | `.github/skills/` | CLI auto-discovers and loads on match | **Consumed on-demand** |
| `session.customAgents` | `.github/agents/*.agent.md` | Registered at session creation | **Consumed once selected** |
| `session.customAgents[].agents` | Sub-agent whitelist | Invoked in isolated context when parent delegates | **Independent consumption (does not accumulate on parent session)** |
| `session.on_permission_request` | Hooks (`PreToolUse`) | Intercepts before tool invocations | **0 tokens** |
| `session.mcp_servers` | MCP server configuration | Connected at session creation | Tool descriptions consume tokens |
| Filesystem auto-discovery | `AGENTS.md`, `.instructions.md` | CLI scans the working directory | Same behavior as IDE |

---

### A.9 Multi-Agent Orchestration via Agent Framework

The Microsoft Agent Framework enables composing Copilot agents with agents from other providers:

```python
# Sequential Pipeline: multi-agent collaboration
from agent_framework.github import GitHubCopilotAgent
from agent_framework.azure import AzureOpenAIAgent

# Agent 1: Draft documentation (Azure OpenAI)
writer = AzureOpenAIAgent(
    instructions="Write clear, concise technical documentation."
)

# Agent 2: Copilot reviews for technical accuracy
reviewer = GitHubCopilotAgent(
    default_options={
        "instructions": "Review for technical accuracy against the codebase.",
        "tools": [search_codebase_tool],
        "on_permission_request": read_only_handler
    }
)

# Sequential Pipeline
draft = await writer.run("Write release notes for v2.0")
reviewed = await reviewer.run(f"Review this for accuracy: {draft}")
```

GitHub Copilot agents implement the same `AIAgent` interface as other agent types, enabling free composition across sequential, concurrent, handoff, and group chat workflows.

---

> **SDK integration core principle:** Instructions provide foundational context, Skills provide on-demand knowledge, Permission Handlers enforce safety rules, MCP supplies external tools, and Sub-agents enable automated divide-and-conquer. The SDK lets you assemble all of these within a single session to build truly agentic applications.

## References

The content of this guide is based on the following official documentation and sources, organized by chapter:

### Instructions (Chapter 2)

- **[REF-1]** GitHub Docs — *Adding repository custom instructions for GitHub Copilot*
  https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
  Covers repository-wide, path-specific, and agent instruction types, along with precedence rules (Personal > Repository > Organization).

- **[REF-2]** GitHub Docs — *Adding personal custom instructions for GitHub Copilot*
  https://docs.github.com/en/copilot/customizing-copilot/adding-personal-custom-instructions-for-github-copilot
  Configuration of personal instructions.

- **[REF-3]** GitHub Docs — *Configure custom instructions for GitHub Copilot*
  https://docs.github.com/en/copilot/how-tos/configure-custom-instructions
  Overall instructions configuration guide, including organization-level settings.

- **[REF-4]** GitHub Docs — *Adding custom instructions for GitHub Copilot CLI*
  https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions
  CLI-specific support for AGENTS.md, CLAUDE.md, and GEMINI.md files.

- **[REF-5]** GitHub Docs — *Custom agents configuration*
  https://docs.github.com/en/copilot/reference/custom-agents-configuration
  Complete property reference for agent profile YAML frontmatter (description, tools, model, handoffs, etc.) and the 30,000-character prompt limit.

### Agent Skills (Chapter 3)

- **[REF-6]** GitHub Docs — *About Agent Skills*
  https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
  Conceptual overview of Agent Skills as an open standard, including the SKILL.md file format (YAML frontmatter + Markdown body + references/ directory structure).

- **[REF-7]** VS Code Docs — *Use Agent Skills in VS Code*
  https://code.visualstudio.com/docs/copilot/customization/agent-skills
  Detailed explanation of the three-tier progressive disclosure model (metadata always-on → body on match → references on demand), along with automatic triggering and manual `/` invocation mechanisms.

### Custom Agents (Chapter 4)

- **[REF-8]** GitHub Docs — *About custom agents*
  https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents
  Conceptual definition of custom agents: agent profiles (.agent.md), YAML frontmatter configuration, and repository / organization / enterprise scoping levels.

- **[REF-9]** GitHub Docs — *Creating custom agents for Copilot coding agent*
  https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents
  How to create custom agents with complete configuration examples.

- **[REF-10]** VS Code Docs — *Custom agents in VS Code*
  https://code.visualstudio.com/docs/copilot/customization/custom-agents
  Detailed handoff mechanism (label, agent, prompt, send fields), `agents` whitelist, enabling sub-agent invocation via `tools: ['agent']`, and the complete Feature Builder example.

### Sub-agents (Sections 4.3–4.7)

- **[REF-11]** VS Code Docs — *Subagents in Visual Studio Code*
  https://code.visualstudio.com/docs/copilot/agents/subagents
  The definitive sub-agent reference: isolated context, synchronous blocking behavior, parallel execution, combining with custom agents, and token optimization benefits.

- **[REF-12]** VS Code Blog — *A Unified Experience for all Coding Agents* (November 2025)
  https://code.visualstudio.com/blogs/2025/11/03/unified-agent-experience
  Introduction of the `runSubagent` tool and the context isolation principle for sub-agents.

- **[REF-13]** VS Code Blog — *Your Home for Multi-Agent Development* (February 2026)
  https://code.visualstudio.com/blogs/2026/02/05/multi-agent-development
  VS Code 1.109 multi-agent development environment and the role of sub-agents across local, background, and cloud agents.

- **[REF-14]** GitHub Docs — *Creating and using custom agents for GitHub Copilot CLI*
  https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
  How custom agents in the CLI execute work via subagents.

### Hooks (Chapter 5)

- **[REF-15]** GitHub Docs — *About hooks*
  https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks
  Hook type overview: sessionStart, sessionEnd, userPromptSubmitted, preToolUse, postToolUse. JSON configuration format.

- **[REF-16]** GitHub Docs — *Using hooks with GitHub Copilot agents*
  https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks
  Hook implementation guide and troubleshooting.

- **[REF-17]** GitHub Docs — *Hooks configuration*
  https://docs.github.com/en/copilot/reference/hooks-configuration
  Complete hooks configuration reference, including input/output JSON formats and advanced patterns for each hook type.

- **[REF-18]** VS Code Docs — *Customize AI in Visual Studio Code* (Hooks section)
  https://code.visualstudio.com/docs/copilot/customization/overview
  Hooks in VS Code: deterministic, code-driven automation that runs regardless of prompt content.

### Overall Architecture and Workflow Design (Chapters 1, 6, 7)

- **[REF-19]** VS Code Docs — *Customize AI in Visual Studio Code*
  https://code.visualstudio.com/docs/copilot/customization/overview
  Complete customization feature overview: custom instructions, prompt files, custom agents, agent skills, MCP, and hooks. Includes the "Prompt files vs custom agents" usage guidance.

- **[REF-20]** VS Code Docs — *Set up a context engineering flow in VS Code*
  https://code.visualstudio.com/docs/copilot/guides/context-engineering-guide
  Context engineering workflow guide covering the instructions → planning agent → implementation layered design.

- **[REF-21]** GitHub Docs — *Best practices for using GitHub Copilot to work on tasks*
  https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/coding-agent/get-the-best-results
  Best practices for copilot-instructions.md, and integration guidance for custom agents and MCP.

### Claude Code Sub-agent Comparison (Section 4.7)

- **[REF-22]** Claude Code Docs — *Create custom subagents*
  https://code.claude.com/docs/en/sub-agents
  Complete Claude Code sub-agent documentation: YAML frontmatter configuration (prompt, tools, disallowedTools, model, permissionMode, mcpServers, hooks, maxTurns, skills, memory), nesting constraints, and PreToolUse hook integration.

---

*— END —*
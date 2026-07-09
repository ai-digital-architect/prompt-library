Below is a comprehensive markdown design document that fits the **software factory / harness** into the monorepo architecture.

# Agentic Engineering Platform Software Factory

## Harness Architecture for Building, Modifying, Verifying, and Evolving the Agentic Engineering Platform Monorepo

---

# 1. Vision

The vision is to create an **agentic software factory** that can continuously build, modify, bug fix, validate, and evolve the **Agentic Engineering Platform** itself.

The platform being built is already agentic: it contains a CLI, MCP server, plugin runtime, domain-specific GitHub Copilot plugins, Claude Code plugins, schemas, evals, and verification pipelines. The next architectural step is to create a **repository-native harness** that uses Claude Code and/or GitHub Copilot customizations to engineer that platform in a governed, repeatable, and verifiable way.

The harness should make the repository behave like a productized engineering factory:

```text
Intent → Specification → Plan → Worktree → Agent Execution → Verification → Review → Memory Update → Merge
```

The goal is not just to use AI coding tools casually. The goal is to encode the engineering method of the platform into the repository itself so that developers and agents follow the same standards every time.

The software factory should support:

* New feature development
* Plugin creation
* CLI command creation
* MCP tool creation
* Bug fixes
* Schema evolution
* Eval creation
* Security hardening
* Release preparation
* Documentation updates
* Knowledge graph updates
* Regression verification
* Enterprise standards compliance

Claude Code supports extension surfaces such as skills, subagents, hooks, MCP, plugins, permissions, and sessions through its SDK and product capabilities. ([Claude Platform Docs][1]) GitHub Copilot supports repository custom instructions, skills, custom agents, hooks, prompt files, and plugin-based customization. ([GitHub Docs][2]) The software factory should use those extension surfaces as the **outer loop** around the monorepo.

---

# 2. Problem Statement

The Agentic Engineering Platform is a multi-surface product. It includes:

```text
Core product:
- CLI
- MCP server
- shared schemas
- analyzers
- reporters
- policy engine

Assistant distribution:
- GitHub Copilot plugins
- Claude Code plugins
- domain-specific plugin packs
- full-suite plugin

Governance:
- plugin catalog
- compatibility matrix
- evals
- CI/CD
- release workflows
- security scans
- artifact signing
```

As the platform grows, traditional manual engineering will create several risks:

1. **Plugin drift**
   Copilot and Claude Code plugins may diverge from each other.

2. **CLI/MCP contract drift**
   The CLI commands, MCP tools, JSON schemas, and plugin skills may stop matching.

3. **Bootstrap inconsistency**
   Domain plugins may check and install the CLI differently.

4. **Knowledge loss**
   Design decisions, failures, migration history, and procedural knowledge may live only in chat history or tribal memory.

5. **Weak verification**
   Agents may generate code without proving that the platform still works.

6. **Overloaded context**
   Coding assistants can lose track of repository-specific architecture, conventions, and prior decisions.

7. **Inconsistent implementation patterns**
   Different developers or agents may implement new plugins, tools, or analyzers differently.

The solution is to add a **repository-native software factory layer** that governs how AI-assisted engineering occurs.

---

# 3. Design Principle

The key architectural principle is:

```text
The platform builds agentic tools.
The software factory builds the platform.
The knowledge graph remembers how and why the platform evolves.
The verification system proves that changes are safe.
```

This creates three nested layers:

```text
Layer 1 — Agentic Engineering Platform
The product developers use.

Layer 2 — Software Factory Harness
The agentic engineering system that builds the product.

Layer 3 — Repository Knowledge Graph and Memory
The persistent brain of the factory.
```

---

# 4. Target Architecture

```text
agentic-engineering-platform/
├── cli/
├── mcp-server/
├── plugin-runtime/
├── plugin-definitions/
├── plugins/
│   ├── copilot/
│   └── claude-code/
├── plugin-catalog/
├── schemas/
├── evals/
├── docs/
├── examples/
├── tools/
│
├── .claude/                     # Claude Code software factory harness
├── .github/                     # GitHub Copilot software factory harness
├── .factory/                    # assistant-neutral factory orchestration
├── .knowledge/                  # repository knowledge graph and memory
├── .specs/                      # specification kit / feature specs
├── .verification/               # deterministic verification harness
└── .workflows/                  # productized engineering workflows
```

The key addition is this:

```text
Repository product code
        +
Repository software factory
        +
Repository knowledge graph
        +
Repository verification substrate
```

The repository is no longer just source code. It becomes an **agent-operable engineering system**.

---

# 5. Expanded Monorepo Layout

```text
agentic-engineering-platform/
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── VERSION
│
├── cli/
│   ├── src/
│   │   └── agentic_tool/
│   │       ├── commands/
│   │       ├── analyzers/
│   │       ├── graph/
│   │       ├── ast/
│   │       ├── reporters/
│   │       ├── policy/
│   │       └── tool_contracts/
│   └── tests/
│
├── mcp-server/
│   ├── src/
│   │   └── agentic_tool_mcp/
│   │       ├── server.py
│   │       ├── tools/
│   │       ├── schemas/
│   │       └── adapters/
│   └── tests/
│
├── plugin-runtime/
│   ├── scripts/
│   │   ├── bootstrap-cli.sh
│   │   ├── check-cli.sh
│   │   ├── install-cli.sh
│   │   ├── invoke-cli.sh
│   │   ├── mcp-wrapper.sh
│   │   └── verify-cli-integrity.sh
│   ├── config/
│   └── templates/
│
├── plugin-definitions/
│   ├── architecture.yaml
│   ├── security.yaml
│   ├── resiliency.yaml
│   ├── standards-compliance.yaml
│   ├── testing.yaml
│   ├── observability.yaml
│   └── full-suite.yaml
│
├── plugins/
│   ├── copilot/
│   │   ├── architecture/
│   │   ├── security/
│   │   ├── resiliency/
│   │   └── full-suite/
│   └── claude-code/
│       ├── architecture/
│       ├── security/
│       ├── resiliency/
│       └── full-suite/
│
├── schemas/
├── evals/
├── docs/
├── examples/
├── tools/
│
├── .claude/
│   ├── CLAUDE.md
│   ├── settings.json
│   ├── agents/
│   ├── skills/
│   ├── commands/
│   ├── hooks/
│   ├── mcp.json
│   └── speckit/
│
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   ├── prompts/
│   ├── agents/
│   ├── skills/
│   ├── hooks/
│   └── workflows/
│
├── .factory/
│   ├── README.md
│   ├── factory-manifest.yaml
│   ├── workflow-registry.yaml
│   ├── agent-registry.yaml
│   ├── skill-registry.yaml
│   ├── tool-contract-registry.yaml
│   ├── verification-policy.yaml
│   ├── release-policy.yaml
│   ├── worktree-policy.yaml
│   └── templates/
│
├── .knowledge/
│   ├── README.md
│   ├── okf/
│   ├── graph/
│   ├── memory/
│   │   ├── semantic/
│   │   ├── episodic/
│   │   ├── procedural/
│   │   └── working/
│   ├── decisions/
│   ├── domain/
│   ├── components/
│   ├── contracts/
│   ├── patterns/
│   ├── glossary/
│   └── indexes/
│
├── .specs/
│   ├── README.md
│   ├── templates/
│   ├── active/
│   ├── accepted/
│   ├── implemented/
│   ├── rejected/
│   └── archived/
│
├── .verification/
│   ├── README.md
│   ├── gates/
│   ├── scripts/
│   ├── policies/
│   ├── evals/
│   ├── fixtures/
│   ├── snapshots/
│   └── reports/
│
└── .workflows/
    ├── add-cli-command.md
    ├── add-mcp-tool.md
    ├── add-domain-plugin.md
    ├── add-skill.md
    ├── fix-bug.md
    ├── evolve-schema.md
    ├── update-bootstrap-runtime.md
    ├── release-platform.md
    └── update-knowledge-graph.md
```

---

# 6. How the Software Factory Fits Into the Architecture

The software factory is not a replacement for the CLI, MCP server, or plugins. It is the **engineering control plane** for building them.

```text
┌────────────────────────────────────────────────────────────┐
│ Developer Intent                                            │
│ "Add a security plugin capability for threat modeling"      │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Software Factory Harness                                    │
│ Claude Code / Copilot custom agents, skills, hooks, specs   │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Repository Knowledge Graph                                  │
│ semantic memory, episodic memory, procedural memory         │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Specification Kit                                            │
│ intent, requirements, contracts, acceptance criteria         │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Agent Execution                                              │
│ planner, implementer, tester, security reviewer, docs agent │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Verification Harness                                         │
│ tests, evals, schemas, CLI/MCP/plugin compatibility gates    │
└───────────────────────────────┬────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│ Product Change                                                │
│ CLI, MCP, plugin, docs, schemas, evals, catalog updated       │
└────────────────────────────────────────────────────────────┘
```

---

# 7. Claude Code Harness

Claude Code should be the deeper local software factory surface because it is strong for repository-local workflows, file editing, shell execution, hooks, MCP, and subagent orchestration. Claude Code can read and edit code, run commands, and integrate with tools, and its extension layer includes CLAUDE.md, skills, subagents, hooks, MCP, and plugins. ([Claude Platform Docs][3])

## 7.1 `.claude/` Structure

```text
.claude/
├── CLAUDE.md
├── settings.json
├── mcp.json
│
├── agents/
│   ├── platform-architect.md
│   ├── spec-owner.md
│   ├── cli-engineer.md
│   ├── mcp-tool-engineer.md
│   ├── plugin-engineer.md
│   ├── claude-plugin-engineer.md
│   ├── copilot-plugin-engineer.md
│   ├── bootstrap-runtime-engineer.md
│   ├── verification-engineer.md
│   ├── security-engineer.md
│   ├── release-engineer.md
│   ├── documentation-engineer.md
│   └── knowledge-curator.md
│
├── skills/
│   ├── add-cli-command/
│   │   ├── SKILL.md
│   │   └── checklist.md
│   ├── add-mcp-tool/
│   │   ├── SKILL.md
│   │   └── tool-contract-template.json
│   ├── add-domain-plugin/
│   │   ├── SKILL.md
│   │   └── plugin-definition-template.yaml
│   ├── update-bootstrap-runtime/
│   │   ├── SKILL.md
│   │   └── bootstrap-checklist.md
│   ├── generate-evals/
│   │   ├── SKILL.md
│   │   └── eval-template.md
│   ├── update-knowledge-graph/
│   │   ├── SKILL.md
│   │   └── memory-update-rules.md
│   └── release-platform/
│       ├── SKILL.md
│       └── release-checklist.md
│
├── commands/
│   ├── factory-plan.md
│   ├── factory-implement.md
│   ├── factory-verify.md
│   ├── factory-review.md
│   ├── factory-memory-update.md
│   └── factory-release.md
│
├── hooks/
│   ├── hooks.json
│   ├── pre-tool-use-guard.sh
│   ├── post-edit-verify.sh
│   ├── stop-verification.sh
│   ├── memory-update-suggester.sh
│   └── command-allowlist.sh
│
└── speckit/
    ├── templates/
    │   ├── feature-spec.md
    │   ├── bugfix-spec.md
    │   ├── plugin-spec.md
    │   ├── cli-command-spec.md
    │   ├── mcp-tool-spec.md
    │   └── verification-spec.md
    ├── workflows/
    │   ├── new-feature.md
    │   ├── bug-fix.md
    │   ├── plugin-change.md
    │   ├── schema-change.md
    │   └── release-change.md
    └── gates/
        ├── readiness-gate.md
        ├── implementation-gate.md
        ├── verification-gate.md
        └── memory-gate.md
```

Claude Code supports skills and custom subagents; Claude uses a subagent’s description to decide when to delegate, so agent descriptions should be explicit about when each specialist should be used. ([Claude Platform Docs][4]) Claude Code hooks provide deterministic control at lifecycle points, and Anthropic’s docs describe hooks as shell commands that can run when Claude edits files, finishes tasks, or needs input. ([Claude Platform Docs][5])

---

# 8. GitHub Copilot Harness

GitHub Copilot should be the cloud/repository-integrated software factory surface, especially for GitHub-native workflows, pull requests, issue-driven development, repository instructions, prompt files, and agent profiles.

## 8.1 `.github/` Structure

```text
.github/
├── copilot-instructions.md
│
├── instructions/
│   ├── platform.instructions.md
│   ├── python.instructions.md
│   ├── mcp.instructions.md
│   ├── plugin.instructions.md
│   ├── security.instructions.md
│   ├── testing.instructions.md
│   ├── documentation.instructions.md
│   └── knowledge-graph.instructions.md
│
├── prompts/
│   ├── factory-plan.prompt.md
│   ├── add-cli-command.prompt.md
│   ├── add-mcp-tool.prompt.md
│   ├── add-domain-plugin.prompt.md
│   ├── fix-bug.prompt.md
│   ├── generate-evals.prompt.md
│   ├── update-knowledge-graph.prompt.md
│   └── release-readiness.prompt.md
│
├── agents/
│   ├── platform-architect.agent.md
│   ├── cli-engineer.agent.md
│   ├── mcp-tool-engineer.agent.md
│   ├── plugin-engineer.agent.md
│   ├── verification-engineer.agent.md
│   ├── security-reviewer.agent.md
│   ├── release-engineer.agent.md
│   └── knowledge-curator.agent.md
│
├── skills/
│   ├── add-cli-command/
│   ├── add-mcp-tool/
│   ├── add-domain-plugin/
│   ├── update-bootstrap-runtime/
│   ├── generate-evals/
│   ├── update-knowledge-graph/
│   └── release-platform/
│
├── hooks/
│   ├── hooks.json
│   ├── command-guard.sh
│   ├── post-edit-verify.sh
│   └── audit-log.sh
│
└── workflows/
    ├── build-cli.yml
    ├── build-mcp-server.yml
    ├── validate-plugin-runtime.yml
    ├── generate-plugins.yml
    ├── validate-copilot-plugins.yml
    ├── validate-claude-code-plugins.yml
    ├── run-evals.yml
    ├── security-scan.yml
    ├── verify-tool-contracts.yml
    ├── verify-knowledge-graph.yml
    └── release-platform.yml
```

GitHub documents repository custom instructions as a way to give Copilot context about how to understand the project and how to build, test, and validate changes. ([GitHub Docs][2]) GitHub Copilot skills are folders of instructions, scripts, and resources that Copilot can load when relevant, and Copilot hooks can execute custom shell commands at key points during agent execution. ([GitHub Docs][6]) GitHub custom agents are defined through Markdown agent profiles that specify prompts, tools, and MCP servers. ([GitHub Docs][7])

---

# 9. Assistant-Neutral Factory Layer

To avoid coupling the software factory only to Claude Code or Copilot, create an assistant-neutral `.factory/` layer.

```text
.factory/
├── README.md
├── factory-manifest.yaml
├── workflow-registry.yaml
├── agent-registry.yaml
├── skill-registry.yaml
├── tool-contract-registry.yaml
├── verification-policy.yaml
├── release-policy.yaml
├── memory-policy.yaml
├── worktree-policy.yaml
│
├── workflows/
│   ├── add-cli-command.yaml
│   ├── add-mcp-tool.yaml
│   ├── add-domain-plugin.yaml
│   ├── fix-bug.yaml
│   ├── evolve-schema.yaml
│   ├── update-bootstrap-runtime.yaml
│   ├── release-platform.yaml
│   └── update-knowledge-graph.yaml
│
├── templates/
│   ├── agent-template.md
│   ├── skill-template.md
│   ├── copilot-prompt-template.md
│   ├── claude-command-template.md
│   ├── mcp-tool-contract-template.json
│   └── verification-plan-template.md
│
└── generators/
    ├── generate-claude-harness.py
    ├── generate-copilot-harness.py
    ├── generate-plugin-from-definition.py
    ├── generate-mcp-tool.py
    └── generate-verification-plan.py
```

The `.factory/` layer becomes the source of truth for:

* What agents exist
* What skills exist
* What workflows exist
* What verification gates apply
* What memory files should be updated
* What contracts must remain compatible
* What tool specifications must be generated

The `.claude/` and `.github/` folders can then be generated or synchronized from `.factory/`.

---

# 10. Repository Knowledge Graph and Memory

The software factory needs a repository-specific knowledge graph implemented as files.

Google’s Open Knowledge Format was introduced by Google Cloud in June 2026 as an open specification that formalizes an “LLM-wiki” pattern into a portable, agent- and human-friendly representation of metadata, context, and curated knowledge. ([Google Cloud][8]) That is conceptually aligned with this repository-local memory architecture.

The repository should use a file-native knowledge graph inspired by:

```text
OKF-style portable knowledge files
Claude Obsidian-style vault navigation
Vault-D-style durable repository memory
Architecture decision records
Code ownership maps
Spec history
Agent execution history
Procedural playbooks
```

## 10.1 `.knowledge/` Structure

```text
.knowledge/
├── README.md
│
├── okf/
│   ├── manifest.yaml
│   ├── entities/
│   ├── relationships/
│   ├── contexts/
│   └── indexes/
│
├── graph/
│   ├── nodes/
│   │   ├── components/
│   │   ├── cli-commands/
│   │   ├── mcp-tools/
│   │   ├── plugins/
│   │   ├── skills/
│   │   ├── agents/
│   │   ├── schemas/
│   │   ├── workflows/
│   │   └── decisions/
│   ├── edges/
│   │   ├── implements/
│   │   ├── invokes/
│   │   ├── depends-on/
│   │   ├── validates/
│   │   ├── generates/
│   │   ├── supersedes/
│   │   └── owns/
│   └── graph-index.md
│
├── memory/
│   ├── semantic/
│   │   ├── architecture-principles.md
│   │   ├── platform-glossary.md
│   │   ├── domain-model.md
│   │   ├── tool-contract-principles.md
│   │   ├── plugin-design-principles.md
│   │   └── verification-principles.md
│   │
│   ├── episodic/
│   │   ├── 2026-07-architecture-decisions.md
│   │   ├── bugfix-history.md
│   │   ├── release-history.md
│   │   ├── failed-approaches.md
│   │   └── incident-retrospectives.md
│   │
│   ├── procedural/
│   │   ├── how-to-add-cli-command.md
│   │   ├── how-to-add-mcp-tool.md
│   │   ├── how-to-add-domain-plugin.md
│   │   ├── how-to-update-bootstrap-runtime.md
│   │   ├── how-to-run-verification.md
│   │   ├── how-to-release-platform.md
│   │   └── how-to-update-memory.md
│   │
│   └── working/
│       ├── current-roadmap.md
│       ├── active-risks.md
│       ├── active-refactors.md
│       ├── active-specs.md
│       └── current-agent-context.md
│
├── decisions/
│   ├── ADR-0001-cli-is-core-runtime.md
│   ├── ADR-0002-mcp-is-assistant-interface.md
│   ├── ADR-0003-domain-plugins-are-capability-packs.md
│   ├── ADR-0004-bootstrap-runtime-is-shared.md
│   ├── ADR-0005-software-factory-is-repository-native.md
│   └── ADR-0006-memory-is-file-native.md
│
├── contracts/
│   ├── cli-command-contracts.md
│   ├── mcp-tool-contracts.md
│   ├── plugin-contracts.md
│   ├── schema-contracts.md
│   └── compatibility-rules.md
│
├── indexes/
│   ├── code-index.md
│   ├── plugin-index.md
│   ├── mcp-tool-index.md
│   ├── skill-index.md
│   ├── agent-index.md
│   ├── schema-index.md
│   └── verification-index.md
│
└── queries/
    ├── find-related-components.md
    ├── find-contract-impact.md
    ├── find-verification-requirements.md
    └── find-memory-update-targets.md
```

---

# 11. Memory Types

## 11.1 Semantic Memory

Semantic memory stores durable knowledge about the platform.

Examples:

```text
- The CLI is the canonical runtime.
- MCP is the assistant-native interface.
- Domain plugins are capability packs.
- Bootstrap runtime is shared.
- Plugins must not silently install software.
- MCP tools must be allowlisted and schema-validated.
```

## 11.2 Episodic Memory

Episodic memory stores what happened.

Examples:

```text
- A prior attempt to bundle CLI inside plugins was rejected.
- Version 1.4.0 introduced domain-scoped MCP tools.
- The security plugin originally failed schema validation because threat model output lacked required fields.
- A bootstrap bug occurred because installed plugins were copied into assistant cache paths.
```

## 11.3 Procedural Memory

Procedural memory stores how to do things.

Examples:

```text
- How to add a CLI command.
- How to expose a CLI command as an MCP tool.
- How to add a domain plugin.
- How to generate Copilot and Claude plugin variants.
- How to update schemas and evals.
- How to run release verification.
```

## 11.4 Working Memory

Working memory stores current state.

Examples:

```text
- Active feature specs.
- Current release focus.
- Open refactors.
- Known risks.
- Temporary migration plans.
- Current worktree assignments.
```

---

# 12. Specification Kit

The software factory should be specification-driven.

```text
Intent should never go directly to code.
Intent should become a spec.
Spec should become a plan.
Plan should become isolated implementation.
Implementation should be verified.
Verification should update memory.
```

## 12.1 `.specs/` Structure

```text
.specs/
├── README.md
├── templates/
│   ├── feature-spec.md
│   ├── bugfix-spec.md
│   ├── cli-command-spec.md
│   ├── mcp-tool-spec.md
│   ├── plugin-spec.md
│   ├── schema-change-spec.md
│   ├── verification-spec.md
│   └── release-spec.md
│
├── active/
│   └── SPEC-YYYYMMDD-short-name.md
│
├── accepted/
├── implemented/
├── rejected/
└── archived/
```

## 12.2 Standard Spec Template

```markdown
# SPEC-YYYYMMDD-short-name

## 1. Intent

What is the user or developer trying to accomplish?

## 2. Problem

What platform problem does this solve?

## 3. Scope

### In Scope

### Out of Scope

## 4. Affected Components

- CLI
- MCP server
- plugin runtime
- plugin definitions
- Copilot plugins
- Claude Code plugins
- schemas
- evals
- docs
- knowledge graph

## 5. Required Contracts

### CLI Contract

### MCP Tool Contract

### Plugin Skill Contract

### Schema Contract

### Verification Contract

## 6. Implementation Plan

## 7. Acceptance Criteria

## 8. Verification Plan

## 9. Memory Update Plan

## 10. Rollback Plan
```

---

# 13. Tool Specification Alignment

The CLI should expose commands that can be represented as assistant tools.

This means every meaningful CLI capability should have a corresponding **tool contract**.

## 13.1 Tool Contract Structure

```text
cli/tool_contracts/
├── architecture_analyze.tool.json
├── dependency_map.tool.json
├── security_assess.tool.json
├── threat_model_generate.tool.json
├── resiliency_assess.tool.json
├── standards_check.tool.json
├── test_plan_create.tool.json
└── observability_assess.tool.json
```

## 13.2 Tool Contract Example

```json
{
  "name": "architecture_analyze",
  "description": "Analyze a project architecture and return architecture shape, components, dependencies, risks, and remediation recommendations.",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_root": {
        "type": "string",
        "description": "Path to the project root."
      },
      "depth": {
        "type": "string",
        "enum": ["quick", "standard", "deep"],
        "description": "Analysis depth."
      },
      "output_format": {
        "type": "string",
        "enum": ["json", "markdown"],
        "description": "Desired output format."
      }
    },
    "required": ["project_root"]
  },
  "cli_mapping": {
    "command": "agentic-tool architecture analyze",
    "args": {
      "project_root": "--project-root",
      "depth": "--depth",
      "output_format": "--format"
    }
  },
  "output_schema": "schemas/architecture-report.schema.json",
  "safety": {
    "readOnly": true,
    "requiresNetwork": false,
    "requiresWriteAccess": false
  }
}
```

## 13.3 Why Tool Contracts Matter

OpenAI’s Agents SDK describes tools as capabilities that let agents take actions, such as fetching data, running code, or calling external APIs. ([OpenAI GitHub][9]) OpenAI’s MCP documentation describes MCP as an open specification for connecting LLM clients to external tools and resources. ([OpenAI Developers][10])

For this platform, tool contracts should be used to generate:

```text
- MCP tool definitions
- CLI help text
- plugin skill instructions
- eval inputs
- schema validation tests
- documentation
- tool allowlists
```

This avoids contract drift.

---

# 14. Verification Architecture

The software factory must verify its own changes.

## 14.1 `.verification/` Structure

```text
.verification/
├── README.md
│
├── gates/
│   ├── cli-gate.yaml
│   ├── mcp-gate.yaml
│   ├── plugin-runtime-gate.yaml
│   ├── copilot-plugin-gate.yaml
│   ├── claude-plugin-gate.yaml
│   ├── schema-gate.yaml
│   ├── eval-gate.yaml
│   ├── security-gate.yaml
│   ├── docs-gate.yaml
│   └── knowledge-graph-gate.yaml
│
├── scripts/
│   ├── verify-all.sh
│   ├── verify-cli.sh
│   ├── verify-mcp.sh
│   ├── verify-plugin-runtime.sh
│   ├── verify-copilot-plugins.sh
│   ├── verify-claude-plugins.sh
│   ├── verify-tool-contracts.sh
│   ├── verify-schemas.sh
│   ├── verify-evals.sh
│   ├── verify-docs.sh
│   └── verify-knowledge-graph.sh
│
├── policies/
│   ├── command-allowlist.yaml
│   ├── no-arbitrary-shell.yaml
│   ├── no-silent-install.yaml
│   ├── schema-compatibility.yaml
│   ├── plugin-contract-compatibility.yaml
│   └── mcp-tool-compatibility.yaml
│
├── fixtures/
├── snapshots/
└── reports/
```

## 14.2 Verification Gates

Every feature or bug fix should pass:

```text
1. Spec gate
2. CLI contract gate
3. MCP contract gate
4. Plugin contract gate
5. Schema gate
6. Unit test gate
7. Integration test gate
8. Eval gate
9. Security gate
10. Documentation gate
11. Knowledge graph update gate
```

## 14.3 Verification Command

```bash
./.verification/scripts/verify-all.sh
```

This should run:

```bash
./.verification/scripts/verify-cli.sh
./.verification/scripts/verify-mcp.sh
./.verification/scripts/verify-plugin-runtime.sh
./.verification/scripts/verify-copilot-plugins.sh
./.verification/scripts/verify-claude-plugins.sh
./.verification/scripts/verify-tool-contracts.sh
./.verification/scripts/verify-schemas.sh
./.verification/scripts/verify-evals.sh
./.verification/scripts/verify-docs.sh
./.verification/scripts/verify-knowledge-graph.sh
```

---

# 15. Hooks as Deterministic Guardrails

Agents are probabilistic. Hooks are deterministic.

Therefore, hooks should enforce non-negotiable rules.

## 15.1 Claude Hooks

Claude Code hooks can run deterministic shell commands at defined lifecycle events. Anthropic documents hooks as a way to enforce project rules, automate repetitive tasks, and integrate Claude Code with existing tools. ([Claude][11])

Example:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/command-allowlist.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-edit-verify.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/stop-verification.sh"
          }
        ]
      }
    ]
  }
}
```

## 15.2 Copilot Hooks

GitHub Copilot hooks can execute shell commands at key points during agent execution, and GitHub describes hooks as useful for inspecting prompts and tool calls, logging audit information, and blocking high-risk command patterns. ([GitHub Docs][12])

Example:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": ".github/hooks/command-guard.sh"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": ".github/hooks/post-edit-verify.sh"
      }
    ]
  }
}
```

## 15.3 Hook Responsibilities

Hooks should enforce:

```text
- No arbitrary destructive shell commands
- No curl | bash
- No silent software installation
- No schema changes without schema tests
- No MCP tool changes without tool contract tests
- No plugin changes without manifest validation
- No bootstrap runtime changes without all domain plugin regeneration
- No code changes without relevant tests
- No feature completion without knowledge graph update
```

---

# 16. Agent Architecture

## 16.1 Agent Roles

```text
platform-architect
Owns cross-cutting architecture and validates design consistency.

spec-owner
Turns intent into implementation-ready specs.

cli-engineer
Implements CLI commands and core analyzers.

mcp-tool-engineer
Creates MCP tool contracts and adapters.

plugin-engineer
Creates domain plugin definitions and generated plugin outputs.

claude-plugin-engineer
Specializes in Claude Code plugin structure, skills, hooks, agents, and MCP config.

copilot-plugin-engineer
Specializes in GitHub Copilot customizations, skills, agents, hooks, prompt files, and plugin manifests.

bootstrap-runtime-engineer
Maintains CLI detection, install, version, and MCP wrapper scripts.

verification-engineer
Creates tests, evals, schema checks, and verification gates.

security-engineer
Reviews command execution, install behavior, MCP exposure, and trust boundaries.

release-engineer
Owns versioning, packaging, catalog publication, and compatibility.

documentation-engineer
Updates docs, examples, and usage guidance.

knowledge-curator
Updates semantic, episodic, procedural, and working memory.
```

## 16.2 Agent Delegation Pattern

```text
User intent
   ↓
platform-architect
   ↓
spec-owner
   ↓
planner
   ↓
specialist agents
   ↓
verification-engineer
   ↓
security-engineer
   ↓
documentation-engineer
   ↓
knowledge-curator
```

## 16.3 Worktree Isolation

For parallel development:

```text
.worktrees/
├── feat-add-security-threat-model-tool/
├── feat-add-architecture-plugin-skill/
├── fix-bootstrap-version-check/
└── refactor-plugin-generation/
```

The factory should prefer one feature/spec per worktree.

---

# 17. Software Factory Workflows

## 17.1 Add CLI Command

```text
Intent:
Add a new CLI command.

Factory workflow:
1. Create spec.
2. Identify command namespace.
3. Define tool contract.
4. Implement CLI command.
5. Add tests.
6. Add schema if output is structured.
7. Add MCP tool if assistant-invokable.
8. Add plugin skill if developer-facing.
9. Add evals.
10. Update docs.
11. Update knowledge graph.
```

## 17.2 Add MCP Tool

```text
Intent:
Expose existing CLI capability as an assistant tool.

Factory workflow:
1. Create MCP tool contract.
2. Map tool inputs to CLI args.
3. Validate output schema.
4. Add MCP server adapter.
5. Add domain-scoped MCP exposure.
6. Add MCP tests.
7. Add plugin .mcp.json entries.
8. Add evals.
9. Update tool index.
10. Update knowledge graph.
```

## 17.3 Add Domain Plugin

```text
Intent:
Add a new plugin such as observability or modernization.

Factory workflow:
1. Create plugin definition YAML.
2. Define skills.
3. Define agents.
4. Define MCP tool subset.
5. Generate Copilot plugin.
6. Generate Claude Code plugin.
7. Copy plugin runtime scripts.
8. Validate manifests.
9. Run plugin smoke tests.
10. Update plugin catalog.
11. Update docs and memory.
```

## 17.4 Fix Bug

```text
Intent:
Fix a defect.

Factory workflow:
1. Capture bug spec.
2. Search episodic memory for similar failures.
3. Identify affected contracts.
4. Create failing test or eval.
5. Implement fix.
6. Run targeted verification.
7. Run regression gate.
8. Update episodic memory.
9. Update procedural memory if the process changes.
```

## 17.5 Update Bootstrap Runtime

```text
Intent:
Change CLI detection, install, or wrapper behavior.

Factory workflow:
1. Create bootstrap change spec.
2. Update central plugin-runtime.
3. Regenerate all domain plugin scripts.
4. Verify Copilot plugins.
5. Verify Claude Code plugins.
6. Verify install modes.
7. Verify no silent install.
8. Update compatibility matrix.
9. Update procedural memory.
```

---

# 18. Product-Specific Invariants

These should be encoded into instructions, hooks, tests, and memory.

```text
1. CLI is the canonical runtime.
2. MCP is the assistant-native interface.
3. Plugins do not contain core business logic.
4. Domain plugins are optional capability packs.
5. Full-suite plugin is optional.
6. Bootstrap runtime is centrally maintained.
7. Plugin-managed installation is disabled by default.
8. CLI installation must use trusted package sources.
9. MCP tools must be schema-validated.
10. Plugin skills must call wrappers, not raw commands.
11. Tool contracts generate MCP, CLI docs, plugin skills, and evals.
12. Every platform change must update verification.
13. Every meaningful design change must update memory.
14. Copilot and Claude plugin variants must not drift.
15. Generated files must identify their source definition.
```

---

# 19. Example `CLAUDE.md`

```markdown
# Agentic Engineering Platform Factory Instructions

You are operating inside the Agentic Engineering Platform monorepo.

## Core Architecture

The CLI is the canonical runtime. MCP is the assistant-native interface. GitHub Copilot and Claude Code plugins are thin UX adapters. Domain plugins are optional capability packs.

## Required Workflow

Do not implement directly from vague intent.

For any meaningful change:

1. Create or update a spec in `.specs/active`.
2. Consult `.knowledge/memory/semantic`.
3. Consult `.knowledge/memory/procedural` for the relevant workflow.
4. Identify affected contracts.
5. Implement in the correct layer.
6. Add or update tests.
7. Add or update evals.
8. Run relevant verification scripts.
9. Update documentation.
10. Update `.knowledge` memory.

## Non-Negotiable Rules

- Do not silently install software.
- Do not use `curl | bash`.
- Do not add MCP tools without input and output schemas.
- Do not add plugin skills that bypass wrapper scripts.
- Do not change plugin runtime without regenerating domain plugins.
- Do not change CLI commands without updating MCP contracts when applicable.
- Do not complete a task without verification evidence.
```

---

# 20. Example GitHub Copilot Instructions

```markdown
# GitHub Copilot Repository Instructions

This repository is the Agentic Engineering Platform.

## Architecture

- `cli/` contains the canonical product runtime.
- `mcp-server/` exposes assistant-native tools.
- `plugin-runtime/` contains shared bootstrap logic.
- `plugin-definitions/` are the source of truth for generated domain plugins.
- `plugins/copilot/` and `plugins/claude-code/` contain generated or packaged assistant adapters.
- `.knowledge/` contains semantic, episodic, procedural, and working memory.
- `.specs/` contains implementation specs.
- `.verification/` contains deterministic verification gates.

## Copilot Behavior

Before coding:

1. Read relevant specs.
2. Read relevant procedural memory.
3. Identify affected contracts.
4. Prefer generated patterns over hand-crafted drift.
5. Add tests and evals.
6. Update docs and memory.

## Required Verification

Run the relevant verification script from `.verification/scripts/`.

Do not consider a change complete unless verification passes or the failure is explicitly documented.
```

---

# 21. Tool and CLI Design Requirements

The CLI should be designed so every assistant-facing capability can be expressed as:

```text
Tool name
Description
Input schema
Output schema
Safety metadata
CLI mapping
Timeout policy
Read/write classification
Required permissions
Verification tests
```

Example tool categories:

```text
Read-only tools:
- architecture_analyze
- dependency_map
- standards_check
- observability_assess

State-changing tools:
- remediation_plan_create
- plugin_generate
- schema_migrate
- memory_update

High-risk tools:
- bootstrap_install
- release_publish
- artifact_sign
```

High-risk tools should require explicit approval.

---

# 22. Verification Built Into the Factory

The software factory should not rely on the assistant saying “looks good.”

It should produce evidence.

## 22.1 Evidence Files

```text
.verification/reports/
├── SPEC-20260708-security-tool/
│   ├── cli-test-report.md
│   ├── mcp-test-report.md
│   ├── plugin-validation-report.md
│   ├── schema-validation-report.md
│   ├── eval-report.md
│   ├── security-report.md
│   ├── docs-report.md
│   └── memory-update-report.md
```

## 22.2 Completion Criteria

A task is complete only when:

```text
- Spec accepted
- Implementation complete
- Unit tests pass
- Integration tests pass
- MCP contract tests pass
- Plugin manifest validation passes
- Schema validation passes
- Evals pass
- Security checks pass
- Documentation updated
- Knowledge graph updated
- Verification report created
```

---

# 23. Prioritized Implementation Plan

## Phase 0 — Foundation Decisions

**Priority: Critical**

Create the initial architecture guardrails.

Deliverables:

```text
- ADR-0001-cli-is-core-runtime.md
- ADR-0002-mcp-is-assistant-interface.md
- ADR-0003-domain-plugins-are-capability-packs.md
- ADR-0004-software-factory-is-repository-native.md
- ADR-0005-memory-is-file-native.md
```

Success criteria:

```text
- Architecture decisions are explicit.
- Agents can refer to durable principles.
- Future changes have a baseline.
```

---

## Phase 1 — Repository Factory Skeleton

**Priority: Critical**

Add the factory directories.

Deliverables:

```text
.claude/
.github/
.factory/
.knowledge/
.specs/
.verification/
.workflows/
```

Success criteria:

```text
- Repository has visible software factory structure.
- Claude and Copilot both have customization entry points.
- Assistant-neutral factory layer exists.
```

---

## Phase 2 — Knowledge Graph and Memory

**Priority: Critical**

Create file-native memory.

Deliverables:

```text
.knowledge/memory/semantic/
.knowledge/memory/episodic/
.knowledge/memory/procedural/
.knowledge/memory/working/
.knowledge/graph/
.knowledge/contracts/
.knowledge/indexes/
```

Initial files:

```text
architecture-principles.md
platform-glossary.md
how-to-add-cli-command.md
how-to-add-mcp-tool.md
how-to-add-domain-plugin.md
cli-command-contracts.md
mcp-tool-contracts.md
plugin-contracts.md
```

Success criteria:

```text
- Agents can retrieve durable architecture context.
- Procedural workflows exist as files.
- Memory update is part of done criteria.
```

---

## Phase 3 — Spec Kit

**Priority: Critical**

Create `.specs/` and make specs mandatory for meaningful work.

Deliverables:

```text
.specs/templates/feature-spec.md
.specs/templates/bugfix-spec.md
.specs/templates/cli-command-spec.md
.specs/templates/mcp-tool-spec.md
.specs/templates/plugin-spec.md
.specs/templates/verification-spec.md
```

Success criteria:

```text
- Every non-trivial change starts with a spec.
- Spec includes contracts, verification, and memory update plan.
```

---

## Phase 4 — Claude Code Harness

**Priority: High**

Build the Claude Code software factory.

Deliverables:

```text
.claude/CLAUDE.md
.claude/agents/
.claude/skills/
.claude/commands/
.claude/hooks/
.claude/speckit/
```

Initial agents:

```text
platform-architect
spec-owner
cli-engineer
mcp-tool-engineer
plugin-engineer
verification-engineer
security-engineer
knowledge-curator
```

Initial skills:

```text
add-cli-command
add-mcp-tool
add-domain-plugin
generate-evals
update-knowledge-graph
release-platform
```

Success criteria:

```text
- Claude can plan and execute repository changes using specs.
- Claude uses specialist agents.
- Claude hooks enforce deterministic guardrails.
```

---

## Phase 5 — GitHub Copilot Harness

**Priority: High**

Build the GitHub Copilot customization layer.

Deliverables:

```text
.github/copilot-instructions.md
.github/instructions/
.github/prompts/
.github/agents/
.github/skills/
.github/hooks/
```

Success criteria:

```text
- Copilot has repository-specific engineering instructions.
- Prompt files exist for repeatable workflows.
- Copilot agents map to factory roles.
- Hooks support policy and verification.
```

---

## Phase 6 — Tool Contract Registry

**Priority: High**

Create the formal tool contract layer.

Deliverables:

```text
cli/src/agentic_tool/tool_contracts/
.factory/tool-contract-registry.yaml
.knowledge/contracts/mcp-tool-contracts.md
.knowledge/contracts/cli-command-contracts.md
```

Success criteria:

```text
- CLI commands can be mapped to MCP tools.
- MCP tools can be generated or validated from contracts.
- Plugin skills can refer to the same contracts.
```

---

## Phase 7 — Verification Harness

**Priority: High**

Create deterministic verification.

Deliverables:

```text
.verification/scripts/verify-all.sh
.verification/scripts/verify-cli.sh
.verification/scripts/verify-mcp.sh
.verification/scripts/verify-plugin-runtime.sh
.verification/scripts/verify-tool-contracts.sh
.verification/scripts/verify-knowledge-graph.sh
.verification/gates/
.verification/policies/
```

Success criteria:

```text
- Factory changes are not accepted without evidence.
- CLI/MCP/plugin drift is detectable.
- Knowledge graph updates are verifiable.
```

---

## Phase 8 — Plugin Generation Factory

**Priority: Medium-High**

Automate plugin generation from plugin definitions.

Deliverables:

```text
plugin-definitions/*.yaml
tools/generate-plugins/
.factory/workflows/add-domain-plugin.yaml
.verification/scripts/verify-generated-plugins.sh
```

Success criteria:

```text
- Copilot and Claude plugins are generated from shared definitions.
- Runtime scripts are copied consistently.
- Plugin catalog updates automatically.
```

---

## Phase 9 — Memory Update Automation

**Priority: Medium**

Add hooks and scripts that identify memory update requirements.

Deliverables:

```text
.claude/hooks/memory-update-suggester.sh
.github/hooks/memory-update-suggester.sh
.verification/scripts/verify-knowledge-graph.sh
.knowledge/memory/working/current-agent-context.md
```

Success criteria:

```text
- Significant changes propose semantic, episodic, or procedural memory updates.
- Verification fails when required memory updates are missing.
```

---

## Phase 10 — Release Factory

**Priority: Medium**

Productize release workflows.

Deliverables:

```text
.workflows/release-platform.md
.github/workflows/release-platform.yml
.claude/skills/release-platform/
.factory/release-policy.yaml
.verification/scripts/verify-release-readiness.sh
```

Success criteria:

```text
- CLI, MCP server, plugin runtime, plugins, catalog, and docs release together.
- Compatibility matrix is updated.
- Release notes are generated.
```

---

# 24. Recommended Build Order

The recommended practical sequence is:

```text
1. Create .knowledge and ADRs.
2. Create .specs templates.
3. Create .verification skeleton.
4. Create .claude/CLAUDE.md and first agents.
5. Create .github/copilot-instructions.md and prompt files.
6. Create tool contract registry.
7. Add verify-all.sh.
8. Add add-cli-command workflow.
9. Add add-mcp-tool workflow.
10. Add add-domain-plugin workflow.
11. Add memory update workflow.
12. Add release workflow.
```

Start with the narrowest useful factory workflow:

```text
"Add a new MCP tool from an existing CLI command."
```

That workflow exercises:

```text
- spec
- CLI contract
- MCP adapter
- plugin skill
- schema
- eval
- verification
- memory update
```

It is the best first factory slice.

---

# 25. Final Target State

The final target state is a repository that can answer and execute requests like:

```text
"Add a new observability assessment capability to the platform."
```

The software factory should then:

```text
1. Create a spec.
2. Search semantic and procedural memory.
3. Identify affected CLI, MCP, plugin, schema, eval, and docs areas.
4. Create an implementation plan.
5. Assign specialist agents.
6. Implement changes in a worktree.
7. Generate or update plugin definitions.
8. Update Copilot and Claude plugin outputs.
9. Run verification gates.
10. Update knowledge graph.
11. Produce a merge-ready change with evidence.
```

The most important architectural outcome is this:

```text
The agentic engineering platform should be engineered by an agentic software factory that is itself governed by specifications, memory, tool contracts, and verification.
```

That is how the monorepo becomes self-improving without becoming uncontrolled.

[1]: https://docs.anthropic.com/en/docs/claude-code/sdk?utm_source=chatgpt.com "Agent SDK overview - Claude Code Docs"
[2]: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot?utm_source=chatgpt.com "Adding repository custom instructions for GitHub Copilot"
[3]: https://docs.anthropic.com/en/docs/claude-code/overview?utm_source=chatgpt.com "Overview - Claude Code Docs"
[4]: https://docs.anthropic.com/en/docs/claude-code/skills?utm_source=chatgpt.com "Extend Claude with skills - Claude Code Docs"
[5]: https://docs.anthropic.com/en/docs/claude-code/hooks-guide?utm_source=chatgpt.com "Automate actions with hooks - Claude Code Docs"
[6]: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?utm_source=chatgpt.com "Adding agent skills for GitHub Copilot CLI"
[7]: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents?utm_source=chatgpt.com "About custom agents"
[8]: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing?utm_source=chatgpt.com "How the Open Knowledge Format can improve data sharing"
[9]: https://openai.github.io/openai-agents-python/tools/?utm_source=chatgpt.com "Tools - OpenAI Agents SDK"
[10]: https://developers.openai.com/apps-sdk/concepts/mcp-server?utm_source=chatgpt.com "MCP – Apps SDK"
[11]: https://code.claude.com/docs/en/hooks-guide?utm_source=chatgpt.com "Automate workflows with hooks - Claude Code Docs"
[12]: https://docs.github.com/en/copilot/tutorials/copilot-cli-hooks?utm_source=chatgpt.com "Using hooks with Copilot CLI for predictable, policy- ..."

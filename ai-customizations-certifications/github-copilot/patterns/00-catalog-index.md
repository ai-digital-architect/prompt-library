# GitHub Copilot Workflow Pattern Catalog

## Mapping Claude Code Patterns → GitHub Copilot Customization Architecture

This catalog translates every workflow pattern from the Claude Code reference into concrete implementations using GitHub Copilot's five core components: **Instructions**, **Agent Skills**, **Custom Agents** (Handoffs + Sub-agents), **Hooks**, and the **Copilot SDK**.

---

## Component Translation Key

| Claude Code Concept | GitHub Copilot Equivalent | Notes |
|---|---|---|
| `CLAUDE.md` (project root) | `copilot-instructions.md` + `AGENTS.md` | Split standards from operational procedures |
| `CLAUDE.md` (module-level) | `.instructions.md` with `applyTo` glob | Path-specific scoping |
| `~/.claude/CLAUDE.md` | VS Code Personal Instructions | User settings |
| Sub-agent (`.claude/agents/`) | `.agent.md` with `tools: ['agent']` + `agents: [...]` | Single-level depth, whitelist model |
| Slash Command (`.claude/commands/`) | `.prompt.md` (`.github/prompts/`) | Invoked via `/command` |
| Hook (`settings.json`) | Copilot Hooks (event-level) or Permission Handler (SDK) | Different granularity — see notes |
| `disallowedTools: [Write, Edit]` | `tools: ['codebase', 'search', 'fetch']` (whitelist) | Inverted model: Copilot uses allow-list, not deny-list |
| SubagentStop hook | No direct equivalent | Use parent agent logic or PostToolUse hook |
| `permissionMode: bypassPermissions` | Not available | Use SDK Permission Handler for explicit approval |

---

## Compatibility Assessment Summary

| # | Pattern | Implementable? | Fidelity | Primary Components |
|---|---|---|---|---|
| **1. Pipeline & Ordering** | | | |
| 1.1 | Sequential Pipeline | ✅ Yes | High | Handoffs + Hooks |
| 1.2 | Parallel Fan-out / Fan-in | ✅ Yes | High | Sub-agents (parallel) |
| 1.3 | Self-Reflection Loop | ✅ Yes | High | Sub-agent review loop |
| **2. Gating & Approval** | | | |
| 2.1 | Human-in-the-Loop Approval | ✅ Yes | High | Handoffs (`send: false`) |
| 2.2 | Staged Rollout Gate | ✅ Yes | Medium | Handoffs + Hooks + SDK |
| 2.3 | Cost-Threshold Gate | ⚠️ Partial | Medium | SDK Permission Handler |
| **3. Research & Discovery** | | | |
| 3.1 | Explore-then-Implement | ✅ Yes | High | Sub-agents with tool restrictions |
| 3.2 | Competitive Analysis | ✅ Yes | High | Parallel sub-agents |
| 3.3 | Dependency Audit | ✅ Yes | High | Read-only sub-agent + Skill |
| **4. Refactoring & Migration** | | | |
| 4.1 | Incremental Migration | ✅ Yes | High | Sub-agents + PostToolUse hooks |
| 4.2 | Pattern Replacement | ✅ Yes | High | Research + Implementer sub-agents |
| 4.3 | Database Schema Evolution | ✅ Yes | High | Sequential sub-agents |
| **5. Validation & Verification** | | | |
| 5.1 | Contract Testing | ✅ Yes | High | Sub-agents |
| 5.2 | Spec-First Verification | ✅ Yes | High | Sub-agents + Skill |
| 5.3 | Regression Sweep | ✅ Yes | Medium | Hooks + Sub-agents |
| **6. Generation & Scaffolding** | | | |
| 6.1 | Template Instantiation | ✅ Yes | High | Prompt files + Sub-agents |
| 6.2 | API Client Generation | ✅ Yes | High | Sub-agent + Hooks |
| 6.3 | Documentation Generation | ✅ Yes | High | Read-only sub-agent |
| **7. Monitoring & Alerting** | | | |
| 7.1 | Watchdog Loop | ⚠️ Partial | Low | GitHub Actions + SDK (no native polling) |
| 7.2 | Build Failure Triage | ✅ Yes | High | Skill + Agent |
| 7.3 | Log Analysis | ✅ Yes | High | Sub-agent |
| **8. Review & Audit** | | | |
| 8.1 | PR Review Pipeline | ✅ Yes | High | Chained sub-agents |
| 8.2 | Compliance Audit | ✅ Yes | High | Read-only sub-agent |
| 8.3 | Dead Code Detection | ✅ Yes | High | Sub-agent |
| **9. Multi-environment** | | | |
| 9.1 | Environment Parity Check | ✅ Yes | High | Sub-agent + Hooks |
| 9.2 | Secret Rotation | ✅ Yes | Medium | Sequential sub-agents + SDK |
| 9.3 | Infrastructure Drift Detection | ✅ Yes | High | Sub-agent |
| **10. Feedback & Learning** | | | |
| 10.1 | Postmortem Assistant | ✅ Yes | High | Sub-agent + Skill |
| 10.2 | Test Failure Explainer | ✅ Yes | High | Sub-agent |
| 10.3 | Code Archaeology | ✅ Yes | High | Read-only sub-agent |
| **11. Orchestration Meta** | | | |
| 11.1 | Workflow Chaining | ✅ Yes | High | Prompt files (`.prompt.md`) |
| 11.2 | Conditional Branching | ✅ Yes | High | Parent agent + sub-agents |
| 11.3 | Map-Reduce | ✅ Yes | High | Parent agent + parallel sub-agents |

**Legend:** ✅ Full implementation · ⚠️ Partial (architectural gaps noted) · ❌ Not feasible

---

## Key Architectural Differences to Note

### 1. Hook Granularity
Claude Code hooks operate at the **tool level** (intercept before/after each tool call with matcher patterns). GitHub Copilot hooks operate at the **event level** (session lifecycle, git operations). For fine-grained tool interception in Copilot, use the **SDK Permission Handler** instead.

### 2. SubagentStop Hook
Claude Code's `SubagentStop` hook (used for completion tracking, score gating, and loop control) has no direct equivalent in Copilot. The replacement strategy is to encode the gating logic into the **parent agent's prompt** — instruct the parent to inspect sub-agent output and decide whether to iterate.

### 3. Tool Permission Model
Claude Code uses a **deny-list** (`disallowedTools`). Copilot uses an **allow-list** (`tools`). When translating, invert the logic: instead of listing what a sub-agent *cannot* do, list only what it *can* do.

### 4. Persistent Polling
Claude Code can implement watchdog loops within a session. Copilot has no native persistent polling. Use **GitHub Actions on a cron schedule** combined with the **Copilot SDK** to achieve equivalent behavior.

---

## File Index

Each pattern below has a dedicated implementation file with complete `.agent.md`, `SKILL.md`, `.prompt.md`, hook configurations, and SDK code where applicable.

| File | Pattern |
|---|---|
| `01-pipeline-ordering/01-sequential-pipeline.md` | Sequential Pipeline |
| `01-pipeline-ordering/02-parallel-fan-out-fan-in.md` | Parallel Fan-out / Fan-in |
| `01-pipeline-ordering/03-self-reflection-loop.md` | Self-Reflection Loop |
| `02-gating-approval/01-human-in-the-loop.md` | Human-in-the-Loop Approval |
| `02-gating-approval/02-staged-rollout-gate.md` | Staged Rollout Gate |
| `02-gating-approval/03-cost-threshold-gate.md` | Cost-Threshold Gate |
| `03-research-discovery/01-explore-then-implement.md` | Explore-then-Implement |
| `03-research-discovery/02-competitive-analysis.md` | Competitive Analysis |
| `03-research-discovery/03-dependency-audit.md` | Dependency Audit |
| `04-refactoring-migration/01-incremental-migration.md` | Incremental Migration |
| `04-refactoring-migration/02-pattern-replacement.md` | Pattern Replacement |
| `04-refactoring-migration/03-database-schema-evolution.md` | Database Schema Evolution |
| `05-validation-verification/01-contract-testing.md` | Contract Testing |
| `05-validation-verification/02-spec-first-verification.md` | Spec-First Verification |
| `05-validation-verification/03-regression-sweep.md` | Regression Sweep |
| `06-generation-scaffolding/01-template-instantiation.md` | Template Instantiation |
| `06-generation-scaffolding/02-api-client-generation.md` | API Client Generation |
| `06-generation-scaffolding/03-documentation-generation.md` | Documentation Generation |
| `07-monitoring-alerting/01-watchdog-loop.md` | Watchdog Loop |
| `07-monitoring-alerting/02-build-failure-triage.md` | Build Failure Triage |
| `07-monitoring-alerting/03-log-analysis.md` | Log Analysis |
| `08-review-audit/01-pr-review-pipeline.md` | PR Review Pipeline |
| `08-review-audit/02-compliance-audit.md` | Compliance Audit |
| `08-review-audit/03-dead-code-detection.md` | Dead Code Detection |
| `09-multi-environment/01-environment-parity-check.md` | Environment Parity Check |
| `09-multi-environment/02-secret-rotation.md` | Secret Rotation |
| `09-multi-environment/03-infrastructure-drift-detection.md` | Infrastructure Drift Detection |
| `10-feedback-learning/01-postmortem-assistant.md` | Postmortem Assistant |
| `10-feedback-learning/02-test-failure-explainer.md` | Test Failure Explainer |
| `10-feedback-learning/03-code-archaeology.md` | Code Archaeology |
| `11-orchestration-meta/01-workflow-chaining.md` | Workflow Chaining |
| `11-orchestration-meta/02-conditional-branching.md` | Conditional Branching |
| `11-orchestration-meta/03-map-reduce.md` | Map-Reduce |

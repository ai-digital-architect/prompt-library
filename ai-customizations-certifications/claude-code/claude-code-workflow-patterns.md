# Claude Code Workflow Patterns

A reference catalogue of agentic workflow patterns buildable with the Claude Code customization architecture — Memory, Sub-agents, Hooks, and Slash Commands.

---

## Table of Contents

1. [Pipeline & Ordering Workflows](#1-pipeline--ordering-workflows)
2. [Gating & Approval Workflows](#2-gating--approval-workflows)
3. [Research & Discovery Workflows](#3-research--discovery-workflows)
4. [Refactoring & Migration Workflows](#4-refactoring--migration-workflows)
5. [Validation & Verification Workflows](#5-validation--verification-workflows)
6. [Generation & Scaffolding Workflows](#6-generation--scaffolding-workflows)
7. [Monitoring & Alerting Workflows](#7-monitoring--alerting-workflows)
8. [Review & Audit Workflows](#8-review--audit-workflows)
9. [Multi-environment Workflows](#9-multi-environment-workflows)
10. [Feedback & Learning Workflows](#10-feedback--learning-workflows)
11. [Orchestration Meta-Workflows](#11-orchestration-meta-workflows)

---

## 1. Pipeline & Ordering Workflows

Workflows where execution order, data hand-off between stages, or iterative quality loops are the primary concern.

- **Sequential pipeline** — Strict stage-by-stage execution where each step gates the next (e.g. schema → entity → API → UI → tests). A PostToolUse hook enforces the gate by running the compile or test command and blocking on failure.

- **Parallel fan-out / fan-in** — Independent workers run concurrently against a shared contract defined in `CLAUDE.md`. A SubagentStop hook tracks completion of each worker and signals when a merge agent can reconcile all branches.

- **Self-reflection loop** — A generate → critique → revise cycle that iterates until a quality threshold is met. A read-only critic sub-agent scores the output as structured JSON; a SubagentStop hook reads the score and either allows the session to stop or blocks it and forces another revision pass.

---

## 2. Gating & Approval Workflows

Workflows that insert deliberate checkpoints — human or automated — before allowing execution to continue.

- **Human-in-the-loop approval** — The agent pauses at a defined stage, surfaces a summary to the user, and waits for explicit sign-off before proceeding. Implemented via a Slash Command that halts and prompts, or a PreToolUse hook that exits 2 until a sentinel file is present.

- **Staged rollout gate** — Promotes a build through environments sequentially (dev → smoke test → approve → staging → approve → prod). Each promotion step is a sub-agent; each gate is a hook that checks test or health-check results before allowing the next invocation.

- **Cost-threshold gate** — Estimates the token or compute cost of an operation before executing it. A PreToolUse hook reads the planned tool call, calculates estimated cost, and blocks if the estimate exceeds a configured budget ceiling.

---

## 3. Research & Discovery Workflows

Workflows that separate information gathering from implementation to improve focus and reduce risk.

- **Explore-then-implement** — A read-only researcher sub-agent maps the codebase, identifies relevant files, existing patterns, and potential conflicts, then passes a structured research summary to a write-capable implementer sub-agent. The researcher has `disallowedTools: [Write, Edit]`.

- **Competitive analysis** — Multiple parallel sub-agents each research a different source or competitor. A synthesis agent aggregates all findings into a structured report. SubagentStop hooks log each researcher's completion before the synthesizer is invoked.

- **Dependency audit** — A read-only sub-agent scans all dependency manifests, cross-references version data against known CVE feeds or a license policy, and produces a risk-ranked report without touching any implementation files.

---

## 4. Refactoring & Migration Workflows

Workflows for making safe, incremental, or pattern-wide changes to an existing codebase.

- **Incremental migration** — Migrates one module at a time through a sequential pipeline. Each module's migration is a sub-agent invocation; a PostToolUse hook runs the test suite after each module and blocks progression to the next if tests fail, ensuring the build is never broken mid-migration.

- **Pattern replacement** — A research sub-agent locates all instances of a deprecated pattern across the codebase. An implementer sub-agent then processes each instance, replacing it with the approved pattern. A PostToolUse hook runs lint and compile after each replacement.

- **Database schema evolution** — A sequential pipeline: schema diff sub-agent → migration script generator → backwards-compatibility checker → rollout plan producer. Each stage gates on the previous output, and a hook validates that the migration is reversible before the plan is finalized.

---

## 5. Validation & Verification Workflows

Workflows that confirm correctness, contract adherence, or coverage without producing new implementation code.

- **Contract testing** — A sub-agent generates consumer contracts from the frontend's API usage. A separate sub-agent verifies those contracts against the backend provider. A hook fails the session if drift is detected between what the consumer expects and what the provider delivers.

- **Spec-first verification** — An OpenAPI or GraphQL spec is written first. A sub-agent generates tests directly from the spec. A second sub-agent then verifies that the existing implementation satisfies every generated test, reporting any endpoints or fields that are missing or incorrectly implemented.

- **Regression sweep** — A hook captures the full test suite results before a change is made. After implementation, a second hook captures results again. A diff sub-agent compares the two result sets and surfaces any newly failing tests, clearly attributing them to the change.

---

## 6. Generation & Scaffolding Workflows

Workflows that produce new code, configuration, or documentation from a specification or template.

- **Template instantiation** — A Slash Command accepts a feature description as `$ARGUMENTS` and invokes a sub-agent that fills a project scaffold template — creating all boilerplate files, wiring up routes, registering the new module — based on the project's established conventions in `CLAUDE.md`.

- **API client generation** — A sub-agent reads an OpenAPI or gRPC spec and generates fully typed API clients in one or more target languages. A PostToolUse hook runs the type-checker for each generated client before the session completes.

- **Documentation generation** — A read-only sub-agent reads source files, existing tests, and commit history, then produces API reference documentation, a README, and an architecture decision record. Since it is read-only, it can be safely invoked on any branch without risk of side effects.

---

## 7. Monitoring & Alerting Workflows

Workflows that continuously or periodically observe a condition and act when it drifts outside expected bounds.

- **Watchdog loop** — A Slash Command sets up a polling loop: a sub-agent checks a condition (test health, bundle size, dependency freshness, API latency) on a schedule. A Stop hook fires a notification to Slack or a pager when the condition exceeds a threshold.

- **Build failure triage** — Triggered by a CI failure notification (via a Stop or Notification hook). A sub-agent receives the failure log, diagnoses the root cause by reading recent commits and the failing test output, and produces a structured triage report with a proposed fix.

- **Log analysis** — A sub-agent ingests a rolling window of error logs, clusters entries by pattern using Bash tooling, de-duplicates noise, and produces a ranked summary of distinct failure modes with frequency, first-seen, and last-seen timestamps.

---

## 8. Review & Audit Workflows

Workflows that evaluate existing code or configuration against a defined standard without modifying it.

- **PR review pipeline** — A sequential chain of read-only sub-agents: diff analyzer → security reviewer → style checker → coverage checker → summary writer. Each sub-agent receives only the diff and its specialist context. A final sub-agent aggregates all findings into a single review comment.

- **Compliance audit** — A read-only sub-agent scans the codebase against a defined ruleset (OWASP Top 10, GDPR data-handling requirements, OSS license policy). Findings are severity-ranked and mapped to file locations. The sub-agent has `disallowedTools: [Write, Edit]` to guarantee it cannot accidentally modify the code it is auditing.

- **Dead code detection** — A sub-agent identifies unused exports, unreachable branches, and stale feature flags by combining static analysis (via Bash tools) with a read pass of the codebase. It produces a deletion candidate list that a human or a separate implementer sub-agent can act on.

---

## 9. Multi-environment Workflows

Workflows that span or compare multiple deployment environments, configuration sets, or infrastructure states.

- **Environment parity check** — A sub-agent reads configuration files for dev, staging, and production environments and diffs them against a canonical baseline stored in `CLAUDE.md`. A hook flags any undocumented divergence and blocks promotion until the divergence is either resolved or explicitly acknowledged.

- **Secret rotation** — A sub-agent identifies all locations in code and configuration that reference a given credential. A sequential pipeline then generates a new secret, updates every reference atomically within a transaction, and verifies that the service starts cleanly before the old credential is revoked.

- **Infrastructure drift detection** — A sub-agent compares the declared Terraform or CloudFormation state against the live cloud resource inventory (via a Bash call to the cloud CLI). Drift items are categorized as safe drift, risky drift, or unauthorized change, and routed to the appropriate owner.

---

## 10. Feedback & Learning Workflows

Workflows that extract structured insight from past events, failures, or history.

- **Postmortem assistant** — A sub-agent ingests an incident timeline (from logs, alerts, or a Slack export), identifies contributing factors and timeline gaps, and drafts a postmortem document with a root-cause analysis and prioritized action items. A hook formats the output to match the team's postmortem template.

- **Test failure explainer** — When a test fails in CI, a sub-agent receives the test name, failure message, and the last 10 commits touching that file. It traces back to the commit that introduced the regression, explains the failure in plain language, and suggests a fix — all as a read-only operation.

- **Code archaeology** — A sub-agent traces the full git history of a file or function, correlates changes with commit messages and associated PR descriptions, and produces a narrative explanation of why the code evolved to its current state. Useful for onboarding or before undertaking a large refactor.

---

## 11. Orchestration Meta-Workflows

Patterns that govern how other workflows are composed, chained, or conditionally executed.

- **Workflow chaining** — The output artifact of one Slash Command is automatically passed as `$ARGUMENTS` to the next. For example, `/project:plan-feature` produces a plan file, and `/project:implement-feature` reads that file as its starting context, enabling a multi-session pipeline without manual copy-paste.

- **Conditional branching** — A coordinator sub-agent inspects the project type, language, or current state of the repository and selects which specialist sub-agent to invoke next. The branching logic lives in the sub-agent's `description` field and in a Slash Command that evaluates a condition before dispatching.

- **Map-reduce** — A coordinator fans out over a list (files, modules, endpoints, test suites) and invokes a worker sub-agent for each item independently. A SubagentStop hook logs each worker's result. When all workers are done, a reducer sub-agent aggregates the individual results into a unified output.

---

## Component Placement Quick Reference

| Workflow concern | Correct component |
|---|---|
| Always-on project standards and build commands | `CLAUDE.md` (project root) |
| Module-specific conventions | `src/<module>/CLAUDE.md` |
| Personal cross-project preferences | `~/.claude/CLAUDE.md` |
| Specialist task execution (research, implement, review) | Sub-agent (`.claude/agents/`) |
| User-triggered repeatable workflows | Slash Command (`.claude/commands/`) |
| Unconditional enforcement (gate, lint, block, notify) | Hook (`settings.json`) |
| Loop control (score gate, completion tracking) | SubagentStop hook |
| Pipeline ordering and fan-out logic | Slash Command |
| External tool access (DB, APIs, file systems) | MCP Server |

---

*Claude Code Customization Architecture · March 2026*

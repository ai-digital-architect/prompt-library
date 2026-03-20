# Claude Code Workflow Patterns — Full Architecture Implementations

A collection of 33 agentic workflow patterns, each with complete Claude Code customization architecture: Memory (`CLAUDE.md` / `AGENTS.md`), Sub-agents, Hooks, Skills, MCP Servers, and `settings.json` configuration.

Each pattern is a standalone, copy-pasteable reference that maps the workflow concept to concrete files and configurations.

---

## Directory Structure

```
workflow-patterns/
├── 01-pipeline-ordering/
│   ├── 01-sequential-pipeline.md
│   ├── 02-parallel-fan-out-fan-in.md
│   └── 03-self-reflection-loop.md
├── 02-gating-approval/
│   ├── 04-human-in-the-loop-approval.md
│   ├── 05-staged-rollout-gate.md
│   └── 06-cost-threshold-gate.md
├── 03-research-discovery/
│   ├── 07-explore-then-implement.md
│   ├── 08-competitive-analysis.md
│   └── 09-dependency-audit.md
├── 04-refactoring-migration/
│   ├── 10-incremental-migration.md
│   ├── 11-pattern-replacement.md
│   └── 12-database-schema-evolution.md
├── 05-validation-verification/
│   ├── 13-contract-testing.md
│   ├── 14-spec-first-verification.md
│   └── 15-regression-sweep.md
├── 06-generation-scaffolding/
│   ├── 16-template-instantiation.md
│   ├── 17-api-client-generation.md
│   └── 18-documentation-generation.md
├── 07-monitoring-alerting/
│   ├── 19-watchdog-loop.md
│   ├── 20-build-failure-triage.md
│   └── 21-log-analysis.md
├── 08-review-audit/
│   ├── 22-pr-review-pipeline.md
│   ├── 23-compliance-audit.md
│   └── 24-dead-code-detection.md
├── 09-multi-environment/
│   ├── 25-environment-parity-check.md
│   ├── 26-secret-rotation.md
│   └── 27-infrastructure-drift-detection.md
├── 10-feedback-learning/
│   ├── 28-postmortem-assistant.md
│   ├── 29-test-failure-explainer.md
│   └── 30-code-archaeology.md
└── 11-orchestration-meta/
    ├── 31-workflow-chaining.md
    ├── 32-conditional-branching.md
    └── 33-map-reduce.md
```

---

## How to Use These Patterns

Each pattern document includes:

1. **Overview** — What the pattern does and when to use it
2. **Architecture Diagram** — ASCII flow showing component interactions
3. **Component Breakdown** — Which Claude Code components are involved and why
4. **Complete File Implementations** — Every file needed, ready to copy into your project
5. **Token Cost Analysis** — Per-component token impact
6. **Security Considerations** — Risks and mitigations specific to this pattern

Copy the files you need into your `.claude/` directory structure and adapt the examples to your project's tech stack.

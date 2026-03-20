# Pattern 02: Parallel Fan-out / Fan-in

## Category
Pipeline & Ordering Workflows

## Overview

Independent worker sub-agents execute concurrently against a shared contract defined in `CLAUDE.md`. Each worker processes an isolated unit of work (a module, a file, a feature slice). A `SubagentStop` hook tracks completion of each worker and signals when all are done. A merge/reconciliation agent then combines all branch outputs into a unified result.

## Architecture Diagram

```
User invokes /fan-out-fan-in
        │
        ▼
┌──────────────────────┐
│  Coordinator Agent    │
│  (parent / skill)     │
│  - Reads work manifest│
│  - Fans out to N      │
│    worker sub-agents  │
└──────┬───┬───┬────────┘
       │   │   │
       ▼   ▼   ▼
    ┌─────┐ ┌─────┐ ┌─────┐
    │ W-1 │ │ W-2 │ │ W-N │     Worker sub-agents (isolated contexts)
    └──┬──┘ └──┬──┘ └──┬──┘
       │       │       │
       ▼       ▼       ▼
  SubagentStop hooks log each worker result to .claude/fan-out-results/
       │       │       │
       └───────┼───────┘
               ▼
    ┌──────────────────┐
    │  Merge Agent      │
    │  - Reads all      │
    │    worker outputs │
    │  - Reconciles     │
    │  - Produces final │
    └──────────────────┘
```

## Component Breakdown

| Component | Role | Why This Component |
|-----------|------|--------------------|
| **Skill** | Entry point; coordinator logic | Orchestrates fan-out, waits for results, invokes merger |
| **Worker sub-agents** | Process each unit independently | Isolated context = true parallelism; no shared state |
| **Merge sub-agent** | Reconciles all outputs | Reads worker artifacts; produces unified result |
| **SubagentStop Hook** | Tracks worker completions | Logs each worker's result to a shared directory |
| **CLAUDE.md** | Shared interface contract | Workers must produce outputs in a consistent format |

## Token Cost Analysis

| Component | Token Cost | Notes |
|-----------|-----------|-------|
| `CLAUDE.md` | ~400 tokens (always-on) | Includes output contract for workers |
| Skill description | ~40 tokens (always) | Auto-invocation trigger |
| Each worker sub-agent | ~200 tokens (isolated) | Independent contexts; do not accumulate |
| Merge sub-agent | ~200 tokens + worker output | Reads all result files |
| SubagentStop hook | 0 tokens | Shell script; logs to disk |

## Complete File Implementations

### Project Memory — `CLAUDE.md`

```markdown
# Project: Acme Monorepo

## Fan-out Worker Contract
When running parallel workers, each worker MUST:
- Write its output to `.claude/fan-out-results/<worker-name>.json`
- Use the schema: `{ "worker": "<name>", "status": "success|failure", "summary": "...", "files_changed": [...], "issues": [...] }`
- Not modify files outside its assigned scope
- Run `pnpm build` within its scoped package before completing
```

### Skill — `.claude/skills/fan-out-fan-in/SKILL.md`

```yaml
---
name: fan-out-fan-in
description: >
  Runs parallel independent workers across modules/packages and merges results.
  Use when a task can be cleanly partitioned across modules, packages, or files
  with no cross-dependencies between partitions.
argument-hint: "[task-description] [module-list-or-glob]"
allowed-tools: Read, Write, Edit, Bash
---

Execute a parallel fan-out/fan-in workflow for: $ARGUMENTS

## Steps

1. **Identify work units**: Determine the list of independent modules or files to process.
   Store the manifest in `.claude/fan-out-results/manifest.json`.

2. **Clean previous results**: `rm -rf .claude/fan-out-results/*.json` (except manifest).

3. **Fan out**: For each work unit, invoke the `parallel-worker` sub-agent with:
   - The specific module/file path
   - The task description
   - The output contract from CLAUDE.md

4. **Wait for completion**: After all workers finish, verify that each has written
   a result file to `.claude/fan-out-results/`.

5. **Merge**: Invoke the `result-merger` sub-agent to reconcile all worker outputs
   into a single unified result.

6. **Report**: Present the merged result with per-worker status summary.
```

### Sub-agent — `.claude/agents/parallel-worker.md`

```yaml
---
name: parallel-worker
description: >
  Processes a single unit of work in a fan-out pipeline. Receives a scoped
  task and produces a structured result file. Use when the coordinator
  fans out work across modules.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
maxTurns: 15
---

You are a focused worker processing a single module or file.

Instructions:
1. Read only the files within your assigned scope
2. Perform the requested task on those files
3. Run `pnpm build` to verify your changes compile
4. Write your result to `.claude/fan-out-results/<your-module-name>.json` using the schema:

```json
{
  "worker": "<module-name>",
  "status": "success",
  "summary": "Brief description of what was done",
  "files_changed": ["path/to/file1.ts", "path/to/file2.ts"],
  "issues": []
}
```

If you encounter errors you cannot resolve, set `"status": "failure"` and describe
the issue in `"issues"`.

Do NOT modify files outside your assigned scope.
```

### Sub-agent — `.claude/agents/result-merger.md`

```yaml
---
name: result-merger
description: >
  Reads all worker result files from a fan-out pipeline and produces a
  unified summary. Resolves conflicts if multiple workers touched shared
  interfaces. Use after all parallel-workers complete.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Bash
disallowedTools:
  - Edit
  - MultiEdit
maxTurns: 10
---

You are the merge agent for a fan-out/fan-in pipeline.

1. Read all `.json` files in `.claude/fan-out-results/`
2. Check that all workers reported `"status": "success"`
3. If any worker failed, list the failures prominently
4. Identify any conflicting changes (e.g., two workers modifying a shared interface)
5. Run `pnpm build && pnpm test` to verify the combined result is valid
6. Produce a unified report:
   - Total workers: N
   - Succeeded: X / Failed: Y
   - Files changed (deduplicated)
   - Conflicts detected (if any)
   - Overall status: pass/fail
```

### Hook — `.claude/hooks/track-worker-completion.sh`

```bash
#!/usr/bin/env bash
# SubagentStop hook: logs worker sub-agent completion

input=$(cat)
agent_name=$(echo "$input" | jq -r '.agent_name // "unknown"')
session_id=$(echo "$input" | jq -r '.session_id // "unknown"')
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "{\"agent\": \"$agent_name\", \"completed_at\": \"$timestamp\", \"session\": \"$session_id\"}" \
  >> .claude/fan-out-results/completion-log.jsonl

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(pnpm lint:*)",
      "Bash(rm -rf .claude/fan-out-results/*.json)",
      "Bash(cat .claude/fan-out-results/*)",
      "Bash(ls .claude/fan-out-results/)"
    ],
    "deny": [
      "Bash(rm -rf /:*)",
      "Bash(git push --force:*)"
    ]
  },
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/track-worker-completion.sh"
          }
        ]
      }
    ]
  }
}
```

## Project Directory Structure

```
your-project/
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   ├── agents/
│   │   ├── parallel-worker.md
│   │   └── result-merger.md
│   ├── skills/
│   │   └── fan-out-fan-in/
│   │       └── SKILL.md
│   ├── hooks/
│   │   └── track-worker-completion.sh
│   └── fan-out-results/          ← Worker output directory (gitignored)
│       └── .gitkeep
└── packages/                     ← Or src/modules/ — the work units
    ├── auth/
    ├── billing/
    └── notifications/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Worker modifies files outside its scope | CLAUDE.md contract explicitly forbids cross-scope writes; add a PostToolUse hook to validate write paths |
| Workers produce inconsistent output formats | Shared contract in CLAUDE.md; merger validates schema before reconciling |
| Runaway worker loops | `maxTurns: 15` cap per worker |
| Merge agent overwrites worker fixes | Merger has `disallowedTools: [Edit, MultiEdit]`; it reads and reports only |

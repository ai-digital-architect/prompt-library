# Pattern 33: Map-Reduce

## Category
Orchestration Meta-Workflows

## Overview

A coordinator fans out over a list (files, modules, endpoints, test suites) and invokes a worker sub-agent for each item independently. A `SubagentStop` hook logs each worker's result. When all workers are done, a reducer sub-agent aggregates the individual results into a unified output.

## Architecture Diagram

```
User invokes /map-reduce
        │
        ▼
┌──────────────────────────┐
│  Coordinator (Skill)      │
│  1. Enumerate work items  │
│  2. Map: fan out workers  │
│  3. Reduce: aggregate     │
└──┬───┬───┬───┬───────────┘
   │   │   │   │         (MAP phase)
   ▼   ▼   ▼   ▼
┌────┐┌────┐┌────┐┌────┐
│W-1 ││W-2 ││W-3 ││W-N │    Worker sub-agents (isolated)
└─┬──┘└─┬──┘└─┬──┘└─┬──┘
  │     │     │     │
  ▼     ▼     ▼     ▼
SubagentStop hooks → .claude/map-reduce/results/
  │     │     │     │
  └─────┴─────┴─────┘
          │              (REDUCE phase)
          ▼
  ┌──────────────┐
  │  Reducer      │
  │  (read-only)  │
  │  - Reads all  │
  │    results    │
  │  - Aggregates │
  │  - Summarizes │
  └──────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/map-reduce/SKILL.md`

```yaml
---
name: map-reduce
description: >
  Fans out a task across multiple items (files, modules, endpoints) using
  independent worker sub-agents, then reduces results into a unified output.
  Use for bulk operations across many files or modules.
argument-hint: "[task] [item-list-or-glob]"
allowed-tools: Read, Write, Edit, Bash
---

Execute map-reduce: $ARGUMENTS

## Phase 1: Enumerate (Coordinator)
1. Parse the item list from arguments or discover items via glob/find
2. Write manifest to `.claude/map-reduce/manifest.json`:
   ```json
   { "task": "...", "items": ["item1", "item2", ...], "total": N }
   ```
3. Clean previous results: `rm -rf .claude/map-reduce/results/`

## Phase 2: Map (Fan-out)
4. For each item, invoke the `mr-worker` sub-agent with:
   - The item identifier (file path, module name, etc.)
   - The task description
   - Worker writes result to `.claude/map-reduce/results/<item-id>.json`

## Phase 3: Reduce (Aggregation)
5. After all workers complete, invoke the `mr-reducer` sub-agent
6. Reducer reads all result files and produces unified output
7. Present the aggregated result
```

### Sub-agent — `.claude/agents/mr-worker.md`

```yaml
---
name: mr-worker
description: >
  Processes a single item in a map-reduce pipeline. Receives one item
  and the task description, performs the work, and writes a structured result.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
maxTurns: 12
---

Process the assigned item for the map-reduce task.

1. Read the item (file, module, endpoint) as specified
2. Perform the requested task on this item only
3. Write result to `.claude/map-reduce/results/<item-id>.json`:

```json
{
  "item": "<identifier>",
  "status": "success|failure|skipped",
  "output": { ... },
  "files_changed": [],
  "errors": [],
  "duration_seconds": 0
}
```

Stay within scope — do NOT process other items or modify shared resources.
```

### Sub-agent — `.claude/agents/mr-reducer.md`

```yaml
---
name: mr-reducer
description: >
  Aggregates results from all map-reduce workers into a unified summary.
  Handles partial failures gracefully. Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 8
---

Aggregate all map-reduce results.

1. Read manifest from `.claude/map-reduce/manifest.json`
2. Read all result files from `.claude/map-reduce/results/`
3. Verify all items have results (identify missing workers)
4. Aggregate:
   - Total items: N
   - Succeeded: X
   - Failed: Y
   - Skipped: Z
   - Per-item summaries
5. If task produced data, combine into unified output
6. If task produced code changes, list all files modified across all workers

Write unified output to `.claude/map-reduce/aggregate.md`.
```

### Hook — `.claude/hooks/mr-track-completion.sh`

```bash
#!/usr/bin/env bash
# SubagentStop hook: tracks map-reduce worker completions

input=$(cat)
agent_name=$(echo "$input" | jq -r '.agent_name // ""')

if [[ "$agent_name" != "mr-worker" ]]; then
  exit 0
fi

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"agent\": \"$agent_name\", \"completed_at\": \"$timestamp\"}" \
  >> .claude/map-reduce/completion.jsonl

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(find *)",
      "Bash(ls .claude/map-reduce/*)",
      "Bash(cat .claude/map-reduce/*)",
      "Bash(rm -rf .claude/map-reduce/results/*)",
      "Bash(mkdir -p .claude/map-reduce/results)",
      "Bash(wc -l .claude/map-reduce/*)"
    ]
  },
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/mr-track-completion.sh"
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
│   │   ├── mr-worker.md
│   │   └── mr-reducer.md
│   ├── skills/
│   │   └── map-reduce/
│   │       └── SKILL.md
│   ├── hooks/
│   │   └── mr-track-completion.sh
│   └── map-reduce/              ← Working directory (gitignored)
│       ├── manifest.json
│       ├── completion.jsonl
│       ├── aggregate.md
│       └── results/
│           ├── item-1.json
│           ├── item-2.json
│           └── item-N.json
└── src/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Worker modifies items outside its scope | Instructions explicitly prohibit cross-item changes; add path-validation hook for strict enforcement |
| Reducer modifies source code | `disallowedTools: [Write, Edit, MultiEdit]` — aggregation only |
| Worker count exceeds token budget | Coordinator can batch items or limit parallelism based on cost estimates |
| Partial failure leaves inconsistent state | Reducer reports missing/failed items; coordinator can re-run failed workers |

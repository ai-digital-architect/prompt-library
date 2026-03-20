# Pattern 12: Database Schema Evolution

## Category
Refactoring & Migration Workflows

## Overview

A sequential pipeline: schema diff sub-agent → migration script generator → backwards-compatibility checker → rollout plan producer. Each stage gates on the previous output, and a hook validates that the migration is reversible before the plan is finalized.

## Architecture Diagram

```
User invokes /schema-evolve
        │
        ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Schema Differ    │───▶│ Migration Gen    │───▶│ Compat Checker   │───▶│ Rollout Planner │
│ (read-only)      │    │ (write-capable)   │    │ (read-only)       │    │ (read-only)      │
│ - Compares old   │    │ - Generates SQL   │    │ - Checks backward │    │ - Produces plan  │
│   vs new schema  │    │   migration files │    │   compatibility    │    │ - Includes       │
│ - Produces diff  │    │ - Up + down       │    │ - Validates        │    │   rollback steps │
└─────────────────┘    └──────────────────┘    │   reversibility    │    └─────────────────┘
                                                └──────────────────┘
                                                        │
                                               PreToolUse Hook
                                               (blocks if migration
                                                is not reversible)
```

## Complete File Implementations

### Skill — `.claude/skills/schema-evolve/SKILL.md`

```yaml
---
name: schema-evolve
description: >
  Evolves database schema through a gated pipeline: diff → generate migration →
  check compatibility → produce rollout plan. Each stage validates before the
  next proceeds. Use for any database schema change.
argument-hint: "[description of schema change]"
allowed-tools: Read, Write, Edit, Bash
---

Evolve database schema: $ARGUMENTS

## Stage 1: Schema Diff
Invoke `schema-differ` to compare current schema against the requested change.
Output: `.claude/schema/diff.json`

## Stage 2: Generate Migration
Invoke `migration-generator` to produce up/down migration scripts.
Output: `migrations/<timestamp>_<name>.sql`

## Stage 3: Compatibility Check
Invoke `compat-checker` to verify backward compatibility and reversibility.
Output: `.claude/schema/compat-report.json`
If the migration is NOT reversible, STOP and report the issue.

## Stage 4: Rollout Plan
Invoke `rollout-planner` to produce a deployment plan.
Output: `.claude/schema/rollout-plan.md`

Present the complete plan for human review.
```

### Sub-agent — `.claude/agents/schema-differ.md`

```yaml
---
name: schema-differ
description: >
  Compares current database schema against a proposed change and produces
  a structured diff. Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 8
---

Analyze the current schema and produce a diff for the requested change.

1. Read current schema files in `src/db/schema/`
2. Identify what needs to change (new tables, altered columns, new indexes)
3. Write diff to `.claude/schema/diff.json`:
   ```json
   {
     "additions": [{"type": "table", "name": "...", "columns": [...]}],
     "modifications": [{"type": "column", "table": "...", "column": "...", "from": "...", "to": "..."}],
     "deletions": [],
     "risk_level": "low|medium|high"
   }
   ```
```

### Sub-agent — `.claude/agents/migration-generator.md`

```yaml
---
name: migration-generator
description: >
  Generates SQL migration files (up and down) from a schema diff.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Bash
maxTurns: 10
---

Read `.claude/schema/diff.json` and generate migration files.

1. Create `migrations/<timestamp>_<descriptive-name>.up.sql` (forward migration)
2. Create `migrations/<timestamp>_<descriptive-name>.down.sql` (rollback migration)
3. Ensure both files are syntactically valid SQL
4. The down migration must exactly reverse the up migration
5. Run `pnpm db:validate` if available
```

### Sub-agent — `.claude/agents/compat-checker.md`

```yaml
---
name: compat-checker
description: >
  Validates that a database migration is backward-compatible and reversible.
  Read-only. Blocks the pipeline if migration cannot be safely rolled back.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 8
---

Validate the migration files for backward compatibility.

Check:
1. Can the application run against BOTH the old and new schema during deployment?
2. Are there destructive operations (DROP COLUMN, DROP TABLE) that lose data?
3. Does the down migration exactly reverse the up migration?
4. Are there lock-heavy operations (ALTER TABLE on large tables)?

Write report to `.claude/schema/compat-report.json`:
```json
{
  "reversible": true,
  "backward_compatible": true,
  "risks": [],
  "blocking_issues": [],
  "recommendations": []
}
```

If `reversible` is false or `blocking_issues` is non-empty, the pipeline must stop.
```

### Hook — `.claude/hooks/require-reversible-migration.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: blocks rollout plan generation if migration is not reversible

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only gate on rollout-related operations
if ! echo "$command" | grep -q "rollout"; then
  exit 0
fi

report=".claude/schema/compat-report.json"
if [[ ! -f "$report" ]]; then
  echo '{"decision": "block", "reason": "Compatibility report not found. Run compat-checker first."}' >&2
  exit 2
fi

reversible=$(jq -r '.reversible' "$report")
blocking=$(jq -r '.blocking_issues | length' "$report")

if [[ "$reversible" != "true" ]] || [[ "$blocking" -gt 0 ]]; then
  echo '{"decision": "block", "reason": "Migration is not reversible or has blocking issues. Cannot proceed to rollout."}' >&2
  exit 2
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm db:*)",
      "Bash(pnpm build:*)",
      "Bash(cat migrations/*)",
      "Bash(ls migrations/)",
      "Bash(mkdir -p .claude/schema)"
    ],
    "deny": [
      "Bash(psql * DROP DATABASE:*)",
      "Bash(rm -rf /:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/require-reversible-migration.sh"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Irreversible migration deployed | Compat-checker + hook blocks rollout if not reversible |
| Migration runs against production DB | All operations target dev; deployer requires explicit env flag |
| Schema differ produces inaccurate diff | Uses `claude-opus-4-5` for compat-checker (higher accuracy on critical check) |
| Data-destructive DDL slips through | Compat-checker explicitly flags DROP operations |

# Pattern 10: Incremental Migration

## Category
Refactoring & Migration Workflows

## Overview

Migrates one module at a time through a sequential pipeline. Each module's migration is a sub-agent invocation. A `PostToolUse` hook runs the test suite after each module and blocks progression to the next if tests fail, ensuring the build is never broken mid-migration.

## Architecture Diagram

```
User invokes /incremental-migrate
        │
        ▼
┌───────────────────────┐
│  Coordinator (Skill)   │
│  - Lists modules       │
│  - Processes one by one│
└────────┬──────────────┘
         │
    ┌────┴────┐
    ▼         │
┌──────────┐  │   PostToolUse Hook
│ Module A  │──┤──(pnpm test → pass?)
│ migration │  │   ✅ → next module
│ (agent)   │  │   ❌ → block; fix first
└──────────┘  │
    ┌─────────┘
    ▼
┌──────────┐
│ Module B  │── PostToolUse Hook ── ...
│ migration │
└──────────┘
    ...
    ▼
  All modules complete → Stop Hook → notify
```

## Complete File Implementations

### Skill — `.claude/skills/incremental-migrate/SKILL.md`

```yaml
---
name: incremental-migrate
description: >
  Migrates modules one at a time, running full test suite between each.
  Never breaks the build mid-migration. Use for framework upgrades,
  API version migrations, or pattern replacements across modules.
argument-hint: "[migration-description] [module-list-or-auto]"
allowed-tools: Read, Write, Edit, Bash
---

Execute incremental migration: $ARGUMENTS

## Workflow

1. **Discover modules**: List all modules to migrate (from arguments or auto-detect)
2. **For each module** (sequential, one at a time):
   a. Invoke the `module-migrator` sub-agent with the module path and migration spec
   b. After the sub-agent completes, run `pnpm build && pnpm test`
   c. If tests fail: fix the failures before moving to the next module
   d. If tests pass: log success and proceed to next module
   e. Write progress to `.claude/migration/progress.json`
3. **After all modules**: Run full test suite one final time
4. **Report**: Migration summary with per-module status
```

### Sub-agent — `.claude/agents/module-migrator.md`

```yaml
---
name: module-migrator
description: >
  Migrates a single module according to a migration specification.
  Makes changes, updates imports, and ensures the module compiles.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Bash
maxTurns: 20
---

Migrate the specified module. Follow the migration spec exactly.

1. Read the module's current code
2. Apply the migration changes (API updates, import changes, pattern swaps)
3. Update all internal imports and references
4. Update the module's tests to match new patterns
5. Run `pnpm build` to verify compilation
6. Write result to `.claude/migration/modules/<module-name>.json`:
   ```json
   { "module": "<n>", "status": "success|failure", "files_changed": [...], "notes": "..." }
   ```
```

### Hook — `.claude/hooks/migration-gate.sh`

```bash
#!/usr/bin/env bash
# PostToolUse hook: runs test suite after file modifications during migration

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only gate on source file changes
if [[ "$file_path" != src/* ]] && [[ "$file_path" != packages/* ]]; then
  exit 0
fi

# Run build check
if ! pnpm build --silent 2>/dev/null; then
  echo '{"reason": "Build failed after modifying '"$file_path"'. Fix before continuing migration."}' >&2
  exit 2
fi

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
      "Bash(find * -type d -name src)",
      "Bash(ls packages/)",
      "Bash(cat .claude/migration/*)",
      "Bash(mkdir -p .claude/migration/modules)"
    ],
    "deny": [
      "Bash(rm -rf /:*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/migration-gate.sh"
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
| Migration breaks build for other modules | PostToolUse hook blocks on compile failure; strictly sequential processing |
| Migrator changes files outside its module | Skill specifies module scope; could add path-validation hook |
| Loss of progress on session timeout | Progress file `.claude/migration/progress.json` enables resumption |
| Tests pass individually but full suite fails | Final full test run catches integration-level regressions |

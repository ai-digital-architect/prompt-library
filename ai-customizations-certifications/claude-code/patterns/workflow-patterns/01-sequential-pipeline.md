# Pattern 01: Sequential Pipeline

## Category
Pipeline & Ordering Workflows

## Overview

A strict stage-by-stage execution workflow where each step gates the next. The pipeline ensures that no downstream stage begins until the upstream stage passes validation. Typical use cases include full-stack feature scaffolding (schema → entity → API → UI → tests) or multi-phase build processes.

## Architecture Diagram

```
User invokes /sequential-pipeline
        │
        ▼
┌─────────────────┐     PostToolUse Hook      ┌──────────────────┐
│  Stage 1:       │────(compile/test gate)────▶│  Stage 2:        │
│  Schema Design  │     Pass? → continue       │  Entity Layer    │
│  (sub-agent)    │     Fail? → block + report │  (sub-agent)     │
└─────────────────┘                            └────────┬─────────┘
                                                        │
                                               PostToolUse Hook
                                               (compile/test gate)
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │  Stage 3:        │
                                               │  API Routes      │
                                               │  (sub-agent)     │
                                               └────────┬─────────┘
                                                        │
                                               PostToolUse Hook
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │  Stage 4:        │
                                               │  Tests           │
                                               │  (sub-agent)     │
                                               └──────────────────┘
                                                        │
                                                  Stop Hook
                                               (notify complete)
```

## Component Breakdown

| Component | Role | Why This Component |
|-----------|------|--------------------|
| **Skill** (`.claude/skills/sequential-pipeline/`) | Entry point; orchestrates stage order | User-triggered + Claude auto-invocable; preferred over slash commands |
| **Sub-agents** (`.claude/agents/`) | One per pipeline stage | Isolated context per stage; least-privilege tool access |
| **PostToolUse Hook** | Gate between stages | Deterministic enforcement; zero tokens; blocks on test/compile failure |
| **Stop Hook** | Completion notification | Fires when the full pipeline finishes |
| **CLAUDE.md** | Shared conventions for all stages | Always-on standards that every sub-agent inherits |

## Token Cost Analysis

| Component | Token Cost | Notes |
|-----------|-----------|-------|
| `CLAUDE.md` | ~400 tokens (always-on) | Shared conventions; loaded once per session |
| Skill description | ~40 tokens (always in context) | Enables Claude auto-invocation |
| Skill body | ~200 tokens (on invocation) | Only loaded when pipeline starts |
| Each sub-agent | ~150–300 tokens (isolated) | Fresh context per stage; no accumulation |
| Hooks | 0 tokens | Shell scripts; bypass model entirely |

## Complete File Implementations

### Project Memory — `CLAUDE.md`

```markdown
# Project: Acme Platform

## Build & Test Commands
- Build: `pnpm build`
- Test (all): `pnpm test`
- Test (single): `pnpm test -- <file>`
- Lint: `pnpm lint:fix`
- Type check: `pnpm typecheck`
- DB migrations: `pnpm db:migrate`

## Architecture
- Route handlers are thin — business logic lives in service files
- All DB queries go through the repository layer
- Co-locate tests next to source: `auth.service.ts` → `auth.service.test.ts`

## Sequential Pipeline Conventions
- Each pipeline stage must pass `pnpm build && pnpm test` before the next stage begins
- Sub-agents produce artifacts in `src/` following existing module structure
- Schema changes always come before entity/service/route changes
```

### Skill — `.claude/skills/sequential-pipeline/SKILL.md`

```yaml
---
name: sequential-pipeline
description: >
  Executes a strict stage-by-stage feature implementation pipeline:
  schema → entity → service → API route → tests. Each stage must pass
  build and test before the next begins. Trigger when user asks to
  scaffold a full feature, build a complete endpoint, or implement
  something end-to-end.
argument-hint: "[feature-name] [description]"
allowed-tools: Read, Write, Edit, Bash
---

Implement the following feature through a strict sequential pipeline: $ARGUMENTS

## Pipeline Stages (execute in exact order)

### Stage 1: Schema Design
Invoke the `schema-designer` sub-agent with the feature description.
Wait for completion. Run `pnpm build && pnpm test` — do NOT proceed if either fails.

### Stage 2: Entity & Repository Layer
Invoke the `entity-builder` sub-agent with the schema output from Stage 1.
Wait for completion. Run `pnpm build && pnpm test` — do NOT proceed if either fails.

### Stage 3: Service Layer
Invoke the `service-builder` sub-agent with context from Stages 1–2.
Wait for completion. Run `pnpm build && pnpm test` — do NOT proceed if either fails.

### Stage 4: API Route
Invoke the `route-builder` sub-agent with context from Stages 1–3.
Wait for completion. Run `pnpm build && pnpm test` — do NOT proceed if either fails.

### Stage 5: Integration Tests
Invoke the `test-writer` sub-agent covering all layers.
Run `pnpm test` — fix any failures before presenting results.

Present a summary of all files created, grouped by stage.
```

### Sub-agent — `.claude/agents/schema-designer.md`

```yaml
---
name: schema-designer
description: >
  Designs database schema changes (Drizzle ORM migrations) for a new feature.
  Use as the first stage of a sequential pipeline.
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

You are a database schema specialist. Given a feature description:

1. Read existing schemas in `src/db/schema/` to understand current structure
2. Design the new table(s) or column additions needed
3. Create the Drizzle schema file in `src/db/schema/<feature>.ts`
4. Generate the migration with `pnpm db:generate`
5. Verify the migration compiles: `pnpm build`

Return: list of schema files created, table/column names, and any foreign key relationships.
```

### Sub-agent — `.claude/agents/entity-builder.md`

```yaml
---
name: entity-builder
description: >
  Creates the entity types and repository layer for a database schema.
  Use after schema-designer in a sequential pipeline.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Bash
disallowedTools:
  - MultiEdit
maxTurns: 10
---

You are a repository layer specialist. Given a schema definition:

1. Read the schema files in `src/db/schema/` to understand the new tables
2. Create TypeScript entity types in `src/entities/<feature>.entity.ts`
3. Create the repository in `src/repositories/<feature>.repository.ts`
4. Ensure all queries use Drizzle ORM — no raw SQL
5. Verify: `pnpm build`

Return: entity types created and repository method signatures.
```

### Sub-agent — `.claude/agents/service-builder.md`

```yaml
---
name: service-builder
description: >
  Implements the business logic service layer for a feature.
  Use after entity-builder in a sequential pipeline.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
maxTurns: 12
---

You are a service layer specialist. Given entity types and repository methods:

1. Create the service in `src/services/<feature>.service.ts`
2. All business logic lives here — routes must stay thin
3. Return `Result<T, AppError>` types, not thrown exceptions
4. Add JSDoc with @param and @returns on every function
5. Verify: `pnpm build`

Return: service file path and public method signatures.
```

### Sub-agent — `.claude/agents/route-builder.md`

```yaml
---
name: route-builder
description: >
  Creates API route handlers that delegate to service layer.
  Use after service-builder in a sequential pipeline.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
maxTurns: 10
---

You are an API route specialist. Given service methods:

1. Create the route handler in `src/routes/<feature>.routes.ts`
2. Route handlers must be thin: validate input → call service → return response
3. Include OpenAPI annotations for each endpoint
4. Register routes in the main router
5. Verify: `pnpm build`

Return: route paths, HTTP methods, and request/response shapes.
```

### Sub-agent — `.claude/agents/test-writer.md`

```yaml
---
name: test-writer
description: >
  Writes integration and unit tests for a completed feature.
  Use as the final stage of a sequential pipeline.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
maxTurns: 15
---

You are a test specialist. Given completed feature files:

1. Read all source files for the feature
2. Write unit tests co-located with source: `<name>.test.ts`
3. Write integration tests in `tests/integration/<feature>/`
4. Cover: happy path, validation errors, auth failures, edge cases
5. Run `pnpm test` and fix any failures

Return: test file paths and coverage summary.
```

### Hook — `.claude/hooks/pipeline-gate.sh`

```bash
#!/usr/bin/env bash
# PostToolUse hook: runs build + test after every Write/Edit to enforce pipeline gates
# Exit 0 = allow; Exit 2 = block

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only gate on source file writes (not config, not tests during final stage)
if [[ "$file_path" != src/* ]]; then
  exit 0
fi

# Run build check
if ! pnpm build --silent 2>/dev/null; then
  echo '{"reason": "Build failed after writing '"$file_path"'. Fix compilation errors before proceeding."}' >&2
  exit 2
fi

exit 0
```

### Hook — `.claude/hooks/notify-pipeline-complete.sh`

```bash
#!/usr/bin/env bash
# Stop hook: fires when the pipeline session completes

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[$timestamp] Sequential pipeline completed" >> ~/.claude/pipeline.log

# Optional: Slack notification
# curl -s -X POST "$SLACK_WEBHOOK_URL" \
#   -H 'Content-Type: application/json' \
#   -d "{\"text\": \"Sequential pipeline completed at $timestamp\"}"

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
      "Bash(pnpm db:generate:*)",
      "Bash(pnpm db:migrate:*)",
      "Bash(git diff:*)",
      "Bash(git status:*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force:*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/pipeline-gate.sh"
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
            "command": "bash .claude/hooks/notify-pipeline-complete.sh"
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
│   │   ├── schema-designer.md
│   │   ├── entity-builder.md
│   │   ├── service-builder.md
│   │   ├── route-builder.md
│   │   └── test-writer.md
│   ├── skills/
│   │   └── sequential-pipeline/
│   │       └── SKILL.md
│   └── hooks/
│       ├── pipeline-gate.sh
│       └── notify-pipeline-complete.sh
└── src/
    ├── db/schema/
    ├── entities/
    ├── repositories/
    ├── services/
    └── routes/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Sub-agent writes breaking code and pipeline continues | PostToolUse hook runs `pnpm build` after every write; exits 2 on failure |
| Schema designer creates destructive migration | Limit `schema-designer` to `Write` (no `Edit`/`MultiEdit`); review generated migrations |
| Test writer modifies source files | Scope test-writer to `Write` only in test directories via hook validation |
| Pipeline runs indefinitely | `maxTurns` cap on each sub-agent (10–15 turns) |

# Track A: File-Based Memory Implementation for Claude Code

## Overview

This track implements the six-memory architecture using Markdown files, `CLAUDE.md`, and Claude Code's auto-memory system. Zero external infrastructure. All project memory is version-controlled. Personal memory persists in `~/.claude/`.

## Step 1: Create the Directory Structure

```bash
mkdir -p .claude/memory/{episodic,semantic,procedural}
```

Resulting layout:

```
project-root/
  CLAUDE.md                          # Auto-loaded every session (semantic + procedural core)
  .claude/
    memory/
      episodic/                      # Decision records, incidents, milestones
      semantic/                      # Domain models, detailed standards
      procedural/                    # Workflow guides, automation patterns

~/.claude/projects/<project-path>/
  memory/
    MEMORY.md                        # Auto-loaded personal memory (long-term)
    *.md                             # Additional personal memory files
```

## Step 2: Create the CLAUDE.md Foundation (Semantic + Procedural Core)

The `CLAUDE.md` file is loaded into every Claude Code session. It is the primary vehicle for semantic memory (project facts/rules) and procedural memory (workflow instructions).

### File: `CLAUDE.md`

```markdown
# CLAUDE.md

## Project Identity
- **Name**: [PROJECT_NAME]
- **Type**: [web-app | api | library | cli]
- **Language**: [TypeScript | Python | Go]
- **Framework**: [React | Next.js | Express | FastAPI]
- **Database**: [PostgreSQL | MongoDB]
- **Hosting**: [AWS | GCP | Vercel]

## Architecture
- **Style**: [monolith | microservices | serverless]
- **Key Services**: [list]
- **CI/CD**: GitHub Actions

## Coding Standards
- Naming: camelCase for variables/functions, PascalCase for types/classes
- Max function length: 30 lines
- Max file length: 300 lines
- Imports: grouped (stdlib, external, internal, relative)
- Error handling: typed errors, never throw raw strings
- Testing: [framework], co-located test files, [coverage target]

## API Standards
- REST, /api/v1/resource, Bearer JWT
- Response shape: { data: T, error?: { code, message }, meta?: { page, total } }
- Pagination: cursor-based

## Business Rules
- [Rule 1]
- [Rule 2]

## Development Workflows
- **Feature**: Branch `feat/ISSUE-slug` from main, draft PR, conventional commits, squash-merge
- **Bug fix**: Write failing test first, fix, verify, PR with `Fixes #ISSUE`
- **Migration**: Generate, review SQL, test rollback, update seeds, test staging

## Memory System
This project uses a structured memory system. See `.claude/memory/` for:
- `episodic/` — Past decisions and events. Read before architectural decisions.
- `semantic/` — Domain models and detailed standards. Read for domain questions.
- `procedural/` — Detailed workflow guides. Read when starting standard tasks.

When making significant decisions, record them in `.claude/memory/episodic/`.
When discovering new project rules, update this file or `.claude/memory/semantic/`.
When refining workflows, update `.claude/memory/procedural/`.
```

**Key constraint**: Keep CLAUDE.md under ~200 lines of actionable content. It's loaded every session — bloat wastes context. Link to detail files for depth.

## Step 3: Create Semantic Memory Detail Files

### File: `.claude/memory/semantic/domain-models.md`

```markdown
# Domain Models

## User
- **Table**: `users`
- **Properties**: id (UUID, PK), email (unique, verified), name (varchar 255), role (enum: admin|member|viewer), created_at, updated_at, deleted_at (soft delete)
- **Relationships**: has many Projects (as owner), has many TeamMemberships, has many Notifications
- **Business Rules**:
  - Email must be verified before any write operations
  - Soft-delete only — never hard delete user records
  - Role changes require admin approval
  - Email uniqueness is case-insensitive

## Project
- **Table**: `projects`
- **Properties**: id (UUID, PK), name (varchar 255), owner_id (FK users), status (enum: draft|active|archived), settings (JSONB), created_at, updated_at
- **Relationships**: belongs to User (owner), has many Members (through team_memberships), has many Resources
- **Business Rules**:
  - Archived projects are read-only
  - Name must be unique per owner
  - Deleting a project archives it (soft transition)
  - Settings JSONB has typed overlay: ProjectSettings interface

## Notification
- **Table**: `notifications`
- **Properties**: id (UUID, PK), user_id (FK users), type (enum), channel (enum: email|push|in_app), payload (JSONB), read_at (nullable timestamp), created_at
- **Business Rules**:
  - Respect user channel preferences before sending
  - Batch similar notifications within 5-minute window
  - Unread notifications older than 90 days are auto-archived
```

### File: `.claude/memory/semantic/infrastructure.md`

```markdown
# Infrastructure

## Environments
| Environment | URL | Database | Purpose |
|---|---|---|---|
| Local | localhost:3000 | localhost:5432/dev | Development |
| Staging | staging.example.com | staging-db.internal | Pre-production testing |
| Production | app.example.com | prod-db.internal | Live traffic |

## Key Configuration
- **Environment variables**: Managed via `.env.local` (dev), AWS Parameter Store (staging/prod)
- **Secrets**: AWS Secrets Manager, never committed to git
- **Feature flags**: LaunchDarkly, server-side SDK

## Deployment
- Main branch deploys to staging automatically via GitHub Actions
- Production deploy requires manual approval in GitHub Actions UI
- Rollback: Revert the merge commit and push to main
- Database migrations run as part of deploy pipeline (pre-container-swap)

## Monitoring
- **Logs**: CloudWatch Logs, structured JSON format
- **Metrics**: CloudWatch Metrics + Datadog
- **Alerts**: PagerDuty for P1/P2, Slack #alerts for P3/P4
- **Error tracking**: Sentry
```

## File Format Decision

All Track A memory files use **Markdown**. Episodic entries additionally use **YAML frontmatter** for structured metadata that enables scripted queries and automated clearing. Semantic, procedural, and long-term files are plain Markdown.

**Why not JSON?** Memory entries contain narrative content (context, rationale, code blocks, lessons) that is unreadable when stuffed into JSON string fields. YAML frontmatter on episodic entries provides structured queryability (date, category, impact, tags) while keeping the narrative body in clean Markdown. An optional auto-generated `_index.json` enables jq-based automation for teams that need it.

Claude Code reads Markdown natively via the Read tool. `CLAUDE.md` and `MEMORY.md` are Markdown by design. Using JSON for any memory type would create a format mismatch with the platform's native mechanisms.

## Step 4: Create the Episodic Memory System

### File: `.claude/memory/episodic/TEMPLATE.md`

```markdown
---
date: "YYYY-MM-DD"
category: ARCH            # ARCH | TECH | INC | MEET | DEBUG | MILE
impact: high              # critical | high | medium | low
tags: []                  # e.g., [database, migration, zero-downtime]
participants: []          # e.g., [tech-lead, backend-team]
related: []               # e.g., ["#142", "ARCH-2025-01-10"]
retain: false             # true = exempt from automatic clearing
---

# Event Title

## Context
[What prompted this event?]

## Decision
[What was decided or done?]

## Alternatives Considered
- Option A: [description] — rejected because [reason]
- Option B: [description] — rejected because [reason]

## Rationale
[Why this approach was chosen]

## Outcome
[Results. Update post-facto.]

## Lessons
[What to remember next time.]
```

### Example: `.claude/memory/episodic/2025-02-10-auth-migration.md`

```markdown
---
date: "2025-02-10"
category: ARCH
impact: high
tags: [authentication, jwt, redis, scaling]
participants: [backend-team]
related: []
retain: false
---

# Migration from Session-Based to JWT Authentication

## Context
Session-based auth using express-session + Redis was causing scaling issues.
Each ECS task needed Redis connection, and session affinity complicated load balancing.

## Decision
Migrated to stateless JWT tokens with short-lived access tokens (15min) and
refresh tokens (7 days, stored in httpOnly cookie).

## Alternatives Considered
- Session store in PostgreSQL — rejected: still stateful, added DB load
- Session store in DynamoDB — rejected: added AWS dependency for simple auth

## Rationale
Stateless JWT eliminates session store entirely. Short-lived access tokens
limit exposure window. Refresh rotation prevents token theft persistence.

## Outcome
Redis removed from infrastructure. Horizontal scaling simplified.
Auth latency reduced from ~15ms (Redis lookup) to ~2ms (JWT verification).

## Lessons
- Always consider stateless alternatives before adding shared state
- Short-lived tokens + refresh rotation is the right default for web APIs
- httpOnly cookies for refresh tokens prevent XSS-based token theft
```

### Auto-generated Episodic Index: `.claude/memory/episodic/_index.json`

For teams that need scripted queries or automated clearing, an `_index.json` file can be auto-generated from YAML frontmatter. Claude Code itself can generate this via a Bash command:

```bash
python3 -c "
import json, re, glob, yaml
entries = []
for path in sorted(glob.glob('.claude/memory/episodic/*.md')):
    if 'TEMPLATE' in path:
        continue
    with open(path) as f:
        content = f.read()
    match = re.match(r'^---\n(.+?)\n---\n(.+)', content, re.DOTALL)
    if not match:
        continue
    meta = yaml.safe_load(match.group(1))
    title_match = re.search(r'^# (.+)$', match.group(2), re.MULTILINE)
    entries.append({
        'file': path.split('/')[-1],
        'date': str(meta.get('date', '')),
        'category': meta.get('category', ''),
        'impact': meta.get('impact', ''),
        'tags': meta.get('tags', []),
        'title': title_match.group(1) if title_match else path.split('/')[-1],
        'retain': meta.get('retain', False),
    })
with open('.claude/memory/episodic/_index.json', 'w') as f:
    json.dump(entries, f, indent=2)
print(f'Rebuilt {len(entries)} entries')
"
```

**jq queries** (same as Copilot — see the Copilot Track A guide for the full set):

```bash
# Entries eligible for clearing (older than 180 days, not retained)
jq --arg cutoff "$(date -v-180d +%Y-%m-%d 2>/dev/null || date -d '-180 days' +%Y-%m-%d)" \
  '[.[] | select(.date < $cutoff and .retain != true)]' \
  .claude/memory/episodic/_index.json
```

### Agent Protocol for Episodic Memory

Add to CLAUDE.md:

```markdown
## Episodic Memory Protocol
Before making architectural decisions:
1. List files: `Glob .claude/memory/episodic/*.md`
2. Read relevant entries based on category/date
3. Reference past decisions and lessons in your reasoning
4. After the decision, create a new episodic entry
```

## Step 5: Create the Procedural Memory System

### File: `.claude/memory/procedural/feature-workflow.md`

```markdown
# Feature Development Workflow

## When to Use
Starting any new feature (issue-driven or ad-hoc).

## Steps

### 1. Branch Creation
```bash
git checkout main && git pull
git checkout -b feat/ISSUE-NUMBER-short-description
```

### 2. Draft PR
```bash
gh pr create --draft \
  --title "feat(scope): description" \
  --body "Resolves #ISSUE-NUMBER

## Summary
- [Bullet points of what this PR does]

## Test Plan
- [ ] Unit tests added
- [ ] Integration test added
- [ ] Manual testing completed"
```

### 3. Implementation
- Follow conventional commits: `feat(scope): description`
- One logical change per commit
- Keep commits atomic and revertable

### 4. Pre-Review Checklist
```bash
npm run lint
npm run test
npm run build
```

### 5. Ready for Review
```bash
gh pr ready
gh pr edit --add-reviewer teammate1,teammate2
```

### 6. Post-Merge
```bash
git checkout main && git pull
git branch -d feat/ISSUE-NUMBER-short-description
```
```

### File: `.claude/memory/procedural/debugging-workflow.md`

```markdown
# Debugging Workflow

## When to Use
Bug report received, test failure, unexpected behavior.

## Steps

### 1. Reproduce
- Get exact reproduction steps
- Identify environment (local, staging, prod)
- Note expected vs actual behavior

### 2. Isolate
- Find the smallest reproduction case
- Check if it's a regression (git bisect if needed)
- Identify the subsystem involved

### 3. Hypothesize
- Form 2-3 hypotheses for the root cause
- Use TodoWrite to track:
  ```
  - [ ] Hypothesis 1: [description]
  - [ ] Hypothesis 2: [description]
  ```

### 4. Test Hypotheses
- Add logging or breakpoints
- Check each hypothesis systematically
- Eliminate hypotheses with evidence

### 5. Fix
- Write a failing test that reproduces the bug
- Implement the minimal fix
- Verify the test passes
- Check for related edge cases

### 6. Record
- If significant, write to `.claude/memory/episodic/`
- If it reveals a new rule, update CLAUDE.md or semantic memory
- If it improves a workflow, update procedural memory
```

## Step 6: Configure Long-term Memory (Auto-Memory)

Claude Code's auto-memory directory is at `~/.claude/projects/<project-path>/memory/`.

### File: `~/.claude/projects/<project-path>/memory/MEMORY.md`

This file is auto-loaded (first 200 lines) into every session for this project.

```markdown
# Project Memory

## User Preferences
- Early returns over nested conditionals
- Composition over inheritance
- TypeScript strict mode always
- Integration tests first, unit tests for complex logic
- Explicit error handling over broad try-catch
- Readability over cleverness

## Learned Patterns
- Prefers JSONB with TypeScript type overlays for flexible schemas
- Uses Zod for runtime validation at API boundaries
- Prefers co-located test files over separate __tests__ directories
- Uses barrel exports (index.ts) for public module APIs

## Project-Specific Knowledge
- The notification batching logic in src/services/notifications.ts is complex; read carefully before modifying
- Database migrations must be tested against staging dataset (see procedural/migration-workflow.md)
- The payment module has strict audit logging requirements

## See Also
- [debugging-notes.md](debugging-notes.md) — Recurring debugging patterns for this project
- [architecture-decisions.md](architecture-decisions.md) — Summary of key architectural choices
```

**Important**: Keep MEMORY.md under 200 lines. Lines after 200 are truncated in auto-loading. Use linked files for depth.

### Updating Long-term Memory

Claude Code should update MEMORY.md when:
1. User explicitly says "remember this" or states a preference
2. A preference is observed consistently (3+ times in a session)
3. A significant project-specific insight is discovered

Protocol (add to CLAUDE.md):
```markdown
## Long-term Memory Protocol
- Read MEMORY.md at session start (auto-loaded)
- When user states a preference: update MEMORY.md immediately
- When user corrects you: update MEMORY.md to fix the incorrect assumption
- Keep MEMORY.md under 200 lines (link to detail files)
- Organize by: User Preferences, Learned Patterns, Project-Specific Knowledge
```

## Step 7: Working Memory and Short-term Memory (Session-Based)

Working memory and short-term memory are handled by Claude Code's conversation context and TodoWrite tool. No file setup needed.

### Working Memory Protocol

```markdown
## Working Memory Protocol
For multi-step problems:
1. Use TodoWrite to decompose the problem into trackable tasks
2. Mark tasks in_progress as you work on them
3. Keep only ONE task in_progress at a time
4. Log hypotheses and evidence in conversation text
5. If session ends with unresolved problem, write findings to `.claude/memory/episodic/`
```

### Short-term Memory Protocol

```markdown
## Short-term Memory Protocol
Claude Code's conversation context handles this automatically.
- Context is preserved throughout the session
- Auto-compression retains the most relevant recent context
- No manual intervention needed for session-level context tracking
```

## Step 8: Create the Master CLAUDE.md

Combine all the pieces. Copy the content from the [CLAUDE.md](CLAUDE.md) file in this directory into your project root.

## Step 9: Validate the Setup

### Validation Checklist

```markdown
- [ ] CLAUDE.md exists at project root with project facts and standards
- [ ] .claude/memory/episodic/ directory exists with at least one entry
- [ ] .claude/memory/semantic/ has domain model documentation
- [ ] .claude/memory/procedural/ has at least one workflow guide
- [ ] ~/.claude/projects/<path>/memory/MEMORY.md exists with preferences
- [ ] Claude Code loads CLAUDE.md on session start (check first message context)
- [ ] Claude Code can read episodic entries when asked about past decisions
- [ ] TodoWrite works for task decomposition
```

### Test Scenarios

1. **Semantic recall**: Ask Claude Code about the project's API standards. It should answer from CLAUDE.md without reading files.
2. **Episodic recall**: Ask "What did we decide about authentication?" Claude Code should search `.claude/memory/episodic/` and find relevant entries.
3. **Procedural execution**: Ask to create a new feature. Claude Code should follow the documented workflow from CLAUDE.md and procedural memory.
4. **Working memory**: Start a multi-step debugging task. Claude Code should use TodoWrite to track progress.
5. **Long-term personalization**: Write code. Claude Code should apply preferences from MEMORY.md (early returns, explicit errors, etc.).

## Working Example: End-to-End

### Scenario: Adding a notification preferences API

**1. Session starts** — CLAUDE.md and MEMORY.md auto-loaded:
- Semantic: API standard (REST, `/api/v1/`, JWT, `{ data, error, meta }`)
- Long-term: Prefers JSONB with typed overlays, Zod validation, co-located tests

**2. Claude Code checks procedural memory**:
- Reads `.claude/memory/procedural/feature-workflow.md`
- Creates branch: `feat/287-notification-preferences`
- Creates draft PR

**3. Working memory activates** (TodoWrite):
```
- [x] Create branch and draft PR
- [>] Design notification preference schema
- [ ] Implement route handler with validation
- [ ] Write tests
- [ ] Update API documentation
```

**4. Claude Code checks episodic memory** before schema design:
- Reads `.claude/memory/episodic/2025-02-10-auth-migration.md` (relevant for auth context)
- Checks for any past notification-related decisions

**5. Implementation follows semantic + long-term memory**:
- JSONB column with TypeScript typed overlay (long-term preference)
- Zod schema for input validation (long-term preference)
- Co-located test file (long-term preference)
- `{ data, error, meta }` response shape (semantic standard)

**6. After completion, episodic memory recorded**:
```markdown
# [ARCH] Notification Preferences Schema Design
- **Date**: 2025-03-05
- **Category**: ARCH
- **Impact**: Medium

## Decision
JSONB column with per-channel (email, push, in-app) per-notification-type granularity.
TypeScript overlay type `NotificationPreferences` for type safety.

## Rationale
Avoids schema migration when adding new notification types.
```

**7. Long-term memory reinforced**:
MEMORY.md already notes JSONB preference — no update needed. Confidence in this pattern increases implicitly.

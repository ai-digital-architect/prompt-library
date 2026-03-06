# Track A: File-Based Memory Implementation for GitHub Copilot

## Overview

This track implements the six-memory architecture using Markdown files in the repository and Copilot's native `/memories/` scopes. Zero external infrastructure required. All memory is version-controlled alongside code.

## Step 1: Create the Directory Structure

Run this in any repository root:

```bash
mkdir -p .github/memory/{episodic,semantic,procedural,working-templates}
mkdir -p .github/instructions
mkdir -p .github/skills
```

Resulting layout:

```
.github/
  memory/
    episodic/              # Event logs, decision records, incident reports
    semantic/              # Domain knowledge, architecture facts, business rules
    procedural/            # Workflow definitions, automation scripts
    working-templates/     # Reusable templates for working memory sessions
  instructions/            # Auto-loaded by Copilot as context
  skills/                  # Copilot skill definitions
```

## Step 2: Create the Semantic Memory Foundation

Semantic memory is the base layer. Create the core instruction file that Copilot loads automatically.

### File: `.github/instructions/project-knowledge.instructions.md`

```markdown
---
applyTo: "**"
---

# Project Knowledge Base

## Project Identity
- **Name**: [PROJECT_NAME]
- **Type**: [web-app | api | library | cli | mobile]
- **Primary Language**: [TypeScript | Python | Go | etc.]
- **Framework**: [React | Next.js | Express | FastAPI | etc.]
- **Database**: [PostgreSQL | MongoDB | etc.]
- **Status**: [active-development | maintenance | pre-release]

## Architecture
- **Style**: [monolith | microservices | serverless | modular-monolith]
- **Hosting**: [AWS | GCP | Azure | Vercel | etc.]
- **CI/CD**: [GitHub Actions | CircleCI | etc.]
- **Key Services**: [list main services/modules]

## Coding Standards
- **Naming**: [camelCase | snake_case] for variables, [PascalCase] for types
- **Max Function Length**: [30] lines
- **Max File Length**: [300] lines
- **Imports**: [grouped by: stdlib, external, internal, relative]
- **Error Handling**: [pattern description]
- **Testing**: [framework, coverage target, test file location convention]

## API Conventions
- **Style**: [REST | GraphQL | gRPC]
- **Auth**: [JWT | OAuth2 | API Key]
- **Versioning**: [URL path | header | query param]
- **Response Shape**: `{ data: T, error?: { code, message }, meta?: { page, total } }`

## Business Rules
<!-- Add domain-specific rules that Copilot must respect -->
- [Rule 1: description]
- [Rule 2: description]

## Key Dependencies
| Package | Purpose | Version Constraint |
|---|---|---|
| [package-name] | [why it's used] | [^major.minor] |
```

### File: `.github/memory/semantic/domain-models.md`

```markdown
# Domain Models

## Core Entities

### User
- **Properties**: id (UUID), email (unique, verified), name, role (admin|member|viewer), createdAt, updatedAt
- **Relationships**: has many Projects, has many Notifications
- **Business Rules**: Email must be verified before any write operations. Soft-delete only.

### Project
- **Properties**: id (UUID), name, ownerId (FK User), status (draft|active|archived), settings (JSONB)
- **Relationships**: belongs to User (owner), has many Members, has many Resources
- **Business Rules**: Archived projects are read-only. Name unique per owner.

<!-- Add more entities as the domain grows -->
```

## File Format Decision

All Track A memory files use **Markdown**. Episodic entries additionally use **YAML frontmatter** for structured metadata that enables scripted queries (date filtering, category filtering, clearing automation). Semantic, procedural, and long-term files are plain Markdown — they are documentation by nature and queried by topic, not filtered by fields.

**Why not JSON?** Episodic, semantic, and procedural entries contain narrative content (context, rationale, code blocks) that becomes unreadable in JSON string fields. JSON excels at structured data, but memory files are primarily prose with embedded structure. YAML frontmatter gives the best of both worlds for episodic entries: parseable metadata + readable narrative body.

An optional auto-generated `_index.json` registry (derived from episodic frontmatter) enables jq-based queries without sacrificing authoring experience. See Step 3 below.

## Step 3: Create the Episodic Memory System

### File: `.github/memory/episodic/TEMPLATE.md`

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
[What prompted this event? What was the state before?]

## Decision / Action
[What was decided or done?]

## Alternatives Considered
- **Option A**: [description] -- rejected because [reason]
- **Option B**: [description] -- rejected because [reason]

## Rationale
[Why this approach was chosen]

## Outcome
[Results observed. Update this section post-facto.]

## Lessons Learned
[What to carry forward. What to avoid next time.]
```

### Example entry: `.github/memory/episodic/2025-01-15-database-migration-strategy.md`

```markdown
---
date: "2025-01-15"
category: ARCH
impact: high
tags: [database, migration, zero-downtime, pgroll]
participants: [tech-lead, backend-team]
related: ["#142"]
retain: false
---

# Database Migration Strategy Decision

## Context
Growing table sizes (users: 2M rows, events: 50M rows) causing migration downtime.
Team debated between zero-downtime migration tooling options.

## Decision / Action
Adopted `pgroll` for schema migrations with expand-contract pattern.
All future migrations must be backward-compatible for at least one deploy cycle.

## Alternatives Considered
- **Manual expand-contract**: Too error-prone at current team size
- **pt-online-schema-change**: MySQL-only, not applicable
- **Feature flags on schema**: Over-engineering for current scale

## Rationale
pgroll automates expand-contract, integrates with GitHub Actions,
and supports rollback without data loss.

## Outcome
First migration (add `preferences` JSONB column) completed with zero downtime.
Migration time reduced from 15min (with lock) to 45sec (online).

## Lessons Learned
- Always test migrations against production-sized dataset before deploy
- Keep a rollback plan even with zero-downtime tooling
```

### Auto-generated Episodic Index: `.github/memory/episodic/_index.json`

This file is auto-generated from YAML frontmatter across all episodic entries. It enables jq-based queries for filtering, counting, and clearing automation. Regenerate it with the script below or via the provided git hook.

**Example `_index.json`**:

```json
[
  {
    "file": "2025-01-15-database-migration-strategy.md",
    "date": "2025-01-15",
    "category": "ARCH",
    "impact": "high",
    "tags": ["database", "migration", "zero-downtime", "pgroll"],
    "title": "Database Migration Strategy Decision",
    "retain": false
  }
]
```

**Index generation script** (`.github/scripts/rebuild-episodic-index.sh`):

```bash
#!/usr/bin/env bash
# Rebuild _index.json from YAML frontmatter in episodic memory files.
# Requires: python3 (with PyYAML) or yq.
set -euo pipefail

EPISODIC_DIR=".github/memory/episodic"
INDEX_FILE="$EPISODIC_DIR/_index.json"

python3 -c "
import json, re, glob, sys
try:
    import yaml
except ImportError:
    print('ERROR: PyYAML required. Install: pip install pyyaml', file=sys.stderr)
    sys.exit(1)

entries = []
for path in sorted(glob.glob('$EPISODIC_DIR/*.md')):
    if 'TEMPLATE' in path:
        continue
    with open(path) as f:
        content = f.read()
    # Extract YAML frontmatter
    match = re.match(r'^---\n(.+?)\n---\n(.+)', content, re.DOTALL)
    if not match:
        continue
    meta = yaml.safe_load(match.group(1))
    body = match.group(2)
    # Extract title from first H1
    title_match = re.search(r'^# (.+)$', body, re.MULTILINE)
    title = title_match.group(1) if title_match else path.split('/')[-1]
    entries.append({
        'file': path.split('/')[-1],
        'date': str(meta.get('date', '')),
        'category': meta.get('category', ''),
        'impact': meta.get('impact', ''),
        'tags': meta.get('tags', []),
        'title': title,
        'retain': meta.get('retain', False),
    })

with open('$INDEX_FILE', 'w') as f:
    json.dump(entries, f, indent=2)
print(f'Rebuilt {len(entries)} entries in $INDEX_FILE')
"
```

**Common jq queries against the index**:

```bash
# All ARCH decisions
jq '[.[] | select(.category == "ARCH")]' .github/memory/episodic/_index.json

# Entries from last 90 days
jq --arg cutoff "$(date -d '-90 days' +%Y-%m-%d 2>/dev/null || date -v-90d +%Y-%m-%d)" \
  '[.[] | select(.date >= $cutoff)]' .github/memory/episodic/_index.json

# High or critical impact entries
jq '[.[] | select(.impact == "high" or .impact == "critical")]' \
  .github/memory/episodic/_index.json

# Count entries per category
jq 'group_by(.category) | map({category: .[0].category, count: length})' \
  .github/memory/episodic/_index.json

# Entries tagged "authentication"
jq '[.[] | select(.tags | index("authentication"))]' \
  .github/memory/episodic/_index.json

# Entries eligible for clearing (older than 180 days, not retained)
jq --arg cutoff "$(date -d '-180 days' +%Y-%m-%d 2>/dev/null || date -v-180d +%Y-%m-%d)" \
  '[.[] | select(.date < $cutoff and .retain != true)]' \
  .github/memory/episodic/_index.json
```

### Copilot Repo Memory Entries for Episodic

When a major event occurs, also create a repo memory entry for quick retrieval:

```
@copilot /memories/repo/ create
[EPISODIC] 2025-01-15: ARCH - Adopted pgroll for zero-downtime migrations. Expand-contract pattern required for all schema changes. See .github/memory/episodic/2025-01-15-database-migration-strategy.md
```

## Step 4: Create the Procedural Memory System

### File: `.github/memory/procedural/workflows.md`

```markdown
# Development Workflows

## New Feature Workflow
1. Create branch: `feat/ISSUE-NUMBER-short-description`
2. Create draft PR immediately, linking the issue
3. Implement with conventional commits: `feat(scope): description`
4. Ensure all tests pass locally: `npm test`
5. Request review after CI is green
6. Squash-merge after approval
7. Delete branch after merge

## Bug Fix Workflow
1. Create branch: `fix/ISSUE-NUMBER-short-description`
2. Write failing test that reproduces the bug FIRST
3. Implement the fix
4. Verify the test passes
5. Check for related edge cases
6. Create PR with `Fixes #ISSUE-NUMBER` in body
7. Squash-merge after approval

## Database Migration Workflow
1. Generate migration: `npx prisma migrate dev --name descriptive-name`
2. Review generated SQL in `prisma/migrations/`
3. Test rollback locally: `npx prisma migrate reset`
4. Update seed data if schema changed: `npx prisma db seed`
5. Test against staging dataset before merge
6. Monitor migration in production deploy logs

## Deployment Workflow
1. Merge to `main` triggers CI pipeline
2. CI runs: lint, test, build, security scan
3. Staging deploy is automatic on CI success
4. Smoke tests run against staging
5. Production deploy requires manual approval in GitHub Actions
6. Post-deploy: check error rates for 15 minutes
```

### Skill File: `.github/skills/create-api-endpoint.skill.md`

```markdown
# Create API Endpoint

## Description
Scaffold a new REST API endpoint with route handler, validation, types, tests, and documentation.

## Trigger
User asks to create a new API endpoint, route, or controller.

## Inputs
- `resource`: The resource name (e.g., "notification", "payment")
- `method`: HTTP method (GET, POST, PUT, PATCH, DELETE)
- `auth`: Whether authentication is required (default: true)

## Steps

### 1. Create the route handler

File: `src/routes/{resource}.ts` (or add to existing)

```typescript
import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { authenticate } from '../middleware/auth';
import { validate } from '../middleware/validate';

const router = Router();

// Validation schema
const create{Resource}Schema = z.object({
  // Add fields based on requirements
});

// POST /api/v1/{resource}
router.post(
  '/',
  authenticate,
  validate(create{Resource}Schema),
  async (req: Request, res: Response) => {
    try {
      // Implementation
      res.status(201).json({ data: result });
    } catch (error) {
      res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: 'Failed to create {resource}' } });
    }
  }
);

export default router;
```

### 2. Create types

File: `src/types/{resource}.ts`

```typescript
export interface {Resource} {
  id: string;
  // Add fields
  createdAt: Date;
  updatedAt: Date;
}

export interface Create{Resource}Input {
  // Add input fields
}
```

### 3. Create tests

File: `src/routes/__tests__/{resource}.test.ts`

```typescript
import request from 'supertest';
import { app } from '../../app';

describe('{Resource} API', () => {
  describe('POST /api/v1/{resource}', () => {
    it('should create a new {resource}', async () => {
      const response = await request(app)
        .post('/api/v1/{resource}')
        .set('Authorization', 'Bearer test-token')
        .send({ /* valid input */ });

      expect(response.status).toBe(201);
      expect(response.body.data).toBeDefined();
    });

    it('should return 401 without auth', async () => {
      const response = await request(app)
        .post('/api/v1/{resource}')
        .send({ /* valid input */ });

      expect(response.status).toBe(401);
    });

    it('should return 400 for invalid input', async () => {
      const response = await request(app)
        .post('/api/v1/{resource}')
        .set('Authorization', 'Bearer test-token')
        .send({ /* invalid input */ });

      expect(response.status).toBe(400);
    });
  });
});
```

### 4. Register route

Add to `src/routes/index.ts`:
```typescript
import {resource}Router from './{resource}';
router.use('/api/v1/{resource}', {resource}Router);
```

## Validation
- Route responds to correct HTTP method and path
- Authentication middleware is applied (if auth: true)
- Input validation returns 400 for invalid payloads
- All tests pass
```

### Copilot User Memory for Procedural

```
@copilot /memories/ create
[PROCEDURAL] My standard feature workflow: branch from main, draft PR immediately, conventional commits, squash-merge. Always write failing test first for bug fixes.
```

## Step 5: Configure Working Memory (Session-Scoped)

Working memory is session-only. No files to persist. Instead, instruct Copilot to use session memory.

### Working Memory Protocol (add to instructions file)

Add this section to `.github/instructions/project-knowledge.instructions.md`:

```markdown
## Working Memory Protocol

When solving a multi-step problem in this session:

1. **Capture the problem**: Create a session memory with the problem definition
   ```
   /memories/session/ create [WORKING] Problem: <description>
   ```

2. **Track hypotheses**: Log each hypothesis as a session memory
   ```
   /memories/session/ create [WORKING] Hypothesis: <description> - Status: investigating|eliminated|confirmed
   ```

3. **Record evidence**: Note findings that support or contradict hypotheses
   ```
   /memories/session/ create [WORKING] Evidence: <finding> - Supports/Contradicts: <hypothesis>
   ```

4. **Update on resolution**: Mark the problem as resolved with solution summary
   ```
   /memories/session/ create [WORKING] Resolved: <problem> - Solution: <summary>
   ```

5. **Promote if significant**: If the resolution reveals a pattern, promote to episodic or semantic memory
```

## Step 6: Configure Short-term Memory (Session-Scoped)

Short-term memory tracks session state. Also session-scoped, no file persistence needed.

### Short-term Memory Protocol (add to instructions file)

```markdown
## Short-term Memory Protocol

During this session, maintain awareness of:

1. **Active task context**:
   ```
   /memories/session/ create [SESSION] Task: <current task description>
   ```

2. **Recent file changes**: After modifying files, note what changed
   ```
   /memories/session/ create [SESSION] Modified: <file> - Change: <what changed and why>
   ```

3. **Decisions made this session**: Track in-session decisions
   ```
   /memories/session/ create [SESSION] Decision: <what> - Reason: <why>
   ```

4. **Context stack**: When switching contexts, save current state
   ```
   /memories/session/ create [SESSION] Context saved: <task being paused> - Resume point: <where to pick up>
   ```

5. **Auto-prune**: When session memory exceeds ~15 entries, archive completed items:
   - Mark completed tasks
   - Compress reasoning chains into summaries
   - Promote important findings to permanent memory
```

## Step 7: Configure Long-term Memory (User-Scoped)

### Seeding Long-term Memory

At the start of using this system, seed your user-scoped memories with personal preferences:

```
@copilot /memories/ create [PREFERENCE] Coding: Early returns over nested conditionals. Descriptive variable names over comments. Small functions over large ones.

@copilot /memories/ create [PREFERENCE] Architecture: Composition over inheritance. Explicit over implicit. Simple solutions first, optimize when measured.

@copilot /memories/ create [PREFERENCE] TypeScript: Strict mode always. Prefer 'type' for unions, 'interface' for object shapes. Avoid 'any', use 'unknown' + type guards.

@copilot /memories/ create [PREFERENCE] Git: Conventional commits. Squash-merge PRs. Feature branches from main. Delete merged branches.

@copilot /memories/ create [PREFERENCE] Testing: Integration tests for API boundaries. Unit tests for complex business logic. Minimal mocking.
```

### Long-term Learning Protocol

```markdown
## Long-term Learning Protocol

Observe and learn from user patterns:

1. **Pattern detection**: When the same preference appears 3+ times, create a user memory
   ```
   /memories/ create [LEARNED] User consistently prefers <pattern> over <alternative>
   ```

2. **Preference updates**: When user explicitly states a preference
   ```
   /memories/ str_replace [old preference text] → [updated preference text]
   ```

3. **Confidence levels**: Track confidence in learned preferences
   - 95%+ (5+ observations): Apply automatically
   - 80-94% (3-4 observations): Apply with brief mention
   - 60-79% (1-2 observations): Suggest as option
   - <60%: Ask for guidance

4. **Cross-repo application**: User memories apply across all repositories
```

## Step 8: Create the Master Instructions File

Copy `copilot-memory.instructions.md` to `.github/instructions/` in your repository. This file ties all memory systems together and instructs Copilot on when and how to use each type.

## Step 9: Validate the Setup

### Validation Checklist

```markdown
- [ ] `.github/instructions/project-knowledge.instructions.md` exists and loads in Copilot
- [ ] `.github/memory/episodic/` has at least one entry
- [ ] `.github/memory/semantic/domain-models.md` is populated
- [ ] `.github/memory/procedural/workflows.md` is populated
- [ ] `/memories/repo/` has semantic entries visible via `@copilot /memories/repo/ view`
- [ ] `/memories/` (user) has at least preference entries
- [ ] Session memories work: create a `[WORKING]` entry and retrieve it
- [ ] Cross-memory works: reference an episodic entry in a session context
```

### Test Scenarios

1. **Semantic recall**: Ask Copilot about project architecture. It should reference `.github/instructions/` content.
2. **Episodic recall**: Ask about a past decision. Copilot should reference episodic entries.
3. **Procedural execution**: Ask to create a new feature. Copilot should follow documented workflow.
4. **Working memory**: Start debugging. Copilot should create session memories for hypotheses.
5. **Long-term personalization**: Write code. Copilot should apply your stated preferences.

## Working Example: End-to-End

### Scenario: Adding a notification preferences API

**1. Short-term memory activates** (session):
```
[SESSION] Task: Add notification preferences API endpoint
[SESSION] Related issue: #287
```

**2. Semantic memory consulted** (instructions + repo memory):
- API convention: REST, `/api/v1/`, JWT auth, `{ data, error, meta }` response
- Business rule: Users must be verified to change preferences
- Database: PostgreSQL with Prisma, JSONB for flexible schemas

**3. Procedural memory triggers** (user memory + skill):
- Feature workflow: branch `feat/287-notification-preferences`
- API endpoint skill: scaffold route, types, tests, register route

**4. Working memory tracks progress** (session):
```
[WORKING] Problem: Design notification preference schema
[WORKING] Approach: JSONB column with typed overlay for type safety
[WORKING] Decision: Channel-based preferences (email, push, in-app) per notification type
```

**5. Episodic memory recorded** (repo memory + file):
```
[EPISODIC] 2025-03-05: ARCH - Notification preferences use JSONB with typed overlay.
Allows per-channel, per-type granularity without schema migration for new notification types.
```

**6. Long-term memory updated** (user memory):
```
[LEARNED] This user prefers JSONB with TypeScript type overlays for flexible schemas
```

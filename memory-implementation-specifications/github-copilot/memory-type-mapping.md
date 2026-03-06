# Memory Type Mapping: GitHub Copilot

## Detailed Mapping Table

| Memory Type | Native Scope | File Path Convention (Track A) | Lifecycle | Read Trigger | Write Trigger |
|---|---|---|---|---|---|
| **Episodic** | `/memories/repo/` | `.github/memory/episodic/YYYY-MM-DD-slug.md` | Permanent per-repo | Decision context needed, similar problem encountered | Major decision made, incident resolved, milestone reached |
| **Semantic** | `/memories/repo/` + `.github/instructions/` | `.github/memory/semantic/*.md` + `.github/instructions/standards.instructions.md` | Permanent, version-controlled | Code generation, architecture decisions, API design | Standards change, new domain rules, tech stack updates |
| **Procedural** | `/memories/` (user) | `.github/memory/procedural/*.md` + `.github/skills/*.skill.md` | Permanent per-user | Repeated workflow detected, task initiation | New workflow established, procedure refined |
| **Working** | `/memories/session/` | Not persisted to files (session only) | Current session | Active problem-solving, multi-step reasoning | Problem decomposition, hypothesis formation |
| **Short-term** | `/memories/session/` | Not persisted to files (session only) | Current session | Context needed for current task, mode switching | File changes, decisions made, errors encountered |
| **Long-term** | `/memories/` (user) | `.github/memory/long-term/preferences.md` | Permanent per-user | Code style decisions, architecture choices | Preference confirmed 3+ times, explicit user statement |

## Scope Selection Logic

```
Is this memory specific to one project?
  YES → Is it a factual standard or rule?
    YES → /memories/repo/ + .github/instructions/ (SEMANTIC)
    NO  → Is it an event or decision record?
      YES → /memories/repo/ + .github/memory/episodic/ (EPISODIC)
      NO  → /memories/repo/ (general project context)
  NO  → Is it a personal preference or habit?
    YES → /memories/ user scope (LONG-TERM)
    NO  → Is it a repeatable workflow?
      YES → /memories/ user scope + .github/skills/ (PROCEDURAL)
      NO  → Does it need to survive this session?
        YES → Promote to appropriate permanent scope
        NO  → /memories/session/ (WORKING or SHORT-TERM)
```

## Memory Type Details

### Episodic Memory → `/memories/repo/` + File-based Archive

**What it stores**: Decisions, incidents, milestones, architectural pivots, retrospective insights.

**Native mapping**: Copilot repo memories capture key project events. File-based archive (Track A) provides searchable history.

**Entry format for `/memories/repo/`**:
```
[EPISODIC] YYYY-MM-DD: <event-type> - <summary>
Context: <why this matters>
Decision: <what was decided>
Outcome: <result, if known>
```

**File archive format** (`.github/memory/episodic/YYYY-MM-DD-slug.md`):
```markdown
# [EVENT-TYPE] Event Title

- **Date**: YYYY-MM-DD
- **Participants**: Names/roles
- **Category**: ARCH | TECH | INC | MEET | DEBUG
- **Impact**: High | Medium | Low

## Context
What prompted this event.

## Decision / Action
What was decided or done.

## Rationale
Why this approach was chosen over alternatives.

## Outcome
Results observed (update post-facto).

## Lessons
What to remember for next time.
```

### Semantic Memory → `/memories/repo/` + `.github/instructions/`

**What it stores**: Project facts, coding standards, architecture rules, business domain knowledge, API contracts.

**Native mapping**: `.github/instructions/*.instructions.md` files are automatically loaded by Copilot as context. Repo memories supplement with dynamic facts.

**Instruction file** (`.github/instructions/standards.instructions.md`):
```markdown
# Project Standards (auto-loaded by Copilot)

## Architecture
- Style: Microservices with API Gateway
- Languages: TypeScript (backend), React (frontend)
- Database: PostgreSQL with Prisma ORM

## Coding Standards
- Naming: camelCase for variables/functions, PascalCase for types/classes
- Max function length: 30 lines
- Max file length: 300 lines
- Error handling: Always use typed errors, never throw raw strings

## API Standards
- REST with versioned URLs: /api/v{n}/resource
- Authentication: Bearer JWT
- Response format: { data, error, meta }
- Pagination: cursor-based

## Business Rules
- All monetary values in cents (integer)
- User emails must be verified before account activation
- Orders cannot be modified after payment processing begins
```

**Repo memory entries** for dynamic semantic facts:
```
[SEMANTIC] Tech stack: Node 20 LTS, React 18, PostgreSQL 16, Redis 7
[SEMANTIC] Deploy target: AWS ECS Fargate, us-east-1
[SEMANTIC] API rate limit: 100 req/min per user, 1000 req/min per org
```

### Procedural Memory → `/memories/` (user) + `.github/skills/`

**What it stores**: Repeatable workflows, automation patterns, development procedures.

**Native mapping**: User-scoped memories persist workflows across repos. Skill files define executable procedures.

**User memory entries**:
```
[PROCEDURAL] React component creation: functional component with TypeScript, co-locate test file, use barrel exports
[PROCEDURAL] PR workflow: draft PR on branch creation, link issue, add labels, request review after CI passes
[PROCEDURAL] Database migration: create migration file, test rollback, update seed data, verify in staging
```

**Skill file** (`.github/skills/create-component.skill.md`):
```markdown
# Create Component

## Trigger
User asks to create a new React component.

## Steps
1. Create `src/components/{Name}/{Name}.tsx` with functional component template
2. Create `src/components/{Name}/{Name}.test.tsx` with testing-library setup
3. Create `src/components/{Name}/{Name}.module.css` if styles needed
4. Create `src/components/{Name}/index.ts` barrel export
5. Add export to parent `index.ts` if exists

## Template
(component template code block)
```

### Working Memory → `/memories/session/`

**What it stores**: Current problem state, hypotheses, investigation progress, active reasoning.

**Native mapping**: Session-scoped memories hold the active mental model. Cleared when session ends.

**Session memory entries**:
```
[WORKING] Current problem: Payment webhook failing for Stripe events > 30 seconds
[WORKING] Hypothesis 1: Timeout in API gateway (investigating)
[WORKING] Hypothesis 2: Race condition in idempotency check (eliminated - logs show sequential)
[WORKING] Evidence: CloudWatch shows 504 at exactly 30s mark, matches ALB default timeout
[WORKING] Next step: Check ALB idle timeout configuration
```

### Short-term Memory → `/memories/session/`

**What it stores**: Session context, recent file changes, active task state, mode transitions.

**Native mapping**: Session-scoped memories track current session state. Auto-pruned by session end.

**Session memory entries**:
```
[SESSION] Active task: Implementing user notification preferences API
[SESSION] Files modified: src/routes/notifications.ts, src/models/preferences.ts
[SESSION] Recent decision: Using PostgreSQL JSONB for flexible preference schema
[SESSION] Blocked: Waiting for design review on notification grouping UX
[SESSION] Context: This relates to Q1 user engagement initiative (see MEET-2025-01-15-01)
```

### Long-term Memory → `/memories/` (user)

**What it stores**: Personal coding preferences, architectural inclinations, tool preferences, learned patterns.

**Native mapping**: User-scoped memories persist across all repos and sessions.

**User memory entries**:
```
[PREFERENCE] Code style: Prefer early returns over nested conditionals
[PREFERENCE] Architecture: Favor composition over inheritance
[PREFERENCE] Testing: Write integration tests first, unit tests for complex logic only
[PREFERENCE] TypeScript: Strict mode always, prefer type over interface for unions
[PREFERENCE] Git: Conventional commits, squash-merge PRs, delete branches after merge
[LEARNED] This user prefers explicit error handling over try-catch blocks
[LEARNED] This user values readability over cleverness in code
```

## Cross-Memory Coordination

| Source Memory | Feeds Into | Example |
|---|---|---|
| Short-term | Working | "Current file context informs active problem" |
| Working | Episodic | "Resolved bug becomes a recorded event" |
| Episodic | Semantic | "Repeated pattern becomes a documented rule" |
| Semantic | Procedural | "Standard becomes an automated workflow step" |
| Procedural | Long-term | "Workflow preference becomes personal habit" |
| Long-term | All | "Personal preferences shape all memory operations" |

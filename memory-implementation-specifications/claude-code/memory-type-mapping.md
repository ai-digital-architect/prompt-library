# Memory Type Mapping: Claude Code

## Detailed Mapping Table

| Memory Type | Claude Code Mechanism | Storage Location | Lifecycle | Read Trigger | Write Trigger |
|---|---|---|---|---|---|
| **Episodic** | Read/Write tools | `.claude/memory/episodic/YYYY-MM-DD-slug.md` | Permanent, git-tracked | Decision context needed, similar problem referenced | Major decision, incident resolved, milestone reached |
| **Semantic** | CLAUDE.md (auto-loaded) + Read tool | `CLAUDE.md` (core rules) + `.claude/memory/semantic/*.md` (detailed) | Permanent, auto-loaded | Every conversation (CLAUDE.md). Detailed files read on demand. | Standards change, new rules, tech stack updates |
| **Procedural** | CLAUDE.md instructions + Bash tool | `CLAUDE.md` (workflow rules) + `.claude/memory/procedural/*.md` | Permanent, git-tracked | Task initiation, repeated workflow detected | New workflow established, procedure refined |
| **Working** | Conversation context + TodoWrite | In-session only | Current session (auto-compressed) | Continuous during problem-solving | Problem decomposition, hypothesis, evidence |
| **Short-term** | Conversation context | In-session only | Current session (auto-compressed) | Continuous | File changes, decisions, context switches |
| **Long-term** | Auto-memory (`MEMORY.md`) + CLAUDE.md | `~/.claude/projects/*/memory/MEMORY.md` + `CLAUDE.md` | Permanent per-user-per-project | Every conversation (MEMORY.md auto-loaded) | Preference confirmed, explicit user request |

## Mechanism Selection Logic

```
Is this memory loaded automatically every session?
  YES → Does it need to be concise (< 200 lines)?
    YES → CLAUDE.md or MEMORY.md (SEMANTIC core rules, LONG-TERM preferences)
    NO  → CLAUDE.md with links to detail files (read on demand)
  NO  → Does it need to persist across sessions?
    YES → Is it project-specific?
      YES → .claude/memory/ files (EPISODIC, SEMANTIC detail, PROCEDURAL)
      NO  → ~/.claude/projects/*/memory/ (LONG-TERM cross-session)
    NO  → Conversation context (WORKING, SHORT-TERM)
```

## Memory Type Details

### Episodic Memory → `.claude/memory/episodic/`

**What it stores**: Past decisions, incidents, milestones, architectural pivots.

**Claude Code mechanism**: Files in `.claude/memory/episodic/` read via the Read tool when historical context is needed. CLAUDE.md includes instructions to check episodic memory before architectural decisions.

**File format** (`.claude/memory/episodic/YYYY-MM-DD-slug.md`):
```markdown
# [CATEGORY] Event Title

- **Date**: YYYY-MM-DD
- **Category**: ARCH | TECH | INC | MEET | DEBUG | MILE
- **Impact**: Critical | High | Medium | Low

## Context
What prompted this event.

## Decision
What was decided or done.

## Rationale
Why this approach, what alternatives were rejected.

## Outcome
Results observed (update post-facto).

## Lessons
What to carry forward.
```

**Agent protocol**: Before major architectural decisions, Claude Code should:
1. Use Glob to list `.claude/memory/episodic/*.md`
2. Read relevant entries based on filename/date
3. Reference past decisions in its reasoning

### Semantic Memory → `CLAUDE.md` + `.claude/memory/semantic/`

**What it stores**: Project facts, coding standards, architecture rules, business domain knowledge.

**Claude Code mechanism**: Core rules go in `CLAUDE.md` (auto-loaded every session, ~200 lines max for effective use). Detailed domain knowledge goes in `.claude/memory/semantic/` files, read on demand.

**CLAUDE.md section** (auto-loaded):
```markdown
## Project Facts
- Language: TypeScript, React 18, Node 20
- Database: PostgreSQL 16 with Prisma ORM
- Hosting: AWS ECS Fargate, us-east-1
- CI: GitHub Actions

## Coding Standards
- Naming: camelCase variables, PascalCase types
- Max function: 30 lines, max file: 300 lines
- Errors: Typed errors, never throw raw strings
- Testing: Vitest, co-located test files

## API Standards
- REST, /api/v1/resource, Bearer JWT
- Response: { data, error, meta }
- Pagination: cursor-based
```

**Detail file** (`.claude/memory/semantic/domain-models.md`):
```markdown
# Domain Models

## User
- Properties: id (UUID), email (unique, verified), name, role (admin|member|viewer)
- Rules: Email verified before write ops. Soft-delete only.
- Relationships: has many Projects, has many Notifications

## Project
- Properties: id (UUID), name, ownerId, status (draft|active|archived)
- Rules: Archived = read-only. Name unique per owner.
```

**Agent protocol**: CLAUDE.md rules are always active. For detailed domain questions, Claude Code reads the relevant semantic file.

### Procedural Memory → `CLAUDE.md` + `.claude/memory/procedural/`

**What it stores**: Repeatable workflows, development procedures, automation patterns.

**Claude Code mechanism**: Workflow rules in CLAUDE.md instruct Claude Code on standard procedures. Detailed step-by-step guides in `.claude/memory/procedural/`.

**CLAUDE.md section**:
```markdown
## Workflows
- Feature branch: feat/ISSUE-slug, draft PR, conventional commits, squash-merge
- Bug fix: Write failing test first, then fix, then verify
- Migration: Generate, review SQL, test rollback, update seeds, staging test
```

**Detail file** (`.claude/memory/procedural/feature-workflow.md`):
```markdown
# Feature Development Workflow

## Steps
1. Create branch: `git checkout -b feat/ISSUE-NUMBER-slug`
2. Create draft PR: `gh pr create --draft --title "feat: description" --body "Fixes #ISSUE"`
3. Implement with conventional commits
4. Run tests: `npm test`
5. Request review after CI passes
6. Squash-merge after approval
7. Delete branch: `git branch -d feat/ISSUE-NUMBER-slug`

## Validation
- All tests pass
- No lint warnings
- PR description links the issue
- At least one approval
```

**Agent protocol**: When starting a task, Claude Code checks CLAUDE.md workflow rules and reads the relevant procedural file for detailed steps.

### Working Memory → Conversation Context + TodoWrite

**What it stores**: Current problem state, hypotheses, investigation progress, task decomposition.

**Claude Code mechanism**: The conversation itself is working memory. TodoWrite provides structured task tracking. Claude Code's context window maintains full conversation history, automatically compressing older messages when approaching limits.

**TodoWrite for problem tracking**:
```
Todo list:
- [x] Reproduce the payment webhook timeout
- [>] Check ALB idle timeout configuration
- [ ] Verify Stripe webhook retry logic
- [ ] Test fix in staging
```

**In-conversation tracking**:
Claude Code naturally maintains hypotheses, evidence, and reasoning chains in the conversation. No external file needed. If a problem spans sessions, promote findings to episodic memory.

**Agent protocol**: Use TodoWrite for multi-step tasks. Keep reasoning in conversation. Before ending a session with unresolved problems, write findings to `.claude/memory/episodic/` for the next session.

### Short-term Memory → Conversation Context

**What it stores**: Session state — active task, recent changes, decisions, mode transitions.

**Claude Code mechanism**: The conversation context inherently tracks all of this. Claude Code's auto-compression preserves the most relevant recent context when the window fills.

**No external mechanism needed**: Unlike Copilot, Claude Code's conversation is persistent within a session and context-managed automatically.

**Agent protocol**: If the conversation is getting long, Claude Code can write a session summary to `.claude/memory/episodic/` tagged as a session checkpoint.

### Long-term Memory → `MEMORY.md` + `CLAUDE.md`

**What it stores**: Personal coding preferences, architectural inclinations, learned patterns.

**Claude Code mechanism**: The auto-memory system at `~/.claude/projects/<path>/memory/MEMORY.md` is loaded every session (first 200 lines). Additional files can be created in that directory and linked from MEMORY.md.

**MEMORY.md** (auto-loaded):
```markdown
# Project Memory

## User Preferences
- Prefers early returns over nested conditionals
- Favors composition over inheritance
- TypeScript strict mode always
- Integration tests first, unit tests for complex logic

## Learned Patterns
- User prefers JSONB with typed overlays for flexible schemas
- User values readability over cleverness
- User wants explicit error handling, not broad try-catch

## See Also
- [debugging-patterns.md](debugging-patterns.md) - Common debugging approaches
- [architecture-decisions.md](architecture-decisions.md) - Key past decisions
```

**Agent protocol**: Claude Code reads MEMORY.md automatically. When a preference is confirmed or explicitly stated, update MEMORY.md. Create additional files for detailed topics and link them.

## Cross-Memory Coordination

| Source Memory | Feeds Into | Claude Code Mechanism |
|---|---|---|
| Short-term (conversation) | Working (TodoWrite) | Natural conversation flow |
| Working (conversation) | Episodic (files) | Write findings to `.claude/memory/episodic/` on resolution |
| Episodic (files) | Semantic (CLAUDE.md) | Repeated pattern → add rule to CLAUDE.md |
| Semantic (CLAUDE.md) | Procedural (files) | Standard → documented workflow |
| Procedural (files) | Long-term (MEMORY.md) | Workflow preference → personal memory |
| Long-term (MEMORY.md) | All | Preferences loaded every session, shape all operations |

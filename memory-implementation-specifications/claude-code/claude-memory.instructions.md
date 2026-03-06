# Claude Code Memory Instructions

Reusable agent instructions block for memory read/write protocols. Include this content in your `CLAUDE.md` or reference it as supplementary documentation for Claude Code sessions.

---

## Memory System Overview

You operate with six memory types, each serving a distinct cognitive function:

| Type | Purpose | Storage | Persistence |
|---|---|---|---|
| **Episodic** | What happened (events, decisions) | `.claude/memory/episodic/*.md` | Permanent, git-tracked |
| **Semantic** | What we know (facts, rules, standards) | `CLAUDE.md` + `.claude/memory/semantic/*.md` | Permanent, auto-loaded (CLAUDE.md) |
| **Procedural** | How we do things (workflows) | `CLAUDE.md` + `.claude/memory/procedural/*.md` | Permanent, git-tracked |
| **Working** | What we're solving now | Conversation + TodoWrite | Session only |
| **Short-term** | What's happening this session | Conversation context | Session only |
| **Long-term** | Who the user is (preferences) | `MEMORY.md` (auto-loaded) | Permanent per-user |

## Read Protocols

### Automatic (Every Session)
These are loaded without any action:
- `CLAUDE.md` — Project facts, standards, workflow rules (semantic + procedural core)
- `MEMORY.md` at `~/.claude/projects/<path>/memory/MEMORY.md` — User preferences (long-term)

### On-Demand (Read When Needed)

**Episodic memory** — Read before architectural decisions or when past context is relevant:
```
1. Glob(".claude/memory/episodic/*.md") to list available entries
2. Read entries matching the current topic by filename/date
3. Incorporate past decisions and lessons into reasoning
```

**Semantic detail** — Read when domain-specific questions arise that go beyond CLAUDE.md:
```
1. Glob(".claude/memory/semantic/*.md") to list knowledge files
2. Read the relevant domain file (e.g., domain-models.md, infrastructure.md)
```

**Procedural detail** — Read when executing a standard workflow:
```
1. Check CLAUDE.md's Development Workflows section first
2. If more detail needed: Read(".claude/memory/procedural/<workflow>.md")
3. Follow the documented steps
```

## Write Protocols

### Episodic Write
**Trigger**: Significant decision made, incident resolved, milestone reached, retrospective insight.

**File**: `.claude/memory/episodic/YYYY-MM-DD-slug.md`

**Template**:
```markdown
# [CATEGORY] Title

- **Date**: YYYY-MM-DD
- **Category**: ARCH | TECH | INC | MEET | DEBUG | MILE
- **Impact**: Critical | High | Medium | Low

## Context
[What prompted this]

## Decision
[What was decided]

## Rationale
[Why, and what alternatives were rejected]

## Outcome
[Results — update post-facto]

## Lessons
[What to remember]
```

### Semantic Write
**Trigger**: New project rule discovered, standard changed, tech stack updated.

**Target**: `CLAUDE.md` for concise rules (keep total under 200 lines). `.claude/memory/semantic/*.md` for detailed domain knowledge.

**Protocol**:
1. Read the current target file
2. Check for contradictions with existing content
3. Add or update the relevant section
4. If updating CLAUDE.md, ensure it stays under 200 actionable lines

### Procedural Write
**Trigger**: New workflow established, existing workflow refined.

**Target**: `CLAUDE.md` Development Workflows section for one-liner summaries. `.claude/memory/procedural/*.md` for detailed step-by-step guides.

### Long-term Write
**Trigger**: User explicitly states a preference, user corrects an assumption, preference observed 3+ times.

**Target**: `MEMORY.md` at `~/.claude/projects/<path>/memory/MEMORY.md`

**Protocol**:
1. Read current MEMORY.md
2. Check if preference already exists — update if so, add if new
3. Keep MEMORY.md under 200 lines (link to detail files for depth)
4. Organize into sections: User Preferences, Learned Patterns, Project-Specific Knowledge

### Working Memory Write
**Trigger**: Multi-step problem-solving in progress.

**Mechanism**: Use TodoWrite for task decomposition. Keep hypotheses and evidence in conversation text.

**Protocol**:
```
1. TodoWrite to create task list with pending items
2. Mark each task in_progress as you work on it (one at a time)
3. Mark completed when done
4. If session ends with unresolved problem, promote findings to episodic memory
```

## Promotion Rules

Memory entries should be promoted when they gain permanence:

| From | To | Trigger | Action |
|---|---|---|---|
| Working | Episodic | Problem resolved with reusable insight | Write `.claude/memory/episodic/` entry |
| Episodic | Semantic | Same pattern observed 3+ times | Add rule to CLAUDE.md or semantic file |
| Semantic | Procedural | Rule defines a repeatable workflow | Create `.claude/memory/procedural/` guide |
| Any | Long-term | User preference confirmed | Update MEMORY.md |

## Correction Protocol

When the user corrects you on something:
1. **Immediately** check if the incorrect belief came from a memory file
2. If from MEMORY.md: Update or remove the incorrect entry right now
3. If from CLAUDE.md: Update the relevant section
4. If from a semantic file: Correct the file
5. Acknowledge the correction and confirm the memory was updated

## Cross-Memory Coordination

**Before code generation**:
- Apply: CLAUDE.md standards (semantic) + MEMORY.md preferences (long-term)
- Check: Procedural guides for established patterns

**Before architecture decisions**:
- Read: Episodic entries for past decisions
- Apply: CLAUDE.md constraints (semantic)
- Use: Working memory (TodoWrite) for decision analysis

**During debugging**:
- Track: Working memory (TodoWrite + conversation)
- Reference: Episodic entries for similar past incidents
- After resolution: Promote findings if significant

**After task completion**:
- Update: Short-term context (automatic via conversation)
- Create: Episodic entry if decision was significant
- Reinforce: Long-term preferences if confirmed

## Vector Store Integration (Track B Only)

> Track B (vector store) agent instructions and MCP tool protocols have been moved to
> [mem-impl-vector/claude-code/trade-offs.md](../../mem-impl-vector/claude-code/trade-offs.md).

## Memory Health Indicators

| Indicator | Healthy | Needs Attention |
|---|---|---|
| CLAUDE.md length | < 200 lines | > 200 lines (trim or link out) |
| MEMORY.md length | < 200 lines | > 200 lines (trim or link out) |
| Episodic entries | 1+ per major decision | None after months of development |
| Semantic files | Populated domain models | Empty or placeholder content |
| Procedural guides | Cover common workflows | None defined |
| Contradictions | Zero | Rules conflict between files |

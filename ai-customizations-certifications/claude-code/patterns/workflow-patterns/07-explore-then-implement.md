# Pattern 07: Explore-then-Implement

## Category
Research & Discovery Workflows

## Overview

Separates information gathering from code modification to reduce risk and improve focus. A read-only researcher sub-agent maps the codebase, identifies relevant files, existing patterns, and potential conflicts. It passes a structured research summary to a write-capable implementer sub-agent. The two-phase approach ensures the implementer works from a complete understanding rather than discovering context mid-edit.

## Architecture Diagram

```
User invokes /explore-implement
        │
        ▼
┌────────────────────────┐
│  Researcher Sub-agent   │
│  (READ-ONLY)            │
│  - Maps codebase        │
│  - Identifies patterns  │
│  - Finds dependencies   │
│  - Writes research.md   │
│                         │
│  Tools: Read, Bash      │
│  disallowed: Write,Edit │
└──────────┬──────────────┘
           │ research summary
           ▼
┌────────────────────────┐
│  Implementer Sub-agent  │
│  (WRITE-CAPABLE)        │
│  - Reads research.md    │
│  - Implements changes   │
│  - Writes tests         │
│  - Runs build/test      │
│                         │
│  Tools: Read,Write,Edit │
│         Bash            │
└────────────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/explore-implement/SKILL.md`

```yaml
---
name: explore-implement
description: >
  Two-phase workflow: first researches the codebase read-only, then implements
  changes based on findings. Use for any new feature, refactor, or bug fix
  where understanding the existing code is important before making changes.
argument-hint: "[feature or task description]"
allowed-tools: Read, Write, Edit, Bash
---

Research, then implement: $ARGUMENTS

## Phase 1: Research
Invoke the `researcher` sub-agent with the task description.
The researcher will produce `.claude/research-output/research.md` with:
- Relevant files and their purposes
- Existing patterns and conventions to follow
- Dependencies that will be affected
- Potential conflicts or risks
- Recommended implementation approach

## Phase 2: Implement
Read `.claude/research-output/research.md`, then invoke the `implementer`
sub-agent with:
- The original task description
- The full research summary
- Specific files to modify and patterns to follow

## Phase 3: Verify
Run `pnpm build && pnpm test` and fix any issues.
Present a summary of what was implemented and how it follows existing patterns.
```

### Sub-agent — `.claude/agents/researcher.md`

```yaml
---
name: researcher
description: >
  Researches the existing codebase to gather context, identify patterns, locate
  relevant files, and map dependencies. Use before implementing new features
  or making significant changes.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

You are a codebase researcher. Your job is to thoroughly understand
the existing code before any changes are made.

Research the codebase for the given task. Use read-only tools exclusively.

Produce a structured report covering:

1. **Relevant Files**: List each file that is relevant, with a one-line purpose summary
2. **Existing Patterns**: How does the codebase currently handle similar concerns?
   - Naming conventions observed
   - File organization patterns
   - Error handling approach
   - Testing patterns
3. **Dependencies**: What modules/services will be affected by this change?
4. **Risks & Conflicts**: Are there potential breaking changes? Race conditions? API contracts?
5. **Recommended Approach**: Step-by-step implementation plan that follows existing conventions

Write the report to `.claude/research-output/research.md`.
```

### Sub-agent — `.claude/agents/implementer.md`

```yaml
---
name: implementer
description: >
  Implements code changes based on a provided research summary and plan.
  Use when context has been gathered and a plan is ready.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Bash
maxTurns: 30
---

You are a code implementer. You receive a research summary and implement
the requested changes faithfully.

Rules:
1. Read `.claude/research-output/research.md` first
2. Follow ALL conventions identified in the research
3. Follow the recommended approach from the research unless you have a strong reason not to
4. Write tests alongside implementation code (co-located)
5. Run `pnpm build && pnpm test` after implementation
6. Fix any failures before completing

Return: list of files created/modified, test results, and deviations from the plan (if any).
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(pnpm lint:*)",
      "Bash(find * -name *.ts)",
      "Bash(grep -rn * src/)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(cat *)",
      "Bash(wc -l *)",
      "Bash(mkdir -p .claude/research-output)"
    ],
    "deny": [
      "Bash(rm -rf /:*)"
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
│   │   ├── researcher.md
│   │   └── implementer.md
│   ├── skills/
│   │   └── explore-implement/
│   │       └── SKILL.md
│   └── research-output/          ← Research artifacts (gitignored)
│       └── .gitkeep
└── src/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Researcher accidentally modifies code | `disallowedTools: [Write, Edit, MultiEdit]` enforced at sub-agent level |
| Implementer ignores research findings | Skill explicitly passes research file as input; implementer instructions require reading it |
| Stale research from previous session | Skill cleans research-output directory before invoking researcher |
| Researcher context too large for implementer | Researcher caps report at structured summary; doesn't dump full file contents |

# Pattern 32: Conditional Branching

## Category
Orchestration Meta-Workflows

## Overview

A coordinator sub-agent inspects the project type, language, or current state of the repository and selects which specialist sub-agent to invoke next. The branching logic lives in the coordinator's instructions and in a skill that evaluates conditions before dispatching.

## Architecture Diagram

```
User invokes /auto-fix
        │
        ▼
┌──────────────────────┐
│  Coordinator Skill    │
│  - Inspects project   │
│  - Evaluates condition│
│  - Dispatches to      │
│    correct specialist │
└──┬──────┬──────┬─────┘
   │      │      │
   ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐
│TS Fix││Py Fix││Go Fix│    Specialist sub-agents
│Agent ││Agent ││Agent │    (one per language/framework)
└──────┘└──────┘└──────┘
```

## Complete File Implementations

### Skill — `.claude/skills/auto-fix/SKILL.md`

```yaml
---
name: auto-fix
description: >
  Automatically detects the project type and dispatches to the correct
  specialist sub-agent. Handles TypeScript, Python, and Go projects.
  Use when the user needs a fix and the project type determines the approach.
argument-hint: "[issue description]"
allowed-tools: Read, Write, Edit, Bash
---

Auto-fix with project detection: $ARGUMENTS

## Step 1: Detect Project Type

Inspect the repository to determine the primary language/framework:
- If `package.json` + `tsconfig.json` exist → TypeScript project
- If `requirements.txt` or `pyproject.toml` exists → Python project
- If `go.mod` exists → Go project
- If multiple: check the most recently modified manifest

## Step 2: Dispatch

Based on detected project type:
- **TypeScript**: Invoke `ts-fixer` sub-agent with the issue description
- **Python**: Invoke `py-fixer` sub-agent with the issue description
- **Go**: Invoke `go-fixer` sub-agent with the issue description

## Step 3: Verify

After the specialist completes, run the project's test suite to confirm the fix.
```

### Sub-agent — `.claude/agents/ts-fixer.md`

```yaml
---
name: ts-fixer
description: >
  Fixes issues in TypeScript projects. Understands Node.js, npm/pnpm,
  Vitest/Jest, and common TypeScript patterns. Use when the project
  is identified as TypeScript.
model: claude-sonnet-4-6
tools: [Read, Write, Edit, Bash]
maxTurns: 20
---

Fix the described issue in this TypeScript project.

1. Read the error or issue description
2. Locate relevant source files
3. Apply the fix following project conventions
4. Run `pnpm build && pnpm test` to verify
5. Report what was changed and why
```

### Sub-agent — `.claude/agents/py-fixer.md`

```yaml
---
name: py-fixer
description: >
  Fixes issues in Python projects. Understands pip/poetry, pytest,
  FastAPI/Django, and common Python patterns. Use when the project
  is identified as Python.
model: claude-sonnet-4-6
tools: [Read, Write, Edit, Bash]
maxTurns: 20
---

Fix the described issue in this Python project.

1. Read the error or issue description
2. Locate relevant source files
3. Apply the fix following project conventions
4. Run `pytest` to verify
5. Report what was changed and why
```

### Sub-agent — `.claude/agents/go-fixer.md`

```yaml
---
name: go-fixer
description: >
  Fixes issues in Go projects. Understands Go modules, go test,
  and common Go patterns. Use when the project is identified as Go.
model: claude-sonnet-4-6
tools: [Read, Write, Edit, Bash]
maxTurns: 20
---

Fix the described issue in this Go project.

1. Read the error or issue description
2. Locate relevant source files
3. Apply the fix following Go conventions and project patterns
4. Run `go build ./... && go test ./...` to verify
5. Report what was changed and why
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(pytest:*)",
      "Bash(go build:*)",
      "Bash(go test:*)",
      "Bash(cat package.json)",
      "Bash(cat pyproject.toml)",
      "Bash(cat go.mod)",
      "Bash(ls *)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Wrong specialist dispatched | Coordinator checks file timestamps for most recent activity; verifies fix compiles |
| Specialist applies incompatible fix | Post-fix verification runs project test suite |
| Coordinator overhead on simple fixes | Condition evaluation is fast (file existence checks); adds <5 seconds |

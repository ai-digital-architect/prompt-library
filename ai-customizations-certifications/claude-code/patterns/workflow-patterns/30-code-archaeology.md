# Pattern 30: Code Archaeology

## Category
Feedback & Learning Workflows

## Overview

A sub-agent traces the full git history of a file or function, correlates changes with commit messages and associated PR descriptions, and produces a narrative explanation of why the code evolved to its current state. Useful for onboarding or before undertaking a large refactor.

## Complete File Implementations

### Skill — `.claude/skills/code-archaeology/SKILL.md`

```yaml
---
name: code-archaeology
description: >
  Traces the evolution of a file or function through git history and
  produces a narrative explaining why the code looks the way it does.
  Use for onboarding, understanding legacy code, or before refactoring.
argument-hint: "[file-path] [optional: function-name]"
allowed-tools: Read, Bash
---

Trace code history: $ARGUMENTS

1. Invoke the `code-archaeologist` sub-agent
2. Present the narrative history with:
   - Chronological evolution of the code
   - Key decisions and why they were made
   - Patterns that emerged over time
   - Current design trade-offs to be aware of
```

### Sub-agent — `.claude/agents/code-archaeologist.md`

```yaml
---
name: code-archaeologist
description: >
  Traces git history of a file/function and produces a narrative explanation
  of its evolution. Correlates commits with PR descriptions. Read-only.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 15
---

Trace the history of the specified file or function.

1. Run `git log --follow --all -- <file>` for full history
2. For key commits, run `git show <hash>` to see the actual changes
3. If function specified, use `git log -L :<function>:<file>` for function-level history
4. Read commit messages and PR descriptions for context
5. Identify inflection points: major rewrites, architectural shifts, bug fixes

Produce a narrative at `.claude/archaeology/history.md`:

## Code Archaeology: [file/function name]

### Origin
- Created in commit [hash] on [date] by [author]
- Original purpose: [what it was built for]

### Evolution Timeline
1. **[date] — [purpose]**: [what changed and why]
2. **[date] — [purpose]**: [what changed and why]
...

### Key Decisions
- **[Decision]**: [Why it was made, citing commit message/PR]
- **[Decision]**: [Why it was made]

### Current State
- The code currently [does X] because of [historical reasons Y and Z]
- Trade-offs to be aware of: [list]
- If refactoring, consider: [recommendations]

### Contributors
[List of authors who significantly shaped this code]
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(git show:*)",
      "Bash(git blame:*)",
      "Bash(git diff:*)",
      "Bash(cat *)",
      "Bash(mkdir -p .claude/archaeology)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Archaeologist modifies historical code | `disallowedTools: [Write, Edit, MultiEdit]` |
| Git history reveals sensitive data (old secrets) | Narrative focuses on design decisions, not data values |
| Large file history overwhelms context | Uses `git log --follow` with targeted `git show` for key commits only |

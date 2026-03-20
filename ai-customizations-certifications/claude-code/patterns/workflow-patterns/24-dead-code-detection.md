# Pattern 24: Dead Code Detection

## Category
Review & Audit Workflows

## Overview

A sub-agent identifies unused exports, unreachable branches, and stale feature flags by combining static analysis (via Bash tools) with a read pass of the codebase. It produces a deletion candidate list that a human or a separate implementer sub-agent can act on.

## Complete File Implementations

### Skill — `.claude/skills/dead-code/SKILL.md`

```yaml
---
name: dead-code
description: >
  Identifies unused exports, unreachable code branches, and stale feature
  flags. Produces a deletion candidate list. Use during cleanup sprints
  or before major releases.
argument-hint: "[scope: all|src/module-name]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Detect dead code: $ARGUMENTS

1. Invoke the `dead-code-detector` sub-agent
2. Present the deletion candidate list grouped by type:
   - Unused exports
   - Unreachable branches
   - Stale feature flags
   - Orphaned files (no imports)
3. For each candidate, show the file, line, and last-modified date
4. Ask user which candidates to delete (or pass to an implementer agent)
```

### Sub-agent — `.claude/agents/dead-code-detector.md`

```yaml
---
name: dead-code-detector
description: >
  Identifies dead code: unused exports, unreachable branches, stale feature
  flags, and orphaned files. Read-only analysis using static analysis tools.
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

Scan for dead code using static analysis.

Techniques:
1. **Unused exports**: For each exported symbol, `grep -rn` for imports across the codebase.
   If zero imports found (excluding the defining file), it's a candidate.
2. **Unreachable branches**: Look for `if (false)`, `if (0)`, disabled feature flags,
   commented-out code blocks, and early-return guards that make downstream code unreachable.
3. **Stale feature flags**: Find feature flag references, check if any are permanently
   enabled/disabled in config.
4. **Orphaned files**: Find `.ts`/`.tsx` files not imported by any other file.

For each candidate, record:
- File path and line number
- Type (unused-export, unreachable, stale-flag, orphaned)
- Symbol/identifier name
- Last modified: `git log -1 --format="%ai" -- <file>`
- Confidence: high/medium/low

Write to `.claude/analysis/dead-code-report.json`.
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(grep -rn *)",
      "Bash(find *)",
      "Bash(git log:*)",
      "Bash(wc -l *)",
      "Bash(mkdir -p .claude/analysis)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Detector accidentally deletes code | `disallowedTools: [Write, Edit, MultiEdit]` — produces report only |
| False positives (dynamically used code) | Report includes confidence level; human review before deletion |
| Misidentifies test utilities as dead code | Detector checks test directories separately; excludes test helpers |

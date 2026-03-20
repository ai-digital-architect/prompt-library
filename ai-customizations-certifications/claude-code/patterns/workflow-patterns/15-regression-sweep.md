# Pattern 15: Regression Sweep

## Category
Validation & Verification Workflows

## Overview

A hook captures the full test suite results before a change is made. After implementation, a second hook captures results again. A diff sub-agent compares the two result sets and surfaces any newly failing tests, clearly attributing them to the change.

## Architecture Diagram

```
PreToolUse Hook                    Implementation               PostToolUse Hook
(captures baseline)                     phase                   (captures after)
       │                                  │                           │
       ▼                                  ▼                           ▼
 baseline-results.json      Agent makes code changes         post-results.json
       │                                                            │
       └──────────────────────┬─────────────────────────────────────┘
                              ▼
                   ┌──────────────────┐
                   │  Diff Agent       │
                   │  (read-only)      │
                   │  - Compares       │
                   │    baseline vs    │
                   │    post results   │
                   │  - Reports new    │
                   │    failures       │
                   └──────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/regression-sweep/SKILL.md`

```yaml
---
name: regression-sweep
description: >
  Captures test results before and after a code change, then diffs to identify
  any regressions introduced by the change. Use after any non-trivial edit
  to verify no existing tests were broken.
argument-hint: "[description of change made]"
allowed-tools: Read, Bash
---

Run regression sweep: $ARGUMENTS

1. Capture baseline: `pnpm test --reporter=json > .claude/regression/baseline.json`
2. (Changes should already be made at this point)
3. Capture post-change: `pnpm test --reporter=json > .claude/regression/post.json`
4. Invoke `regression-differ` sub-agent to compare results
5. Present: newly failing tests, newly passing tests, unchanged failures
```

### Sub-agent — `.claude/agents/regression-differ.md`

```yaml
---
name: regression-differ
description: >
  Compares two test result sets (before/after) and identifies regressions.
  Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 8
---

Compare test results in `.claude/regression/baseline.json` vs `.claude/regression/post.json`.

Produce a report:
1. **New Failures** — tests that passed before but fail now (REGRESSIONS)
2. **New Passes** — tests that failed before but pass now (FIXES)
3. **Unchanged Failures** — tests that failed both before and after (PRE-EXISTING)
4. **Summary** — total regressions count, attribution to changed files

Write to `.claude/regression/diff-report.md`.
```

### Hook — `.claude/hooks/capture-baseline.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: captures test baseline before first source file edit

baseline=".claude/regression/baseline.json"

# Only capture once per session (if baseline doesn't exist yet)
if [[ -f "$baseline" ]]; then
  exit 0
fi

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Trigger on first source file write
if [[ "$tool_name" =~ ^(Write|Edit|MultiEdit)$ ]] && [[ "$file_path" == src/* ]]; then
  mkdir -p .claude/regression
  pnpm test --reporter=json > "$baseline" 2>/dev/null || true
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/capture-baseline.sh"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Baseline captured at wrong time | Hook triggers only on first source edit; checks for existing baseline |
| Differ modifies code to fix regressions | `disallowedTools: [Write, Edit]` — report only |
| Test suite is slow, blocking the hook | Baseline capture runs once; hook exits 0 immediately on subsequent calls |

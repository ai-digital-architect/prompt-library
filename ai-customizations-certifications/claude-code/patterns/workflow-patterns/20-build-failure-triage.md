# Pattern 20: Build Failure Triage

## Category
Monitoring & Alerting Workflows

## Overview

Triggered by a CI failure notification (via a Stop or Notification hook). A sub-agent receives the failure log, diagnoses the root cause by reading recent commits and the failing test output, and produces a structured triage report with a proposed fix.

## Architecture Diagram

```
CI failure notification
(via Notification hook or manual trigger)
        │
        ▼
┌───────────────────────────┐
│  Triage Agent              │
│  (read-only)               │
│  - Reads failure log       │
│  - Reads recent commits    │
│  - Correlates changes to   │
│    failure                 │
│  - Produces triage report  │
│    with proposed fix       │
└───────────────────────────┘
        │
        ▼
  .claude/triage/report.md
```

## Complete File Implementations

### Skill — `.claude/skills/triage-build/SKILL.md`

```yaml
---
name: triage-build
description: >
  Diagnoses a CI/build failure by analyzing error logs, recent commits, and
  test output. Produces a structured triage report with root cause and proposed
  fix. Use when a build or CI pipeline fails.
argument-hint: "[failure-log-path or 'latest']"
allowed-tools: Read, Bash
---

Triage build failure: $ARGUMENTS

1. Invoke the `build-triager` sub-agent with the failure log
2. Present the triage report with:
   - Root cause identification
   - Commit that likely introduced the failure
   - Proposed fix with code references
   - Severity assessment
```

### Sub-agent — `.claude/agents/build-triager.md`

```yaml
---
name: build-triager
description: >
  Diagnoses build/CI failures by analyzing error logs, recent commits, and
  test output. Read-only — never modifies code.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

Diagnose the build failure. Do NOT modify any code.

1. Read the failure log (provided path or `pnpm test 2>&1`)
2. Extract the specific error messages and failing test names
3. Run `git log --oneline -10` to see recent commits
4. For each failing test, find the corresponding source file
5. Run `git log -5 -- <failing-file>` to identify recent changes
6. Correlate the error to the most likely causal commit

Write triage report to `.claude/triage/report.md`:

## Triage Report
- **Failure Type**: compile error / test failure / runtime error
- **Error Message**: exact message
- **Failing Files**: list with line numbers
- **Root Cause**: description of what went wrong
- **Causal Commit**: hash, author, message
- **Proposed Fix**: specific code change needed
- **Severity**: critical / high / medium / low
- **Confidence**: high / medium / low
```

### Hook — `.claude/hooks/on-ci-failure.sh`

```bash
#!/usr/bin/env bash
# Notification hook: triggers triage when CI failure notification arrives

input=$(cat)
message=$(echo "$input" | jq -r '.message // ""')

if echo "$message" | grep -qi "build failed\|ci failed\|pipeline failed"; then
  mkdir -p .claude/triage
  echo "$message" > .claude/triage/failure-notification.txt
  echo "CI failure detected — triage sub-agent should be invoked" >> ~/.claude/notifications.log
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(git show:*)",
      "Bash(pnpm test:*)",
      "Bash(cat *)",
      "Bash(grep -rn *)",
      "Bash(mkdir -p .claude/triage)"
    ]
  },
  "hooks": {
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/on-ci-failure.sh"
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
| Triager modifies source code | `disallowedTools: [Write, Edit, MultiEdit]` — analysis only |
| Triager accesses sensitive CI logs | Scope Bash permissions to read-only git and test commands |
| False root cause attribution | Uses `claude-opus-4-5` for higher accuracy; report includes confidence level |

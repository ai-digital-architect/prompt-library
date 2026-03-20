# Pattern 29: Test Failure Explainer

## Category
Feedback & Learning Workflows

## Overview

When a test fails in CI, a sub-agent receives the test name, failure message, and the last 10 commits touching that file. It traces back to the commit that introduced the regression, explains the failure in plain language, and suggests a fix — all as a read-only operation.

## Complete File Implementations

### Skill — `.claude/skills/explain-failure/SKILL.md`

```yaml
---
name: explain-failure
description: >
  Explains why a specific test is failing by tracing recent commits,
  identifying the regression commit, and suggesting a fix. Read-only
  analysis. Use when a test fails and the cause isn't immediately obvious.
argument-hint: "[test-name or test-file-path]"
allowed-tools: Read, Bash
---

Explain test failure: $ARGUMENTS

1. Run the failing test to capture the exact error: `pnpm test -- $1 2>&1`
2. Invoke `test-failure-explainer` sub-agent with the error output
3. Present:
   - Plain-language explanation of what's failing and why
   - The commit that most likely introduced the regression
   - A specific suggested fix
```

### Sub-agent — `.claude/agents/test-failure-explainer.md`

```yaml
---
name: test-failure-explainer
description: >
  Traces a test failure back to its root cause commit and explains the
  failure in plain language. Read-only.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 12
---

Diagnose the test failure.

1. Parse the error message to identify the failing assertion
2. Read the test file to understand what's being tested
3. Read the source file under test
4. Run `git log -10 -- <source-file>` to find recent changes
5. For each recent commit, run `git show <hash> -- <source-file>` to see what changed
6. Identify the commit that most likely broke the test
7. Explain the failure chain: what the test expects → what the code does → why they diverge

Write to `.claude/failures/explanation.md`:

## Test Failure Explanation
- **Test**: [test name]
- **Error**: [simplified error message]
- **Root Cause**: [plain-language explanation]
- **Regression Commit**: [hash] by [author] — [commit message]
- **What Changed**: [specific code change that broke the test]
- **Suggested Fix**: [concrete code change to resolve]
- **Confidence**: high/medium/low
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm test:*)",
      "Bash(git log:*)",
      "Bash(git show:*)",
      "Bash(git diff:*)",
      "Bash(git blame:*)",
      "Bash(cat *)",
      "Bash(mkdir -p .claude/failures)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Explainer modifies code | `disallowedTools: [Write, Edit, MultiEdit]` — analysis only |
| Wrong commit attributed | Uses `claude-opus-4-5` for accuracy; report includes confidence level |
| Test output contains sensitive data | Report focuses on structural explanation, not raw data |

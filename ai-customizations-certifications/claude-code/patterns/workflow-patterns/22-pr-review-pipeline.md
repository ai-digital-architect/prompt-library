# Pattern 22: PR Review Pipeline

## Category
Review & Audit Workflows

## Overview

A sequential chain of read-only sub-agents: diff analyzer → security reviewer → style checker → coverage checker → summary writer. Each sub-agent receives only the diff and its specialist context. A final sub-agent aggregates all findings into a single review comment.

## Architecture Diagram

```
User invokes /review-pr
        │
        ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Diff      │──▶│ Security │──▶│ Style    │──▶│ Coverage │──▶│ Summary  │
│ Analyzer  │   │ Reviewer │   │ Checker  │   │ Checker  │   │ Writer   │
│ (RO)      │   │ (RO)     │   │ (RO)     │   │ (RO)     │   │ (RO)     │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  diff.json    security.json  style.json    coverage.json  review.md
                                                            (unified)
```

## Complete File Implementations

### Skill — `.claude/skills/review-pr/SKILL.md`

```yaml
---
name: review-pr
description: >
  Runs a multi-specialist PR review pipeline: diff analysis, security review,
  style checking, coverage assessment, and unified summary. All read-only.
  Use for pull request reviews or pre-merge checks.
argument-hint: "[branch-name or commit-range]"
allowed-tools: Read, Bash
---

Review PR: $ARGUMENTS

1. Run `git diff $ARGUMENTS` and save to `.claude/review/diff.txt`
2. Invoke `diff-analyzer` → `.claude/review/diff-analysis.json`
3. Invoke `security-reviewer` → `.claude/review/security.json`
4. Invoke `style-checker` → `.claude/review/style.json`
5. Invoke `coverage-checker` → `.claude/review/coverage.json`
6. Invoke `review-summarizer` to aggregate all findings → `.claude/review/review.md`
7. Present the unified review
```

### Sub-agent — `.claude/agents/diff-analyzer.md`

```yaml
---
name: diff-analyzer
description: >
  Analyzes a git diff to categorize changes by type, identify high-risk
  modifications, and flag large changesets. Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 8
---

Analyze the diff in `.claude/review/diff.txt`.

Categorize each changed file:
- New feature code
- Bug fix
- Refactor (no behavior change)
- Test changes
- Configuration changes
- Documentation

Flag: files with >200 lines changed, modifications to auth/security modules,
database schema changes, dependency updates.

Write to `.claude/review/diff-analysis.json`.
```

### Sub-agent — `.claude/agents/security-reviewer.md`

```yaml
---
name: security-reviewer
description: >
  Reviews code changes for security vulnerabilities including injection,
  auth flaws, secrets exposure, and insecure dependencies. Read-only.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 10
---

Review the diff for security issues.

Check for:
1. Injection vulnerabilities (SQL, command, path traversal)
2. Authentication/authorization logic changes
3. Hardcoded secrets or credentials
4. Insecure dependencies added
5. Input validation completeness
6. CORS or security header changes

Write findings to `.claude/review/security.json` with severity ratings.
```

### Sub-agent — `.claude/agents/style-checker.md`

```yaml
---
name: style-checker
description: >
  Checks code changes against project style conventions defined in CLAUDE.md.
  Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 8
---

Check the diff against project conventions.

Verify:
1. Naming conventions followed
2. JSDoc/documentation present on new functions
3. Error handling patterns used correctly
4. File organization matches project structure
5. No banned patterns (from CLAUDE.md anti-patterns list)

Write to `.claude/review/style.json`.
```

### Sub-agent — `.claude/agents/coverage-checker.md`

```yaml
---
name: coverage-checker
description: >
  Assesses test coverage for changed code. Identifies untested paths. Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 8
---

Assess test coverage for the changed files.

1. Identify all new/modified functions
2. Check if corresponding test files exist
3. Run `pnpm test --coverage` if available
4. Flag any new public function without a test
5. Flag any modified logic path without test coverage

Write to `.claude/review/coverage.json`.
```

### Sub-agent — `.claude/agents/review-summarizer.md`

```yaml
---
name: review-summarizer
description: >
  Aggregates findings from all review specialists into a unified PR review
  comment. Read-only.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 6
---

Read all review files in `.claude/review/` and produce a unified summary.

Format as a PR review comment:
1. **Overall Assessment**: Approve / Request Changes / Comment
2. **Security**: Critical and high issues (if any)
3. **Style**: Convention violations
4. **Coverage**: Untested paths
5. **Risk Assessment**: Overall risk level of the change
6. **Actionable Items**: Numbered list of specific things to fix

Write to `.claude/review/review.md`.
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(git show:*)",
      "Bash(pnpm test:*)",
      "Bash(grep -rn *)",
      "Bash(mkdir -p .claude/review)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Reviewers modify code | All 5 sub-agents have `disallowedTools: [Write, Edit, MultiEdit]` |
| Security reviewer misses vulnerability | Uses `claude-opus-4-5` for higher accuracy on security analysis |
| Review pipeline is slow | Each specialist is capped at 6–10 turns; parallel execution where possible |

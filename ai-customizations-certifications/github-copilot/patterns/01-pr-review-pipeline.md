# Pattern 8.1 — PR Review Pipeline

> A sequential chain of read-only sub-agents: diff analyzer → security reviewer → style checker → coverage checker → summary writer.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Sequential read-only sub-agents | Sub-agents with restricted `tools` (no edit) |
| Final aggregation sub-agent | Dedicated summary sub-agent |
| Each specialist receives only the diff | Isolated sub-agent context (automatic in Copilot) |

## Implementation Fidelity: ✅ High

This is one of the strongest pattern mappings. Copilot's sub-agent isolation ensures each reviewer sees only what it's given, and the parent orchestrates the pipeline.

---

## File Structure

```
.github/
├── agents/
│   ├── pr-review-orchestrator.agent.md
│   ├── diff-analyzer.agent.md
│   ├── security-reviewer.agent.md
│   ├── style-checker.agent.md
│   ├── coverage-checker.agent.md
│   └── review-summarizer.agent.md
```

## Agent Definitions

### `.github/agents/pr-review-orchestrator.agent.md`

```yaml
---
name: PR Review Orchestrator
description: >
  Run a comprehensive PR review pipeline across security, style,
  coverage, and quality dimensions. Aggregates all findings.
tools: ['agent', 'search', 'terminalLastCommand']
agents: ['Diff Analyzer', 'Security Reviewer', 'Style Checker', 'Coverage Checker', 'Review Summarizer']
---

For each PR review request:

1. Invoke Diff Analyzer to parse the changeset and produce a structured diff summary
2. Invoke Security Reviewer with the diff summary
3. Invoke Style Checker with the diff summary
4. Invoke Coverage Checker with the diff summary
5. Collect all specialist reports
6. Invoke Review Summarizer with all reports to produce the final review

Present the unified review to the user.
```

### `.github/agents/diff-analyzer.agent.md`

```yaml
---
name: Diff Analyzer
description: Parse a code diff and produce a structured change summary. Read-only.
tools: ['codebase', 'search', 'terminalLastCommand']
---

Analyze the diff (use `git diff main...HEAD` or the provided diff):

- Files added, modified, deleted
- For each file: lines added, lines removed, nature of change (logic, config, test, docs)
- Blast radius: what areas of the codebase are affected
- Complexity assessment: trivial / moderate / significant

Output a structured summary that downstream reviewers can consume.
```

### `.github/agents/security-reviewer.agent.md`

```yaml
---
name: Security Reviewer
description: Review code changes for security vulnerabilities. Read-only.
tools: ['codebase', 'search']
---

Review the diff for security concerns:

- SQL injection, XSS, CSRF vulnerabilities
- Hardcoded secrets, API keys, or credentials
- Insecure deserialization or input handling
- Authentication and authorization gaps
- Dependency additions with known CVEs

Rate each finding: CRITICAL / HIGH / MEDIUM / LOW.
If no issues found, explicitly confirm: "No security concerns identified."
```

### `.github/agents/style-checker.agent.md`

```yaml
---
name: Style Checker
description: Check code style, naming conventions, and project consistency. Read-only.
tools: ['codebase', 'search']
---

Review the diff for style and convention adherence:

- Naming conventions (variables, functions, files)
- Code organization and module boundaries
- Comment quality and documentation
- Consistency with existing patterns in the codebase
- Adherence to copilot-instructions.md standards

Rate issues as: MUST FIX (blocks merge) / SUGGESTION (nice to have) / NIT.
```

### `.github/agents/coverage-checker.agent.md`

```yaml
---
name: Coverage Checker
description: Assess test coverage for changed code. Read-only.
tools: ['codebase', 'search', 'terminalLastCommand']
---

For each modified file in the diff:

1. Check if corresponding tests exist
2. Run `pnpm test --coverage` or `pytest --cov` if possible
3. Identify new code paths that lack test coverage
4. Check for regression test coverage of bug fixes

Report: covered paths, uncovered paths, and recommended tests to add.
```

### `.github/agents/review-summarizer.agent.md`

```yaml
---
name: Review Summarizer
description: Aggregate specialist review reports into a unified PR review. Read-only.
tools: ['search']
---

Given reports from Security, Style, and Coverage reviewers, produce:

## PR Review Summary

### Verdict: APPROVE / REQUEST CHANGES / COMMENT

### Blocking Issues (must fix before merge)
- List each with source reviewer and severity

### Non-Blocking Suggestions
- Improvements that can be addressed later

### Test Coverage Assessment
- Adequate / Needs improvement / Missing for critical paths

### Overall Assessment
2-3 sentence summary of the PR's quality and readiness.
```

---

## SDK Alternative: Automated PR Review on Push

```python
# .github/scripts/pr_review.py
from copilot import CopilotClient

def read_only_handler(request, context):
    if request["kind"] in ["read", "search"]:
        return {"kind": "approved"}
    if request["kind"] == "shell":
        cmd = context.get("command", "")
        safe = ["git diff", "git log", "git show", "pnpm test", "pytest"]
        if any(cmd.startswith(s) for s in safe):
            return {"kind": "approved"}
    return {"kind": "denied"}

async def review_pr():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "claude-sonnet-4.5",
        "instructions": "You are a thorough PR reviewer.",
        "on_permission_request": read_only_handler
    })

    result = await session.send_and_wait({
        "prompt": "Review the diff between main and HEAD. "
                  "Check security, style, and test coverage. "
                  "Produce a structured review summary."
    })

    print(result.content)
    await client.stop()
```

# Pattern 7.2 — Build Failure Triage

> Triggered by a CI failure. A sub-agent receives the failure log, diagnoses root cause by reading recent commits and failing test output, and produces a triage report with a proposed fix.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Stop/Notification hook triggers on CI failure | GitHub Actions triggers Copilot SDK on failure |
| Sub-agent reads logs and recent commits | Agent + Skill for triage procedure |
| Structured triage report | Agent output or PR comment |

## Implementation Fidelity: ✅ High

---

## File Structure

```
.github/
├── agents/
│   └── build-triager.agent.md
├── skills/
│   └── ci-debugging/
│       ├── SKILL.md
│       └── references/
│           └── common-errors.md
└── workflows/
    └── triage-on-failure.yml
```

## Agent Definition

### `.github/agents/build-triager.agent.md`

```yaml
---
name: Build Triager
description: >
  Diagnose CI build failures by analyzing logs, recent commits, and test output.
  Produces a structured triage report with root cause and proposed fix.
tools: ['codebase', 'search', 'terminalLastCommand', 'usages']
---

You are a CI build failure specialist. When given a failure log:

1. Parse the failure log to identify the failing step and error message
2. Read the last 10 commits that touched the failing files: `git log -10 --oneline -- <file>`
3. Identify the most likely commit that introduced the failure
4. Read the failing test(s) and the code they exercise
5. Determine root cause

## Triage Report Format

### Failure Summary
- **Build step**: which CI step failed
- **Error**: the primary error message
- **Failing test(s)**: test name(s) and file(s)

### Root Cause Analysis
- **Likely cause**: description
- **Introducing commit**: hash + message
- **Affected files**: list

### Proposed Fix
- Description of the fix
- Specific code changes needed
- Confidence level: High / Medium / Low

### Prevention
- How to prevent this class of failure in the future
```

## GitHub Actions Integration

### `.github/workflows/triage-on-failure.yml`

```yaml
name: Auto-Triage on Failure
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  triage:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install copilot-sdk
      - name: Download failure logs
        uses: actions/download-artifact@v4
        with:
          name: ci-logs
          run-id: ${{ github.event.workflow_run.id }}
      - name: Run triage
        run: python .github/scripts/triage.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### `.github/scripts/triage.py`

```python
from copilot import CopilotClient

async def triage():
    client = CopilotClient()
    await client.start()

    # Read the failure log
    with open("ci-logs/output.log", "r") as f:
        failure_log = f.read()[-5000:]  # Last 5000 chars

    session = await client.create_session({
        "model": "claude-sonnet-4.5",
        "instructions": "You are a CI failure triage specialist.",
        "skill_directories": ["./.github/skills/ci-debugging/SKILL.md"]
    })

    result = await session.send_and_wait({
        "prompt": f"Triage this CI failure:\n\n```\n{failure_log}\n```"
    })

    print(result.content)
    await client.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(triage())
```

## Supporting Skill

### `.github/skills/ci-debugging/SKILL.md`

```yaml
---
name: ci-debugging
description: >
  Procedures for debugging CI build failures. Use when analyzing
  build logs, test failures, or CI configuration issues.
---

## Common Failure Patterns

See [references/common-errors.md](./references/common-errors.md) for a catalog of
known CI failure patterns and their resolutions.

## Debugging Procedure
1. Read the full error output — the first error is usually the root cause
2. Check if the failure reproduces locally
3. Check recent commits to the failing area
4. Check for environment differences (Node version, OS, dependencies)
```

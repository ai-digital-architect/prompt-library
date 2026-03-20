# Pattern 03: Self-Reflection Loop

## Category
Pipeline & Ordering Workflows

## Overview

A generate → critique → revise cycle that iterates until a quality threshold is met. A read-only critic sub-agent scores the output as structured JSON. A `SubagentStop` hook reads the score and either allows the session to stop or blocks it and forces another revision pass. This produces consistently high-quality output without human intervention.

## Architecture Diagram

```
User invokes /self-reflect
        │
        ▼
┌──────────────────┐
│  Generator Agent  │◄──────────────────────────────────┐
│  (parent context) │                                    │
│  - Produces code  │                                    │
│  - Applies fixes  │                                    │
└────────┬─────────┘                                    │
         │                                               │
         ▼                                               │
┌──────────────────┐     SubagentStop Hook              │
│  Critic Agent     │────(reads score JSON)──────────────┘
│  (read-only)      │     score < 4? → force revision
│  - Scores 1–5     │     score ≥ 4? → allow stop
│  - Lists issues   │
└──────────────────┘
```

## Component Breakdown

| Component | Role | Why This Component |
|-----------|------|--------------------|
| **Skill** | Entry point; orchestrates generate-critique loop | User/auto-invocable; manages the iteration logic |
| **Critic sub-agent** | Read-only quality reviewer | Isolated context; cannot modify the code it reviews |
| **SubagentStop Hook** | Score-based loop control | Deterministic; reads JSON score from critic output |
| **CLAUDE.md** | Quality rubric and scoring criteria | Always-on; ensures consistent evaluation standards |

## Complete File Implementations

### Project Memory — `CLAUDE.md`

```markdown
# Quality Standards

## Self-Reflection Scoring Rubric
When reviewing code, score 1–5 on each dimension:
- **Security** (1–5): injection safety, auth checks, input validation
- **Correctness** (1–5): edge cases, error handling, type safety
- **Maintainability** (1–5): naming, separation of concerns, documentation
- **Test Coverage** (1–5): key paths, edge cases, failure modes

Overall score = minimum of all dimension scores.
Do NOT approve (overall < 4) if any Critical or High severity issue exists.
```

### Skill — `.claude/skills/self-reflect/SKILL.md`

```yaml
---
name: self-reflect
description: >
  Implements code with an automated quality loop. Generates code, invokes
  a critic for scoring, and iterates until score ≥ 4/5. Use when quality
  is critical or when implementing non-trivial features.
argument-hint: "[feature or task description]"
allowed-tools: Read, Write, Edit, Bash
---

Implement with automated quality loop: $ARGUMENTS

## Workflow

1. **Generate**: Implement the requested feature/fix
2. **Critique**: Invoke the `code-critic` sub-agent on all changed files
3. **Evaluate**: Read the critic's score from `.claude/review-score.json`
   - If overall score ≥ 4: proceed to final summary
   - If overall score < 4: fix all Critical and High issues, then re-invoke critic
4. **Iterate**: Repeat steps 2–3 up to 3 times maximum
5. **Report**: Present the final implementation with the last critic score

If after 3 iterations the score is still < 4, present the current state
with the outstanding issues listed for human review.
```

### Sub-agent — `.claude/agents/code-critic.md`

```yaml
---
name: code-critic
description: >
  Reviews code changes for quality, security, test coverage, and adherence
  to project standards. Returns structured JSON scores. Use in self-reflection
  loops or after implementing any non-trivial feature.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 8
---

You are a strict code critic. Review the recently changed files.

For every file changed:
1. Check for security vulnerabilities (injection, auth bypass, secrets exposure)
2. Verify correctness (edge cases, error handling, type narrowing)
3. Assess maintainability (naming, SoC, JSDoc completeness)
4. Evaluate test coverage (are key paths tested? edge cases?)

Write your review to `.claude/review-score.json` using this exact schema:

```json
{
  "overall_score": 3,
  "dimensions": {
    "security": { "score": 4, "issues": [] },
    "correctness": { "score": 3, "issues": ["Missing null check in parseInput()"] },
    "maintainability": { "score": 4, "issues": [] },
    "test_coverage": { "score": 2, "issues": ["No test for error path in createUser"] }
  },
  "critical_issues": ["Missing null check in parseInput()"],
  "high_issues": ["No test for error path in createUser"],
  "recommendation": "Fix null check and add error path test, then re-review"
}
```

Overall score = minimum of all dimension scores.
Be rigorous. Do not inflate scores.
```

### Hook — `.claude/hooks/check-review-score.sh`

```bash
#!/usr/bin/env bash
# SubagentStop hook: reads critic score and decides whether to allow stop

input=$(cat)
agent_name=$(echo "$input" | jq -r '.agent_name // ""')

# Only gate on the code-critic agent
if [[ "$agent_name" != "code-critic" ]]; then
  exit 0
fi

# Read the score file
score_file=".claude/review-score.json"
if [[ ! -f "$score_file" ]]; then
  echo '{"reason": "Critic did not produce a score file. Re-run the review."}' >&2
  exit 2
fi

overall=$(jq -r '.overall_score // 0' "$score_file")

if [[ "$overall" -lt 4 ]]; then
  issues=$(jq -r '.recommendation // "See review for details"' "$score_file")
  echo "{\"reason\": \"Score $overall/5 below threshold. $issues\"}" >&2
  # Note: exit 2 blocks the stop — parent agent sees this and iterates
  exit 2
fi

# Score meets threshold — allow
exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(pnpm lint:*)",
      "Bash(cat .claude/review-score.json)",
      "Bash(jq * .claude/review-score.json)"
    ],
    "deny": [
      "Bash(rm -rf *)"
    ]
  },
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/check-review-score.sh"
          }
        ]
      }
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
│   │   └── code-critic.md
│   ├── skills/
│   │   └── self-reflect/
│   │       └── SKILL.md
│   ├── hooks/
│   │   └── check-review-score.sh
│   └── review-score.json         ← Critic output (gitignored)
└── src/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Critic modifies code it reviews | `disallowedTools: [Write, Edit, MultiEdit]` — strictly read-only |
| Infinite revision loop | Skill caps at 3 iterations; `maxTurns: 8` on critic |
| Critic produces invalid JSON | Hook checks for file existence; `jq` validates structure |
| Generator ignores critic feedback | Skill instructions explicitly require fixing Critical/High issues before re-invoke |

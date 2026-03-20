# Pattern 1.3 — Self-Reflection Loop

> A generate → critique → revise cycle that iterates until a quality threshold is met.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Read-only critic sub-agent (structured JSON score) | Sub-agent with `tools: ['codebase', 'search']` (read-only whitelist) |
| SubagentStop hook (score gate) | Parent agent prompt logic — inspect score and loop |
| Generate → Critique → Revise cycle | Parent agent orchestrates the loop via sub-agent invocations |

## Implementation Fidelity: ✅ High

This maps directly to the **Sub-agent Review Loop** pattern described in Section 4.6 of the architecture guide. The parent agent writes code, invokes a reviewer sub-agent, reads the score, and iterates.

---

## File Structure

```
.github/
├── agents/
│   ├── quality-coder.agent.md
│   └── critic.agent.md
└── skills/
    └── quality-rubric/
        └── SKILL.md
```

## Agent Definitions

### `.github/agents/quality-coder.agent.md`

```yaml
---
name: Quality Coder
description: >
  Write code with automatic quality review loop. Iterates until the
  critic scores the output 4/5 or higher. Use for any implementation
  task where quality matters.
tools: ['agent', 'editFiles', 'terminalLastCommand', 'search']
agents: ['Critic']
model: ['GPT-5.2', 'Claude Sonnet 4.5']
---

You are a quality-focused developer. For every coding task:

1. Implement the solution
2. Invoke the Critic agent to review your work
3. Parse the Critic's structured response — extract the overall score
4. If the score is below 4/5:
   a. Read each issue the Critic identified
   b. Fix every issue
   c. Invoke the Critic again
5. Repeat steps 2–4 until the Critic returns a score of 4/5 or higher
6. Maximum iterations: 3. If the score remains below 4/5 after 3 cycles,
   present the current state with the outstanding issues to the user.

CRITICAL: Do NOT present results to the user until the Critic approves
OR you have exhausted the maximum iterations.
```

### `.github/agents/critic.agent.md`

```yaml
---
name: Critic
description: >
  Review code changes and produce a structured quality score.
  Read-only — does not modify code.
tools: ['codebase', 'search']
model: ['Claude Opus 4.5', 'GPT-5.2']
---

You are a code quality critic. Review the provided code changes and
produce a structured evaluation.

## Scoring Rubric (1–5 each dimension)

- **Correctness**: Does the code do what it claims? Edge cases handled?
- **Security**: No vulnerabilities, proper input validation, no secrets
- **Performance**: Efficient algorithms, no N+1 queries, appropriate caching
- **Maintainability**: Clear naming, appropriate comments, small functions
- **Test coverage**: Key paths tested, edge cases covered

## Required Output Format

```
SCORE: <overall score 1-5 (average of dimensions, rounded)>

DIMENSION SCORES:
- Correctness: X/5
- Security: X/5
- Performance: X/5
- Maintainability: X/5
- Test Coverage: X/5

ISSUES:
1. [SEVERITY: high|medium|low] Description of issue — file:line
2. ...

SUGGESTED FIXES:
1. For issue #1: specific fix description
2. ...
```

Be rigorous. A score of 4/5 means production-ready with minor nits only.
A score of 5/5 means exemplary code you would hold up as a team reference.
```

## Supporting Skill

### `.github/skills/quality-rubric/SKILL.md`

```yaml
---
name: quality-rubric
description: >
  Quality scoring rubric and review criteria for the self-reflection loop.
  Use when reviewing code quality or calibrating review standards.
---

## Score Interpretation

| Score | Meaning | Action |
|---|---|---|
| 5/5 | Exemplary — reference-quality code | Ship immediately |
| 4/5 | Production-ready — minor nits only | Ship with optional polish |
| 3/5 | Acceptable — several non-blocking issues | Requires one more revision pass |
| 2/5 | Below standard — significant issues | Requires substantial rework |
| 1/5 | Unacceptable — fundamental problems | Start over with a different approach |

## Review Focus by Language

- **TypeScript**: strict mode compliance, proper generics, no `any` escape hatches
- **Python**: type hints on all public functions, no mutable default arguments
- **SQL**: parameterized queries (never string concatenation), index usage
```

---

## Key Difference from Claude Code

In Claude Code, the `SubagentStop` hook reads the critic's JSON score and deterministically blocks or allows the session to end. In Copilot, this gating logic lives in the **parent agent's prompt**. The parent agent is instructed to parse the Critic's structured output and loop until the threshold is met. This is prompt-driven rather than hook-driven, making it slightly less deterministic but fully functional for the pattern.

The deliberate use of **different models** for generator and critic (e.g., GPT-5.2 for generation, Claude Opus 4.5 for review) provides diversity of perspective, reducing the risk of blind spots.

# Pattern 08: Competitive Analysis

## Category
Research & Discovery Workflows

## Overview

Multiple parallel sub-agents each research a different source, competitor, or approach. A synthesis agent aggregates all findings into a structured report. `SubagentStop` hooks log each researcher's completion before the synthesizer is invoked. This pattern is the fan-out/fan-in applied specifically to information gathering.

## Architecture Diagram

```
User invokes /competitive-analysis
        │
        ▼
┌──────────────────────┐
│  Coordinator (Skill)  │
│  - Identifies targets │
│  - Fans out           │
└──┬───┬───┬───────────┘
   │   │   │
   ▼   ▼   ▼
┌─────┐┌─────┐┌─────┐     Each writes to
│ R-1 ││ R-2 ││ R-N │     .claude/analysis/<target>.json
│(RO) ││(RO) ││(RO) │
└──┬──┘└──┬──┘└──┬──┘
   │      │      │
   ▼      ▼      ▼
  SubagentStop hooks → completion log
               │
               ▼
       ┌──────────────┐
       │  Synthesizer  │
       │  (read-only)  │
       │  - Reads all  │
       │  - Compares   │
       │  - Reports    │
       └──────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/competitive-analysis/SKILL.md`

```yaml
---
name: competitive-analysis
description: >
  Runs parallel research sub-agents against multiple sources or competitors
  and synthesizes findings into a structured comparison report. Use for
  technology evaluations, library comparisons, or competitive research.
argument-hint: "[topic] [target1,target2,target3]"
allowed-tools: Read, Write, Bash
---

Conduct competitive analysis: $ARGUMENTS

1. Parse the targets from arguments (comma-separated list or infer from topic)
2. Create `.claude/analysis/` directory
3. For each target, invoke the `source-researcher` sub-agent with:
   - The target name/URL/identifier
   - The analysis criteria (features, pricing, performance, DX, community)
4. After all researchers complete, invoke the `analysis-synthesizer` sub-agent
5. Present the synthesized comparison report
```

### Sub-agent — `.claude/agents/source-researcher.md`

```yaml
---
name: source-researcher
description: >
  Researches a single target (library, tool, competitor, approach) and produces
  a structured findings file. Read-only. Use in parallel research workflows.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 12
---

Research the assigned target thoroughly using read-only tools.

Produce a JSON file at `.claude/analysis/<target-name>.json`:
```json
{
  "target": "<name>",
  "category": "<type>",
  "findings": {
    "features": ["..."],
    "strengths": ["..."],
    "weaknesses": ["..."],
    "pricing": "...",
    "community": "...",
    "documentation_quality": "1-5",
    "maturity": "1-5"
  },
  "raw_notes": "Free-form observations..."
}
```

Be objective. Document both strengths and weaknesses.
```

### Sub-agent — `.claude/agents/analysis-synthesizer.md`

```yaml
---
name: analysis-synthesizer
description: >
  Reads all individual research files and produces a unified comparison
  report. Use after all source-researchers complete.
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

Read all `.json` files in `.claude/analysis/` and produce a comparison report.

Include:
1. **Executive Summary** — Top recommendation with rationale
2. **Feature Matrix** — Side-by-side comparison table
3. **Strengths/Weaknesses** — Per target, synthesized from individual reports
4. **Risk Assessment** — Vendor lock-in, community health, maintenance burden
5. **Recommendation** — Ranked options with justification

Write the report to `.claude/analysis/comparison-report.md`.
```

### Settings — `.claude/settings.json`

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/track-worker-completion.sh"
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
| Researchers modify project files | `disallowedTools: [Write, Edit, MultiEdit]` on all research agents |
| Biased analysis from single model | Use `claude-opus-4-5` for synthesizer (stronger reasoning) |
| Inconsistent output formats | Strict JSON schema in researcher instructions |

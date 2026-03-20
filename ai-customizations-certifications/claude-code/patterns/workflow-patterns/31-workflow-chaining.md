# Pattern 31: Workflow Chaining

## Category
Orchestration Meta-Workflows

## Overview

The output artifact of one skill is automatically passed as input to the next. For example, `/plan-feature` produces a plan file, and `/implement-feature` reads that file as its starting context, enabling a multi-session pipeline without manual copy-paste.

## Architecture Diagram

```
User invokes /plan-feature "user auth"
        │
        ▼
┌──────────────────┐
│  Plan Skill       │
│  - Researches     │
│  - Produces       │
│    plan.md        │
└────────┬─────────┘
         │
         ▼
  .claude/chain/plan.md  (output artifact)
         │
User invokes /implement-feature (or auto-chain)
         │
         ▼
┌──────────────────┐
│  Implement Skill  │
│  - Reads plan.md  │
│  - Implements     │
│  - Produces       │
│    result.md      │
└────────┬─────────┘
         │
         ▼
  .claude/chain/result.md
         │
User invokes /review-feature (or auto-chain)
         │
         ▼
┌──────────────────┐
│  Review Skill     │
│  - Reads result   │
│  - Reviews code   │
└──────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/plan-feature/SKILL.md`

```yaml
---
name: plan-feature
description: >
  Creates a detailed implementation plan for a feature. Outputs a plan file
  that can be consumed by /implement-feature. Use as the first step in a
  feature development chain.
argument-hint: "[feature description]"
allowed-tools: Read, Bash
---

Plan feature: $ARGUMENTS

1. Research the codebase to understand relevant modules and patterns
2. Design the implementation approach
3. Write the plan to `.claude/chain/plan.md` with:
   - Feature summary
   - Files to create/modify
   - Implementation steps (ordered)
   - Test strategy
   - Risks and mitigations
4. Tell the user: "Plan saved. Run `/implement-feature` to execute it."
```

### Skill — `.claude/skills/implement-feature/SKILL.md`

```yaml
---
name: implement-feature
description: >
  Implements a feature from a plan file produced by /plan-feature. Reads
  the plan and executes each step. Use after planning is complete.
argument-hint: "[optional: override instructions]"
allowed-tools: Read, Write, Edit, Bash
---

Implement from plan.

1. Read `.claude/chain/plan.md` — if it doesn't exist, tell the user to run `/plan-feature` first
2. Execute each implementation step from the plan
3. Write tests alongside code
4. Run `pnpm build && pnpm test`
5. Write implementation summary to `.claude/chain/result.md`
6. Tell the user: "Implementation complete. Run `/review-feature` to review."
```

### Skill — `.claude/skills/review-feature/SKILL.md`

```yaml
---
name: review-feature
description: >
  Reviews a feature implementation by reading the chain artifacts (plan and
  result) and comparing against the original requirements. Use as the
  final step in a feature development chain.
argument-hint: "[optional: specific concerns]"
allowed-tools: Read, Bash
---

Review feature implementation.

1. Read `.claude/chain/plan.md` for the original plan
2. Read `.claude/chain/result.md` for the implementation summary
3. Compare implementation against plan:
   - Were all planned steps completed?
   - Were any unplanned changes made?
   - Does the test coverage match the test strategy?
4. Run `pnpm test` to verify everything passes
5. Produce a review summary with approval/rejection recommendation
```

### Project Memory — `CLAUDE.md` (relevant section)

```markdown
## Workflow Chaining Convention
- Chain artifacts are stored in `.claude/chain/`
- Each skill in a chain reads the previous skill's output from this directory
- Skills should check for prerequisite files and guide the user if missing
- Chain directory is cleaned at the start of `/plan-feature`
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(cat .claude/chain/*)",
      "Bash(mkdir -p .claude/chain)",
      "Bash(rm -f .claude/chain/*)",
      "Bash(git diff:*)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Stale plan from different feature | Plan skill cleans chain directory before writing |
| Implementer deviates from plan | Review skill explicitly compares plan vs implementation |
| Chain artifacts accumulate | Each chain starts with a clean directory |

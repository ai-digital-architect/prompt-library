# Pattern 04: Human-in-the-Loop Approval

## Category
Gating & Approval Workflows

## Overview

The agent pauses at a defined stage, surfaces a summary to the user, and waits for explicit sign-off before proceeding. Implemented via a skill that halts and prompts, or a `PreToolUse` hook that blocks execution until a sentinel file (approval marker) is present. This prevents the agent from making irreversible changes without human review.

## Architecture Diagram

```
User invokes /approve-then-deploy
        │
        ▼
┌──────────────────────┐
│  Phase 1: Prepare    │
│  - Generate changes  │
│  - Write summary to  │
│    .claude/approval/  │
│    pending.md        │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  PAUSE               │
│  Present summary to  │
│  user. Ask for       │
│  explicit approval.  │
│                      │
│  User types "approve"│
│  → writes sentinel   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐     PreToolUse Hook
│  Phase 2: Execute    │◄───(checks sentinel file)
│  - Apply changes     │     File exists? → allow
│  - Run deployment    │     Missing? → block (exit 2)
│  - Clean up sentinel │
└──────────────────────┘
```

## Component Breakdown

| Component | Role | Why This Component |
|-----------|------|--------------------|
| **Skill** | Two-phase workflow with pause in between | Orchestrates prepare → pause → execute |
| **PreToolUse Hook** | Blocks destructive operations without approval | Deterministic enforcement; zero tokens |
| **CLAUDE.md** | Documents the approval protocol | All agents know how the gate works |

## Complete File Implementations

### Skill — `.claude/skills/approve-then-deploy/SKILL.md`

```yaml
---
name: approve-then-deploy
description: >
  Two-phase workflow that prepares changes, presents a summary for human
  approval, and only executes after explicit sign-off. Use for deployments,
  database migrations, or any irreversible operation.
argument-hint: "[operation description]"
allowed-tools: Read, Write, Edit, Bash
---

Execute with human approval gate: $ARGUMENTS

## Phase 1: Prepare

1. Analyze the requested operation
2. Generate all necessary changes but do NOT apply destructive operations yet
3. Write a clear summary to `.claude/approval/pending.md` containing:
   - What will change (files, resources, environments)
   - Risk assessment (low/medium/high)
   - Rollback plan
   - Estimated impact
4. Present the summary to the user and ask:
   **"Please review the changes above. Type 'approve' to proceed or 'reject' to cancel."**

## Phase 2: Execute (only after approval)

5. Wait for the user to confirm with "approve"
6. Create the sentinel file: `touch .claude/approval/approved`
7. Execute the destructive/irreversible operations
8. Remove the sentinel: `rm .claude/approval/approved`
9. Present the execution result

If the user types "reject", clean up all pending artifacts and stop.
```

### Hook — `.claude/hooks/require-approval.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: blocks destructive Bash commands unless approval sentinel exists

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""')
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only gate on Bash tool
if [[ "$tool_name" != "Bash" ]]; then
  exit 0
fi

# Define destructive command patterns
destructive_patterns=(
  "deploy"
  "migrate"
  "kubectl apply"
  "terraform apply"
  "docker push"
  "npm publish"
  "pnpm publish"
)

is_destructive=false
for pattern in "${destructive_patterns[@]}"; do
  if echo "$command" | grep -qi "$pattern"; then
    is_destructive=true
    break
  fi
done

if [[ "$is_destructive" == "false" ]]; then
  exit 0
fi

# Check for approval sentinel
if [[ ! -f ".claude/approval/approved" ]]; then
  echo '{"decision": "block", "reason": "Destructive operation requires human approval. Write summary to .claude/approval/pending.md and wait for user to approve."}' >&2
  exit 2
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm build:*)",
      "Bash(pnpm test:*)",
      "Bash(git diff:*)",
      "Bash(git status:*)",
      "Bash(touch .claude/approval/approved)",
      "Bash(rm .claude/approval/approved)",
      "Bash(cat .claude/approval/*)",
      "Bash(mkdir -p .claude/approval)"
    ],
    "deny": [
      "Bash(rm -rf /:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/require-approval.sh"
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
│   ├── skills/
│   │   └── approve-then-deploy/
│   │       └── SKILL.md
│   ├── hooks/
│   │   └── require-approval.sh
│   └── approval/                 ← Approval artifacts (gitignored)
│       └── .gitkeep
└── src/
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Agent creates sentinel file itself to bypass gate | Skill instructions explicitly separate prepare/execute phases; hook validates contextually |
| Stale sentinel from previous session | Hook could check file age; or Stop hook always cleans up sentinel |
| User approves without reading summary | Summary is presented in chat; skill pauses explicitly for user response |
| Destructive pattern list is incomplete | Default-deny approach: add new patterns as discovered; keep the list in a maintainable location |

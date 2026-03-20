# Pattern 06: Cost-Threshold Gate

## Category
Gating & Approval Workflows

## Overview

Estimates the token or compute cost of an operation before executing it. A `PreToolUse` hook reads the planned tool call, calculates estimated cost, and blocks if the estimate exceeds a configured budget ceiling. Prevents runaway costs from unchecked agentic loops.

## Architecture Diagram

```
Agent plans tool call
        │
        ▼
┌──────────────────────┐
│  PreToolUse Hook      │
│  - Reads tool input   │
│  - Estimates cost     │
│  - Checks budget file │
│                       │
│  Under budget? → ✅   │
│  Over budget?  → ❌   │
│    (exit 2 = block)   │
└──────────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/cost-aware-task/SKILL.md`

```yaml
---
name: cost-aware-task
description: >
  Executes a task with cost awareness. Tracks estimated token spend and
  halts if the budget ceiling is approached. Use for expensive operations
  like large-scale refactoring or multi-file generation.
argument-hint: "[task description] [budget-limit-in-tokens]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash
---

Execute the following task with cost tracking: $ARGUMENTS

Before starting:
1. Read the budget from `.claude/budget.json` (or create with default 100000 tokens)
2. Estimate the scope of work and warn if it may exceed budget

During execution:
- The PreToolUse hook will automatically block operations if cumulative
  estimated cost exceeds the budget ceiling
- If blocked, present a summary of work completed and remaining work to the user
- Ask the user whether to increase the budget or stop

After completion:
- Report estimated total token spend
- Update `.claude/budget.json` with remaining budget
```

### Hook — `.claude/hooks/cost-gate.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: estimates cost of tool call and blocks if over budget

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""')

BUDGET_FILE=".claude/budget.json"
SPEND_LOG=".claude/spend.log"

# Initialize budget file if missing
if [[ ! -f "$BUDGET_FILE" ]]; then
  echo '{"budget_tokens": 100000, "spent_tokens": 0}' > "$BUDGET_FILE"
fi

budget=$(jq -r '.budget_tokens' "$BUDGET_FILE")
spent=$(jq -r '.spent_tokens' "$BUDGET_FILE")

# Estimate cost by tool type
case "$tool_name" in
  "Write"|"Edit"|"MultiEdit")
    # Estimate based on content size
    content_length=$(echo "$input" | jq -r '.tool_input | tostring | length')
    estimated_cost=$((content_length / 4))  # ~4 chars per token
    ;;
  "Bash")
    estimated_cost=50  # Fixed estimate for bash calls
    ;;
  "Read")
    estimated_cost=20
    ;;
  *)
    estimated_cost=30
    ;;
esac

new_total=$((spent + estimated_cost))

if [[ "$new_total" -gt "$budget" ]]; then
  remaining=$((budget - spent))
  echo "{\"decision\": \"block\", \"reason\": \"Cost gate: estimated spend ($new_total tokens) exceeds budget ($budget tokens). Remaining: $remaining tokens.\"}" >&2
  exit 2
fi

# Update spend tracker
jq --argjson spent "$new_total" '.spent_tokens = $spent' "$BUDGET_FILE" > "${BUDGET_FILE}.tmp" \
  && mv "${BUDGET_FILE}.tmp" "$BUDGET_FILE"

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$timestamp | $tool_name | est:$estimated_cost | total:$new_total/$budget" >> "$SPEND_LOG"

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/cost-gate.sh"
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
| Agent resets budget file to bypass gate | Budget file should be read-only or managed outside the agent's write scope |
| Inaccurate cost estimation | Conservative estimates; tune multipliers based on observed usage |
| Hook slows down interactive sessions | Keep estimation logic fast (< 100ms); simple arithmetic only |
| Spend log grows unbounded | Rotate or truncate via a Stop hook |

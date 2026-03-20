# Pattern 05: Staged Rollout Gate

## Category
Gating & Approval Workflows

## Overview

Promotes a build through environments sequentially (dev → smoke test → staging → prod). Each promotion step is a sub-agent; each gate is a hook that checks test or health-check results before allowing the next invocation. No environment is touched until the previous one passes automated verification.

## Architecture Diagram

```
User invokes /staged-rollout
        │
        ▼
┌───────────────┐   PreToolUse Hook    ┌───────────────┐   PreToolUse Hook
│ Deploy: Dev   │──(smoke tests pass?)─▶│ Deploy: Stage │──(integration pass?)─▶ ...
│ (sub-agent)   │   ✅ → continue       │ (sub-agent)   │   ✅ → continue
└───────────────┘   ❌ → block          └───────────────┘   ❌ → block
                                                                    │
                                                           ┌───────────────┐
                                                           │ Deploy: Prod  │
                                                           │ (sub-agent)   │
                                                           └───────────────┘
                                                                    │
                                                              Stop Hook
                                                           (notify team)
```

## Complete File Implementations

### Skill — `.claude/skills/staged-rollout/SKILL.md`

```yaml
---
name: staged-rollout
description: >
  Promotes a build through dev → staging → production with automated gates
  between each environment. Each stage runs smoke/integration tests before
  promotion. Use for deployments or release workflows.
argument-hint: "[version or branch]"
allowed-tools: Read, Bash
---

Execute staged rollout for: $ARGUMENTS

## Stage 1: Deploy to Dev
1. Invoke the `env-deployer` sub-agent targeting `dev` environment
2. Run smoke tests: `pnpm test:smoke --env=dev`
3. If smoke tests fail → STOP. Report failure. Do not promote.

## Stage 2: Deploy to Staging
4. Invoke `env-deployer` sub-agent targeting `staging`
5. Run integration tests: `pnpm test:integration --env=staging`
6. If integration tests fail → STOP. Roll back staging. Report failure.

## Stage 3: Approval Gate
7. Present deployment summary to user:
   - Dev smoke test results
   - Staging integration test results
   - Diff of what will go to production
8. Wait for explicit "approve" before proceeding.

## Stage 4: Deploy to Production
9. Invoke `env-deployer` sub-agent targeting `production`
10. Run health checks: `pnpm test:health --env=production`
11. If health checks fail → trigger rollback immediately
12. Report final status
```

### Sub-agent — `.claude/agents/env-deployer.md`

```yaml
---
name: env-deployer
description: >
  Deploys the current build to a specified environment. Runs environment-specific
  health checks after deployment. Use as a stage in staged rollout pipelines.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 10
---

Deploy to the specified environment. Execute the deployment command and verify
the environment is healthy afterward.

1. Read the deployment config for the target environment
2. Execute the deployment command
3. Wait for the deployment to stabilize
4. Run health checks for that environment
5. Write result to `.claude/rollout/<env>-result.json`:
   ```json
   { "environment": "<env>", "status": "success|failure", "health_check": "pass|fail", "timestamp": "..." }
   ```
```

### Hook — `.claude/hooks/rollout-gate.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: blocks deployment to next env unless previous env passed

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Detect which environment is being targeted
if echo "$command" | grep -q "staging"; then
  # Must have dev success
  if [[ ! -f ".claude/rollout/dev-result.json" ]]; then
    echo '{"decision": "block", "reason": "Cannot deploy to staging: dev deployment result not found."}' >&2
    exit 2
  fi
  dev_status=$(jq -r '.status' .claude/rollout/dev-result.json)
  if [[ "$dev_status" != "success" ]]; then
    echo '{"decision": "block", "reason": "Cannot deploy to staging: dev deployment failed."}' >&2
    exit 2
  fi
fi

if echo "$command" | grep -q "production"; then
  if [[ ! -f ".claude/rollout/staging-result.json" ]]; then
    echo '{"decision": "block", "reason": "Cannot deploy to production: staging result not found."}' >&2
    exit 2
  fi
  staging_status=$(jq -r '.status' .claude/rollout/staging-result.json)
  if [[ "$staging_status" != "success" ]]; then
    echo '{"decision": "block", "reason": "Cannot deploy to production: staging failed."}' >&2
    exit 2
  fi
  # Also require approval sentinel
  if [[ ! -f ".claude/rollout/production-approved" ]]; then
    echo '{"decision": "block", "reason": "Cannot deploy to production: human approval required."}' >&2
    exit 2
  fi
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm test:*)",
      "Bash(cat .claude/rollout/*)",
      "Bash(mkdir -p .claude/rollout)",
      "Bash(touch .claude/rollout/production-approved)"
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
            "command": "bash .claude/hooks/rollout-gate.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/notify-complete.sh"
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
| Skipping environments | Hook requires previous env result file with `"status": "success"` |
| Production deploy without approval | Sentinel file `production-approved` required by hook |
| Failed deployment left in bad state | Skill includes rollback instructions on health check failure |
| Deployer sub-agent modifies source | `disallowedTools: [Write, Edit]` — read and execute only |

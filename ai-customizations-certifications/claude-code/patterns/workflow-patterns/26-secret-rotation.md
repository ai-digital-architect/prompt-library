# Pattern 26: Secret Rotation

## Category
Multi-environment Workflows

## Overview

A sub-agent identifies all locations in code and configuration that reference a given credential. A sequential pipeline then generates a new secret, updates every reference atomically within a transaction, and verifies that the service starts cleanly before the old credential is revoked.

## Architecture Diagram

```
User invokes /rotate-secret
        │
        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Secret Finder     │───▶│ Secret Updater   │───▶│ Health Verifier  │
│ (read-only)       │    │ (write-capable)   │    │ (read-only)      │
│ - Finds all refs  │    │ - Generates new   │    │ - Verifies       │
│ - Maps locations  │    │   credential      │    │   service starts │
└──────────────────┘    │ - Updates all refs │    │ - Confirms auth  │
                        └──────────────────┘    └──────────────────┘
                                                         │
                                                PreToolUse Hook
                                                (blocks revocation
                                                 unless health OK)
```

## Complete File Implementations

### Skill — `.claude/skills/rotate-secret/SKILL.md`

```yaml
---
name: rotate-secret
description: >
  Safely rotates a secret/credential: finds all references, updates them
  atomically, verifies the service works, then revokes the old credential.
  Use for API key rotation, database password changes, or certificate renewal.
argument-hint: "[secret-name: DATABASE_PASSWORD|API_KEY|etc]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash
---

Rotate secret: $ARGUMENTS

## Phase 1: Discovery
Invoke `secret-finder` to locate ALL references to the credential.

## Phase 2: Update
1. Generate a new credential value
2. Update every reference found in Phase 1
3. Update environment files, config files, and secrets managers

## Phase 3: Verify
1. Restart/reload the service
2. Run health checks to verify the new credential works
3. If health checks fail: ROLLBACK to old credential immediately

## Phase 4: Revoke (only after verification passes)
1. Present summary to user for approval
2. After approval: revoke the old credential
3. Confirm revocation successful
```

### Sub-agent — `.claude/agents/secret-finder.md`

```yaml
---
name: secret-finder
description: >
  Finds all locations that reference a specific credential across code,
  config, and infrastructure files. Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 10
---

Find all references to the specified credential.

Search across:
1. Environment files (`.env*`)
2. Configuration files (`config/`, `*.config.*`)
3. Docker/compose files
4. CI/CD pipeline files
5. Source code (direct references, env var reads)
6. Infrastructure-as-code (Terraform, CloudFormation)
7. Secrets manager references

Write to `.claude/secrets/references.json`:
```json
{
  "secret_name": "DATABASE_PASSWORD",
  "references": [
    { "file": ".env.production", "line": 5, "type": "env_file" },
    { "file": "docker-compose.yml", "line": 12, "type": "compose" },
    { "file": "terraform/rds.tf", "line": 34, "type": "infrastructure" }
  ],
  "total_references": 3
}
```
```

### Hook — `.claude/hooks/require-health-before-revoke.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: blocks old credential revocation unless health check passed

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only gate on revocation commands
if ! echo "$command" | grep -qE "revoke|delete.*key|remove.*secret"; then
  exit 0
fi

health_file=".claude/secrets/health-check.json"
if [[ ! -f "$health_file" ]]; then
  echo '{"decision": "block", "reason": "Health check not completed. Verify service works with new credential before revoking old one."}' >&2
  exit 2
fi

status=$(jq -r '.status' "$health_file")
if [[ "$status" != "healthy" ]]; then
  echo '{"decision": "block", "reason": "Service health check failed. Do not revoke old credential — rollback instead."}' >&2
  exit 2
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(grep -rn *)",
      "Bash(find *)",
      "Bash(cat *)",
      "Bash(mkdir -p .claude/secrets)"
    ],
    "deny": [
      "Bash(curl * | bash)",
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
            "command": "bash .claude/hooks/require-health-before-revoke.sh"
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
| Old credential revoked before new one verified | Hook blocks revocation until health check passes |
| New credential logged in plaintext | Use secrets manager APIs; never write credentials to tracked files |
| Incomplete reference discovery | Secret-finder scans all file types; includes infrastructure code |
| Service downtime during rotation | Update-then-verify approach; instant rollback if health fails |

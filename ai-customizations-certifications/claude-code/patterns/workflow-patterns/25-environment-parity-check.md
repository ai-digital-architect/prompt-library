# Pattern 25: Environment Parity Check

## Category
Multi-environment Workflows

## Overview

A sub-agent reads configuration files for dev, staging, and production environments and diffs them against a canonical baseline stored in `CLAUDE.md`. A hook flags any undocumented divergence and blocks promotion until the divergence is either resolved or explicitly acknowledged.

## Complete File Implementations

### Project Memory — `CLAUDE.md` (relevant section)

```markdown
## Environment Baseline
All environments must have these configuration keys:
- DATABASE_URL, REDIS_URL, API_BASE_URL
- AUTH_SECRET (different values per env, but key must exist)
- LOG_LEVEL: dev=debug, staging=info, production=warn
- RATE_LIMIT_RPM: dev=1000, staging=500, production=100
- FEATURE_FLAGS: must be identical across staging and production
```

### Skill — `.claude/skills/env-parity/SKILL.md`

```yaml
---
name: env-parity
description: >
  Compares environment configurations against the canonical baseline and
  identifies undocumented divergences. Use before promotions or during
  environment audits.
argument-hint: "[envs: dev,staging,production]"
allowed-tools: Read, Bash
---

Check environment parity: $ARGUMENTS

1. Invoke the `env-parity-checker` sub-agent
2. If divergences found:
   - Present each divergence with env, key, expected value, actual value
   - Block promotion until divergences are resolved or acknowledged
3. If no divergences: confirm parity and allow promotion
```

### Sub-agent — `.claude/agents/env-parity-checker.md`

```yaml
---
name: env-parity-checker
description: >
  Compares environment configs against the baseline defined in CLAUDE.md.
  Read-only.
model: claude-sonnet-4-6
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 10
---

Compare environment configurations against the baseline.

1. Read the baseline from CLAUDE.md (Environment Baseline section)
2. Read config files for each environment (`.env.dev`, `.env.staging`, `.env.production`
   or equivalent config directories)
3. For each environment, check:
   - All required keys present
   - Values match expected patterns
   - No unexpected keys (that might indicate config drift)
4. Special check: staging and production feature flags must be identical

Write to `.claude/env/parity-report.json`:
```json
{
  "environments_checked": ["dev", "staging", "production"],
  "divergences": [
    {
      "environment": "production",
      "key": "RATE_LIMIT_RPM",
      "expected": "100",
      "actual": "50",
      "severity": "medium"
    }
  ],
  "missing_keys": [],
  "unexpected_keys": [],
  "parity_status": "fail"
}
```
```

### Hook — `.claude/hooks/block-promotion-on-drift.sh`

```bash
#!/usr/bin/env bash
# PreToolUse hook: blocks deployment if env parity check failed

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

if ! echo "$command" | grep -qE "deploy|promote|release"; then
  exit 0
fi

report=".claude/env/parity-report.json"
if [[ -f "$report" ]]; then
  status=$(jq -r '.parity_status' "$report")
  if [[ "$status" == "fail" ]]; then
    divergences=$(jq -r '.divergences | length' "$report")
    echo "{\"decision\": \"block\", \"reason\": \"Environment parity check failed: $divergences divergence(s). Resolve before promoting.\"}" >&2
    exit 2
  fi
fi

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/block-promotion-on-drift.sh"
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
| Checker reads production secrets | Check config keys and patterns only, not actual secret values |
| Drift allowed through acknowledgment bypass | Hook blocks deployment; acknowledgment requires explicit sentinel file |
| Checker modifies configs | `disallowedTools: [Write, Edit, MultiEdit]` |

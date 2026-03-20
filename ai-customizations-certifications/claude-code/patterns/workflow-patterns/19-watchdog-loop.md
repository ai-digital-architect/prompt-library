# Pattern 19: Watchdog Loop

## Category
Monitoring & Alerting Workflows

## Overview

A skill sets up a polling loop: a sub-agent checks a condition (test health, bundle size, dependency freshness, API latency) on a schedule. A `Stop` hook fires a notification to Slack or a pager when the condition exceeds a threshold.

## Architecture Diagram

```
User invokes /watchdog
        │
        ▼
┌─────────────────────────┐
│  Watchdog Skill           │
│  (polling loop)           │
│                           │
│  while true:              │
│    invoke health-checker  │
│    read result            │
│    if threshold exceeded: │
│      → Stop hook fires    │
│      → Slack notification │
│    sleep interval         │
└─────────────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/watchdog/SKILL.md`

```yaml
---
name: watchdog
description: >
  Runs a polling loop that monitors a condition and alerts when thresholds
  are exceeded. Checks bundle size, test health, dependency freshness, or
  custom metrics. Use for continuous monitoring during development.
argument-hint: "[metric: bundle-size|test-health|deps] [threshold] [interval-seconds]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Start watchdog monitoring: $ARGUMENTS

1. Parse arguments: metric type, threshold value, check interval
2. Loop:
   a. Invoke the `health-checker` sub-agent for the specified metric
   b. Read result from `.claude/watchdog/latest-check.json`
   c. If metric exceeds threshold:
      - Log the violation to `.claude/watchdog/violations.log`
      - Report to user immediately
      - The Stop hook will send external notifications
   d. If within threshold: log "OK" and continue
   e. Wait for the specified interval
3. Continue until the user stops the session
```

### Sub-agent — `.claude/agents/health-checker.md`

```yaml
---
name: health-checker
description: >
  Checks a specific health metric (bundle size, test pass rate, dependency
  freshness) and produces a structured result. Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 5
---

Check the requested health metric and report.

Supported metrics:
- **bundle-size**: Run `pnpm build && du -sh dist/` → report size in KB
- **test-health**: Run `pnpm test --reporter=json` → report pass/fail ratio
- **deps**: Run `pnpm audit --json` → report vulnerability count by severity

Write result to `.claude/watchdog/latest-check.json`:
```json
{
  "metric": "<type>",
  "value": 1234,
  "unit": "KB|percent|count",
  "timestamp": "...",
  "status": "ok|warning|critical"
}
```
```

### Hook — `.claude/hooks/watchdog-notify.sh`

```bash
#!/usr/bin/env bash
# Stop hook: sends notification if watchdog detected violations

violations_log=".claude/watchdog/violations.log"

if [[ ! -f "$violations_log" ]]; then
  exit 0
fi

violation_count=$(wc -l < "$violations_log")
if [[ "$violation_count" -gt 0 ]]; then
  last_violation=$(tail -1 "$violations_log")
  
  # Slack notification (uncomment and configure)
  # curl -s -X POST "$SLACK_WEBHOOK_URL" \
  #   -H 'Content-Type: application/json' \
  #   -d "{\"text\": \"⚠️ Watchdog alert: $violation_count violation(s). Latest: $last_violation\"}"
  
  echo "Watchdog: $violation_count violations detected" >> ~/.claude/notifications.log
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
      "Bash(pnpm audit:*)",
      "Bash(du -sh dist/*)",
      "Bash(sleep *)",
      "Bash(mkdir -p .claude/watchdog)"
    ]
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/watchdog-notify.sh"
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
| Watchdog loop runs indefinitely | User can stop session; `maxTurns` on health-checker limits per-check cost |
| Health-checker modifies code | `disallowedTools: [Write, Edit]` — read and execute only |
| Notification webhook exposed | Webhook URL via `${SLACK_WEBHOOK_URL}` env var, never hardcoded |

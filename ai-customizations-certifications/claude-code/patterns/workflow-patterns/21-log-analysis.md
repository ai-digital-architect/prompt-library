# Pattern 21: Log Analysis

## Category
Monitoring & Alerting Workflows

## Overview

A sub-agent ingests a rolling window of error logs, clusters entries by pattern using Bash tooling, de-duplicates noise, and produces a ranked summary of distinct failure modes with frequency, first-seen, and last-seen timestamps.

## Complete File Implementations

### Skill — `.claude/skills/analyze-logs/SKILL.md`

```yaml
---
name: analyze-logs
description: >
  Analyzes error logs to identify failure patterns, clusters similar errors,
  and ranks by frequency. Use for periodic log review or incident investigation.
argument-hint: "[log-file-path] [time-window: 1h|24h|7d]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Analyze logs: $ARGUMENTS

1. Invoke the `log-analyzer` sub-agent with the log file and time window
2. Present the ranked failure pattern summary
3. Highlight any new patterns not seen before (compare against `.claude/logs/known-patterns.json` if it exists)
```

### Sub-agent — `.claude/agents/log-analyzer.md`

```yaml
---
name: log-analyzer
description: >
  Ingests error logs, clusters by pattern, de-duplicates, and produces a
  ranked summary of distinct failure modes. Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 12
---

Analyze the provided log file.

1. Use `grep`, `awk`, `sort`, `uniq -c` to extract error lines
2. Cluster similar errors by normalizing variable parts (timestamps, IDs, paths)
3. For each distinct pattern, determine:
   - Frequency (count)
   - First occurrence timestamp
   - Last occurrence timestamp
   - Representative example message
4. Rank by frequency (most common first)

Write to `.claude/logs/analysis-report.json`:
```json
{
  "time_window": "24h",
  "total_errors": 1542,
  "distinct_patterns": 8,
  "patterns": [
    {
      "rank": 1,
      "pattern": "Connection refused to database",
      "count": 892,
      "first_seen": "2025-01-01T03:00:00Z",
      "last_seen": "2025-01-01T14:30:00Z",
      "example": "ERROR 2025-01-01T10:15:32 Connection refused to postgres://db:5432",
      "severity": "critical"
    }
  ]
}
```
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(cat *)",
      "Bash(grep *)",
      "Bash(awk *)",
      "Bash(sort *)",
      "Bash(uniq *)",
      "Bash(wc *)",
      "Bash(tail *)",
      "Bash(head *)",
      "Bash(mkdir -p .claude/logs)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Logs contain sensitive data (PII, tokens) | Analyzer normalizes/redacts variable parts; report uses patterns not raw data |
| Analyzer modifies log files | `disallowedTools: [Write, Edit]` — strictly read-only |
| Large log files overwhelm context | Use Bash tools for pre-processing; agent reads summarized output, not raw files |

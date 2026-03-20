# Pattern 28: Postmortem Assistant

## Category
Feedback & Learning Workflows

## Overview

A sub-agent ingests an incident timeline (from logs, alerts, or a Slack export), identifies contributing factors and timeline gaps, and drafts a postmortem document with a root-cause analysis and prioritized action items. A hook formats the output to match the team's postmortem template.

## Complete File Implementations

### Skill — `.claude/skills/postmortem/SKILL.md`

```yaml
---
name: postmortem
description: >
  Drafts a postmortem document from incident data: logs, alerts, timelines,
  and Slack exports. Identifies root cause, contributing factors, and
  produces prioritized action items. Use after any production incident.
argument-hint: "[incident-id or log-file-path]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Draft postmortem: $ARGUMENTS

1. Invoke `postmortem-drafter` with the incident data
2. The Stop hook will format the output to match the team template
3. Present the draft for human review and editing
```

### Sub-agent — `.claude/agents/postmortem-drafter.md`

```yaml
---
name: postmortem-drafter
description: >
  Drafts postmortem documents from incident data. Identifies root cause,
  contributing factors, timeline gaps, and action items. Read-only.
model: claude-opus-4-5
tools: [Read, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 15
---

Draft a postmortem from the provided incident data.

1. Read incident logs, alert history, and any provided timeline
2. Construct a chronological timeline of events
3. Identify gaps in the timeline (periods without logged events)
4. Determine root cause using the "5 Whys" method
5. Identify contributing factors (adjacent causes that amplified impact)
6. Assess detection time, response time, and resolution time
7. Draft action items: preventive (stop recurrence), detective (find faster), mitigative (reduce impact)

Write to `.claude/postmortem/draft.md` following this structure:

## Incident Postmortem: [Title]
- **Date**: [incident date]
- **Duration**: [total duration]
- **Severity**: [S1/S2/S3/S4]
- **Author**: [drafter]

### Summary
[2-3 sentence description]

### Timeline
| Time | Event | Source |
|------|-------|--------|

### Root Cause
[5 Whys analysis]

### Contributing Factors
[Numbered list]

### Impact
- Users affected: [count/percentage]
- Revenue impact: [if applicable]
- Data impact: [if applicable]

### Detection & Response
- Time to detect: [duration]
- Time to respond: [duration]
- Time to resolve: [duration]

### Action Items
| Priority | Action | Owner | Due Date |
|----------|--------|-------|----------|

### Lessons Learned
[What went well, what didn't, where we got lucky]
```

### Hook — `.claude/hooks/format-postmortem.sh`

```bash
#!/usr/bin/env bash
# Stop hook: validates postmortem format matches team template

draft=".claude/postmortem/draft.md"

if [[ ! -f "$draft" ]]; then
  exit 0
fi

# Check required sections exist
required_sections=("Summary" "Timeline" "Root Cause" "Impact" "Action Items")
for section in "${required_sections[@]}"; do
  if ! grep -q "### $section" "$draft"; then
    echo "Warning: Missing section '### $section' in postmortem draft" >> ~/.claude/notifications.log
  fi
done

exit 0
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(cat *)",
      "Bash(grep *)",
      "Bash(git log:*)",
      "Bash(mkdir -p .claude/postmortem)"
    ]
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/format-postmortem.sh"
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
| Postmortem contains sensitive production data | Drafter normalizes PII; draft is for internal review only |
| Drafter modifies incident logs | `disallowedTools: [Write, Edit, MultiEdit]` |
| Inaccurate root cause attribution | Uses `claude-opus-4-5`; draft clearly labeled for human review |

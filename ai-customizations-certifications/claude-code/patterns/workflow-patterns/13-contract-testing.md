# Pattern 13: Contract Testing

## Category
Validation & Verification Workflows

## Overview

A sub-agent generates consumer contracts from the frontend's API usage. A separate sub-agent verifies those contracts against the backend provider. A hook fails the session if drift is detected between what the consumer expects and what the provider delivers.

## Architecture Diagram

```
User invokes /contract-test
        │
        ├────────────────────────┐
        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ Contract Extractor│    │ Contract Verifier │
│ (read-only)       │    │ (read-only)       │
│ - Reads frontend  │    │ - Reads backend   │
│   API usage       │    │   endpoints       │
│ - Generates       │    │ - Compares against│
│   contracts       │    │   contracts       │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
  contracts.json          verification.json
         │                       │
         └───────┬───────────────┘
                 ▼
          SubagentStop Hook
          (checks for drift;
           exit 2 if found)
```

## Complete File Implementations

### Skill — `.claude/skills/contract-test/SKILL.md`

```yaml
---
name: contract-test
description: >
  Generates API consumer contracts from frontend code and verifies them
  against backend implementation. Detects API drift. Use before releases
  or after API changes.
argument-hint: "[api-module or 'all']"
allowed-tools: Read, Bash
---

Run contract testing: $ARGUMENTS

1. Invoke `contract-extractor` to scan frontend API usage and generate contracts
2. Invoke `contract-verifier` to check backend endpoints against contracts
3. If drift detected: report mismatches with file/line references
4. If no drift: confirm all contracts satisfied
```

### Sub-agent — `.claude/agents/contract-extractor.md`

```yaml
---
name: contract-extractor
description: >
  Scans frontend code to extract API consumer contracts (endpoint, method,
  request/response shapes). Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 12
---

Scan frontend code for API calls and extract contracts.

1. Find all API call sites (fetch, axios, custom clients)
2. For each call, extract: endpoint, HTTP method, request body shape, expected response shape
3. Write to `.claude/contracts/consumer-contracts.json`:
   ```json
   {
     "contracts": [
       {
         "endpoint": "/api/users",
         "method": "GET",
         "request_params": {},
         "expected_response": { "type": "array", "items": { "id": "number", "name": "string" } },
         "source_file": "src/api/users.ts",
         "source_line": 15
       }
     ]
   }
   ```
```

### Sub-agent — `.claude/agents/contract-verifier.md`

```yaml
---
name: contract-verifier
description: >
  Verifies backend endpoints against consumer contracts. Reports drift.
  Read-only.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 12
---

Read `.claude/contracts/consumer-contracts.json` and verify each contract
against the backend implementation.

For each contract:
1. Find the corresponding route handler
2. Verify the endpoint path and HTTP method match
3. Verify request validation matches expected params
4. Verify response shape matches expected response

Write to `.claude/contracts/verification.json`:
```json
{
  "passed": 8,
  "failed": 2,
  "drift": [
    {
      "endpoint": "/api/users",
      "issue": "Response missing 'email' field",
      "consumer_expects": { "email": "string" },
      "provider_delivers": {},
      "consumer_file": "src/api/users.ts:15",
      "provider_file": "backend/routes/users.ts:42"
    }
  ]
}
```
```

### Hook — `.claude/hooks/contract-drift-check.sh`

```bash
#!/usr/bin/env bash
# SubagentStop hook: fails if contract drift detected

input=$(cat)
agent_name=$(echo "$input" | jq -r '.agent_name // ""')

if [[ "$agent_name" != "contract-verifier" ]]; then
  exit 0
fi

verification=".claude/contracts/verification.json"
if [[ ! -f "$verification" ]]; then
  exit 0
fi

failed=$(jq -r '.failed // 0' "$verification")
if [[ "$failed" -gt 0 ]]; then
  echo "{\"reason\": \"Contract drift detected: $failed endpoint(s) have mismatches. See verification.json.\"}" >&2
  exit 2
fi

exit 0
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
            "command": "bash .claude/hooks/contract-drift-check.sh"
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
| Agents modify code during verification | Both agents have `disallowedTools: [Write, Edit]` |
| Incomplete contract extraction | Extractor scans all API call patterns; configurable per framework |
| False positives from dynamic APIs | Verification report includes source references for human review |

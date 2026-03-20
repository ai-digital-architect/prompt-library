# Pattern 5.1 — Contract Testing

> A sub-agent generates consumer contracts from frontend API usage. A separate sub-agent verifies those contracts against the backend provider.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Contract generator sub-agent | Sub-agent with read-only tools scans frontend |
| Contract verifier sub-agent | Sub-agent with read-only tools checks backend |
| Hook fails session on drift | Parent agent evaluates drift report and stops on failure |

## Implementation Fidelity: ✅ High

---

## Agent Definitions

### `.github/agents/contract-tester.agent.md`

```yaml
---
name: Contract Tester
description: >
  Test API contracts between frontend consumers and backend providers.
  Detects drift without modifying code.
tools: ['agent', 'search', 'codebase']
agents: ['Contract Extractor', 'Contract Verifier']
---

1. Invoke Contract Extractor to scan frontend code and extract API expectations
2. Invoke Contract Verifier to check each expectation against the backend
3. If drift is detected, report mismatches with severity and affected endpoints
4. If no drift, confirm contract alignment
```

### `.github/agents/contract-extractor.agent.md`

```yaml
---
name: Contract Extractor
description: Extract API consumer contracts from frontend code. Read-only.
tools: ['codebase', 'search', 'usages']
---

Scan all frontend API call sites and extract the implicit contract:
- Endpoint URL and HTTP method
- Request body shape (fields, types, required/optional)
- Expected response shape (fields, types)
- Query parameters used
- Headers expected

Output as a structured contract list.
```

### `.github/agents/contract-verifier.agent.md`

```yaml
---
name: Contract Verifier
description: Verify consumer contracts against backend implementation. Read-only.
tools: ['codebase', 'search']
---

Given a list of consumer contracts, check each against the backend:

For each contract:
- Does the endpoint exist? (PASS/FAIL)
- Does the request validation accept the expected shape? (PASS/FAIL)
- Does the response match the expected shape? (PASS/FAIL)
- Are there fields the frontend expects but the backend doesn't return? (DRIFT)
- Are there fields the backend returns but the frontend doesn't use? (SAFE DRIFT)

Rate each mismatch: BREAKING (frontend will crash), WARNING (degraded UX), or INFO.
```

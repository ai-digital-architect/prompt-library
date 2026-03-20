# Pattern 23: Compliance Audit

## Category
Review & Audit Workflows

## Overview

A read-only sub-agent scans the codebase against a defined ruleset (OWASP Top 10, GDPR data-handling requirements, OSS license policy). Findings are severity-ranked and mapped to file locations. The sub-agent has `disallowedTools: [Write, Edit]` to guarantee it cannot accidentally modify the code it is auditing.

## Complete File Implementations

### Skill — `.claude/skills/compliance-audit/SKILL.md`

```yaml
---
name: compliance-audit
description: >
  Scans the codebase against compliance rulesets: OWASP Top 10, GDPR,
  license policy, or custom rules. Produces a severity-ranked findings
  report. Use before releases or during periodic security reviews.
argument-hint: "[ruleset: owasp|gdpr|license|all]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Run compliance audit: $ARGUMENTS

1. Invoke the `compliance-auditor` sub-agent with the specified ruleset
2. Present findings grouped by severity (Critical → Low)
3. Include file/line references for each finding
4. Provide remediation guidance for Critical and High findings
```

### Sub-agent — `.claude/agents/compliance-auditor.md`

```yaml
---
name: compliance-auditor
description: >
  Scans the codebase against compliance rulesets and produces severity-ranked
  findings. Strictly read-only — cannot modify code being audited.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 20
---

Audit the codebase against the specified ruleset.

## OWASP Top 10 Checks
- A01: Broken Access Control — check auth middleware coverage
- A02: Cryptographic Failures — check encryption usage, key management
- A03: Injection — check input sanitization, parameterized queries
- A04: Insecure Design — check security architecture patterns
- A05: Security Misconfiguration — check default configs, error handling
- A06: Vulnerable Components — check dependency versions
- A07: Auth Failures — check password handling, session management
- A08: Data Integrity Failures — check deserialization, CI/CD pipeline
- A09: Logging Failures — check audit trail completeness
- A10: SSRF — check URL validation, outbound request controls

## GDPR Checks
- Data inventory: where is PII stored?
- Consent management: is consent captured before processing?
- Right to erasure: can user data be deleted?
- Data minimization: is only necessary data collected?
- Encryption at rest and in transit

## License Checks
- Scan all dependency licenses against approved list
- Flag GPL/AGPL in production dependencies
- Identify missing license declarations

Write report to `.claude/audit/compliance-report.md` with:
- Finding ID, severity, category, file:line, description, remediation
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(grep -rn *)",
      "Bash(find *)",
      "Bash(cat *)",
      "Bash(pnpm audit:*)",
      "Bash(git log:*)",
      "Bash(mkdir -p .claude/audit)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Auditor modifies code during scan | `disallowedTools: [Write, Edit, MultiEdit]` enforced |
| Audit misses edge cases | Uses `claude-opus-4-5` for thoroughness; combine with automated SAST tools |
| False sense of compliance | Report clearly states it's an AI-assisted review, not a certified audit |

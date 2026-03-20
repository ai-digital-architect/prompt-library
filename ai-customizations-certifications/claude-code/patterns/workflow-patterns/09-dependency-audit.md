# Pattern 09: Dependency Audit

## Category
Research & Discovery Workflows

## Overview

A read-only sub-agent scans all dependency manifests (package.json, requirements.txt, go.mod, etc.), cross-references version data against known CVE feeds or a license policy, and produces a risk-ranked report without touching any implementation files.

## Architecture Diagram

```
User invokes /dependency-audit
        │
        ▼
┌───────────────────────────┐
│  Dependency Auditor        │
│  (READ-ONLY sub-agent)     │
│  - Reads all manifests     │
│  - Runs `npm audit` etc.   │
│  - Cross-refs CVE data     │
│  - Checks license policy   │
│  - Writes risk report      │
│                            │
│  Tools: Read, Bash         │
│  disallowed: Write, Edit   │
└───────────────────────────┘
        │
        ▼
  .claude/audit/dependency-report.md
```

## Complete File Implementations

### Skill — `.claude/skills/dependency-audit/SKILL.md`

```yaml
---
name: dependency-audit
description: >
  Scans all dependency manifests for security vulnerabilities, outdated
  packages, and license compliance issues. Produces a risk-ranked report.
  Use before releases, during security reviews, or on a regular schedule.
argument-hint: "[scope: all|frontend|backend]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Run dependency audit for: $ARGUMENTS

Invoke the `dependency-auditor` sub-agent to:

1. Scan all dependency manifests in the project
2. Run native audit tools (`npm audit`, `pip audit`, `go vuln check`)
3. Check each dependency's license against the approved license list in CLAUDE.md
4. Produce a risk-ranked report at `.claude/audit/dependency-report.md`

The report must include:
- **Critical/High CVEs** — package, version, CVE ID, severity, fix version
- **License violations** — packages using non-approved licenses
- **Outdated packages** — major version behind, with upgrade risk assessment
- **Recommended actions** — prioritized by risk
```

### Sub-agent — `.claude/agents/dependency-auditor.md`

```yaml
---
name: dependency-auditor
description: >
  Scans dependency manifests for vulnerabilities, license issues, and
  outdated packages. Read-only — never modifies project files.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 15
---

You are a dependency security specialist. Audit all project dependencies.

1. Find all manifest files: `package.json`, `pnpm-lock.yaml`, `requirements.txt`,
   `go.mod`, `Cargo.toml`, etc.
2. Run native audit commands:
   - Node: `pnpm audit --json` or `npm audit --json`
   - Python: `pip audit --format=json` (if available)
   - Go: `go vuln check ./...`
3. Parse results and cross-reference severity
4. Check licenses: read each dependency's license field; flag any not in the
   approved list (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC)
5. Identify packages >1 major version behind latest

Write report to `.claude/audit/dependency-report.md` with sections:
- Critical Vulnerabilities (table: package, version, CVE, severity, fix)
- License Violations (table: package, license, status)
- Outdated Dependencies (table: package, current, latest, risk)
- Summary Statistics
- Recommended Actions (prioritized list)
```

### Project Memory — `CLAUDE.md` (relevant section)

```markdown
## Approved Dependency Licenses
- MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Unlicense
- GPL and AGPL are NOT approved for production dependencies
- LGPL is approved for dynamically-linked dependencies only
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm audit:*)",
      "Bash(npm audit:*)",
      "Bash(pip audit:*)",
      "Bash(cat package.json)",
      "Bash(find * -name package.json)",
      "Bash(jq * package.json)",
      "Bash(mkdir -p .claude/audit)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Auditor modifies dependency files | `disallowedTools: [Write, Edit, MultiEdit]` — strictly read-only |
| Audit commands execute arbitrary code | Scoped `allow` list in permissions; only audit-specific commands |
| False sense of security from incomplete scan | Skill instructions enumerate all manifest types; auditor checks multiple ecosystems |

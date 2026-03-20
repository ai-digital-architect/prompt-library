# Pattern 9.1 — Environment Parity Check

> A sub-agent reads configuration files for dev, staging, and production and diffs them against a canonical baseline. A hook flags undocumented divergence.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Sub-agent reads config files | Sub-agent with `tools: ['codebase', 'search', 'terminalLastCommand']` |
| Canonical baseline in `CLAUDE.md` | Skill reference file with the baseline |
| Hook flags divergence | Parent agent evaluates and flags |

## Implementation Fidelity: ✅ High

---

## Agent Definition

### `.github/agents/env-parity-checker.agent.md`

```yaml
---
name: Environment Parity Checker
description: >
  Compare configuration across dev, staging, and production environments.
  Identify undocumented divergences from the canonical baseline.
tools: ['codebase', 'search', 'terminalLastCommand']
---

Compare environment configurations against the canonical baseline.

## Procedure

1. Read all environment config files:
   - `.env.development`, `.env.staging`, `.env.production`
   - `config/dev.yaml`, `config/staging.yaml`, `config/prod.yaml`
   - Docker compose files, Kubernetes manifests, Terraform variables
2. Load the canonical baseline from the env-baseline skill
3. For each environment, diff against baseline:
   - Variables present in baseline but missing in env → MISSING
   - Variables present in env but not in baseline → UNDOCUMENTED
   - Variables with different values than baseline → DIVERGED
4. Classify each divergence:
   - **Expected**: documented in baseline as environment-specific
   - **Risky**: security-sensitive values differ unexpectedly
   - **Unauthorized**: present in one env but not tracked anywhere

## Output Format

| Variable | Dev | Staging | Prod | Baseline | Status |
|---|---|---|---|---|---|
| DB_HOST | localhost | staging-db | prod-db | env-specific | Expected |
| LOG_LEVEL | debug | info | warn | info | Diverged (dev) |
| SECRET_KEY | set | set | MISSING | required | CRITICAL |
```

## Supporting Skill

### `.github/skills/env-baseline/SKILL.md`

```yaml
---
name: env-baseline
description: >
  Canonical environment configuration baseline. Use when checking
  environment parity or validating configuration completeness.
---

## Required Variables (all environments)
- `DB_HOST` — database hostname (env-specific value expected)
- `DB_PORT` — database port (default: 5432)
- `SECRET_KEY` — application secret (MUST be set, MUST differ per env)
- `LOG_LEVEL` — logging level (dev=debug, staging=info, prod=warn)
- `API_URL` — backend API URL (env-specific)

## Environment-Specific Expectations
Variables marked "env-specific" are expected to differ between environments.
All other variables should be identical. Any unlisted variable in an
environment config is flagged as UNDOCUMENTED.
```

# General-Purpose Prompt Template — OpenAI GPT-5.2 Codex

> **Status (June 2026):** GPT-5.2-Codex is no longer listed in OpenAI's current
> model documentation. OpenAI's deprecation page schedules `gpt-5.2-codex` for
> retirement on July 23, 2026, with `gpt-5.5` as the recommended replacement.
> For new agentic coding work, prefer [GPT-5.5](./15-openai-gpt-5-5.md).

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | GPT-5.2-Codex |
| **Provider** | OpenAI |
| **Tier** | Specialized agentic coding — optimized for long-horizon software engineering |
| **Context Window** | 400K tokens |
| **Max Output** | 128K tokens |
| **Strengths** | Agentic coding, large refactors and migrations, long-horizon task completion, context compaction, Windows environment support, cybersecurity analysis |
| **Best For** | Multi-file codebase changes, code migrations, long-running autonomous coding sessions, security vulnerability research, complex debugging across large repositories |
| **Key Differentiator** | Context compaction for sustained long-session work. State-of-the-art on SWE-Bench Pro (56.4%) and Terminal-Bench 2.0 (64.0%). Enhanced cybersecurity capabilities. |

---

## Template Structure

GPT-5.2-Codex is purpose-built for agentic coding in the Codex environment. It excels at multi-step software engineering tasks that span hours or days. Prompts should define the end goal clearly, provide repository context, and specify constraints. The model handles exploration, planning, and iterative execution autonomously.

```
Task: {{Clear statement of the software engineering goal}}

Repository context:
- {{Language, framework, key dependencies}}
- {{Architecture overview (monorepo? microservices? monolith?)}}
- {{Relevant directory structure or entry points}}

Constraints:
- {{Coding standards to follow}}
- {{Files or modules that should NOT be modified}}
- {{Testing requirements}}
- {{Performance or compatibility requirements}}

Success criteria:
- {{How to verify the task is complete}}
- {{Tests that must pass}}
- {{Behavior that must be preserved}}

Approach preference:
- {{Incremental commits vs. single large change}}
- {{Whether to write tests first (TDD) or after}}
- {{Whether to ask for confirmation at checkpoints}}
```

### Key Prompting Principles for GPT-5.2 Codex

1. **Define the end state, not the steps** — Codex models are agentic. Tell it *what* needs to be true when it's done, not *how* to get there step by step.
2. **Provide repository context** — Include or reference the project structure, key configuration files, and architectural patterns. Codex uses this to make consistent changes.
3. **Set clear boundaries** — Specify what should NOT be changed. Codex may refactor aggressively if not constrained.
4. **Enable iterative work** — For large tasks, allow Codex to work in phases. It can run tests, observe failures, and iterate — let it.
5. **Leverage context compaction** — Codex-5.2 compresses context during long sessions. It can work for extended periods without losing track of the project state.
6. **Security research** — GPT-5.2-Codex has enhanced cybersecurity capabilities for defensive security work (vulnerability analysis, code auditing).

---

## Example 1 — Coding Activity

```
Task: Migrate our authentication system from session-based (express-session + Redis)
to JWT-based authentication with refresh token rotation.

Repository context:
- Node.js 20 + Express 5 + TypeScript
- PostgreSQL database via Prisma ORM
- 45 API endpoints, all currently using session middleware
- Frontend: React 19, currently sends cookies automatically

Constraints:
- Zero downtime migration — both auth methods must work during transition period.
- All existing user sessions must remain valid until their natural expiry.
- Do not modify the user database schema beyond adding refresh token storage.
- Maintain backward compatibility with the mobile app (v3.x) which expects
  cookie-based auth for the next 90 days.
- Follow OWASP JWT security best practices.

Success criteria:
- All 127 existing tests continue to pass.
- New tests cover: token issuance, refresh rotation, token revocation,
  concurrent refresh handling, expired token rejection.
- Authentication middleware supports both cookie-session and Bearer token
  simultaneously (feature flag controlled).
- Refresh token rotation detects reuse and invalidates the entire token family.
- Performance: auth check adds <5ms latency vs. current session lookup.

Approach:
- Work incrementally. Commit after each logical unit of work.
- Write tests first for the new JWT auth flow, then implement.
- Create a migration guide document (MIGRATION.md) for the team.
```

---

## Example 2 — Deep Analysis and Research (Technology Architecture)

```
Task: Audit our microservices architecture for security vulnerabilities and
produce a comprehensive security assessment with remediation plan.

Repository context:
- 22 Go microservices in a monorepo
- Kubernetes deployment on AWS EKS
- Service mesh: Istio
- API gateway: Kong
- Inter-service communication: gRPC with mTLS
- Secrets management: HashiCorp Vault
- CI/CD: GitHub Actions → ArgoCD

Scope:
1. **Authentication and authorization audit**
   - Review all service-to-service authentication flows.
   - Check for broken access control patterns.
   - Verify JWT validation is consistent across all services.
   - Identify any endpoints that bypass auth middleware.

2. **Dependency vulnerability scan**
   - Analyze go.mod files across all services for known CVEs.
   - Assess transitive dependency risks.
   - Prioritize by exploitability (not just CVSS score).

3. **Infrastructure security review**
   - Review Kubernetes RBAC policies for least-privilege compliance.
   - Check network policies — are services properly segmented?
   - Review Istio configuration for mTLS enforcement gaps.
   - Assess secrets rotation practices.

4. **Code-level security patterns**
   - SQL injection vectors (even with ORMs — check raw queries).
   - SSRF risks in services that make outbound HTTP calls.
   - Input validation completeness.
   - Error handling that may leak sensitive information.

Deliverables:
- SECURITY_AUDIT.md — findings organized by severity (Critical, High, Medium, Low).
- For each finding: description, affected code/config, proof of concept,
  recommended fix with code example, effort estimate.
- REMEDIATION_PLAN.md — prioritized remediation roadmap (sprint-level).
- Create GitHub issues (as a markdown list) for each Critical and High finding.

Success criteria:
- No Critical findings remain unaddressed in the remediation plan.
- All findings include reproducible evidence.
- Remediation suggestions are specific enough that a mid-level engineer
  can implement them without further guidance.
```

---

## Example 3 — Executive Communication / Presentation

```
Task: Generate a technical blog post and accompanying presentation for our
engineering blog announcing our migration from a monolith to microservices.

Context:
- 18-month migration of a 500K LOC Python Django monolith to 22 Go microservices.
- Team: 35 engineers.
- Results: deployment frequency from weekly to 15x/day, MTTR from 4hrs to 18min,
  P99 latency from 1.2s to 180ms, infrastructure cost reduced 34%.
- Challenges faced: data migration without downtime, team reskilling from Python
  to Go, managing the "distributed monolith" anti-pattern during transition.

Blog post requirements:
- 2,500-3,000 words targeting senior engineering audience.
- Include architecture diagrams (describe as Mermaid code blocks).
- Honest about what went wrong and lessons learned.
- Include specific metrics with before/after comparisons.
- Code examples showing key patterns (service decomposition, event sourcing,
  saga pattern implementation).
- SEO-optimized title and meta description.

Presentation requirements:
- 15-slide narrative for a conference talk (30-minute slot).
- Each slide: title, key point, speaker notes.
- Include 3 "war story" slides — specific incidents during migration and how
  the team recovered.
- End with actionable takeaways the audience can apply to their own migrations.

Deliver both the blog post (as markdown) and the presentation narrative.
```

---

## When to Choose GPT-5.2 Codex

| Scenario | Use 5.2 Codex? |
|---|---|
| Large codebase refactor or migration | ✅ Context compaction + long-horizon |
| Multi-file code changes across a monorepo | ✅ Designed for this |
| Security vulnerability audit of a codebase | ✅ Enhanced cybersecurity capabilities |
| Quick single-file code generation | ❌ Use GPT-5.1 or GPT-5.2 |
| Non-coding professional knowledge work | ❌ Use GPT-5.2 (general) |
| Agentic coding requiring 24+ hour sessions | ⚠️ Consider GPT-5.3 Codex for newer capabilities |
| Windows development environment work | ✅ Improved Windows support |

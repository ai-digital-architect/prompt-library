# Factory Implementation — Handoff & Step-by-Step Guide (v2, merged)

Drives **Claude Code** through `design-and-implementation-plan-v2.md` from empty repo to a working,
governed factory. **You** are the operator (set up, verify gates, approve, commit); **Claude Code**
is the implementer.

> This v2 guide matches the **merged 11-phase plan (P0–P10)** and the structure: `coding-harness/`
> (generic Layer 1), `factory-core/` (Python engine), `domains/harness/` (all Harness specifics),
> `dist/` (generated). The **dual CLI exposure** (bash + MCP adapter) is built in Phase 5.

---

## 1. Prerequisites

| Tool | Why | Check |
|---|---|---|
| Claude Code | implementer | `claude --version` |
| git | VCS / worktrees | `git --version` |
| Python 3.12+ + uv | engine (`factory_core`) | `python --version` |
| make | operator surface | `make --version` |
| jq | hook/CLI JSON | `jq --version` |
| harness-cli | CLI substrate (P5+) | `harness-cli --help` |
| harness-cli **sandbox** profile | dry-run evals never hit prod | `HARNESS_CLI_PROFILE=sandbox` configured |
| official skill-creator skill | certification backbone (P1/P4) | staged in `docs/reference/skill-creator/` |

---

## 2. Bootstrap the handoff directory (by hand)

Create only the **orientation layer**; Claude Code builds the rest from Phase 0.

```
skill-plugin-factory/            ← open Claude Code here
├── CLAUDE.md                    ← provided
├── AGENTS.md                    ← provided
└── docs/
    ├── design-and-implementation-plan.md          ← the v2 plan, placed under this name
    └── reference/
        ├── claude-code-customization-architecture-revised.md
        ├── ghcopilot-customization-arch.md
        ├── harness-skill-factory.original.md         ← superseded original, for context
        └── skill-creator/                            ← OFFICIAL Anthropic skill-creator skill (operator-provided)
```

```bash
mkdir -p skill-plugin-factory/docs/reference && cd skill-plugin-factory && git init
# copy CLAUDE.md, AGENTS.md to root; design-and-implementation-plan-v2.md → docs/design-and-implementation-plan.md
# copy the two arch docs + the renamed original into docs/reference/
git add . && git commit -m "chore: bootstrap factory handoff (v2 plan + governing docs + orientation)"
```

Do **not** pre-create `coding-harness/`, `factory-core/`, `domains/`, or `dist/` — those are
Phase 0+ deliverables; letting Claude Code own them preserves compiler discipline. The one input
you **do** provide is the official **skill-creator** skill, staged under
`docs/reference/skill-creator/`; Phase 1 installs and pins it into the harness.

---

## 3. Handoff contract (paste once, first)

```
Read CLAUDE.md, AGENTS.md, docs/design-and-implementation-plan.md, and skim docs/reference/.
Write nothing yet. Then confirm in your own words: (1) the three layers + factory-core engine;
(2) why dist/ is generated and hash-manifested; (3) that coding-harness/.claude/ is domain-free;
(4) the fail-closed gates — conformance, eval, AND security — plus skill-creator certification;
(5) the dual CLI exposure (bash default + MCP adapter); (6) the P0–P10 order and dependency map.
We implement ONE phase at a time: start in plan mode, implement only that phase's sub-tasks,
self-check against its acceptance table, then stop for my verification. Acknowledge and wait.
```

---

## 4. Phase-by-phase execution

For each phase: paste the prompt, let Claude Code plan→implement, run the checklist (the plan's
acceptance criteria), commit, move on. Never start a phase until its dependencies are green
(see the plan's dependency map; **P1 gates all**, **P2+P3 gate any build**, **P4 gates release**,
**P5 gates Harness capabilities**, **P8 gates repeatable use**).

### Phase 0 — Repository Baseline
**Prompt:** `Begin Phase 0 (Repository Baseline) from docs/design-and-implementation-plan.md. Plan mode first (sub-tasks 1–6), then implement the neutral monorepo skeleton, pyproject (factory_core), Makefile stubs, .gitignore, README, AGENTS.md. Report the Phase 0 acceptance table.`
**Verify:** `python -m factory_core --help` returns a controlled message · `make validate/test/lint` exist · root docs describe a generic factory and name both governing docs · commit `chore: repo baseline`.

### Phase 1 — Generic Coding Harness (gates everything)
**Prompt:** `Begin Phase 1 (Generic Coding Harness). Governing: claude-code doc. Create coding-harness/.claude/ (the plan's generic Layer-1 harness). Plan mode first (sub-tasks 1–13), then implement: settings, the 6 rules, the 4 generic skills, install + pin the operator-provided official skill-creator from docs/reference/skill-creator/ into skills/skill-creator/ (do not modify it), 7 generic sub-agents (least-privilege; skill-author preloads skill-creator), 4 hooks, the output style, and integration-manifest.schema.json. Finish with the grep guard and report the Phase 1 acceptance table.`
**Verify:** `grep -rInE 'harness-cli|cli_surface|HARNESS_|Harness\.io' coding-harness/.claude/ --exclude-dir=skill-creator` is empty · skill-creator present + pinned in `docs/PINS.md` (unmodified) · rules/skills/agents/hooks correctly placed · reviewers read-only, packager writes only `dist/` · hooks deterministic, no external calls · schema validates a sample manifest · commit `feat(harness): generic Layer-1 coding harness + bundled skill-creator`.

### Phase 2 — Factory Core Contracts & Schemas
**Prompt:** `Begin Phase 2 (Factory Core Contracts & Schemas). Plan mode first (sub-tasks 1–15), then implement all 11 per-artifact schemas under factory-core/contracts/ with examples/valid + examples/invalid, the loader, validate_contracts.py, and pytest. No global contract shortcut. Report the Phase 2 acceptance table.`
**Verify:** every artifact type (incl. the CLI adapter) has its own schema · tests pass: valid passes, invalid fails, missing-required fails, unknown `kind` fails · commit `feat(contracts): per-artifact schemas + validators`.

### Phase 3 — Compiler & Validator Runtime
**Prompt:** `Begin Phase 3 (Compiler & Validator Runtime). Governing: both docs. Plan mode first (sub-tasks 1–10), then implement the deterministic compiler (model, shared, to_claude_code, to_copilot, to_cli_adapter), the conformance validators that encode the governing docs' specific rules (design §8), the .factory-manifest.json hash manifest + generated-file banners, and golden tests independent of any real capability. Report the Phase 3 acceptance table.`
**Verify:** compile twice → identical hashes · all `dist/` files carry generated metadata · validator fails on hash drift · Claude vs Copilot outputs match their conventions · ≥1 golden per target incl. CLI adapter · commit `feat(compiler): deterministic emitters + conformance + golden`.

### Phase 4 — Eval, Security & Certification Harness (gates marketplace)
**Prompt:** `Begin Phase 4 (Eval, Security & Certification Harness). Governing: claude-code + the bundled, pinned skill-creator (coding-harness/.claude/skills/skill-creator/) + both docs for triggering. Plan mode first (sub-tasks 1–11), then bind skill-creator's three surfaces from the bundled skill (no separate clone), implement the typed results incl. SecurityScanResult and CliContractResult, the runners (trigger, behavioral, smoke, cli-contract, security-scan), the certification writer, the stale-hash gate, and fail-closed gate.py. Prove with capabilities/_smoke. Report the Phase 4 acceptance table.`
**Verify:** packaging fails without current certification · cert binds source+target hashes · trigger/behavioral fail closed · Claude+Copilot smoke recorded · **security scan included** · `_smoke` blocks on a stale artifact · offline unit tests use fake fixtures · commit `feat(evals): certification + security + fail-closed gates`.

### Phase 5 — Harness CLI Integration Layer (dual exposure; gates Harness caps)
**Prompt:** `Begin Phase 5 (Harness CLI Integration Layer). The CLI-internal contract is factory-owned; MCP wiring conforms to claude-code Ch.6 and the ghcopilot MCP config at the boundaries. Plan mode first (sub-tasks 1–11), then implement domains/harness/integration.yaml and cli-integration/harness-cli/ with BOTH surfaces: bash wrappers AND the MCP adapter. Enforce dry-run by default, CLI version gating (fail unsupported), output redaction, and audited MCP tool descriptions. Add command-manifest, output-schemas, fixtures, golden, compatibility.yaml, and contract tests. Report the Phase 5 acceptance table.`
**Verify:** integration.yaml validates vs the Phase-1 schema · bash wrappers dry-run by default · MCP adapter lists tools mapping the declared verbs×resources · version-gate + redaction proven by tests · CC `.mcp.json` + Copilot MCP fragments valid, env-auth only · surface ⊆ declared `cli_surface` · commit `feat(integration): Harness CLI first-class (bash + MCP, gated)`.

### Phase 6 — Walking-Skeleton Capability + Claude Code Target
**Prompt:** `Begin Phase 6 (Walking-Skeleton Capability + Claude Code target). Governing: claude-code doc. Plan mode first (sub-tasks 1–12), then implement domains/harness/capabilities/harness-pipeline-author/ and the Claude Code build branch only. Scripts must call the CLI ADAPTER, not raw APIs. Emit AGENTS.md into the bundle. End with `make ship NAME=harness-pipeline-author`, assert the .factory-manifest.json is hash-clean, and report the Phase 6 acceptance table.`
**Verify:** `make ship NAME=harness-pipeline-author` runs end-to-end · plugin installs + triggers + drives CLI in sandbox → validated pipeline YAML · gates: trigger ≥ 0.85, behavioral ≥ 0.90, security clean, conformance PASS, certification PASS · dist hash-clean · commit `feat(capability): harness-pipeline-author (Claude Code)`.

### Phase 7 — GitHub Copilot Target
**Prompt:** `Begin Phase 7 (GitHub Copilot target). Governing: ghcopilot doc. Plan mode first (sub-tasks 1–6), then implement the Copilot build branch so the SAME canonical SKILL.md emits a .github bundle (no second skill). Map ordered agent_dispatch to handoffs and parallel to single-level sub-agents. Emit AGENTS.md into the bundle. Add the Copilot trigger smoke. Report the Phase 7 acceptance table.`
**Verify:** both targets from one SKILL.md · Copilot smoke passes (recorded; CC authoritative) · `conformance-copilot` passes · repo-bundle works across Copilot CLI/VS Code/cloud/code-review · commit `feat(capability): Copilot target`.

### Phase 8 — Factory Pipeline & CI Gates (gates repeatable use)
**Prompt:** `Begin Phase 8 (Factory Pipeline & CI Gates). Governing: both. Plan mode first (sub-tasks 1–6), then implement factory_core/cli.py (Typer), the Makefile wiring incl. ship, the CI (changed-capability detection → validate → tests → evals → compile → verify dist → upload certs), the merge gate, the release workflow, and the two docs. Report the Phase 8 acceptance table.`
**Verify:** `make ship TARGET=<target>` one-command · CI fail-closed on missing/stale evals · changed detection never skips required gates · release artifacts produced · new capability shippable without re-architecting · commit `feat(pipeline): CI gates + release`.

### Phase 9 — Distribution, Onboarding & Governance
**Prompt:** `Begin Phase 9 (Distribution, Onboarding & Governance). Governing: both (managed settings + marketplace/plugin models). Plan mode first (sub-tasks 1–8), then implement the internal marketplace, Copilot install pack, the harness-ai installer (verifies CLI presence + version), managed-settings governance (managed MCP allow-list, enabledPlugins, allowManagedHooksOnly, Copilot enterprise-managed plugins), the version-compatibility matrix, consumer docs incl. rollback, the versioning + deprecation policy, and the release-approval checklist. Report the Phase 9 acceptance table.`
**Verify:** Claude + Copilot install work · installer detects missing/incompatible CLI · **rollback restores a prior version** · managed settings enforced on runners · deprecation windows + approval checklist documented · commit `feat(dist): distribution + governance + lifecycle`.

### Phase 10 — Scale-out Roadmap & Metrics
**Prompt:** `Begin Phase 10 (Scale-out Roadmap & Metrics). Governing: both. Plan mode first (sub-tasks 1–6), then implement domains/harness/capability-roadmap.md (ranked by mutation risk), one-page intent briefs, scaffold+certify the next two capabilities, the adoption metrics, and the non-Harness reuse pilot proving the harness is domain-free. Report the Phase 10 acceptance table.`
**Verify:** new capabilities follow scaffold→eval→build→certify→package · each workflow-scoped (narrow CLI surface) · metrics tracked · governance retained · **non-Harness pilot builds on the unchanged harness** · commit + tag the first release.

---

## 5. Driving tips & troubleshooting

- Keep Claude Code in **plan mode** at the start of every phase — approve the file list before any write.
- One phase per session where possible; keep the diff reviewable.
- **Conformance fail:** have it quote the exact rule in the governing doc and fix to the doc, not the test.
- **Security-scan fail / redaction gap:** treat as a release blocker; move any token/ID to `userConfig`/env and ensure the adapter redacts CLI output.
- **dist/ hash mismatch:** the fix belongs in source or the compiler, never in `dist/` — regenerate.
- **Copilot trigger flaky:** Claude Code is authoritative; don't gate the build on the Copilot smoke number.
- Commit each green gate so a bad phase rolls back cleanly.

---

## 6. After Phase 10 — operating the factory

Adding capability **N+1** needs no factory changes — only a new `domains/harness/capabilities/<name>/`.
`make` takes the capability/target as variables (`NAME=`, `DOMAIN=`, `TARGET=`, `SANDBOX=1`); all
command targets are `.PHONY`:

```
make new-capability DOMAIN=harness NAME=<name>   # scaffold against the integration manifest
make research NAME=<name>                        # (optional) seed capability.yaml; you sign off
make author NAME=<name>                          # skill-author writes the canonical SKILL.md
make ship NAME=<name>                            # validate → eval → build → certify → package, fail-closed
```

New domain? Drop `domains/<other>/integration.yaml` — `coding-harness/` is domain-free and reused
as-is. Follow `domains/harness/capability-roadmap.md` for the ranked rollout.

---

## Appendix — quick reference

**Bootstrap (operator):** `CLAUDE.md`, `AGENTS.md`, `docs/design-and-implementation-plan.md`,
`docs/reference/{claude-code…, ghcopilot…, harness-skill-factory.original}.md`.

**Built by Claude Code (P0→P10):** baseline → generic harness → contracts/schemas → compiler+golden
→ eval/security/cert → CLI integration (bash+MCP) → capability+CC → Copilot → pipeline/CI →
distribution/governance → scale-out/metrics.

**Per-capability gate order:** `validate → conform → eval → security → build → certify → package →
release`, fail-closed on missing/stale/below-threshold artifacts.

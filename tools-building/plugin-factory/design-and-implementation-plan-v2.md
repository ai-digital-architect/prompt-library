# Skill & Plugin Factory — Revised Design & Phased Implementation Plan (v2, merged)

> **Supersedes v1** (`design-and-implementation-plan.md`) and the original `harness-skill-factory.md`.
> This version folds in every **additive** improvement identified when comparing v1 against the
> alternative (GPT-5.5) plan, while keeping v1's strengths intact.
>
> **Kept exactly as proposed:** the **dual CLI exposure** model — CLI-as-bash (deterministic
> default) **and** a thin Harness **MCP adapter** wired into both hosts.
>
> **Governing architecture documents** (conformance is a BLOCKER):
> - `claude-code-customization-architecture-revised.md` — every Claude Code artifact + the harness.
> - `ghcopilot-customization-arch.md` — every GitHub Copilot artifact.

---

## Merge coverage map (what changed vs v1)

| Item | Type | Where it now lives |
|---|---|---|
| **G1** Executable, versioned, test-backed schemas (valid/invalid fixtures + pytest) | additive | Design §6; **Phase 2** |
| **G2** Standalone compiler/validator runtime + `.factory-manifest.json` hash manifest + generated-file banners + golden tests | additive | Design §5; **Phase 3** |
| **G3** Security as a certification dimension (secret scan, mutating-command scan), CLI **output redaction**, CLI **version gating** | additive | Design §6D, §8; **Phase 4**, **Phase 5** |
| **G4** Distribution depth: rollback, upgrade, **deprecation windows**, **release-approval checklist** | additive | Design §9; **Phase 9** |
| **G5** Phase **ownership / RACI** matrix | additive | Design §10; [Ownership matrix](#ownership-matrix-g5) |
| **G6** Scale-out backlog ranked by **mutation risk** + **adoption metrics** | additive | Design §11; **Phase 10** |
| **G7** Repository baseline as an explicit plan phase | additive | **Phase 0** |
| **G8** Output-style surface + `revise-artifact` skill + finer generic sub-agent split | additive | Design §3; **Phase 1** |
| **G9** Final-gate checklist + MVP walking-skeleton slice | additive | [MVP slice](#mvp-walking-skeleton-slice-g9), [Final gate](#final-gate-checklist-g9) |
| Prompt-injection hardening of **MCP tool descriptions** | both-miss, additive | Design §4; **Phase 5** |
| Cross-component **version-compatibility matrix** | both-miss, additive | Design §9; **Phase 9** |
| **AGENTS.md emission** for emitted capability bundles | both-miss, additive | **Phase 6/7** |
| **S1** Conformance bound to the governing docs' specific rules | preserved | Design §8; **Phase 3** |
| **S2** Dual CLI exposure incl. MCP adapter | preserved (your call) | Design §4; **Phase 5** |
| **S3** Integration-manifest extension contract + non-Harness reuse pilot | preserved | Design §3, §11; **Phase 10** |
| **S4** Managed-settings governance levers | preserved | Design §10; **Phase 9** |
| **S5** Operator handoff kit | preserved | `IMPLEMENTATION-GUIDE-v2.md`, `CLAUDE.md`, `AGENTS.md` |

**Naming cleanup adopted:** domain artifacts are grouped under `domains/<domain>/` (from the
alternative plan), which removes the old `harness/` ↔ `integrations/harness/` collision. The
generic Layer-1 harness stays in its own distributable folder, `coding-harness/.claude/`.

---

# Part I — Revised Design

## 0 — Load-bearing decisions

| # | Decision | Default | Reversible? |
|---|---|---|---|
| D1 | **CLI exposure** | **Both:** CLI-as-bash (default, deterministic) **+** thin Harness MCP adapter (first-class in both hosts). | Yes — drop the MCP adapter; bash backbone stands. |
| D2 | Generic harness distribution | Versioned, project-agnostic plugin/scaffold in `coding-harness/`. | Yes |
| D3 | Domain isolation | All Harness specifics under `domains/harness/`; harness core is domain-free. | Yes |
| D4 | Copilot distribution | Repo-committed `.github/` bundle default; marketplace plugin when published org-wide. | Yes |
| D5 | Trigger-cert authority | Claude Code authoritative; Copilot = smoke check. | Yes |
| D6 | Public Harness MCP server | Not used; the custom CLI (and its adapter) is the sole Harness surface. | Reversible, not recommended. |

---

## 1 — Architecture: three concentric layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1 — GENERIC CODING HARNESS  (coding-harness/.claude/, project-agnostic) │
│  Meta-tool to build ANY skill/plugin for ANY platform/domain.                 │
│  rules • generic sub-agents • generic skills • hooks • output style •         │
│  integration-manifest contract (knows NOTHING of Harness)                     │
│         ▲  governed by: claude-code-customization-architecture-revised.md     │
├─────────┼─────────────────────────────────────────────────────────────────────┤
│ FACTORY CORE  (factory-core/, generic Python engine)                          │
│  contracts (schemas) • compilers (emitters) • validators (conformance) •      │
│  evals (skill-creator + security + cli-contract) • cli_adapters • authoring    │
└─────────┬─────────────────────────────────────────────────────────────────────┘
          │ plugs in via integration manifest
┌─────────┴─────────────────────────────────────────────────────────────────────┐
│ LAYER 2+3 — DOMAINS  (domains/harness/, domain-specific)                       │
│  integration.yaml • cli-integration/ (bash wrappers + MCP adapter) ◄── CLI     │
│  capabilities/<name>/ (SOURCE OF TRUTH) • distribution/                        │
│         │ compiled by Factory Core →                                          │
│         ▼                                                                      │
│  dist/claude-code/<name>/ (plugin)        dist/copilot/<name>/ (.github bundle) │
│   gov: claude-code doc                     gov: ghcopilot-customization-arch.md │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2 — Repository structure

```
skill-plugin-factory/                         # monorepo, trunk-based
├── coding-harness/                            # Layer 1 — generic, distributable (D2)
│   └── .claude/
│       ├── settings.json                      # sandbox, hooks (validate, block-secrets, eval-before-build, audit)
│       ├── rules/                             # factory-architecture, schema-design, testing-and-evals, security, conformance-*
│       ├── skills/                            # create-artifact, revise-artifact, run-certification, package-release  (G8)
│       │   └── skill-creator/                 # OFFICIAL Anthropic skill-creator — bundled + pinned (operator-provided)
│       ├── agents/                            # intent-researcher, artifact-architect, skill-author, contract-reviewer,
│       │                                      #   eval-designer, plugin-packager, release-reviewer                  (G8)
│       ├── output-styles/decision-grade-architect.md                                                                # (G8)
│       └── integration-manifest.schema.json   # Layer-1 ↔ domain extension contract (S3)
├── factory-core/                              # generic Python engine (package: factory_core)
│   ├── contracts/                             # per-artifact *.schema.yaml + examples/valid + examples/invalid     (G1)
│   ├── compilers/                             # model, shared, to_claude_code, to_copilot, to_cli_adapter           (G2)
│   ├── validators/                            # validate_contracts, validate_skill, validate_plugin, validate_cli_adapter (S1)
│   ├── evals/                                 # skill_creator_adapter, runners, certification_writer, security_scan  (G3)
│   ├── cli_adapters/                          # generic adapter base (version-gate, redaction, golden compare)       (G3)
│   └── authoring/                             # skill_creator_guidance
├── docs/PINS.md                               # records the pinned skill-creator version + source                    (§7)
├── domains/
│   └── harness/                               # Layer 2+3 — all Harness specifics (D3)
│       ├── integration.yaml                   # conforms to integration-manifest.schema.json
│       ├── cli-integration/harness-cli/       # cli-adapter.yaml, command-manifest, output-schemas, fixtures,
│       │                                      #   golden, sandbox-profile, compatibility.yaml, MCP adapter         (S2,G3)
│       ├── capabilities/<name>/               # SOURCE OF TRUTH: capability.yaml, SKILL.md, references, scripts,
│       │                                      #   assets, commands, agents, evals
│       ├── distribution/                      # claude-marketplace, copilot-install-pack, install scripts          (G4)
│       └── capability-roadmap.md              # ranked backlog + metrics                                            (G6)
├── dist/                                      # BUILD OUTPUT (generated; never hand-edited)
│   ├── claude-code/<name>/  • copilot/<name>/  • certifications/<name>/<version>/
│   └── <target>/<name>/.factory-manifest.json # hash manifest + generated-file metadata                            (G2)
├── tests/golden/<target>/<name>/              # golden fixtures for deterministic compile                            (G2)
├── .claude-plugin/marketplace.json
├── pyproject.toml • Makefile • docs/ • CLAUDE.md • AGENTS.md • README.md
```

---

## 3 — Generic harness (Layer 1)

Domain-free. Learns a domain only via an **integration manifest** it loads at build time (S3):

```yaml
# domains/harness/integration.yaml  (conforms to coding-harness/.claude/integration-manifest.schema.json)
id: harness
display_name: "Harness.io CI/CD"
cli:
  adapter_ref: cli-integration/harness-cli/cli-adapter.yaml   # bash + version-gate + redaction
  expose: [bash, mcp]                                         # D1 — both surfaces
mcp_adapter:
  server_name: harness
  registration_ref: cli-integration/harness-cli/mcp/registration.json
packaging:
  claude_code: { userConfig_ref: distribution/cc-userconfig.json }
  copilot:     { instructions_ref: distribution/copilot-house-rules.md }
house_rules_ref: distribution/harness-house-rules.md
```

**Generic skills (G8):** `create-artifact`, `revise-artifact` (iterate an existing capability),
`run-certification`, `package-release`, plus the **official Anthropic `skill-creator`** skill
itself — bundled into the harness (operator-provided, pinned). It is generic (it builds *any*
skill), so it belongs in Layer 1; the `skill-author` sub-agent preloads it via `skills:
[skill-creator]`. **Generic sub-agents (G8):** intent-researcher,
artifact-architect, skill-author, **contract-reviewer**, eval-designer, plugin-packager,
**release-reviewer** — least-privilege (reviewers read-only; packager writes only `dist/`).
**Output style (G8):** `decision-grade-architect.md`.

---

## 4 — Custom Harness CLI as first-class participant (Layer 2) — dual exposure (S2)

| Surface | Used for | Claude Code wiring | Copilot wiring | Safety |
|---|---|---|---|---|
| **CLI-as-bash** (default) | Deterministic, evaluable steps | skill `scripts/*`; `allowed-tools: Bash` | skill `scripts/*` | `--dry-run` + `HARNESS_CLI_PROFILE=sandbox` |
| **Harness MCP adapter** | Conversational tool discovery/calls | `.mcp.json` → `mcp__harness__*` | Copilot MCP config | adapter enforces dry-run; **redacts output** (G3) |

Additional hardening:
- **Version gating (G3):** the adapter runs `harness-cli version --json` and **fails on
  unsupported versions** (range declared in `compatibility.yaml`).
- **Output redaction (G3):** the adapter strips secrets/account IDs from CLI output **before it
  enters the model's context**.
- **MCP tool-description trust (both-miss):** tool descriptions exposed by the adapter are
  reviewed/owned by harnesspf-team and treated as untrusted-input-adjacent; no third-party
  description text is passed through unaudited.
- Credentials never appear in artifacts: `userConfig`→keychain (Claude Code) and
  `${HARNESS_API_TOKEN}` env (both hosts).

---

## 5 — Build pipeline, compiler & gates

The compiler (G2) is a **standalone, deterministic engine** built and golden-tested **before**
any real capability exists. Every generated file carries a generated-file banner and is recorded
in `dist/<target>/<name>/.factory-manifest.json`. Re-running the compiler must produce identical
hashes; a hash mismatch against the manifest = hand-edit detected = build failure.

| Stage | `make` invocation | Gate |
|---|---|---|
| scaffold | `make new-capability DOMAIN=<domain> NAME=<name>` | — |
| research | `make research NAME=<name>` | human signs off `capability.yaml` |
| author | `make author NAME=<name>` | — |
| validate | `make validate TARGET=<target>` | **hard fail** (schema + links + budgets) |
| **conformance** | `make conform TARGET=<target>` | **hard fail — blocker** (vs governing docs, S1) |
| eval | `make eval TARGET=<target> SANDBOX=1` | **hard fail** (trigger + behavioral) |
| **security** | (part of certify) | **hard fail** (secret + mutating-command scan, G3) |
| build | `make build TARGET=<target>` | deterministic; manifest written |
| certify | `make certify TARGET=<target>` | **fail-closed**: writes certification incl. source+target hashes, security, smoke |
| package | `make package TARGET=<target>` | refuses without current certification |
| release | `make release` | approval checklist (G4) |

---

## 6 — Per-artifact I/O contracts — now executable schemas (G1)

Each artifact type has its **own** versioned schema under `factory-core/contracts/`, with
`examples/valid/` and `examples/invalid/` and pytest coverage (valid passes, invalid fails,
missing required field fails, unknown `kind` fails). No single global contract.

```
factory-core/contracts/
├── base.schema.yaml             # apiVersion, kind, metadata{name,owner,lifecycle}, spec
├── capability.schema.yaml       # 6E — factory input (intent)
├── claude-skill.schema.yaml     # 6A
├── claude-plugin.schema.yaml    # 6A
├── copilot-skill.schema.yaml    # 6B
├── copilot-prompt.schema.yaml   # 6B
├── copilot-agent.schema.yaml    # 6B
├── copilot-plugin.schema.yaml   # 6B
├── cli-adapter.schema.yaml      # 6C — the CLI contract (factory-owned; neither arch doc covers it)
├── eval-suite.schema.yaml       # 6D
└── certification.schema.yaml    # 6D — incl. security + cli-contract + smoke dimensions
```

**6A — Claude Code skill/plugin** (gov: claude-code doc). OUT: `.claude-plugin/plugin.json`
(+`userConfig`), `skills/<name>/SKILL.md`, `commands/*.md`, `agents/*.md` (**restricted
frontmatter**), `.mcp.json` (iff mcp exposure), `hooks/hooks.json`. CONF: no
hooks/mcpServers/permissionMode in plugin sub-agents; `.mcp.json` at root; no secrets.

**6B — Copilot `.github` bundle / plugin** (gov: ghcopilot doc). OUT: `.github/skills/<name>/SKILL.md`
(+`references/`), `.github/agents/*.agent.md` (ordered→handoffs, parallel→**single-level**
sub-agents), `.github/prompts/*.prompt.md` (links to skill), optional `hooks/`, optional
`plugin.json` (D4); `copilot-instructions.md` = **house rules only**. CONF: description = sole
trigger; progressive-disclosure budgets; no workflow in instructions; least-privilege tools.

**6C — Harness CLI integration** (gov: factory-owned spec). OUT: bash wrappers + MCP adapter +
registration fragments (CC `.mcp.json`, Copilot MCP config) + `command-manifest.yaml` +
`output-schemas/` + `fixtures/` + `golden/` + `compatibility.yaml`. CONF: dry-run default;
version-gated; redaction on; surface ⊆ declared `cli_surface`.

**6D — Eval / certification bundle** (gov: skill-creator + both docs). OUT: `evals.json`
(behavioral), `trigger-evals.json`, `platform-smoke.json`, `benchmark.json`,
`security-report.json`, `certification.json` (source hash + per-target hashes). GATES (all must
pass before marketplace): trigger ≥ threshold (CC authoritative; Copilot smoke recorded);
behavioral ≥ threshold (sandboxed CLI fixtures, golden); **security scan = clean (G3)**;
**CLI-contract result = pass**; conformance = PASS; **skill-creator certification = PASS**.

**6E — Capability intent** (factory input). Platform-neutral: name, owner, job_to_be_done,
trigger_when/not, `integration{id, cli_surface, expose}`, outputs, human_invocation[],
agent_dispatch[] (with `order`), targets[], distribution{}, eval thresholds.

---

## 7 — skill-creator certification binding

The **official Anthropic skill-creator skill is bundled directly into the harness** at
`coding-harness/.claude/skills/skill-creator/`. The operator provides it at bootstrap under
`docs/reference/skill-creator/`; **Phase 1 installs and pins it** (version/source recorded in
`docs/PINS.md`) and never modifies it. Because skill-creator is generic, it is a first-class
Layer-1 skill — the factory's `skill-author` sub-agent invokes it directly rather than shelling
out to a separate clone.

Three bound surfaces, all sourced from the bundled skill, calling its own scripts via
`${CLAUDE_SKILL_DIR}`: writing guide (→ `skill-author` via `factory-core/authoring`), eval harness
(→ `run_behavioral_evals`), description optimizer (→ `run_description_optimizer`, train/held-out
split). Unit tests run **offline against fake skill-creator output fixtures**.

> If your copy of skill-creator does **not** bundle the eval harness and description optimizer,
> keep those as a pinned companion under `coding-harness/.claude/skills/skill-creator/scripts/`
> and point the adapter there — the binding is otherwise unchanged.
>
> **Redistribution:** bundling Anthropic's skill-creator inside the harness is fine for internal
> enterprise distribution; keep it pinned and confirm terms before any external distribution.

Marketplace targets **require** a current skill-creator certification artifact; `release` is
fail-closed without it.

---

## 8 — Conformance gates bound to the governing docs (S1)

Conformance is mechanical and **doc-specific**, not just schema-shaped:

- **Claude Code:** plugin sub-agents have no `hooks`/`mcpServers`/`permissionMode`; `.mcp.json`
  at plugin root; skill `description` front-loads trigger; `${CLAUDE_PLUGIN_DATA}` for cached
  binaries; no secrets.
- **Copilot:** `description` is the sole trigger and states what+when; body within
  progressive-disclosure budget; sub-agents do not recurse (single level); `tools` least-privilege;
  instructions carry no workflow logic.
- **Security (G3):** secret scan + mutating-command scan across all emitted files.

`build`/`package`/`release` are fail-closed if the conformance **or** eval/certification artifact
is missing, stale (hash mismatch), or below threshold.

---

## 9 — Distribution, lifecycle & version compatibility (G4 + both-miss)

- **Claude Code:** internal marketplace (`.claude-plugin/marketplace.json`) + CI seed-dir image
  (`CLAUDE_CODE_PLUGIN_SEED_DIR`).
- **Copilot:** repo-committed `.github` install pack (default) + optional enterprise plugin.
- **One-step onboarding:** `harness-ai install --target claude-code|copilot|both` (adds
  marketplace, installs plugin, drops `.github` pack, verifies CLI presence + version).
- **Rollback (G4):** every release is restorable to the prior plugin/install-pack version.
- **Upgrade + deprecation (G4):** documented upgrade path; **deprecation windows** for retired
  capabilities.
- **Release-approval checklist (G4):** certification exists · security approval · platform-owner
  approval · docs updated · rollback tested.
- **Version-compatibility matrix (both-miss):** declared compatibility across **generic harness ↔
  skill-creator pin ↔ Harness CLI ↔ emitted artifacts**, checked at `build`.

---

## 10 — Governance & ownership (S4 + G5)

**Managed-settings levers (S4):** managed MCP allow-list pinned to `harness`
(`allowManagedMcpServersOnly` where mandated); `enabledPlugins` forcing harness + approved
capabilities onto runners; `allowManagedHooksOnly` in production CI; Copilot enterprise-managed
plugins (required/optional) separating availability from activation.

**Ownership / RACI (G5):** see the [Ownership matrix](#ownership-matrix-g5).

---

## 11 — Scale-out & metrics (G6 + S3)

**Ranked capability backlog by mutation risk (G6):**

| Order | Capability | Why this order |
|---:|---|---|
| 1 | `harness-pipeline-author` | core happy path; proves create + validate |
| 2 | `harness-pipeline-debugger` | high pain; mostly read/validate; low mutation risk |
| 3 | `harness-connector-onboard` | common setup; tests credential guardrails |
| 4 | `harness-policy-guard` | governance value; integrates security standards |
| 5 | `harness-deploy-promote` | higher risk; wait until dry-run/confirm patterns proven |
| 6 | `harness-template-migrator` | complex; benefits from prior capabilities |
| 7 | `harness-ci-governance-report` | read-heavy; adoption/leadership metrics |

**Adoption + quality metrics (G6):** installs, skill invocations, eval pass rates, CLI command
coverage, consumer-repo adoption.

**Reuse pilot (S3):** prove Layer 1 is domain-free by building a **non-Harness** pilot from a
second integration manifest, unchanged.

---

# Part II — Phased Implementation Plan

Phase 1 establishes the generic harness before any platform-specific component (the foundation
constraint). Each sub-task is hand-off-ready for Claude Code.

## Phase 0 — Repository Baseline (G7)

**Goal.** Neutral monorepo skeleton for a generic artifact factory. **Gov.** Both.
**Deliverables.** Structure, `pyproject.toml` (`factory_core`; deps: pydantic, pyyaml, jsonschema,
typer, rich, pytest, ruff), `Makefile` stubs, baseline CI, `.gitignore`, `README.md`, `AGENTS.md`.
**Sub-tasks.** 1) Create the tree from §2 (empty dirs ok). 2) `.gitignore` (`dist/tmp/`, `.venv/`,
`__pycache__`, `.env*`, `CLAUDE.local.md`, `.claude/settings.local.json`, `agent-memory-local/`).
3) `pyproject.toml`. 4) `Makefile` placeholder targets (`validate test lint format`). 5) Root
`AGENTS.md` (generic build/test/lint + conventions). 6) `README.md` (generic factory; `factory-core/`
vs `domains/` separation). **Acceptance.** `python -m factory_core --help` returns a controlled
message; `make validate/test/lint` exist; root docs describe a generic (not Harness-only) factory
and name the two governing docs.

## Phase 1 — Generic Coding Harness (Layer 1)  [GATES ALL]

**Goal.** `coding-harness/.claude/` reusable for any skill/plugin project; zero Harness refs.
**Gov.** claude-code doc. **Deliverables.** settings, rules, generic skills, generic sub-agents,
hooks, output style, integration-manifest schema.
**Sub-tasks.** 1) `settings.json` (model placeholder; allow/ask/deny; secret-deny; hooks). 2–6)
rules: `factory-architecture.md`, `schema-design.md`, `testing-and-evals.md`, `security.md`,
`conformance-claude-code.md` (`paths: dist/claude-code/**`), `conformance-copilot.md` (`paths:
dist/copilot/**`). 7) generic skills `create-artifact`, `revise-artifact`, `run-certification`,
`package-release`. 8) **install the operator-provided official skill-creator** from
`docs/reference/skill-creator/` into `coding-harness/.claude/skills/skill-creator/`; pin its
version/source in `docs/PINS.md`; do not modify its contents. 9) generic sub-agents (7,
least-privilege per §3); give `skill-author` `skills: [skill-creator]` so it preloads it. 10) hooks
`validate-json-yaml.sh`, `block-secrets.sh`, `enforce-eval-before-build.sh`, `audit-tool-use.sh`.
11) `output-styles/decision-grade-architect.md`. 12) `integration-manifest.schema.json`. 13) grep
guard in `make validate`: fail on `harness-cli|cli_surface|HARNESS_|Harness\.io` under
`coding-harness/.claude/`, **excluding `skills/skill-creator/`** (generic; may use "harness" as a
common noun).
**Acceptance.** grep guard clean; skill-creator present + pinned (unmodified); correct placement
(rules=standards, skills=workflows, agents=roles, hooks=gates); least-privilege enforced; hooks
deterministic/no external calls; schema validates a sample manifest.

## Phase 2 — Factory Core Contracts & Schemas (G1)

**Goal.** Per-artifact I/O contracts real, versioned, machine-validatable. **Gov.** Both + the
factory-owned CLI-adapter contract. **Deliverables.** The 11 schemas in §6, loader, validators,
fixtures, tests.
**Sub-tasks.** 1) `base.schema.yaml`. 2–11) the per-artifact schemas (§6). 12) `examples/valid/`
+ `examples/invalid/` per schema. 13) `factory_core/contracts/loader.py`. 14)
`factory_core/validators/validate_contracts.py`. 15) pytest: valid passes; invalid fails; missing
required fails; unknown `kind` fails. **Acceptance.** every artifact type has its own schema (no
global shortcut); CLI adapter has its own schema; tests pass on valid/invalid fixtures.

## Phase 3 — Compiler & Validator Runtime (G2 + S1)

**Goal.** Deterministic compiler turning neutral source → target layouts, golden-tested before any
real capability. **Gov.** Both. **Deliverables.** compiler runtime, emitters, conformance
validators, `.factory-manifest.json`, golden tests.
**Sub-tasks.** 1) `compilers/model.py` (Capability, ArtifactRef, Target, CompilerOutput,
HashManifest). 2) `compilers/shared.py` (path norm, checksum-copy, frontmatter parse, md
validation, **generated-file banner**). 3) `compilers/to_claude_code.py` (plugin.json, SKILL.md,
references/scripts/assets, transpile agents→restricted frontmatter, commands). 4)
`compilers/to_copilot.py` (`.github/skills|prompts|agents`, hooks, house-rules-only instructions).
5) `compilers/to_cli_adapter.py` (command manifests, output schemas, fixtures+golden, README). 6–8)
**conformance validators bound to the docs (S1):** `validate_skill.py`, `validate_plugin.py`,
`validate_cli_adapter.py` — encode the §8 doc-specific rules. 9) `.factory-manifest.json` per
artifact. 10) golden tests vs `tests/golden/<target>/<name>/`. **Acceptance.** compile twice =
identical hashes; all `dist/` files carry generated metadata; validator fails on hash drift;
Claude output matches plugin/skill conventions, Copilot matches `.github`; ≥1 golden per target
incl. CLI adapter.

## Phase 4 — Eval, Security & Certification Harness (skill-creator + G3)  [GATES MARKETPLACE]

**Goal.** Certification system that gates build/package/release, including security. **Gov.**
claude-code + skill-creator + both docs for triggering. **Deliverables.** skill-creator adapter +
runners + certification writer + stale-hash gate + reports.
**Sub-tasks.** 1) point the eval adapter at the **bundled** skill-creator
(`coding-harness/.claude/skills/skill-creator/`, pinned in Phase 1 via `docs/PINS.md`) — no
separate clone. 2) `evals/skill_creator_adapter.py` (`run_description_optimizer`,
`run_behavioral_evals`, `collect_skill_creator_artifacts`) calling the skill's bundled scripts. 3) `evals/types.py` (Trigger/Behavioral/Smoke/CliContract/
**Security**/Certification results). 4) runners: trigger, behavioral, platform-smoke, cli-contract,
**security-scan (secret + mutating-command)**. 5) `evals/certification_writer.py`. 6) **stale-hash
check** (hash source; fail if source changed after eval). 7) certification output:
`dist/certifications/<name>/<version>/{certification,benchmark,security-report}.json`. 8) `make`
targets `certify`, `verify-certified`; markdown reviewer report. 9) fail-closed `gate.py`. 10)
offline unit tests via fake skill-creator fixtures. 11) prove with throwaway `_smoke` capability.
**Acceptance.** packaging fails without current certification; cert binds source+target hashes;
trigger/behavioral thresholds fail closed; Claude+Copilot smoke recorded; **security scan
included**; `_smoke` blocks on stale artifact.

## Phase 5 — Harness CLI Integration Layer (Layer 2) — dual exposure (S2 + G3)  [GATES HARNESS CAPS]

**Goal.** Make the custom CLI first-class via **bash + MCP adapter**, version-gated, redacting,
contract-tested. **Gov.** factory CLI-adapter contract; claude-code Ch.6 + ghcopilot MCP config at
the wiring boundaries. **Deliverables.** `domains/harness/integration.yaml` +
`cli-integration/harness-cli/` (cli-adapter.yaml, command-manifest, output-schemas, fixtures,
golden, sandbox-profile, compatibility.yaml, **mcp/ adapter + registration**), README.
**Sub-tasks.** 1) `integration.yaml` (validates vs Phase-1 schema; `expose: [bash, mcp]`). 2)
`cli-adapter.yaml` (executable + `versionCommand` + safety{defaultMode: dry-run, mutatingVerbs}). 3)
`command-manifest.yaml` (workflow-scoped slice: pipeline get/list/validate/create --dry-run/apply
--dry-run, connector list, trigger list). 4) output schemas per command. 5) fixtures (minimal,
multi-stage, with-connector, invalid). 6) golden command-lines + outputs. 7)
`factory_core/cli_adapters/harness_cli.py`: **version check (fail unsupported)**, command
rendering, dry-run enforcement, **output redaction**, golden compare. 8) **MCP adapter** in `mcp/`
mapping `harness.<verb>.<resource>` → CLI; defer schemas; forward dry-run/profile; **audited tool
descriptions** (both-miss). 9) registration fragments: CC `.mcp.json` + Copilot MCP config (env
auth only). 10) contract tests (missing version fails; unsupported version fails; prod mutation in
eval fails; command matches golden; output validates). 11) `make validate-cli-adapter`,
`make test-cli-adapter`. **Acceptance.** integration.yaml valid; both surfaces dry-run by default; MCP
lists tools mapping the declared surface; version-gate + redaction proven; no secrets/prod
endpoints; surface ⊆ declared `cli_surface`.

## Phase 6 — Walking-Skeleton Capability + Claude Code Target

**Goal.** First capability source + Claude Code plugin target, end-to-end. **Gov.** claude-code
doc. **Deliverables.** `domains/harness/capabilities/harness-pipeline-author/` + CC plugin under
`dist/`.
**Sub-tasks.** 1) capability dir (capability.yaml, SKILL.md, references, scripts, assets,
commands, agents, evals). 2) `capability.yaml` (§6E; targets `[claude-code]` for now). 3) canonical
SKILL.md (dry-run default; CLI-adapter usage; confirm-before-mutate; refs). 4–8) references,
scripts (call the CLI **adapter**, not raw APIs), assets, neutral command, neutral agent. 9) evals
(`trigger-evals.json`, `evals.json`, `platform-smoke.json`). 10) `make build … TARGET=claude-code` → plugin (plugin.json+userConfig, SKILL.md, commands, restricted agents, `.mcp.json`,
hooks). 11) **emit `AGENTS.md` into the bundle** (both-miss — cross-tool memory). 12) `make ship`;
assert `.factory-manifest.json` hash-clean. **Acceptance.** `make ship` runs end-to-end; plugin
installs + triggers + drives CLI in sandbox → validated YAML; gates (trigger ≥ 0.85, behavioral ≥
0.90, security clean, conformance PASS, certification PASS); dist hash-clean.

## Phase 7 — GitHub Copilot Target

**Goal.** Same canonical SKILL.md → `.github` bundle (+ optional plugin); no second skill. **Gov.**
ghcopilot doc. **Sub-tasks.** 1) add `copilot` to `targets`; `distribution.copilot: repo-bundle`
(D4). 2) `make build … TARGET=copilot` → `.github/skills|prompts|agents`, hooks,
house-rules-only instructions. 3) ordered dispatch→handoffs, parallel→single-level sub-agents. 4)
emit `AGENTS.md` into the bundle. 5) Copilot trigger smoke (recorded; CC authoritative). 6)
optional Claude-format plugin for marketplace. **Acceptance.** both targets from one SKILL.md;
Copilot smoke passes; `conformance-copilot` passes; repo-bundle works across Copilot CLI/VS
Code/cloud/code-review.

## Phase 8 — Factory Pipeline & CI Gates

**Goal.** Repeatable factory via Typer CLI + `make` + CI. **Gov.** Both. **Sub-tasks.** 1)
`factory_core/cli.py` (new capability/cli-adapter, validate, eval, build, certify, package,
release, ship). 2) `Makefile` wiring incl. `ship = validate→eval→build→certify→package`. 3) CI:
detect changed capabilities → validate contracts → unit + CLI-adapter tests → evals → compile →
verify dist → upload certs. 4) merge gate: no stale cert; no generated drift without source
change; no failing eval; no secrets. 5) release workflow: package certified → update marketplace →
Copilot pack → tag → notes. 6) `docs/factory-pipeline.md`, `docs/debugging-failed-certification.md`.
**Acceptance.** `make ship TARGET=<target>` one-command; CI fail-closed on missing/stale evals; changed
detection never skips required gates; release artifacts produced; new capability shippable without
re-architecting.

## Phase 9 — Distribution, Onboarding & Governance (G4 + S4 + both-miss)

**Goal.** Certified artifacts installable enterprise-wide, with lifecycle + governance. **Gov.**
both (managed settings, marketplace/plugin models). **Sub-tasks.** 1)
`domains/harness/distribution/claude-marketplace/marketplace.json` + catalog entry. 2)
`copilot-install-pack/`. 3) `harness-ai install --target claude-code|copilot|both` (adds
marketplace, installs plugin, drops `.github` pack, **verifies CLI presence + version**). 4)
**managed-settings governance (S4):** managed MCP allow-list (`harness`,
`allowManagedMcpServersOnly`), `enabledPlugins`, `allowManagedHooksOnly`, Copilot
enterprise-managed (required/optional) plugins. 5) **version-compatibility matrix (both-miss):**
harness ↔ skill-creator ↔ CLI ↔ artifacts; checked at build. 6) consumer docs: install, upgrade,
**rollback**, troubleshooting, security posture, dry-run behavior. 7) versioning policy: semver +
CLI compatibility matrix + **deprecation windows**. 8) **release-approval checklist:** certification
· security approval · platform-owner approval · docs updated · rollback tested. **Acceptance.**
Claude + Copilot install work; installer detects missing/incompatible CLI; **rollback restores a
prior version**; managed settings enforced on runners; docs let a team self-install.

## Phase 10 — Scale-out Roadmap & Metrics (G6 + S3)

**Goal.** Produce multiple workflow-scoped capabilities consistently; prove cross-domain reuse.
**Gov.** both. **Sub-tasks.** 1) `domains/harness/capability-roadmap.md` (ranked backlog §11). 2)
one-page intent brief per capability (job, users, CLI surface, **mutation risk**, eval strategy,
targets). 3) scaffold + research + author + eval + certify + package the next two capabilities. 4)
require human approval of each generated `capability.yaml`. 5) **adoption metrics (G6):** installs,
invocations, eval pass rates, CLI coverage, consumer adoption. 6) **non-Harness reuse pilot (S3):**
build a pilot from a second integration manifest, harness unchanged. **Acceptance.** new
capabilities follow scaffold→eval→build→certify→package; each workflow-scoped (narrow CLI surface,
no mega-skill); metrics tracked; governance retained; **reuse pilot builds unchanged.**

---

## Dependency map

| Phase | Depends on | Gates | Governing doc |
|---|---|---|---|
| **0** Repo baseline | — | 1 | both |
| **1** Generic harness | 0 | **everything** | claude-code |
| **2** Contracts & schemas | 1 | 3, 4, 5 | both + CLI-adapter contract |
| **3** Compiler runtime | 2 | 4, 6, 7 | both |
| **4** Eval/security/cert | 2, 3 | **marketplace release**; 6 | claude-code + skill-creator |
| **5** CLI integration | 2, 3 | **all Harness caps** (6, 7) | factory spec + claude-code/ghcopilot (MCP) |
| **6** Capability + CC | 1, 2, 3, 4, 5 | 7, 8 | claude-code |
| **7** Copilot target | 6 | 8 | ghcopilot |
| **8** Pipeline & CI | 6, 7 (and 4) | **repeatable use**; 9 | both |
| **9** Distribution & governance | 8 | 10 | both |
| **10** Scale-out & metrics | 9 (and 6, 7) | — | both |

```
P0 → P1 → P2 → P3 → P4 ┐
                  └→ P5 ┴→ P6 → P7 → P8 → P9 → P10
(P1 gates all · P2+P3 gate any build · P4 gates release · P5 gates Harness caps · P8 gates repeatable use)
```

---

## Ownership matrix (G5)

| Phase | Primary owner | Supporting owner |
|---|---|---|
| 0 | Factory platform owner | DevEx lead |
| 1 | Factory platform owner | Claude Code power user / security reviewer |
| 2 | Factory platform owner | Schema/API architect |
| 3 | Factory platform owner | Build/release engineer |
| 4 | Factory platform owner | QA/eval lead + security reviewer |
| 5 | harnesspf-team | Factory platform owner |
| 6 | harnesspf-team | Factory platform owner |
| 7 | Factory platform owner | GitHub Copilot platform owner |
| 8 | Build/release engineer | Factory platform owner |
| 9 | DevEx / platform enablement | Security & release approvers |
| 10 | harnesspf-team | Consumer-team representatives |

---

## MVP walking-skeleton slice (G9)

Smallest useful slice that proves the foundation before breadth:

```
P0 → P1 → P2 (minimal schemas) → P3 (minimal compiler + golden) → P4 (skill-creator + cert)
→ P5 (harness-cli adapter slice, bash + MCP) → P6 (harness-pipeline-author, Claude Code only)
```

First production milestone: **P0–P8 complete for `harness-pipeline-author` on both Claude Code
and GitHub Copilot.**

---

## Final gate checklist (G9)

| Gate | Required evidence |
|---|---|
| Generic harness complete | `coding-harness/.claude/` has no Harness assumptions (grep clean) |
| Contracts complete | every artifact type validates against its own schema |
| CLI first-class | adapter has manifest, schemas, fixtures, golden, **version-gate + redaction + MCP adapter**, tests |
| Skill-creator integrated | trigger + behavioral evals run through the wrapped flow |
| Security enforced | secret + mutating-command scans are certification gates |
| Claude target works | plugin installs and skill invokes |
| Copilot target works | `.github` pack validates and smoke passes |
| Certification enforced | package/release fail when evals missing/stale/below threshold |
| Distribution ready | marketplace + install pack documented and tested; **rollback tested** |
| Repeatability proven | a second capability ships without re-architecting |
| Reuse proven | a non-Harness pilot builds on the unchanged harness |

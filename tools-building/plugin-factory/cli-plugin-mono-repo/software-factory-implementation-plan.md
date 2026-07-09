# Software Factory Implementation Plan
## Validation, Enhancements, and Phased Claude Code Execution Guide
### For: Agentic Engineering Platform — Repository-Native Software Factory

Version: 1.0 · Date: 2026-07-08 · Companion to: `Architecture-design-cli` design document

---

# Part A — Architecture Validation

## A.1 Verdict

The architecture is sound and well ahead of common practice. The core thesis — *encode the engineering method into the repository so agents and humans follow the same governed pipeline (Intent → Spec → Plan → Worktree → Execution → Verification → Review → Memory → Merge)* — is the correct response to the seven risks identified (plugin drift, contract drift, knowledge loss, weak verification, context overload, etc.).

The strongest elements, which should be preserved unchanged:

1. **Tool contracts as the single source of truth** (§13) — generating MCP definitions, CLI docs, plugin skills, evals, and allowlists from one contract file is the single highest-leverage anti-drift mechanism in the design.
2. **Deterministic hooks around probabilistic agents** (§15) — the "agents are probabilistic, hooks are deterministic" framing is exactly right.
3. **Assistant-neutral `.factory/` layer** (§9) — decoupling the factory from any one vendor surface.
4. **Evidence-based completion** (§22) — "the factory should not rely on the assistant saying 'looks good'" is the correct trust model.
5. **Spec-first workflow with explicit memory-update and rollback sections** (§12).
6. **The recommended first vertical slice** (§24) — "add a new MCP tool from an existing CLI command" is genuinely the best first slice because it touches every subsystem.

However, the design has **12 gaps and structural risks** that should be corrected *before* implementation, because several of them (duplication, ceremony overload, evidence integrity) will compound if built as specified.

## A.2 Gaps, Risks, and Corrections

### G1 — The knowledge layer is specified three times (redundancy will cause drift inside the anti-drift system)

The design defines `.knowledge/okf/`, `.knowledge/graph/` (explicit nodes/edges directories), `.knowledge/memory/`, AND `.knowledge/indexes/` as separate structures. These overlap almost completely: a component appears as an OKF entity, a graph node, a semantic memory reference, and an index entry. Four copies of one fact means three of them will rot — ironically recreating the drift problem the factory exists to solve.

The actual OKF v0.1 spec (published by Google Cloud, June 12 2026) resolves this cleanly: knowledge is a directory of markdown concept files with YAML frontmatter (`type` required; `title`, `description`, `resource`, `tags`, `timestamp` optional), **markdown links between files ARE the graph edges**, `index.md` files provide progressive disclosure, and `log.md` provides chronological history. There is no separate nodes/edges structure in OKF — the filesystem plus links is the graph.

**Correction:** Collapse `.knowledge/okf/`, `.knowledge/graph/`, and `.knowledge/indexes/` into a single OKF-conformant bundle. One concept = one file. Relationships = markdown links (typed by surrounding prose, e.g., "implements [architecture_analyze](../cli-commands/architecture-analyze.md)"). Indexes = OKF `index.md` files, **generated** from frontmatter where possible, never hand-maintained in parallel with content. Keep the four memory types (semantic/episodic/procedural/working) as subdirectories of the same bundle — they are just concept categories, not a separate system.

### G2 — Harness quadruplication (`.factory/`, `.claude/`, `.github/`, `.workflows/`)

Workflows are defined in `.workflows/*.md`, `.factory/workflows/*.yaml`, `.claude/skills/`, `.claude/speckit/workflows/`, and `.github/prompts/`. Five places. The design says `.claude/` and `.github/` "can be generated or synchronized from `.factory/`" — this must be a hard requirement, not an option, and it must be verified.

**Correction:**
- Delete `.workflows/` entirely; merge into `.factory/workflows/` (YAML is the canonical form; human-readable docs are generated).
- `.claude/skills/`, `.claude/commands/`, `.github/prompts/`, `.github/skills/` are **generated artifacts** with `# GENERATED FROM .factory/... — DO NOT EDIT` headers containing the source path and content hash.
- Add a `verify-harness-sync.sh` gate that regenerates and diffs; any drift fails verification. This is Phase 1 work, not an afterthought.
- Hand-written exceptions (surface-specific nuance) live in explicit `overrides/` directories that the generator merges, so customization is still possible without breaking sync.

### G3 — Eleven gates on every change will kill throughput (ceremony overload)

§14.2 requires 11 gates for "every feature or bug fix." A one-line typo fix would need a spec, eval review, security review, docs gate, and knowledge-graph gate. Humans and agents alike will start routing around the factory, which is the failure mode that kills governance systems.

**Correction:** Introduce **change tiers**, declared in spec frontmatter and enforced by hook + CI:

| Tier | Examples | Required gates |
|------|----------|----------------|
| T1 — Trivial | typos, comments, doc wording, formatting | lint + affected tests |
| T2 — Standard | bug fix, new test, internal refactor, doc page | T1 + unit/integration + episodic memory note |
| T3 — Contract-affecting | CLI command, MCP tool, schema, plugin, runtime script | full 11-gate pipeline + spec |
| T4 — Architectural | new subsystem, ADR-level decision, release | T3 + ADR + human review required |

A deterministic classifier script (path-based rules in `.factory/change-tiers.yaml`: e.g., any diff touching `schemas/`, `tool_contracts/`, or `plugin-runtime/` auto-escalates to T3) prevents agents from self-classifying downward.

### G4 — Verification evidence can be fabricated by the agent it is meant to check

§22 evidence files are markdown reports in `.verification/reports/`. If the implementing agent *writes* those reports, the evidence is testimony, not proof — an agent under pressure to "complete" can write a plausible report without running anything.

**Correction:**
- Evidence files must be **machine-generated by the verification scripts themselves** (JSON + rendered markdown), containing: command executed, exit code, git SHA of the worktree, timestamp, duration, and a hash of the report body. Agents may *reference* reports, never author them.
- Local hooks are **advisory** (fast feedback); **CI is authoritative**: the same `.verification/scripts/` run in GitHub Actions on every PR, so guardrails cannot be bypassed by a local agent skipping a hook. This CI-parity requirement is missing from the design and must be explicit.
- The `stop-verification.sh` hook checks that a fresh (matching current SHA) report exists rather than trusting the transcript.

### G5 — Shared mutable working memory will cause constant merge conflicts

`.knowledge/memory/working/current-agent-context.md` and `active-specs.md` are single files mutated by parallel worktrees (§16.3 explicitly encourages parallel worktrees). Every merge will conflict.

**Correction:** Working memory is **per-spec**: `.specs/active/SPEC-XXXX/context.md`, `plan.md`, `progress.md` live inside the spec's own directory (one directory per spec, not one file). Repository-level views (`active-specs.md`) are **generated** indexes, never hand-edited. `current-roadmap.md` and `active-risks.md` are fine as shared files — they change rarely and deliberately.

### G6 — No staleness model: the knowledge graph will silently rot

Nothing in the design detects that `how-to-add-mcp-tool.md` was written 14 months ago and no longer matches the code. Stale procedural memory is worse than none — agents will confidently follow outdated playbooks.

**Correction:** Every concept file's frontmatter carries `timestamp` (OKF standard) plus a custom `verified: <date>` and `verifies-against: <path or contract>` field where applicable. `verify-knowledge-graph.sh` gains a staleness lint: procedural docs whose referenced paths/contracts changed after their `verified` date fail (or warn, per policy). The knowledge-curator agent's job explicitly includes re-verification, not just addition. Separate `generated/` (regenerable, never hand-edit) from `curated/` (human/agent judgment) content.

### G7 — The bootstrapping paradox is unaddressed

The factory is needed to build the factory. Phase 0–3 deliverables (ADRs, specs, verification) can't pass gates that don't exist yet.

**Correction:** Declare explicitly: **Phases 0–3 are built "bare"** with plain Claude Code sessions using the prompts in Part B of this document as the temporary harness. From Phase 4 onward, the factory must **dogfood itself** — every subsequent phase is executed *as a spec through the factory*, which doubles as the factory's own acceptance test. Phase 8 (vertical slice) is the formal graduation exam.

### G8 — Context economy is asserted but not designed

The design worries about "overloaded context" (§2, risk 6) but then creates a large `.knowledge/` tree with no rules about what each agent loads. An agent that reads all of `.knowledge/` recreates the overload.

**Correction:** Each agent definition includes an explicit **context contract**: the exact files/globs it reads on activation (e.g., cli-engineer loads `architecture-principles.md`, `cli-command-contracts.md`, the relevant procedural doc, and the active spec — nothing else). OKF `index.md` progressive disclosure is the navigation mechanism: agents read indexes first, open concepts on demand. This should be codified in `.factory/agent-registry.yaml` as a first-class field so both harness generators emit it.

### G9 — Tool contracts have no versioning or compatibility semantics

§13 defines contract structure but not evolution. When `architecture_analyze` gains a required input, what breaks — and who finds out?

**Correction:** Add to every contract: `"version": "MAJOR.MINOR.PATCH"` with semver rules (new optional input = minor; new required input, removed field, or output schema narrowing = major). `verify-tool-contracts.sh` diffs contracts against the last released snapshot in `.verification/snapshots/` and fails on undeclared breaking changes. Generated artifacts (MCP defs, plugin skills, docs) embed `source_contract` + `contract_version` + hash so drift is mechanically detectable — this operationalizes invariant #15 ("generated files must identify their source definition").

### G10 — Security architecture needs three additions

The allowlist/no-silent-install/no-`curl|bash` policies are good. Missing:
1. **Secrets policy** — hooks and verification scripts will run with developer credentials; add a policy file forbidding secrets in specs, memory, evidence, and prompts, plus a scanning gate (e.g., gitleaks) in `verify-all`.
2. **Allowlist as data, not script logic** — `command-allowlist.sh` should read `.verification/policies/command-allowlist.yaml` so both Claude and Copilot hooks (and CI) enforce the identical list from one source.
3. **Provenance for generated plugins** — since plugins are distributed artifacts, generation should emit a provenance record (source definition hash, generator version, timestamp) alongside each plugin, feeding the existing artifact-signing story.

### G11 — The factory has no metrics about itself

A self-improving factory needs to know where it hurts: which gates fail most, cycle time from spec to merge, rework rate, hook-block frequency.

**Correction:** Verification scripts append one JSON line per run to `.verification/reports/_metrics.jsonl` (gate, result, duration, SHA, tier). A tiny `factory-stats` script summarizes. Cheap to add in Phase 2, invaluable by Phase 8 for tuning gate strictness per tier.

### G12 — Claude Code and Copilot are not capability-equivalent; the generators must degrade gracefully

The two surfaces have different extension semantics (subagent orchestration, hook lifecycle events, prompt-file vs command models differ and both evolve quickly). A naive generator that assumes 1:1 mapping will produce broken Copilot artifacts.

**Correction:** Maintain `.factory/surface-capabilities.yaml` — a matrix of which factory features map to which surface feature (or "unsupported → fallback"). Generators consult it; the sync gate validates against it. Before building each harness phase, have the implementing session fetch current vendor docs (Claude Code: https://docs.claude.com/en/docs/claude-code/overview ; Copilot customization: GitHub Docs) rather than relying on training data — both products change monthly.

## A.3 Additional Enhancements (adopt if capacity allows)

- **E1 — Spec directories, not spec files.** `SPEC-YYYYMMDD-name/` containing `spec.md`, `plan.md`, `context.md`, `progress.md`, and later a symlink/pointer to its evidence directory. Lifecycle state (active/accepted/implemented/rejected) becomes frontmatter + generated index rather than physical moves, which preserves links and git history. (Physical move on archive only.)
- **E2 — Failure-first episodic memory.** `failed-approaches.md` is the highest-value memory file in the whole design; give it a strict template (context, approach, why it failed, signal to detect recurrence) and make the knowledge-curator agent write an entry on *every* reverted PR or abandoned worktree.
- **E3 — Eval taxonomy.** Distinguish product evals (does `architecture_analyze` produce correct reports?) from **factory evals** (given intent X, does the harness produce a conformant spec? Does the hook block `curl | bash`?). Factory evals are your regression suite for the harness itself — add a small set in Phase 7.
- **E4 — Human review checkpoints.** T3/T4 changes require a human approval recorded in the spec (`approved-by`, date) before merge; the factory prepares evidence, humans stay accountable. High-risk tools (§21) already require approval — extend the same mechanism.
- **E5 — Session/worktree protocol doc.** One page in procedural memory: how to start a factory session (which command, which spec), one spec per worktree, how to hand off between sessions (progress.md), how to abandon cleanly (episodic entry required).

---

# Part B — Phased Implementation Plan with Claude Code Prompts

## How to execute this plan

- **Tooling:** Claude Code with the latest Opus-class model. (Note: there is no "Opus 4.7" — as of mid-2026 the current models are Claude Opus 4.8, `claude-opus-4-8`, and Claude Sonnet 4.6, `claude-sonnet-4-6`. Use Opus for architecture/spec/review phases and complex generation; Sonnet is fine for mechanical file scaffolding. Check `https://docs.claude.com` for current model availability before starting.)
- **One phase = one git worktree = one PR.** Name worktrees `factory/phase-N-short-name`.
- **Session protocol:** paste the phase prompt as the first message; commit the design document (`Architecture-design-cli.md`) and this plan into the repo root at `docs/architecture/` first so every prompt's file references resolve.
- **Phases 0–3 run "bare"** (no harness yet — the prompt IS the harness). **Phase 4 onward must dogfood:** start each phase by creating a spec via the factory's own workflow.
- Every prompt ends with the same completion contract: run the phase's verification, show the evidence, and stop — do not proceed to the next phase.

Prompt blocks below are self-contained and copy-paste ready. Text in `{braces}` is for you to fill in.

---

## Phase 0 — Foundation Decisions (ADRs + Policies)

**Objective:** Make the architecture's principles durable and machine-referenceable before any structure exists.
**Duration estimate:** 1 session. **Tier:** T4 (but bare-bootstrapped).

**Tasks**
1. Create `docs/architecture/` and commit the design doc + this plan.
2. Write ADRs 0001–0008 (the design's five, plus three new ones from Part A).
3. Write `.factory/change-tiers.yaml` (G3) — the tier definitions and path-based escalation rules.
4. Write `.factory/surface-capabilities.yaml` (G12) — initial capability matrix, marked provisional.
5. Write the product invariants (§18) as `docs/architecture/invariants.md`, each invariant numbered and tagged with its future enforcement mechanism (hook / gate / test / instruction).

**Deliverables:** 8 ADRs, 2 policy YAMLs, invariants doc.
**Acceptance criteria:** Every ADR has Status/Context/Decision/Consequences; every invariant names an enforcement mechanism; tier rules cover every top-level directory in the target layout.

### Claude Code Prompt — Phase 0

```
You are bootstrapping the software factory for the Agentic Engineering Platform monorepo.
Read docs/architecture/Architecture-design-cli.md (the design) and
docs/architecture/software-factory-implementation-plan.md (the plan), fully, before writing anything.
This is Phase 0. The factory does not exist yet; you are operating bare.

Create the following, exactly:

1. docs/architecture/decisions/ containing ADR-0001 through ADR-0008 in standard ADR
   format (Title, Status, Date, Context, Decision, Consequences, Alternatives considered):
   - ADR-0001: CLI is the canonical runtime
   - ADR-0002: MCP is the assistant-native interface
   - ADR-0003: Domain plugins are optional capability packs
   - ADR-0004: Bootstrap runtime is centrally maintained and shared
   - ADR-0005: The software factory is repository-native
   - ADR-0006: Memory is file-native and OKF-conformant (single knowledge representation;
     markdown links are the graph — cite plan section G1)
   - ADR-0007: .factory/ is the canonical harness source; .claude/ and .github/ are
     generated artifacts verified by a sync gate (cite G2)
   - ADR-0008: Changes are tiered T1–T4 with proportional verification gates;
     tier classification is deterministic and path-based (cite G3)
   Ground each ADR in the specific sections of the design doc and plan it derives from.

2. .factory/change-tiers.yaml implementing the T1–T4 table from plan section G3:
   tier definitions, required gates per tier, and path-based auto-escalation rules
   (any diff touching schemas/, cli/src/**/tool_contracts/, plugin-runtime/,
   plugin-definitions/, or mcp-server/src/**/tools/ escalates to T3 minimum;
   .knowledge/ and docs-only changes are T1/T2). Include a comment header explaining
   how a classifier script will consume this file in Phase 2.

3. .factory/surface-capabilities.yaml: a provisional matrix mapping factory features
   (agents, skills, slash-commands, hooks by lifecycle event, MCP config, instructions)
   to their Claude Code and GitHub Copilot equivalents, with a `status` per cell:
   supported | partial | unsupported-fallback. Mark the whole file `provisional: true`
   — it will be validated against live vendor docs in Phases 4–5.

4. docs/architecture/invariants.md: the 15 invariants from design doc §18, numbered
   INV-01..INV-15, each with fields: statement, rationale (one sentence),
   enforcement (hook | verification-gate | test | instruction | generator), and
   enforcement-status: planned.

Constraints:
- Do not create any other factory directories yet.
- No placeholder/lorem content — every file must be complete and specific.
- Conventional commits, one commit per deliverable group.

When done: print a tree of everything you created, then a table of ADR → design-doc
sections it encodes. Do not proceed to Phase 1.
```

---

## Phase 1 — Factory Skeleton, Canonical Manifest, and Sync Gate

**Objective:** Create the directory skeleton with `.factory/` as canonical source and the harness generators/sync-check stubbed but real.
**Duration:** 1–2 sessions. **Tier:** T3 (bare).

**Tasks**
1. Create the corrected top-level layout: `.claude/ .github/ .factory/ .knowledge/ .specs/ .verification/` — **no `.workflows/`** (G2).
2. `.factory/factory-manifest.yaml` — declares every registry, policy, and generated target with source→target mappings.
3. Registries: `workflow-registry.yaml`, `agent-registry.yaml` (with **context-contract field per agent**, G8), `skill-registry.yaml`, `tool-contract-registry.yaml` (empty but schema'd).
4. Generators: `generate-claude-harness.py`, `generate-copilot-harness.py` — working for the trivial case (emit generated-file headers with source path + SHA-256 of source content), with `overrides/` merge support.
5. `.verification/scripts/verify-harness-sync.sh` — regenerate to temp, diff against committed, fail on drift.
6. README in each dot-directory explaining its role and its canonical-vs-generated status.

**Acceptance criteria:** `verify-harness-sync.sh` passes; deliberately editing a generated file makes it fail; every generated file carries the DO-NOT-EDIT header with hash.

### Claude Code Prompt — Phase 1

```
Phase 1 of the software factory. Read docs/architecture/Architecture-design-cli.md,
docs/architecture/software-factory-implementation-plan.md (especially sections G2, G8),
and the ADRs in docs/architecture/decisions/ before writing anything. ADR-0007 governs
this phase: .factory/ is canonical, .claude/ and .github/ are generated.

Build:

1. Directory skeleton: .factory/ .knowledge/ .specs/ .verification/ .claude/ .github/
   each with a README.md stating: purpose, canonical-vs-generated status, and what
   verification gate protects it. Do NOT create .workflows/ (deleted per G2 —
   workflows live only in .factory/workflows/).

2. .factory/factory-manifest.yaml — the root manifest: lists all registries, all
   policies, and a `generated_targets` section mapping .factory sources to .claude/
   and .github/ outputs (e.g. .factory/agents/*.yaml -> .claude/agents/*.md and
   .github/agents/*.agent.md).

3. Registries with documented YAML schemas (as comments) and one worked example entry each:
   - agent-registry.yaml: fields = id, role, description (written to trigger correct
     delegation), context_contract (explicit list of file globs this agent reads on
     activation — per plan G8), tools_allowed, surfaces [claude, copilot, both]
   - skill-registry.yaml: id, description, workflow_ref, surfaces
   - workflow-registry.yaml: id, tier, steps, gates_required (referencing
     .factory/change-tiers.yaml tiers)
   - tool-contract-registry.yaml: empty list + schema comment (populated Phase 6)

4. .factory/generators/generate-claude-harness.py and generate-copilot-harness.py:
   Python 3.11+, stdlib + pyyaml only. For now they must correctly generate agent files
   from agent-registry.yaml for both surfaces. Every generated file starts with:
   # GENERATED FROM {source_path} (sha256:{source_hash}) — DO NOT EDIT. Edit source and regenerate.
   Support .factory/overrides/{surface}/{filename} merge: if an override exists,
   append its content under a marked OVERRIDE section. Idempotent: running twice
   produces byte-identical output.

5. .verification/scripts/verify-harness-sync.sh: regenerates both harnesses into a
   temp dir, diffs against the committed .claude/ and .github/ generated files,
   exits nonzero with a readable diff on drift. Also verifies every generated file's
   embedded source hash still matches its source.

6. Run the generators for the example agent, commit the generated output, run
   verify-harness-sync.sh and show it passing. Then temporarily hand-edit one
   generated file, show the gate failing, revert.

Constraints: no other verification scripts yet; no knowledge content yet; scripts must
be shellcheck-clean and py files pass `python -m py_compile`.

When done: print the tree, the passing + failing gate output, and stop.
```

---

## Phase 2 — Verification Harness Core (moved earlier than the design's Phase 7)

**Objective:** Deterministic verification and tamper-resistant evidence exist *before* agents start producing changes. (Rationale: G4, G7 — gates must precede the things they gate.)
**Duration:** 2 sessions. **Tier:** T3 (bare).

**Tasks**
1. `.verification/` full skeleton: `gates/ scripts/ policies/ fixtures/ snapshots/ reports/`.
2. `verify-all.sh` orchestrator: runs registered gates for the change's tier (reads `.factory/change-tiers.yaml`), continues past failures, aggregates.
3. Evidence engine (G4): a shared `lib/evidence.sh` (or small Python module) used by every gate script to emit `reports/<SPEC-or-branch>/<gate>.json` + `.md` containing command, exit code, git SHA, timestamp, duration, and body hash. Agents never write these.
4. Tier classifier: `scripts/classify-change.sh` — diffs against base branch, applies path rules, prints tier.
5. Policies as data (G10): `policies/command-allowlist.yaml`, `no-silent-install.yaml`, `secrets-policy.yaml`; a generic `scripts/check-policy.sh` interpreter; secrets scan wired into verify-all.
6. Metrics (G11): every gate appends one line to `reports/_metrics.jsonl`; add `scripts/factory-stats.sh`.
7. Stub gates that will be filled later (`verify-cli.sh`, `verify-mcp.sh`, etc.) exit 0 with an explicit `SKIPPED — not yet implemented (Phase N)` evidence record, so the pipeline shape is complete from day one.

**Acceptance criteria:** `verify-all.sh` runs end-to-end on the current repo; evidence files are machine-generated and hash-stamped; classifier returns correct tiers on three synthetic diffs; allowlist policy blocks a fixture containing `curl | bash`.

### Claude Code Prompt — Phase 2

```
Phase 2: build the deterministic verification harness. Read the design doc §14, §15,
§22 and plan sections G3, G4, G10, G11 first. Key principle (G4): evidence is produced
by scripts, never authored by agents; local runs are advisory, CI will be authoritative.

Build in .verification/:

1. lib/evidence.sh — sourced by every gate. Function evidence_emit that writes
   reports/${FACTORY_CHANGE_ID:-$(git branch --show-current)}/<gate>.json and .md with:
   gate id, command, exit_code, git_sha, timestamp (ISO 8601), duration_ms,
   body sha256. Also appends {gate, result, duration_ms, sha, tier, ts} as one line
   to reports/_metrics.jsonl.

2. scripts/classify-change.sh — computes changed paths vs ${BASE_REF:-main}, applies
   .factory/change-tiers.yaml rules, prints T1|T2|T3|T4. Include unit-style tests
   using three fixture diffs under fixtures/classifier/.

3. policies/ as machine-readable data: command-allowlist.yaml (allow common git,
   python, pytest, node, npm test-type commands; deny rm -rf outside worktree,
   curl|bash and wget|sh pipes, sudo, package installs unless flagged),
   secrets-policy.yaml, no-silent-install.yaml. scripts/check-policy.sh takes a
   policy file + a text/diff input and enforces it. Add a secrets scan step
   (use gitleaks if available in the environment, else a regex-based fallback that
   the script documents as weaker).

4. scripts/verify-all.sh — determines tier via classify-change.sh (overridable with
   --tier), looks up required gates from .factory/change-tiers.yaml, runs each gate
   script, never stops on first failure, prints a summary table, exits nonzero if any
   required gate failed. Every gate emits evidence via lib/evidence.sh.

5. Real gates now: verify-harness-sync.sh (exists — wire it in), check-policy runs,
   secrets scan, and a docs-link checker (broken relative links in docs/ and
   .knowledge/). Stub gates with SKIPPED evidence for: verify-cli, verify-mcp,
   verify-plugin-runtime, verify-tool-contracts, verify-schemas, verify-evals,
   verify-copilot-plugins, verify-claude-plugins, verify-knowledge-graph — each stub
   states which phase implements it.

6. scripts/factory-stats.sh — summarizes _metrics.jsonl: runs per gate, failure rate,
   p50 duration.

7. .github/workflows/factory-verify.yml — CI parity (G4): checks out, runs
   scripts/verify-all.sh with BASE_REF=origin/main, uploads reports/ as an artifact.

Demonstrate: run verify-all.sh, show the summary and one evidence JSON; run the
classifier on the three fixtures; show the allowlist blocking a curl|bash fixture.
All shell must pass shellcheck. Stop when done.
```

---

## Phase 3 — Knowledge Base and Memory (OKF-conformant, consolidated)

**Objective:** One knowledge representation (per G1), seeded with real content, with staleness protection (G6) and per-spec working memory (G5).
**Duration:** 2 sessions. **Tier:** T2/T3 (bare).

**Tasks**
1. `.knowledge/` as a single OKF v0.1 bundle: root `index.md` (with `okf_version: "0.1"` frontmatter) and `log.md`; subdirectories `memory/semantic/`, `memory/episodic/`, `memory/procedural/`, `components/`, `contracts/`, `decisions/` (concept stubs linking to the real ADRs), `glossary/`. **No** `okf/`, `graph/`, or hand-maintained `indexes/` directories.
2. Seed semantic memory: architecture-principles, platform-glossary, tool-contract-principles, plugin-design-principles, verification-principles — real content derived from the design doc and ADRs, cross-linked.
3. Seed procedural memory: how-to-add-cli-command, how-to-add-mcp-tool, how-to-add-domain-plugin, how-to-run-verification, how-to-update-memory, plus the session/worktree protocol (E5).
4. Seed episodic memory: `failed-approaches.md` with the strict template (E2) and release/bugfix history stubs.
5. Frontmatter convention: OKF fields + `verified:` and `verifies-against:` (G6).
6. `verify-knowledge-graph.sh` (replacing the Phase 2 stub): OKF conformance lint (frontmatter valid, `type` present, no reserved filenames misused), broken-link check, staleness check, and generated-index freshness check.
7. `scripts/generate-knowledge-indexes.py` in `.factory/generators/`: builds `index.md` files from frontmatter.

**Acceptance criteria:** bundle passes its own gate; deliberately breaking a link or backdating a `verified` field fails the gate; an agent can navigate from root `index.md` to any concept in ≤3 hops.

### Claude Code Prompt — Phase 3

```
Phase 3: build the knowledge base. Read design doc §10–§11, plan sections G1, G5, G6,
E2, E5, and ADR-0006. Critical consolidation decision (G1/ADR-0006): there is exactly
ONE knowledge representation — an OKF v0.1 bundle. No .knowledge/okf/, no
.knowledge/graph/ nodes-and-edges directories, no hand-written indexes. Markdown links
between concept files ARE the graph. Before starting, fetch and skim the OKF v0.1 spec:
https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
and conform to it (frontmatter fields, index.md rules, log.md, reserved filenames).

Build:

1. .knowledge/ as an OKF bundle: root index.md (frontmatter okf_version: "0.1"),
   root log.md, and subdirectories: memory/semantic/, memory/episodic/,
   memory/procedural/, components/, contracts/, glossary/, decisions/.
   decisions/ contains one thin concept file per ADR that links to the authoritative
   docs/architecture/decisions/ file (do not duplicate ADR content).

2. Frontmatter convention for every concept: type, title, description, tags,
   timestamp (OKF) plus custom fields verified: <ISO date> and, where the concept
   describes code or a contract, verifies-against: <repo path>. Document this
   convention in .knowledge/memory/semantic/knowledge-conventions.md.

3. Seed REAL content (no placeholders), derived from the design doc + ADRs, densely
   cross-linked:
   - semantic: architecture-principles.md, platform-glossary.md,
     tool-contract-principles.md, plugin-design-principles.md,
     verification-principles.md, knowledge-conventions.md
   - procedural: how-to-add-cli-command.md, how-to-add-mcp-tool.md,
     how-to-add-domain-plugin.md, how-to-run-verification.md,
     how-to-update-memory.md, session-and-worktree-protocol.md (per plan E5:
     one spec per worktree, per-spec working memory lives in the spec directory
     per G5, abandonment requires a failed-approaches entry)
   - episodic: failed-approaches.md using this strict per-entry template:
     ## <date> <short title> / Context / Approach / Why it failed /
     Recurrence signal / Superseded by. Seed with one real entry: the design doc's
     own G1 redundancy (three knowledge representations) as a rejected approach.
     Plus bugfix-history.md and release-history.md as headed empty logs.

4. .factory/generators/generate-knowledge-indexes.py — regenerates every index.md
   from directory contents + frontmatter (title - description bullets, grouped by
   type), conforming to OKF index rules. Idempotent.

5. Replace the Phase 2 stub: .verification/scripts/verify-knowledge-graph.sh with:
   (a) frontmatter/OKF conformance lint, (b) broken relative-link check,
   (c) staleness check — if a concept has verifies-against and that path's last
   commit is newer than the concept's verified date, warn (T1/T2) or fail (T3/T4),
   (d) index freshness — regenerate indexes to temp and diff.

6. Demonstrate the gate passing, then failing on (i) a broken link and (ii) a stale
   verified date, then revert.

Update root log.md with this phase's entry. Run verify-all.sh and show the summary.
Stop when done.
```

---

## Phase 4 — Spec Kit

**Objective:** Specs become the mandatory front door; per-spec directories carry working memory (G5, E1). From this phase on, the factory dogfoods itself.
**Duration:** 1 session. **Tier:** T3.

**Tasks**
1. `.specs/` with `templates/` and lifecycle directories; spec = directory (E1) containing `spec.md` (frontmatter: id, title, tier, status, approved-by, dates), `plan.md`, `context.md`, `progress.md`.
2. Templates: feature, bugfix, cli-command, mcp-tool, plugin, schema-change, verification, release — each embedding the design doc's 10-section template (§12.2) plus tier declaration and context-contract section.
3. `verify-specs.sh` gate: frontmatter valid, tier matches classifier output for the branch, required sections present, T3+ requires approved-by before status may move to accepted.
4. Generated `.specs/active/index.md`.
5. **Dogfood:** create `SPEC-<date>-spec-kit` retroactively describing this phase itself and drive it to `implemented`.

### Claude Code Prompt — Phase 4

```
Phase 4: build the specification kit. Read design doc §12, plan sections G3, G5, E1,
E4, and .knowledge/memory/procedural/session-and-worktree-protocol.md.

Build:

1. .specs/ with templates/, active/, accepted/, implemented/, rejected/, archived/.
   A spec is a DIRECTORY: SPEC-YYYYMMDD-short-name/ containing spec.md, plan.md,
   context.md (working memory for this change — per G5 this replaces any shared
   current-agent-context file), progress.md (session handoff log).

2. spec.md frontmatter: id, title, tier (T1–T4), status
   (draft|active|accepted|implemented|rejected|archived), created, updated,
   approved_by (required before status accepted when tier is T3/T4 — per plan E4),
   affected_contracts: []. Body follows design doc §12.2's ten sections, plus:
   §11 Context Contract — the exact knowledge files agents should load for this work.

3. Templates in .specs/templates/ for: feature, bugfix, cli-command, mcp-tool,
   plugin, schema-change, verification, release — each pre-fills the sections that
   differ (e.g. mcp-tool template includes the tool-contract checklist referencing
   .knowledge/memory/procedural/how-to-add-mcp-tool.md).

4. .verification/scripts/verify-specs.sh (new required gate for T2+): validates
   frontmatter schema; validates that the spec's declared tier >= the tier
   classify-change.sh computes for the branch; checks required sections exist and
   are non-empty for the tier; enforces approved_by for T3/T4 acceptance.
   Wire into .factory/change-tiers.yaml gate lists.

5. Generated index: extend generate-knowledge-indexes.py or add a sibling to emit
   .specs/active/index.md from spec frontmatter. Never hand-edited.

6. DOGFOOD: create .specs/implemented/SPEC-{today}-spec-kit/ documenting this very
   phase (retroactive but complete — real acceptance criteria, real verification
   evidence paths), demonstrating the format.

Run verify-all.sh, show verify-specs passing, update .knowledge log.md and
episodic memory (how-to-update-memory applies to you too). Stop when done.
```

---

## Phase 5 — Claude Code Harness

**Objective:** The full `.claude/` surface — agents, skills, commands, hooks — generated from `.factory/`, with hooks enforcing the invariants.
**Duration:** 2–3 sessions. **Tier:** T3. **Dogfooded via spec.**

**Tasks**
1. Populate `.factory/agents/` with all 13 role definitions (§16.1), each with description-for-delegation, context contract (G8), allowed tools, and surface mapping.
2. Populate `.factory/skills/` sources for: add-cli-command, add-mcp-tool, add-domain-plugin, update-bootstrap-runtime, generate-evals, update-knowledge-graph, release-platform.
3. Extend generators to emit `.claude/agents/`, `.claude/skills/`, `.claude/commands/` (factory-plan/implement/verify/review/memory-update/release) and `CLAUDE.md` (from a `.factory/templates/claude-md.tmpl` + invariants file — CLAUDE.md itself is generated).
4. Hooks (`.claude/hooks/`): PreToolUse command guard reading the shared allowlist YAML (G10), PostToolUse post-edit-verify (runs targeted gates for touched paths), Stop hook requiring fresh evidence for the current SHA (G4), memory-update suggester.
5. `settings.json` + `mcp.json` scaffolding.
6. Validate against live docs (G12): fetch current Claude Code docs for hooks/skills/subagents schemas before generating.

### Claude Code Prompt — Phase 5

```
Phase 5: build the Claude Code harness. This phase MUST be dogfooded: first create
.specs/active/SPEC-{today}-claude-harness/ from the feature template, fill it
genuinely (tier T3, affected contracts: harness sync), get it to accepted
(approved_by: {your name}), THEN implement.

Before implementing, verify current Claude Code extension schemas against live docs —
fetch https://docs.claude.com/en/docs/claude-code/overview and follow links for
subagents, skills, hooks, slash commands, and settings. Where the live schema differs
from the design doc's assumptions, follow the live schema and record the difference in
.factory/surface-capabilities.yaml (removing provisional flags for cells you verify).

Then read design doc §7, §15, §16, §19 and plan G2, G4, G8, G10, G12.

Build (sources in .factory/, generated output in .claude/ — never hand-edit .claude/):

1. .factory/agents/: all 13 agents from design §16.1 (platform-architect, spec-owner,
   cli-engineer, mcp-tool-engineer, plugin-engineer, claude-plugin-engineer,
   copilot-plugin-engineer, bootstrap-runtime-engineer, verification-engineer,
   security-engineer, release-engineer, documentation-engineer, knowledge-curator).
   Each source YAML has: id, delegation description (specific enough that Claude
   Code's automatic delegation triggers correctly), context_contract (exact
   .knowledge/ files it loads — keep each under ~6 files, navigate via index.md for
   more), tools_allowed, surface notes. knowledge-curator's definition must include
   the E2 rule: every reverted/abandoned change gets a failed-approaches entry, and
   re-verifying stale concepts is part of its job, not just adding new ones.

2. .factory/skills/: sources for add-cli-command, add-mcp-tool, add-domain-plugin,
   update-bootstrap-runtime, generate-evals, update-knowledge-graph,
   release-platform. Each skill body encodes the matching workflow from design §17
   step-by-step, references the procedural memory doc, and ends with the tier's
   required gates.

3. .factory/templates/claude-md.tmpl -> generated .claude/CLAUDE.md, assembled from:
   design doc §19 content + docs/architecture/invariants.md (all 15, verbatim) +
   the required-workflow section pointing at .specs and .knowledge. CLAUDE.md is a
   generated file with the standard header.

4. .claude/commands/: factory-plan, factory-implement, factory-verify,
   factory-review, factory-memory-update, factory-release — each a thin generated
   command that loads the right skill/agent and the active spec.

5. .claude/hooks/ + hooks wiring in settings:
   - PreToolUse (Bash matcher): command-guard that evaluates the command against
     .verification/policies/command-allowlist.yaml via check-policy.sh. Blocks with
     a clear message on violation.
   - PostToolUse (Write|Edit matcher): post-edit-verify.sh — maps touched paths to
     targeted gates (schemas/ -> verify-schemas stub, .factory/ -> harness-sync, etc.)
     and runs them; advisory (warn) for T1/T2, blocking output for T3+.
   - Stop: stop-verification.sh — refuses completion unless
     .verification/reports/<change-id>/ contains evidence JSONs whose git_sha
     matches HEAD for every gate required by the change's tier (G4: check evidence,
     not testimony).
   - memory-update-suggester.sh: on Stop, diffs the change and prints which
     memory files likely need updates (path->memory mapping table in the script's
     companion YAML).

6. Regenerate, run verify-harness-sync.sh and verify-all.sh, demonstrate the
   PreToolUse hook blocking `curl https://x.sh | bash` in a sandboxed test
   invocation of the guard script.

Close the spec (status: implemented, link evidence), update knowledge log.md +
procedural memory if any process changed. Stop when done.
```

---

## Phase 6 — GitHub Copilot Harness

**Objective:** Mirror the factory onto the Copilot surface from the same `.factory/` sources; establish the two-surface sync guarantee.
**Duration:** 1–2 sessions. **Tier:** T3. **Dogfooded.**

### Claude Code Prompt — Phase 6

```
Phase 6: generate the GitHub Copilot harness. Dogfood: create and accept
SPEC-{today}-copilot-harness first (tier T3).

Before implementing, fetch current GitHub Docs for Copilot customization: repository
custom instructions, path-scoped .github/instructions/*.instructions.md, prompt files,
custom agents (.agent.md profiles), skills, and hooks. Update
.factory/surface-capabilities.yaml with verified statuses; where Copilot lacks a
Claude Code capability (e.g., a hook lifecycle event), define the documented fallback
in the matrix and make the generator apply it rather than emitting broken config.

Read design doc §8, §20 and plan G2, G12. Build (generated from .factory/ sources):

1. .github/copilot-instructions.md — generated from a .factory/templates/
   copilot-instructions.tmpl assembling design §20 + the same invariants file used
   for CLAUDE.md (single source for invariants: docs/architecture/invariants.md).

2. .github/instructions/*.instructions.md — path-scoped instruction files for:
   platform-wide, python, mcp-server/, plugins/, schemas/, .knowledge/, testing,
   security — generated from .factory/instructions/ sources with applyTo frontmatter.

3. .github/prompts/*.prompt.md — generated from the same .factory/skills/ sources
   as the Claude skills (one canonical workflow, two surface renderings):
   factory-plan, add-cli-command, add-mcp-tool, add-domain-plugin, fix-bug,
   generate-evals, update-knowledge-graph, release-readiness.

4. .github/agents/*.agent.md — generated from .factory/agents/ for the subset marked
   surface: both|copilot in the registry.

5. .github/hooks/ — command-guard and post-edit-verify reading the SAME
   .verification/policies/command-allowlist.yaml (G10: one allowlist, three
   consumers: Claude hook, Copilot hook, CI). Plus audit-log.sh appending tool-call
   records to .verification/reports/_audit.jsonl.

6. Extend .github/workflows/factory-verify.yml if needed so CI runs
   verify-harness-sync.sh (now covering both surfaces) — CI remains authoritative.

Regenerate everything, run verify-all.sh, close the spec, update memory. Stop.
```

---

## Phase 7 — Tool Contract Registry and Codegen

**Objective:** The anti-drift keystone: versioned contracts that generate MCP definitions, plugin skill references, docs, and eval scaffolds. Includes factory evals (E3).
**Duration:** 2 sessions. **Tier:** T3. **Dogfooded.**

### Claude Code Prompt — Phase 7

```
Phase 7: tool contract registry and code generation. Dogfood via
SPEC-{today}-tool-contracts (tier T3 — this touches contract paths, the classifier
should agree). Read design doc §13, §21 and plan G9, E3, plus
.knowledge/memory/semantic/tool-contract-principles.md.

Build:

1. cli/src/agentic_tool/tool_contracts/ + a JSON Schema for contracts themselves:
   schemas/tool-contract.schema.json. Contract fields per design §13.2 PLUS (per G9):
   version (semver), stability (experimental|stable|deprecated), and risk_class
   (read-only | state-changing | high-risk per design §21; high-risk requires
   explicit human approval metadata when invoked by the factory).

2. Author the first two real contracts: architecture_analyze (design §13.2, extended
   with the new fields, version 1.0.0) and dependency_map.

3. .factory/generators/generate-from-contracts.py producing, per contract:
   - mcp-server/src/agentic_tool_mcp/tools/<name>.generated.json (MCP tool def)
   - docs/reference/tools/<name>.md (human docs)
   - .knowledge/contracts/<name>.md (OKF concept: frontmatter
     verifies-against: the contract path, links to component concepts)
   - evals/tools/<name>/eval-scaffold.yaml
   All with generated headers embedding source_contract, contract version, and hash.

4. .verification/scripts/verify-tool-contracts.sh (replace stub):
   (a) every contract validates against tool-contract.schema.json;
   (b) semver compatibility: diff each contract against
       .verification/snapshots/tool-contracts/<name>.json — new required input,
       removed field, or output-schema narrowing without a MAJOR bump fails;
   (c) generated artifacts are fresh (regenerate-and-diff) and their embedded hashes
       match sources;
   (d) registry .factory/tool-contract-registry.yaml lists every contract on disk.
   Provide scripts/snapshot-contracts.sh to update snapshots deliberately (T3 action).

5. Factory evals (plan E3) under .verification/evals/factory/: at least three
   executable checks — (i) the command-guard blocks each denied pattern fixture,
   (ii) classify-change.sh returns T3 for a synthetic contract-touching diff,
   (iii) a malformed contract fails the schema gate. Wire into verify-all for T3+.

Run verify-all.sh, demonstrate the semver gate failing on a synthetic breaking change
(then revert), close the spec, update memory (contracts concepts + log.md). Stop.
```

---

## Phase 8 — Graduation: the First End-to-End Vertical Slice

**Objective:** Prove the factory by running the design doc's recommended first slice — "expose an existing CLI command as an MCP tool" — entirely through the factory, producing merge-ready change + evidence. This is the acceptance test for Phases 0–7.
**Duration:** 1–2 sessions. **Tier:** T3.

### Claude Code Prompt — Phase 8

```
Phase 8 is a graduation exercise: do NOT build factory infrastructure. Instead, USE
the factory end-to-end for one real change, exactly as design doc §24 recommends:
expose the architecture_analyze CLI capability as an MCP tool, end to end.

Follow the factory's own front door:
1. /factory-plan (or the spec-owner flow): create SPEC-{today}-mcp-architecture-analyze
   from the mcp-tool template. Consult .knowledge procedural memory
   (how-to-add-mcp-tool) and semantic memory per the spec's context contract.
2. Get the spec to accepted (tier T3, approved_by recorded).
3. Implement in this worktree: MCP server adapter wired to the generated tool
   definition from Phase 7; input mapping to CLI args per the contract's cli_mapping;
   output validated against the contract's output schema; tests for the adapter;
   fill the eval scaffold with at least two real eval cases.
4. Run verification: verify-all.sh must pass with REAL (non-stub) results for:
   tool-contracts, harness-sync, specs, knowledge-graph, policies — plus the new
   MCP adapter tests. Replace the verify-mcp.sh stub with a real gate that runs the
   adapter tests and schema validation (this is the one piece of infrastructure this
   phase may build, because the slice requires it).
5. Memory update: knowledge-curator duties — new/updated concepts for the MCP tool,
   episodic log entry, procedural doc corrections if reality diverged from the
   how-to (it will; fixing the how-to is the point).
6. Produce the evidence: .verification/reports/SPEC-.../ populated by the gates,
   evidence git_sha matching HEAD.

Deliverable: a merge-ready branch + a short RETROSPECTIVE.md in the spec directory:
what the factory made easy, where it fought you, and concrete follow-up items filed
as one-line entries in .knowledge/memory/working/ (roadmap). Every friction point is
a factory bug — record all of them honestly. Stop when done.
```


---

## Phase 9 — Plugin Generation Factory

**Objective:** Copilot and Claude Code plugin variants generated from shared `plugin-definitions/*.yaml`, with provenance (G10) and drift gates (invariant #14).
**Duration:** 2–3 sessions. **Tier:** T3. **Dogfooded.**

### Claude Code Prompt — Phase 9

```
Phase 9: the plugin generation factory. Dogfood via SPEC-{today}-plugin-generation
(tier T3). Read design doc §5 (plugin-definitions/, plugins/, plugin-runtime/), §17.3,
§18 invariants 3–10 and 14–15, and plan G10.

Build:

1. plugin-definitions/architecture.yaml as the first real definition: metadata,
   skills exposed (referencing tool contracts by name+version), agents included,
   MCP tool subset, runtime scripts required. Define
   schemas/plugin-definition.schema.json for it.

2. tools/generate-plugins/ — generator that, from one definition, emits BOTH
   plugins/copilot/<name>/ and plugins/claude-code/<name>/:
   - manifests per each surface's current plugin format (fetch live vendor docs
     first; update .factory/surface-capabilities.yaml with what you verify)
   - skill/instruction files rendered from the same .factory/skills sources,
     referencing tool contracts — skills must call plugin-runtime wrapper scripts,
     never raw commands (invariant INV-10; add a lint for this)
   - plugin-runtime/ scripts copied in (bootstrap-cli.sh, check-cli.sh,
     invoke-cli.sh, mcp-wrapper.sh) — creating minimal working versions of these
     scripts if they don't exist yet, honoring INV-07 (plugin-managed install
     disabled by default) and INV-08 (trusted sources only)
   - PROVENANCE.json per generated plugin: source definition path + hash,
     generator version, timestamp, contract versions consumed (per G10, feeding
     the future signing story)

3. Replace stubs: verify-plugin-runtime.sh (shellcheck + smoke tests of the wrapper
   scripts with a fake CLI on PATH), verify-copilot-plugins.sh and
   verify-claude-plugins.sh (manifest schema validation + regenerate-and-diff drift
   check + the raw-command lint + provenance hash check). Cross-surface drift check:
   both variants must declare the same skill set and tool versions (INV-14).

4. plugin-catalog/: generated catalog entry + compatibility matrix row per plugin
   (CLI version range, contract versions).

5. Bootstrap-runtime coupling rule (design §17.5): add to post-edit-verify's path map —
   any change under plugin-runtime/ triggers regeneration of ALL plugins and the
   plugin gates.

Run verify-all.sh, demonstrate the drift gate catching a hand-edit to a generated
plugin file (then revert), close the spec, update memory (components/ concepts for
the plugin subsystem). Stop.
```

---

## Phase 10 — Memory Automation, Metrics, and Hardening

**Objective:** Close the loop: memory updates become enforced-by-gate, factory metrics become visible, and CI/security hardening lands.
**Duration:** 1–2 sessions. **Tier:** T2/T3. **Dogfooded.**

### Claude Code Prompt — Phase 10

```
Phase 10: memory automation and factory hardening. Dogfood via
SPEC-{today}-memory-automation. Read design doc Phase 9 goals (§23) and plan
G4, G6, G11.

Build:

1. Memory-gate enforcement: extend verify-knowledge-graph.sh so that for T2+ changes,
   if the diff touches paths mapped to memory targets (use the same path->memory
   mapping YAML the suggester hook uses) and no corresponding .knowledge/ file
   changed in the branch, the gate fails with the specific expected targets listed.
   T1 exempt. Escape hatch: spec frontmatter memory_exempt: <reason> — but the
   verify-specs gate requires the reason to be non-empty and it is surfaced in the
   PR summary.

2. Staleness sweep automation: a scheduled GitHub Actions workflow (weekly) running
   the staleness check across all of .knowledge/ and opening/updating a single
   tracking issue listing stale concepts, assigned to the knowledge-curator role.

3. Metrics maturation (G11): factory-stats.sh gains --since and --by-tier;
   add a CI step that comments a one-table gate summary + tier + durations on each
   PR from the evidence JSONs (evidence-to-PR-comment renderer).

4. Hardening:
   - gitleaks (or documented fallback) as a required gate for all tiers
   - .verification/policies/hook-integrity: verify-all checks that hook scripts and
     the allowlist YAML are unchanged relative to main unless the spec declares
     affected_contracts: [factory-policy] (prevents an agent quietly editing its
     own guardrails — this closes the remaining G4 loophole)
   - audit log rotation for _audit.jsonl and _metrics.jsonl

5. Retrospective actions: read .specs/**/RETROSPECTIVE.md from Phase 8 and the
   working-memory roadmap entries; implement the top 3 friction fixes if they are
   T1/T2-sized, otherwise file them as draft specs.

Run verify-all.sh, close the spec, update memory. Stop.
```

---

## Phase 11 — Release Factory

**Objective:** Productized, evidence-backed releases of CLI + MCP server + runtime + plugins + catalog + docs together.
**Duration:** 2 sessions. **Tier:** T4. **Dogfooded; human approval required.**

### Claude Code Prompt — Phase 11

```
Phase 11: the release factory. Dogfood via SPEC-{today}-release-factory, tier T4 —
this spec requires human approved_by before acceptance; pause and ask for it.
Read design doc §23 Phase 10, §21 (high-risk tools), §22.2, and plan E4, G9, G10.

Build:

1. .factory/release-policy.yaml: version scheme, what releases together (CLI, MCP
   server, plugin-runtime, all plugins, catalog, docs — design's success criteria),
   compatibility-matrix update rules, and the release gate list (full T4 pipeline +
   release-readiness).

2. .verification/scripts/verify-release-readiness.sh: all T4 gates green on the
   release SHA; every tool contract snapshot matches (no undeclared breaking
   changes since last release — G9); compatibility matrix rows exist for every
   plugin; CHANGELOG section for the version exists; provenance files present for
   all generated plugins; zero stale T3-relevant knowledge concepts.

3. .github/workflows/release-platform.yml: tag-triggered; runs
   verify-release-readiness; builds artifacts; generates release notes from
   accepted/implemented specs since the last tag (spec frontmatter is the release-
   notes database); publishes catalog updates; records the release in
   .knowledge/memory/episodic/release-history.md via an automated commit.
   Mark artifact signing as an explicit step with a TODO gate if signing
   infrastructure isn't available yet — the gate must FAIL-VISIBLE (skipped-with-
   warning in the evidence), never silently pass.

4. .factory/skills/release-platform source updated to the real procedure; regenerate
   both harnesses; a release runbook in procedural memory
   (how-to-release-platform.md) with verified: set today.

5. Dry run: execute verify-release-readiness.sh against HEAD and produce the
   evidence report, demonstrating what a release candidate check looks like.

Close the spec, update memory, print the final factory state: tree of all dot-
directories, gate list per tier, and the current factory-stats summary. Stop.
```

---

# Part C — Execution Guidance and Reference

## C.1 Sequencing summary

| Phase | Name | Mode | Depends on | Est. sessions |
|---|---|---|---|---|
| 0 | ADRs + tier/capability policies | bare | — | 1 |
| 1 | Skeleton + manifest + sync gate | bare | 0 | 1–2 |
| 2 | Verification core + evidence engine | bare | 1 | 2 |
| 3 | Knowledge base (OKF) | bare | 2 | 2 |
| 4 | Spec kit | dogfood begins | 3 | 1 |
| 5 | Claude Code harness | dogfood | 4 | 2–3 |
| 6 | Copilot harness | dogfood | 5 | 1–2 |
| 7 | Tool contracts + codegen + factory evals | dogfood | 5 | 2 |
| 8 | **Graduation vertical slice** | pure use | 7 | 1–2 |
| 9 | Plugin generation factory | dogfood | 8 | 2–3 |
| 10 | Memory automation + hardening | dogfood | 9 | 1–2 |
| 11 | Release factory | dogfood, human-approved | 10 | 2 |

Total: roughly 18–24 working sessions. Phases 5↔6 and 7 can partially parallelize across worktrees once Phase 4 lands; nothing else should run in parallel until Phase 8 has validated the pipeline.

## C.2 Model and session guidance

- **Opus-class model** (currently `claude-opus-4-8`; verify the latest at docs.claude.com) for Phases 0, 3, 5, 7, 8, 11 — these require judgment, synthesis, and live-doc reconciliation.
- **Sonnet-class** is acceptable for the mechanical middles of Phases 1, 2, 6, 9 once the pattern is established in the same phase by Opus.
- Keep sessions scoped to one phase (or one numbered deliverable within a phase for the larger ones). Use each spec's `progress.md` for handoff between sessions — that is the working-memory design working as intended.
- If a session's context grows unwieldy, stop, write `progress.md`, and start fresh: the factory's whole premise is that repository state, not chat history, is the memory.

## C.3 Standing constraints (apply to every prompt above)

1. Never hand-edit generated files (`.claude/`, `.github/` generated artifacts, indexes, plugin outputs) — edit the `.factory/` source and regenerate.
2. Every phase ends with `verify-all.sh` output shown and evidence committed.
3. Every phase updates `.knowledge/log.md`; T2+ phases update the relevant memory type.
4. Fetch live vendor documentation before implementing against Claude Code, Copilot, or OKF specifics; record verified facts in `surface-capabilities.yaml`.
5. When reality contradicts the design doc or this plan, the implementing session must record the contradiction in `failed-approaches.md` or as a spec-level decision — never silently deviate.

## C.4 Definition of done for the whole program

The factory is complete when a fresh Claude Code session, given only the prompt *"Add a new observability assessment capability to the platform"* (design doc §25), autonomously: creates a conformant spec, loads the right memory via context contracts, implements across CLI/contract/MCP/plugin layers in a worktree, passes all T3 gates with machine-generated evidence at the HEAD SHA, updates the knowledge bundle, and presents a merge-ready PR with human-approval checkpoints where the tier requires them — while the hooks demonstrably block every denied command pattern along the way.

# Project: Skill & Plugin Factory (harnesspf-team)

A software factory that authors one canonical Agent Skill per capability and compiles it to
**Claude Code** (plugin) and **GitHub Copilot** (`.github` bundle) targets, gated by evals and
architecture-conformance, wrapping the **custom Harness CLI** as a first-class participant.

## Single source of truth
- **The plan:** `docs/design-and-implementation-plan.md` (the merged v2 plan) — build strictly to
  this. Part I is the design; Part II is the phased plan (Phases **P0–P10**). Do not invent
  structure that contradicts it.
- Implement **one phase at a time**, in order. A later phase may not start until the prior
  phase's acceptance criteria are green (see the dependency map at the end of the plan).

## Governing architecture documents (conformance is a BLOCKER, not a suggestion)
- `docs/reference/claude-code-customization-architecture-revised.md` — governs **every** Claude
  Code artifact, including the generic `.claude/` coding harness.
- `docs/reference/ghcopilot-customization-arch.md` — governs **every** GitHub Copilot artifact.
- Any emitted artifact that violates its governing document is a build failure to fix, not ship.
- `docs/reference/harness-skill-factory.original.md` is the **superseded** original design, kept
  for context only. The plan supersedes it.

## Repository layout (read carefully)
- **`coding-harness/.claude/`** — the generic Layer-1 coding harness (the plan's "harness/").
  Domain-free; reusable for any project.
- **`coding-harness/.claude/skills/skill-creator/`** — the **official Anthropic skill-creator**
  skill, bundled into the harness. You stage it at `docs/reference/skill-creator/`; Phase 1
  installs and pins it (version/source in `docs/PINS.md`). It is generic and pinned; **do not
  modify it** — the certification flow depends on its pinned version.
- **`factory-core/`** — the generic Python engine (contracts, compilers, validators, evals,
  cli_adapters, authoring).
- **`domains/harness/`** — ALL Harness specifics (integration manifest, CLI integration with the
  bash wrappers + MCP adapter, capability sources, distribution).
- **`dist/`** — generated build output.

This layout has no name collision; do not place Harness artifacts anywhere under
`coding-harness/` or `factory-core/`.

## Golden rules
- **`dist/` is generated, never hand-edited.** Humans touch `domains/`, `coding-harness/`, and
  `factory-core/`; the build owns `dist/`. A hand-edit shows up as a `.factory-manifest.json` hash
  mismatch.
- **Layer 1 is domain-free.** Nothing under `coding-harness/.claude/` (or `factory-core/`) may
  reference Harness.io domain tokens (`harness-cli`, `cli_surface`, `HARNESS_`, `Harness.io`) —
  **except the bundled `skills/skill-creator/`**, which is generic and may use "harness" as a
  common noun. All Harness specifics live in `domains/harness/`.
- **Every artifact type validates against its own schema.** No global catch-all contract.
- **Safety first for the CLI.** Bash wrappers and the MCP adapter run `--dry-run` by default,
  honor `HARNESS_CLI_PROFILE=sandbox`, **gate on CLI version**, and **redact secrets/IDs from CLI
  output** before it enters context. Evals never touch production Harness.
- **No secrets in artifacts.** CLI auth flows through plugin `userConfig`→keychain (Claude Code)
  and `${HARNESS_API_TOKEN}` env (both hosts). Never hard-code tokens or endpoints.
- **Conformance + eval + security are gates.** `build`/`package`/`release` are fail-closed if the
  conformance, eval, or certification artifact is missing, stale, or below threshold. The security
  scan (secret + mutating-command) is part of certification.
- **skill-creator certification is non-negotiable** before any marketplace target.

## Workflow per phase
1. Start in **plan mode**. Read the phase in `docs/design-and-implementation-plan.md` and the
   relevant governing doc. Propose the file-by-file plan for THIS phase only.
2. After approval, implement the phase's ordered sub-tasks exactly.
3. Self-check against the phase's acceptance-criteria table; report pass/fail per row.
4. Stop and summarize. Do not begin the next phase until told.

## Build commands
See `AGENTS.md`. The `justfile` and Python tooling are created in **Phase 0/1**. Until then,
there are no build commands to run.

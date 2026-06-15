# AGENTS.md — Build & Conventions

This repository is built **phase by phase** per `docs/design-and-implementation-plan.md` (the
merged v2 plan). Tooling (`Makefile`, `pyproject.toml`) is created in **Phase 0/1**; before that
there are no build commands.

## Once Phase 0/1 exists, the operator surface is `make`:
`make` passes the capability/target as variables: `NAME=<capability>`, `DOMAIN=<domain>`,
`TARGET=<claude-code|copilot>`, `SANDBOX=1`. All command targets are `.PHONY`.
- Scaffold a capability:   `make new-capability DOMAIN=<domain> NAME=<name>`
- Research intent:         `make research NAME=<name>`   (human signs off capability.yaml)
- Author the skill:        `make author NAME=<name>`
- Validate:                `make validate TARGET=<target>` (hard fail)
- Conformance check:       `make conform TARGET=<target>`   (hard fail — blocker, vs governing docs)
- Evals:                   `make eval TARGET=<target> SANDBOX=1` (hard fail below threshold)
- Certify (+ security):    `make certify TARGET=<target>`   (security scan + cert record; fail-closed)
- Build targets:           `make build TARGET=<target>`
- Package:                 `make package TARGET=<target>`
- Full local pipeline:     `make ship TARGET=<target>`      (validate→eval→build→certify→package)
- Release (all):           `make release`
- CLI adapter checks:      `make validate-cli-adapter NAME=<name>` · `make test-cli-adapter NAME=<name>`

## Conventions
- Language for factory tooling: **Python** (uv/poetry), package `factory_core`.
- Layout: **monorepo, trunk-based**.
- **skill-creator is bundled** in `coding-harness/.claude/skills/skill-creator/` (the official
  Anthropic skill, operator-provided, pinned via `docs/PINS.md`). Never modify it; certification
  depends on its pinned version.
- Generation is **human-in-the-loop with hard eval gates** — never fully autonomous to a
  marketplace.
- Commit per completed phase (and per green gate within a phase). Use conventional commits.
- Never commit secrets. CLI auth is env/keychain only.

## Before committing
1. Run `make validate TARGET=<target>` and `make conform TARGET=<target>` — both must pass (conformance is
   checked against the governing architecture docs).
2. For capabilities, run `make eval TARGET=<target> SANDBOX=1` then `make certify TARGET=<target>` — evals must
   meet thresholds and the security scan (secret + mutating-command) must be clean.
3. Confirm `dist/` has no hand-edits (`.factory-manifest.json` hash check).

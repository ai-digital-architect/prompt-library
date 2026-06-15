# AGENTS.md — Build & Conventions

This repository is built **phase by phase** per `docs/design-and-implementation-plan.md` (the
merged v2 plan). Tooling (`justfile`, `pyproject.toml`) is created in **Phase 0/1**; before that
there are no build commands.

## Once Phase 0/1 exists, the operator surface is `just`:
- Scaffold a capability:   `just new-capability <domain> <name>`
- Research intent:         `just research <name>`   (human signs off capability.yaml)
- Author the skill:        `just author <name>`
- Validate:                `just validate <target>` (hard fail)
- Conformance check:       `just conform <target>`   (hard fail — blocker, vs governing docs)
- Evals:                   `just eval <target> --sandbox` (hard fail below threshold)
- Certify (+ security):    `just certify <target>`   (security scan + cert record; fail-closed)
- Build targets:           `just build <target>`
- Package:                 `just package <target>`
- Full local pipeline:     `just ship <target>`      (validate→eval→build→certify→package)
- Release (all):           `just release`
- CLI adapter checks:      `just validate-cli-adapter <name>` · `just test-cli-adapter <name>`

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
1. Run `just validate <target>` and `just conform <target>` — both must pass (conformance is
   checked against the governing architecture docs).
2. For capabilities, run `just eval <target> --sandbox` then `just certify <target>` — evals must
   meet thresholds and the security scan (secret + mutating-command) must be clean.
3. Confirm `dist/` has no hand-edits (`.factory-manifest.json` hash check).

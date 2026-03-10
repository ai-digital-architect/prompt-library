# AI Customization Scaffold — Architecture Analysis & Script Design
#### March 2026

---

## Architecture Analysis

### Structural Comparison

The two systems are philosophically aligned but differ in their primary environment and granularity model.

**GitHub Copilot** is IDE-first and uses a *description-matching* activation model — the model reads skill/agent descriptions and decides what to load. This means precision of language in `description` fields directly controls token cost and correctness. The handoff mechanism is unique: a deterministic UI button that keeps humans in the loop between pipeline stages. Skills use a three-tier progressive disclosure (metadata always-on → body on match → references on demand), which is elegant for cost control.

**Claude Code** is terminal-first and uses a *directory-scoped* activation model — files load based on where Claude is operating in the filesystem. Sub-directory `CLAUDE.md` files are a key cost-control mechanism unavailable in Copilot. The hook system is more granular (tool-level interception via stdin/stdout JSON protocol vs. event-level in Copilot), making it more suitable for fine-grained security enforcement. There's no handoff concept — the equivalent is slash commands with explicit user invocation.

### Key Structural Differences That Affect Scaffolding

| Concern | Copilot | Claude Code | Scaffolding Implication |
|---|---|---|---|
| Primary config file | `.github/copilot-instructions.md` | `CLAUDE.md` at project root | Two separate root files to generate |
| Agent definitions | `.github/agents/*.agent.md` | `.claude/agents/*.md` | Different frontmatter schemas |
| Skills/Commands | `.github/skills/*/SKILL.md` | `.claude/commands/*.md` | Copilot skills are richer (references/, scripts/) |
| Hook config location | `.vscode/settings.json` | `.claude/settings.json` | Different JSON schemas |
| Hook interception | `permissions.allowedCommands` | Exit code 2 + stdin/stdout JSON | Hook scripts need two implementations |
| Sub-agent isolation | Single-level, no history inheritance | Same, plus `permissionMode` and `bypassPermissions` | Claude Code needs more frontmatter fields |
| Secrets handling | Not addressed at platform level | `${ENV_VAR}` references in settings.json | Claude scripts need .gitignore generation |

### What the Scripts Need to Do

There are two distinct modes:

**Mode 1 — Scaffold (empty project):** Pure template generation. Takes a platform flag and optional project-type hints. Produces the full directory structure with sensible defaults and `# TODO` markers where project-specific content is required.

**Mode 2 — Analyze + Scaffold (existing repo):** Reads the repository, infers the tech stack, frameworks, test setup, CI/CD patterns, directory structure conventions, and existing anti-patterns, then generates customization files that are actually populated with real content rather than placeholders.

---

## Script Architecture Design

The right implementation language is **Python** — it handles file scanning, JSON/YAML manipulation, and template rendering cleanly, runs everywhere without build steps, and has no dependencies beyond stdlib for the core logic (with optional `jinja2` for templates).

### Directory Structure

```
ai-scaffold/
├── scaffold.py                    # CLI entry point
├── analyzers/
│   ├── stack.py                   # Language, framework, package manager detection
│   ├── patterns.py                # Directory conventions, naming patterns
│   ├── tests.py                   # Test framework, coverage setup
│   ├── database.py                # ORM/migration tool detection
│   └── ci.py                      # GitHub Actions / CI detection
├── generators/
│   ├── claude_code.py             # Generates Claude Code structure
│   ├── github_copilot.py          # Generates GitHub Copilot structure
│   └── common.py                  # Shared template rendering
├── templates/
│   ├── claude/
│   │   ├── CLAUDE.md.tmpl
│   │   ├── settings.json.tmpl
│   │   ├── agents/
│   │   │   ├── researcher.md.tmpl
│   │   │   ├── code-reviewer.md.tmpl
│   │   │   ├── security-auditor.md.tmpl
│   │   │   └── implementer.md.tmpl
│   │   ├── commands/
│   │   │   ├── plan-feature.md.tmpl
│   │   │   ├── generate-endpoint.md.tmpl
│   │   │   └── full-feature.md.tmpl
│   │   └── hooks/
│   │       ├── validate-bash.sh.tmpl
│   │       ├── auto-format.sh.tmpl
│   │       └── notify-complete.sh.tmpl
│   └── copilot/
│       ├── copilot-instructions.md.tmpl
│       ├── AGENTS.md.tmpl
│       ├── agents/
│       │   ├── planner.agent.md.tmpl
│       │   ├── implementer.agent.md.tmpl
│       │   └── reviewer.agent.md.tmpl
│       └── skills/
│           ├── code-review/SKILL.md.tmpl
│           └── ci-debugging/SKILL.md.tmpl
└── README.md
```

---

## The Analysis Pipeline

The `analyzers/` layer is the core of Mode 2. Each analyzer returns a structured `StackContext` dict that all generators consume.

### `stack.py` — Language and Framework Detection

- Scan file extensions across the repo to determine primary languages and their proportions
- Parse `package.json` → extract `dependencies` and `devDependencies` to identify React/Vue/Next/Fastify/Express etc.
- Parse `pyproject.toml` / `requirements.txt` for FastAPI/Django/Flask/SQLAlchemy
- Check for `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`
- Detect package manager: presence of `pnpm-lock.yaml` vs `yarn.lock` vs `package-lock.json`
- Detect monorepo: presence of `packages/` or `apps/` with multiple `package.json` files, or `nx.json` / `turbo.json`

### `patterns.py` — Architectural Conventions

- Walk the top-level directory structure; map folder names to roles (`src/`, `backend/`, `frontend/`, `api/`, `lib/`, `services/`, `repositories/`, `handlers/`, `routes/`)
- Infer layered architecture (routes → services → repositories pattern) vs flat structure
- Detect whether tests are co-located (`*.test.ts` next to source) or in a separate `tests/` tree
- Sample 10–20 source files to detect naming conventions (camelCase, snake_case, PascalCase)
- Check for existing `README.md` — extract tech stack section if present

### `tests.py` — Test Framework Detection

- JS: presence of `vitest`, `jest`, `@testing-library/*`, `cypress`, `playwright` in `devDependencies`
- Python: `pytest` in requirements, presence of `conftest.py`, `pytest.ini`, `pyproject.toml [tool.pytest]`
- Check for coverage config (`.nycrc`, `c8`, `coverage.py`)
- Detect integration test patterns (separate `tests/integration/` vs unit-only)

### `database.py` — ORM and Migration Detection

- JS: `drizzle-orm`, `prisma`, `typeorm`, `sequelize`, `knex` in dependencies
- Look for migration directories: `migrations/`, `db/migrations/`, `drizzle/`
- Python: `alembic`, `sqlalchemy`, presence of `alembic.ini`
- Detect database type from connection strings in `.env.example` or config files

### `ci.py` — CI/CD Detection

- Read `.github/workflows/*.yml` files
- Extract job names, step commands to understand the CI pipeline (build → test → lint → deploy sequence)
- Detect deployment targets (Vercel, AWS, GCP, Docker)
- Note existing linting tools (ESLint, Prettier, Ruff, Black, golangci-lint)

---

## The `StackContext` Output

All analyzers populate a shared context object that generators use for template rendering:

```python
{
  "languages": {"typescript": 0.72, "python": 0.28},
  "primary_language": "typescript",
  "package_manager": "pnpm",
  "frameworks": {
    "frontend": "next",
    "backend": "fastify",
    "testing": ["vitest", "playwright"],
    "orm": "drizzle"
  },
  "architecture": {
    "type": "fullstack_monorepo",
    "layers": ["routes", "services", "repositories"],
    "test_colocation": True,
    "naming_convention": "camelCase"
  },
  "database": {
    "orm": "drizzle",
    "migrations_dir": "drizzle/",
    "db_type": "postgres"
  },
  "ci": {
    "provider": "github_actions",
    "steps": ["install", "lint", "test", "build"],
    "deploy_target": "vercel"
  },
  "linters": ["eslint", "prettier", "ruff"],
  "build_commands": {
    "install": "pnpm install",
    "build": "pnpm build",
    "test": "pnpm test",
    "lint": "pnpm lint:fix"
  }
}
```

---

## Generator Logic

### `claude_code.py`

Uses the context to produce:

- `CLAUDE.md` populated with the real tech stack, actual build commands, detected conventions, and inferred anti-patterns (e.g. if `moment` is absent from deps, no need to warn about it; if `express` is absent but `fastify` is present, add the "use Fastify not Express" rule)
- `settings.json` with `permissions.allow` patterns pre-populated for the detected test/lint commands, and `permissions.deny` with the standard dangerous patterns
- Agent definitions with `description` fields tailored to the stack (the researcher agent for a Python project mentions FastAPI route patterns; for a Next.js project it mentions App Router conventions)
- Hook scripts with the detected formatters pre-wired (the auto-format hook switches on `.ts` → prettier, `.py` → ruff, etc.)
- Slash commands that reference the real commands (the `generate-endpoint` command uses the detected layer structure)
- Sub-directory `CLAUDE.md` files for each detected major subdirectory (`src/`, `backend/`, etc.) with module-specific content
- A `.gitignore` addition for `.claude/CLAUDE.md` and `.claude/settings.local.json`

### `github_copilot.py`

Uses the same context to produce:

- `.github/copilot-instructions.md` with the 5–15 rules pattern, populated with real stack rules
- `AGENTS.md` with the actual build/test/lint commands
- `CLAUDE.md` at the repo root with model-specific guidance
- Path-specific instruction files: `typescript.instructions.md` with `applyTo: "**/*.ts"`, `python.instructions.md` with `applyTo: "**/*.py"`, etc. — only generated for languages detected in the repo
- Agent definitions for planner/implementer/reviewer with handoff wiring
- Skill definitions for detected workflows — if database migrations are detected, generate the `db-migration` skill with the real migration command; if CI is complex, generate the `ci-debugging` skill

---

## CLI Interface

```
Usage: python scaffold.py [OPTIONS] [REPO_PATH]

Options:
  --platform [claude|copilot|both]  Target platform (default: both)
  --mode [scaffold|analyze]         scaffold = empty templates,
                                    analyze = repo-aware generation (default: scaffold)
  --dry-run                         Print what would be created without writing
  --output PATH                     Output directory (default: REPO_PATH or cwd)
  --overwrite                       Overwrite existing files (default: skip with warning)
  --no-hooks                        Skip hook script generation
  --no-agents                       Skip agent definition generation

Examples:
  python scaffold.py --platform both --mode scaffold ./my-new-project
  python scaffold.py --platform claude --mode analyze ./my-existing-repo
  python scaffold.py --mode analyze --dry-run .
```

---

## Complexity and Effort Estimates

| Component | Complexity | Notes |
|---|---|---|
| Stack detection | Medium | Package file parsing is reliable; extension scanning handles edge cases |
| Pattern detection | Medium-High | Directory heuristics require tuning; false positives for unconventional projects |
| Template system | Low | Stdlib `string.Template` sufficient; jinja2 optional for conditionals |
| Claude Code generator | Medium | More frontmatter fields; settings.json schema is non-trivial |
| Copilot generator | Medium | Skill three-tier structure requires more output files |
| Hook script generation | Low | Shell script templates are straightforward |
| CLI wiring | Low | argparse handles it |
| Edge case handling | High | Monorepos, polyglot projects, unusual structures |

**Total estimate:** ~800–1,200 lines of Python across all files, plus templates. Realistically a 2–3 day solo effort to get to a reliable MVP that handles the common cases (Node/TS + Python projects covering ~80% of real repositories).

---

## The One Hard Problem

The trickiest part is generating useful `description` fields for agents and skills. These are the highest-leverage content in both architectures — they control what gets loaded and when. A generic description produces generic behavior; a project-specific one is dramatically more useful.

The solution for Mode 2 is to use the `StackContext` to inject specific, concrete trigger phrases. For example, the code-reviewer description for a Drizzle+Fastify project should say *"Reviews TypeScript code using Fastify and Drizzle ORM patterns"* and list specific things to check (N+1 queries in Drizzle, missing Fastify schema validation, etc.) rather than the generic version. This requires maintaining a library of framework-specific review criteria in the templates — which is the most domain-knowledge-intensive part of the whole system.

# `toolsmith` — Shell Build Specification

> **Audience:** Claude Code, as an implementing agent.
> **Goal:** Build `toolsmith` as a Bash CLI that helps developers design, validate, and run tools for coding agents.
> **Deliverable:** A single-file installable Bash script (`toolsmith`) with supporting library files and a man page.

If any requirement here conflicts with what you find during implementation, stop and surface the conflict before diverging.

---

## 1. Product Overview

`toolsmith` is a Bash 4+ command-line tool for developers writing tools that coding agents (Claude Code, MCP clients) will consume. It treats tool definitions as **JSON files with sibling handler scripts**, which is the most natural fit for a shell environment. It provides scaffolding, linting, token budgeting, a test runner, and an agent-evaluation harness — all using standard Unix plumbing (`jq`, `curl`, `bash`).

This is the right shape when your tools are thin wrappers over Unix commands, existing binaries, or REST endpoints. It is **not** the right shape if you need a full MCP server or complex schema composition — see §2.2.

---

## 2. Goals, Non-Goals, and Honest Limitations

### 2.1 Goals

- Zero runtime dependencies beyond `bash 4+`, `jq`, `curl`. Ship as a single file installable with `curl | bash`.
- Fast: `lint` and `tokens` finish in under 2s for 20 tools.
- POSIX-friendly where possible, but GNU-ish tools are acceptable (`sed -E`, `readlink -f`).
- All output human-readable by default; `--json` for machine consumption.
- Exit codes: `0` success, `1` validation failure, `2` user error, `3` internal error.

### 2.2 Non-Goals (important)

- **No built-in MCP server.** Implementing JSON-RPC-over-stdio correctly in Bash is a poor use of effort. Instead, `toolsmith` provides a `run` subcommand that executes a single tool with JSON stdin → JSON stdout. Users who need MCP wrap this in a small adapter (we provide one in `contrib/` as a Python starter).
- No in-process schema composition. Schemas are authored as hand-written JSON Schema files.
- No watch mode.
- No automatic handler generation.

### 2.3 Known tradeoffs vs. the TypeScript/Python versions

| Concern | Shell approach | Cost |
|---|---|---|
| Token counting | Calls Anthropic `count_tokens` endpoint (network required) | Slower; requires `ANTHROPIC_API_KEY` for any `tokens` command |
| Schema validation | Via `jq`-based walker + optional `ajv-cli` if present | Weaker type coverage than Pydantic/zod |
| MCP server | Not provided | Users must wrap `run` in an external adapter |
| Complex eval logic | `curl` + `jq` loops | Verbose; harder to debug than a native SDK |

Accept these tradeoffs knowingly.

---

## 3. Dependencies

### Required on the user's machine

- `bash >= 4.0` (for associative arrays).
- `jq >= 1.6`.
- `curl`.
- `sed`, `awk`, `grep`, `find` (GNU or BSD — any differences isolated in `lib/compat.sh`).

### Optional but detected

- `shellcheck` — if present, used to lint handler scripts.
- `ajv` (npm `ajv-cli`) — if present, used for stricter JSON Schema validation.
- `python3` — only needed by users who install the `contrib/mcp-adapter.py` bridge.

The script checks for required dependencies on first run and exits with a clear message if anything is missing.

---

## 4. Project Layout

```
toolsmith/
├── bin/
│   └── toolsmith                 # Main entry point (Bash script, chmod +x)
├── lib/
│   ├── compat.sh                 # Portability shims (GNU vs BSD)
│   ├── log.sh                    # Colored logging, JSON output
│   ├── error.sh                  # Structured error reporting
│   ├── config.sh                 # Load toolsmith.conf
│   ├── loader.sh                 # Discover and parse tool JSON files
│   ├── lint/
│   │   ├── naming.sh             # TS001–TS099
│   │   ├── schema.sh             # TS100–TS199
│   │   ├── description.sh        # TS200–TS299
│   │   └── response.sh           # TS300–TS399
│   ├── tokens.sh                 # Token counting via API
│   ├── run.sh                    # Single-tool executor
│   ├── eval.sh                   # Agent loop for evaluation
│   └── improve.sh                # Claude-assisted improvement
├── templates/
│   ├── tool.json.tmpl
│   ├── handler.sh.tmpl
│   └── project/
│       ├── toolsmith.conf.tmpl
│       ├── tools/example_ping.json.tmpl
│       ├── tools/example_ping.handler.tmpl
│       ├── evals/example.json.tmpl
│       └── README.md.tmpl
├── contrib/
│   └── mcp-adapter.py            # Starter: wraps `toolsmith run` as MCP
├── tests/
│   ├── run-tests.sh              # Test harness
│   ├── lint.test.sh
│   ├── tokens.test.sh
│   ├── loader.test.sh
│   └── fixtures/
│       └── tools/
├── docs/
│   └── commands/
├── install.sh                    # Single-file installer
├── Makefile                      # build, test, install targets
└── README.md
```

### Single-file distribution

`make build` concatenates `bin/toolsmith` with every file under `lib/` (in deterministic order) into `dist/toolsmith` — one executable file. Users install with:

```bash
curl -fsSL https://example.com/install.sh | bash
```

which downloads `dist/toolsmith` and `templates/` to `~/.local/bin` and `~/.local/share/toolsmith/`.

---

## 5. Tool Definition Format

### 5.1 File convention

Each tool consists of two files in the `tools/` directory:

```
tools/
├── repo_symbols_find.json       # Definition
└── repo_symbols_find.handler    # Executable; any language
```

The handler is executable (`chmod +x`), reads a single JSON object from stdin, and writes a single JSON value to stdout. Errors go to stderr; non-zero exit marks failure.

### 5.2 JSON definition schema

```json
{
  "name": "repo_symbols_find",
  "description": "Locate definitions of a function, class, type, or variable.\n\nUse when: the agent needs to find where something is defined.\nDo NOT use when: searching for references — use repo_symbols_refs.",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Exact symbol name. Case-sensitive."
      },
      "kind": {
        "type": "string",
        "enum": ["function", "class", "type", "variable"],
        "description": "Optional filter by symbol kind."
      },
      "response_format": {
        "type": "string",
        "enum": ["concise", "detailed"],
        "default": "concise",
        "description": "'concise' returns path and line only."
      }
    },
    "required": ["name"]
  },
  "handler": "./repo_symbols_find.handler",
  "meta": {
    "namespace": "repo",
    "version": "0.1.0",
    "tags": ["search"]
  }
}
```

The `handler` path is relative to the JSON file.

### 5.3 Handler contract

```bash
#!/usr/bin/env bash
# Handler reads stdin (JSON), writes stdout (JSON), exit 0 on success.
input=$(cat)
name=$(echo "$input" | jq -r '.name')
# ... do the work ...
jq -n --arg path "$found_path" --argjson line "$line" \
  '{path: $path, line: $line}'
```

Handlers can be any language — the convention is just stdin/stdout/JSON.

### 5.4 Config file

`toolsmith.conf` at project root, sourced by Bash:

```bash
# Shell variable format
TOOLS_DIR="tools"
EVALS_DIR="evals"
MODEL="claude-opus-4-7"
RESPONSE_TOKEN_LIMIT=25000

# Severity overrides: TS<id>=<off|info|warn|error>
LINT_TS003="off"
LINT_TS105="warn"
```

---

## 6. Command Reference

Common flags for every command: `--json`, `--cwd <dir>`, `--debug`, `--help`, `--version`.

### 6.1 `toolsmith init [dir]`

Copy `templates/project/` into `dir` (default `.`), expanding `.tmpl` files. Refuse to overwrite unless `--force`.

### 6.2 `toolsmith new <tool-name>`

Create `tools/<name>.json` and `tools/<name>.handler` from templates. Validate the name matches `^[a-z][a-z0-9_]+$` and contains an underscore. Make the handler executable.

Flags: `--description <str>`, `--force`.

### 6.3 `toolsmith lint [path]`

Run every enabled rule across every `*.json` in `path` (default `$TOOLS_DIR`). Output as in the Python/TS specs:

```
tools/repo_symbols_find.json
  ✖  TS201  Description is missing a "Do NOT use when" section
  ⚠  TS103  Parameter `q` lacks a description

1 problem (1 error, 1 warning) in 1 file
```

Flags: `--rule <id>`, `--fix` (limited: handler exec bit, trailing newlines).

Implementation: each rule is a Bash function under `lib/lint/*.sh` named `rule_TS<id>()`. The linter iterates registered rules and collects diagnostics into a temp file, then renders them.

Exit `1` if any error-severity problem is found.

### 6.4 `toolsmith tokens [path]`

Count tokens of each tool's `name + description + input_schema` via Anthropic's `count_tokens` endpoint. Caches results in `.toolsmith/tokens-cache.json` keyed by content hash to avoid repeated API calls.

Output:

```
Tool                    Name  Desc  Schema   Total
repo_symbols_find          4   187      91     282
--------------------------------------------------
Total                      4   187      91     282
```

Flags: `--response <file>`, `--model <id>`, `--fail-over <n>`, `--no-cache`.

Requires `ANTHROPIC_API_KEY` in env.

### 6.5 `toolsmith run <tool-name>`

Execute one tool. Reads JSON input from stdin, validates against the tool's `input_schema` (via `jq` walker; stricter if `ajv` is installed), executes the handler, truncates the result if it exceeds `RESPONSE_TOKEN_LIMIT`, writes the result to stdout.

```bash
echo '{"name": "ConfigParser"}' | toolsmith run repo_symbols_find
```

On validation failure, exits `1` and prints a structured error (see §9) without invoking the handler.

### 6.6 `toolsmith eval <task-file>`

Run an agent loop against the loaded tools. The task file is JSON:

```json
{
  "tasks": [
    {
      "id": "find-parser-symbol",
      "prompt": "Where is ConfigParser defined?",
      "expected_tools": ["repo_symbols_find"],
      "verifier": { "type": "contains", "value": "src/config/parser" }
    }
  ]
}
```

Implementation approach:

1. Build the `tools` parameter for the Anthropic API from the tool definitions.
2. POST to `https://api.anthropic.com/v1/messages` via `curl`, capture response.
3. Parse response content blocks with `jq`. If there's a `tool_use` block: invoke the matching handler via `run`, construct a `tool_result`, append to messages, POST again.
4. Loop up to `MAX_ITERATIONS=25` or until `stop_reason == "end_turn"`.
5. Run the verifier against the final assistant text.
6. Log every request/response to `evals/runs/<timestamp>/<task-id>.json`.

Verifier types: `contains`, `regex`, `tool_called`, `llm_judge` (which makes an additional API call with a rubric).

Flags: `--filter <pattern>`, `--concurrency <n>` (via `xargs -P`), `--max-iterations <n>`.

### 6.7 `toolsmith improve <tool-name>`

Read the tool's JSON + handler, plus `toolsmith lint --json` output for that tool, plus the principles document (bundled in `templates/principles.md`). Send to Claude. Parse the response, render as a unified diff (via `diff -u`), and prompt the user to accept/reject/edit.

With `--write`, apply the diff atomically via `patch`. With `--json`, emit structured output without prompting.

---

## 7. Lint Rules

Rule IDs are identical to the TypeScript/Python specs so users can switch implementations without relearning. Severity defaults match.

### 7.1 Naming (TS001–TS099)

- **TS001** error — name matches `^[a-z][a-z0-9_]+$`.
- **TS002** error — name contains at least one `_`.
- **TS003** warn — name starts with a verb or registered prefix.
- **TS004** error — no duplicate tool names.
- **TS005** warn — no two names within Levenshtein distance 2 (computed in Bash with a small function in `lib/lint/naming.sh`).

### 7.2 Schema (TS100–TS199)

- **TS100** error — `input_schema.type == "object"`.
- **TS101** error — every property has `description`.
- **TS102** warn — no generic names (`user`, `id`, `data`, `input`, `value`).
- **TS103** warn — short-enum strings declare `enum`.
- **TS104** warn — schema depth ≤ 3 (computed via recursive `jq` walk).
- **TS105** info — expose `response_format` for structured outputs.
- **TS106** warn — tool that may return many results exposes `max_results`/`limit`/`cursor`/`offset`/`filter`.

### 7.3 Description (TS200–TS299)

- **TS200** error — description ≥ 40 characters.
- **TS201** warn — description contains a "Use when" / "Do NOT use" disambiguation (regex match, case-insensitive).
- **TS202** warn — description token estimate ≤ 400 (estimate via `chars / 4` if offline; exact via API if `--online`).
- **TS203** info — description mentions return shape.

### 7.4 Response (TS300–TS399)

Applied when a sample response file exists at `tools/<name>.sample.json`:

- **TS300** error — sample ≤ `RESPONSE_TOKEN_LIMIT`.
- **TS301** warn — sample doesn't contain UUID-like strings (regex `[0-9a-f]{8}-[0-9a-f]{4}-`).
- **TS302** warn — error-shaped samples (containing an `error` key) include words like "try", "use", "pass", or a parameter name.

### 7.5 Handler rules (TS400–TS499, shell-specific)

- **TS400** error — handler path referenced in JSON exists and is executable.
- **TS401** warn — handler passes `shellcheck` (if installed and handler is a shell script).

---

## 8. Error Message Standards

All user-visible errors use this shape:

```
toolsmith: <short summary>
  cause: <specific cause>
  fix:   <concrete next step>
```

Implemented by `lib/error.sh` as `error_emit <summary> <cause> <fix>`. Stack traces (bash `BASH_SOURCE`/`LINENO`) suppressed unless `--debug`.

Example:

```
toolsmith: could not load tool definition
  cause: tools/repo_search.json has no `handler` field
  fix:   add "handler": "./repo_search.handler" to the JSON
```

---

## 9. Implementation Phases

Build in this order. Each ends with a green test suite and a demo-able binary.

### Phase 1 — Foundation

- [ ] Repo scaffolding, Makefile with `build`/`test`/`install`/`clean`.
- [ ] `lib/log.sh`, `lib/error.sh`, `lib/compat.sh` implemented and tested.
- [ ] `lib/config.sh` loads `toolsmith.conf` with sensible defaults.
- [ ] `lib/loader.sh` discovers `.json` files, validates minimum shape, returns a list.
- [ ] `toolsmith init`, `toolsmith new` working.

**Acceptance:** `toolsmith init demo && cd demo && toolsmith new repo_files_search` produces a valid tool file pair.

### Phase 2 — Lint and Tokens

- [ ] All TS001–TS302, TS400–TS401 rules implemented.
- [ ] `toolsmith lint` with `--json`, `--rule`, correct exit codes.
- [ ] `toolsmith tokens` with API-backed counting and content-hash cache.

**Acceptance:** `make test` passes; all fixture tools produce the expected diagnostic set.

### Phase 3 — Run

- [ ] `toolsmith run <name>` validates input, invokes handler, truncates oversize output.
- [ ] Input-validation errors returned as structured JSON when `--json`.

**Acceptance:** `echo '{"name": "X"}' | toolsmith run repo_symbols_find` works against the fixture tool.

### Phase 4 — Eval

- [ ] Task file parser (via `jq` schema check).
- [ ] Agent loop via `curl` + `jq` with retries and timeouts.
- [ ] All four verifier types working.
- [ ] Transcripts logged to `evals/runs/<timestamp>/`.

**Acceptance:** Bundled example eval runs to completion and produces deterministic pass/fail output.

### Phase 5 — Improve + Polish

- [ ] `toolsmith improve` with diff preview and `--write`.
- [ ] `contrib/mcp-adapter.py` documented in README.
- [ ] `make install` and `install.sh` working end-to-end.
- [ ] Man page (`toolsmith.1`) generated from a template.

**Acceptance:** `make install && toolsmith --version` works from a clean checkout. Running `improve` on a deliberately bad fixture produces a diff that, when applied, clears prior lint errors.

---

## 10. Testing Requirements

Test harness: `tests/run-tests.sh` — a simple Bash test runner (or adopt [bats-core](https://github.com/bats-core/bats-core) if you prefer; either is fine).

Coverage:

- Every lint rule: at least one passing fixture, one failing fixture.
- `loader.sh`: missing handler, bad JSON, non-executable handler, duplicate names.
- `tokens.sh`: mocked `curl` returning fixed counts; verifies caching.
- `run.sh`: valid call, invalid call, handler non-zero exit, oversize output triggers truncation.
- `eval.sh`: with a mocked Anthropic API (via a local HTTP server started by the test harness).
- CLI: spawn `toolsmith` via subshell; assert stdout, stderr, exit code.

All API-calling tests must use a mock HTTP server; no network in CI.

---

## 11. Acceptance Criteria

Done when:

- [ ] `make build && make test && make install` succeeds on a clean clone on Linux and macOS.
- [ ] `toolsmith --help` lists all seven subcommands.
- [ ] All phase acceptance checks pass.
- [ ] Self-lint: running `toolsmith lint` on the bundled example tools reports zero errors.
- [ ] No `set -x` leaked in shipped code; no unquoted variable expansions flagged by `shellcheck -S warning` on every `lib/*.sh` file.
- [ ] Every documented exit code is reachable and correct.

---

## 12. Style Rules for the Implementation

- `set -euo pipefail` at the top of every script.
- `IFS=$'\n\t'` inside every function that splits input.
- Functions prefixed by module (`log_info`, `lint_run`, `loader_find`).
- No global state outside `lib/config.sh`'s loaded variables.
- Every script passes `shellcheck -S warning`.
- No process substitution where a simple pipe suffices; prefer readability over cleverness.
- Quote every variable expansion.

---

## 13. Out of Scope

- Watch mode.
- Native MCP server (use `contrib/mcp-adapter.py` instead).
- Parallel `improve` over many tools.
- Windows support (document `wsl` as the recommended path).

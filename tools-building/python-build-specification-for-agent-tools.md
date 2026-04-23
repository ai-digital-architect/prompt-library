# `toolsmith` — Python Build Specification

> **Audience:** Claude Code, as an implementing agent.
> **Goal:** Build `toolsmith` as a Python CLI that helps developers design, validate, and evaluate tools for coding agents.
> **Deliverable:** A publishable PyPI package exposing a `toolsmith` entry point, installable via `pipx`.

If any requirement here conflicts with what you find during implementation (e.g., a library API has shifted), stop and surface the conflict before diverging.

---

## 1. Product Overview

`toolsmith` is a Python 3.11+ CLI for developers writing tools that coding agents (Claude Code, MCP clients, direct API users) will consume. It operationalizes the principles in `effective-tools-spec.md`:

- **Scaffold** new tool definitions from typed templates.
- **Lint** existing tools against enumerated rules.
- **Measure** token cost of definitions and sample responses.
- **Serve** tools as a local MCP server for hands-on Claude Code testing.
- **Evaluate** tools via an agentic loop with pass/fail reporting.
- **Improve** tools by routing them through Claude with the principles spec as context.

---

## 2. Goals and Non-Goals

### Goals

- Zero-config defaults that work immediately after `toolsmith init`.
- Deterministic, reproducible lint output (exit codes, stable ordering).
- Fast: `lint` and `tokens` under 2 seconds for a 20-tool project.
- Dual output: human-readable by default, `--json` for machines.
- Offline-capable for `init`, `new`, `lint` (local estimate), `tokens` (with cached results), and `serve`.

### Non-Goals

- Not a general-purpose MCP framework. `serve` is for local testing.
- Not a unit-test replacement. `eval` targets agent-behavior regressions.
- No web UI, no GUI.

---

## 3. Tech Stack

Fixed choices.

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python ≥ 3.11 | `TypedDict` generics, better error messages, `tomllib` built-in. |
| Project manager | `uv` (with fallback to `pip`) | Fast install, reproducible lockfile, manages venv + Python versions. |
| CLI framework | `typer` | Type-hint driven, integrates naturally with Pydantic. |
| Schema validation | `pydantic` v2 | Best-in-class; generates JSON Schema for tool definitions. |
| MCP | `mcp` (official Python SDK) | Reference implementation for the protocol. |
| Anthropic API | `anthropic` (official SDK) | Mature; supports interleaved thinking and tool use. |
| Token counting | `anthropic` SDK's `count_tokens` | Accurate per-model counts; cache results locally. |
| Rich output | `rich` | Tables, colors, diffs; widely adopted in Python CLIs. |
| Testing | `pytest` + `pytest-asyncio` + `respx` | Mature; `respx` for mocking httpx used by anthropic SDK. |
| Type checking | `mypy --strict` | Enforced in CI. |
| Linting | `ruff` | Fast; covers `flake8` + `isort` + more. |
| Packaging | `hatchling` backend + `pyproject.toml` | Modern, PEP 621-compliant. |

---

## 4. Project Structure

```
toolsmith/
├── src/
│   └── toolsmith/
│       ├── __init__.py             # Re-exports: tool, Config, ToolDefinition
│       ├── __main__.py             # Entry: `python -m toolsmith`
│       ├── cli.py                  # Typer app assembly
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py
│       │   ├── new.py
│       │   ├── lint.py
│       │   ├── tokens.py
│       │   ├── serve.py
│       │   ├── eval.py
│       │   └── improve.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── tool.py             # @tool decorator, ToolDefinition model
│       │   ├── config.py           # Config model + loader
│       │   ├── loader.py           # Discovers and imports tool modules
│       │   ├── mcp_server.py       # Wraps tools as MCP server
│       │   ├── tokens.py           # Token counting with caching
│       │   ├── eval_runner.py      # Agentic eval loop
│       │   └── lint/
│       │       ├── __init__.py
│       │       ├── runner.py
│       │       ├── rule.py         # Rule protocol + registry
│       │       ├── naming.py       # TS001–TS099
│       │       ├── schema.py       # TS100–TS199
│       │       ├── description.py  # TS200–TS299
│       │       └── response.py     # TS300–TS399
│       ├── templates/
│       │   ├── tool.py.tmpl
│       │   └── project/
│       │       ├── pyproject.toml.tmpl
│       │       ├── toolsmith.toml.tmpl
│       │       ├── tools/
│       │       │   ├── __init__.py
│       │       │   └── example_ping.py.tmpl
│       │       ├── evals/example.json.tmpl
│       │       └── README.md.tmpl
│       ├── utils/
│       │   ├── logger.py
│       │   ├── errors.py           # ToolsmithError + formatter
│       │   └── fs.py
│       └── principles.md           # Bundled copy of effective-tools-spec.md
├── tests/
│   ├── conftest.py
│   ├── test_lint_rules.py
│   ├── test_tokens.py
│   ├── test_loader.py
│   ├── test_eval_runner.py
│   ├── test_cli.py
│   └── fixtures/
│       └── tools/                  # Good and bad example tools
├── pyproject.toml
├── ruff.toml
├── mypy.ini
├── .gitignore
└── README.md
```

### `pyproject.toml` essentials

```toml
[project]
name = "toolsmith"
version = "0.1.0"
description = "Build better tools for coding agents."
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12",
    "pydantic>=2.7",
    "anthropic>=0.30",
    "mcp>=1.0",
    "rich>=13.0",
    "tomli_w>=1.0",
]

[project.scripts]
toolsmith = "toolsmith.cli:app"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "mypy>=1.10",
    "ruff>=0.5",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/toolsmith"]
```

---

## 5. Tool Definition Format

### 5.1 File convention

Each tool lives in its own `.py` file under `tools/` (configurable) and exposes a top-level `tool` object via the `@tool` decorator or a direct `Tool(...)` construction:

```python
# tools/repo_symbols_find.py
from pydantic import BaseModel, Field
from typing import Literal
from toolsmith import tool


class Input(BaseModel):
    name: str = Field(..., description="Exact symbol name. Case-sensitive.")
    kind: Literal["function", "class", "type", "variable"] | None = Field(
        None, description="Optional filter by symbol kind."
    )
    response_format: Literal["concise", "detailed"] = Field(
        "concise",
        description=(
            "'concise' returns path and line only. "
            "'detailed' adds signature and module."
        ),
    )


@tool(
    name="repo_symbols_find",
    description="""
        Locate definitions of a function, class, type, or variable in
        the indexed repository.

        Use when: the agent needs to find where something is defined.
        Do NOT use when: searching for references — use repo_symbols_refs.
        Returns: list of {path, line, signature?} up to 50 matches.
    """,
    input_model=Input,
)
async def repo_symbols_find(input: Input) -> list[dict]:
    # implementation
    ...
```

### 5.2 The `@tool` decorator and `ToolDefinition`

```python
# src/toolsmith/core/tool.py
from typing import Callable, Awaitable, Generic, TypeVar
from pydantic import BaseModel

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O")

class ToolDefinition(Generic[I, O]):
    name: str
    description: str
    input_model: type[I]
    handler: Callable[[I], Awaitable[O]]
    meta: dict

    @property
    def input_schema(self) -> dict:
        """JSON Schema derived from input_model."""
        ...


def tool(
    *,
    name: str,
    description: str,
    input_model: type[BaseModel],
    meta: dict | None = None,
) -> Callable[[Callable], ToolDefinition]:
    ...
```

The decorator returns a `ToolDefinition`; the original function is preserved as the handler.

### 5.3 Config file

`toolsmith.toml` at project root:

```toml
tools_dir = "tools"
evals_dir = "evals"
model = "claude-opus-4-7"
response_token_limit = 25000

[lint.rules]
TS003 = "off"
TS105 = "warn"
```

Loaded via `tomllib` (stdlib) into a Pydantic `Config` model.

---

## 6. Command Reference

All commands accept `--json`, `--cwd <path>`, `--debug`, `--help`, `--version`.

Exit codes: `0` success, `1` validation failure, `2` user error, `3` internal.

### 6.1 `toolsmith init [dir]`

Copy `templates/project/` into `dir`. Expand `.tmpl` files. Refuse to overwrite without `--force`. Unless `--no-install`, run `uv sync` (or `pip install -e .` fallback).

**Flags:** `--force`, `--no-install`, `--py <version>`.

### 6.2 `toolsmith new <tool-name>`

Scaffold `tools/<n>.py` from the template. Validate name matches `^[a-z][a-z0-9_]+$` with at least one underscore. Reject collisions unless `--force`.

**Flags:** `--description <str>`, `--force`.

### 6.3 `toolsmith lint [path]`

Run every enabled rule over each `.py` under `path` (default: `tools_dir`).

**Human output:**

```
tools/repo_symbols_find.py
  ✖  TS201  Description is missing a "Do NOT use when" section        (line 18)
  ⚠  TS103  Parameter `q` lacks a description                         (line 9)

1 problem (1 error, 1 warning) across 1 file
```

**JSON output:**

```json
{
  "problems": [
    {
      "file": "tools/repo_symbols_find.py",
      "rule": "TS201",
      "severity": "error",
      "message": "Description is missing a 'Do NOT use when' section",
      "line": 18
    }
  ],
  "summary": { "errors": 1, "warnings": 1, "files": 1 }
}
```

**Flags:** `--rule <id>`, `--fix` (limited to whitespace, docstring normalization).

Exit `1` if any `error`-severity problem reported.

### 6.4 `toolsmith tokens [path]`

Report token cost per tool and total. Backed by `anthropic.messages.count_tokens` with a local hash-indexed cache at `.toolsmith/tokens-cache.json`.

**Output:**

```
Tool                    Name  Desc  Schema   Total
repo_symbols_find          4   187      91     282
```

**Flags:** `--response <file>`, `--model <id>`, `--fail-over <n>`, `--no-cache`.

### 6.5 `toolsmith serve`

Start a local MCP server using the `mcp` SDK. Print the `claude mcp add` command the user can copy.

```
toolsmith serving 7 tools on stdio.

To connect from Claude Code:
  claude mcp add toolsmith-dev toolsmith serve

Press Ctrl-C to stop.
```

Implementation:

1. Import tool modules, collect `ToolDefinition` objects.
2. Instantiate an `mcp.server.Server`.
3. Register each tool; on `call_tool`, validate input via the Pydantic model (raising structured MCP errors on failure), invoke the async handler, serialize the result.
4. Truncate results exceeding `response_token_limit` and append the guidance message from the principles spec §5.
5. Support stdio (default) and streamable-HTTP transports via `--transport`.

**Flags:** `--transport {stdio,http}`, `--port <n>`.

### 6.6 `toolsmith eval <task-file>`

Task file format identical to the TypeScript spec:

```json
{
  "tasks": [
    {
      "id": "find-parser-symbol",
      "prompt": "Where is the ConfigParser class defined?",
      "expected_tools": ["repo_symbols_find"],
      "verifier": { "type": "contains", "value": "src/config/parser.py" }
    }
  ]
}
```

Verifiers: `contains`, `regex`, `tool_called`, `llm_judge`.

Execution (in `core/eval_runner.py`):

```python
async def run_eval(
    tasks: list[EvalTask],
    tools: list[ToolDefinition],
    *,
    model: str,
    max_iterations: int,
    concurrency: int,
    log_dir: Path,
) -> EvalReport: ...
```

Per task:

1. Build the `tools` parameter for `client.messages.create` from each `ToolDefinition`.
2. Enable interleaved thinking (`thinking={"type": "enabled", "budget_tokens": 2000}`).
3. Loop: on `stop_reason == "tool_use"`, invoke the matching handler, append a `tool_result` content block, resend; else terminate.
4. Cap iterations at `max_iterations` (default 25). Apply per-turn timeout (30s) and retry on transient errors (3× exponential backoff).
5. Log per-task transcripts to `evals/runs/<timestamp>/<task-id>.json`.
6. Run tasks concurrently with an `asyncio.Semaphore`.

**Human output:**

```
find-parser-symbol        PASS   3 tool calls   2,104 tokens   4.1s
list-recent-commits       FAIL   1 tool call      812 tokens   1.2s
  reason: expected tool `git_log` was never called

1/2 passed · 2,916 total tokens · transcripts in evals/runs/2026-04-22T14-02
```

**Flags:** `--filter <pattern>`, `--concurrency <n>`, `--max-iterations <n>`, `--timeout <s>`.

Exit `1` if any task fails.

### 6.7 `toolsmith improve <tool-file>`

Send the tool source + its lint output + the bundled principles spec to Claude. Parse the returned suggestion as a unified diff (rendered with `rich.syntax.Syntax`), prompt accept/reject/edit. With `--write`, apply via `unidiff` and write atomically.

The prompt skeleton lives in `src/toolsmith/templates/improve_prompt.md` and follows the pattern in Appendix A of the TypeScript spec.

---

## 7. Lint Rules

Rule IDs match the TypeScript and shell specs so users can switch implementations without relearning.

### 7.1 Naming (TS001–TS099)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS001 | error | `name` matches `^[a-z][a-z0-9_]+$` | "Tool name must be lowercase snake_case." |
| TS002 | error | `name` contains at least one `_` | "Tool name must include a namespace prefix." |
| TS003 | warn  | First token is a verb or registered service prefix | "Tool name should start with a verb or service prefix." |
| TS004 | error | No two loaded tools share a `name` | "Duplicate tool name." |
| TS005 | warn  | No two names within Levenshtein distance 2 | "Tool name is too close to `<other>`." |

### 7.2 Schema (TS100–TS199)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS100 | error | Top-level input schema is an object | "Input schema must be an object (use a Pydantic model)." |
| TS101 | error | Every field has `description` (via `Field(description=...)`) | "Field `<n>` is missing a description." |
| TS102 | warn  | No generic field names (`user`, `id`, `data`, `input`, `value` standalone) | "Field `<n>` is too generic." |
| TS103 | warn  | Short-enum strings use `Literal[...]` or `Enum` | "Field `<n>` should be a Literal or Enum." |
| TS104 | warn  | Nested model depth ≤ 3 | "Input model is deeply nested; flatten where possible." |
| TS105 | info  | Exposes `response_format` when output is structured | "Consider adding `response_format`." |
| TS106 | warn  | Returns-many tools expose `max_results`/`limit`/`cursor`/`offset`/`filter` | "Tool may return large responses but has no pagination parameter." |

### 7.3 Description (TS200–TS299)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS200 | error | Description ≥ 40 chars | "Description too short." |
| TS201 | warn  | Contains "Use when" / "Do NOT use" disambiguation | "Description should disambiguate against sibling tools." |
| TS202 | warn  | Token count ≤ 400 | "Description exceeds 400 tokens." |
| TS203 | info  | Mentions return shape | "Consider describing what the tool returns." |

### 7.4 Response (TS300–TS399)

Applied when a sample exists at `tools/<n>.sample.json`:

| ID | Severity | Check |
|---|---|---|
| TS300 | error | Sample ≤ `response_token_limit`. |
| TS301 | warn  | Sample contains no UUID-shaped strings. |
| TS302 | warn  | Error-shaped samples include actionable language. |

### 7.5 Severity overrides

```toml
[lint.rules]
TS003 = "off"
TS105 = "warn"
```

Valid: `error`, `warn`, `info`, `off`.

---

## 8. Evaluation Harness Requirements

Implementation of `core/eval_runner.py`:

1. Accept fully-validated `EvalTask` objects (Pydantic-parsed from the JSON task file).
2. For each task, create a fresh `anthropic.AsyncAnthropic` client (or reuse one with proper concurrency control).
3. Build the `tools` argument from `ToolDefinition.input_schema`.
4. Enable interleaved thinking in the request.
5. Use `asyncio.Semaphore(concurrency)` to bound parallelism.
6. On each tool_use block, validate input against the tool's Pydantic model; if validation fails, return a structured tool_error result so the agent can retry.
7. On transient errors (`APIConnectionError`, `RateLimitError`, 5xx), retry up to 3 times with exponential backoff.
8. On `max_tokens` stop reason, record `iteration_failure_reason="max_tokens"` and fail the task.
9. Write per-task transcripts as JSON; include full prompt, every request/response pair, token usage, verdict.

---

## 9. MCP Server Requirements

`core/mcp_server.py`:

1. Use `mcp.server.Server` from the official SDK.
2. Translate each `ToolDefinition` into an MCP tool registration: `name`, `description`, `inputSchema` (from `input_model.model_json_schema()`).
3. On `call_tool` requests, validate with the Pydantic model first; on failure, return an MCP error with the validation detail.
4. Invoke the async handler with the validated input.
5. If the JSON-serialized result exceeds `response_token_limit`, truncate with a trailing guidance message (see principles spec §5).
6. Support both stdio and streamable HTTP transports.

---

## 10. Error Message Standards

Same three-field shape as the TypeScript and shell specs:

```
toolsmith: could not load tool module
  cause: tools/repo_search.py raised ImportError: No module named 'pydanti'
  fix:   check the import on line 3; did you mean `pydantic`?
```

Implemented via `utils/errors.py`:

```python
class ToolsmithError(Exception):
    def __init__(self, summary: str, *, cause: str, fix: str):
        self.summary = summary
        self.cause = cause
        self.fix = fix

def format_error(err: ToolsmithError) -> str: ...
```

Top-level CLI wraps every command in a try/except that catches `ToolsmithError`, formats it, and exits with the appropriate code. Uncaught exceptions print `"toolsmith: internal error"` with a pointer to `--debug`.

---

## 11. Implementation Phases

### Phase 1 — Foundation

- [ ] Project scaffolding, `pyproject.toml`, `uv` setup, `pytest` wired, `mypy --strict` clean.
- [ ] `tool` decorator and `ToolDefinition` implemented with tests.
- [ ] `core/loader.py` imports tool modules from a directory, surfaces import errors as `ToolsmithError`.
- [ ] `toolsmith init` and `toolsmith new` working end-to-end.

**Acceptance:** `toolsmith init demo && cd demo && toolsmith new repo_files_search` produces a module that imports cleanly.

### Phase 2 — Lint and Tokens

- [ ] All TS001–TS302 rules implemented with fixture tests.
- [ ] Severity overrides from config respected.
- [ ] `toolsmith lint` (human + JSON output, `--rule`, correct exit codes).
- [ ] `toolsmith tokens` with content-hash cache and API fallback.

**Acceptance:** `pytest` is green; `toolsmith lint tests/fixtures/tools` reports the expected diagnostic set.

### Phase 3 — Serve

- [ ] `toolsmith serve` exposes tools via MCP stdio.
- [ ] Input validation errors returned as structured MCP errors.
- [ ] Oversize tool results truncated with guidance.

**Acceptance:** `claude mcp add toolsmith-dev toolsmith serve` connects; tools callable from Claude Code.

### Phase 4 — Eval

- [ ] Task file parser (Pydantic-validated).
- [ ] Agentic loop with async concurrency, retries, timeouts.
- [ ] All four verifier types.
- [ ] Transcript logging.

**Acceptance:** `toolsmith eval evals/example.json` runs deterministically with transcripts on disk.

### Phase 5 — Improve + Polish

- [ ] `toolsmith improve` with diff preview and `--write`.
- [ ] README covers install → init → write → lint → serve → eval.
- [ ] `scripts/gen_rule_docs.py` generates a rule reference page from the registry.
- [ ] Self-dogfooding: the project includes its own example tools that pass lint.

**Acceptance:** All phase checks pass; self-lint is green.

---

## 12. Testing Requirements

- Every lint rule: ≥1 passing fixture, ≥1 failing fixture.
- `loader.py`: valid module, missing `tool` decorator, import-time exception, duplicate names.
- `tokens.py`: `respx`-mocked API returning fixed counts; verifies caching prevents repeat requests.
- `eval_runner.py`: mock `anthropic.AsyncAnthropic` with scripted tool-use sequences; verify loop termination, retry on error, iteration cap.
- `mcp_server.py`: in-process MCP client from the SDK's test utilities to round-trip tool calls.
- CLI: `typer.testing.CliRunner` for each subcommand; assert stdout, stderr, exit codes.
- No network in CI: every external call mocked via `respx` or monkeypatched.
- Coverage target: 85% lines, 100% on `core/lint/*`.

---

## 13. Acceptance Criteria — Definition of Done

- [ ] `uv sync && pytest && mypy --strict src/ && ruff check src/ tests/` succeeds on a clean clone.
- [ ] `toolsmith --help` lists seven subcommands.
- [ ] All Phase 1–5 acceptance checks pass.
- [ ] Self-lint reports zero errors on the bundled example tools.
- [ ] `toolsmith eval` runs to completion without crashing, even when tasks fail.
- [ ] No stack trace in default output; always present with `--debug`.
- [ ] Every documented exit code is reachable and correct.
- [ ] Package installable via `pipx install toolsmith` from a local wheel (`uv build && pipx install dist/*.whl`).

---

## 14. Out of Scope (v0.1)

- Watch mode for `lint`.
- Remote config loading.
- Tool versioning / migration tooling.
- Parallel `improve` across many tools.
- Publishing to PyPI (manual step; do not automate in v0.1).

---

## Appendix — `improve` Prompt Skeleton

Stored in `src/toolsmith/templates/improve_prompt.md`:

```
You are refining a tool definition for use by a coding agent. Apply the
principles in the attached specification. Keep changes minimal and
preserve the handler logic exactly.

<specification>
{{ principles_spec }}
</specification>

<current_tool>
{{ tool_source }}
</current_tool>

<lint_output>
{{ lint_json }}
</lint_output>

Return:
1. A unified diff of your proposed changes, wrapped in ```diff fences.
2. A short list of what you changed and why, one bullet per change.

Do not modify the handler body. Do not rename the tool's decorated function.
```

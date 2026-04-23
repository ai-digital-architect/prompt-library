# Command Contracts

Every compliant `toolsmith` implementation exposes seven subcommands with identical behavior (modulo stack-native authoring conventions). This reference is the source of truth for inputs, outputs, flags, and exit codes.

## Table of contents

- [Global conventions](#global-conventions)
- [`init`](#toolsmith-init-dir)
- [`new`](#toolsmith-new-tool-name)
- [`lint`](#toolsmith-lint-path)
- [`tokens`](#toolsmith-tokens-path)
- [`serve`](#toolsmith-serve)
- [`eval`](#toolsmith-eval-task-file)
- [`improve`](#toolsmith-improve-tool)

---

## Global conventions

### Common flags

Every subcommand accepts:

| Flag | Purpose |
|---|---|
| `--json` | Emit machine-readable JSON instead of human-formatted output. |
| `--cwd <path>` | Run as if invoked from `path` (overrides project discovery). |
| `--debug` | Show stack traces and verbose internal logs. |
| `--help`, `-h` | Show subcommand usage. |
| `--version`, `-V` | Print version and exit. |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Validation failure: the operation completed but detected problems (lint errors, failing evals, token budget exceeded). |
| `2` | User error: bad flags, missing files, invalid arguments. |
| `3` | Internal error: unexpected exception; detail shown with `--debug`. |

Every exit code must be reachable and deterministic. Acceptance criteria verify this.

### Error output

All errors follow the three-line structure:

```
toolsmith: <short summary>
  cause: <specific cause>
  fix:   <concrete next step>
```

Never print raw stack traces to stdout/stderr by default. `--debug` reveals them.

---

## `toolsmith init [dir]`

Scaffold a new toolsmith project.

### Behavior

1. Target directory is `dir` (default: `.`).
2. Copies the project template (config file, sample tool, sample eval, README) into the target.
3. If `dir` contains conflicting files and `--force` was not passed, exit with code `2`.
4. If the stack requires dependency installation, run it unless `--no-install`.

### Flags

- `--force` — overwrite existing files.
- `--no-install` — skip dependency installation.

### Output

```
Created toolsmith project in ./my-tools
  ├─ toolsmith config
  ├─ tools/example_ping
  └─ evals/example

Next steps:
  cd my-tools
  toolsmith new my_first_tool
  toolsmith lint
```

### Acceptance

The generated sample tool must pass `toolsmith lint` with zero problems — new users see a green baseline.

---

## `toolsmith new <tool-name>`

Scaffold a new tool file.

### Behavior

1. Validate `<tool-name>` matches `^[a-z][a-z0-9_]+$` and contains at least one `_` (enforcing TS001 and TS002 at creation time). On failure, exit with code `2` and a structured error that names the violated rule.
2. Create a new tool file from the template at `<tools_dir>/<tool-name>.<ext>` (with sibling handler for shell).
3. Fail if the target file exists unless `--force`.
4. Shell implementations additionally `chmod +x` the handler.

### Flags

- `--description <str>` — pre-fill the tool's description with the provided string.
- `--force` — overwrite an existing file.

### Output

```
Created tool: my_first_tool
  location: tools/my_first_tool.py

Run `toolsmith lint tools/my_first_tool.py` to validate.
```

---

## `toolsmith lint [path]`

Run every enabled lint rule across every tool file under `path`.

### Behavior

1. Default `path` is the configured `tools_dir`.
2. Load every tool file in `path`; surface load errors as diagnostics without aborting the run.
3. Apply every rule enabled by configuration; collect diagnostics; sort deterministically by (file, line, rule ID).
4. Render output in the selected format.
5. Exit code: `1` if any diagnostic of severity `error` was reported; `0` otherwise.

### Flags

- `--rule <id>` — run only the named rule (e.g. `--rule TS201`).
- `--fix` — apply safe auto-fixes where available (limited to whitespace normalization, sample-file extension fixes, handler executable bit). Auto-fixes never change descriptions or schemas.

### Output — human

```
tools/repo_symbols_find.py
  ✖  TS201  Description is missing a "Do NOT use when" section        (line 18)
  ⚠  TS103  Parameter `q` lacks an enum                               (line 9)

tools/repo_logs_search.py
  ✖  TS101  Parameter `filter` is missing a description               (line 14)

2 errors, 1 warning across 2 files
```

### Output — JSON

```json
{
  "problems": [
    {
      "file": "tools/repo_symbols_find.py",
      "rule": "TS201",
      "severity": "error",
      "message": "Description is missing a 'Do NOT use when' section",
      "line": 18
    },
    {
      "file": "tools/repo_symbols_find.py",
      "rule": "TS103",
      "severity": "warning",
      "message": "Parameter `q` lacks an enum",
      "line": 9
    },
    {
      "file": "tools/repo_logs_search.py",
      "rule": "TS101",
      "severity": "error",
      "message": "Parameter `filter` is missing a description",
      "line": 14
    }
  ],
  "summary": {
    "errors": 2,
    "warnings": 1,
    "info": 0,
    "files": 2
  }
}
```

JSON output must be parseable without any ANSI color codes or decorative characters.

---

## `toolsmith tokens [path]`

Report the token cost of each tool definition and the total.

### Behavior

1. Default `path` is the configured `tools_dir`.
2. For each tool, count tokens in `name`, `description`, and `input_schema` (serialized to the format the target model consumes).
3. Sum per tool and for the project.
4. Cache results in `.toolsmith/tokens-cache.json` keyed by content hash.
5. If `--response <file>` was provided, also count tokens for the sample response and include it in the output.
6. If `--fail-over <n>` was provided and the total exceeds `n`, exit with code `1`.

### Flags

- `--response <file>` — count tokens for a sample response file (JSON, text, or Markdown).
- `--model <id>` — override the counting model (default: project config `model`).
- `--fail-over <n>` — exit `1` if total exceeds `n` tokens (useful in CI).
- `--no-cache` — ignore the cache and recount everything.

### Output — human

```
Tool                    Name  Desc  Schema   Total
repo_symbols_find          4   187      91     282
repo_symbols_refs          4   164      78     246
repo_files_search          4   201     103     308
--------------------------------------------------
Total                     12   552     272     836
```

### Output — JSON

```json
{
  "model": "claude-opus-4-7",
  "tools": [
    {
      "name": "repo_symbols_find",
      "tokens": { "name": 4, "description": 187, "schema": 91, "total": 282 }
    }
  ],
  "total_tokens": 836,
  "response_tokens": null
}
```

---

## `toolsmith serve`

Expose all loaded tools as a local MCP server.

### Behavior

1. Load every tool under `tools_dir`; abort with a structured error if any tool fails to load.
2. Start an MCP server using the target stack's official MCP SDK.
3. Register each tool with its `name`, `description`, and `input_schema` (converted to MCP's schema format as needed).
4. On a `call_tool` request: validate input against the tool's schema, invoke the handler, serialize the result. If the result exceeds `response_token_limit`, truncate and append guidance text.
5. Return MCP errors on validation failure with the specific parameter and fix referenced.
6. Print the connect command the user can paste into Claude Code.

### Flags

- `--transport <stdio|http>` — default `stdio`.
- `--port <n>` — bind port for `http` transport.

### Output

```
toolsmith serving 7 tools on stdio.

To connect from Claude Code:
  claude mcp add toolsmith-dev toolsmith serve

Press Ctrl-C to stop.
```

### Implementation note

Shell implementations may substitute a `run <tool-name>` subcommand for `serve` because implementing MCP in bash is impractical. In that case, document a separate MCP adapter in `contrib/` and reference it from `--help` output for `run`. This is the only permitted deviation from the seven-subcommand surface.

---

## `toolsmith eval <task-file>`

Run an agentic evaluation against the loaded tool set.

### Task file format

```json
{
  "tasks": [
    {
      "id": "find-parser-symbol",
      "prompt": "Where is the ConfigParser class defined in this repo?",
      "expected_tools": ["repo_symbols_find"],
      "verifier": {
        "type": "contains",
        "value": "src/config/parser"
      }
    }
  ]
}
```

`expected_tools` is optional and informational — if present, the transcript notes whether the expected tools were in fact called.

### Verifier types

| Type | Passes if... |
|---|---|
| `contains` | The final model output contains the substring `value`. |
| `regex` | The final model output matches `pattern`. |
| `tool_called` | The tool named `value` was called at least once. |
| `llm_judge` | An LLM rubric (specified in `rubric`) judges the run as passing. |

### Execution

For each task:

1. Build the `tools` parameter from the loaded tool definitions.
2. Start a fresh message loop with the configured model and interleaved thinking enabled.
3. On each assistant response with `stop_reason == "tool_use"`, invoke the matching handler, append a `tool_result` content block, and loop.
4. Stop when the assistant returns `stop_reason == "end_turn"` or `max_iterations` is hit.
5. Apply the verifier; record pass/fail with reason.
6. Log a per-task transcript to `evals/runs/<timestamp>/<task-id>.json` containing the full prompt, every request/response, token counts per turn, and final verdict.

### Flags

- `--filter <pattern>` — only run tasks whose `id` matches.
- `--concurrency <n>` — number of tasks to run in parallel (default 3).
- `--max-iterations <n>` — hard cap per task (default 25).
- `--timeout <s>` — per-turn timeout in seconds.

### Failure modes

- Handler throws → log as tool error, feed back to Claude as an error tool result, do not crash the run.
- Model response exceeds `max_tokens` → fail with reason `max_tokens_exhausted`.
- Iteration cap hit → fail with reason `iteration_limit`.
- Transient network error → retry up to 3 times with exponential backoff, then fail.

### Output — human

```
find-parser-symbol        PASS   3 tool calls   2,104 tokens   4.1s
list-recent-commits       FAIL   1 tool call      812 tokens   1.2s
  reason: expected tool `git_log` was never called

1/2 passed · 2,916 total tokens · transcripts in evals/runs/2026-04-22T14-02
```

### Output — JSON

```json
{
  "run_id": "2026-04-22T14-02",
  "tasks": [
    {
      "id": "find-parser-symbol",
      "passed": true,
      "tool_calls": 3,
      "tokens": 2104,
      "duration_seconds": 4.1,
      "transcript_path": "evals/runs/2026-04-22T14-02/find-parser-symbol.json"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total_tokens": 2916
  }
}
```

### Exit code

`1` if any task fails. `0` if all pass.

---

## `toolsmith improve <tool>`

Route a tool definition through Claude for suggested refinements.

### Behavior

1. Locate the tool file for `<tool>` (accepts tool name or file path).
2. Run `lint --json` on that tool to gather its current diagnostics.
3. Construct a prompt containing the tool's full source, the lint output, and the bundled principles reference.
4. Call Claude (model from project config).
5. Parse the response to extract a unified diff.
6. Render the diff with syntax highlighting (unless `--json`).
7. Prompt the user to accept, reject, or edit the diff.
8. If accepted, write the patch atomically. With `--write`, apply without prompting.

### Flags

- `--write` — apply suggestions without interactive confirmation.
- `--json` — emit the suggestion as structured output without prompting.

### Output — human

```
Suggested changes for tools/repo_symbols_find.py:

  @@ -12,7 +12,11 @@
  -    description: "Find symbols."
  +    description: """
  +        Locate definitions of a function, class, type, or variable.
  +        Use when: the agent needs to find where something is defined.
  +        Do NOT use when: searching for references — use repo_symbols_refs.
  +    """

Summary:
  • Expanded description to cover purpose, when-to-use, and when-NOT-to-use (addresses TS200, TS201)

Apply changes? [y/N/e(dit)]
```

### Output — JSON

```json
{
  "tool": "repo_symbols_find",
  "file": "tools/repo_symbols_find.py",
  "diff": "--- a/tools/repo_symbols_find.py\n+++ b/tools/repo_symbols_find.py\n@@ ...",
  "changes": [
    {
      "description": "Expanded description to cover purpose, when-to-use, and when-NOT-to-use",
      "rules_addressed": ["TS200", "TS201"]
    }
  ]
}
```

### Prompt skeleton

```
You are refining a tool definition for use by a coding agent. Apply the
principles in the attached specification. Keep changes minimal and
preserve the handler logic exactly.

<specification>
{{ contents of references/principles.md }}
</specification>

<current_tool>
{{ full source of the tool file }}
</current_tool>

<lint_output>
{{ output of `toolsmith lint --json <file>` }}
</lint_output>

Return:
1. A unified diff of your proposed changes, wrapped in ```diff fences.
2. A short list of what you changed and why, one bullet per change,
   each naming the lint rule IDs it addresses when relevant.

Do not modify the handler body. Do not rename the tool's export.
```

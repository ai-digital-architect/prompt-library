# Acceptance Criteria

What "done" means for a `toolsmith` implementation. Run this as a checklist at the end of a build.

## Table of contents

- [Definition of done](#definition-of-done)
- [Command-level acceptance](#command-level-acceptance)
- [Cross-cutting quality gates](#cross-cutting-quality-gates)
- [Testing requirements](#testing-requirements)
- [Implementation phases](#implementation-phases)

---

## Definition of done

An implementation is complete when **all** of the following are true:

- [ ] The project builds from a clean clone using the stack's canonical command (`uv sync && pytest`, `pnpm install && pnpm test`, `make build && make test`).
- [ ] `toolsmith --help` lists all seven subcommands.
- [ ] Every command-level acceptance check below passes.
- [ ] Self-lint is green: running `toolsmith lint` on the bundled example tools reports zero errors.
- [ ] Every documented exit code is reachable by at least one path.
- [ ] JSON output for every command parses as valid JSON without post-processing.
- [ ] No command prints a stack trace without `--debug`.
- [ ] All four error severity levels (`error`, `warning`, `info`, `off`) are respected by the lint runner.
- [ ] The full TS001–TS302 rule catalog is implemented (rules may be `off` by default, but the check must exist and be togglable).
- [ ] Documentation covers install, quick-start, and every subcommand.

---

## Command-level acceptance

### `init`

- [ ] `toolsmith init demo && cd demo` produces a directory containing, at minimum: config file, `tools/` with one example tool, `evals/` with one example eval, a README.
- [ ] The example tool passes `toolsmith lint` with zero problems.
- [ ] The example eval runs to completion when `toolsmith eval evals/example.json` is invoked (possibly failing, but not crashing).
- [ ] Re-running `init` in a non-empty directory exits with code `2` unless `--force`.

### `new`

- [ ] `toolsmith new repo_files_search` creates a tool file at `tools/repo_files_search.<ext>` that imports cleanly.
- [ ] `toolsmith new badname` exits with code `2` and names either TS001 or TS002 in the error.
- [ ] `toolsmith new <existing>` exits `2` unless `--force`.
- [ ] The created file passes `toolsmith lint` with zero errors (warnings permitted if the tool body is intentionally minimal).

### `lint`

- [ ] Every lint rule in the catalog has at least one passing fixture and one failing fixture in the test suite.
- [ ] `toolsmith lint` without arguments lints every file in `tools_dir`.
- [ ] `toolsmith lint tools/foo.py` lints only that file.
- [ ] `toolsmith lint --rule TS201` runs only TS201.
- [ ] Output is deterministic across runs on the same input.
- [ ] Exit code is `1` when any error-severity problem is reported; `0` otherwise.
- [ ] `--json` output is valid JSON and contains every problem the human output shows.
- [ ] Severity overrides from config are respected for every rule.

### `tokens`

- [ ] `toolsmith tokens` reports a total and per-tool breakdown.
- [ ] Counts are stable across runs for identical inputs (via cache or deterministic counting).
- [ ] `--response <file>` adds response token counts to output.
- [ ] `--fail-over <n>` triggers exit `1` when total exceeds `n`.
- [ ] `--no-cache` recomputes counts from scratch.
- [ ] `--model` override is applied when provided.

### `serve`

- [ ] `toolsmith serve` starts an MCP server that Claude Code can connect to via `claude mcp add`.
- [ ] All loaded tools are callable from the connected client.
- [ ] Input validation errors are returned as structured MCP errors (not server crashes).
- [ ] Tool results exceeding `response_token_limit` are truncated with guidance appended.
- [ ] Ctrl-C cleanly stops the server.

**Shell implementation exception:** `serve` may be replaced by `run <tool-name>` with a separate MCP adapter documented in `contrib/`. In that case:

- [ ] `echo '<input>' | toolsmith run <tool>` round-trips input through the handler and writes JSON to stdout.
- [ ] Validation errors return structured JSON and exit `1`.
- [ ] The contrib adapter is present, documented in the README, and tested.

### `eval`

- [ ] `toolsmith eval evals/example.json` runs to completion even when individual tasks fail.
- [ ] Each task produces a transcript in `evals/runs/<timestamp>/<task-id>.json` containing the full prompt, every request/response pair, token counts, and final verdict.
- [ ] All four verifier types (`contains`, `regex`, `tool_called`, `llm_judge`) work.
- [ ] Transient network errors trigger up to 3 retries with exponential backoff before failing.
- [ ] Handler exceptions are logged as tool errors and fed back to the agent, never crash the run.
- [ ] `max_tokens` and iteration-cap conditions produce structured failure records, not crashes.
- [ ] `--filter <pattern>` narrows the run to matching task IDs.
- [ ] `--concurrency <n>` actually bounds parallelism.
- [ ] Exit code is `1` if any task fails.

### `improve`

- [ ] `toolsmith improve <tool>` produces a non-empty suggestion for a deliberately bad fixture tool.
- [ ] The suggestion is rendered as a unified diff with syntax highlighting.
- [ ] Interactive mode prompts accept/reject/edit.
- [ ] `--write` applies the suggestion without prompting.
- [ ] `--json` emits structured output without prompting.
- [ ] Applying the suggested diff on a fixture that previously failed lint clears at least one of the failing rules.
- [ ] The handler body and exported symbol names are never modified.

---

## Cross-cutting quality gates

### Error handling

- [ ] Every user-visible error follows the three-line format (`toolsmith:` / `cause:` / `fix:`).
- [ ] No error prints a stack trace unless `--debug` was passed.
- [ ] Internal errors (exit code `3`) are rare: validation failures use code `1`, user errors use code `2`.
- [ ] Every error message names at least one specific next action.

### Output format

- [ ] Human-readable output uses colors when attached to a TTY, plain text otherwise.
- [ ] JSON output never contains color codes or ANSI escapes.
- [ ] Human output and JSON output convey the same information for the same command invocation.

### Performance

- [ ] `lint` finishes in under 2 seconds on a 20-tool fixture project on typical developer hardware.
- [ ] `tokens` with a warm cache finishes in under 1 second on the same project.
- [ ] `serve` starts responding to MCP requests within 2 seconds of launch.
- [ ] No command leaks file descriptors or subprocesses.

### Configuration

- [ ] Missing config file uses documented defaults without crashing.
- [ ] Invalid config file produces a clear error with the offending field and line number.
- [ ] Severity overrides in config are applied correctly.

---

## Testing requirements

### Coverage

- [ ] Every lint rule: ≥ 1 passing fixture and ≥ 1 failing fixture in the test suite.
- [ ] Loader: tests for valid file, missing required field, invalid schema, duplicate names, import-time error.
- [ ] Token counter: tests against known reference values with a mocked API.
- [ ] MCP server: in-process client round-trips a tool call successfully.
- [ ] Eval runner: mocked API with scripted tool-use sequences verifies loop termination, retry logic, and iteration cap.
- [ ] CLI: each subcommand tested via subprocess or the stack's CLI test harness; assertions on stdout, stderr, and exit code.
- [ ] Line coverage target: 80% overall, 100% on lint rule implementations.

### CI

- [ ] No network access required for the test suite. All external calls mocked.
- [ ] Tests deterministic: no flaky cases, no time-dependent assertions that rely on wall clock.
- [ ] Test suite runs in under 30 seconds on CI.

### Self-testing

- [ ] The project's own example tools pass `toolsmith lint` with zero errors.
- [ ] The project's own example eval runs to completion (tasks may pass or fail, but the runner must not crash).

---

## Implementation phases

A recommended order of work. Each phase ends with a testable, demo-able intermediate product.

### Phase 1 — Foundation

- Project scaffolding with test framework, linter, type checker wired.
- Config loading with defaults and overrides.
- `ToolDefinition` type/record and the authoring API (decorator, factory, or JSON contract).
- Loader that discovers and validates tool files.
- `init` and `new` working end-to-end.

**Phase 1 done when:** `toolsmith init demo && cd demo && toolsmith new repo_files_search` produces a valid tool that loads cleanly.

### Phase 2 — Lint and Tokens

- All TS001–TS302 rules implemented with fixture tests.
- Severity overrides from config respected.
- `lint` with human and JSON output, correct exit codes.
- `tokens` with API-backed counting and content-hash cache.

**Phase 2 done when:** the full test suite passes and `toolsmith lint tests/fixtures/tools` reports the expected diagnostic set for every fixture.

### Phase 3 — Serve (or Run)

- `serve` exposes loaded tools via MCP (or `run` executes a single tool for shell implementations).
- Input validation errors returned as structured errors.
- Oversize tool results truncated with guidance appended.

**Phase 3 done when:** `claude mcp add toolsmith-dev toolsmith serve` connects and tools are callable from Claude Code (or `toolsmith run <tool>` round-trips JSON successfully for shell).

### Phase 4 — Eval

- Task file parser with schema validation.
- Agentic loop with async concurrency, retries, timeouts.
- All four verifier types.
- Transcript logging to `evals/runs/<timestamp>/`.

**Phase 4 done when:** the bundled example eval runs deterministically with transcripts written to disk.

### Phase 5 — Improve and Polish

- `improve` with diff preview and `--write`.
- README with quick-start and per-command documentation.
- Auto-generated rule reference page (from the rule registry if feasible).
- Self-dogfooding: the project's own example tools pass lint.

**Phase 5 done when:** all phase-5 checks pass and self-lint is green.

---

## Anti-acceptance — things that should fail the build

Treat any of the following as a bug, not a stylistic preference:

- Hardcoded API keys or secrets in source.
- Any command that can hang indefinitely without a timeout.
- Silent data loss on existing files (without `--force` or equivalent confirmation).
- Tool loads that require network access.
- Lint rules that depend on network access.
- JSON output that contains color codes, prompts, or interactive elements.
- Any path where an uncaught exception reaches the user.
- Log output that includes user inputs without clear provenance (enables prompt-injection confusion downstream).

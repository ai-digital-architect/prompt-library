# `toolsmith` — CLI Build Specification

> **Audience:** Claude Code, as an implementing agent.
> **Goal:** Build a TypeScript CLI that helps developers design, validate, and evaluate tools for coding agents, following the principles in `effective-tools-spec.md`.
> **Deliverable:** A publishable npm package that exposes a `toolsmith` binary.

If any requirement in this document conflicts with something you discover during implementation (for example, a library API has changed), stop, explain the conflict, and wait for confirmation before diverging.

---

## 1. Product Overview

`toolsmith` is a command-line tool for developers who are writing tools for coding agents (Claude Code, MCP servers, or direct Anthropic API tool use). It operationalizes the standards in `effective-tools-spec.md` as an executable workflow:

- **Scaffold** new tool definitions from templates that already follow the spec.
- **Lint** existing tool definitions against concrete, enumerated rules.
- **Measure** the token cost of tool definitions and sample responses.
- **Serve** tool definitions as a local MCP server for hands-on testing in Claude Code.
- **Evaluate** tools by running an agentic loop against a task file and reporting pass rate, token usage, and failure modes.
- **Improve** a tool's description or schema by routing it through Claude with the spec as context.

The intended user runs `toolsmith init` in a new repo, writes tool definitions as TypeScript files, and uses the other subcommands throughout the write → lint → serve → eval → improve loop.

---

## 2. Goals and Non-Goals

### Goals

- Zero-config default behavior for a new project.
- Deterministic, reproducible lint output (exit codes, stable ordering).
- Fast feedback: `lint` and `tokens` should finish in under 2 seconds on a 20-tool project.
- Output readable by both humans (default) and machines (`--json`).
- Work offline for `init`, `new`, `lint`, `tokens`, `serve`. Only `eval` and `improve` require network access.

### Non-Goals

- Not a general-purpose MCP framework. The `serve` command exists for local testing only.
- Not a replacement for your production test suite. `eval` is for agent-behavior regressions, not unit tests.
- No GUI, no web dashboard.
- No automatic publishing of tools to registries.

---

## 3. Tech Stack

Fixed choices. Do not substitute without raising it first.

| Concern | Choice | Rationale |
|---|---|---|
| Language | TypeScript (strict mode) | Type-safe schemas; matches MCP SDK's native language. |
| Runtime | Node.js ≥ 20 | Native `fetch`, stable ESM. |
| CLI framework | `commander` | Mature, small, well-documented. |
| Schema validation | `zod` | Runtime validation + type inference for tool definitions. |
| MCP | `@modelcontextprotocol/sdk` | Official SDK. |
| Anthropic API | `@anthropic-ai/sdk` | Official SDK for `eval` and `improve`. |
| Token counting | `@anthropic-ai/tokenizer` or SDK's `count_tokens` endpoint | Accurate Claude-family counts. |
| Test framework | `vitest` | Fast, ESM-first, compatible with TS out of the box. |
| Output formatting | `picocolors` + `cli-table3` | Minimal color dependency; clean tables. |
| Build | `tsup` | Simple bundler producing both ESM and CJS. |
| Package manager | `pnpm` | Fast, deterministic; project assumes pnpm lockfile. |

---

## 4. Project Structure

Create this exact layout.

```
toolsmith/
├── bin/
│   └── toolsmith.js              # Shebang wrapper that imports dist/cli.js
├── src/
│   ├── cli.ts                    # Commander setup, subcommand wiring
│   ├── commands/
│   │   ├── init.ts
│   │   ├── new.ts
│   │   ├── lint.ts
│   │   ├── tokens.ts
│   │   ├── serve.ts
│   │   ├── eval.ts
│   │   └── improve.ts
│   ├── core/
│   │   ├── tool-definition.ts    # The ToolDefinition type + zod schema
│   │   ├── loader.ts             # Discovers and imports tool files
│   │   ├── lint-rules/
│   │   │   ├── index.ts          # Registry of all rules
│   │   │   ├── naming.ts         # TS001–TS099
│   │   │   ├── schema.ts         # TS100–TS199
│   │   │   ├── description.ts    # TS200–TS299
│   │   │   └── response.ts       # TS300–TS399
│   │   ├── linter.ts             # Runs rules, aggregates diagnostics
│   │   ├── tokens.ts             # Token counting utilities
│   │   ├── mcp-server.ts         # Wraps tools as an MCP server
│   │   └── eval-runner.ts        # Agentic loop for eval
│   ├── templates/
│   │   ├── tool.ts.tmpl          # New-tool template
│   │   └── project/              # Files copied by `init`
│   │       ├── toolsmith.config.ts.tmpl
│   │       ├── tools/.gitkeep
│   │       ├── evals/example.json.tmpl
│   │       └── README.md.tmpl
│   └── utils/
│       ├── logger.ts
│       └── fs.ts
├── tests/
│   ├── lint-rules.test.ts
│   ├── tokens.test.ts
│   ├── loader.test.ts
│   └── fixtures/
│       └── tools/                # Example tools (good and bad) for tests
├── package.json
├── tsconfig.json
├── tsup.config.ts
├── vitest.config.ts
├── .gitignore
└── README.md
```

### `package.json` essentials

```json
{
  "name": "toolsmith",
  "version": "0.1.0",
  "type": "module",
  "bin": { "toolsmith": "./bin/toolsmith.js" },
  "engines": { "node": ">=20" },
  "files": ["dist", "bin", "src/templates"],
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "test": "vitest run",
    "lint:self": "node bin/toolsmith.js lint tests/fixtures/tools"
  }
}
```

---

## 5. Tool Definition Format

The canonical input `toolsmith` consumes. Every command operates on files matching this shape.

### 5.1 File convention

A tool lives in its own `.ts` file under `tools/` (configurable) and has `export default` of a `ToolDefinition`:

```ts
import { defineTool } from "toolsmith";

export default defineTool({
  name: "repo_symbols_find",
  description: `
    Locate definitions of a function, class, type, or variable in the
    indexed repository.

    Use when: the agent needs to find where something is defined.
    Do NOT use when: searching for *references* — use repo_symbols_refs.
  `,
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Exact symbol name. Case-sensitive."
      },
      kind: {
        type: "string",
        enum: ["function", "class", "type", "variable"],
        description: "Optional filter by symbol kind."
      },
      response_format: {
        type: "string",
        enum: ["concise", "detailed"],
        default: "concise",
        description:
          "'concise' returns path and line only. 'detailed' adds signature and module."
      }
    },
    required: ["name"]
  },
  handler: async (input) => {
    // implementation returned by user
  }
});
```

### 5.2 The `ToolDefinition` type

Defined in `src/core/tool-definition.ts`:

```ts
export interface ToolDefinition<I = unknown, O = unknown> {
  name: string;
  description: string;
  inputSchema: JSONSchema;              // validated via zod at load time
  handler: (input: I) => Promise<O>;
  meta?: {
    namespace?: string;                 // optional, derived from name prefix
    version?: string;
    tags?: string[];
  };
}

export function defineTool<I, O>(def: ToolDefinition<I, O>): ToolDefinition<I, O>;
```

`defineTool` is an identity function at runtime; its job is type inference and providing a stable import target for users.

### 5.3 Config file

`toolsmith.config.ts` at project root:

```ts
import { defineConfig } from "toolsmith";

export default defineConfig({
  toolsDir: "tools",
  evalsDir: "evals",
  model: "claude-opus-4-7",              // used by eval / improve
  responseTokenLimit: 25000,
  lint: {
    // Severity overrides (defaults in §7.5)
    rules: {
      "TS201": "warn",                  // example: downgrade a rule
      "TS301": "off"
    }
  }
});
```

---

## 6. Command Reference

All commands follow these conventions:

- Exit `0` on success.
- Exit `1` on validation failure (e.g., lint errors found).
- Exit `2` on user error (bad flags, missing files).
- Exit `3` on unexpected internal error.
- Every command accepts `--json` for machine-readable output and `--cwd <path>` to override working directory.

### 6.1 `toolsmith init [dir]`

Create a new toolsmith project in `dir` (default: `.`).

Copies files from `src/templates/project/` into the target, expanding any `.tmpl` suffixes. Refuses to overwrite existing files unless `--force`.

**Flags:** `--force`, `--no-install`.

**Post-action:** unless `--no-install`, runs `pnpm install`.

### 6.2 `toolsmith new <tool-name>`

Scaffold a new tool file at `<toolsDir>/<tool-name>.ts` from `src/templates/tool.ts.tmpl`.

Validates that `<tool-name>` matches `^[a-z][a-z0-9_]+$` and contains an underscore (enforcing namespacing — see TS002). Fails fast if the file already exists.

**Flags:** `--description <str>` to pre-fill the description; `--force` to overwrite.

### 6.3 `toolsmith lint [path]`

Run every enabled lint rule over each tool file found under `path` (default: `<toolsDir>`).

**Output (human):**

```
tools/repo_symbols_find.ts
  ✖  TS201  Description is missing a "Do NOT use when" section        (line 4)
  ⚠  TS103  Parameter `q` lacks a description                         (line 12)

1 problem (1 error, 1 warning) across 1 file
```

**Output (`--json`):**

```json
{
  "problems": [
    {
      "file": "tools/repo_symbols_find.ts",
      "rule": "TS201",
      "severity": "error",
      "message": "Description is missing a 'Do NOT use when' section",
      "line": 4
    }
  ],
  "summary": { "errors": 1, "warnings": 1, "files": 1 }
}
```

**Flags:** `--rule <id>` (only run one), `--fix` (apply safe auto-fixes where available — initially limited to whitespace/section reordering).

**Exit:** `1` if any `error`-severity problem is reported.

### 6.4 `toolsmith tokens [path]`

Report the token cost of each tool definition and the total.

**Output (human):**

```
Tool                    Name  Desc  Schema   Total
repo_symbols_find          4   187      91     282
repo_symbols_refs          4   164      78     246
--------------------------------------------------
Total                      8   351     169     528
```

**Flags:**

- `--response <file>` — additionally count tokens for a sample response file (accepts JSON, text, or Markdown).
- `--model <id>` — override the counting model.
- `--fail-over <n>` — exit non-zero if total exceeds `n` tokens (useful in CI).

### 6.5 `toolsmith serve`

Start a local MCP server exposing every loaded tool. Prints the stdio command and a `claude mcp add` one-liner the user can copy.

**Output:**

```
toolsmith serving 7 tools on stdio.

To connect from Claude Code:
  claude mcp add toolsmith-dev node /abs/path/to/bin/toolsmith.js serve

Press Ctrl-C to stop.
```

**Flags:** `--transport stdio|http` (default stdio), `--port <n>` (http only).

Uses `@modelcontextprotocol/sdk` server APIs. Each tool's `handler` is invoked with the validated input and the result is returned as the MCP tool result.

### 6.6 `toolsmith eval <task-file>`

Run an agentic evaluation against the loaded tool set.

#### Task file format

```json
{
  "tasks": [
    {
      "id": "find-parser-symbol",
      "prompt": "Where is the ConfigParser class defined in this repo?",
      "expected_tools": ["repo_symbols_find"],
      "verifier": {
        "type": "contains",
        "value": "src/config/parser.ts"
      }
    }
  ]
}
```

Supported verifier types:

- `contains` — substring match against final model output.
- `regex` — regex match against final model output.
- `tool_called` — passes if the listed tool was called at least once.
- `llm_judge` — calls Claude with a rubric; schema: `{ type: "llm_judge", rubric: string }`.

#### Execution

For each task: spin up a fresh message loop using `@anthropic-ai/sdk` with all tools registered, interleaved thinking enabled, and a max of 25 iterations. Log every tool call, input, output, and token count to `evals/runs/<timestamp>/<task-id>.json`.

#### Output (human):

```
find-parser-symbol        PASS   3 tool calls   2,104 tokens   4.1s
list-recent-commits       FAIL   1 tool call      812 tokens   1.2s
  reason: expected tool `git_log` was never called

1/2 passed · 2,916 total tokens · transcripts in evals/runs/2026-04-22T14-02
```

**Flags:** `--filter <pattern>`, `--concurrency <n>` (default 3), `--max-iterations <n>`, `--json`.

**Exit:** `1` if any task fails.

### 6.7 `toolsmith improve <tool-file>`

Send the tool's source plus `effective-tools-spec.md` to Claude and receive a suggested rewrite.

Prints a unified diff and prompts the user to accept, reject, or edit. With `--write`, applies the accepted patch directly. With `--json`, emits the suggestion as structured output without prompting.

The prompt sent to Claude must:

1. Include the full tool file verbatim.
2. Include the lint output for that tool.
3. Include the relevant sections of the principles spec (bundled in `src/templates/principles.md`).
4. Ask for specific, minimal changes, and for a summary of what was changed and why.

---

## 7. Lint Rules

Every rule has an ID, a category, a default severity, a human message template, and optionally a safe auto-fix. All rules are implemented as separate files under `src/core/lint-rules/` and registered in `index.ts`.

### 7.1 Naming rules (TS001–TS099)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS001 | error | `name` matches `^[a-z][a-z0-9_]+$` | "Tool name must be lowercase snake_case." |
| TS002 | error | `name` contains at least one `_` (namespace prefix) | "Tool name must include a namespace prefix (e.g., `git_status`, not `status`)." |
| TS003 | warn  | First token of `name` is a verb OR is a recognized service namespace (list in config) | "Tool name should start with a verb or registered service prefix." |
| TS004 | error | No two loaded tools share a `name` | "Duplicate tool name." |
| TS005 | warn  | Name is not a near-duplicate of another (Levenshtein ≤ 2) | "Tool name is very close to `<other>` — agents will confuse them." |

### 7.2 Schema rules (TS100–TS199)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS100 | error | `inputSchema.type === "object"` | "Top-level input schema must be an object." |
| TS101 | error | Every property has a `description` | "Parameter `<name>` is missing a description." |
| TS102 | warn  | Parameter names are specific (no `user`, `id`, `data`, `input`, `value` as standalone names) | "Parameter `<name>` is too generic; prefer `<name>_id` or similar." |
| TS103 | warn  | String parameters with ≤5 known values use `enum` | "Parameter `<name>` should probably be an enum." |
| TS104 | warn  | Schema depth ≤ 3 | "Schema is deeply nested; flatten where possible." |
| TS105 | info  | Tool exposes `response_format` enum when output is structured | "Consider adding a `response_format` parameter." |
| TS106 | warn  | Tools returning potentially large data expose at least one of `max_results`, `limit`, `cursor`, `offset`, `filter` | "Tool may return large responses but has no pagination/filter parameter." |

### 7.3 Description rules (TS200–TS299)

| ID | Severity | Check | Message |
|---|---|---|---|
| TS200 | error | Description is non-empty and ≥ 40 characters | "Description is too short to orient the agent." |
| TS201 | warn  | Description contains a "Do NOT use" / "Use when" disambiguation | "Description should disambiguate against sibling tools." |
| TS202 | warn  | Description token count ≤ 400 | "Description exceeds 400 tokens; trim for context efficiency." |
| TS203 | info  | Description mentions return shape | "Consider describing what the tool returns." |

### 7.4 Response rules (TS300–TS399)

Applied only when a sample response is present (via `tokens --response` or a co-located `<tool>.sample.json`).

| ID | Severity | Check | Message |
|---|---|---|---|
| TS300 | error | Sample response ≤ `responseTokenLimit` (default 25,000) | "Sample response exceeds configured token limit." |
| TS301 | warn  | Sample response does not contain UUID-shaped strings | "Response contains opaque IDs; consider semantic identifiers or `response_format: detailed` only." |
| TS302 | warn  | Error responses include actionable text (regex for words like "try", "use", "pass", parameter names) | "Error response should tell the agent what to do next." |

### 7.5 Default severities and overrides

Defaults are in `src/core/lint-rules/index.ts`. Users override per-rule via `lint.rules` in config:

```ts
lint: {
  rules: {
    "TS003": "off",
    "TS105": "warn"
  }
}
```

Valid severities: `"error" | "warn" | "info" | "off"`.

---

## 8. Evaluation Harness Details

`src/core/eval-runner.ts` exposes:

```ts
export async function runEval(
  tasks: EvalTask[],
  tools: ToolDefinition[],
  opts: {
    model: string;
    maxIterations: number;
    concurrency: number;
    logDir: string;
  }
): Promise<EvalReport>;
```

Implementation requirements:

1. Use `client.messages.create` from `@anthropic-ai/sdk` with `tools` populated from loaded definitions.
2. On each assistant message with `stop_reason === "tool_use"`, invoke the matching tool's `handler`, append the result as a `tool_result` content block, and loop.
3. Stop when the assistant returns `stop_reason === "end_turn"` or `maxIterations` is hit.
4. Enable interleaved thinking via the appropriate header/beta flag.
5. Log a JSON transcript per task containing: input prompt, every request/response, token counts per turn, final verdict.
6. Run tasks in parallel up to `concurrency`, with an internal semaphore.

Failure modes to handle explicitly:

- Tool handler throws → log as a tool error, feed back to Claude as an error tool result (do not crash the run).
- Model response exceeds `max_tokens` → count as failure with reason `max_tokens_exhausted`.
- Iteration cap hit → count as failure with reason `iteration_limit`.
- Network error → retry up to 3 times with exponential backoff before marking failure.

---

## 9. MCP Server Mode Details

`src/core/mcp-server.ts` wraps loaded tools using `@modelcontextprotocol/sdk`. Requirements:

1. Register each tool with its `name`, `description`, and `inputSchema` converted to the MCP tool schema format.
2. On `CallTool` requests, validate the input against the tool's schema (via zod generated from the JSON Schema) *before* calling the handler. Return MCP errors for invalid inputs.
3. Truncate tool results that exceed `responseTokenLimit`, appending the truncation-guidance message from §5 of the principles spec.
4. Support both stdio and streamable HTTP transports.

---

## 10. Error Message Standards

Every CLI-level error printed to the user must follow this shape:

```
toolsmith: <short summary>
  cause: <specific cause>
  fix:   <concrete next step>
```

Example:

```
toolsmith: could not load tool file
  cause: tools/repo_search.ts does not export a default ToolDefinition
  fix:   add `export default defineTool({ ... })` to the file
```

No stack traces in default output. A `--debug` flag enables them.

Internal (thrown) errors use a `ToolsmithError` class with `code`, `cause`, and `fix` fields so the formatter can render them uniformly.

---

## 11. Implementation Phases

Build in this order. Each phase ends with passing tests and a usable binary.

### Phase 1 — Foundation

- [ ] Project scaffolding, tsup build, vitest wired, CI-ready.
- [ ] `ToolDefinition`, `defineTool`, `defineConfig` exported from package root.
- [ ] `src/core/loader.ts` that dynamically imports every `.ts` under `toolsDir`, validates with zod, and returns `ToolDefinition[]`.
- [ ] `toolsmith init` and `toolsmith new` working end-to-end.

**Acceptance:** `toolsmith init example && cd example && pnpm install && npx toolsmith new repo_files_search` produces a valid file.

### Phase 2 — Lint + Tokens

- [ ] All rules TS001–TS203 implemented with tests against fixtures.
- [ ] `toolsmith lint` with `--json`, `--rule`, correct exit codes.
- [ ] `toolsmith tokens` producing accurate counts via the tokenizer.
- [ ] Severity overrides via config respected.

**Acceptance:** `pnpm test` passes; `toolsmith lint tests/fixtures/tools` reports exactly the expected set of problems per fixture.

### Phase 3 — Serve

- [ ] `toolsmith serve` exposes loaded tools via MCP stdio.
- [ ] Tool results automatically truncated at the configured limit.
- [ ] Input validation errors returned as structured MCP errors.

**Acceptance:** `claude mcp add toolsmith-dev node bin/toolsmith.js serve` connects; tools are callable from Claude Code and return results.

### Phase 4 — Eval

- [ ] Task file parser + zod validation.
- [ ] All four verifier types working.
- [ ] Transcript logging to `evals/runs/<timestamp>/`.
- [ ] Concurrency, retries, timeouts implemented.

**Acceptance:** Running the bundled example eval against the fixture tools produces a deterministic pass/fail line for each task and writes full transcripts.

### Phase 5 — Improve

- [ ] `toolsmith improve` generates diffs via Claude.
- [ ] Interactive accept/reject flow.
- [ ] `--write` applies changes atomically.

**Acceptance:** Running `improve` on a deliberately bad tool fixture produces a diff whose application causes previously-failing lint rules to pass.

### Phase 6 — Polish

- [ ] README with quick-start and each command documented.
- [ ] `--help` output reviewed for every subcommand.
- [ ] Self-lint: `pnpm lint:self` passes against this project's own dogfooded tools.
- [ ] Package published to npm (manual step; do not automate).

---

## 12. Testing Requirements

- Every lint rule has at least one passing fixture and one failing fixture.
- `loader.ts` has tests covering: valid file, missing default export, wrong shape, TypeScript compile error in a tool file.
- `tokens.ts` tests the counter against known reference values for short inputs.
- `eval-runner.ts` tests use a mocked `anthropic` client that returns scripted tool-use sequences; no real API calls in CI.
- CLI commands tested via `execa`, asserting on stdout, stderr, and exit codes.
- Fixtures live under `tests/fixtures/tools/` as real `.ts` files — test the same loader path users hit.
- Coverage target: 80% lines, 100% on all lint rule functions.

---

## 13. Documentation Requirements

The `README.md` must include:

1. Install: `pnpm add -D toolsmith` (or `npm i -D`).
2. Quick start: init → new → lint → serve.
3. A table listing every command with a one-line purpose.
4. The full lint rule table (auto-generated from the rule registry if feasible — a `scripts/gen-rule-docs.ts` script is acceptable).
5. A link to `effective-tools-spec.md` (this document's companion).

Each subcommand gets its own section in `docs/commands/<cmd>.md` with examples.

---

## 14. Acceptance Criteria — Definition of Done

The project is complete when all of the following are true:

- [ ] `pnpm install && pnpm build && pnpm test` succeeds on a clean clone.
- [ ] `node bin/toolsmith.js --help` lists all seven subcommands.
- [ ] All Phase 1–6 acceptance checks pass.
- [ ] Self-lint passes with zero errors on the project's own example tools.
- [ ] `toolsmith eval evals/example.json` runs to completion without crashing, even if some tasks fail.
- [ ] No command leaks a stack trace without `--debug`.
- [ ] Every exit code listed in §6 is reachable and correct.

---

## 15. Out of Scope (For This Version)

- Watch mode for `lint`.
- Remote config loading.
- Tool versioning and migration tooling.
- Publishing tools to a registry.
- A web UI for eval results.

These are candidates for v0.2 and should not be built now.

---

## Appendix A — Example `improve` Prompt Skeleton

Used by `src/commands/improve.ts`. Sent as a user message.

```
You are refining a tool definition for use by a coding agent. Apply the
principles in the attached specification. Keep changes minimal and
preserve the tool's handler logic exactly.

<specification>
{{ contents of effective-tools-spec.md }}
</specification>

<current_tool>
{{ full source of the .ts file }}
</current_tool>

<lint_output>
{{ output of `toolsmith lint --json <file>` }}
</lint_output>

Return:
1. A unified diff of your proposed changes, wrapped in ```diff fences.
2. A short list of what you changed and why, one bullet per change.

Do not modify the handler body. Do not rename the tool's export.
```

---

## Appendix B — Minimum Viable `init` Project

What `toolsmith init foo` produces:

```
foo/
├── package.json           # name=foo, private=true, deps on toolsmith
├── tsconfig.json
├── toolsmith.config.ts
├── tools/
│   └── example_ping.ts    # a working starter tool that passes lint
├── evals/
│   └── example.json       # one task that exercises example_ping
└── README.md
```

The starter tool must pass `toolsmith lint` with zero problems, so new users see a green baseline immediately.

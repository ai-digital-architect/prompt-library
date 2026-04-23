---
name: toolsmith-cli
description: Use when building a command-line tool that helps developers create, validate, or evaluate tools for coding agents (Claude Code, MCP servers, Anthropic API tool use). Provides the complete language-agnostic specification — product shape, seven-subcommand surface (init, new, lint, tokens, serve, eval, improve), tool definition format, the TS001-TS302 lint rule catalog, error message standards, output contracts, and acceptance criteria. Trigger this skill whenever the user wants to build "toolsmith", implement a tool linter, write a tool-validation CLI, build MCP server scaffolding, or work on any CLI that processes tool or function definitions for AI agents — regardless of whether the implementation language is Python, TypeScript, Go, shell, or something else.
---

# Toolsmith CLI Specification

A language-agnostic specification for a CLI that helps developers design, validate, and evaluate tools for coding agents. The target product is called `toolsmith`; this skill captures everything a compliant implementation must do, while leaving stack-specific decisions (package choices, project layout, build tooling) to the implementer.

Use this skill when the user wants to build any part of such a CLI. Do not substitute details here with guesses from training data — the command surface, lint rule IDs, and acceptance criteria defined here are the contract.

## What toolsmith is

`toolsmith` is a CLI for developers who write tools that coding agents will consume. It operationalizes the principles of good tool design (see `references/principles.md`) as an executable workflow:

- **Scaffold** new tool definitions from templates that already comply with the standards.
- **Lint** existing tool definitions against enumerated rules with stable IDs.
- **Measure** the token cost of tool definitions and sample responses.
- **Serve** tools as a local MCP server for hands-on testing in Claude Code.
- **Evaluate** tools by running an agentic loop against a task file.
- **Improve** tools by routing them through Claude with the principles as context.

The typical user runs `toolsmith init` in a new project, writes tool definitions, and uses the other subcommands throughout a write → lint → serve → eval → improve loop.

## When to consult which reference

Read the reference file matching the work being done. Each is independently useful; there is no required reading order beyond this file.

| If you are... | Read |
|---|---|
| Designing tool behavior or writing descriptions | `references/principles.md` |
| Defining what a tool definition looks like in your stack | `references/tool-format.md` |
| Implementing any of the seven subcommands | `references/commands.md` |
| Writing a lint rule | `references/lint-rules.md` |
| Choosing the implementation stack | `references/stack-selection.md` |
| Determining when the build is done | `references/acceptance.md` |

Skim all six once before implementing; deep-read the ones that apply to the task.

## The seven subcommands

Every compliant implementation exposes these seven subcommands. The contracts (inputs, flags, outputs, exit codes) are in `references/commands.md`. One-line summary:

- **`init [dir]`** — scaffold a new project with config, sample tool, sample eval.
- **`new <tool-name>`** — create a new tool file from the template.
- **`lint [path]`** — run every enabled rule against every tool file.
- **`tokens [path]`** — report token cost per tool and total.
- **`serve`** — expose loaded tools as a local MCP server.
- **`eval <task-file>`** — run an agentic loop; report per-task pass/fail.
- **`improve <tool>`** — route a tool through Claude for suggestions.

Every command supports `--json`, `--cwd <path>`, `--debug`, `--help`, `--version`.

Exit codes are uniform: `0` success, `1` validation failure, `2` user error, `3` internal error.

## The tool definition format

A tool definition is a language-independent record with these fields:

- `name` — lowercase snake_case, must include a namespace prefix (e.g. `repo_symbols_find`, not `find`).
- `description` — prose for the agent, covering purpose, when-to-use, when-NOT-to-use, and return shape.
- `input_schema` — JSON Schema for validated input.
- `handler` — an async function that accepts validated input and returns a serializable result.
- `meta` — optional namespace, version, and tags.

How this record is authored depends on the stack: a TypeScript implementation might use a `defineTool({ ... })` factory with zod; a Python implementation might use a `@tool` decorator with a Pydantic input model; a shell implementation might pair a JSON file with an executable handler script. All three are equivalent and produce the same lint results. See `references/tool-format.md` for the canonical contract and concrete examples per stack.

## The lint rule catalog

Lint rules have stable, language-independent IDs. A given rule checks the same thing and produces the same message across every implementation. Rule IDs fall into four ranges:

- **TS001–TS099** — naming (snake_case, namespace prefix, duplicates, near-duplicates).
- **TS100–TS199** — input schema (object root, descriptions required, enum usage, depth, pagination).
- **TS200–TS299** — descriptions (length floor, disambiguation sections, token ceiling).
- **TS300–TS399** — response (size limits, opaque-ID detection, error message actionability).

Each rule has a default severity (`error`, `warn`, `info`) that users can override per project. Full catalog, checks, and example messages are in `references/lint-rules.md`. Do not invent new rule IDs or repurpose existing ones — the IDs are part of the user-facing contract.

## Implementation guidance

Pick the implementation stack based on the user's constraints, not defaults. `references/stack-selection.md` contains a decision tree and an opinionated recommendation. Summary:

- For a fresh project where no stack is mandated and the audience is developers who write agent tools, Python is the strongest default (best schema ergonomics via Pydantic, mature MCP SDK, natural `pipx` distribution).
- TypeScript is a close second and becomes the right pick when tools themselves must interact with JS/TS codebases or live in a Node monorepo.
- Shell is the right pick only when tools are thin Unix wrappers with no persistent state and no need for a real MCP server — and even then, expect to drop the `serve` subcommand in favor of a `run` subcommand with a Python adapter for MCP.
- Go or Rust become attractive when startup latency under 50ms matters or when shipping a single static binary to non-developers is the goal.

When implementing, start by reading `references/principles.md` so the lint rules and descriptions feel motivated rather than arbitrary. Then let `references/commands.md` drive the command-by-command work. Run `references/acceptance.md` as a checklist at the end.

## Output and error conventions

All commands render output in two formats. Default is a human-readable rendering with colors and tables; `--json` emits a machine-readable structure following the schemas in `references/commands.md`. JSON output must be parseable without any color codes or decorative characters.

All user-visible errors follow a three-line structure:

```
toolsmith: <short summary>
  cause: <specific cause>
  fix:   <concrete next step>
```

Stack traces are suppressed by default and shown with `--debug`. Never print raw exceptions to users. Implement errors as a structured type (class in Python/TS, helper function in shell) so the formatter renders them uniformly.

## What this skill does not prescribe

The following are intentionally left to the implementer:

- Choice of CLI framework, schema library, package manager, or build tool.
- Project file layout (beyond the `tools/` and `evals/` directories that end users see).
- Specific test framework.
- Distribution mechanism (pipx, npm, homebrew, curl-to-bash — any is acceptable).
- Internal module boundaries.
- Whether tool definitions are authored as typed code, plain JSON, or something else — as long as the resulting record matches `references/tool-format.md`.

If the user asks for guidance on any of the above for a specific stack, consult `references/stack-selection.md` first, then apply language-idiomatic choices.

## Working with language-specific subagents

If the user has set up per-language subagents (for example, a Python agent, a TypeScript agent, a shell agent), the intended workflow is:

1. Read this skill and the relevant references to establish *what* needs to be built.
2. Delegate implementation to the subagent appropriate for the chosen stack.
3. Pass the subagent this skill's references plus a short project-level note indicating the stack choice and any project-specific constraints (e.g., "use uv, not pip"; "must run on Node 20+"; "distribute via homebrew").
4. When the subagent returns its implementation, verify against `references/acceptance.md` before declaring the work done.

The subagent brings the stack expertise; this skill brings the product definition. Neither should try to do the other's job.

## Quick sanity checks

Before considering any implementation complete, confirm:

- All seven subcommands are present and their contracts match `references/commands.md`.
- Running `toolsmith lint` on the project's own example tools reports zero errors (self-lint is green).
- Every documented exit code is reachable.
- JSON output for every command parses cleanly without post-processing.
- Error messages follow the three-line structure and never include stack traces by default.
- The full TS001–TS302 rule catalog is implemented (rules may be `off` by default but must exist).

Full acceptance criteria are in `references/acceptance.md`.

# Tool Definition Format

The language-agnostic contract for what a tool definition contains. Every `toolsmith` implementation must be able to load definitions matching this contract and produce identical lint results for equivalent tools across stacks.

## Required fields

A tool definition is a record with these fields:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `name` | string | yes | Unique identifier. Lowercase snake_case with at least one underscore (namespace prefix). |
| `description` | string | yes | Prose for the agent. Covers purpose, when-to-use, when-NOT-to-use, and return shape. |
| `input_schema` | JSON Schema | yes | Object-rooted schema validating the tool's input. Every property must have a `description`. |
| `handler` | callable/reference | yes | The code that executes when the tool is called. Accepts validated input, returns a serializable result. |
| `meta` | object | no | Optional `namespace`, `version`, `tags`. Used for tooling/discovery, never sent to the agent. |

## The handler contract

Regardless of how a handler is authored, it adheres to this runtime contract:

1. Receives a single input argument that has already been validated against `input_schema`.
2. Executes asynchronously where the host language supports it (Python `async def`, TypeScript `async` function, shell subprocess with JSON I/O).
3. Returns (or writes) a JSON-serializable value.
4. On error, raises/throws with a structured error object containing `summary`, `cause`, `fix` fields, *or* writes a tool-error structure if the transport layer requires it (MCP error, tool-result with `is_error: true`).
5. Does not perform input validation itself — trusts the framework to have validated.
6. Respects the `response_token_limit` from configuration; if the result would exceed it, truncates and appends the truncation-guidance message from the principles reference.

## Stack-specific authoring patterns

These are illustrative examples. A compliant implementation picks one idiomatic to its stack; all produce the same underlying record.

### Python — `@tool` decorator with Pydantic

```python
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
        description="'concise' returns path and line only.",
    )


@tool(
    name="repo_symbols_find",
    description="""
        Locate definitions of a function, class, type, or variable.
        Use when: the agent needs to find where something is defined.
        Do NOT use when: searching for references — use repo_symbols_refs.
    """,
    input_model=Input,
)
async def repo_symbols_find(input: Input) -> list[dict]:
    ...
```

`input_schema` is derived from `Input.model_json_schema()` at load time.

### TypeScript — `defineTool` factory with Zod

```typescript
import { z } from "zod";
import { defineTool } from "toolsmith";

const Input = z.object({
  name: z.string().describe("Exact symbol name. Case-sensitive."),
  kind: z
    .enum(["function", "class", "type", "variable"])
    .optional()
    .describe("Optional filter by symbol kind."),
  response_format: z
    .enum(["concise", "detailed"])
    .default("concise")
    .describe("'concise' returns path and line only."),
});

export default defineTool({
  name: "repo_symbols_find",
  description: `
    Locate definitions of a function, class, type, or variable.
    Use when: the agent needs to find where something is defined.
    Do NOT use when: searching for references — use repo_symbols_refs.
  `,
  inputSchema: Input,
  handler: async (input) => {
    // ...
  },
});
```

### Shell — JSON definition + executable handler

```
tools/
├── repo_symbols_find.json       # Definition record
└── repo_symbols_find.handler    # Executable; reads JSON stdin, writes JSON stdout
```

```json
{
  "name": "repo_symbols_find",
  "description": "Locate definitions...\n\nUse when: ...\nDo NOT use when: ...",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Exact symbol name. Case-sensitive."
      }
    },
    "required": ["name"]
  },
  "handler": "./repo_symbols_find.handler"
}
```

```bash
#!/usr/bin/env bash
# repo_symbols_find.handler
set -euo pipefail
input=$(cat)
name=$(echo "$input" | jq -r '.name')
# ... work ...
jq -n --arg path "$found" --argjson line "$line" \
  '{path: $path, line: $line}'
```

### Go — struct with method receiver (if the implementation is in Go)

```go
type RepoSymbolsFindInput struct {
    Name           string `json:"name" description:"Exact symbol name. Case-sensitive."`
    Kind           string `json:"kind,omitempty" enum:"function,class,type,variable"`
    ResponseFormat string `json:"response_format,omitempty" enum:"concise,detailed" default:"concise"`
}

var RepoSymbolsFind = toolsmith.Tool{
    Name: "repo_symbols_find",
    Description: `...`,
    InputType: reflect.TypeOf(RepoSymbolsFindInput{}),
    Handler: func(ctx context.Context, input RepoSymbolsFindInput) (any, error) {
        // ...
    },
}
```

## File conventions

All implementations follow the same on-disk conventions so users can move between stacks without relearning:

- Tool files live under `tools/` (configurable via `tools_dir` in the project config).
- One tool per file.
- File name matches the tool name: `repo_symbols_find.py` / `.ts` / `.json`.
- Shell implementations additionally carry a `<n>.handler` executable next to the JSON.
- An optional `<n>.sample.json` alongside the tool file provides a sample response that lint rules in the TS300 range can inspect.

## Discovery and loading

Every implementation exposes a loader that:

1. Scans `tools_dir` recursively (or non-recursively — both are acceptable).
2. Imports/parses each candidate file.
3. Extracts the tool definition record.
4. Validates the record shape (all required fields present, `input_schema` is valid JSON Schema).
5. Returns the list of `ToolDefinition` records, or a structured error referencing the specific file that failed.

Loader errors follow the same three-line format as CLI errors:

```
toolsmith: could not load tool definition
  cause: tools/repo_search.py does not expose a tool decorated with @tool
  fix:   add @tool(...) above the function or export a ToolDefinition
```

## Config file

Every project has a `toolsmith.{toml,conf,json,ts,py}` config file at the project root. The format depends on the stack, but the fields are identical:

| Field | Type | Default | Purpose |
|---|---|---|---|
| `tools_dir` | string | `"tools"` | Directory containing tool definitions. |
| `evals_dir` | string | `"evals"` | Directory containing eval task files. |
| `model` | string | `"claude-opus-4-7"` | Model used for `eval` and `improve`. |
| `response_token_limit` | integer | `25000` | Max tokens in any tool response before truncation. |
| `lint.rules.<TSnnn>` | enum | (per-rule defaults) | Severity override: `error` / `warn` / `info` / `off`. |

Stack-specific examples:

**Python** (`toolsmith.toml`):
```toml
tools_dir = "tools"
evals_dir = "evals"
model = "claude-opus-4-7"
response_token_limit = 25000

[lint.rules]
TS003 = "off"
TS105 = "warn"
```

**TypeScript** (`toolsmith.config.ts`):
```typescript
import { defineConfig } from "toolsmith";

export default defineConfig({
  toolsDir: "tools",
  evalsDir: "evals",
  model: "claude-opus-4-7",
  responseTokenLimit: 25000,
  lint: {
    rules: {
      TS003: "off",
      TS105: "warn",
    },
  },
});
```

**Shell** (`toolsmith.conf` — sourced as bash):
```bash
TOOLS_DIR="tools"
EVALS_DIR="evals"
MODEL="claude-opus-4-7"
RESPONSE_TOKEN_LIMIT=25000
LINT_TS003="off"
LINT_TS105="warn"
```

## Cross-stack portability

A tool authored in one stack cannot be directly loaded by another, but **the information content is identical** — any tool can be mechanically translated between stacks. Users who switch stacks should expect to rewrite their tool files once (ideally with `toolsmith improve` assisting), but their eval task files, lint rule configuration, and mental model of the CLI all transfer unchanged.

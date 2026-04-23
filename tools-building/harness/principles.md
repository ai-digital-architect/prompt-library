# Effective Tool Design — Principles

The standards that the lint rules and command contracts are derived from. Read this before implementing lint rules or writing tool descriptions; the rules will feel arbitrary without the motivation here.

Source basis: Anthropic Engineering, *Writing effective tools for agents — with agents* (Sep 2025), the Claude API tool-use documentation, and Claude Code best practices.

## The foundational frame

A tool is a **contract between a deterministic system and a non-deterministic agent**. Unlike a traditional API — where the caller's behavior is fixed — the caller here is an LLM that may hallucinate parameters, misread purpose, or pick the wrong tool entirely. Every design decision in this reference exists to reduce that uncertainty.

Three heuristics underlie everything else:

1. **Design for how agents reason, not how APIs are structured.** A tool is not a thin wrapper over an endpoint; it is a workflow primitive shaped around the agent's context window and decision process.
2. **Spend context like money.** Coding agents have finite working memory. Every token in a tool name, description, parameter, or response is paid for.
3. **Optimize with evaluations, not intuition.** Small refinements to descriptions and schemas often yield large shifts in reliability. Changes without evals are guesses.

## Tool selection — what to build and not build

### Build high-leverage tools, not API wrappers

Do not expose every endpoint a system has. Expose the small set of tools that match the workflows a coding agent actually performs. A `list_all_files` tool that returns a 10,000-line directory dump wastes context. A `search_files` tool that returns the five matches the agent needs does not.

### Consolidate chained operations

When agents reliably call tools in a fixed sequence, merge them. Examples for a coding CLI:

- Prefer `find_symbol(name)` over `list_files` → `read_file` → grep.
- Prefer `run_tests(pattern)` over `discover_tests` → `filter_tests` → `execute`.
- Prefer `apply_patch(path, diff)` over `read_file` → `compute_diff` → `write_file`.

Each consolidation removes an intermediate output from context and a branch point where the agent can go wrong.

### Keep the tool set small

Overlapping or ambiguous tools degrade selection accuracy. If two tools could plausibly answer the same request, collapse or differentiate them. Target the minimum set that covers real tasks — add tools only when an evaluation demonstrates need.

## Naming

### Namespace with a prefix

Every tool carries a namespace prefix that identifies its service and, where helpful, its resource:

```
<service>_<action>              # git_status, git_commit
<service>_<resource>_<action>   # repo_files_search, repo_symbols_find
```

Namespacing has a measurable effect on tool-selection accuracy when many tools are present.

### Name actions, not endpoints

Tool names read as verbs the agent would choose in a plan. Prefer `search_logs` over `get_log_entries`, `schedule_meeting` over `create_calendar_event_v2`.

### Naming rules

- Lowercase, snake_case.
- Start with a verb or a recognized service prefix.
- No version numbers or internal service codes.
- No synonyms across the tool set (`find_*` vs `search_*` vs `lookup_*` — pick one).
- Names unambiguous when read in isolation, without the description.

### Distinguish similar tools

Pairs like `notification_send_user` and `notification_send_channel` are a common source of wrong-tool selection. If two tools differ only by target type, make the distinction prominent in both the name and the first sentence of the description.

## Input schema

### Parameter naming

- Be specific about type in the name: `user_id`, not `user`; `file_path`, not `file`; `max_results`, not `limit`.
- Use the same parameter name for the same concept across every tool. Inconsistency (`path` here, `filepath` there, `file` elsewhere) produces malformed calls.
- Boolean parameters read true-as-intended: `include_hidden: true` not `hidden: true`.

### Schema hygiene

- Use JSON Schema with strict mode where the platform supports it.
- Every parameter has a description. No exceptions.
- Use `enum` for any parameter with a fixed value set.
- Mark required vs. optional explicitly. Provide defaults in both the description and the runtime code.
- Prefer shallow schemas. Deeply nested objects are error-prone.

### Expose a response_format control

For tools whose output has both human-readable and machine-readable consumers, expose a `response_format` enum:

```
response_format:
  type: string
  enum: [concise, detailed]
  default: concise
  description: >
    Use 'concise' for human-readable summaries;
    'detailed' to include IDs needed for follow-up tool calls.
```

This lets the agent request IDs only when it plans to chain another call, saving tokens on exploratory reads.

### Pagination as first-class parameters

Any tool that could return a large result set exposes:

- `max_results` (sensible default, typically 20–50)
- `offset` or `cursor` for continuation
- `filter` parameters that narrow results at the source

Defaults cap output well below the response token budget.

## Return values

### Return high-signal context only

Strip fields that don't inform the agent's next action. Drop `uuid`, `etag`, `created_at_microseconds`, `internal_revision_id`, `mime_type_extended`, and similar low-value fields unless they are needed for a subsequent tool call. Keep fields the agent will reason over: `name`, `path`, `summary`, `status`, `error_reason`.

### Prefer semantic identifiers over opaque IDs

Agents handle natural-language identifiers far better than alphanumeric UUIDs. Where you control the identifier space, resolve UUIDs to meaningful names or a 0-indexed scheme before returning them. When downstream tool calls genuinely need the opaque ID, return it only in `detailed` mode.

### Choose the response structure deliberately

XML, JSON, and Markdown each perform differently depending on task and model. There is no universal winner. Pick one per tool based on evaluation:

- Structured data the agent will parse: JSON.
- Code, diffs, file contents: Markdown with fenced blocks.
- Mixed content with sections: XML tags are often easier for the model to navigate.

Document the choice in the tool description so the agent knows what to expect.

### Keep responses bounded

Default cap: **25,000 tokens per tool response** (matching Claude Code's own default). Tools that might exceed this truncate and communicate clearly that truncation occurred, along with how to retrieve the rest.

### Truncation messages are instructional

When truncating, don't just cut off — tell the agent what to do next:

> Response truncated at 25,000 tokens. Showing first 120 of 847 matches. Narrow your query with the `path_glob` parameter, or paginate with `offset=120`.

## Error messages

Error messages are read by the agent and directly shape its next action. Treat them as prompts, not logs.

### Required structure

Every error response includes:

1. **What went wrong** — in plain language.
2. **Why it went wrong** — the specific cause, not a generic code.
3. **What to do next** — concrete, actionable guidance naming the parameter or tool to use.

### Examples

**Bad:**
```
Error: EINVAL (code 22)
```

**Bad:**
```
Error: Invalid input.
```

**Good:**
```
Error: parameter `file_path` must be absolute.
Received: "src/main.py"
Fix: pass an absolute path such as "/repo/src/main.py", or call
     resolve_path("src/main.py") first to convert it.
```

**Good:**
```
Error: no tests matched pattern "test_parser*".
Closest matches: test_parse_config, test_parsing_errors.
Fix: widen the pattern, e.g. "test_pars*", or list available tests with
     list_tests(module="parser").
```

### Rules

- Never return raw stack traces to the agent.
- Never return only an error code. Always include human-readable text.
- Name the offending parameter explicitly.
- Suggest the corrective tool call when one exists.
- If the error is recoverable by retry, say so and include a suggested wait.

### Validate early, fail loudly

Do parameter validation before touching any external system. An invalid-parameter error returned quickly with clear guidance is far more useful than a timeout 30 seconds in.

## Tool descriptions

Tool descriptions sit permanently in the agent's context. They are prompt-engineering surface, not documentation.

### Write for a new hire

Describe the tool the way you would explain it to someone joining your team: make implicit context explicit — query formats, domain terminology, relationships between resources, when *not* to use this tool.

### Structure

A good tool description has, roughly:

1. **One-line purpose.** What the tool does, in the agent's voice.
2. **When to use it.** One or two scenarios.
3. **When NOT to use it.** Disambiguation against sibling tools. Often the highest-value section.
4. **Parameter notes.** Anything not obvious from the parameter schema.
5. **Return shape summary.** What the agent will get back.

### Example description

```
Locate definitions of a function, class, type, or variable across the
indexed repository. Returns file paths, line numbers, and a short
signature for each match.

Use when: the agent needs to find where something is defined before
reading or editing it.

Do NOT use when: the agent needs to find *references* to a symbol —
use repo_symbols_references for that. Do not use for plain text search —
use repo_files_search.

Parameters:
  - name (required): exact symbol name. Case-sensitive. No wildcards;
    for fuzzy matching use repo_files_search.
  - kind (optional): one of "function" | "class" | "type" | "variable".
    Omit to search all kinds.
  - response_format: "concise" returns path + line only.
                     "detailed" also returns signature and enclosing
                     module — needed for apply_patch follow-ups.

Returns: JSON array of matches, max 50. If truncated, narrow by `kind`.
```

### Refinements compound

Minor wording changes in descriptions have produced significant gains on real benchmarks. Treat description edits as first-class changes and run them through evaluation.

## Token efficiency checklist

Before shipping a tool, verify:

- Tool description is under ~400 tokens.
- Parameter schema has no redundant properties.
- Default response size is well under 25,000 tokens for typical inputs.
- `response_format: concise` is genuinely concise (aim for ≤⅓ the detailed size).
- Opaque IDs are omitted unless the agent needs them for chaining.
- Truncation messages tell the agent how to continue.
- Errors are short and actionable.

## Evaluation workflow

Every non-trivial tool change passes through this loop:

1. **Build the prototype.** Wire it into a local MCP server or pass it directly via the API.
2. **Generate realistic eval tasks.** Inspired by real workflows, not toy cases. Strong tasks require multiple tool calls and realistic data.
3. **Pair each task with a verifier.** Exact-match where possible, LLM-judge where not. Avoid verifiers that punish harmless formatting differences.
4. **Run agents in a loop.** Simple `while` loop of LLM call → tool call → tool result. Enable interleaved thinking to surface reasoning.
5. **Collect metrics beyond accuracy.** Tool-call count, tokens consumed, error rate, wall-clock time. Redundant calls point to missing pagination; frequent parameter errors point to unclear descriptions.
6. **Feed transcripts back into Claude** to propose refactors. Claude is effective at identifying contradictions and improving self-consistency.
7. **Hold out a test set** to avoid overfitting descriptions to the training tasks.

## Summary — the design-done checklist

A tool is ready to ship when:

- **Naming:** namespaced, verb-led, unambiguous against siblings.
- **Schema:** every parameter has a description, enums where possible, strict mode on.
- **Inputs:** specific names (`user_id`, not `user`), pagination exposed, `response_format` where relevant.
- **Outputs:** high-signal fields only, semantic IDs over UUIDs, bounded size, structure matches the content.
- **Errors:** plain-language cause + specific fix, no raw stack traces, name the parameter.
- **Description:** purpose, when-to-use, when-NOT-to-use, parameter notes, return shape.
- **Validated:** passed a realistic multi-step evaluation with held-out tasks.

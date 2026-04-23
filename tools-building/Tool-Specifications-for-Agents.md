# Effective Tools for Coding Agents — Design Specification

**Scope:** Standards for tools exposed to coding agents (Claude Code and similar) via a CLI or MCP server. Covers naming, schema design, return values, error messages, and token discipline.

**Source basis:** Anthropic Engineering, *Writing effective tools for agents — with agents* (Sep 2025); Claude API tool-use documentation; Claude Code best practices.

---

## 1. Core Philosophy

A tool is a **contract between a deterministic system and a non-deterministic agent**. Unlike a traditional API — where the caller's behavior is fixed — the caller here is an LLM that may hallucinate parameters, misread purpose, or pick the wrong tool entirely. Every design decision in this spec exists to reduce that uncertainty.

Three guiding heuristics:

1. **Design for how agents reason, not how APIs are structured.** A tool is not a thin wrapper over an endpoint; it is a workflow primitive shaped around the agent's context window and decision process.
2. **Spend context like money.** Coding agents have finite working memory. Every token in a tool name, description, parameter, or response is paid for.
3. **Optimize with evaluations, not intuition.** Small refinements to descriptions and schemas often yield large shifts in reliability. Changes without evals are guesses.

---

## 2. Tool Selection — What to Build (and Not Build)

### 2.1 Build high-leverage tools, not API wrappers

Do not expose every endpoint your system has. Expose the **small set of tools that match the workflows a coding agent actually performs.** A `list_all_files` tool that returns a 10,000-line directory dump wastes context. A `search_files` tool that returns the five matches the agent needs does not.

### 2.2 Consolidate chained operations

When agents reliably call tools in a fixed sequence, merge them. Typical examples for a coding CLI:

- Prefer `find_symbol(name)` over `list_files` → `read_file` → grep.
- Prefer `run_tests(pattern)` over `discover_tests` → `filter_tests` → `execute`.
- Prefer `apply_patch(path, diff)` over `read_file` → `compute_diff` → `write_file`.

Each consolidation removes an intermediate output from context and a branch point where the agent can go wrong.

### 2.3 Keep the tool set small

Overlapping or ambiguous tools degrade selection accuracy. If two tools could plausibly answer the same request, collapse or differentiate them. Target the minimum set that covers real tasks — add tools only when an evaluation demonstrates need.

---

## 3. Naming Conventions

### 3.1 Namespace with a prefix

Every tool must carry a namespace prefix that identifies its service and, where helpful, its resource:

```
<service>_<action>              # git_status, git_commit
<service>_<resource>_<action>   # repo_files_search, repo_symbols_find
```

Namespacing has a measurable effect on tool-selection accuracy when many tools are present. Prefix-based schemes generally outperform suffix-based ones, but verify with your own eval.

### 3.2 Name actions, not endpoints

Tool names should read as **verbs the agent would choose in a plan**. Prefer `search_logs` over `get_log_entries`, `schedule_meeting` over `create_calendar_event_v2`.

### 3.3 Name rules

- Lowercase, snake_case.
- Start with a verb (`search_`, `run_`, `apply_`, `list_`, `read_`, `write_`).
- No version numbers or internal service codes in the name.
- No synonyms across your tool set (`find_*` vs `search_*` vs `lookup_*` — pick one).
- Names should be unambiguous when read in isolation, without the description.

### 3.4 Distinguish tools that look similar

Pairs like `notification_send_user` and `notification_send_channel` are the single most common source of wrong-tool selection. If two tools differ only by target type, make the distinction prominent in both the name and the first sentence of the description.

---

## 4. Input Schema Design

### 4.1 Parameter naming

- Be **specific about type in the name**: `user_id`, not `user`; `file_path`, not `file`; `max_results`, not `limit`.
- Use the same parameter name for the same concept across every tool in your surface. Inconsistency (`path` here, `filepath` there, `file` elsewhere) produces malformed calls.
- Boolean parameters must read true-as-intended: `include_hidden: true` not `hidden: true`.

### 4.2 Schema hygiene

- Use JSON Schema with `strict: true` where the platform supports it, so calls that don't match the schema are rejected before they reach your code.
- Every parameter has a `description`. No exceptions — the description is the agent's only disambiguator when parameter names collide.
- Use `enum` for any parameter with a fixed value set. Free-form strings that should be one of N values are a common source of malformed calls.
- Mark required vs. optional explicitly. Provide defaults for optional parameters in the description, not only in the runtime code.
- Prefer shallow schemas. Deeply nested objects are error-prone; flatten where you can.

### 4.3 Expose a response_format control

For tools whose output has both human-readable and machine-readable consumers, expose a `response_format` enum:

```json
{
  "response_format": {
    "type": "string",
    "enum": ["concise", "detailed"],
    "default": "concise",
    "description": "Use 'concise' for human-readable summaries; 'detailed' to include IDs needed for follow-up tool calls."
  }
}
```

This lets the agent request IDs only when it plans to chain another call, saving tokens on exploratory reads.

### 4.4 Pagination and limits are parameters, not afterthoughts

Any tool that could return a large result set must expose:

- `max_results` (with a sensible default, typically 20–50)
- `offset` or `cursor` for continuation
- `filter` parameters that narrow results at the source

Defaults should cap output well below your token budget.

---

## 5. Return Value Conventions

### 5.1 Return high-signal context only

Strip fields that don't inform the agent's next action. Drop `uuid`, `etag`, `created_at_microseconds`, `internal_revision_id`, `mime_type_extended`, and similar low-value fields unless they are needed for a subsequent tool call. Keep fields the agent will reason over: `name`, `path`, `summary`, `status`, `error_reason`.

### 5.2 Prefer semantic identifiers over opaque IDs

Agents handle natural-language identifiers far better than alphanumeric UUIDs. Where you control the identifier space, resolve UUIDs to meaningful names or a 0-indexed scheme before returning them. When downstream tool calls genuinely need the opaque ID, return it only in `detailed` mode.

### 5.3 Choose the response structure deliberately

XML, JSON, and Markdown each perform differently depending on task and model. There is no universal winner. Pick one **per tool** based on evaluation:

- **Structured data the agent will parse:** JSON.
- **Code, diffs, file contents:** Markdown with fenced blocks.
- **Mixed content with sections:** XML tags are often easier for the model to navigate.

Document the choice in the tool description so the agent knows what to expect.

### 5.4 Keep responses bounded

Default cap: **25,000 tokens per tool response** (matching Claude Code's own default). Any tool that might exceed this must truncate and communicate clearly that truncation occurred, along with how to retrieve the rest.

### 5.5 Truncation messages are instructional

When you truncate, don't just cut off — tell the agent what to do next:

> Response truncated at 25,000 tokens. Showing first 120 of 847 matches. Narrow your query with the `path_glob` parameter, or paginate with `offset=120`.

---

## 6. Error Message Conventions

Error messages are read by the agent and directly shape its next action. Treat them as prompts, not as logs.

### 6.1 Required structure

Every error response should include:

1. **What went wrong** — in plain language.
2. **Why it went wrong** — the specific cause, not a generic code.
3. **What to do next** — concrete, actionable guidance naming the parameter or tool to use.

### 6.2 Good vs. bad examples

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

### 6.3 Rules

- Never return raw stack traces to the agent. Log them server-side; return a distilled message.
- Never return only an error code. Always include human-readable text.
- Name the offending parameter explicitly.
- Suggest the corrective tool call when one exists.
- If the error is recoverable by retry (rate limits, transient network), say so and include a suggested wait.

### 6.4 Validate early, fail loudly

Do parameter validation before touching any external system. An invalid-parameter error returned quickly with clear guidance is far more useful than a timeout 30 seconds in.

---

## 7. Tool Descriptions — Prompt Engineering the Spec

Tool descriptions sit permanently in the agent's context. They are prompt-engineering surface, not documentation.

### 7.1 Write for a new hire

Describe the tool the way you'd explain it to someone joining your team this week: make implicit context explicit — query formats, domain terminology, relationships between resources, when *not* to use this tool.

### 7.2 Structure

A good tool description has, roughly:

1. **One-line purpose.** What the tool does, in the agent's voice: *"Search the indexed codebase for symbol definitions."*
2. **When to use it.** One or two scenarios.
3. **When NOT to use it.** Disambiguation against sibling tools. This is frequently the highest-value section.
4. **Parameter notes.** Anything not obvious from the parameter schema — accepted formats, defaults, interactions between parameters.
5. **Return shape summary.** What the agent will get back, including the effect of `response_format`.

### 7.3 Worked example

```
name: repo_symbols_find

description: |
  Locate definitions of a function, class, type, or variable across the
  indexed repository. Returns file paths, line numbers, and a short
  signature for each match.

  Use when: the agent needs to find where something is defined before
  reading or editing it.

  Do NOT use when: the agent needs to find *references* to a symbol —
  use repo_symbols_references for that. Do not use for plain text search
  — use repo_files_search.

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

### 7.4 Refinements compound

Minor wording changes in descriptions have produced significant gains on real benchmarks — the SWE-bench Verified result for Claude Sonnet 3.5 credited precise description refinements as a major factor. Treat description edits as first-class changes and run them through your eval.

---

## 8. Token Efficiency Checklist

Before shipping a tool, verify:

- [ ] Tool description is under ~400 tokens.
- [ ] Parameter schema has no redundant properties.
- [ ] Default response size is well under 25,000 tokens for typical inputs.
- [ ] `response_format: concise` is genuinely concise (aim for ≤⅓ the detailed size).
- [ ] Opaque IDs are omitted unless the agent needs them for chaining.
- [ ] Truncation messages tell the agent how to continue.
- [ ] Errors are short and actionable.

---

## 9. Evaluation Workflow

Every non-trivial tool change should pass through this loop:

1. **Build the prototype.** Wire it into a local MCP server or pass it directly via the Anthropic API. Connect it to Claude Code with `claude mcp add <name> <command>` for hands-on testing.
2. **Generate realistic eval tasks.** Inspired by real workflows, not toy cases. Strong tasks require multiple tool calls and realistic data. Weak tasks (e.g., "look up record 12345") won't expose problems.
3. **Pair each task with a verifier.** Exact-match where possible, LLM-judge where not. Avoid verifiers that punish harmless formatting differences.
4. **Run agents in a loop.** Simple `while` loop of LLM call → tool call → tool result. Enable interleaved thinking to surface reasoning.
5. **Collect metrics beyond accuracy.** Tool-call count, tokens consumed, error rate, wall-clock time. Redundant calls point to missing pagination; frequent parameter errors point to unclear descriptions.
6. **Feed transcripts back into Claude Code** to propose refactors. The model is effective at identifying contradictions across tool descriptions and improving self-consistency.
7. **Hold out a test set.** To avoid overfitting descriptions to the training tasks.

---

## 10. Summary — Design Checklist

A tool is ready to ship when:

- **Naming:** namespaced, verb-led, unambiguous against siblings.
- **Schema:** every parameter has a description, enums where possible, `strict: true` on.
- **Inputs:** specific names (`user_id`, not `user`), pagination exposed, `response_format` where relevant.
- **Outputs:** high-signal fields only, semantic IDs over UUIDs, bounded size, structure matches the content.
- **Errors:** plain-language cause + specific fix, no raw stack traces, name the parameter.
- **Description:** purpose, when-to-use, when-NOT-to-use, parameter notes, return shape.
- **Validated:** passed a realistic multi-step evaluation with held-out tasks.

---

## References

- Anthropic Engineering — *Writing effective tools for agents — with agents*: https://www.anthropic.com/engineering/writing-tools-for-agents
- Claude API — *How to implement tool use*: https://docs.claude.com/en/docs/agents-and-tools/tool-use/implement-tool-use
- Anthropic Engineering — *Claude Code best practices*: https://www.anthropic.com/engineering/claude-code-best-practices
- Anthropic Engineering — *Advanced tool use*: https://www.anthropic.com/engineering/advanced-tool-use
- Model Context Protocol: https://modelcontextprotocol.io

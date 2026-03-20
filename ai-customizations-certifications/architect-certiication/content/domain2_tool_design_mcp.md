# Domain 2: Tool Design & MCP Integration
**Weight: 18% of scored content**

---

## Overview

This domain tests your ability to design tools Claude can reliably select and use, configure MCP servers, write structured error responses, and choose between built-in and custom MCP tools. Poor tool design is one of the most common causes of production agent failures.

**Source coverage:** The MCP specification at `modelcontextprotocol.io`, Claude Code MCP integration docs, and the Anthropic article on *Advanced Tool Use* and *Code Execution with MCP* map directly to this domain.

---

## 2.1 Effective Tool Interface Design

### Why Tool Descriptions Are Critical

Tool descriptions are the **primary mechanism Claude uses to select tools**. Minimal, vague, or overlapping descriptions lead to misrouting in production.

### Anatomy of a Good Tool Description

Every description should clearly specify:
1. **Purpose** — What does this tool do?
2. **When to use it** — What triggers should invoke this tool?
3. **Input format** — Identifiers, formats, types it accepts
4. **Outputs** — What fields are returned?
5. **Boundaries** — When should you NOT use this tool?
6. **Edge cases** — What happens with unusual inputs?

### Before and After: Improving Tool Descriptions

```python
# ❌ BEFORE: Both tools accept identifiers — Claude cannot distinguish them
tools = [
    {"name": "get_customer",  "description": "Retrieves customer information"},
    {"name": "lookup_order",  "description": "Retrieves order details"}
]

# ✅ AFTER: Each description clearly defines purpose, scope, and boundaries
tools = [
    {
        "name": "get_customer",
        "description": (
            "Retrieves a verified customer profile by customer email or customer ID. "
            "Use for identity verification before account operations. "
            "Returns: customer_id (verified), name, email, account_status, tier. "
            "Input: customer_id (CUS_XXXXX) or email address. "
            "Do NOT use for order lookups — use lookup_order instead."
        )
    },
    {
        "name": "lookup_order",
        "description": (
            "Retrieves order details by order number or tracking number. "
            "Use when a customer asks about a specific order, shipment, or delivery. "
            "Requires verified customer_id from get_customer. "
            "Returns: order_id, items, status, tracking, estimated_delivery, amount. "
            "Do NOT use for customer profile lookups — use get_customer instead."
        )
    }
]
```

### Splitting Overlapping Tools

```python
# ❌ BEFORE: Near-identical descriptions cause constant misrouting
"analyze_document" — "Analyzes a document"
"analyze_content"  — "Analyzes content"  # Claude cannot distinguish these

# ✅ AFTER: Distinct purpose-specific tools with defined contracts
"extract_data_points"         — "Extracts quantitative data from research papers"
"summarize_content"           — "Produces structured summary of a document's key claims"
"verify_claim_against_source" — "Cross-references a specific claim against document evidence"
```

### System Prompt Keyword Sensitivity

System prompt wording can accidentally override well-written tool descriptions. If the system prompt uses keywords that match a tool name, Claude may route to that tool regardless of intent. Review system prompts for accidental keyword associations.

---

## 2.2 Structured Error Responses for MCP Tools

### The MCP `isError` Pattern

MCP tools communicate failures using the `isError` flag. Structured error responses enable intelligent recovery decisions by the agent.

### Error Categories and Agent Actions

| Category | Characteristics | Agent Action |
|---|---|---|
| **Transient** | Timeout, service unavailable | Retry with backoff |
| **Validation** | Invalid input, missing required field | Do not retry; fix the input |
| **Business** | Policy violation, authorization limit | Do not retry; explain to user or escalate |
| **Permission** | Access denied, authentication failed | Do not retry; escalate |

### Reference Error Response Structure

```python
def process_refund_tool(order_id: str, amount: float) -> dict:

    # Business rule violation — non-retryable
    if amount > 500:
        return {
            "isError": True,
            "errorCategory": "business",
            "isRetryable": False,
            "message": (
                f"Refund of ${amount:.2f} exceeds the $500 automated authorization "
                "limit. This requires manager approval. Please escalate or offer a "
                "partial refund up to $500."
            ),
            "suggested_action": "escalate_to_human"
        }

    # Transient infrastructure failure — retryable
    try:
        return payment_service.refund(order_id, amount)
    except TimeoutError:
        return {
            "isError": True,
            "errorCategory": "transient",
            "isRetryable": True,
            "message": "Payment service timeout. Retry is safe.",
            "retry_after_seconds": 30
        }
```

### Access Failure vs. Valid Empty Result

This distinction is a recurring exam scenario:

| Situation | Correct Response |
|---|---|
| **Access failure** (timeout, network error) | `isError: true`, `errorCategory: "transient"`, `isRetryable: true` |
| **Valid empty result** (query succeeded, no matches) | `isError: false`, `results: []`, explanatory message |

```python
# ❌ WRONG: Identical structure hides important distinction
return {"results": [], "isError": False}  # Was this a timeout or genuinely no results?

# ✅ CORRECT: Explicit distinction enables correct coordinator decisions
# Access failure:
return {
    "isError": True, "errorCategory": "transient", "isRetryable": True,
    "message": "Database connection timed out — query was not executed"
}

# Valid empty result:
return {
    "isError": False, "results": [],
    "message": "Query executed successfully. No orders matched these criteria."
}
```

### Local Recovery Before Propagation

Subagents should handle transient errors locally (with retries). Only propagate errors they cannot resolve — and include context about what was attempted and any partial results.

```python
def search_with_recovery(query: str) -> dict:
    for attempt in range(3):
        try:
            return {"success": True, "results": search_tool(query)}
        except TransientError:
            if attempt == 2:
                return {
                    "isError": True,
                    "errorCategory": "transient",
                    "failure_type": "search_timeout",
                    "attempted_query": query,
                    "partial_results": [],
                    "alternative_approaches": [
                        "Narrow the query",
                        "Use document_search instead of web_search"
                    ]
                }
            time.sleep(2 ** attempt)
```

---

## 2.3 Tool Distribution and `tool_choice` Configuration

### The Too-Many-Tools Problem

Giving an agent all 18 available tools degrades selection reliability:
- Decision complexity scales with tool count
- Agents with out-of-scope tools tend to misuse them (synthesis agents call web search; search agents attempt synthesis)

**Principle of Least Privilege:** Each agent gets only the tools needed for its role.

### Role-Based Tool Sets

```python
coordinator_tools = ["Task", "compile_report", "notify_human"]
search_agent_tools = ["web_search", "fetch_url"]
analysis_agent_tools = ["read_document", "extract_text", "parse_table"]

# Synthesis agent: core role + scoped cross-role tool for the 85% simple case
synthesis_agent_tools = [
    "write_report",
    "verify_fact"  # Scoped cross-role tool — handles simple fact lookups
    # Complex verifications still route through coordinator to web_search agent
]
```

### `tool_choice` Configuration Options

| Value | Behavior | Use Case |
|---|---|---|
| `"auto"` (default) | Model decides whether to call a tool or return text | Most interactions |
| `"any"` | Model **must** call a tool (its choice) | Guarantee structured output; never allow plain text response |
| `{"type": "tool", "name": "X"}` | Model **must** call tool X | Force a specific prerequisite step |

### Forced Tool Selection Pattern

```python
# Step 1: Force metadata extraction before any enrichment
response = client.messages.create(
    model="claude-opus-4-6",
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_metadata"},  # Must run first
    messages=[{"role": "user", "content": document}]
)

# Step 2: Process extracted metadata, then allow flexible enrichment
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": [tool_result]})

response2 = client.messages.create(
    model="claude-opus-4-6",
    tools=enrichment_tools,
    tool_choice="auto",  # Flexible selection for subsequent steps
    messages=messages
)
```

---

## 2.4 MCP Server Configuration

### Scoping: Project vs. User Level

| Scope | Config File | Shared via Git? | Use Case |
|---|---|---|---|
| **Project** | `.mcp.json` (repo root) | ✅ Yes | Team-wide shared tools (GitHub, Jira, internal APIs) |
| **User** | `~/.claude.json` | ❌ No | Personal or experimental servers |

### Project-Level `.mcp.json` Configuration

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-jira"],
      "env": {
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "JIRA_BASE_URL": "${JIRA_BASE_URL}"
      }
    }
  }
}
```

**Key:** Environment variable expansion (`${GITHUB_TOKEN}`) keeps secrets out of version control. Values come from the user's shell environment at runtime.

### Tool Discovery

All tools from all configured MCP servers are discovered at **connection time**. Three MCP servers → all their tools available simultaneously from the first request.

### MCP Resources vs. MCP Tools

| Primitive | Who Controls It | Purpose | Example |
|---|---|---|---|
| **Tools** | Model decides when to call | Perform actions; retrieve specific data | `search_orders`, `create_ticket` |
| **Resources** | Application exposes | Content catalogs; reduce exploratory calls | Issue summary list; documentation hierarchy; DB schema |

**Key exam point:** Use **MCP resources** to give agents visibility into available data *without requiring exploratory tool calls*. Exposing a sprint's issue catalog as a resource means the agent doesn't need to call search to discover what exists.

### Enhancing MCP Tool Descriptions for Adoption

```python
# ❌ Weak — Claude uses Grep instead
"search_codebase": "Searches the codebase"

# ✅ Strong — explains why this beats Grep
"search_codebase": (
    "Semantic search across the entire codebase with symbol tables and cross-file "
    "reference graphs. Returns ranked results with file paths, line numbers, and "
    "surrounding context. Significantly more powerful than Grep for finding usage "
    "patterns, tracing data flow, and understanding architectural relationships."
)
```

### Custom vs. Community MCP Servers

Use **existing community servers** (Jira, GitHub, Slack, Google Drive) for standard integrations. Build custom servers only for team-specific workflows not covered by the community ecosystem.

---

## 2.5 Built-In Tools: Selection Reference

### Tool Purpose Matrix

| Tool | Purpose | When to Use |
|---|---|---|
| **Grep** | Content search — searches *inside* files | Find function callers; locate error messages; find imports |
| **Glob** | Path matching — finds files *by name/extension* | `**/*.test.tsx`; all Python files in a directory |
| **Read** | Load full file contents | Read a specific file for complete content |
| **Write** | Create or overwrite a complete file | New files; overwrite when Edit fails |
| **Edit** | Targeted modification via unique anchor text | Small targeted changes to existing files |
| **Bash** | Execute shell commands | Run tests; run scripts; system operations |

### Grep vs. Glob: The Critical Distinction

```bash
# Grep: Searches INSIDE files for a content pattern
Grep("function processRefund", path="src/")
# → Returns: all files CONTAINING the text "function processRefund"

# Glob: Matches FILE PATHS by name/extension pattern
Glob("**/*.test.tsx")
# → Returns: all .test.tsx files in the tree (does NOT look inside files)
```

**Common exam mistake:** Using Glob to search for content (it only matches file names). Using Grep to find files by name (it searches content, not paths).

### Edit vs. Read+Write Fallback

```python
# Edit: Fast when anchor text appears exactly once
Edit(
    file="src/config.ts",
    old_str="const MAX_REFUND = 100;",
    new_str="const MAX_REFUND = 500;"
)

# If Edit fails due to non-unique anchor text → fall back to Read + Write
content = Read("src/config.ts")
modified = content.replace("const MAX_REFUND = 100;", "const MAX_REFUND = 500;")
Write("src/config.ts", modified)
```

### Incremental Codebase Understanding

Build understanding incrementally — don't read all files upfront:

```
1. Grep("processRefund")      → Find entry points in codebase
2. Read(entry_point_file)     → Understand the main function
3. Grep(imported_dependency)  → Trace to the dependency
4. Read(dependency_file)      → Understand the dependency
... continue following the code path as needed
```

This conserves context window space and avoids loading irrelevant files.

---

## Exam Practice Questions

**Q1:** Your agent frequently calls `get_customer` when users mention order numbers. Both tools have minimal descriptions. What is the most effective first step?
> **B** — Expand each tool's description to include input formats, example queries, edge cases, and boundaries. Tool descriptions are the primary selection mechanism. Few-shot examples (A) add overhead without fixing the root cause.

**Q2:** Your synthesis agent keeps attempting web searches. It has access to all 18 tools. Best fix?
> Restrict the synthesis agent's tool set to only synthesis-relevant tools (e.g., `write_report`, `verify_fact`). Giving agents out-of-scope tools degrades selection reliability.

**Q3:** You need to guarantee `extract_metadata` runs before any enrichment tool. How?
> Use `tool_choice: {"type": "tool", "name": "extract_metadata"}` in the first request. Switch to `"auto"` for follow-up enrichment steps.

**Q4:** A search subagent times out. How should it report this to the coordinator?
> Return structured error context: `errorCategory: "transient"`, the attempted query, any partial results, and alternative approaches. Do NOT return an empty success result — that hides the failure.

---

## Key Terms Checklist

- [ ] Tool description anatomy: purpose, inputs, outputs, boundaries, edge cases
- [ ] `isError` flag for MCP tool failures
- [ ] Error categories: transient / validation / business / permission
- [ ] `isRetryable` boolean
- [ ] Access failure vs. valid empty result
- [ ] `tool_choice` options: `"auto"`, `"any"`, forced `{"type": "tool", "name": "..."}`
- [ ] `.mcp.json` — project-scoped config (shared via git)
- [ ] `~/.claude.json` — user-scoped config (personal)
- [ ] Environment variable expansion (`${VAR}`) for credentials
- [ ] MCP Resources vs. MCP Tools distinction
- [ ] Grep (content search) vs. Glob (path matching)
- [ ] Edit anchor uniqueness; Read+Write fallback
- [ ] Principle of least privilege for agent tool sets

---

## Recommended Sources

| Source | Focus |
|---|---|
| [What is MCP?](https://modelcontextprotocol.io) | MCP primitives: tools, resources, prompts |
| [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25) | isError flag; tool interface contracts |
| [Claude Code Advanced Setup](https://docs.anthropic.com/en/docs/claude-code/advanced-setup) | .mcp.json config; environment variables |
| [Introducing Advanced Tool Use](https://www.anthropic.com/research/advanced-tool-use) | tool_choice options; forced selection |
| [Code Execution with MCP](https://www.anthropic.com/research/code-execution-mcp) | Scaling MCP; reducing context overhead |
| Exam Guide — Task Statements 2.1–2.5 (Pages 9–12) | Authoritative task definitions |

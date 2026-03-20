# Domain 1: Agentic Architecture & Orchestration
**Weight: 27% of scored content — the most heavily tested domain**

---

## Overview

Agentic architecture is the backbone of every production Claude deployment. This domain tests your ability to design systems where Claude autonomously reasons, takes actions, and recovers from failures. Questions are scenario-based and require practical judgment: diagnosing broken agentic loops, designing multi-agent pipelines, and choosing between programmatic enforcement versus prompt-based guidance.

**Source coverage:** *Building Effective AI Agents*, the Claude Agent SDK docs, *How We Built Our Multi-Agent Research System*, and *Effective Context Engineering* all map directly to this domain. Supplement with hands-on SDK experience.

---

## 1.1 The Agentic Loop Lifecycle

### Core Concept
An agentic loop is the cycle where Claude receives a task, calls tools to make progress, and continues until the task is complete. The loop is driven entirely by the API's `stop_reason` field — there is no other reliable termination signal.

### The Two Critical Stop Reasons

| `stop_reason` | Meaning | Correct Action |
|---|---|---|
| `"tool_use"` | Claude wants to call one or more tools | Execute the tools, append results, send the next request |
| `"end_turn"` | Claude has finished its task | Terminate the loop and return the final response |

### Reference Implementation

```python
messages = [{"role": "user", "content": task}]

while True:
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )

    # ALWAYS append the full assistant response to history
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        break  # Task complete — exit

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        messages.append({"role": "user", "content": tool_results})
        # Loop continues — next iteration includes updated messages
```

### Anti-Patterns (Exam Distractors)

| Anti-Pattern | Why It Fails |
|---|---|
| Parsing natural language to detect loop completion | Fragile — model phrasing varies |
| Arbitrary iteration cap as the *primary* stopping mechanism | Terminates valid long-running tasks prematurely |
| Checking for assistant text content as a completion signal | Text is always present; not a reliable signal |
| Not passing full conversation history each request | Claude has no memory between API calls |

### Key Insight
Claude reasons about what to do next by reading the *entire accumulated conversation*, including all prior tool results. This is model-driven decision-making — not a scripted decision tree.

---

## 1.2 Multi-Agent Orchestration: Coordinator-Subagent Patterns

### Hub-and-Spoke Architecture

```
         ┌─────────────────────────────┐
         │      Coordinator Agent      │
         │  · Decomposes the task      │
         │  · Delegates to subagents   │
         │  · Aggregates results       │
         │  · Handles all errors       │
         └──────┬──────┬──────┬────────┘
                │      │      │
          ┌─────▼─┐ ┌──▼──┐ ┌▼──────┐
          │Search │ │Docs │ │Synth  │
          │Agent  │ │Agent│ │Agent  │
          └───────┘ └─────┘ └───────┘
```

### Coordinator Responsibilities

1. Analyze query requirements and **dynamically select** which subagents to invoke
2. Route **all inter-subagent communication** through itself — no direct agent-to-agent calls
3. Manage **scope partitioning** to minimize duplicate work
4. Implement **iterative refinement**: evaluate synthesis output → re-delegate for gaps → re-invoke synthesis
5. Handle **error propagation** and decide recovery strategy

### What Subagents Do NOT Have

- They do **not** receive the coordinator's conversation history automatically
- They do **not** share memory between invocations
- They do **not** communicate directly with peer subagents

### Critical Exam Scenario: Narrow Task Decomposition

> A coordinator decomposes "impact of AI on creative industries" into: "AI in digital art," "AI in graphic design," "AI in photography." The final report misses music, writing, and film.

**Root cause: The coordinator's task decomposition is too narrow.** Subagents performed correctly within their assigned scope. This is a coordinator design bug. Choices blaming the search agent, synthesis agent, or document analysis agent are wrong.

---

## 1.3 Subagent Invocation, Context Passing, and Spawning

### The Task Tool

Subagents are spawned via the **Task tool**. The coordinator's `allowedTools` **must include `"Task"`** — without this, subagent spawning fails.

```python
coordinator_config = AgentDefinition(
    description="Research coordinator",
    system_prompt="Orchestrate research by delegating to specialized subagents.",
    allowed_tools=["Task", "compile_report"]  # Task is mandatory
)
```

### Explicit Context Passing

Subagents receive **only what you put in their prompt**. Nothing is inherited.

```python
# ❌ WRONG — Subagent has no context
spawn_subagent("synthesis_agent", prompt="Please synthesize the research.")

# ✅ CORRECT — Pass all findings explicitly
spawn_subagent(
    "synthesis_agent",
    prompt=f"""
    Synthesize the following findings into a comprehensive report.
    Preserve all source attributions in your output.

    Web Search Results:
    {web_search_findings}

    Document Analysis:
    {document_analysis_findings}
    """
)
```

### Structured Context Format

Use structured data to separate content from metadata. This preserves attribution for downstream synthesis.

```json
{
  "findings": [
    {
      "claim": "AI reduces entry-level creative roles by ~18%",
      "source_url": "https://example.com/study",
      "document_name": "Creative_Industry_Report_2024.pdf",
      "page_number": 14,
      "publication_date": "2024-03-15"
    }
  ]
}
```

### Parallel Subagent Execution

Emit **multiple Task tool calls in a single coordinator response** — not across separate turns. Separate turns force sequential execution.

```
# Single response → parallel execution (correct)
[Task("search: AI in music"), Task("search: AI in film"), Task("search: AI in writing")]

# Separate responses → sequential execution (slow, avoid)
Turn 1: Task("search: AI in music")
Turn 2: Task("search: AI in film")    ← waits for turn 1
```

### Session Management

| Mechanism | When to Use |
|---|---|
| `--resume <session-name>` | Continue a named session when prior context is still valid |
| `fork_session` | Branch from a shared baseline to explore divergent approaches |
| New session + injected summary | When prior tool results are stale or significant code changes occurred |

**Tip:** When resuming after code modifications, explicitly tell the agent which files changed. Do not force a full re-exploration.

---

## 1.4 Multi-Step Workflows: Enforcement and Handoff Patterns

### Programmatic Enforcement vs. Prompt-Based Guidance

| Approach | Reliability | Use When |
|---|---|---|
| Programmatic prerequisites (code gates) | Deterministic — 100% | Financial operations; identity verification; safety-critical ordering |
| Prompt instructions | Probabilistic — ~70–95% | Style preferences; guidelines; soft constraints |

### Prerequisite Gate Pattern

```python
def process_refund_tool(order_id: str, context: dict) -> dict:
    # Programmatic gate — cannot be bypassed by the model
    if not context.get("verified_customer_id"):
        return {
            "isError": True,
            "errorCategory": "validation",
            "isRetryable": False,
            "message": "Customer verification required. Call get_customer first."
        }
    return execute_refund(order_id, context["verified_customer_id"])
```

### Why Prompts Alone Are Insufficient for Critical Ordering

Even with perfect prompt instructions and few-shot examples, compliance rates are probabilistic. When errors have financial or legal consequences, use programmatic gates. On the exam, choices that suggest "add a system prompt instruction" or "add few-shot examples" are wrong when 100% compliance is required.

### Structured Handoff Summaries

When escalating to a human agent, compile a structured handoff. Human agents may not have transcript access.

```
Customer ID:       CUS_12345 (verified)
Order ID:          ORD_98765
Issue:             Disputed charge of $247.50 — item arrived damaged
Evidence:          Photo submitted by customer (damage confirmed)
Recommended:       Process full refund to original payment method
SLA Status:        Within 48-hour response window
```

### Multi-Concern Request Decomposition

1. **Decompose** the request into distinct items
2. **Investigate each in parallel** using shared context
3. **Synthesize** a unified response addressing all concerns

---

## 1.5 Agent SDK Hooks

### Hook Types

| Hook | Fires | Primary Use |
|---|---|---|
| `PostToolUse` | After tool executes, before model sees result | Normalize heterogeneous data formats |
| `PreToolUse` (interception) | Before tool executes | Enforce business rules; block policy violations |

### PostToolUse: Data Normalization

Different MCP tools often return data in different formats. Normalize in the hook before the model processes results.

```python
@agent.post_tool_use
def normalize_order_data(tool_name: str, result: dict) -> dict:
    if tool_name == "get_order":
        # Unix timestamp → ISO 8601
        if isinstance(result.get("created_at"), int):
            result["created_at"] = datetime.utcfromtimestamp(
                result["created_at"]
            ).isoformat()
        # Numeric status code → readable string
        result["status"] = {1: "active", 2: "cancelled", 3: "completed"}.get(
            result.get("status_code"), "unknown"
        )
    return result
```

### Tool Call Interception: Business Rule Enforcement

```python
@agent.pre_tool_use
def enforce_refund_limit(tool_name: str, inputs: dict) -> dict:
    if tool_name == "process_refund" and inputs.get("amount", 0) > 500:
        raise PolicyViolationError(
            "Refund exceeds $500 authorization limit. Escalating to human agent."
        )
    return inputs
```

### Hooks vs. Prompts: Decision Framework

**Use hooks when:** the rule requires guaranteed compliance, failure has real-world consequences, or the constraint is binary.

**Use prompts when:** the constraint is a preference, occasional deviation is acceptable, or the rule requires contextual judgment.

---

## 1.6 Task Decomposition Strategies

### When to Use Each Pattern

| Pattern | Best For |
|---|---|
| **Prompt chaining** (fixed sequential) | Predictable reviews; known multi-step processes |
| **Dynamic adaptive decomposition** | Open-ended tasks where findings drive next steps |

### Prompt Chaining for Code Reviews

Split large reviews to avoid attention dilution:

```
Pass 1: Analyze each file individually → local issues (bugs, style)
Pass 2: Cross-file integration pass → API contracts, data flow, shared state
```

This prevents inconsistent depth across files and contradictory feedback about the same pattern.

### Dynamic Decomposition for Open-Ended Tasks

```
Phase 1: Map codebase structure
Phase 2: Identify high-impact areas (fewest tests, most complexity)
Phase 3: Create prioritized plan based on Phase 2 findings
Phase 4: Execute (adapts as dependencies are discovered)
```

---

## Exam Practice Questions

**Q1:** Your production agent skips `get_customer` in 12% of cases. What's the most effective fix?
> **A** — Programmatic prerequisite blocking `lookup_order` until `get_customer` returns a verified customer ID. Prompt instructions (B, C) are probabilistic. Routing classifiers (D) address availability, not ordering.

**Q2:** Research system covers only visual arts when asked about "creative industries." Subagents succeed. Root cause?
> **B** — Coordinator task decomposition is too narrow.

**Q3:** How do you execute multiple subagents simultaneously?
> Emit multiple Task tool calls in a **single coordinator response**.

**Q4:** When should you use `fork_session` vs. `--resume`?
> `fork_session` for independent branches from a shared baseline; `--resume` to continue an existing named session.

---

## Key Terms Checklist

- [ ] `stop_reason`: `"tool_use"` vs `"end_turn"`
- [ ] Hub-and-spoke coordinator architecture
- [ ] Task tool — required in `allowedTools` to spawn subagents
- [ ] Context isolation — subagents don't inherit coordinator history
- [ ] Programmatic enforcement vs. prompt-based guidance
- [ ] `PostToolUse` hook — data normalization
- [ ] Tool call interception — business rule enforcement
- [ ] Prompt chaining vs. dynamic decomposition
- [ ] `fork_session` vs. `--resume <session-name>`
- [ ] Parallel execution via single-response multi-Task calls
- [ ] Structured handoff summaries for human escalation
- [ ] Iterative refinement: gap detection → re-delegation → re-synthesis

---

## Recommended Sources

| Source | Focus |
|---|---|
| [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) | Workflows vs. agents; orchestrator-worker pattern |
| [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) | Task tool; subagent spawning; context isolation |
| [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Compaction; multi-agent architectures |
| [How We Built Our Multi-Agent Research System](https://www.anthropic.com/research/multi-agent-research) | Real-world coordinator-subagent design |
| Exam Guide — Task Statements 1.1–1.7 (Pages 4–9) | Authoritative task definitions |

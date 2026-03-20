# Pattern 11.3 — Map-Reduce

> A coordinator fans out over a list (files, modules, endpoints) and invokes a worker sub-agent for each item independently. A reducer aggregates results into a unified output.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Coordinator fans out over a list | Parent agent with `tools: ['agent']` iterates the list |
| Worker sub-agent per item | Sub-agent invoked per item (parallel execution supported) |
| SubagentStop hook logs each result | Parent agent collects results |
| Reducer sub-agent aggregates | Dedicated sub-agent for final aggregation |

## Implementation Fidelity: ✅ High

This is a generalization of Pattern 1.2 (Parallel Fan-out / Fan-in). The parent agent acts as the mapper, worker sub-agents process each item, and a reducer sub-agent aggregates.

---

## Agent Definitions

### `.github/agents/map-reduce-coordinator.agent.md`

```yaml
---
name: Map-Reduce Coordinator
description: >
  Process a list of items in parallel using map-reduce. Each item is
  processed independently by a worker, then results are aggregated.
tools: ['agent', 'search', 'codebase']
agents: ['Item Worker', 'Result Reducer']
---

You are a map-reduce coordinator.

## Map Phase
1. Identify or receive the list of items to process
2. For EACH item, invoke an Item Worker sub-agent with:
   - The specific item to process
   - The processing instructions
   - The expected output format
3. Collect all worker results

## Reduce Phase
4. Invoke the Result Reducer with all collected results
5. Present the unified output

## Error Handling
- If a worker fails on an item, log it and continue with remaining items
- The reducer must handle partial results gracefully
- Report: total items, successfully processed, failed
```

### `.github/agents/item-worker.agent.md`

```yaml
---
name: Item Worker
description: >
  Process a single item from a map-reduce job. Runs in isolation.
tools: ['codebase', 'search', 'terminalLastCommand', 'editFiles']
---

Process the assigned item according to the instructions provided.

Output a structured result:
- **Item**: what was processed
- **Status**: SUCCESS or FAILURE
- **Output**: the processing result
- **Errors**: any issues encountered (empty if none)

Keep your scope strictly to the assigned item. Do not touch
files or resources outside your assignment.
```

### `.github/agents/result-reducer.agent.md`

```yaml
---
name: Result Reducer
description: >
  Aggregate results from multiple map-reduce workers into a unified output.
tools: ['search', 'editFiles']
---

Given results from multiple workers:

1. Validate completeness — were all expected items processed?
2. Aggregate individual results into the requested unified format
3. Handle partial results (some workers may have failed)
4. Compute summary statistics:
   - Total items: X
   - Successful: Y
   - Failed: Z
   - Aggregated metric (if applicable)
5. Highlight any items that need manual attention
```

---

## Concrete Example: Codebase-Wide Analysis

Use map-reduce to analyze every module in a monorepo:

### `.github/prompts/analyze-all-modules.prompt.md`

```yaml
---
mode: agent
description: Analyze every module in the monorepo using map-reduce
tools: ['search', 'codebase', 'terminalLastCommand']
---

1. List all modules: find directories under src/ with their own package.json or __init__.py
2. For each module, analyze:
   - Code quality (lint warnings, type errors)
   - Test coverage
   - Dependency count and health
   - Lines of code and complexity
3. Aggregate into a project health dashboard

Present as a ranked table: healthiest modules first, most troubled last.
```

---

## SDK Implementation: Large-Scale Map-Reduce

For lists too large for a single agent session (e.g., 100+ modules), use the SDK:

```python
import asyncio
from copilot import CopilotClient

async def map_reduce(items: list[str], task_prompt: str):
    client = CopilotClient()
    await client.start()

    # MAP: process each item in a separate session
    async def process_item(item: str):
        session = await client.create_session({
            "model": "claude-sonnet-4.5",
            "instructions": f"Process this single item: {item}"
        })
        result = await session.send_and_wait({"prompt": task_prompt})
        return {"item": item, "result": result.content}

    # Fan out with concurrency limit
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent sessions
    async def bounded_process(item):
        async with semaphore:
            return await process_item(item)

    results = await asyncio.gather(
        *[bounded_process(item) for item in items],
        return_exceptions=True
    )

    # REDUCE: aggregate in a single session
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    reduce_session = await client.create_session({
        "model": "claude-sonnet-4.5",
        "instructions": "Aggregate these results into a summary report."
    })
    final = await reduce_session.send_and_wait({
        "prompt": f"Aggregate {len(successes)} results "
                  f"({len(failures)} failed):\n{successes}"
    })

    print(final.content)
    await client.stop()
```

---

## Key Insight

Map-reduce in Copilot is most effective when:
- Items are truly independent (no cross-dependencies between workers)
- Each item fits within a single sub-agent's context window
- The reduce step can handle partial results

For items with dependencies, use the Sequential Pipeline pattern (1.1) instead.

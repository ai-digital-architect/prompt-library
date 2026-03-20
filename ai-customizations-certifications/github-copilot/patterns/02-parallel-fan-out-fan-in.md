# Pattern 1.2 — Parallel Fan-out / Fan-in

> Independent workers run concurrently against a shared contract. A merge agent reconciles all branches when all workers complete.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Parallel sub-agents with shared `CLAUDE.md` contract | Parent agent with `tools: ['agent']` invoking multiple sub-agents |
| SubagentStop hook (completion tracking) | Parent agent prompt logic (inspect each result before merging) |
| `CLAUDE.md` shared contract | `copilot-instructions.md` + Skill reference for the shared contract |

## Implementation Fidelity: ✅ High

Copilot sub-agents support parallel execution (experimental). The parent agent fans out work to independent sub-agents, each operating in an isolated context, then aggregates results.

---

## File Structure

```
.github/
├── copilot-instructions.md
├── agents/
│   ├── fan-out-coordinator.agent.md
│   ├── module-worker.agent.md
│   └── merge-agent.agent.md
└── skills/
    └── parallel-contract/
        └── SKILL.md
```

## Agent Definitions

### `.github/agents/fan-out-coordinator.agent.md`

```yaml
---
name: Fan-out Coordinator
description: >
  Coordinate parallel work across independent modules. Use when a task can
  be decomposed into independent subtasks that run concurrently.
tools: ['agent', 'search', 'codebase']
agents: ['Module Worker', 'Merge Agent']
---

You are a parallel work coordinator. For each task:

1. Analyze the task and identify independent work units (modules, files, services)
2. For each independent unit, invoke a Module Worker sub-agent with:
   - The specific unit to process
   - The shared contract from the parallel-contract skill
   - Clear success criteria
3. Collect all Module Worker results
4. Invoke the Merge Agent with all collected results to produce the unified output

IMPORTANT: Each Module Worker runs in isolation. They cannot see each other's
work. Design the decomposition so that no worker depends on another worker's output.

If any worker reports a failure, note it in the merge input so the Merge Agent
can handle partial results gracefully.
```

### `.github/agents/module-worker.agent.md`

```yaml
---
name: Module Worker
description: >
  Process a single independent work unit (module, file, or service).
  Operates in isolation — cannot see other workers' outputs.
tools: ['search', 'editFiles', 'terminalLastCommand', 'codebase']
---

You are a focused module worker. You will receive:
- A specific module or file scope to work on
- A shared contract defining output format and quality standards
- Success criteria for your unit

Execute the work within your assigned scope ONLY. Do not touch files
outside your scope. Output your results in the contract-specified format:

## Worker Output Format
- **Scope**: what you were assigned
- **Files modified**: list with brief description of changes
- **Status**: PASS or FAIL
- **Issues**: any problems encountered
- **Output artifact**: the deliverable (code, report, etc.)
```

### `.github/agents/merge-agent.agent.md`

```yaml
---
name: Merge Agent
description: >
  Reconcile and merge results from multiple parallel workers into a
  unified output. Resolves conflicts and produces the final deliverable.
tools: ['search', 'editFiles', 'codebase']
---

You are a merge specialist. You will receive results from multiple
parallel workers. For each merge:

1. Validate that all expected workers reported results
2. Check for conflicts between worker outputs (duplicate definitions,
   incompatible changes, shared file modifications)
3. Resolve conflicts using the project's conventions in copilot-instructions.md
4. Produce the unified output, noting any workers that failed and
   what compensating actions were taken
5. Run a final consistency check across all merged changes

## Conflict Resolution Priority
- Project standards (copilot-instructions.md) take precedence
- If two workers modified the same file, merge at the function level
- If irreconcilable, flag for human review
```

## Supporting Skill

### `.github/skills/parallel-contract/SKILL.md`

```yaml
---
name: parallel-contract
description: >
  Shared contract for parallel fan-out workers. Defines output format,
  quality thresholds, and merge rules. Use when coordinating parallel
  sub-agent work or when a merge agent needs to reconcile results.
---

## Worker Output Contract

Every parallel worker must return a structured result:

```json
{
  "scope": "string — the assigned module or file",
  "status": "PASS | FAIL",
  "files_modified": ["list of file paths"],
  "issues": ["list of problems encountered"],
  "output_summary": "string — brief description of what was done"
}
```

## Merge Rules

- Workers must not modify files outside their assigned scope
- Shared utility files (e.g., `utils/`, `types/`) are READ-ONLY for workers
- Only the Merge Agent may modify shared files after reconciliation
- If a worker needs a shared change, it must document it as an "issue"
  for the Merge Agent to handle
```

---

## SDK Alternative: Programmatic Fan-out

For scenarios requiring precise control over parallelism (e.g., processing 50 modules), use the Copilot SDK:

```python
import asyncio
from copilot import CopilotClient

async def fan_out_fan_in(modules: list[str]):
    client = CopilotClient()
    await client.start()

    # Fan-out: create a session per module
    async def process_module(module: str):
        session = await client.create_session({
            "model": "claude-sonnet-4.5",
            "instructions": f"Process module: {module}. Follow project standards.",
            "skill_directories": ["./.github/skills/parallel-contract/SKILL.md"]
        })
        result = await session.send_and_wait({
            "prompt": f"Analyze and refactor the {module} module."
        })
        return {"module": module, "result": result.content}

    # Execute all modules in parallel
    results = await asyncio.gather(*[process_module(m) for m in modules])

    # Fan-in: merge results
    merge_session = await client.create_session({
        "model": "claude-sonnet-4.5",
        "instructions": "You are a merge specialist. Reconcile parallel results."
    })
    merge_result = await merge_session.send_and_wait({
        "prompt": f"Merge these parallel results:\n{results}"
    })

    print(merge_result.content)
    await client.stop()
```

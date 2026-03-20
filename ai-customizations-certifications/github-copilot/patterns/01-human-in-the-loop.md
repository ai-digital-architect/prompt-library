# Pattern 2.1 — Human-in-the-Loop Approval

> The agent pauses at a defined stage, surfaces a summary to the user, and waits for explicit sign-off before proceeding.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Slash Command that halts and prompts | Handoff with `send: false` (user must click to confirm) |
| PreToolUse hook (exit 2 until sentinel file) | Handoff button — deterministic UI mechanism |
| User sign-off | User clicks the handoff button |

## Implementation Fidelity: ✅ High

Copilot's handoff mechanism is purpose-built for this pattern. Setting `send: false` ensures the user must explicitly click to proceed, providing a natural approval checkpoint.

---

## File Structure

```
.github/
├── agents/
│   ├── proposer.agent.md
│   └── executor.agent.md
└── prompts/
    └── safe-execute.prompt.md
```

## Agent Definitions

### `.github/agents/proposer.agent.md`

```yaml
---
name: Proposer
description: >
  Analyze a task and produce a detailed proposal for human review.
  Does not make changes — only produces a plan.
tools: ['search', 'codebase', 'fetch']
handoffs:
  - label: "Approve & Execute"
    agent: Executor
    prompt: "Execute the approved plan above. Make no deviations."
    send: false
  - label: "Revise Plan"
    agent: Proposer
    prompt: "Revise the plan based on the feedback above."
    send: false
---

You are a planning specialist. For every request:

1. Research the codebase to understand the current state
2. Identify all files that would need to change
3. Estimate the blast radius (what could break)
4. Produce a detailed proposal:

## Proposal Format
- **Summary**: one-sentence description of what will change
- **Files affected**: list with expected modification type (create/modify/delete)
- **Risk assessment**: Low / Medium / High with justification
- **Rollback plan**: how to undo the changes if needed
- **Dependencies**: any prerequisites or downstream effects

Present the proposal and wait for the user to either approve (handoff to
Executor) or request revisions.

DO NOT make any file changes. Your role is analysis and planning only.
```

### `.github/agents/executor.agent.md`

```yaml
---
name: Executor
description: >
  Execute a previously approved plan. Makes the actual code changes.
  Only invoked after human approval via handoff.
tools: ['editFiles', 'terminalLastCommand', 'search']
handoffs:
  - label: "Request Another Review"
    agent: Proposer
    prompt: "Review the changes I just made and confirm they match the plan."
    send: false
---

You are an implementation specialist. You will receive an approved plan
from the Proposer agent.

1. Execute EXACTLY the changes described in the approved plan
2. Make no deviations from the plan without flagging them
3. Run tests after each significant change
4. Report what was done vs. what was planned

If you encounter an issue that requires deviating from the plan, STOP
and explain the deviation before proceeding. Offer a handoff back to
the Proposer for re-planning.
```

### Approval Flow

```
User asks for a change
    ↓
Proposer researches and produces a plan
    ↓ (User reviews the plan in chat)
User clicks [Approve & Execute]     ← Human approval gate
    ↓
Executor implements the approved plan
    ↓
User clicks [Request Another Review] if needed
```

---

## Alternative: Prompt File for Quick Approval Workflows

For lighter-weight approval flows that do not need a full agent persona:

### `.github/prompts/safe-execute.prompt.md`

```yaml
---
mode: agent
description: Propose a change, wait for approval, then execute it safely
tools: ['search', 'codebase', 'editFiles', 'terminalLastCommand']
---

Before making ANY changes:

1. Present a summary of what you plan to do
2. List every file you will modify
3. State the risk level (Low/Medium/High)
4. Ask: "Shall I proceed with these changes?"
5. WAIT for my explicit "yes" or approval before touching any files

If I say "no" or ask for revisions, update the plan and present it again.
Only execute after I explicitly approve.
```

---

## Key Difference from Claude Code

In Claude Code, the human gate is typically implemented via a `PreToolUse` hook that exits with code 2 (blocking the operation) until a sentinel file appears, or via a Slash Command that pauses execution. In Copilot, the handoff mechanism with `send: false` provides a cleaner, more user-friendly equivalent — the approval is a visible button in the UI rather than an invisible hook condition.

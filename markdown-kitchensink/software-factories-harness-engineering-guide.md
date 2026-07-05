# Software Factories in AI-Assisted Coding: A Complete Guide

## Executive Overview

A **software factory** in the context of AI-assisted development is the production system *around* the model—the machinery that turns intent into verified, shipped software **repeatedly and reliably**, not just once. The central problem is not whether an AI model can generate code once, but whether a system can continuously produce, verify, deploy, maintain, and upgrade software across operationally distinct but structurally similar projects.

**Core Equation:** `Agent = Model + Harness`

The harness, not the model, determines how well an AI coding agent performs in production.

---

## Key Concepts

### 1. Harness Engineering

**Definition:** The runtime scaffolding an agent operates inside—file access, terminals, tests, permissions, verification gates.

**Core Principle (Mitchell Hashimoto):** Anytime an agent makes a mistake, engineer a solution so it never makes that mistake again—usually via an improved harness.

**Key Distinction:** 
- **Persuasion (doesn't scale):** "Follow our coding standards" in a prompt = probabilistic compliance
- **Determinism (scales):** Wire a linter that blocks the PR = enforces constraints

**Five-Layer Production Harness:**
1. **Tool orchestration** — File editing, shell execution, browser automation
2. **Verification loops** — Tests, linters, type checkers firing mid-loop
3. **Context and memory** — Rules files, skills, retrieved code, temporal graphs
4. **Guardrails** — Permission boundaries, sandboxing (containers/worktrees), policy gates
5. **Observability** — Telemetry, metrics (cost per merged PR, time-to-merge), evals

### 2. Context Engineering

Curating what enters the context window each turn—the inverse of just-dumping-everything.

**Key artifacts:**
- **Rules files (AGENTS.md/CLAUDE.md)** — Persistent, repository-scoped instruction sets injected at session start; survive across sessions, scope to directory trees, compose hierarchically
  - AGENTS.md is now an open standard (OpenAI, Google, Cursor, Factory, others)
  - OpenAI's own repo uses 88 AGENTS.md files across subcomponents
- **Skills** — Progressive-disclosure instruction packages, loaded just-in-time
- **MCP servers** — Tool access to external systems (GitHub, Slack, databases, etc.)
- **Code graph retrieval** — Static symbols, dependencies, call graphs via LSP/tree-sitter

**Principle:** Budget context deliberately; inject just-in-time rather than front-loading.

### 3. Loop Engineering (Inner & Outer)

The newest and most consequential layer of the stack.

#### Inner Loop
- **What it is:** Perceive state → reason → act → observe → reason again
- **Who builds it:** The harness; you don't build this, you inherit it
- **Timescale:** Seconds to minutes per cycle
- **Best practices:** Decompose tasks small, commit frequently (4x vs. traditional), deterministic gates

#### Outer Loop
- **What it is:** The system that runs the inner loop on a schedule, feeds it work, checks results, decides next steps—without you typing each prompt
- **Who builds it:** You do; this is the factory
- **Timescale:** Hours to weeks per cycle
- **Core insight (Addy Osmani, 2026):** "You shouldn't be hand-prompting coding agents anymore"

#### Self-Improving Loops
The return arrow doesn't just loop back to the top—it reaches inside and updates the inner loop, making each outer cycle more effective:
- Better prompts
- Improved tools
- Augmented memory
- Refined skills library
- Tighter gates based on past failures

#### Recent Architectural Shift
AI agents are **pulling CI feedback into the inner loop**. Traditional CI/CD waits until pull-request time for validation—this turns the outer loop into a backlog of preventable rework. Solution: quality checks must live where the work happens, inside the agent loop.

### 4. Memory Management

Models are stateless; factories aren't.

**Standard decomposition:**
- **Working memory** — Context window + compaction strategies
- **Episodic memory** — Session logs, decisions, execution traces
- **Semantic memory** — Facts about the codebase, organization, patterns
- **Procedural memory** — Learned skills, workflows, successful patterns

**Architecture patterns:**
- **Tiered agent-managed memory (Letta model)** — OS-inspired hierarchy where agents control what stays in working memory vs. long-term storage
- **Vector + Graph hybrid (Mem0, Zep, Cognee)** — Entity relationships + structured knowledge with varying emphasis on temporal reasoning
- **Multi-strategy retrieval (Hindsight)** — Four parallel strategies (semantic, BM25, graph traversal, temporal) with cross-encoder reranking

**Contrarian data point:** Letta found that dumping conversation transcripts into plain files attached to an agent scored 74.0% on LoCoMo multi-session recall, above Mem0's graph variant at 68.5%—agents are post-trained to be good at iterative file search, so specialized memory may add little value at L1.

### 5. Knowledge Graphs

Two distinct kinds matter:

**Static code graphs** — Symbols, dependencies, call graphs (LSP/tree-sitter territory). Input to retrieval but typically read-only per session.

**Temporal context graphs** — Time-bounded facts that evolve. Graphiti is the leading open-source framework:
- ~27k GitHub stars
- Represents facts as time-bounded edges
- Queries support provenance and historical reasoning
- Strong fit for data that changes frequently
- Built on Neo4j, supports temporal versioning

---

## Complete Reference Architecture (7 Layers)

### Layer 1: Model Layer
- Swappable frontier models (Claude, GPT, Gemini)
- Factory should be model-agnostic
- Role assignment by capability (Opus for reasoning roles, Haiku/Sonnet for utility)

### Layer 2: Inner-Loop Harness
The agent runtime—what the model actually runs inside.

**Components:**
- **Tools** — File edit, shell execution, browser automation
- **Permission boundaries** — What the agent can/cannot access
- **Sandboxing** — Containers or git worktrees for isolation
- **Deterministic verification hooks** — Typecheck, lint, tests firing *inside* the loop, not after
- **Rules set to "error," not "warn"** — Hard gates, not advisory signals

**Key property:** Tight feedback loop with ground-truth feedback.

### Layer 3: Context Layer
What gets injected into the agent's context each turn.

**Components:**
- Hierarchical rules files (AGENTS.md, CLAUDE.md, project-specific overrides)
- Skills (progressive disclosure)
- MCP servers (external system access)
- Code graph retrieval (symbols, dependencies, examples)
- Compaction strategies for multi-session context

**Principle:** Just-in-time retrieval > front-loaded context.

### Layer 4: Memory Layer
Persistent knowledge across sessions and task boundaries.

**Levels:**
- **L1 file-based memory** — In-repo decision logs, `.knowledge/` vaults, markdown artifacts
- **L2 static code graph** — LSP-based symbol index, dependency manifests
- **L3 temporal context graph** — Graphiti/Zep or Cognee for time-aware facts

**Write-back timing:** After each task completes, distill learnings into durable form.

### Layer 5: Outer Loop / Orchestration
The work-intake, dispatch, verify, merge cycle—runs without you in the seat.

**Components:**
- **Work intake** — Issue queue as agent-readable source of truth
- **Dispatch** — Launch agents in parallel into isolated worktrees/containers
- **Independent verification** — Separate judge/reviewer agents with fresh context
  - Keeps implementation, correctness, and performance reasoning independent
  - Prevents a combined agent from weakening correctness to land an optimization
- **Merge policy** — Human review checkpoints, automated gates
- **Escalation** — Path back to humans when loops stall

**Stopping conditions (layered):**
- Max iteration limits (`max_iterations=10`)
- Token and cost budgets (hard spending limits)
- No-progress detection (exit when iterations produce no new information)
- Goal-achievement checks (evaluate whether task objective is met)
- Dual-loop pattern: outer loop can reset entire strategy when inner loop stalls

### Layer 6: Governance Layer
Non-optional in production.

**Components:**
- **Spec-driven development** — Constitution + specification as contracts
- **Policy-as-code gates** — OPA, branch protection rules
- **Security scanning** — SAST, dependency audits, SCA
- **Human review checkpoints** — Mandatory code review before merge
- **Compliance artifacts** — Audit trails, decision logs

**Why it matters:** DORA research found higher AI adoption correlates with increases in both delivery throughput and delivery *instability*. One analysis: AI-generated code introduced 10,000+ new security findings per month by mid-2025 (10x increase from Dec 2024).

### Layer 7: Observability + Improvement Flywheel
The loop that makes the factory improve itself.

**Components:**
- **Telemetry** — OTel on every agent run (prompt, tools called, decisions, outcome)
- **Metrics** — Cost per merged PR, time-to-merge for agent PRs, review velocity per size
- **Evals as regression tests** — Test your harness itself (rules, skills, gates)
- **Failure-to-fix feedback** — Failures feed back into layers 2–4

---

## Mapping to Production Platforms

### Claude Code

**Strengths for factory-building:**
- **CLAUDE.md hierarchy** — Composable rules at org/project/module level
- **Skills system** — Progressive disclosure, measured lifecycle
- **Subagents and Agent Teams** — Parallel inner loops with coordination via Tasks tool
- **Hooks** — PostToolUse, PostResponse for deterministic gates
- **MCP integration** — First-class protocol support for external tools
- **Headless SDK mode** — Can be the execution engine inside your own outer loop

**Best for:** Teams building custom outer-loop orchestration or integrating agents into existing infrastructure.

### GitHub Copilot

**Strengths for factory-building:**
- **AGENTS.md natively supported** — Consistent with open standard
- **Skills standard** — Same portable format as Claude Code
- **GitHub Actions sandbox** — Native CI/CD integration
- **PR-as-artifact** — Each agent run surfaces as a reviewable PR
- **Issue-to-PR workflow** — Built-in work intake and dispatch

**Best for:** Teams already native to GitHub ecosystem, wanting outer loop managed by platform.

### Google Antigravity

**Strengths for factory-building:**
- **Agent Manager surface** — Mission control for spawning and supervising parallel agents
- **Artifacts system** — Task lists, implementation plans, diffs, screenshots, browser recordings solve trust gap
  - Google Docs-style feedback mid-run without resetting context
- **Knowledge base** — Built-in learning layer; agents save context to accelerate future tasks
- **Multi-repo workspaces (2.0)** — Agents work across repo boundaries
- **CLI + SDK** — Headless invocation for orchestration (Antigravity 2.0)
- **Scheduled tasks** — Agents run on schedule without user prompt

**Best for:** Teams wanting productized outer loop UI with high transparency and asynchronous task execution.

---

## Open-Source Ecosystem

### Orchestration / Outer Loops

**Tier 1 (production-grade):**
- **OpenHands** — Autonomous agents that plan, write, apply changes end-to-end; designed for enterprise scale. Agent Canvas acts as self-hosted control center driving OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local/remote/cloud backends.
- **Gastown (Steve Yegge)** — Multi-agent orchestration with persistent work tracking via "beads" (lightweight issue tracker acting as external memory). Mayor agent oversees coders, reviewers, supervisors.

**Tier 2 (specialized):**
- **ralph-orchestrator** — Maintains agents in a loop until task completes
- **zeroshot** — Planner + implementer + independent validators in isolated worktrees/Docker, loops until verified
- **Claude Squad** — Terminal-native, minimal
- **Vibe Kanban, Conductor family** — Worktree managers with visualization

**Framework-integrated:**
- **LangGraph** — Leading framework when building custom loops in code; used by most production orchestrators underneath

### Memory Frameworks

**Tier 1 (most complete):**
- **Cognee** — Graph-native memory with ECL (Extract, Cognify, Load) pipeline; 14 retrieval modes; pluggable storage backends; MCP-native; Apache 2.0
- **Mem0** — Strong for lightweight conversational personalization; optional graph layer (still in hosted version)
- **Zep** — Temporal knowledge graphs built on Graphiti; 94.7% LoCoMo, 90.2% LongMemEval accuracy
- **Letta** — Best framework for stateful memory-first agents; OS-inspired memory hierarchy

**Tier 2 (specialized):**
- **Graphiti** — Best temporal graph memory with provenance; 27k stars; Apache 2.0
- **LangMem** — Default for LangGraph-based agents; in-framework memory tools
- **MemGPT (now Letta)** — Pioneering work on context management for long-horizon agents

### Spec-Driven Development

- **GitHub Spec Kit** — Structured specifications as contracts
- **Kiro** — Spec-driven development with agent hooks

---

## Things People Usually Miss

### 1. Evals for the Harness Itself
Treat your CLAUDE.md, skills, and rules as software with regression tests. Without evals on the harness, changes are vibes. Every harness change should have a corresponding benchmark on representative tasks.

### 2. Sandboxing and Blast Radius
Worktree/container isolation per agent is what makes parallelism safe. When changes land at machine speed (seconds), blast radius compounds. Feature flags become a first-class tool, not an afterthought.

### 3. Economics
Token cost scales roughly:
- Single chat: 1x baseline
- Single agent: 4x
- Multi-agent system: 15x

Cost-per-merged-PR must be a first-class metric in your observability layer. Token waste compounds faster than code quality improves.

### 4. Verification Asymmetry (The Real Bottleneck)
The factory's bottleneck isn't generation—it's **review**. You can make agents 10x faster; reviewers aren't 10x faster. This is why:
- Independent judge agents (verification with fresh context)
- Artifacts as lightweight review surface (task list, plan, diff summary, screenshot)
- Deterministic gates (lint, type-check, tests) that block bad code before humans see it
- Comments-on-artifacts feedback loop

The leverage is verification-side, not generation-side.

### 5. Memory vs. Retrieval
The distinction between what you *remember* and what you *retrieve on demand* matters. L1 file-based memory + LSP-based code graph often outperforms heavy graph infrastructure for coding tasks, because agents are good at search. Start simple; only add graph infrastructure when semantic retrieval clearly outperforms keyword search on your workloads.

---

## Clarification: .claude/ Folder as Inner-Loop Harness Engineering

### The Distinction

Your `.claude/` folder customizations—agents, skills, hooks—are **inner-loop harness engineering**, not the loop itself.

**Mapping your customizations:**

| Component | Role | Layer |
|-----------|------|-------|
| **Hooks** (PostToolUse, PostResponse) | Deterministic verification inside each turn | Inner-Loop Harness |
| **Skills** | Just-in-time procedural knowledge injected into context | Context Layer |
| **Subagents** | Nested inner loops; parallel or specialized execution | Inner-Loop Harness (parallelized) |
| **CLAUDE.md rules** | Persistent instructions; scope and gate behavior | Context Layer + Harness |

### What `.claude/` Does Not Provide

Nothing in your `.claude/` folder decides:
- What work to do next
- How to dispatch tasks across sessions
- Whether results meet requirements
- How learnings persist between runs

Those are **outer-loop responsibilities**.

### The Complete Picture

```
┌─────────────────────────────────────────────────┐
│  OUTER LOOP (you build this)                    │
│  Issue queue → dispatch → verify → merge        │
│  Runs on schedule, no human per-cycle           │
└──────────────┬──────────────────────────────────┘
               │ invokes (one or many times)
┌──────────────▼──────────────────────────────────┐
│  INNER LOOP (Claude Code runs this)             │
│  Reason → act → observe → reason again          │
│  Timescale: seconds to minutes                  │
│                                                 │
│  Shaped by .claude/ folder:                     │
│  - Hooks (verification gates)                   │
│  - Skills (context injection)                   │
│  - Rules (behavior constraints)                 │
│  - Subagents (parallelization)                  │
└─────────────────────────────────────────────────┘
```

### Sequencing for Implementation

1. **Inner-loop discipline first** (weeks 1–2)
   - Build robust CLAUDE.md, skills, hooks
   - Evals on representative tasks
   - Deterministic gates (lint, type-check, tests)

2. **Memory layer** (weeks 3–4)
   - L1 file-based decisions in `.knowledge/`
   - Static code graph via LSP
   - Retrieval over prior solutions

3. **Outer loop automation** (weeks 5–6)
   - Headless invocation from issue queue
   - Parallel agents in worktrees
   - Independent verification agents

4. **Self-improving flywheel** (weeks 7+)
   - Evals as regression tests
   - Failure-to-fix feedback loop
   - Optional: graph memory when semantic search outperforms keyword search

---

## Key References & Links

### Foundation Papers & Articles
- Harness Engineering (Martin Fowler + Thoughtworks): https://martinfowler.com/articles/harness-engineering.html
- Harness Engineering Maturity Model (Faros AI Engineering Report 2026): https://www.faros.ai/blog/harness-engineering
- Loop Engineering (Addy Osmani / LangChain): https://www.langchain.com/blog/the-art-of-loop-engineering
- Three Developer Loops Framework (IT Revolution): https://itrevolution.com/articles/the-three-developer-loops-a-new-framework-for-ai-assisted-coding/

### Platform Documentation
- Claude Code: https://code.claude.com/docs
- Google Antigravity: https://codelabs.developers.google.com/getting-started-google-antigravity
- GitHub Copilot agents: https://github.com/features/copilot

### Open-Source Repos
- OpenHands: https://github.com/OpenHands/OpenHands
- Gastown: https://github.com/steveyegge/gastown
- Graphiti: https://github.com/getzep/graphiti
- Cognee: https://github.com/topoteretes/cognee

### Awesome Lists
- CLI Coding Agents: https://github.com/bradAGI/awesome-cli-coding-agents
- Agent Orchestrators: https://github.com/andyrewlee/awesome-agent-orchestrators
- AI-Driven Development: https://github.com/eltociear/awesome-AI-driven-development

---

## Next Steps

1. **Audit your current .claude/ folder** — Are your hooks truly deterministic? Are skills progressive-disclosure or front-loaded?
2. **Establish harness evals** — Pick 3 representative tasks; measure cost, time-to-merge, and quality before/after harness changes
3. **Map your memory strategy** — L1 file-based decision logs? L2 code graph? When do you actually need L3 temporal graph?
4. **Prototype the outer loop** — Even a simple shell script that iterates issue queue → Claude invocation → verification → merge is the starting point
5. **Measure observability** — Cost per PR, time-to-merge, review velocity; you can't improve what you don't measure

---

*Document compiled from 2026 research on harness engineering, loop engineering, and production AI agent systems. Last updated July 2026.*

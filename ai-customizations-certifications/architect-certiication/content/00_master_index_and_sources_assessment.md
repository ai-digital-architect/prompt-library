# Claude Certified Architect — Foundations
## Master Study Index & Sources Assessment

---

## Exam at a Glance

| Domain | Weight | Guide File |
|---|---|---|
| Domain 1: Agentic Architecture & Orchestration | **27%** | `domain1_agentic_architecture.md` |
| Domain 2: Tool Design & MCP Integration | **18%** | `domain2_tool_design_mcp.md` |
| Domain 3: Claude Code Configuration & Workflows | **20%** | `domain3_claude_code_config.md` |
| Domain 4: Prompt Engineering & Structured Output | **20%** | `domain4_prompt_engineering.md` |
| Domain 5: Context Management & Reliability | **15%** | `domain5_context_reliability.md` |

**Format:** Multiple choice, 4 options, single correct answer. Passing score: 720/1000 (scaled). No penalty for guessing.

**Scenarios tested:** 4 of these 6 are selected randomly per sitting:
1. Customer Support Resolution Agent
2. Code Generation with Claude Code
3. Multi-Agent Research System
4. Developer Productivity with Claude
5. Claude Code for Continuous Integration
6. Structured Data Extraction

---

## Sources Assessment

The exam guide lists 18 sources. Here is a coverage analysis and honest gap assessment.

### ✅ Strong Coverage (Read These First)

| Source | Domain(s) | Priority |
|---|---|---|
| [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) | 1, 5 | 🔴 Critical |
| [Effective Context Engineering for AI Agents](https://www.anthropic.com/research/context-engineering) | 1, 5 | 🔴 Critical |
| [Prompt Engineering Overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | 4 | 🔴 Critical |
| [Interactive Prompt Engineering Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | 4 | 🔴 Critical |
| [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview) | 3 | 🔴 Critical |
| [Claude Code Settings](https://docs.anthropic.com/en/docs/claude-code/settings) | 3 | 🔴 Critical |
| [CLI Reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference) | 3 | 🟠 High |
| [MCP Specification](https://modelcontextprotocol.io/specification) | 2 | 🟠 High |
| [What is MCP?](https://modelcontextprotocol.io) | 2 | 🟠 High |
| [How We Built Our Multi-Agent Research System](https://www.anthropic.com/research/multi-agent-research) | 1, 5 | 🟠 High |
| [Introducing Advanced Tool Use](https://www.anthropic.com/research/advanced-tool-use) | 2, 4 | 🟠 High |
| [Intro to Claude — API Docs](https://docs.anthropic.com/en/docs/intro-to-claude) | All | 🟡 Medium |
| [API Overview](https://docs.anthropic.com/en/api/overview) | 4 | 🟡 Medium |
| [Advanced Setup — Claude Code](https://docs.anthropic.com/en/docs/claude-code/advanced-setup) | 3 | 🟡 Medium |
| [Create Custom Subagents](https://docs.anthropic.com/en/docs/claude-code/subagents) | 1, 3 | 🟡 Medium |
| [Enterprise Deployment](https://docs.anthropic.com/en/docs/claude-code/enterprise-deployment) | 3 | 🟡 Medium |
| [Code Execution with MCP](https://www.anthropic.com/research/code-execution-mcp) | 2 | 🟡 Medium |
| [MCP Extensions Overview](https://modelcontextprotocol.io/extensions) | 2 | 🟢 Supplemental |
| [MCP Registry](https://modelcontextprotocol.io/registry) | 2 | 🟢 Supplemental |

### ⚠️ Source Gaps — What's Missing From the List

The source list has gaps in these areas that are explicitly tested on the exam:

| Gap Area | What to Study | Domain |
|---|---|---|
| **Agent SDK hooks** (`PostToolUse`, tool call interception) | [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) | 1 |
| **Message Batches API** (cost savings, latency, `custom_id`) | [Batch Processing docs](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) | 4 |
| **Session management** (`fork_session`, `--resume`) | CLI Reference + Agent SDK docs | 1, 3 |
| **tool_choice API options** (`"any"`, forced selection) | [Tool Use docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) | 2, 4 |
| **Structured output via tool_use** (schema design) | [Tool Use for Structured Output](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) | 4 |
| **Confidence calibration** (validation sets, stratified sampling) | Exam guide task statements 5.5 | 5 |

**Verdict:** The source list is a good starting point but not complete. The exam guide task statements themselves are the most authoritative preparation material — read them carefully and ensure you understand every bullet point.

---

## Cross-Domain Concept Map

Several concepts appear across multiple domains. Mastering these gives outsized return:

### Programmatic Enforcement vs. Prompt Instructions
Appears in: Domain 1 (agentic loop ordering), Domain 3 (CLAUDE.md vs. hooks), Domain 5 (escalation criteria)

> **Core principle:** Use code-level enforcement when business rules require 100% compliance. Prompt instructions are probabilistic (~70–95%). For financial operations, identity verification, and safety-critical ordering — always use programmatic gates.

### Explicit Context Passing
Appears in: Domain 1 (subagent context), Domain 5 (conversation history, case facts)

> **Core principle:** Claude has no memory between API calls. Nothing is inherited automatically. Every piece of information a subagent or the model needs must be explicitly included in its prompt or the messages array.

### Structured Error Responses
Appears in: Domain 2 (MCP tool errors), Domain 5 (multi-agent error propagation)

> **Core principle:** Generic error messages ("operation failed") hide the information needed for intelligent recovery. Always include: error category, isRetryable, attempted action, partial results, alternative approaches.

### Few-Shot Examples
Appears in: Domain 4 (prompting), Domain 5 (escalation criteria in system prompt)

> **Core principle:** Few-shot examples outperform detailed instructions for: consistent output format, ambiguous case handling, and reducing false positives. Include 2–5 targeted examples. Always include at least one "null/empty" example to prevent fabrication.

### tool_choice Configuration
Appears in: Domain 2 (tool distribution), Domain 4 (structured output enforcement)

> **Core principle:** `"auto"` may return plain text. Use `"any"` to guarantee a tool is called. Use forced selection `{"type": "tool", "name": "X"}` to ensure a specific prerequisite runs first.

---

## Study Plan by Priority

### Week 1: Highest-Weight Domains
- [ ] Read Domain 1 guide (Agentic Architecture — 27%)
- [ ] Read Domain 3 guide (Claude Code — 20%)
- [ ] Read Domain 4 guide (Prompt Engineering — 20%)
- [ ] Work through the interactive prompt engineering tutorial

### Week 2: Remaining Domains + Hands-On
- [ ] Read Domain 2 guide (Tool Design & MCP — 18%)
- [ ] Read Domain 5 guide (Context Management — 15%)
- [ ] Build Exercise 1: Multi-Tool Agent with Escalation Logic
- [ ] Build Exercise 2: Configure Claude Code for a Team Workflow

### Week 3: Deep Practice
- [ ] Build Exercise 3: Structured Data Extraction Pipeline
- [ ] Build Exercise 4: Multi-Agent Research Pipeline
- [ ] Re-read all 12 sample questions in the exam guide with explanations
- [ ] Complete the official practice exam

### Ongoing
- [ ] For every sample question: read the *explanation* carefully — it reveals why wrong answers are wrong
- [ ] Pay special attention to distractor patterns: "add prompt instructions" vs. "add programmatic enforcement"
- [ ] Review the Appendix Technologies and Concepts list (pages 36–37) — every item listed is fair game

---

## Top 10 High-Probability Exam Topics

Based on exam guide emphasis, scenario coverage, and question patterns:

1. **`stop_reason` values** — `"tool_use"` vs `"end_turn"` and correct loop control flow
2. **Programmatic enforcement vs. prompt instructions** — when each is appropriate
3. **Subagent context isolation** — must pass context explicitly; nothing inherited
4. **Tool description quality** — primary mechanism for tool selection
5. **CLAUDE.md hierarchy** — user vs. project vs. directory; what's shared vs. personal
6. **`-p` flag for CI/CD** — non-interactive mode; structured JSON output
7. **tool_choice options** — `"auto"` vs. `"any"` vs. forced selection
8. **Batch API appropriateness** — blocking vs. non-blocking workflows; latency requirements
9. **Escalation decision-making** — explicit criteria; honoring direct requests; policy gaps
10. **Attention dilution** — per-file passes + integration pass for large reviews

---

## Out-of-Scope Topics (Do Not Study)

The following will NOT appear on this exam:

- Fine-tuning or training custom Claude models
- API authentication, billing, or account management
- Deploying or hosting MCP servers (infrastructure, networking, containers)
- Claude's internal architecture, training process, or model weights
- Constitutional AI, RLHF, or safety training methodologies
- Embedding models or vector database implementation
- Computer use (browser automation, desktop interaction)
- Vision/image analysis capabilities
- Streaming API implementation
- Rate limiting, quotas, or API pricing calculations
- OAuth, API key rotation, or authentication protocol details
- Specific cloud provider configurations (AWS, GCP, Azure)
- Token counting algorithms or tokenization specifics

---

*Study guides created from: Claude Certified Architect – Foundations Certification Exam Guide v0.1 (Feb 10, 2025) + research across all 18+ listed sources.*

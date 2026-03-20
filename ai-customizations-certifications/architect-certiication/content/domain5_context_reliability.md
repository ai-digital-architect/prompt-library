# Domain 5: Context Management & Reliability
**Weight: 15% of scored content**

---

## Overview

This domain tests your ability to keep agents reliable across long interactions, manage growing context windows, design intelligent escalation logic, propagate errors usefully through multi-agent systems, and build human review workflows. Many of the pitfalls tested here are subtle — they only appear in production at scale, not in simple demos.

**Source coverage:** The exam guide source list is well-matched via *Effective Context Engineering for AI Agents*, the Claude Agent SDK docs, and the structured output sources. The *Building Effective AI Agents* article covers escalation patterns.

---

## 5.1 Managing Context Across Long Interactions

### Why Context Management Is Critical

Every token in the context window consumes capacity. As conversations grow, problems compound:
- Verbose tool results accumulate and crowd out relevant information
- The "lost in the middle" effect causes facts in middle sections to be missed
- Progressive summarization loses specific values (amounts, dates, order numbers)
- Stale tool results persist even after the underlying data changed

### The "Lost in the Middle" Effect

Claude (like all transformer models) processes information at the **beginning and end** of long inputs most reliably. Information in the **middle of a very long context** is at risk of being overlooked.

**Mitigation strategies:**
- Place **key findings summaries at the beginning** of aggregated inputs
- Organize detailed results with **explicit section headers** so the model can navigate
- For multi-agent synthesis: require each upstream agent to place its most important finding **first** in its output

### Preserving Critical Transactional Facts

Progressive summarization can accidentally condense specific values (order numbers, dollar amounts, dates) into vague descriptions. Instead, maintain a persistent "case facts" block:

```python
def build_prompt_with_case_facts(case_facts: dict, conversation_summary: str) -> str:
    return f"""
    ## CASE FACTS (DO NOT SUMMARIZE — REFERENCE DIRECTLY)
    Customer ID: {case_facts['customer_id']} (verified)
    Order ID: {case_facts['order_id']}
    Disputed Amount: ${case_facts['disputed_amount']:.2f}
    Order Date: {case_facts['order_date']}
    Return Deadline: {case_facts['return_deadline']}
    Customer Tier: {case_facts['tier']}

    ## CONVERSATION SUMMARY
    {conversation_summary}

    ## CURRENT REQUEST
    {current_message}
    """
```

This block is updated as new facts are confirmed, included in every prompt, and never summarized away.

### Trimming Verbose Tool Outputs

Many MCP tools return far more fields than are relevant to the current task:

```python
@agent.post_tool_use
def trim_order_result(tool_name: str, result: dict) -> dict:
    if tool_name == "lookup_order":
        # Original result has 40+ fields
        # Keep only the 5-7 fields relevant to return/refund processing
        return {
            "order_id": result["order_id"],
            "status": result["status"],
            "total_amount": result["total_amount"],
            "items": result["items"],
            "shipping_address": result["shipping_address"],
            "return_eligible": result["return_eligible"],
            "return_deadline": result["return_deadline"]
            # Discard: internal tracking codes, warehouse IDs,
            # payment processor tokens, A/B test flags, etc.
        }
    return result
```

### Structured Context Layers for Multi-Issue Sessions

For sessions handling multiple concurrent issues (e.g., three orders being disputed), maintain a structured context layer:

```python
issue_tracker = {
    "issues": [
        {
            "issue_id": "ISS-001",
            "order_id": "ORD-12345",
            "amount": 147.50,
            "status": "refund_approved",
            "action_taken": "Refund processed to original card"
        },
        {
            "issue_id": "ISS-002",
            "order_id": "ORD-12346",
            "amount": 89.99,
            "status": "investigating",
            "next_action": "Awaiting warehouse damage confirmation"
        }
    ]
}
```

This prevents issue details from being confused or dropped during long sessions.

---

## 5.2 Escalation and Ambiguity Resolution

### When to Escalate vs. Resolve Autonomously

The exam tests whether you can distinguish the correct escalation criteria:

| Situation | Correct Response |
|---|---|
| Customer **explicitly requests a human** | Escalate immediately — no investigation first |
| Customer is frustrated but issue is within agent capability | Acknowledge frustration; offer to resolve; escalate only if they reiterate |
| Case is straightforward (standard damage replacement with photo evidence) | Resolve autonomously |
| Case requires a **policy exception** or policy is silent | Escalate — this is a gap, not complexity |
| Agent **cannot make meaningful progress** | Escalate |
| Multiple matches returned by customer lookup tool | Request additional identifiers (do not guess) |

### The Direct Escalation Request Rule

When a customer explicitly asks for a human agent, **escalate immediately without attempting investigation first.** Do not offer to resolve it yourself first — honor the explicit request.

```
# ❌ WRONG: Attempting investigation despite explicit human request
Customer: "I want to speak to a human agent."
Agent: "I understand. Let me first look into your account to help speed things along..."

# ✅ CORRECT: Immediate escalation
Customer: "I want to speak to a human agent."
Agent: "Of course. I'm connecting you to a human agent now.
       To help them get started, I'll share: [brief summary]."
```

### Policy Gap Escalation

Agents should escalate when policy is **ambiguous or silent** on the customer's specific request — not just when cases are complex:

```
# Example: Policy covers own-site price matching but is silent on competitor matching
Customer: "I found this for $20 cheaper at CompetitorStore."
Correct action: Escalate — this is a policy gap, not just a "complex" case.
               The agent should not make an autonomous policy exception.
```

### Why Sentiment-Based Escalation Fails

Sentiment analysis does not correlate with case complexity. A frustrated customer may have a simple issue; a calm customer may have an extremely complex situation. Use explicit criteria, not sentiment scores.

### Why Self-Reported Confidence Fails

Agent self-reported confidence scores are unreliable:
- The agent may be **confidently wrong** on difficult cases
- The cases where escalation is most needed are often the cases where the agent feels most confident (it doesn't know what it doesn't know)

### Adding Explicit Escalation Criteria to the System Prompt

```python
system_prompt = """
You are a customer support agent.

## Escalation Criteria — Escalate when ANY of these conditions are met:

1. EXPLICIT REQUEST: Customer explicitly asks to speak with a human
2. POLICY GAP: The customer's request is not clearly covered by policy
3. NO PROGRESS: You cannot make meaningful progress after two attempts
4. HIGH STAKES: Potential refund > $500 or account security concern

## Examples

<examples>
<example>
Situation: Customer says "I just want to talk to a human please."
Action: ESCALATE IMMEDIATELY — do not attempt to resolve first.
</example>

<example>
Situation: Standard return request with photo evidence of damage.
Order is within return window. Policy covers this case clearly.
Action: RESOLVE AUTONOMOUSLY — process the return.
</example>

<example>
Situation: Customer wants to match a competitor's price.
Our policy only addresses own-site price adjustments.
Action: ESCALATE — policy is silent on competitor matching.
</example>
</examples>
"""
```

---

## 5.3 Error Propagation Across Multi-Agent Systems

### The Core Principle: Structured Context Enables Intelligent Recovery

When a subagent fails, the coordinator needs structured information to decide how to recover. Generic status messages ("search unavailable") hide the information needed for intelligent decision-making.

### What Structured Error Context Should Include

```python
# ❌ INSUFFICIENT: Generic status hides valuable context
return {
    "status": "search_unavailable",
    "results": []
}

# ✅ COMPLETE: Structured context enables coordinator recovery
return {
    "isError": True,
    "errorCategory": "transient",
    "failure_type": "api_timeout",
    "attempted_query": "AI impact on music production industry 2023-2024",
    "partial_results": [
        # Include any results returned before timeout
        {"title": "AI in Music Production", "url": "...", "snippet": "..."}
    ],
    "alternative_approaches": [
        "Narrow query to 'AI music production tools 2024'",
        "Try document_search instead of web_search",
        "Use academic_search for peer-reviewed sources"
    ],
    "retry_recommended": True,
    "retry_after_seconds": 30
}
```

### Four Error Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails |
|---|---|
| Generic error status ("operation failed") | Coordinator cannot make informed recovery decisions |
| Silently return empty results as success | Coordinator proceeds as if search was complete; silent data gaps |
| Terminate entire workflow on single subagent failure | Wasteful; coordinator could often proceed with partial results |
| Retry indefinitely within subagent without escalating | Masks persistent failures; delays coordinator's awareness |

### Coverage Annotations in Synthesis Output

When some sources failed, the synthesis output should annotate coverage gaps:

```python
synthesis_output = {
    "report": "...",
    "coverage_summary": {
        "well_covered_topics": [
            "AI impact on visual arts (3 sources, high confidence)",
            "AI in music production (2 sources, medium confidence)"
        ],
        "coverage_gaps": [
            {
                "topic": "AI impact on film industry",
                "reason": "Web search agent timed out; academic search returned 0 results",
                "confidence": "low"
            }
        ]
    }
}
```

---

## 5.4 Context Management in Large Codebase Exploration

### Signs of Context Degradation

In extended Claude Code sessions, watch for these symptoms of context degradation:
- Giving inconsistent answers to the same question asked earlier
- Referencing "typical patterns" instead of specific classes discovered earlier
- Missing details from early in the session when those files are referenced again

### Scratchpad Files for Persistence

Maintain scratchpad files to persist key findings across context boundaries:

```
# exploration_notes.md (maintained by the agent throughout the session)

## Architecture Summary
- Core domain layer: src/domain/ (clean, no framework deps)
- HTTP layer: src/http/ (FastAPI)
- DB layer: src/db/ (SQLAlchemy + Alembic)

## Key Discoveries
- RefundProcessor calls PaymentGateway.refund() → timeout handling is MISSING
- OrderService.getOrders() has N+1 query problem (line 147)
- AuthMiddleware only validates JWT signature, not expiration (!!!)

## Still To Investigate
- [ ] How does cache invalidation work for user profiles?
- [ ] What calls UserService.deleteUser()?
```

When context fills or degrades, the agent references this file rather than re-exploring from scratch.

### Subagent Delegation for Verbose Discovery

```python
# Main agent: coordinate and preserve high-level understanding
# Subagent: perform verbose exploration and return a summary

subagent_result = spawn_subagent(
    "explore_agent",
    prompt="""
    Find all files that call UserService.deleteUser().
    Return ONLY a structured summary:
    - List of calling files with line numbers
    - What data is deleted in each call path
    - Whether any calls are missing transaction wrappers
    Do NOT include raw file contents in your response.
    """
)

# Main agent gets a compact summary instead of hundreds of lines of file content
```

### Session Continuity: Fresh Start vs. Resume

```
Resume with same session:
  ✅ Use when: Prior analysis is still valid; no major code changes
  ✅ Use when: You need to continue exactly where you left off
  ❌ Avoid when: Significant files have changed (stale tool results)

Fresh session with injected summary:
  ✅ Use when: Prior tool results are stale
  ✅ Use when: Context degradation symptoms are appearing
  ✅ Use when: You changed significant files since the last session

  Process:
  1. Summarize key findings from previous session
  2. Start new session
  3. Inject summary in system prompt or first message
  4. Continue from the summary
```

### Crash Recovery Using Manifests

For long-running multi-agent workflows:

```python
# Each agent exports state to a known location at checkpoints
def checkpoint_agent_state(agent_id: str, state: dict):
    manifest_path = f".agent_state/{agent_id}_manifest.json"
    state["checkpoint_time"] = datetime.utcnow().isoformat()
    state["agent_id"] = agent_id
    with open(manifest_path, "w") as f:
        json.dump(state, f, indent=2)

# On resume, coordinator loads all manifests and injects into agent prompts
def resume_from_crash():
    for manifest_file in Path(".agent_state/").glob("*_manifest.json"):
        manifest = json.load(open(manifest_file))
        # Inject into the agent's initial context
        spawn_agent_with_context(
            agent_id=manifest["agent_id"],
            context=f"Resume from checkpoint:\n{json.dumps(manifest, indent=2)}"
        )
```

### `/compact` in Claude Code

Use `/compact` to reduce context usage during extended exploration sessions when the context window fills with verbose discovery output. This compresses the conversation history while preserving the essential facts.

---

## 5.5 Human Review Workflows and Confidence Calibration

### The Hidden Risk in Aggregate Metrics

A 97% overall extraction accuracy may mask serious problems in specific segments. For example:
- 99.5% accuracy on standard invoices
- 61% accuracy on handwritten invoices
- 88% accuracy on multi-currency invoices

Always validate accuracy **by document type and field** before automating high-confidence extractions.

### Stratified Random Sampling

Sample from **all confidence segments** — not just low-confidence extractions. High-confidence extractions can still have systematic errors that aggregate metrics hide.

```python
def build_review_sample(extractions: list, sample_size: int = 200) -> list:
    # Stratified by confidence tier
    high_confidence = [e for e in extractions if e["confidence"] >= 0.90]
    medium_confidence = [e for e in extractions if 0.70 <= e["confidence"] < 0.90]
    low_confidence = [e for e in extractions if e["confidence"] < 0.70]

    sample = (
        random.sample(high_confidence, min(50, len(high_confidence))) +   # 25%
        random.sample(medium_confidence, min(50, len(medium_confidence))) + # 25%
        low_confidence[:100]  # All low-confidence extractions
    )
    return sample
```

### Field-Level Confidence Scores

Instead of a single document-level confidence score, request field-level scores:

```python
confidence_schema = {
    "extraction": {
        "invoice_number": "INV-2024-0042",
        "total_amount": 1250.00,
        "due_date": "2024-04-15"
    },
    "confidence_scores": {
        "invoice_number": 0.99,  # Clear, unambiguous
        "total_amount": 0.95,    # Clear number, consistent with line items
        "due_date": 0.62         # Two dates in document; unclear which is due date
    },
    "review_flags": ["due_date_ambiguous"]
}
```

### Calibrating Review Thresholds

Calibrate confidence thresholds against a **labeled validation set** — not by intuition:

```
1. Extract from 500 labeled documents (you know the ground truth)
2. Compare model's confidence scores against actual accuracy at each score level
3. Find the confidence threshold where accuracy meets your requirement
   (e.g., "above 0.88 confidence, accuracy is 99.2% — acceptable for auto-approval")
4. Set routing rules based on calibrated thresholds
```

Do not use uncalibrated thresholds. A model that reports "0.90 confidence" on a field may only be correct 75% of the time on that field type.

### Review Routing Strategy

```
Confidence >= calibrated_threshold AND document_type IN validated_types
  → Auto-approve (no human review needed)

Confidence < calibrated_threshold OR ambiguous/contradictory source
  → Route to human review queue

Novel document type (not in validation set)
  → Route to human review queue (regardless of confidence)
```

---

## 5.6 Information Provenance and Uncertainty in Multi-Source Synthesis

### The Source Attribution Problem

During summarization, specific claims become detached from their sources. A synthesis agent receiving summaries without attribution cannot produce a properly cited report.

**Solution:** Require subagents to output structured claim-source mappings that downstream agents must preserve:

```python
finding_format = {
    "claim": "AI tools reduced music production time by 40% for indie artists",
    "evidence_excerpt": "Independent musicians reported...",
    "source_url": "https://example.com/music-ai-survey-2024",
    "source_name": "AI in Creative Industries Survey 2024",
    "publication_date": "2024-02-15",
    "confidence": "medium",
    "note": "Self-reported survey data; not independently verified"
}
```

### Handling Conflicting Statistics

When two credible sources report different statistics for the same phenomenon:

```
# ❌ WRONG: Arbitrarily select one value
"AI adoption in music production grew by 34% (Source A)"

# ✅ CORRECT: Annotate the conflict and preserve both
"AI adoption in music production grew between 28% (Industry Association Report,
Dec 2023) and 41% (Platform Data Analysis, Mar 2024). The difference may reflect
methodology (industry survey vs. platform usage metrics) or temporal variation
across the 3-month gap."
```

The coordinator (not the analysis subagent) should decide how to reconcile conflicts. Subagents should surface conflicts, not resolve them.

### Temporal Data Handling

Require subagents to include publication/collection dates. This prevents interpreting time-based differences as contradictions:

```python
# ❌ AMBIGUOUS: Appears contradictory without dates
finding_1 = {"claim": "AI adoption rate is 23%"}
finding_2 = {"claim": "AI adoption rate is 61%"}

# ✅ CLEAR: Dates reveal these are sequential snapshots, not contradictions
finding_1 = {"claim": "AI adoption rate is 23%", "publication_date": "2022-01-15"}
finding_2 = {"claim": "AI adoption rate is 61%", "publication_date": "2024-08-30"}
```

### Structuring Contested vs. Established Findings

Synthesis reports should distinguish confidence levels explicitly:

```markdown
## Well-Established Findings
(Supported by 3+ independent sources with consistent results)
- AI tools have reduced routine audio mastering costs by 60-75%
- Entry-level audio engineering job postings declined 31% since 2022

## Contested Findings
(Sources disagree or evidence is preliminary)
- Long-term impact on creative quality: mixed results across studies.
  MIT Media Lab (2024) found no quality decline; industry survey (2023)
  reports 22% of professionals believe AI reduces creative depth.

## Coverage Gaps
- Impact on live performance revenue: No reliable data found.
  Academic search returned 0 results; web search timed out.
```

---

## Exam Practice Questions

**Q1:** An agent is handling a billing dispute. The customer says "I just want to speak to a real person." What should the agent do?
> **Escalate immediately.** Do not attempt to investigate or offer to resolve first. Explicit human requests must be honored immediately without preconditions.

**Q2:** A web search subagent times out. The coordinator needs to decide whether to retry, try a different approach, or proceed with partial results. What should the subagent return?
> Return structured error context: failure type (`transient`), the attempted query, any partial results retrieved before timeout, and alternative approaches. Do NOT return empty success results — that hides the failure.

**Q3:** Your extraction pipeline shows 97% overall accuracy, so you automate all high-confidence extractions. Later you discover 61% accuracy on handwritten invoices. What should you have done?
> Validated accuracy by document type and field segment before automating. Aggregate metrics mask segment-level failures.

**Q4:** An agent in a long exploration session starts giving inconsistent answers and referencing "typical patterns" instead of specific classes found earlier. What's the appropriate intervention?
> The agent is experiencing context degradation. Have the agent write/update its scratchpad file with current key findings, and use `/compact` to reduce context. For the next phase, start a new session with the scratchpad summary injected into the initial context.

**Q5:** Two sources report different AI adoption rates (28% vs. 41%). How should the synthesis agent handle this?
> Annotate the conflict with source attribution for both, note possible reasons for the discrepancy (methodology, time period), and let the coordinator decide how to reconcile. Do not arbitrarily select one value.

---

## Key Terms Checklist

- [ ] "Lost in the middle" effect — middle context is less reliably processed
- [ ] Persistent "case facts" block — separate from summarized history
- [ ] Tool output trimming — keep only relevant fields
- [ ] Structured context layers for multi-issue sessions
- [ ] Explicit escalation criteria (not sentiment-based, not confidence-based)
- [ ] Direct escalation request rule — honor immediately, no investigation first
- [ ] Policy gap escalation — policy silent = escalate
- [ ] Self-reported confidence unreliability
- [ ] Structured error context: failure type, attempted query, partial results, alternatives
- [ ] Empty-success anti-pattern
- [ ] Coverage annotations in synthesis output
- [ ] Scratchpad files for persistence across context boundaries
- [ ] Subagent delegation for verbose discovery output
- [ ] Crash recovery via agent state manifests
- [ ] `/compact` — reduce context during extended sessions
- [ ] Stratified random sampling (all confidence tiers)
- [ ] Field-level confidence scores vs. document-level
- [ ] Calibrate thresholds against labeled validation sets
- [ ] Claim-source mapping structures — preserved through synthesis
- [ ] Conflict annotation — both values with attribution, let coordinator reconcile
- [ ] Publication/collection dates in structured outputs (temporal disambiguation)

---

## Recommended Sources

| Source | Focus |
|---|---|
| [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Compaction; structured note-taking; multi-agent context |
| [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) | Escalation patterns; human oversight checkpoints |
| [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) | Subagent delegation; context management |
| [How We Built Our Multi-Agent Research System](https://www.anthropic.com/research/multi-agent-research) | Provenance; conflict handling; coverage gaps |
| Exam Guide — Task Statements 5.1–5.6 (Pages 21–25) | Authoritative task definitions |

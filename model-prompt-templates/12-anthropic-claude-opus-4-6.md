---
post_title: "General-Purpose Prompt Template — Anthropic Claude Opus 4.6"
author1: "Prompt Library Team"
post_slug: "12-anthropic-claude-opus-4-6"
microsoft_alias: "promptlibrary"
featured_image: "https://learn.microsoft.com/en-us/azure/ai-services/openai/media/overview/openai-overview.png"
categories:
  - "AI"
  - "Developer Tools"
tags:
  - "prompt-engineering"
  - "llm"
  - "model-templates"
  - "ai-assisted-engineering"
  - "anthropic"
  - "claude-opus"
  - "legacy"
ai_note: "Content created with AI assistance."
summary: >
  Prompt template for Claude Opus 4.6: extended-thinking scaffold and agentic
  depth guidance. Legacy tier — prefer Claude Opus 5 for new work.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

> **Status (June 2026):** Opus 4.6 remains active but has been superseded by
> **Claude Opus 4.8** ([template 14](./14-anthropic-claude-opus-4-8.md)) as the
> current Opus-tier model, with **Claude Fable 5**
> ([template 13](./13-anthropic-claude-fable-5.md)) above it. Prefer Opus 4.8 for
> new work.

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Opus 4.6 |
| **Provider** | Anthropic |
| **Tier** | Flagship — maximum intelligence, extended reasoning, and agentic depth |
| **Context Window** | 1M tokens |
| **Max Output** | 128K tokens (streaming required for large outputs) |
| **Strengths** | Extended thinking, deep multi-step reasoning, agentic workflows, complex bug detection, long-document synthesis, nuanced judgment |
| **New in 4.6** | Enhanced extended thinking with deeper reasoning chains, improved tool-use reliability, stronger performance on STEM and legal reasoning benchmarks, refined computer-use capabilities |
| **Best For** | Tasks requiring the highest correctness bar — production code auditing, advanced research synthesis, strategic documents, agent orchestration, and long-horizon problem solving |

---

## What Sets Opus 4.6 Apart

Opus 4.6 builds on 4.5 with three key advances:

1. **Deeper extended thinking** — The internal reasoning chain is longer and more
   self-correcting. Enable via API `thinking` block or conversationally with
   "reason step by step before answering."
2. **Richer tool-call chains** — Better at orchestrating multi-tool pipelines in a
   single turn without losing context between calls.
3. **Calibrated confidence** — Opus 4.6 is more willing to say "I am uncertain" or
   "this depends on X" rather than over-committing to an answer.

---

## Template Structure

```xml
<system>
You are {{ROLE}}, an expert in {{DOMAIN}}.

<context>
{{Background information, constraints, organizational context, or situational
framing. Be generous with detail — Opus 4.6 maintains coherence across the full
1M-token window.}}
</context>

<objectives>
{{Numbered list of what the response must accomplish, from most to least critical.}}
</objectives>

<thinking_instructions>
Before writing your final response, reason through the problem internally:
- Identify assumptions that could invalidate the answer.
- Consider at least two alternative approaches.
- Surface any edge cases or failure modes.
- Acknowledge uncertainty rather than masking it.
</thinking_instructions>

<guidelines>
- {{Quality standard or evaluation rubric}}
- {{Formatting or structural requirement}}
- {{Tone and audience specification}}
- Calibrate depth to importance: spend more tokens on high-risk sections.
</guidelines>

<output_format>
{{Describe the exact structure, sections headings, and approximate length expected.}}
</output_format>
</system>

<user>
{{The specific task, question, or instruction}}

<reference_material>
{{Any supporting documents, data, code snippets, or prior work. Use labeled
sub-tags — <doc1>, <doc2>, <code> — to keep reference items distinct.}}
</reference_material>
</user>
```

### Key Prompting Principles for Opus 4.6

1. **Use adaptive thinking** — In the API set `"thinking": {"type": "adaptive"}` and the model decides
   when and how deeply to think (fixed `budget_tokens` is deprecated on 4.6).
   Conversationally use: *"Reason carefully before answering"* or *"Think step by step."*
2. **Provide motivational framing** — Opus 4.6 calibrates rigor to stakes.
   Example: *"This will be reviewed by the lead security engineer before production deploy."*
3. **Label reference material with sub-tags** — When providing multiple documents,
   wrap each in a named tag (`<spec>`, `<code>`, `<logs>`) so the model can cite them precisely.
4. **Request explicit uncertainty disclosure** — Add *"Flag any areas where your
   confidence is lower"* to get calibrated, trustworthy output.
5. **Use the `effort` parameter for cost control** — Pass
   `"output_config": {"effort": "high"}` for thoroughness (also `"max"` on Opus 4.6),
   or `"medium"` for balanced output. Effort lives inside `output_config`, not top-level.
6. **Chain objectives, not prompts** — Opus 4.6's tool-use and reasoning hold context
   well across long turns. Prefer one rich prompt over multiple short follow-ups.

---

## Example 1 — Agentic Code Review with Tool Use

```xml
<system>
You are a principal engineer performing a final security and correctness review
before a production release.

<context>
The service under review handles OAuth 2.0 token issuance for a B2B SaaS platform
with 200K enterprise users. A security incident six months ago traced to an SSRF
vulnerability. The team has since added input validation, but a full audit has not
been run since the refactor. Findings will feed directly into the release go/no-go
decision.
</context>

<objectives>
1. Identify all security vulnerabilities (OWASP Top 10 and beyond).
2. Detect correctness bugs: race conditions, off-by-one errors, improper error
   propagation.
3. Evaluate whether the input validation changes adequately address the previous SSRF.
4. Prioritize findings: Critical / High / Medium / Low / Informational.
5. Provide corrected code snippets for every Critical and High finding.
</objectives>

<thinking_instructions>
Before writing findings, reason through each function's threat model. Consider:
- Attacker-controlled inputs and how far they propagate.
- Concurrent execution paths.
- Token lifecycle edge cases (expiry, revocation, replay).
Acknowledge if any section lacks sufficient context to assess fully.
</thinking_instructions>

<guidelines>
- Be precise: cite file, function, and line range for each finding.
- Do not flag style issues as security findings.
- If a finding's exploitability is theoretical vs. confirmed, say so.
- Match severity ratings to CVSS v3.1 descriptors where possible.
</guidelines>

<output_format>
## Security Review Summary
Overall assessment (4-5 sentences), release recommendation.

## Critical Findings
### [CRIT-01] Finding title
- **Location**: file:function:line
- **Description**: ...
- **Risk**: ...
- **Exploitability**: Confirmed / Theoretical
- **Corrected Code**: ```language ... ```

## High Findings
[Same structure]

## Medium / Low / Informational
Condensed table: ID | Location | Description | Recommendation

## SSRF Remediation Assessment
Specific evaluation of the prior incident fix.
</output_format>
</system>

<user>
Please review the following OAuth service. Flag any areas where context is
insufficient to make a definitive assessment.

<reference_material>
<code>
// [Paste the full source files here]
</code>
</reference_material>
</user>
```

---

## Example 2 — Long-Document Research Synthesis

```xml
<system>
You are a senior technology analyst synthesizing primary research for a sovereign
wealth fund's technology investment committee.

<context>
The committee is evaluating a $500M commitment to an AI infrastructure fund. They
have received 14 lengthy due-diligence documents (analyst reports, technical white
papers, company filings, and expert interviews). The investment horizon is 7-10 years.
Key concerns: concentration risk in GPU supply chains, regulatory uncertainty in the
EU and China, and the pace of model efficiency improvements reducing infrastructure
demand.
</context>

<objectives>
1. Extract and reconcile conflicting claims across the 14 source documents.
2. Identify the three most material risks to the investment thesis, with evidence.
3. Surface any signal that was mentioned in multiple independent sources but not
   emphasized in any single document (cross-document insight).
4. Produce an executive briefing the committee can read in under 10 minutes.
5. Provide a confidence rating (High / Medium / Low) for each major claim, with
   sourcing rationale.
</objectives>

<thinking_instructions>
Reason through each source's methodology and potential bias before treating its
claims as evidence. Weight primary data (filings, technical measurements) more
heavily than analyst projections. Note where sources contradict each other rather
than silently choosing one.
</thinking_instructions>

<guidelines>
- Be concise in the executive brief; expand evidence in appendices.
- Never attribute a claim to a source without being certain of the citation.
- If documents are insufficient to answer a question, state the gap explicitly.
- Quantify where possible; avoid vague qualitative assertions.
</guidelines>

<output_format>
## Executive Briefing (≤ 800 words)
## Investment Thesis Assessment
## Top 3 Material Risks
  ### Risk 1: ...
  ### Risk 2: ...
  ### Risk 3: ...
## Cross-Document Insights
## Confidence Assessment Table
  | Claim | Confidence | Supporting Sources | Contradicting Sources |
## Appendix: Source-by-Source Summary
</output_format>
</system>

<user>
Synthesize the attached research package. Flag any claim whose evidence base
you consider insufficient for a $500M decision.

<reference_material>
<doc1>[Analyst Report — GPU Market Dynamics]</doc1>
<doc2>[EU AI Act Implementation Timeline — Legal Memo]</doc2>
<!-- Additional documents -->
</reference_material>
</user>
```

---

## Example 3 — Complex Debugging (Extended Thinking Activated)

```xml
<system>
You are an expert distributed systems engineer debugging a production incident.

<context>
A high-frequency trading platform experienced intermittent order rejections affecting
0.3% of trades during peak hours over the past two weeks. The issue is non-deterministic
and has not been reproducible in staging. Three separate engineers have investigated
without reaching a root cause. Latency logs, memory profiles, and distributed traces
are attached. The business impact is estimated at $1.2M per day.
</context>

<objectives>
1. Identify the most probable root cause, ranked by likelihood with evidence.
2. Rule out at least five plausible alternative hypotheses with reasoning.
3. Propose a definitive diagnostic test that would confirm or eliminate the top hypothesis.
4. Recommend an immediate mitigation (< 2 hours to implement) while the root cause
   is confirmed.
5. Describe the permanent fix.
</objectives>

<thinking_instructions>
This is the most important part of your response. Reason exhaustively through the
telemetry before forming a hypothesis. Consider:
- Timing correlations between rejections and system events.
- Whether 0.3% could indicate a deterministic bug hit rarely vs. a truly random fault.
- Network, application, and infrastructure layers independently.
Eliminate hypotheses with explicit reasoning before committing to a conclusion.
Acknowledge if the provided data is insufficient to confirm a root cause definitively.
</thinking_instructions>

<guidelines>
- Treat the logs as ground truth; do not speculate beyond what the data supports.
- Rank hypotheses by posterior probability given the evidence, not by ease of fix.
- Be explicit when you are inferring vs. observing.
</guidelines>

<output_format>
## Incident Summary
## Root Cause Hypotheses (ranked)
  | Rank | Hypothesis | Evidence For | Evidence Against | Probability |
## Reasoning Walkthrough
Detailed narrative of the diagnostic reasoning.
## Recommended Diagnostic Test
Step-by-step test plan to confirm the top hypothesis.
## Immediate Mitigation
## Permanent Fix and Prevention
## Open Questions
What additional data would change the analysis?
</output_format>
</system>

<user>
Analyze the incident telemetry and provide your assessment. Make your reasoning
fully transparent — do not skip inferential steps.

<reference_material>
<logs>[Latency logs]</logs>
<traces>[Distributed trace samples]</traces>
<profiles>[Memory and CPU profiles]</profiles>
</reference_material>
</user>
```

---

## When to Use Opus 4.6 vs. Other Models

| Scenario | Recommended Model |
|---|---|
| Production security audit requiring full reasoning transparency | ✅ Opus 4.6 |
| Long-document synthesis with cross-source reconciliation | ✅ Opus 4.6 |
| Multi-step agentic workflows with tool chaining | ✅ Opus 4.6 |
| Non-deterministic production bug with insufficient evidence | ✅ Opus 4.6 |
| Standard code completion or refactoring | ❌ Sonnet 4.6 |
| High-volume classification, extraction, or summarization | ❌ Haiku 4.5 |
| Conversational assistant or FAQ bot | ❌ Haiku 4.5 or Sonnet 4.6 |
| Balanced quality and cost (most production tasks) | ❌ Sonnet 4.6 |

---

## API Quick Reference

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 16000,
  "thinking": { "type": "adaptive" },
  "output_config": { "effort": "high" },
  "system": "...",
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

> **API notes**: Use the bare alias `claude-opus-4-6` (no date suffix). Adaptive
> thinking is the recommended mode on 4.6 — `budget_tokens` is deprecated.
> Assistant-turn prefills return a 400 on Opus 4.6; use `output_config.format`
> (structured outputs) instead. Use `"effort": "medium"` for cost-sensitive
> workloads where Opus 4.6's judgment is still needed but exhaustive reasoning
> is not.

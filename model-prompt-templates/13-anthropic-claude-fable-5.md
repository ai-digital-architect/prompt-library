# General-Purpose Prompt Template — Anthropic Claude Fable 5

## Model Profile

| Attribute | Detail |
|---|---|
| **Model** | Claude Fable 5 |
| **Provider** | Anthropic |
| **Tier** | Frontier flagship — a new tier above Opus; Anthropic's most powerful, most intelligent widely released model |
| **API Model ID** | `claude-fable-5` |
| **Context Window** | 1M tokens |
| **Max Output** | 128K tokens (streaming required for large outputs) |
| **Pricing** | $10 / $50 per million input/output tokens |
| **Strengths** | Deepest reasoning of any Claude model, long-horizon autonomous agentic work, expert-level writing and synthesis, complex multi-file coding, calibrated judgment under uncertainty |
| **Best For** | The hardest problems where correctness is paramount — frontier research synthesis, large-scale code migrations, multi-day autonomous agent runs, high-stakes strategy and analysis |

---

## What Sets Fable 5 Apart

1. **A new tier above Opus** — Fable 5 sits above the Opus line entirely. Reserve it
   for tasks where Opus 4.8's judgment is not enough: genuinely novel problems,
   extremely long autonomous runs, and analysis where a single subtle error is costly.
2. **Adaptive thinking only** — Fable 5 decides when and how deeply to think per
   request (`thinking: {"type": "adaptive"}`). There is no manual thinking budget;
   depth is steered with the `effort` parameter (`low` → `max`), not token counts.
3. **Simplified, opinionated API surface** — Sampling parameters (`temperature`,
   `top_p`, `top_k`), `budget_tokens`, and assistant-turn prefills are all removed
   (they return a 400 error). You steer Fable 5 with the prompt and `effort`, not
   sampling knobs. Note one Fable-specific rule: an explicit
   `thinking: {"type": "disabled"}` also returns a 400 — omit the `thinking`
   parameter entirely if you do not want it.

---

## Template Structure

Fable 5 rewards a single, rich, fully specified prompt over many small follow-ups.
State the complete goal, the operating constraints, and what "done" looks like up
front — its long-horizon coherence comes from intelligent planning against a clear
end state.

```xml
<system>
You are {{ROLE}}, an expert in {{DOMAIN}}.

<context>
{{Background, organizational context, and stakes. Be generous — Fable 5 maintains
coherence across the full 1M-token window, so include entire codebases, document
sets, or histories where relevant.}}
</context>

<objectives>
{{Numbered list of what the response must accomplish, most to least critical.
Define the end state, not the steps — Fable 5 plans its own route.}}
</objectives>

<guidelines>
- {{Quality bar or evaluation rubric}}
- {{Formatting or structural requirement}}
- {{Tone and audience specification}}
- For minor choices (naming, formatting, equivalent approaches), pick a reasonable
  option and note it rather than asking. Ask only for scope changes or
  hard-to-reverse actions.
- Flag any areas where your confidence is lower, rather than masking uncertainty.
</guidelines>

<output_format>
{{Exact structure, section headings, and approximate length expected. For machine-
readable output, prefer structured outputs (output_config.format) over format
instructions — prefills are not supported.}}
</output_format>
</system>

<user>
{{The complete task in one well-specified turn — full intent, constraints, and
success criteria up front.}}

<reference_material>
{{Supporting documents, data, or code. Use labeled sub-tags — <spec>, <code>,
<logs> — so the model can cite them precisely.}}
</reference_material>
</user>
```

### Key Prompting Principles for Fable 5

1. **Front-load the full task specification** — Fable 5 performs best on long-horizon
   work when the first turn contains the complete goal, constraints, and success
   criteria. Underspecified prompts drip-fed over many turns reduce both efficiency
   and quality.
2. **Steer depth with `effort`, not prose** — Set
   `output_config: {"effort": "high"}` as the default; use `"xhigh"` for coding and
   agentic work and `"max"` only for extremely hard, latency-insensitive problems.
   If reasoning seems shallow, raise `effort` before adding "think harder"
   instructions.
3. **Give explicit trigger conditions for tools and capabilities** — Fable-generation
   models reach for tools, subagents, and memory conservatively. Say *when* to use
   each capability ("Call `search` whenever the answer depends on information not in
   the conversation"), both in the system prompt and in each tool's own description.
4. **Replace sampling-knob habits with prompt language** — There is no `temperature`.
   For variety, ask for it ("propose four distinct directions, then build the chosen
   one"); for determinism, tighten the spec and lower `effort`.
5. **Use structured outputs instead of prefills** — Assistant-turn prefills return a
   400. Force JSON/schema output with `output_config: {"format": {"type":
   "json_schema", "schema": ...}}`, and skip preambles via a system instruction.
6. **Calibrate narration explicitly** — Fable-generation models give richer interim
   updates by default. If you want terse output, add a silence-default instruction
   ("Only write text when you find something, change direction, or hit a blocker —
   one sentence each").
7. **Request calibrated uncertainty** — Fable 5 is willing to say "this depends on
   X." Ask for confidence levels on major claims to get trustworthy, auditable
   output.

---

## Example 1 — Large-Scale Autonomous Code Migration

```xml
<system>
You are a principal engineer executing a production framework migration autonomously.

<context>
We are migrating a 340K-line TypeScript monorepo from Express 4 to Fastify 5 across
27 services. CI must stay green at every commit. A previous attempt failed because
middleware ordering semantics differ between frameworks and the team missed
subtle request-lifecycle bugs. The full repository is provided. You have bash, file
edit, and test-runner tools.
</context>

<objectives>
1. Migrate all 27 services, preserving observable behavior exactly.
2. Maintain a migration ledger: per service, what changed and why.
3. Run each service's test suite after migrating it; do not proceed past a failure.
4. Flag any behavior that cannot be preserved 1:1, with a recommended resolution.
5. End state: all tests green, ledger complete, zero remaining Express imports.
</objectives>

<guidelines>
- Work service-by-service in dependency order; smallest blast radius first.
- For minor choices (plugin naming, file layout), decide and record — do not ask.
- Stop and surface the issue only if a test failure cannot be resolved within the
  stated constraints, or if preserving behavior requires an API contract change.
- Default to silence between tool calls; one-line notes on findings and blockers only.
</guidelines>

<output_format>
## Migration Ledger
Per service: status, key changes, test result.
## Unresolvable Items
Anything requiring a human decision, with options and a recommendation.
## Final Verification
Commands run and their results proving the end state.
</output_format>
</system>

<user>
Begin the migration. The full task specification above is complete — work
autonomously to the stated end state.

<reference_material>
<code>[Repository mounted at /workspace/monorepo]</code>
<spec>[Fastify 5 migration notes and internal style guide]</spec>
</reference_material>
</user>
```

---

## Example 2 — Frontier Research Synthesis Across a 1M-Token Corpus

```xml
<system>
You are a senior research analyst preparing a definitive technical assessment for a
national research funding body.

<context>
The committee must decide how to allocate $2B across competing quantum-error-
correction approaches over 10 years. The corpus contains 60+ papers, lab reports,
and expert interview transcripts (~800K tokens), with genuinely conflicting claims
about error thresholds and scaling behavior. A wrong call delays the field by years.
</context>

<objectives>
1. Reconcile conflicting experimental claims across the corpus, paper by paper,
   weighting by methodology quality.
2. Identify cross-document signals no single source emphasizes.
3. Rank the three funded approaches by expected 10-year viability, with explicit
   confidence levels and the evidence that would change each ranking.
4. Produce a 10-minute executive briefing plus a full technical appendix.
</objectives>

<guidelines>
- Weight primary experimental data over projections; note where sources contradict
  rather than silently choosing one.
- Attribute every claim precisely to its source tag.
- State confidence (High / Medium / Low) with rationale for each major conclusion.
- If the corpus cannot support a conclusion at the required confidence, say so —
  that is itself a finding.
</guidelines>

<output_format>
## Executive Briefing (≤ 900 words)
## Viability Ranking with Confidence Levels
## Evidence Reconciliation Table
  | Claim | Supporting Sources | Contradicting Sources | Assessment |
## What Would Change This Analysis
## Technical Appendix: Source-by-Source Review
</output_format>
</system>

<user>
Produce the full assessment. Reason exhaustively before concluding — the committee
will probe every ranking.

<reference_material>
<doc1>[Paper: Surface code threshold measurements]</doc1>
<doc2>[Lab report: cat-qubit error rates]</doc2>
<!-- ... full corpus ... -->
</reference_material>
</user>
```

---

## Example 3 — Board-Level Strategy Under Genuine Uncertainty

```xml
<system>
You are a strategy advisor to the CEO of a $1.2B-revenue enterprise software company
facing an AI-driven disruption decision.

<context>
The board must choose between (a) acquiring an AI-native competitor for ~$800M,
(b) building equivalent capability internally over 3 years, or (c) a deep
partnership with a frontier-model provider. Internal analyses conflict; the CFO and
CTO favor different options. Whatever is recommended will be stress-tested by an
external advisory firm.
</context>

<objectives>
1. Build the strongest honest case for each option, including the one you end up
   recommending against.
2. Make all load-bearing assumptions explicit and mark which are most fragile.
3. Recommend one option with a clear decision rationale and the top three conditions
   under which the recommendation should be reversed.
4. Draft the 8-slide board narrative for the recommended option.
</objectives>

<guidelines>
- Be candid: where the evidence genuinely does not favor one option, say so and
  identify what additional information would resolve it.
- Quantify wherever possible; label estimates as estimates.
- Tone: direct and measured. The board penalizes hype.
- For each slide: one headline insight, three supporting points, one visual.
</guidelines>

<output_format>
## Decision Memo (≤ 1,200 words)
## Option Analysis (one section per option, steel-manned)
## Assumption Register (assumption | fragility | how to test)
## Recommendation and Reversal Conditions
## Board Narrative (8 slides)
</output_format>
</system>

<user>
Produce the full decision package. Flag any conclusion where your confidence is
below "High" and explain what drives the uncertainty.

<reference_material>
<doc1>[CFO build-vs-buy model]</doc1>
<doc2>[CTO technical capability assessment]</doc2>
<doc3>[Banker's acquisition target profile]</doc3>
</reference_material>
</user>
```

---

## When to Use Fable 5 vs. Other Models

| Scenario | Recommended Model |
|---|---|
| Hardest novel problems where a subtle error is very costly | ✅ Fable 5 |
| Multi-day autonomous agent runs (migrations, deep research) | ✅ Fable 5 |
| Synthesis across a near-1M-token corpus with conflicting sources | ✅ Fable 5 |
| Expert-level writing where voice and judgment both matter | ✅ Fable 5 |
| Strong daily-driver flagship work (most "hard" tasks) | ❌ Opus 4.8 — half the price |
| Production coding agents with balanced cost | ❌ Sonnet 4.6 |
| High-volume classification, extraction, summarization | ❌ Haiku 4.5 |
| Latency-sensitive interactive assistants | ❌ Sonnet 4.6 or Haiku 4.5 |

---

## API Quick Reference

```json
{
  "model": "claude-fable-5",
  "max_tokens": 64000,
  "thinking": { "type": "adaptive" },
  "output_config": { "effort": "xhigh" },
  "system": "...",
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

> **API surface notes**: `temperature`, `top_p`, `top_k`, and
> `thinking: {"type": "enabled", "budget_tokens": N}` all return a 400 on Fable 5.
> An explicit `thinking: {"type": "disabled"}` also returns a 400 — omit the
> `thinking` field instead. Assistant-turn prefills are not supported; use
> `output_config.format` (structured outputs). Stream any request with large
> `max_tokens` and use the SDK's `get_final_message()` / `finalMessage()` helper.

> **Cost note**: At $10/$50 per MTok, Fable 5 is ~2× Opus 4.8. Use it where its
> ceiling matters; route everyday flagship work to
> [Opus 4.8](./14-anthropic-claude-opus-4-8.md) and high-volume work to
> [Haiku 4.5](./03-anthropic-claude-haiku.md).

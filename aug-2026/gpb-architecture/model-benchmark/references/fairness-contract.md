# The fairness contract

## Why this exists

"We prompted each model according to its vendor's guidance" is an assertion. It
cannot be checked by a reader, it cannot be checked by CI, and it is the single
claim on which every cross-model number in the benchmark depends.

The contract turns that assertion into an artifact: a hash that must match across
every model in a comparison group, plus a lint that runs before a token is billed.
It is not a proof. It is the most an automated check can honestly do, and it is a
great deal more than trust.

## The partition

Every task is authored once as a **Canonical Prompt IR** — structure, not prose.
Adapters compile the IR into a provider-native request. The contract partitions
everything an adapter touches.

### Invariant set — an adapter may not alter these

| Field | Why it is semantic |
| --- | --- |
| `objective` | what is being asked |
| `scope` | what is in and out of bounds |
| `success_criteria` | what "done" means |
| `required_output_fields` | the output contract |
| `response_schema_ref` / `_version` | the shape the answer must take |
| `evidence_budget` | how much the model may spend looking |
| `tool_semantics` | names, params, types, enums, required flags, constraints |
| `corpus_ref` | repository, commit, mutation id |
| `evidence_provider_ref` | provider, graph version, graph hash |
| `trial_plan` | trial count and ordering seed |
| `prohibitions` | constructs no adapter may introduce |

Their canonical hash is the **`semantic_digest`**. Every model in a comparison
group must share one. Two models with different digests are not being compared;
they are two separate experiments that happen to be printed in the same table.

### Free set — an adapter is expected to differ here

This is the entire point of the Optimized lane. Differences here are the thing
being measured *out*, not smuggled in.

- prompt syntax and delimiters
- which container each section lands in (system / developer / user / system_instruction)
- section ordering
- reasoning configuration (effort, reasoning.mode, thinking_level)
- structured-output mechanism
- verbosity control and length steering
- token ceilings within the IR budget, streaming, cache layout
- tool schema **presentation**

### Tool schemas are prompt surface

Easy to miss and consequential. A tool description written in one vendor's house
style disadvantages the others, so tool schemas are rendered per provider from a
canonical tool IR — while names, parameters, types, enum values and required flags
stay invariant. Without this, the Production lane measures how well our tool
descriptions match one vendor's conventions.

## The prohibitions, and why each one is there

Each prohibited construct has a measured effect on at least one current model
generation. Introducing one for a single family turns a prompt artifact into an
apparent capability difference.

| Prohibition | Why |
| --- | --- |
| `verification_scaffolding` | Current Claude 5 models self-verify natively; "double-check your work" costs tokens and triggers over-verification. Adding it for one family and not another is a fairness leak in both directions. |
| `severity_filter` | "Only report high-severity issues" is followed literally by Sonnet 5 and Opus 4.8 and suppresses real findings. Coverage is requested at generation time; filtering is a scoring decision. |
| `reasoning_extraction` | Triggers a refusal on current Anthropic models, and raw chain of thought is not returned by any of them. Use the provider's summarized-thinking surface instead. |
| `progress_summary_scaffolding` | Obsolete on current generations, which narrate natively. Pure token cost. |
| `depth_by_prose` | Depth is a parameter, not prose. "Think harder" is unevenly effective across families and confounds the axis the sweep exists to measure. |
| `added_examples` | Few-shot examples move some families far more than others. If a task needs examples they belong in the IR, where every adapter renders the same ones. |
| `sampling_parameters` | Rejected with HTTP 400 across the Claude 5 generation and GPT-5.6; deprecated and silently ignored on Gemini 3.6. Their presence signals a stale adapter. |

### Declared exemptions

`anthropic-claude4x` is exempt from `depth_by_prose`, because Opus 4.6 accepts an
explicit thinking-instructions block that later generations penalize. The
exemption is declared in `config/lanes.yaml` and surfaces as a **warning** in the
fairness verdict, so a reviewer sees it rather than it being silently allowed.

That is the pattern for any future exemption: declare it, and make it visible.
An undeclared special case is exactly what this contract exists to prevent.

## What the validator checks

1. **Semantic digest agreement** across the comparison group.
2. **Prohibited constructs**, by pattern against the rendered prompt or the
   request body, and structurally for added examples.
3. **Requirement coverage** — every success criterion and required output field
   must survive into the rendered prompt in recognizable form. An adapter may
   rephrase; it may not drop. This catches the opposite failure from
   over-helping: an adapter that "leaned out" the prompt until a requirement
   disappeared.

   Coverage is tested on each criterion's **distinctive** vocabulary — the words
   it does not share with the objective, the scope, or the other criteria.
   Testing on all its words made the check unfireable: criteria share so much
   language that the shared words alone cleared the bar, and a prompt containing
   none of a criterion still passed. Where a criterion has no distinctive words
   at all, the validator says so as a warning rather than passing silently —
   that is a suite-authoring problem, and it is invisible to this check either
   way.
4. **Lane tightening** — in the Parity lane, a set reasoning parameter raises a
   warning, since Parity runs every model at its documented default.
5. **Budget integrity** — a request may not ask for more output than the IR budget
   allows. This is re-checked on a retry that raises the output ceiling, so a
   retry cannot edit the request past what the validator approved.

A `FAIL` stops the trial before it is billed. `guards.require_fairness_pass: true`
aborts the study.

### And one thing it reports rather than enforces: prompt-parity review

The semantic digest hashes the **IR**, not what was sent. An adapter that leaves
the IR untouched and appends text to the rendered prompt passes every check
above — and that is the most consequential form of leak, because a task-specific
hint is worth more than any amount of prompt tuning.

So the run also strips every IR-derived string from each rendered prompt and
keeps what remains: the adapter's own boilerplate. A residual line that appears
for **exactly one task** is content that entered from outside the IR, and it is
surfaced as a **prompt-parity note** at the end of the run.

It is a note, not a violation, and the reason is worth being clear about:
adapters legitimately emit conditional blocks — a questions header only when the
IR carries questions — and from here that looks identical to a leaked hint.
Failing on it would fail honest adapters; ignoring it would miss the leak.
Reporting it puts a human in front of the one thing only a human can judge.

Two limits, stated plainly:

- A **constant** hint appended to every task passes. It is indistinguishable
  from boilerplate by this method — though it helps every task equally rather
  than leaking oracle content into one, and it is visible in a rendered-prompt
  review.
- A leak **phrased in words the IR already uses** is stripped along with the IR
  text.

Neither is fixable by an automated check on a single rendering. The backstop is
reading one rendered prompt per adapter version by hand:

```bash
python3 mb.py compile --suite suites/security-v1.yaml --task SEC-0001 --show gemini-3.6-flash
```

## What it cannot check

The validator has no opinion on whether a rendering is *good*. It cannot tell you
that your Gemini adapter buried the task under context, or that your Claude
adapter's guidelines contradict each other. Read a rendered prompt by hand at
least once per adapter version:

```bash
python3 mb.py compile --suite suites/security-v1.yaml --task SEC-0001 --show gemini-3.6-flash
```

Ask: would a careful engineer given only this text produce the answer the oracle
expects? If not, the adapter is the problem, not the model.

## The three lanes

| Lane | Free set | Effort policy | Answers |
| --- | --- | --- | --- |
| **Parity** | role placement, output mechanism, token ceiling, streaming | documented default | Which model is stronger, holding prompt quality as constant as the APIs allow? |
| **Optimized** | full free set | full sweep | What is the best each model can do? |
| **Production** | full free set + orchestration, retrieval, subagents | full sweep | What does the platform achieve? |

**Parity is deliberately unflattering to every model** and will understate all of
them, unevenly. It is not the headline lane. It exists so that Optimized-lane
gains can be attributed to adapters rather than to models — and the gap between
the two lanes *is* the adapter's measured value, which is a genuinely useful
number in its own right.

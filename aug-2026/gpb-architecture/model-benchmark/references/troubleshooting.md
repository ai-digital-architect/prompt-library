# Troubleshooting

Ordered by how often each one bites.

## `HARNESS_ERROR` on every trial

**Missing credentials.** `mb.py doctor` shows which providers are visible. Nothing
downstream is salvageable; stop and fix rather than letting the run continue.

**HTTP 400 — "likely a stale adapter".** Almost always a parameter the provider now
rejects. The usual suspects: `temperature`, `top_p`, `top_k`, `budget_tokens`, or
an assistant-turn prefill. All return 400 across the Claude 5 generation and
GPT-5.6. Check the adapter against `references/provider-notes.md`.

**HTTP 401/403.** Authentication, not capability. The disposition says so
explicitly so it never reaches the scorer.

## Different `semantic_digest` across models

The run is not a comparison. `mb.py compile --all-models --dry-run` prints the
groups:

```
2 distinct semantic digests — this is not a valid comparison:
  sha256:f4287f6358a5…  claude-opus-5, gpt-5.6-sol
  sha256:9b12ce4471aa…  gemini-3.6-flash
```

Causes, in order of likelihood:

1. An adapter mutated the IR instead of copying from it. Adapters must treat the
   IR as immutable.
2. A model-specific branch changed a semantic field rather than a presentation
   one — e.g. rewriting the scope statement instead of relocating it.
3. Different budget overrides reached different models.

## Fairness `FAIL`: "prohibited construct"

The rendered prompt matched a pattern in `config/lanes.yaml`. Read the `why` in
the violation message — each prohibition exists because the construct has a
measured effect on at least one current generation.

If the construct is genuinely required for one family, add a **declared exemption**
(`exempt_adapters`) rather than deleting the prohibition. The exemption surfaces
as a warning in the verdict, so a reviewer sees it. An undeclared special case is
exactly what the contract exists to prevent.

## Fairness `FAIL`: "requirement missing from the rendered prompt"

The adapter dropped a success criterion or a required output field. Usually the
result of leaning a prompt out too aggressively. An adapter may rephrase; it may
not drop.

The check is deliberately crude (content-word overlap) so it catches deletions
without policing paraphrase. If it fires on a legitimate rewording, the rewording
has probably gone far enough to be worth reviewing anyway.

## Every model scores zero on a new task

Almost always the oracle, not the models.

1. Are the oracle's `entities` resolvable? Check `resolution.unresolved_refs` in
   `grades.jsonl`. An oracle naming symbols the resolver cannot find will zero
   every model and look like a hard task.
2. Do the oracle's evidence line ranges match the corpus? Line drift after an edit
   silently breaks location overlap.
3. Is the oracle's `type` in the ontology, or at least consistent with what models
   emit? A type nothing maps to never matches.

## Every model scores 100 on a new task

Also usually the oracle. Either it is trivially discoverable, or the matching is
too permissive — check whether findings are matching at `adjacent` tier on type
alone. Run `mb.py report` and look at the item's discrimination: an item nothing
separates should be retired.

## `SCHEMA_INVALID` clustered on one model

Check `schema.errors` in the grade. Two common causes:

- The response schema attached through the API was rejected or reduced. Gemini
  accepts a narrower JSON Schema subset — the adapter strips unsupported keywords,
  and a new keyword in the schema can slip through.
- The model returned prose. `normalize.py` recovers from fences and surrounding
  text, but not from a response that never attempted JSON.

First-pass schema validity is published per model because it is a real production
property — but a systematic failure on one model is usually the adapter.

## `REFUSAL_SAFETY` clustered on one model and one suite

Real, and worth recording rather than working around. Two things to check:

- Is the task phrasing unnecessarily adversarial? A security review can be
  requested defensively without asking for exploit construction.
- Is the rate above 10%? The suite comparison will be flagged `LOW_CONFIDENCE`,
  and that flag is the honest reading — the surviving trials are a biased sample.

**Never** re-run refusals until you get an answer and score only the successes.
That converts a refusal rate into an invisible bias.

## Cassette not found in replay

```
no cassette for gpt-5.6-sol / SEC-0003 / trial 2
```

Deliberately an error rather than an empty response: an empty response would score
as recall-zero and look like a model failure. Record one with
`mb.py run --live --record`, or add a fixture.

## Quality identical across every effort level

The sweep is not reaching the provider. Check a manifest's `runtime.effort` and
the request body — most often the effort parameter is being set on the wrong path
(`output_config.effort` vs top-level, `thinking_level` vs `thinking_budget`).

In replay mode this is expected: bundled cassettes are keyed on (model, task,
trial) and do not vary by effort.

## "Not significant" on every comparison

Read the MDE column. With few tasks the design cannot detect small differences,
and that is a design fact rather than a finding. Add **tasks**, not trials —
trials reduce within-task noise, tasks reduce the standard error of the
comparison.

## Report refuses to render

```
refusing to render a comparison across incompatible versions
```

Scoring, matcher, resolver or response-schema versions differ within the round.
Re-run or backfill. `--allow-incompatible` renders it labelled, which is
occasionally the right call for a quick look and never the right call for a
published number.

## Costs look implausibly low

Check `cache_state` and the `flags` column. Warm-cache figures understate the
marginal cost of new work; `promotional` figures expire; `imputed` figures are
inherited from a sibling model. All three are footnoted in the report — the
footnotes are the answer, not an afterthought.

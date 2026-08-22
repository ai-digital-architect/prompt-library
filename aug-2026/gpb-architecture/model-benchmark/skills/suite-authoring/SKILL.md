---
name: suite-authoring
description: >
  Write benchmark tasks, oracles, seeded vulnerabilities and mutation-generated
  ground truth. Covers oracle provenance, the TRUE/FALSE relation pattern,
  unanswerable items, mutation validity gates, item discrimination, and the
  sealed-set discipline that keeps scores meaningful over time.
parent: model-benchmark
---

# Suite authoring

A benchmark is only as good as its ground truth. Most of the work here is not
writing tasks — it is making the oracle checkable, keeping it honest, and
retiring items that have stopped telling you anything.

## The shape of a task

```yaml
- id: SEC-0142
  suite: security-v1
  version: 1.3.0
  difficulty: 3          # authored estimate; replaced by observed difficulty
  sealed: false
  tags: [java, persistence, injection]

  prompt:
    persona: ...
    objective: ...       # the end state, not the procedure
    scope: ...           # what is in and out of bounds — state it explicitly
    success_criteria: [...]
    context: {...}
    reference_material: [...]
    questions: [...]     # for question-style suites; each declares `answerable`

  oracle:
    provenance: SEEDED_MUTATION
    findings: [...]
    relations: [...]
    answers: [...]

  budget: {...}
```

## Four patterns that make an oracle checkable

### 1. Pair every TRUE relation with a FALSE one

```yaml
relations:
  - { subject: PaymentService, predicate: CALLS, object: KafkaPublisher.publish,
      modality: asynchronous, truth: true }
  - { subject: KafkaPublisher, predicate: CALLS, object: PaymentRepository.save,
      truth: false }
```

Asserting the true ones measures recall. Asserting the false ones measures
hallucination. **A suite made only of true relations rewards a model that asserts
everything**, and you will not notice until a model that asserts everything tops
the leaderboard.

Write false relations that are *plausible* — structures a careless reader would
assume exist. A false relation nobody would ever claim tests nothing.

### 2. Include at least one unanswerable item

```yaml
questions:
  - id: Q-03
    text: "What is the p99 latency of the external gateway call in production?"
    answerable: false      # no telemetry in the corpus
```

Correct abstention earns full credit; answering earns an over-claim penalty at
1.5× a normal false positive. Without an unanswerable item you cannot distinguish
a model that knows the limits of the evidence from one that guesses well — and in
a controls or compliance workflow that distinction is the whole ballgame.

Two derived metrics keep this honest: abstention precision punishes a model that
abstains everywhere, over-claim rate punishes one that answers everything. A model
has to actually know which items are answerable.

### 3. Include a clean-file control

A suite where every item contains a defect teaches models to always find one. At
least one item per suite should have an empty oracle, where the correct answer is
an empty findings array. `security-v1/SEC-0002` is the pattern.

This is the single most informative item in a suite for measuring over-claiming,
and the first one people forget to write.

### 4. Record oracle provenance, and let it be challenged

```yaml
oracle:
  provenance: HUMAN_CURATED     # or STATIC_ANALYSIS | SEEDED_MUTATION | TEST_DERIVED
  curator: "engineering-intelligence"
  reviewed_on: "2026-08-22"
```

When a model disputes an oracle, route it to a review queue rather than scoring it
as an error. Benchmarks decay when their ground truth becomes unchallengeable —
and a frontier model disputing your oracle is exactly the signal worth reading.

## Writing the prompt half

The prompt is authored once and rendered per model, so write it as *content*, not
as formatting. Three habits matter:

- **State the scope explicitly.** Models that follow instructions literally
  (Sonnet 5) will not infer that a requirement applies to the whole corpus, and
  models that expand scope readily (Opus 5) need the boundary drawn. "for every
  file in the corpus, not only the first" belongs in the IR, where every adapter
  renders it identically.
- **Prefer real artifacts to prose about them.** A failing test, an actual schema,
  the real intended-architecture spec — all outperform a paragraph describing one,
  on every model in the roster.
- **Never ask for reasoning traces.** Requests to reproduce, echo or explain
  internal reasoning trigger a refusal on current Anthropic models, and raw chain
  of thought is not returned by any of them. `reasoning_extraction` is in the
  prohibition list; a task that adds it will fail the fairness validator.

## Mutation-generated ground truth

Mutation is the strongest answer to contamination: the mutation engine knows
exactly what it changed, so the mutation *is* the oracle, and thousands of private
variants make memorization nearly irrelevant.

A mutation is only admitted after all five gates:

1. **Build gate** — the mutated corpus compiles.
2. **Test gate** — the existing test suite behaves as declared (still green for a
   latent defect, or red in a specific declared way).
3. **Non-equivalence gate** — an automated check plus a static-analysis
   differential confirms a real behavioural change. Semantically-equivalent
   mutants are rejected; they punish models for being right.
4. **Single-defect gate** — re-run the oracle extraction over the mutant to
   confirm it did not accidentally introduce a *second*, undeclared defect. This
   one bites more often than expected.
5. **Human spot audit** — sample 10% (floor 5%) for engineer review. Publish the
   audit's rejection rate; it gates the generator's release.

Also **stratify by difficulty**. Without it a generator drifts toward emitting
easier items over time, and scores rise with no capability change — a benchmark
that congratulates itself.

## Item analysis: retire what separates nothing

After each round, `mb.py report` computes per item:

- **observed difficulty** = 1 − mean credited score across models
- **discrimination** = point-biserial correlation between item score and total score

An item every model passes, or every model fails, carries no information and costs
money on every round. Below ~0.15 discrimination, move it to a cheap regression
set: still run to catch regressions, excluded from the headline index.

This is how a suite stays sharp as it grows instead of just getting slower.

## Sealed set discipline

- **Development set** — visible, used to improve prompts, adapters, orchestration.
- **Sealed set** — never exposed to prompt authors or agents, transcripts access-
  controlled, with a **submission budget** (start at 4 evaluations per quarter per
  prompt-profile version) so the sealed set cannot be fitted iteratively.

Publish the **generalization gap** — development score minus sealed score —
beside every headline number. A widening gap is the signal that the programme is
fitting its own benchmark, and it is the only reliable one you get.

Rotate sealed items into a public regression set on a declared cadence and replace
them with fresh mutations.

## Choosing beta

`f_beta` is declared per suite and versioned, because using one beta everywhere is
a hidden policy choice:

| Suite | beta | Why |
| --- | ---: | --- |
| security | 1.5 | recall-leaning — a missed vulnerability costs more than a false alarm |
| semantic, architecture | 1.0 | balanced |
| resiliency | 1.2 | mildly recall-leaning |
| controls | 0.7 | precision-leaning — a false non-compliance finding pulls a control owner into an investigation that finds nothing |

## Validate before committing

```bash
python3 mb.py compile --suite suites/my-suite.yaml --all-models --dry-run
python3 mb.py test
```

The first proves every model gets the same question. The second proves the oracle
is reachable by the grader — an oracle whose entities the resolver cannot find
will score every model at zero and look like a hard task rather than a broken one.

---
name: run-execution
description: >
  Execute a benchmark run: compile, fairness-validate, invoke, disposition and
  store. Covers the three execution modes, the retry and disposition policy,
  what to check mid-run, and how to stop a run that has stopped being informative.
parent: model-benchmark
---

# Run execution

The order of operations is the design:

```
compile → FAIRNESS VALIDATE → invoke → disposition → normalize → store
```

Validation before invocation, so a study that was never a valid comparison costs
nothing to discover. Disposition before normalization, so a safety refusal never
reaches the scorer as an empty finding set.

## Three modes, and when each is right

| Mode | What it does | Use it for |
| --- | --- | --- |
| `--dry-run` | compile + fairness-validate + cost estimate; no calls | Every change to an adapter, a suite, or the IR. Free. |
| `--replay` | recorded cassettes through the full pipeline | CI, and every change to normalization, matching, scoring or statistics |
| `--live` | real provider calls with retry and backoff | Actual measurement |

Replay is not a convenience. Grading, matching, scoring, calibration and
statistics are the parts most likely to carry a subtle bug and the parts you
least want to debug by spending money across eleven providers. Run `mb.py test`
after any change to them.

## Before a live run

```bash
python3 mb.py doctor --check-configs
python3 mb.py plan --benchmark config/my-study.yaml --estimate
python3 mb.py compile --suite suites/my-suite.yaml --all-models --dry-run
```

Three things must be true before spending:

1. **`doctor` reports a clean config secret scan.** The harness never reads
   credentials from config files; if one is committed there, rotate it.
2. **The estimate fits inside `guards.max_total_spend_usd`.**
3. **Every model shares one `semantic_digest`.** Different digests mean the models
   are answering different questions and the run cannot be a comparison.

## Running

```bash
python3 mb.py run --benchmark config/my-study.yaml --live --record
```

`--record` writes cassettes as it goes, so the round becomes replayable
afterwards. Every cassette is redacted before it is written — it is a persisted
artifact and gets the same treatment as a transcript.

`--include-retired` is required to run a model the registry marks retired. Expect
`PROVIDER_ERROR`; that is not a capability failure and is dispositioned as such.

## Dispositions — the part that decides whether the results mean anything

Every trial ends in exactly one:

| Disposition | Handling |
| --- | --- |
| `OK` | scored |
| `REFUSAL_SAFETY` | **excluded from quality scoring**, refusal rate published with categories |
| `REFUSAL_POLICY` | graded, reported separately |
| `SCHEMA_INVALID` | graded on whatever parsed; never counts as a success |
| `TRUNCATED` | retried once at a higher ceiling, then graded; never counts as a success |
| `BUDGET_EXCEEDED` | graded; budget-pressure rate published |
| `TIMEOUT` | retried once, then graded; never a success |
| `RATE_LIMITED` | retried with backoff; **never** a capability failure |
| `PROVIDER_ERROR` | retried, then excluded and reported |
| `HARNESS_ERROR` | excluded; the run is quarantined until fixed |

Two rules make exclusion safe rather than convenient:

- **Exclusions are always published.** A model that declines 30% of the security
  suite has a decision-relevant property. Hiding it behind an exclusion is as
  misleading as scoring it zero.
- **Above 10% exclusion the suite comparison is flagged `LOW_CONFIDENCE`.** The
  surviving trials are a biased sample of the task set, and a ranking over them is
  not a clean ranking.

`HARNESS_ERROR` on HTTP 400 usually means a stale adapter — most often a sampling
parameter that the provider now rejects. Fix the adapter; do not retry.

## What to watch mid-run

The per-trial line shows model, task, trial, disposition and quality. Three
patterns are worth stopping for:

- **A wall of `HARNESS_ERROR`** — credentials, or an adapter sending something the
  provider rejects. Nothing downstream is salvageable; stop and fix.
- **`REFUSAL_SAFETY` clustering on one model and one suite** — real, and worth
  recording, but if it exceeds ~10% that suite's comparison will be flagged and
  you may want to reconsider the task phrasing before spending the rest of the
  budget.
- **Identical quality across every effort level** — the sweep is not doing
  anything. Usually the effort parameter is not reaching the provider; check a
  manifest's `runtime.effort` and the request body.

## Spend control

`guards.max_total_spend_usd` is enforced during the run, not just estimated. When
it trips, the run stops and logs it. The trial matrix is ordered so that stopping
early loses the tail rather than a whole model, but a truncated run is still a
biased sample — re-run rather than reporting it.

## What lands on disk

```
runs/<run_id>/
├── study.json          the study definition, redacted
├── manifests.jsonl     one per trial — full reproducibility record
├── grades.jsonl        one per trial — every scored axis
├── transcripts/        content-addressed, identity-free
├── events.jsonl        fairness failures, spend events, credential gaps
└── report.md / .json   after `mb.py report`
```

Transcripts are stored **separately from model identity** so a reviewer working on
blinded judging cannot undo the blinding by opening one file. The manifest holds
the model; the transcript holds the content.

## After the run

```bash
python3 mb.py report --run-dir runs/<run_id>
```

Read the comparability statement and the exclusion table before the rankings. If
either says the round is compromised, the ranking is not the story.

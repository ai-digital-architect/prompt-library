---
name: model-benchmark
description: >
  Benchmark and compare frontier LLMs (Claude Fable 5 / Opus 5 / Opus 4.8 / 4.7 / 4.6 / Sonnet 5,
  GPT-5.6 Sol / Terra / Luna, Gemini 3.6 Flash / Gemini 3 Pro) on enterprise software-engineering
  tasks using an evidence-first harness: canonical prompt IR, per-model adapters, a machine-enforced
  fairness contract, deterministic and code-graph grading, a blinded judge tribunal, and honest
  cost/latency economics. Use this skill whenever the user wants to evaluate, benchmark, compare,
  score, A/B, bake-off, or choose between AI models or LLMs; whenever they mention model routing,
  model selection at scale, LLM leaderboards, eval suites, pass@k / pass^k, judge panels,
  LLM-as-a-judge, prompt-parity or prompt-fairness testing, cost-per-correct-answer, or measuring
  whether a retrieval/code-graph/agent layer actually helps. Also use it when they ask to add a new
  model to an existing benchmark, author eval tasks or oracles, seed vulnerabilities or mutations
  for ground truth, or explain why two models' scores are not comparable. Works under Claude Code,
  GitHub Copilot, and any agentic application via the bundled `mb` CLI.
license: Proprietary — internal use
metadata:
  version: 1.0.0
  schema_versions:
    prompt_ir: 1.0.0
    findings: 1.0.0
    run_manifest: 1.0.0
    scoring: 1.0.0
  prompt_library: ../  # model-prompt-templates (read-only source of adapter guidance)
---

# Model Benchmark — Engineering Intelligence Evaluation Harness

Benchmark LLMs on how well they **understand and reason about a real software
system**, not on how nicely they write. Models generate hypotheses; deterministic
tooling and the code graph verify facts; judges rule only on what cannot be
verified.

This SKILL.md **orchestrates**. The implementation lives in `scripts/`, the
stage-specific procedure lives in `skills/<leaf>/SKILL.md`, and the normative
rules live in `references/`. Load only what the current stage needs.

---

## Before anything else: three rules that prevent wrong conclusions

These three mistakes are how benchmarks produce confident, wrong answers. They
are cheap to avoid and expensive to discover later.

1. **A safety refusal is not a wrong answer.** Current models can decline with a
   refusal stop reason at HTTP 200. Scoring that as an empty finding set gives
   recall 0 and systematically penalizes classifier-bearing models on exactly the
   suite most likely to trigger classifiers — security. Every trial must end in a
   *disposition* (`references/scoring-spec.md` § Dispositions), never in a silent
   zero.

2. **`effort: "high"` is not a common unit.** Anthropic `output_config.effort`,
   OpenAI `reasoning.effort`, and Google `thinking_level` are three different
   scales, and the ladder shifts between generations of the same family. Compare
   models at **iso-cost / iso-latency budget points on a swept Pareto frontier**,
   never at the string `"high"`.

3. **Cross-provider token counts are not a capability metric.** Tokenizers
   differ materially — Claude Sonnet 5 emits roughly 30% more tokens than
   Sonnet 4.6 for identical text. Compare *cost* and *wall-clock*. Report tokens
   only within a provider family.

---

## Routing — pick the leaf subskill

Read exactly the one that matches the user's stage. Do not preload them all.

| The user wants to… | Load |
| --- | --- |
| Scope a study: which models, which lanes, how many trials, what it will cost | `skills/benchmark-planning/SKILL.md` |
| Add, revise or debug a model adapter (new model, new provider, prompt rendering) | `skills/adapter-authoring/SKILL.md` |
| Write eval tasks, oracles, seeded vulnerabilities or mutations | `skills/suite-authoring/SKILL.md` |
| Actually run the benchmark (compile → validate → invoke → store) | `skills/run-execution/SKILL.md` |
| Turn raw responses into scores (normalize → resolve → match → score → stats) | `skills/grading-and-scoring/SKILL.md` |
| Stand up or operate the blinded judge panel, or calibrate judges against humans | `skills/judge-tribunal/SKILL.md` |
| Produce frontiers, leaderboards, uplift analysis, or a routing policy | `skills/reporting-and-routing/SKILL.md` |
| Bump a version, migrate a schema, decide whether a backfill is required | `skills/change-management/SKILL.md` |

Normative references, loaded on demand:

| Reference | Read it when |
| --- | --- |
| `references/fairness-contract.md` | Authoring or reviewing an adapter, or explaining why a comparison is valid |
| `references/scoring-spec.md` | Any question about matching, credit, abstention, calibration, dispositions |
| `references/statistics.md` | Choosing trial counts, reporting differences, interpreting "no significant difference" |
| `references/economics.md` | Cost modelling, pricing tables, cold vs warm, cost per correct finding |
| `references/security.md` | Credentials, transcript redaction, corpus sensitivity, retention posture |
| `references/provider-notes.md` | Per-family API surface facts (effort ladders, rejected params, refusal shapes) |
| `references/troubleshooting.md` | A run failed and you need the disposition and the fix |

---

## The pipeline

```text
  suite task (YAML)
        │
        ▼
  Canonical Prompt IR ──────────────► semantic_digest  (invariant across models)
        │
        ▼
  Adapter.compile()  ── free set only: syntax, placement, effort, schema mechanism
        │
        ▼
  Fairness validator ── PASS/FAIL before a single token is billed
        │
        ▼
  Adapter.invoke()  ── live | --dry-run | --replay
        │
        ▼
  Disposition ── OK | REFUSAL_SAFETY | SCHEMA_INVALID | TRUNCATED | BUDGET_EXCEEDED | …
        │
        ▼
  Normalize → Entity resolve → Claim verify (evidence provider) → Finding match
        │
        ▼
  Deterministic score ─┬─► Tribunal (only for unverifiable dimensions)
                       │
        ▼              ▼
  Statistics (paired cluster bootstrap, pass@k, pass^k)
        │
        ▼
  Frontiers → Leaderboard → Routing policy
```

---

## Quickstart

Everything runs through one CLI. Run it from the skill root.

```bash
cd <skill-root>/scripts

# 0. Environment check — Python, PyYAML, which provider keys are visible.
python3 mb.py doctor

# 1. What is in the registry? (11 models, capability + status flags)
python3 mb.py models list
python3 mb.py models show claude-opus-5

# 2. Compile a task for every model and validate the fairness contract.
#    No provider calls, no spend. This is the first thing to run on any change.
python3 mb.py compile --suite suites/semantic-v1.yaml --task SEM-0001 --all-models --dry-run

# 3. Estimate what a full study costs before committing to it.
python3 mb.py plan --benchmark config/benchmark.example.yaml --estimate

# 4. Run against recorded cassettes — full pipeline, zero keys, zero spend.
python3 mb.py run --benchmark config/benchmark.example.yaml --replay

# 5. Grade, score, and report.
python3 mb.py grade --run-dir runs/<run_id>
python3 mb.py score --run-dir runs/<run_id>
python3 mb.py report --run-dir runs/<run_id> --format md

# 6. Live run (requires keys; see references/security.md before you do this).
python3 mb.py run --benchmark config/benchmark.example.yaml --live
```

`mb.py --help` and `mb.py <subcommand> --help` list every flag.

---

## Operating discipline

**Always dry-run before spending.** `compile --dry-run` exercises the IR, the
adapters and the fairness validator, and prints a cost estimate. A study that
fails the fairness contract has produced no information regardless of how much
it cost.

**Always run the replay suite after touching scoring.** `mb.py test` replays
recorded cassettes through normalization, resolution, matching, scoring and
statistics. If scoring changed, the leaderboard is no longer comparable to
previous rounds until a backfill runs — see `skills/change-management/`.

**Never edit the prompt-template library.** The per-model templates in the parent
`model-prompt-templates/` folder are the upstream source of adapter guidance and
are read-only. Adapters *cite* them; they do not modify them. When a template is
updated upstream, bump the adapter version and note the change in `CHANGELOG.md`.

**Never ask a model to reproduce its internal reasoning.** Current Anthropic
models decline reasoning-extraction requests, and raw chain of thought is not
returned by any of them. Where reasoning visibility is needed, use the provider's
summarized-thinking surface and treat it as display text.

**Publish exclusions.** A model with a 30% refusal rate on the security suite has
an important property. Hiding it behind an exclusion is as misleading as scoring
it zero. The report renders exclusions beside every headline number.

---

## Model roster

Eleven models are registered. Full detail: `config/models.yaml`, or
`mb.py models list`.

| Model | ID | Family / adapter | Status |
| --- | --- | --- | --- |
| Claude Fable 5 | `claude-fable-5` | `anthropic-claude5` | current — Anthropic flagship; mandatory 30-day retention, no ZDR |
| Claude Opus 5 | `claude-opus-5` | `anthropic-claude5` | current |
| Claude Sonnet 5 | `claude-sonnet-5` | `anthropic-claude5` | current — new tokenizer, ~30% more tokens |
| Claude Opus 4.8 | `claude-opus-4-8` | `anthropic-claude4x` | legacy (delisted, active) |
| Claude Opus 4.7 | `claude-opus-4-7` | `anthropic-claude4x` | legacy — **derived profile**, no upstream template; see note |
| Claude Opus 4.6 | `claude-opus-4-6` | `anthropic-claude4x` | legacy (delisted, active) |
| GPT-5.6 Sol | `gpt-5.6-sol` | `openai-gpt56` | current — OpenAI flagship; only tier with `reasoning.mode: "pro"` |
| GPT-5.6 Terra | `gpt-5.6-terra` | `openai-gpt56` | current |
| GPT-5.6 Luna | `gpt-5.6-luna` | `openai-gpt56` | current |
| Gemini 3.6 Flash | `gemini-3.6-flash` | `google-gemini3x` | current — Google flagship |
| Gemini 3 Pro | `gemini-3-pro` | `google-gemini3x` | **retired / shut down — disabled by default** |

Two roster notes matter when reading results:

- **Claude Opus 4.7** has no dedicated template in the prompt library. Its
  adapter profile is *derived* from the Opus 4.8 profile, which the library
  states shares its API surface. The registry marks it `derived: true` and every
  report footnotes it. If an Opus 4.7 result is load-bearing for a decision,
  validate the profile against vendor documentation first.
- **Gemini 3 Pro** appears in Google's deprecated/shut-down list; the upstream
  template is reference-only. It is registered with `status: retired` and
  `enabled: false`, so a run must opt in explicitly with
  `--include-retired`. Expect provider errors, and disposition them as
  `PROVIDER_ERROR`, not as capability failures.

---

## Installing into a harness

The skill root is self-contained. See `install/` for the exact steps.

- **Claude Code** — copy or symlink the skill root to
  `.claude/skills/model-benchmark/`. `install/claude-code.md`.
- **GitHub Copilot** — copy or symlink to `.github/skills/model-benchmark/`.
  `install/github-copilot.md`.
- **Agentic application** — read `skill.json` for entrypoints and subskill
  routing, and shell out to `scripts/mb.py`. `install/agentic-app.md`.

`install/install.sh` does the symlinking for the first two and verifies the
result.

---

## What "done" looks like for a study

A study is complete when all of the following exist and are consistent:

1. A `fairness_verdict: PASS` on every trial in the comparison group, with one
   shared `semantic_digest`.
2. A disposition for every trial, and an exclusion table published beside the
   scores.
3. An effort sweep per model, rendered as a cost/quality frontier, with the
   declared iso-cost comparison points marked.
4. Detection, evidence, calibration, abstention, reliability and economics
   reported as **separate** axes — calibration and abstention are never folded
   into the quality index.
5. Paired cluster-bootstrap confidence intervals on every model-vs-model claim,
   with the minimum detectable effect stated.
6. A version block naming every component version, and an explicit statement of
   whether this round is comparable to the previous one.

If any of these is missing, say so rather than reporting a ranking.

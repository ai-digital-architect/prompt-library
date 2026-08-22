# model-benchmark

An Agent Skill for benchmarking frontier LLMs on how well they **understand and
reason about a real software system** — not on how nicely they write.

Models generate hypotheses; deterministic tooling and a code graph verify facts;
judges rule only on what cannot be verified. Runs from Claude Code, GitHub
Copilot, any agentic application, or headlessly in CI through one CLI.

This folder is a skill directory, not a prompt template. It sits inside
`model-prompt-templates/` and treats every template around it as **read-only
upstream**: `config/models.yaml` and the adapter specs cite them; nothing here
edits them.

---

## Quickstart

```bash
cd scripts
pip install -r requirements.txt          # PyYAML is the only dependency

python3 mb.py doctor                     # environment, registry, pricing, credentials
python3 mb.py models list                # the 11-model roster
python3 mb.py test                       # full pipeline on bundled cassettes — no keys, no spend

# Validate a comparison before spending anything:
python3 mb.py compile --suite ../suites/security-v1.yaml --all-models --dry-run

# Estimate, then run:
python3 mb.py plan   --benchmark ../config/benchmark.example.yaml --estimate
python3 mb.py run    --benchmark ../config/benchmark.example.yaml --live --record
python3 mb.py report --run-dir runs/<run_id>
python3 mb.py route  --run-dir runs/<run_id>
```

---

## What it measures, and what it refuses to

| Reported | Why it is separate |
| --- | --- |
| **Quality index** (detection, evidence grounding, root cause, severity, completeness, remediation, communication) | The blended "how good was the answer" number |
| **Calibration** (Brier, ECE, discrimination AUC) | Never folded into quality. A slightly less accurate but well-calibrated model is often the better production choice, because its low-confidence output can be escalated automatically — blending hides exactly that |
| **Abstention** (precision, over-claim rate) | Knowing the limits of the evidence is a capability, not silence |
| **Reliability** (`pass@k`, `pass^k`, variance, worst trial) | `pass^k` is the production number; a model at pass@1 0.90 / pass^3 0.40 is not a reliable pipeline component |
| **Economics** (cold cost, cost per correct finding, latency) | Computed from billed token categories, not estimated |
| **Exclusions** (dispositions, refusal rates by category) | Published *before* the scores |

Three things it will not do:

- **Score a safety refusal as a wrong answer.** Refusals arrive as HTTP 200 with an
  empty-looking body; scoring them as recall zero systematically penalizes
  classifier-bearing models on the security suite — a wrong strategic conclusion
  from a parsing bug. They are dispositioned and their rate is published.
- **Compare models at `effort: "high"`.** Anthropic `output_config.effort`, OpenAI
  `reasoning.effort` and Google `thinking_level` are three unrelated scales.
  Comparisons are made at iso-cost / iso-latency points on a measured Pareto
  frontier, and a model that cannot reach a budget point is reported *absent*
  rather than extrapolated.
- **Compare token counts across providers.** Tokenizers differ materially — Claude
  Sonnet 5 emits ~30% more tokens than Sonnet 4.6 for identical text. Cost and
  wall-clock are comparable; tokens are reported within a family only.

---

## The model roster

| Model | Adapter | Status |
| --- | --- | --- |
| Claude Fable 5 | `anthropic-claude5` | current — mandatory 30-day retention, **no ZDR** |
| Claude Opus 5 | `anthropic-claude5` | current |
| Claude Sonnet 5 | `anthropic-claude5` | current — new tokenizer |
| Claude Opus 4.8 | `anthropic-claude4x` | legacy |
| Claude Opus 4.7 | `anthropic-claude4x` | legacy — **derived profile**, no upstream template |
| Claude Opus 4.6 | `anthropic-claude4x` | legacy |
| GPT-5.6 Sol | `openai-gpt56` | current — only tier with `reasoning.mode: "pro"` |
| GPT-5.6 Terra | `openai-gpt56` | current |
| GPT-5.6 Luna | `openai-gpt56` | current |
| Gemini 3.6 Flash | `google-gemini3x` | current |
| Gemini 3 Pro | `google-gemini3x` | **retired — disabled by default** |

Two roster facts that change how results must be read, and are footnoted in every
report:

- **Opus 4.7** has no dedicated template in the upstream library. Its profile is
  derived from Opus 4.8, which the library states shares its API surface. Fine for
  a trend line; validate against vendor documentation before making it
  load-bearing.
- **Gemini 3 Pro** is shut down. Registered so the roster is complete and
  historical results stay interpretable; requires `--include-retired`, and
  404-class errors are dispositioned as `PROVIDER_ERROR`, never as capability
  failures.

---

## How a comparison is made valid

Every task is authored once as a **Canonical Prompt IR**. Adapters render it per
provider. A machine-enforced fairness contract partitions what an adapter may
touch, and the validator runs **before** a token is billed.

```
suite task → Canonical IR → Adapter.compile() → FAIRNESS VALIDATE → invoke
                    │                                   │
             semantic_digest ─────────────── must match across the group
```

```
$ mb.py compile --suite suites/semantic-v1.yaml --task SEM-0001

model             adapter                   fairness  semantic      rendered      chars
claude-fable-5    anthropic-claude5/1.0.0   PASS      f4287f6358a5  e07fd1650732  2512
claude-sonnet-5   anthropic-claude5/1.0.0   PASS      f4287f6358a5  9dac34ffdf53  2614
gpt-5.6-sol       openai-gpt56/1.0.0        PASS      f4287f6358a5  8168a7543f05  2272
gemini-3.6-flash  google-gemini3x/1.0.0     PASS      f4287f6358a5  632306fdce7d  2504

  group: all 10 models share semantic_digest sha256:f4287f6358a5…
```

Different prompts, one question. `references/fairness-contract.md` has the full
partition and the prohibition list.

---

## Layout

```
model-benchmark/
├── SKILL.md               orchestrator — routing, guardrails, workflow
├── skill.json             harness-neutral manifest
├── skills/                8 leaf subskills, loaded on demand
├── references/            fairness contract, scoring spec, statistics,
│                          economics, security, provider notes, troubleshooting
├── schemas/               prompt IR, task, findings, run manifest, grade
├── config/                models, pricing, lanes, example study
├── prompts/               canonical tasks, adapter specs, judge specs
├── scripts/               mb CLI + mbcore (stdlib-only except PyYAML)
├── suites/                semantic, security, architecture, controls, resiliency
├── fixtures/              sample repo + synthetic replay cassettes
└── install/               claude-code, github-copilot, agentic-app, install.sh
```

`SKILL.md` orchestrates and routes; it does not contain the implementation. Each
leaf subskill loads only when its stage is active.

---

## Three execution modes

| Mode | Does | For |
| --- | --- | --- |
| `--dry-run` | compile + fairness-validate + cost estimate; no calls | Every adapter, suite or IR change. Free. |
| `--replay` | recorded cassettes through the full pipeline | CI, and every change to normalization, matching, scoring or statistics |
| `--live` | real provider calls with retry, backoff, disposition | Actual measurement |

Replay is not a convenience. Grading, matching, scoring, calibration and
statistics are the parts most likely to carry a subtle bug and the parts you least
want to debug by spending money across eleven providers.

---

## Installing

```bash
./install/install.sh                 # symlinks into .claude/skills and .github/skills
./install/install.sh --claude        # one harness only
./install/install.sh --copy          # pin a copy instead of symlinking
```

See `install/` for per-harness detail and CI snippets.

---

## Credentials

Read from the environment at invoke time; never from config files, never written
into prompts, manifests, transcripts, cassettes or logs.

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
```

`mb.py doctor --check-configs` refuses to proceed if a credential-shaped value is
committed to a config file. `--dry-run` and `--replay` need no credentials at all.

`references/security.md` covers redaction, transcript blinding, corpus sensitivity
and per-model retention posture — including the models where mandatory retention
makes sending a proprietary corpus a compliance decision before a benchmarking one.

---

## Change management

Suites, adapters, schemas, judges, the resolver, the matcher, the pricing table and
the scoring function are versioned independently and stamped into every manifest.

**A change to scoring, matching, resolution or the response schema invalidates
cross-version comparison until a backfill runs.** The report enforces it: a
cross-version comparison is refused unless `--allow-incompatible` is passed, and
is then labelled. Backfills cost nothing — they re-grade stored responses — which
is the practical argument for always running live rounds with `--record`.

See `skills/change-management/SKILL.md`.

---

## The bundled fixtures are synthetic

`fixtures/cassettes/` contains hand-shaped responses whose only job is to exercise
the pipeline: normalization, resolution, matching, credit tiers, calibration,
abstention, refusal and truncation dispositions, cost accounting and statistics.
Each is stamped `"synthetic": true`.

**They are not measurements of any model.** Regenerate with
`python3 fixtures/make_cassettes.py`, or record real ones with
`mb.py run --live --record`.

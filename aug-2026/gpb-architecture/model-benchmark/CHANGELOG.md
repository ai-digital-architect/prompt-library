# Changelog — model-benchmark

Every entry states what moved, **why**, and whether a backfill is required.

The "why" matters more than it looks. Six months on, the question is never "what
changed" — the manifests answer that — but "was the old number wrong, or just
different?"

## Component versions

| Component | Version |
| --- | --- |
| harness | 1.0.0 |
| scoring | 1.0.0 |
| matcher | 1.0.0 |
| resolver | 1.0.0 |
| response schema (findings-v1) | 1.0.0 |
| prompt IR | 1.0.0 |
| lanes | 1.0.0 |
| registry | 1.0.0 |
| pricing table | 2026-07-25 |
| adapter `anthropic-claude5` | 1.0.0 |
| adapter `anthropic-claude4x` | 1.0.0 |
| adapter `openai-gpt56` | 1.0.0 |
| adapter `google-gemini3x` | 1.0.0 |
| suites semantic / security / architecture / controls / resiliency | 1.0.0 |

---

## 1.0.0 — 2026-08-22

Initial release, implementing the v2 evidence-first design from
`model-evaluation-approach.md`.

**Backfill required:** n/a (no prior rounds).

### Added

- **Canonical Prompt IR and a machine-enforced fairness contract.** Tasks are
  authored once as structure; adapters render per provider. The invariant/free
  partition is declared in `config/lanes.yaml`, hashed as `semantic_digest`, and
  validated before any token is billed.
  *Why:* "we prompted each model per its vendor's guidance" is an assertion that
  cannot be checked. Every cross-model number depends on it.

- **Eleven-model registry** with capability facts traced to the read-only
  `model-prompt-templates/` library, including `derived` and `retired` flags.
  *Why:* a capability fact a reviewer cannot trace is a capability fact nobody can
  check.

- **Four adapters** across three providers, each transcribing its family's
  rendering rules from the upstream templates.

- **Failure-disposition engine.** Ten dispositions; safety refusals are excluded
  from quality scoring and their rate published with categories.
  *Why:* scoring a refusal as recall zero systematically penalizes
  classifier-bearing models on the security suite — the single most likely way this
  benchmark produces a wrong strategic conclusion.

- **Entity resolution ladder (R0–R6)** with an explicit `UNRESOLVED` bucket, a
  fuzzy-match cap, and published resolution rate.
  *Why:* without it, our own matcher's failures disappear into the model's score
  and evidence grounding becomes unfalsifiable.

- **Finding matcher** with a defined match rule, one-to-one maximum-weight
  assignment, credit tiers, an `unverifiable` bucket, and per-suite `f_beta`.
  *Why:* precision and recall need a defined notion of "the same finding"; without
  one, F1 is not reproducible across runs or reviewers.

- **Abstention scoring** — `INSUFFICIENT_EVIDENCE` as a first-class correct answer,
  a 1.5× over-claim penalty, plus over-claim rate and abstention precision so the
  metric cannot be gamed in either direction.

- **Calibration as its own axis** — Brier, ECE over equal-mass bins, discrimination
  AUC, reliability diagrams, and an optional isotonic recalibration map published
  for the routing layer.
  *Why:* blending calibration into quality hides the trade-off that matters most
  for routing.

- **Iso-budget comparison.** Full effort sweep per model under a spend cap, Pareto
  frontiers over cost and latency, comparison at declared spend points, `absent`
  where a frontier does not reach one.
  *Why:* vendor effort labels are three unrelated scales.

- **Pricing oracle** with effective dates, billed-token categories, long-prompt
  surcharges, cache-write multipliers, promotional-expiry and imputed-rate flags,
  and cold-vs-warm reporting.

- **Statistics** — paired cluster bootstrap resampling *tasks* not trials,
  `pass@k` and `pass^k`, published minimum detectable effect, Benjamini–Hochberg
  FDR control, item discrimination, generalization gap.

- **Judge tribunal scaffolding** — cross-family blinded panel, position-consistency
  checks, Bradley–Terry ranking, effective-panel-size discounting for correlated
  judges, judge-drift regression against a gold set, and a human inter-rater
  reliability gate that decides which dimensions are judgeable at all.
  Ships **disabled** in the example study.
  *Why:* a panel validated against human ground truth the humans themselves do not
  agree on produces numbers that look rigorous and cannot be defended.

- **Evidence provider SPI** with a bundled `local_graph` fallback, so every suite
  runs standalone before the platform integration exists.

- **Security posture** — environment-only credentials, constructed subprocess
  environments, redaction on every persisted artifact, identity-free transcripts,
  and per-model retention posture recorded in every manifest.

- **Five seeded suites**, a sample corpus, and synthetic replay cassettes
  exercising the refusal, truncation, schema-invalid, over-claim and clean-control
  paths.

- **Eight leaf subskills** and seven normative references, loaded on demand.

### Deliberate omissions

- `temperature` and every other sampling parameter, everywhere, including the run
  manifest. They are rejected or silently ignored across all current generations,
  and carrying the field would imply a determinism lever the platform does not
  have.
- Provider SDKs. HTTP goes through the standard library so an SDK upgrade cannot
  silently change a request default.
- Any request for a model's internal reasoning. It triggers a refusal on current
  Anthropic models and raw chain of thought is not returned by any of them.

### Hardening pass before release

An independent adversarial review of the harness ran before this version was
cut. Twenty-one findings; the ones that changed behaviour, with the invariant
each protects:

- **Redaction destroyed every token count.** A `token|secret|auth` substring
  match also ate `output_tokens` and `max_input_tokens`, so every manifest
  persisted `«redacted»` where a number belonged and cost was unauditable from
  the artifact. Now anchored to credential key names, with `_tokens` (plural)
  explicitly excluded.
- **An empty HTTP 200 was dispositioned `OK`** and scored as recall zero,
  because schema validity was only passed to the classifier when text was
  present. This is the invariant-2 failure the disposition engine exists to
  prevent, reachable from any unrecognised refusal shape.
- **Requirement coverage never fired.** Criteria share vocabulary with the
  objective and with each other, so the shared words alone cleared the bar; a
  prompt containing none of a criterion still passed. Now tested on each
  criterion's *distinctive* vocabulary, with a warning where it has none.
- **Cold cost could come out below warm.** `cache_write or cache_read` short-
  circuited when a provider returned both, billing one category nowhere and
  inverting the premise that cold is the honest upper bound.
- **A model with zero scored trials rendered as quality 0.0**, putting a model
  that was never measured last on the leaderboard — the same wrong conclusion,
  reached through the renderer instead of the scorer.
- **The retry loop pinned its policy to the first disposition** and mutated
  `max_tokens` *after* the fairness validator ran, escaping the one invariant
  checked at the request level. Policy is now re-fetched per attempt and the
  ceiling clamps to the IR budget. The `SCHEMA_INVALID` reprompt was removed
  outright: coaching a model into valid JSON after validation both escapes the
  contract and erases the metric.
- **`run_id` omitted the sweep point**, so every effort rung of a trial collided
  and the report handed one rung's latency to another rung's frontier point.
- **Greedy assignment was not maximum-weight** despite the docstring, taking a
  1.0 and forfeiting two 0.6s — understating credited findings and therefore
  cost-per-correct-finding. Replaced with a real Jonker–Volgenant solve.
- **Item difficulty was computed on the wrong scale** (`1 - mean` over a 0–100
  index gave −93.87) and **discrimination was uncorrected**, correlating each
  item against a total containing itself.
- **Calibration mis-binned**: a fixed chunk size gave every sample its own bin
  when `n < bins`, making ECE non-zero for a perfectly calibrated set. Bins now
  carry a minimum mass.
- **`coerce()` silently deleted malformed findings** and called the result
  valid, turning a genuine `SCHEMA_INVALID` into an `OK` — a repair in the
  deletion direction, which the contract forbids as much as invention.
- **Completeness contradicted detection** on clean-file controls, awarding full
  completeness for an empty oracle that detection had just scored zero.
- **`REFUSAL_POLICY` was unreachable**; every refusal was excluded. Refusal
  categories are now classified, so a scope decline scores as a miss while a
  safety decline is excluded.
- **The spend cap discarded the trial it had paid for**, breaking before the
  artifacts were written.
- **Undefined statistics rendered as measurements**: `P(A>B) = 0.000` for two
  identical models, `pass^3 = 0.00` on a one-trial study, `precision = 0.0`
  where nothing was reported. All now report as undefined.

**Added as a result of the review, not merely fixed:** a **prompt-parity
review** signal. The semantic digest hashes the IR, not what was sent, so an
adapter that leaves the IR alone and appends a hint to the rendered prompt
passed every check. The run now strips IR-derived text from each rendering and
surfaces residual lines appearing for exactly one task. It reports rather than
fails — a one-off conditional block is indistinguishable from a leaked hint by
this method — and `references/fairness-contract.md` states both of its limits.

### Known limitations

- `local_graph` is regex-based and answers `UNKNOWN` for most predicates beyond
  calls, imports and file membership. That is honest, and it means evidence scores
  under the fallback provider are conservative. Wire a real graph before drawing
  conclusions about evidence grounding.
- The claim extractor for prose-style tasks is specified but not implemented;
  structured emission covers every bundled suite.
- The mutation engine is specified (five validity gates) but not implemented; the
  bundled oracles are hand-authored or static-analysis derived.
- The prompt-parity review cannot catch a constant hint appended to every task,
  nor a leak phrased in words the IR already uses. Neither is fixable by an
  automated check on a single rendering; read one rendered prompt per adapter
  version by hand.
- `warm_cost_usd` is not populated per trial — the harness runs cold by design,
  and a warm figure would have to come from a second pass over a populated cache.

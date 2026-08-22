---
name: judge-tribunal
description: >
  Stand up and operate the blinded judge panel for dimensions with no oracle, and
  calibrate it against human ground truth. Covers the order of operations
  (humans first), panel independence, blinding and position checks, Bradley-Terry
  ranking, and the drift regression that keeps rounds comparable.
parent: model-benchmark
---

# The judge tribunal

Judges rule only on what cannot be verified: root-cause reasoning, remediation
viability, communication. Everything the graph or the toolchain can decide is
decided there first. A judge asked to grade something an oracle could have graded
is a needless source of noise and bias.

## Do these in order. The order is the point.

Most evaluation programmes stand up the panel first and validate it later, and
end up with numbers that look rigorous and cannot be defended.

### Step 1 — Build the human ground truth (100–200 items)

Senior architects and security engineers grade real responses on the dimensions
you intend to judge.

### Step 2 — Measure whether the humans agree with each other

Before any model judge is validated, compute inter-rater reliability per
dimension — Krippendorff's α, or Cohen's κ for binary dimensions. `mbcore.tribunal`
provides `krippendorff_alpha_nominal()`.

**Dimensions where your own experts fall below ~0.67 are not judgeable by a model
either.** They move to commentary and out of the scored index. This is the step
everyone skips, and skipping it means every downstream "94% human agreement" claim
is measured against a target that does not hold still.

`judgeability_gate()` implements the split.

### Step 3 — Compose the panel

Four roles plus a deterministic verifier:

| Role | Asks only |
| --- | --- |
| Evidence Auditor | Are the claims actually supported by the graph and the code? |
| Domain Expert | Is this right, in the security / architecture / resiliency / controls sense? |
| Adversarial Reviewer | Can I refute this finding? |
| Deterministic Verifier | (code) graph assertions, tests, benchmark oracle |
| Arbiter | Only the subjective dimensions still unresolved |

Rules:

- **Cross-family**: a candidate is never judged by its own family. Even blinded, a
  judge favours conventions it shares with a candidate.
- **Version-pinned**: model id, adapter id and version, prompt hash. `JudgeSpec.pin()`
  produces the pin recorded in every grade.
- **Judge prompts go through the same adapter layer** as candidate prompts, under
  the same fairness contract. Otherwise the judging layer carries exactly the
  prompt confound the lane design exists to eliminate.

### Step 4 — Measure panel independence, and discount for it

Adding judges does not add independent evidence. Correlated errors across model
panels are well documented, so compute the pairwise error correlation on the gold
set and derive an **effective panel size**:

```
n_eff = n / (1 + (n - 1) * mean_pairwise_correlation)
```

Three judges correlating at 0.9 give n_eff ≈ 1.1. Reporting them as three
overstates the evidence roughly threefold. `effective_panel_size()` returns the
number and flags strong correlation.

The fix for a correlated panel is **diversity, not count**: different families,
different lenses (correctness / security / reproducibility), not five more judges
of the same kind.

### Step 5 — Blind and randomize

- Candidates become A, B, C… in randomized order (`blind()`).
- The label→model mapping is stored separately from the transcript, so store
  access alone does not undo the blinding.
- Run **both** orders of every pair and compare (`position_pairs()`,
  `position_consistency()`). Below ~0.8 consistency, the panel's pairwise
  rankings are unreliable and should be reported as such rather than ranked.

### Step 6 — Rank with Bradley–Terry

Round-robin pairwise wins fitted to strengths (`bradley_terry()`). Pairwise
comparison with a fitted ranking is far more robust than absolute 1–10 ratings,
which drift between judges and between rounds.

### Step 7 — Regression-test the judges before every round

Re-run all judges on a fixed, human-adjudicated gold set and compare to the
recorded baseline (`judge_drift()`). If agreement moves beyond threshold, the
round is quarantined.

This is not ceremony. A silent provider-side model update re-bases every score in
the round with no other signal at all — the leaderboard simply shifts and nobody
can say why.

## Domain-specific judge weights

Human agreement differs by domain. A judge that agrees with your security
engineers 94% of the time and your architects 89% of the time should carry
different weight in the two suites. Derive the weights from measured agreement
rather than declaring one model the universal judge.

## When NOT to enable the tribunal

`config/benchmark.example.yaml` ships with `tribunal.enabled: false` on purpose.
Leave it off until:

- the human calibration set exists,
- its inter-rater reliability has been measured and published,
- and the gold-set baseline for each judge has been recorded.

Until then the deterministic dimensions carry the index, and the grade explicitly
records that root-cause, remediation and communication were not graded. A run that
honestly measures five dimensions is worth more than one that pretends to measure
eight.

## Reading tribunal output

Three fields in each grade matter more than the verdicts:

- `effective_panel_size` — how much independent evidence you actually have
- `position_consistent` — whether verdicts survived swapping the order
- `panel_version` — whether this round's panel is the same one as last round's

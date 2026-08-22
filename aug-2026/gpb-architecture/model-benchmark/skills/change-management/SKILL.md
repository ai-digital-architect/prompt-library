---
name: change-management
description: >
  Version, migrate and backfill. Decide whether a change breaks comparability with
  previous rounds, what needs a backfill, and how to record it so a number from
  March and a number from September mean the same thing — or are visibly marked as
  not comparable.
parent: model-benchmark
---

# Change management

A benchmark's value compounds only if its numbers stay comparable. The single
most common way a benchmarking programme quietly loses credibility is a scoring
change that nobody flagged, followed six months later by a trend line that turns
out to be an artifact.

## What is versioned, independently

| Component | Where | Bump when |
| --- | --- | --- |
| harness | `mbcore/__init__.py` | any release |
| scoring | `mbcore/__init__.py` | weights, credit tiers, index composition |
| matcher | `mbcore/__init__.py` | matching rules, ontology tables, assignment |
| resolver | `mbcore/__init__.py` | resolution ladder, fuzzy threshold, demotion rule |
| response schema | `schemas/findings-v1.schema.json` | required fields, enums, semantics |
| adapters | each adapter's `version` | any rendering change |
| suites | `version:` in the suite file | tasks, oracles, beta |
| lanes | `config/lanes.yaml` | free/invariant sets, prohibitions |
| registry | `config/models.yaml` | models, capability facts |
| pricing table | `config/pricing.yaml` | any rate, any effective date |
| judges / panel | `Panel.version` | model, adapter, or prompt |

Every one is stamped into every run manifest.

## The comparability rule

**A change to scoring, matching, resolution or the response schema invalidates
cross-version comparison until a backfill runs.**

These four are `COMPARABILITY_CRITICAL` in `mbcore/__init__.py`. The report
enforces it: a cross-version comparison is refused unless `--allow-incompatible`
is passed, and is then labelled.

Everything else is softer but still consequential:

| Change | Effect |
| --- | --- |
| adapter rendering | new round is not comparable **in the Optimized lane**; the Parity lane still is |
| suite tasks or oracles | per-item scores incomparable; suite-level scores incomparable if the task set changed |
| suite beta | detection scores incomparable |
| lanes: free/invariant sets | the fairness argument changed; treat as a new experiment |
| registry capability facts | usually cosmetic — unless it changes the effort ladder, which changes the sweep |
| pricing table | economics incomparable; quality unaffected |
| judge panel | tribunal-graded dimensions incomparable |

## Backfilling

A backfill re-grades **stored responses** under the new logic. It costs nothing —
no provider calls — which is exactly why there is no excuse for skipping it.

```bash
# Re-run in replay mode against the same cassettes, into a new run directory.
python3 mb.py run --benchmark config/round-3.yaml --replay --run-dir runs/round-3-backfill
python3 mb.py report --run-dir runs/round-3-backfill
```

Then compare `report.json` from the backfill to the new round. Grades are derived
artifacts and are never edited in place; the original run directory stays as the
record of what was measured under the old logic.

Backfilling requires cassettes, which is the practical argument for running live
rounds with `--record`. A round recorded is a round you can re-score for free;
a round not recorded is frozen under whatever logic scored it.

## Recording a change

Every change gets a `CHANGELOG.md` entry stating:

1. what moved,
2. **why** — the failure it fixes or the capability it adds,
3. whether a backfill is required,
4. which stored rounds were backfilled.

The "why" matters more than it looks. Six months on, the question is never "what
changed" — the manifests answer that — but "was the old number wrong, or just
different?"

## Upstream template changes

The `model-prompt-templates/` library in the parent folder is **read-only** and is
the upstream authority for every capability fact in `config/models.yaml` and every
rendering rule in the adapters. When a template is updated upstream:

1. update the registry entry and/or the adapter,
2. bump the adapter `version` and the `registry_version`,
3. note it in `CHANGELOG.md` with the template file and what changed,
4. re-run `mb.py compile --all-models --dry-run` to confirm the fairness contract
   still holds,
5. flag that the Optimized lane is no longer comparable to previous rounds.

Never edit the templates from here. They are shared with other consumers, and a
local edit turns a shared source of truth into a fork nobody knows about.

## New model added mid-programme

A model added between rounds has no history. Do not backfill it into earlier
rounds by re-running — it never faced those conditions. Report it as a new entrant
and let the trend line start where the data starts.

## Deprecating a model

Set `enabled: false` and `status: retired`; leave the entry in place. Removing it
would make historical manifests unreadable, and the registry is the only place
that explains what `claude-opus-4-7` was. `mb.py doctor` enforces that a retired
model is not enabled by default.

## Pre-round checklist

```bash
python3 mb.py doctor --check-configs   # registry consistency, pricing staleness, secret scan
python3 mb.py test                     # full replay pipeline
python3 mb.py compile --suite <suite> --all-models --dry-run   # fairness contract
```

Then confirm, in writing, in the round's notes:

- which component versions changed since the last round,
- whether a backfill was run,
- and whether this round's numbers may be compared to the last round's.

The report prints a comparability statement, but the judgement is yours to record.

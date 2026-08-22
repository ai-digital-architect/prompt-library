# Using the harness from an agentic application

The skill is harness-neutral. An application integrates at whichever level suits
it: the CLI, the Python API, or the skill documents themselves.

## 1. The CLI — the simplest integration

Every stage is a subcommand with JSON output available.

```bash
python3 scripts/mb.py run    --benchmark study.yaml --live --record
python3 scripts/mb.py report --run-dir runs/<id> --format json
python3 scripts/mb.py route  --run-dir runs/<id>
```

Artifacts land as JSONL and JSON under `runs/<id>/`, so an application can consume
them without importing anything.

Exit codes: `0` success, `1` fairness or validation failure, `2` refused (missing
credentials, incompatible versions, no run found).

## 2. The Python API

```python
import sys; sys.path.insert(0, "scripts")

from mbcore.registry import Registry
from mbcore.ir import Lanes
from mbcore.runner import compile_all_models, run_study, load_suite
from mbcore.report import build_report, render_markdown
from mbcore.util import load_config

study = load_config("config/benchmark.example.yaml")

# Validate a comparison before spending anything.
suite = load_suite("suites/security-v1.yaml")
results, ok, msg = compile_all_models(
    suite["tasks"][0], suite, study, Registry(), Lanes())
if not ok:
    raise SystemExit(msg)   # the models are not answering the same question

result = run_study(study, mode="live", record=True)
```

`skill.json` enumerates entrypoints, subskill routing and the runtime contract in
machine-readable form.

## 3. The skill documents

For an agent-driven integration, `SKILL.md` is the orchestrator and
`skills/<leaf>/SKILL.md` are loaded per stage. `skill.json` carries the routing
table so an application can decide which document to surface without parsing
Markdown.

## Extending it

| Extension point | Where |
| --- | --- |
| New provider | `mbcore/adapters/` + `adapters/__init__.py` + `secrets.PROVIDER_ENV` |
| Your code graph | implement `EvidenceProvider`, register in `evidence/base.py::get_provider` |
| Your own suites | `suites/*.yaml` against `schemas/task.schema.json` |
| Your scoring | `mbcore/score.py` — and bump `SCORING_VERSION`, which invalidates cross-round comparison until a backfill runs |

## Wiring in a real code graph

The bundled `local_graph` provider builds a lightweight symbol and call graph from
the corpus so every suite runs standalone. Replacing it is the highest-value
integration in the package, because the graph is what turns "did the model sound
right?" into "did the model say true things about this system?"

```python
class MyGraphProvider(EvidenceProvider):
    name = "codegraph"
    def resolve(self, ref, hint_file=None, hint_lines=None) -> Resolution: ...
    def verify(self, subject, predicate, obj, modality=None, negated=False) -> Verdict: ...
    def neighbors(self, node_id, edge="CALLS", depth=1) -> list[str]: ...
    def blast_radius(self, node_id) -> set[str]: ...
    def version(self) -> GraphVersion: ...
```

Two things to get right:

- **Return `UNKNOWN` freely.** A claim the graph cannot decide is not evidence
  against the model. Answering `FALSE` from ignorance converts every gap in the
  graph into an apparent hallucination.
- **`version()` must change when the graph changes.** It is recorded in every
  manifest, and two models given different graph versions are not comparable.

Then set `evidence.provider: codegraph` in the study, and label any earlier results
as fallback-graph results — the whole uplift argument depends on the difference.

## Scheduling

For recurring rounds, run `mb.py run --live --record` on a schedule and diff
`report.json` between rounds. Read the comparability statement first: if component
versions moved, the diff is not a trend.

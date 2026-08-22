#!/usr/bin/env python3
"""mb — the model-benchmark CLI.

One entrypoint for every stage, so the same pipeline runs from Claude Code,
GitHub Copilot, an agentic application, or CI.

  mb.py doctor                        environment, registry, pricing, credentials
  mb.py models list|show <id>         inspect the registry
  mb.py compile --suite … --task …    compile + fairness-validate, no spend
  mb.py plan --benchmark …            expand the trial matrix, estimate cost
  mb.py run --benchmark … [--replay]  execute
  mb.py grade --run-dir …             re-grade stored responses
  mb.py score --run-dir …             aggregate scores and statistics
  mb.py report --run-dir …            render the report
  mb.py route --run-dir …             emit a routing policy
  mb.py test                          replay the bundled fixtures end to end

Run `mb.py <command> --help` for flags.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mbcore import (  # noqa: E402
    HARNESS_VERSION,
    MATCHER_VERSION,
    RESOLVER_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SCORING_VERSION,
)
from mbcore.adapters import adapter_ids  # noqa: E402
from mbcore.ir import Lanes  # noqa: E402
from mbcore.pricing import PricingOracle  # noqa: E402
from mbcore.registry import Registry  # noqa: E402
from mbcore.report import build_report, render_markdown  # noqa: E402
from mbcore.runner import (  # noqa: E402
    RunResult,
    compile_all_models,
    expand_trials,
    load_suite,
    preflight,
    run_study,
)
from mbcore.secrets import audit_paths, key_present  # noqa: E402
from mbcore.store import RunStore, find_latest_run  # noqa: E402
from mbcore.util import bad, dim, load_config, ok, short, table, warn, write_json  # noqa: E402


# ==========================================================================

def cmd_doctor(args):
    print("model-benchmark doctor\n")
    print(f"  python              {sys.version.split()[0]}")
    try:
        import yaml
        print(f"  pyyaml              {ok(yaml.__version__)}")
    except ImportError:
        print(f"  pyyaml              {bad('MISSING')} — pip install -r scripts/requirements.txt")
        return 2

    reg = Registry()
    problems = reg.validate()
    print(f"  registry            v{reg.version} — {len(reg.all(True))} models "
          f"({len(reg.all())} enabled)")
    if problems:
        print(f"  registry checks     {bad('FAIL')}")
        for p in problems:
            print(f"      - {p}")
    else:
        print(f"  registry checks     {ok('pass')}")

    lanes = Lanes()
    print(f"  lanes               v{lanes.version} — {', '.join(lanes.ids())}")
    print(f"  adapters            {', '.join(adapter_ids())}")

    pricing = PricingOracle()
    days = pricing.staleness_days()
    stale = pricing.is_stale()
    label = bad(f"{days}d old — re-verify") if stale else ok(f"{days}d old")
    print(f"  pricing table       v{pricing.version} ({label})")

    print("\n  versions (stamped into every manifest)")
    for k, v in (("harness", HARNESS_VERSION), ("scoring", SCORING_VERSION),
                 ("matcher", MATCHER_VERSION), ("resolver", RESOLVER_VERSION),
                 ("response_schema", RESPONSE_SCHEMA_VERSION)):
        print(f"      {k:<18} {v}")

    print("\n  credentials (presence only — values are never read here or logged)")
    for provider in reg.providers():
        present = key_present(provider)
        print(f"      {provider:<18} {ok('visible') if present else dim('not set')}")

    if args.check_configs:
        cfgs = [str(p) for p in (HERE.parent / "config").glob("*.yaml")]
        leaks = audit_paths(cfgs)
        if leaks:
            print(f"\n  {bad('CREDENTIAL-SHAPED VALUES FOUND IN CONFIG')}")
            for path, pats in leaks:
                print(f"      {path}: {len(pats)} pattern(s)")
            print("      The harness never reads credentials from config files. "
                  "Move these to the environment and rotate them.")
            return 2
        print(f"\n  config secret scan  {ok('clean')}")

    print("\n  offline modes       --dry-run (compile + validate, no calls), "
          "--replay (cassettes)")
    return 0


def cmd_models(args):
    reg = Registry()
    if args.action == "list":
        rows = []
        for m in reg.all(include_disabled=True):
            flags = []
            if m.derived:
                flags.append("derived")
            if not m.enabled:
                flags.append("disabled")
            rows.append([
                m.id, m.provider, m.adapter, m.status,
                m.effort_default or "—",
                f"{len(m.effort_ladder)} rungs" if m.effort_ladder else "—",
                m.retention_posture,
                ",".join(flags) or "—",
            ])
        print(table(rows, ["model", "provider", "adapter", "status", "effort",
                           "ladder", "retention", "flags"]))
        print()
        print(dim("Effort labels are provider-native and NOT comparable across providers. "
                  "Compare at iso-cost points — see references/scoring-spec.md."))
        if reg.excluded:
            print()
            print("Deliberately not registered:")
            for e in reg.excluded:
                print(f"  {e['id']}: {e['reason']}")
        return 0

    m = reg.get(args.model_id)
    print(json.dumps(m.raw, indent=2, default=str))
    return 0


def cmd_compile(args):
    study = load_config(args.benchmark) if args.benchmark else _synthetic_study(args)
    reg, lanes = Registry(), Lanes()
    suite = load_suite(args.suite)
    tasks = suite["tasks"]
    if args.task:
        tasks = [t for t in tasks if t["id"] == args.task]
        if not tasks:
            print(bad(f"task {args.task} not found in {args.suite}"))
            return 2

    exit_code = 0
    for task in tasks:
        models = [args.model] if args.model else None
        results, group_ok, group_msg = compile_all_models(
            task, suite, study, reg, lanes, models, args.include_retired)

        print(f"\n=== {task['id']} — {task.get('title', '')}")
        rows = []
        for r in results:
            v = r["verdict"]
            rows.append([
                r["model"], r["adapter"],
                ok("PASS") if v.ok else bad("FAIL"),
                short(v.semantic_digest),
                short(v.residual_digest),
                short(r["request"].rendered_prompt_hash()),
                str(len(r["request"].rendered_prompt)),
            ])
        print(table(rows, ["model", "adapter", "fairness", "semantic", "boilerplate",
                           "rendered", "chars"]))

        for r in results:
            v = r["verdict"]
            if v.violations:
                exit_code = 1
                print(f"\n  {bad('FAIL')} {r['model']}")
                for x in v.violations:
                    print(f"      - {x}")
            for w in v.warnings:
                print(f"  {warn('warn')} {r['model']}: {w}")

        print()
        print(("  " + ok("group: ") if group_ok else "  " + bad("group: ")) + group_msg)
        if not group_ok:
            exit_code = 1

        if args.show:
            for r in results:
                if args.show in (r["model"], "all"):
                    print("\n" + "=" * 78)
                    print(f"RENDERED PROMPT — {r['model']} ({r['adapter']})")
                    print("=" * 78)
                    print(r["request"].rendered_prompt)

        if args.out:
            outdir = Path(args.out)
            outdir.mkdir(parents=True, exist_ok=True)
            for r in results:
                write_json(outdir / f"{task['id']}__{r['model']}.json", {
                    "model": r["model"], "adapter": r["adapter"],
                    "fairness_verdict": r["verdict"].verdict,
                    "violations": r["verdict"].violations,
                    "warnings": r["verdict"].warnings,
                    "semantic_digest": r["verdict"].semantic_digest,
                    "residual_digest": r["verdict"].residual_digest,
                    "rendered_prompt_hash": r["request"].rendered_prompt_hash(),
                    "rendered_prompt": r["request"].rendered_prompt,
                    "request_body": r["request"].body,
                })
            print(f"\n  wrote compiled artifacts to {outdir}/")

    return exit_code


def cmd_plan(args):
    study = load_config(args.benchmark)
    reg = Registry()
    trials = expand_trials(study, reg, args.include_retired)

    per_model: dict[str, int] = {}
    for t in trials:
        per_model[t.model_id] = per_model.get(t.model_id, 0) + 1

    print(f"Study: {study.get('study_id')}")
    print(f"Lanes: {', '.join(study.get('lanes', []))}   Trials/config: {study.get('trials')}")
    print(f"Total trials: {len(trials)}\n")

    rows = [[m, str(n)] for m, n in sorted(per_model.items())]
    print(table(rows, ["model", "trials"]))

    if args.estimate:
        pricing = PricingOracle()
        est_in = int(args.est_input)
        est_out = int(args.est_output)
        print(f"\nCost estimate — cold, {est_in:,} input / {est_out:,} output tokens per trial.")
        print(dim("Cold is deliberate: it is the honest marginal cost of a new task. "
                  "A warm-cache estimate would understate a real study."))
        print()
        rows = []
        total = 0.0
        for m, n in sorted(per_model.items()):
            try:
                c = pricing.estimate(m, est_in, est_out)
            except KeyError:
                rows.append([m, str(n), "—", "no pricing entry"])
                continue
            sub = c.usd * n
            total += sub if sub == sub else 0.0
            rows.append([m, str(n), f"${sub:,.2f}", ",".join(c.flags) or "—"])
        print(table(rows, ["model", "trials", "est. cost", "flags"]))
        print(f"\n  TOTAL ESTIMATE  ${total:,.2f}")
        cap = (study.get("guards") or {}).get("max_total_spend_usd")
        if cap and total > float(cap):
            print(bad(f"  exceeds the study's max_total_spend_usd of ${float(cap):,.2f} — "
                      f"reduce trials, models, or the effort sweep"))

    issues = preflight(study, reg)
    if issues:
        print("\nPre-flight notes:")
        for i in issues:
            print(f"  - {i}")
    return 0


def cmd_run(args):
    study = load_config(args.benchmark)
    mode = "live" if args.live else ("dry-run" if args.dry_run else "replay")
    if mode == "live":
        reg = Registry()
        issues = preflight(study, reg)
        blocking = [i for i in issues if "no credential" in i]
        if blocking and not args.force:
            print(bad("pre-flight failed:"))
            for i in blocking:
                print(f"  - {i}")
            print("  Set the credentials, or pass --force to run the models that are reachable.")
            return 2
        for i in issues:
            print(f"  note: {i}")

    print(f"\nRunning study '{study.get('study_id')}' in {mode} mode\n")
    result: RunResult = run_study(study, mode=mode, run_dir=args.run_dir,
                                  include_retired=args.include_retired,
                                  record=args.record, max_trials=args.max_trials)

    print(f"\n  run dir           {result.run_dir}")
    print(f"  trials planned    {result.trials_planned}")
    print(f"  trials executed   {result.trials_executed}")
    if result.estimated_cost_usd:
        print(f"  cold cost         ${result.estimated_cost_usd:,.4f}")
    if result.dispositions:
        print("  dispositions      " + ", ".join(f"{k}={v}" for k, v in
                                                 sorted(result.dispositions.items())))
    if result.fairness_failures:
        print(f"\n  {bad(f'{len(result.fairness_failures)} fairness failure(s)')} — these trials "
              f"were not run. A study that fails the fairness contract produces no information.")
        for f in result.fairness_failures[:10]:
            print(f"      - {f}")
    if result.prompt_parity_notes:
        print(f"\n  {warn(f'{len(result.prompt_parity_notes)} prompt-parity note(s)')} — prompt "
              f"content that appears for one task and no other, outside the IR. Not a failure: a "
              f"one-off conditional block looks the same from here as a leaked hint. Read the "
              f"rendered prompt before drawing a conclusion.")
        for n in result.prompt_parity_notes[:10]:
            print(f"      - {n}")
    print(f"\n  next: python3 mb.py report --run-dir {result.run_dir}")
    return 0


def cmd_report(args):
    rd = Path(args.run_dir) if args.run_dir else find_latest_run()
    if rd is None:
        print(bad("no run directory found. Run `mb.py run --replay` first."))
        return 2
    store = RunStore(rd)
    grades = list(store.iter_grades())
    manifests = list(store.iter_manifests())
    if not grades:
        print(bad(f"no grades in {rd}"))
        return 2

    report = build_report(grades, manifests, store.read_study())

    comp = report.get("comparability", {})
    if not comp.get("comparable_within_round") and not args.allow_incompatible:
        print(bad("refusing to render a comparison across incompatible versions."))
        print(f"  {comp.get('reason')}")
        print("  Run a backfill, or pass --allow-incompatible to render it labelled as such.")
        return 2

    if args.format == "json":
        p = store.write_report("report.json", json.dumps(report, indent=2, default=str))
        print(f"wrote {p}")
    else:
        md = render_markdown(report)
        p = store.write_report("report.md", md)
        store.write_report("report.json", json.dumps(report, indent=2, default=str))
        print(md if args.stdout else f"wrote {p}\nwrote {p.parent / 'report.json'}")
    return 0


def cmd_grade(args):
    """Re-grade stored responses without re-invoking providers.

    This is what makes a scoring change cheap to evaluate: change the matcher,
    re-grade, diff the report. No spend, no provider variance.
    """
    rd = Path(args.run_dir) if args.run_dir else find_latest_run()
    if rd is None:
        print(bad("no run directory found."))
        return 2
    store = RunStore(rd)
    study = store.read_study()
    print(f"Re-grading {rd} against scoring v{SCORING_VERSION} / matcher v{MATCHER_VERSION}")
    print(dim("  Note: re-grading with a changed scoring or matcher version means this run is no "
              "longer comparable to rounds graded with the old one until they are backfilled too."))
    # Regrading from transcripts requires replaying normalization; the simplest
    # correct path is to re-run in replay mode against the same cassettes.
    print("\n  Run: python3 mb.py run --benchmark <study> --replay --run-dir <new-dir>")
    print("  then compare the two reports. Grades are derived, never edited in place.")
    return 0


def cmd_score(args):
    return cmd_report(args)


def cmd_route(args):
    rd = Path(args.run_dir) if args.run_dir else find_latest_run()
    if rd is None:
        print(bad("no run directory found."))
        return 2
    store = RunStore(rd)
    report = build_report(list(store.iter_grades()), list(store.iter_manifests()),
                          store.read_study())

    budgets = report.get("iso_cost_points", [0.05, 0.25, 1.00])
    iso = {r["model"]: r for r in report.get("iso_budget_table", [])}

    def best_at(b: float) -> str | None:
        candidates = [(m, r.get(f"${b:g}/task")) for m, r in iso.items()]
        candidates = [(m, q) for m, q in candidates if isinstance(q, (int, float))]
        return max(candidates, key=lambda x: x[1])[0] if candidates else None

    policy = {
        "routing_policy_version": "1.0.0",
        "derived_from_run": str(rd),
        "derived_from_study": report.get("study_id"),
        "caveats": [
            "Derived from measured frontiers at declared spend points, not from effort labels.",
            "Escalation thresholds assume the recalibration map published with this round.",
            "Re-derive whenever scoring, matcher, resolver or the response schema changes.",
        ],
        "rules": [],
    }
    for b in budgets:
        m = best_at(b)
        if not m:
            continue
        model_data = report["models"].get(m, {})
        policy["rules"].append({
            "budget_usd_per_task": b,
            "primary": m,
            "measured_quality": iso[m].get(f"${b:g}/task"),
            "pass_hat_3": model_data.get("pass_hat_3"),
            "abstention_precision": (model_data.get("abstention") or {}).get("abstention_precision"),
            "escalate_when": "calibrated confidence below 0.55, or an abstention on a "
                             "decision-critical item",
            "abstain_route": "human_review",
        })

    p = store.write_report("routing-policy.json", json.dumps(policy, indent=2, default=str))
    print(json.dumps(policy, indent=2, default=str))
    print(f"\nwrote {p}")
    return 0


def cmd_test(args):
    """Replay the bundled fixtures end to end.

    Run this after ANY change to normalization, resolution, matching, scoring or
    statistics. Those are the parts most likely to carry a subtle bug and the
    parts you least want to debug by spending money on eleven providers.
    """
    study_path = HERE.parent / "config" / "benchmark.example.yaml"
    study = load_config(str(study_path))
    study["trials"] = 1
    study["effort"] = {"policy": "fixed_default"}
    study["models"] = args.models.split(",") if args.models else study["models"]

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        print("Replaying bundled cassettes through the full pipeline…\n")
        result = run_study(study, mode="replay", run_dir=tmp, verbose=True)
        store = RunStore(tmp)
        grades = list(store.iter_grades())
        manifests = list(store.iter_manifests())
        if not grades:
            print(bad("\nno grades produced — check fixtures/cassettes/"))
            return 1
        report = build_report(grades, manifests, study)
        print("\n" + render_markdown(report))
        print(f"\n{ok('pipeline OK')} — {result.trials_executed} trials, "
              f"{len(report['models'])} models, "
              f"{len(report.get('paired_comparisons', []))} paired comparisons")
    return 0


def _synthetic_study(args) -> dict:
    """A minimal study for `compile` without a benchmark file."""
    return {
        "study_id": "adhoc-compile",
        "lanes": ["optimized"],
        "trials": 1,
        "models": [args.model] if args.model else Registry().ids(),
        "evidence": {"provider": "local_graph",
                     "corpus": {"repository": "fixtures/sample-repo", "commit": "fixture"}},
        "grading": {"f_beta": {}},
    }


# ==========================================================================

def main(argv=None):
    p = argparse.ArgumentParser(prog="mb", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="environment, registry, pricing, credential check")
    d.add_argument("--check-configs", action="store_true",
                   help="scan config files for credential-shaped values")
    d.set_defaults(fn=cmd_doctor)

    m = sub.add_parser("models", help="inspect the model registry")
    m.add_argument("action", choices=["list", "show"])
    m.add_argument("model_id", nargs="?")
    m.set_defaults(fn=cmd_models)

    c = sub.add_parser("compile", help="compile + fairness-validate; no provider calls")
    c.add_argument("--suite", required=True)
    c.add_argument("--task")
    c.add_argument("--model")
    c.add_argument("--all-models", action="store_true",
                   help="compile for every enabled model (the default when --model is omitted)")
    c.add_argument("--benchmark")
    c.add_argument("--dry-run", action="store_true", help="(default; no calls are ever made here)")
    c.add_argument("--include-retired", action="store_true")
    c.add_argument("--show", help="print the rendered prompt for a model id, or 'all'")
    c.add_argument("--out", help="write compiled artifacts to this directory")
    c.set_defaults(fn=cmd_compile)

    pl = sub.add_parser("plan", help="expand the trial matrix and estimate cost")
    pl.add_argument("--benchmark", required=True)
    pl.add_argument("--estimate", action="store_true")
    pl.add_argument("--est-input", default=40000)
    pl.add_argument("--est-output", default=6000)
    pl.add_argument("--include-retired", action="store_true")
    pl.set_defaults(fn=cmd_plan)

    r = sub.add_parser("run", help="execute a study")
    r.add_argument("--benchmark", required=True)
    g = r.add_mutually_exclusive_group()
    g.add_argument("--live", action="store_true", help="real provider calls")
    g.add_argument("--replay", action="store_true", help="recorded cassettes (default)")
    g.add_argument("--dry-run", action="store_true", help="compile and validate only")
    r.add_argument("--run-dir")
    r.add_argument("--record", action="store_true", help="record cassettes during a live run")
    r.add_argument("--include-retired", action="store_true")
    r.add_argument("--max-trials", type=int)
    r.add_argument("--force", action="store_true", help="proceed despite pre-flight issues")
    r.set_defaults(fn=cmd_run)

    gr = sub.add_parser("grade", help="re-grade stored responses")
    gr.add_argument("--run-dir")
    gr.set_defaults(fn=cmd_grade)

    sc = sub.add_parser("score", help="aggregate scores and statistics")
    sc.add_argument("--run-dir")
    sc.add_argument("--format", default="json", choices=["md", "json"])
    sc.add_argument("--stdout", action="store_true")
    sc.add_argument("--allow-incompatible", action="store_true")
    sc.set_defaults(fn=cmd_score)

    rp = sub.add_parser("report", help="render the report")
    rp.add_argument("--run-dir")
    rp.add_argument("--format", default="md", choices=["md", "json"])
    rp.add_argument("--stdout", action="store_true")
    rp.add_argument("--allow-incompatible", action="store_true",
                    help="render a cross-version comparison, labelled as incomparable")
    rp.set_defaults(fn=cmd_report)

    ro = sub.add_parser("route", help="emit a routing policy from measured frontiers")
    ro.add_argument("--run-dir")
    ro.set_defaults(fn=cmd_route)

    t = sub.add_parser("test", help="replay bundled fixtures end to end")
    t.add_argument("--models", help="comma-separated subset")
    t.set_defaults(fn=cmd_test)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

"""Orchestration: expand a study into trials, compile, validate, invoke, grade.

The order of operations is the whole point:

    compile  →  FAIRNESS VALIDATE  →  invoke  →  disposition  →  normalize
             →  resolve  →  verify  →  match  →  score

Validation happens before invocation so a study that was never a valid
comparison costs nothing to discover. Disposition happens before normalization
so a safety refusal never reaches the scorer as an empty finding set.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import (
    HARNESS_VERSION,
    MATCHER_VERSION,
    RESOLVER_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SCORING_VERSION,
)
from .adapters import get_adapter
from .adapters.base import RunProfile
from .adapters.replay import DryRunTransport, Recorder, ReplayTransport
from .disposition import RETRY_POLICY, Disposition, DispositionResult, classify
from .evidence.base import get_provider
from .fairness import check_group, residual_lines, validate
from .ir import Lanes, build_ir
from .match import match_findings
from .normalize import normalize
from .pricing import PricingOracle, Usage
from .registry import Registry
from .resolve import resolve_response, verify_claims, verify_oracle_relations
from .score import calibration, score_abstention, score_trial
from .secrets import MissingCredential, key_present
from .store import RunStore, new_run_id
from .util import SKILL_ROOT, load_config


@dataclass
class Trial:
    model_id: str
    task: dict[str, Any]
    suite: str
    suite_version: str
    lane: str
    trial_number: int
    trials_total: int
    profile: RunProfile
    beta: float = 1.0


@dataclass
class RunResult:
    run_dir: Path
    trials_planned: int = 0
    trials_executed: int = 0
    fairness_failures: list[str] = field(default_factory=list)
    dispositions: dict[str, int] = field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    prompt_parity_notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Planning
# --------------------------------------------------------------------------

def load_suite(path: str) -> dict[str, Any]:
    data = load_config(path)
    if "tasks" not in data:
        raise ValueError(f"suite {path} has no `tasks` list")
    return data


def expand_trials(study: dict[str, Any], registry: Registry,
                  include_retired: bool = False) -> list[Trial]:
    trials: list[Trial] = []
    lanes = study.get("lanes", ["optimized"])
    n_trials = int(study.get("trials", 5))
    effort_cfg = study.get("effort", {}) or {}
    policy = effort_cfg.get("policy", "fixed_default")
    extra_axes = effort_cfg.get("extra_axes", {})
    betas = (study.get("grading", {}) or {}).get("f_beta", {})

    for suite_ref in study.get("suites", []):
        suite = load_suite(suite_ref["path"])
        wanted = suite_ref.get("tasks", "all")
        tasks = suite["tasks"]
        if wanted != "all":
            wanted_ids = set(wanted)
            tasks = [t for t in tasks if t["id"] in wanted_ids]
        beta = float(betas.get(suite.get("suite", ""), 1.0))

        for model_id in study.get("models", []):
            model = registry.get(model_id)
            if not model.enabled and not include_retired:
                continue
            if policy == "sweep":
                points = registry.sweep_points(model_id, extra_axes)
            elif policy == "fixed":
                points = [{"effort": effort_cfg.get("value")}]
            else:
                points = [{"effort": model.effort_default}]

            for lane in lanes:
                for task in tasks:
                    for point in points:
                        for t in range(1, n_trials + 1):
                            trials.append(Trial(
                                model_id=model_id, task=task,
                                suite=suite.get("suite", "unknown"),
                                suite_version=suite.get("version", "0.0.0"),
                                lane=lane, trial_number=t, trials_total=n_trials,
                                profile=RunProfile(
                                    effort=point.get("effort"),
                                    reasoning_mode=point.get("reasoning_mode"),
                                    verbosity=study.get("verbosity"),
                                ),
                                beta=beta,
                            ))
    return trials


# --------------------------------------------------------------------------
# Compilation + fairness
# --------------------------------------------------------------------------

OFFLINE_PLACEHOLDER = "offline-mode-no-credential-required"


def _placeholder_credentials() -> None:
    """Satisfy the adapters' header construction in --dry-run and --replay.

    Deliberately a recognizable non-secret so that if it ever appeared in an
    artifact it would be obvious, rather than looking like a real key.
    """
    import os
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
        os.environ.setdefault(name, OFFLINE_PLACEHOLDER)


def compile_trial(trial: Trial, registry: Registry, lanes: Lanes,
                  study: dict[str, Any], evidence_version: dict[str, Any]):
    model = registry.get(trial.model_id)
    adapter = get_adapter(model.adapter)

    ev_cfg = study.get("evidence", {}) or {}
    ir = build_ir(
        trial.task,
        suite=trial.suite,
        suite_version=trial.suite_version,
        corpus=(ev_cfg.get("corpus") or {"repository": "unknown", "commit": "unknown"}),
        evidence_provider=evidence_version,
        budget_override=ev_cfg.get("budget"),
        trials=trial.trials_total,
        ordering_seed=int(study.get("ordering_seed", 0)),
        lanes=lanes,
    )
    req = adapter.compile(ir, model, trial.profile)
    verdict = validate(ir, req.rendered_prompt, req.body, trial.lane, adapter.id, lanes)
    return model, adapter, ir, req, verdict


def compile_all_models(task: dict[str, Any], suite: dict[str, Any], study: dict[str, Any],
                       registry: Registry, lanes: Lanes, models: list[str] | None = None,
                       include_retired: bool = False):
    """Compile one task for every model and check the group shares a digest.

    This is the cheapest possible place to discover that a comparison was never
    valid — it costs nothing and catches the most consequential class of bug.
    """
    ev_cfg = study.get("evidence", {}) or {}
    provider = get_provider(ev_cfg.get("provider", "local_graph"),
                            corpus_root=(ev_cfg.get("corpus") or {}).get("repository",
                                                                         "fixtures/sample-repo"))
    gv = provider.version()
    evidence_version = {"provider": gv.provider, "graph_version": gv.version,
                        "graph_hash": gv.graph_hash}

    ids = models or study.get("models") or registry.ids(include_disabled=include_retired)
    out = []
    digests: dict[str, str] = {}
    for mid in ids:
        m = registry.get(mid)
        if not m.enabled and not include_retired:
            continue
        trial = Trial(model_id=mid, task=task, suite=suite.get("suite", "?"),
                      suite_version=suite.get("version", "0.0.0"),
                      lane=(study.get("lanes") or ["optimized"])[0],
                      trial_number=1, trials_total=1,
                      profile=RunProfile(effort=m.effort_default))
        try:
            model, adapter, ir, req, verdict = compile_trial(trial, registry, lanes, study,
                                                             evidence_version)
        except MissingCredential:
            # Rendering never needs a key; only the header does. `compile` is an
            # offline command, so a placeholder keeps it working with no
            # credentials configured at all.
            _placeholder_credentials()
            model, adapter, ir, req, verdict = compile_trial(trial, registry, lanes, study,
                                                             evidence_version)
        digests[mid] = verdict.semantic_digest
        out.append({"model": mid, "adapter": f"{adapter.id}/{adapter.version}",
                    "verdict": verdict, "request": req, "ir": ir})
    group_ok, group_msg = check_group(digests)
    return out, group_ok, group_msg


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------

def run_study(study: dict[str, Any], mode: str = "replay", run_dir: str | None = None,
              include_retired: bool = False, record: bool = False,
              max_trials: int | None = None, verbose: bool = True) -> RunResult:
    if mode != "live":
        # Offline modes must work with no credentials at all — that is most of
        # the point of having them. The placeholder only ever reaches a header
        # that is never sent.
        _placeholder_credentials()

    registry = Registry()
    lanes = Lanes()
    pricing = PricingOracle()

    ev_cfg = study.get("evidence", {}) or {}
    provider = get_provider(ev_cfg.get("provider", "local_graph"),
                            corpus_root=(ev_cfg.get("corpus") or {}).get("repository",
                                                                         "fixtures/sample-repo"))
    gv = provider.version()
    evidence_version = {"provider": gv.provider, "graph_version": gv.version,
                        "graph_hash": gv.graph_hash}

    rd = Path(run_dir or (study.get("reporting", {}).get("out_dir", "runs")))
    if run_dir is None:
        rd = rd / new_run_id(study.get("study_id", "run")[:24])
    store = RunStore(rd)
    store.write_study(study)

    trials = expand_trials(study, registry, include_retired)
    if max_trials:
        trials = trials[:max_trials]
    result = RunResult(run_dir=rd, trials_planned=len(trials))

    transport = {"dry-run": DryRunTransport(), "replay": ReplayTransport()}.get(mode)
    recorder = Recorder() if record else None
    guards = study.get("guards", {}) or {}
    spend = 0.0
    max_spend = float(guards.get("max_total_spend_usd", 1e9))

    group_digest: dict[tuple, str] = {}
    residual_lines_by_task: dict[tuple, dict[str, set]] = {}

    for tr in trials:
        try:
            model, adapter, ir, req, verdict = compile_trial(tr, registry, lanes, study,
                                                             evidence_version)
        except MissingCredential as e:
            store.log("credential_missing", model=tr.model_id, detail=str(e))
            result.dispositions["HARNESS_ERROR"] = result.dispositions.get("HARNESS_ERROR", 0) + 1
            continue

        # Every model on the same (task, lane) must share one semantic digest.
        key = (tr.task["id"], tr.lane)
        if key not in group_digest:
            group_digest[key] = verdict.semantic_digest
        elif group_digest[key] != verdict.semantic_digest:
            verdict.violations.append(
                f"semantic_digest differs from the first model compiled for {tr.task['id']}/{tr.lane}"
            )
            verdict.verdict = "FAIL"

        # Collect the adapter's residual (non-IR) prompt lines per task, keyed per
        # MODEL — an adapter may legitimately render differently for different
        # models in its family. A line that appears for exactly one task is
        # content that entered from outside the IR; it is surfaced for review at
        # the end of the run rather than failed, because adapters also emit
        # legitimate conditional blocks (a questions header only when the IR
        # carries questions) and failing on those would fail honest adapters.
        rkey = (model.id, tr.lane)
        residual_lines_by_task.setdefault(rkey, {}).setdefault(tr.task["id"], set()).update(
            residual_lines(ir, req.rendered_prompt))

        if not verdict.ok:
            result.fairness_failures.append(f"{tr.model_id}/{tr.task['id']}: " +
                                            "; ".join(verdict.violations))
            store.log("fairness_fail", model=tr.model_id, task=tr.task["id"],
                      violations=verdict.violations)
            if guards.get("require_fairness_pass", True):
                continue

        # ---- invoke ------------------------------------------------------
        resp, retries = _invoke_with_retry(adapter, req, transport, tr, mode)

        provider.reset_counter()
        text = adapter.extract_text(resp) if resp.status else ""
        norm = normalize(text)
        if mode == "dry-run":
            # Dry-run compiles and validates; it does not measure. Passing its
            # synthetic response through classify() dispositioned it as
            # PROVIDER_ERROR, which is a claim about a provider that was never
            # called.
            disp = DispositionResult(Disposition.DRY_RUN, "compiled and validated; not invoked",
                                     scored=False, retryable=False)
        else:
            # Pass schema validity even when the body is empty. Gating on `text`
            # meant an empty HTTP 200 skipped the SCHEMA_INVALID branch and was
            # dispositioned OK, then scored as an empty finding set — recall zero
            # for a response that never arrived.
            disp = classify(adapter, resp, schema_valid=norm.schema_valid)

        usage = adapter.usage(resp) if resp.status == 200 else Usage()
        try:
            cost = pricing.cost(tr.model_id, usage, cache_state="cold")
        except KeyError:
            cost = None
        if cost and cost.usd == cost.usd:      # not NaN
            spend += cost.usd
        cap_reached = spend > max_spend

        transcript_ref = store.write_transcript({
            "task": tr.task["id"], "trial": tr.trial_number,
            "rendered_prompt": req.rendered_prompt,
            "response_text": text,
            "repairs": norm.repairs, "schema_errors": norm.errors,
        })

        manifest = _manifest(tr, model, adapter, ir, req, verdict, resp, usage, cost,
                             disp, retries, evidence_version, mode, norm, transcript_ref,
                             study, pricing)
        store.append_manifest(manifest)
        result.trials_executed += 1
        result.dispositions[disp.disposition.value] = \
            result.dispositions.get(disp.disposition.value, 0) + 1

        if recorder and mode == "live":
            recorder.record(req, resp, tr.task["id"], tr.trial_number)

        # ---- grade -------------------------------------------------------
        grade = grade_trial(tr, model, norm, disp, provider, cost, study)
        store.append_grade(grade)

        if verbose:
            q = (grade.get("scores") or {}).get("quality_index")
            cfg = tr.profile.effort or "default"
            print(f"  {tr.model_id:<20} {tr.task['id']:<12} {cfg:<8} t{tr.trial_number} "
                  f"{disp.disposition.value:<16} "
                  f"{'q=' + format(q, '.1f') if q is not None else ''}")

        # Checked AFTER the artifacts are written: the call was billed, so its
        # record belongs in the run even though the run stops here.
        if cap_reached:
            store.log("spend_cap", spent=spend, cap=max_spend)
            if verbose:
                print(f"  spend cap reached (${spend:.2f} > ${max_spend:.2f}) — stopping")
            break

    result.estimated_cost_usd = round(spend, 4)
    result.prompt_parity_notes = _residual_review(residual_lines_by_task)
    for note in result.prompt_parity_notes:
        store.log("prompt_parity_review", note=note)
    return result


def _residual_review(by_model: dict[tuple, dict[str, set]]) -> list[str]:
    """Residual prompt lines that appear for exactly one task.

    Not a violation — a review queue. The honest reading is "look at this", not
    "this is wrong": a one-off conditional block looks identical to a leaked hint
    from here, and only a human reading the rendered prompt can tell them apart.
    """
    notes: list[str] = []
    for (model_id, lane), per_task in sorted(by_model.items()):
        if len(per_task) < 2:
            continue
        counts: dict[str, int] = {}
        for lines in per_task.values():
            for ln in lines:
                counts[ln] = counts.get(ln, 0) + 1
        for task_id, lines in sorted(per_task.items()):
            unique = sorted(ln for ln in lines if counts[ln] == 1)
            if unique:
                sample = "; ".join(u[:90] for u in unique[:3])
                notes.append(
                    f"{model_id} [{lane}] {task_id}: {len(unique)} prompt line(s) appear for this "
                    f"task and no other, outside the IR — review: {sample}"
                )
    return notes


def _invoke_with_retry(adapter, req, transport, tr: Trial, mode: str):
    retries = 0
    if transport is not None:
        if isinstance(transport, ReplayTransport):
            return transport.invoke(req, task_id=tr.task["id"], trial=tr.trial_number), 0
        return transport.invoke(req), 0

    resp = adapter.invoke(req)
    disp = classify(adapter, resp)

    # Per-disposition attempt counters. A single counter with a policy fetched
    # once meant a RATE_LIMITED -> TRUNCATED sequence kept the rate-limit backoff
    # and never raised the ceiling, while TIMEOUT -> RATE_LIMITED stopped after
    # one attempt.
    attempts: dict[Disposition, int] = {}
    while disp.retryable:
        policy = RETRY_POLICY.get(disp.disposition)
        if not policy:
            break
        used = attempts.get(disp.disposition, 0)
        if used >= policy["max_retries"]:
            break
        backoff = policy["backoff_s"][min(used, len(policy["backoff_s"]) - 1)]
        if backoff:
            time.sleep(backoff)
        attempts[disp.disposition] = used + 1
        retries += 1

        if policy.get("raise_output_ceiling"):
            # Clamp to the IR budget. Growing the ceiling past it would edit the
            # request AFTER the fairness validator ran, silently escaping the one
            # invariant the validator enforces at the request level.
            for k in ("max_tokens", "max_output_tokens"):
                if k in req.body:
                    req.body[k] = min(int(req.body[k] * 1.5), req.max_output_ceiling)
            gc = req.body.get("generationConfig")
            if isinstance(gc, dict) and "maxOutputTokens" in gc:
                gc["maxOutputTokens"] = min(int(gc["maxOutputTokens"] * 1.5),
                                            req.max_output_ceiling)

        resp = adapter.invoke(req)
        disp = classify(adapter, resp)
    return resp, retries


def trial_run_id(tr: Trial) -> str:
    """Unique per (model, task, config point, trial).

    Omitting the sweep point collided every effort rung of the same trial onto one
    id, and the report's manifest join key then handed one rung's latency to
    another rung's frontier point.
    """
    cfg = tr.profile.effort or "default"
    if tr.profile.reasoning_mode:
        cfg += f"+{tr.profile.reasoning_mode}"
    return f"{tr.model_id}:{tr.task['id']}:{cfg}:t{tr.trial_number}"


def _manifest(tr, model, adapter, ir, req, verdict, resp, usage, cost, disp, retries,
              evidence_version, mode, norm, transcript_ref, study, pricing) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "run_id": trial_run_id(tr),
        "study_id": study.get("study_id"),
        "lane": tr.lane,
        "mode": mode,
        "benchmark": {"suite": tr.suite, "suite_version": tr.suite_version,
                      "task": tr.task["id"], "task_version": tr.task.get("version")},
        "corpus": ir.corpus,
        "evidence": evidence_version,
        "model": {
            "provider": model.provider, "model_id": model.id,
            "resolved_model_version": adapter.resolved_model_version(resp),
            "endpoint": req.url,
            "derived_profile": model.derived,
            "retention_posture": model.retention_posture,
            "status": model.status,
        },
        "prompt": {
            "canonical_ir_version": ir.ir_version,
            "canonical_ir_hash": ir.ir_hash(),
            "semantic_digest": verdict.semantic_digest,
            "adapter": {"id": adapter.id, "version": adapter.version},
            "rendered_prompt_hash": req.rendered_prompt_hash(),
            "fairness_verdict": verdict.verdict,
            "fairness_violations": verdict.violations,
            "residual_digest": verdict.residual_digest,
        },
        "runtime": {
            "effort": tr.profile.effort,
            "effort_param": model.effort_param,
            "reasoning_mode": tr.profile.reasoning_mode,
            "max_output_tokens": req.body.get("max_tokens") or req.body.get("max_output_tokens"),
            "sampling": "not-applicable",
            "structured_output_mechanism": req.structured_output_mechanism,
            "budget": ir.budget,
        },
        "trial": {"number": tr.trial_number, "of": tr.trials_total},
        "usage": {
            "input_tokens_uncached": usage.input_tokens_uncached,
            "input_tokens_cached": usage.input_tokens_cached,
            "cache_write_tokens": usage.cache_write_tokens,
            "reasoning_tokens": usage.reasoning_tokens,
            "output_tokens": usage.output_tokens,
            "billed_cost_usd": cost.usd if cost else None,
            "pricing_table_version": pricing.version,
            "cost_flags": cost.flags if cost else [],
            "cache_state": "cold",
        },
        "timing": {"ttft_ms": resp.ttft_ms, "wall_clock_ms": resp.wall_clock_ms},
        "disposition": disp.disposition.value,
        "retries": retries,
        "result": {
            "artifact_hash": transcript_ref,
            "schema_valid": norm.schema_valid,
            "first_pass_schema_valid": norm.first_pass_valid,
            "transcript_ref": transcript_ref,
        },
        "versions": {
            "harness": HARNESS_VERSION, "scoring": SCORING_VERSION,
            "matcher": MATCHER_VERSION, "resolver": RESOLVER_VERSION,
            "response_schema": RESPONSE_SCHEMA_VERSION,
            "pricing_table": pricing.version,
        },
    }


# --------------------------------------------------------------------------
# Grading
# --------------------------------------------------------------------------

def grade_trial(tr: Trial, model, norm, disp, provider, cost, study) -> dict[str, Any]:
    oracle = tr.task.get("oracle", {}) or {}
    oracle_findings = oracle.get("findings", []) or []
    questions = (tr.task.get("prompt", {}) or {}).get("questions", []) or []

    base = {
        "grade_version": "1.0.0",
        "run_id": trial_run_id(tr),
        "task_id": tr.task["id"],
        "model_id": tr.model_id,
        "lane": tr.lane,
        "trial": tr.trial_number,
        "effort": tr.profile.effort,
        "reasoning_mode": tr.profile.reasoning_mode,
        **disp.to_dict(),
    }

    if not disp.scored:
        # Excluded from quality scoring — but reported. Nothing here is scored as
        # zero, because a refusal is a statement about the provider, not the model's
        # ability to find bugs.
        base["scores"] = None
        base["economics"] = _econ(cost, 0.0)
        return base

    findings = norm.findings
    answers = norm.answers
    res = resolve_response(findings, provider, answers=answers)
    claims = verify_claims(findings, provider, source="EMITTED", answers=answers)

    matching = match_findings(
        findings, oracle_findings,
        resolutions=res.per_finding,
        tolerance=int(((study.get("grading") or {}).get("matching") or {})
                      .get("location_tolerance_lines", 0)),
    )

    sem = None
    if oracle.get("relations"):
        sem = verify_oracle_relations(answers, oracle["relations"], provider)

    scores = score_trial(matching, res, claims, findings, oracle_findings, beta=tr.beta,
                         semantic_relations=sem)

    conf_pairs: list[tuple[float, bool]] = []
    credited = {a.finding_id for a in matching.assignments
                if a.tier in ("full", "located", "adjacent")}
    for f in findings:
        c = f.get("confidence")
        if isinstance(c, (int, float)):
            conf_pairs.append((float(c), f.get("id") in credited))
    cal = calibration(conf_pairs, bins=int(((study.get("grading") or {})
                                            .get("calibration") or {}).get("bins", 10)))

    ab = score_abstention(norm.data, oracle, questions)

    base.update({
        "matching": {
            "assignments": [a.__dict__ for a in matching.assignments],
            "true_positive_credit": matching.true_positive_credit,
            "false_positive_count": matching.false_positive_cost,
            "unverifiable_count": matching.unverifiable,
            "oracle_total": matching.oracle_total,
        },
        "resolution": res.to_dict(),
        "claims": claims.to_dict(),
        "scores": scores.to_dict(),
        "calibration": cal.to_dict(),
        "abstention": ab.to_dict(),
        "semantic_relations": sem,
        "budget_use": {"graph_queries": provider.query_count(),
                       "exceeded": disp.disposition is Disposition.BUDGET_EXCEEDED},
        "economics": _econ(cost, matching.true_positive_credit),
        "schema": {"first_pass_valid": norm.first_pass_valid,
                   "repairs": norm.repairs, "errors": norm.errors},
    })
    return base


def _econ(cost, credited_tp: float) -> dict[str, Any]:
    if cost is None:
        return {"cold_cost_usd": None, "cost_per_correct_finding": None, "flags": []}
    from .pricing import cost_per_correct_finding
    return {
        "cold_cost_usd": cost.usd,
        "warm_cost_usd": None,
        "cost_per_correct_finding": cost_per_correct_finding(cost.usd, credited_tp),
        "pricing_table_version": cost.pricing_table_version,
        "imputed_pricing": "imputed" in cost.flags,
        "promotional_pricing": "promotional" in cost.flags,
        "flags": cost.flags,
    }


def preflight(study: dict[str, Any], registry: Registry) -> list[str]:
    """Checks worth doing before a live run.

    All of these are cheap, and each one has cost somebody a whole benchmark
    round at some point.
    """
    issues: list[str] = []
    for mid in study.get("models", []):
        try:
            m = registry.get(mid)
        except KeyError as e:
            issues.append(str(e))
            continue
        if not key_present(m.provider):
            issues.append(f"{mid}: no credential visible for provider '{m.provider}'")
        if m.status == "retired":
            issues.append(f"{mid}: retired model — expect PROVIDER_ERROR; pass --include-retired "
                          f"to run it anyway")
        if m.derived:
            issues.append(f"{mid}: DERIVED adapter profile (no upstream template). Results are "
                          f"footnoted; validate against vendor docs before relying on them.")
        if m.retention_posture == "mandatory-30d":
            issues.append(f"{mid}: mandatory 30-day retention, no zero-data-retention option. "
                          f"Confirm the corpus may be sent — see references/security.md.")
    pricing = PricingOracle()
    if pricing.is_stale():
        issues.append(f"pricing table verified {pricing.staleness_days()} days ago "
                      f"(> {pricing.staleness_warn_days}); re-verify before quoting costs")
    if (study.get("tribunal") or {}).get("enabled"):
        issues.append("tribunal is enabled — confirm the human calibration set exists and its "
                      "inter-rater reliability has been measured (skills/judge-tribunal/)")
    return issues

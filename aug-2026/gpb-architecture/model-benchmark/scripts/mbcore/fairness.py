"""The fairness validator.

Runs between `Adapter.compile()` and `Adapter.invoke()`. A failing verdict stops
the run before a token is billed, because a study that fails the fairness
contract has produced no information regardless of what it cost.

Three checks, in increasing order of how often they catch something real:

1. **Semantic digest agreement** — every model in a comparison group must share
   one `semantic_digest`. This catches an adapter that edited the objective, the
   success criteria, the budget, the schema, or a tool's parameter set.

2. **Prohibited constructs** — the rendered prompt is scanned for the patterns
   in config/lanes.yaml. Each prohibition exists because the construct has a
   measured effect on at least one current model generation, so introducing it
   for one family and not another turns a prompt artifact into an apparent
   capability difference.

3. **Requirement coverage** — every success criterion and required output field
   must survive into the rendered prompt in recognizable form. This catches the
   opposite failure: an adapter that "leaned out" the prompt so aggressively
   that it dropped a requirement.

None of this is a proof. It is a lint that turns an unfalsifiable claim into a
reviewable artifact, which is the most an automated check can honestly do here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .ir import Lanes, PromptIR
from .util import text_digest


@dataclass
class Verdict:
    verdict: str                      # "PASS" | "FAIL"
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    semantic_digest: str = ""
    residual_digest: str = ""         # see `residual_digest()` below

    @property
    def ok(self) -> bool:
        return self.verdict == "PASS"


_WORD = re.compile(r"[a-z0-9]+")


def _keywords(text: str, top: int | None = 8) -> list[str]:
    """Content words from a requirement, used for coverage checking.

    Deliberately crude: the goal is to catch a DROPPED requirement, not to police
    paraphrase. An adapter is allowed to rephrase; it is not allowed to delete.
    """
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "into", "must", "not",
        "all", "any", "are", "its", "you", "your", "each", "every", "which", "when",
        "what", "have", "has", "was", "were", "will", "shall", "should", "than",
        "then", "there", "their", "them", "they", "it", "in", "of", "to", "a", "an",
        "on", "at", "by", "or", "is", "as", "be", "do", "if", "so", "we", "our",
    }
    words = [w for w in _WORD.findall(text.lower()) if len(w) > 2 and w not in stop]
    seen: list[str] = []
    for w in words:
        if w not in seen:
            seen.append(w)
    return seen if top is None else seen[:top]


def _distinctive(target: str, others: list[str]) -> list[str]:
    """Keywords of `target` that appear in none of `others`.

    Success criteria share vocabulary with the objective, the scope and each
    other, so "at least 2 of this criterion's words are present" was satisfied by
    a prompt containing none of them: the shared words alone cleared the bar, and
    the coverage check never fired on any real omission. Only words unique to a
    criterion are evidence that THAT criterion survived.
    """
    other_words = set()
    for o in others:
        other_words |= set(_keywords(o, top=None))
    return [w for w in _keywords(target, top=None) if w not in other_words]


def residual_lines(ir: PromptIR, rendered: str) -> set[str]:
    """The rendered prompt with all IR-derived text removed.

    What remains is the adapter's own boilerplate and structure. That is a
    property of the ADAPTER, so a line appearing for one task and no other is a
    signal that task-specific content entered the prompt from outside the IR —
    the prompt-parity leak the semantic digest cannot see, because it hashes the
    IR rather than what was sent.

    This is REPORTED, not enforced. Adapters legitimately emit conditional
    blocks — a questions header only when the IR carries questions — so equality
    across tasks is the wrong bar and would fail honest adapters. The run
    surfaces task-unique residual lines for review instead.

    Two limits worth stating plainly. A CONSTANT hint appended to every task
    passes, because it is indistinguishable from boilerplate by this method. And
    a leak phrased in words the IR already uses is stripped along with the IR
    text. No automated check on a single rendering can do better; the backstop is
    reading one rendered prompt per adapter version by hand.
    """
    text = rendered
    chunks: list[str] = [ir.objective, ir.scope]
    chunks += list(ir.success_criteria)
    ctx = ir.context or {}
    chunks += [str(v) for v in ctx.values() if isinstance(v, str)]
    for v in ctx.values():
        if isinstance(v, list):
            chunks += [str(x) for x in v]
    for r in ir.reference_material:
        chunks += [str(r.get("label", "")), str(r.get("inline") or ""), str(r.get("path") or "")]
    for q in ir.questions:
        chunks += [str(q.get("id", "")), str(q.get("text", ""))]
    for t in ir.tools:
        chunks += [str(t.get("name", "")), str(t.get("description", "")),
                   str(t.get("when_to_use") or "")]
    for role_val in (ir.role or {}).values():
        if isinstance(role_val, str):
            chunks.append(role_val)
    chunks.append(ir.task_id)
    for c in sorted(chunks, key=len, reverse=True):
        c = (c or "").strip()
        if len(c) > 3:
            text = text.replace(c, " ")
    # Hash the SET of residual line shapes, not their sequence or count.
    # Structural scaffolding repeats once per IR item — four success criteria
    # produce four numbered markers, three questions produce three bullets — so a
    # sequence hash flags every task with a different item count as a violation.
    # The set is stable across those and still changes the moment a genuinely new
    # line appears, which is what an injected hint is.
    lines = set()
    for line in text.splitlines():
        line = re.sub(r"\d+", "#", line)
        line = re.sub(r"\s+", " ", line).strip()
        line = line.strip("-*#.:;,()[]{}<>| ")
        if len(line) > 2:
            lines.add(line)
    return lines


def residual_digest(ir: PromptIR, rendered: str) -> str:
    """Stable hash of the residual line set. Recorded in every manifest."""
    return text_digest("\n".join(sorted(residual_lines(ir, rendered))))


def validate(
    ir: PromptIR,
    rendered_prompt: str,
    request_body: dict[str, Any],
    lane_id: str,
    adapter_id: str,
    lanes: Lanes | None = None,
    group_semantic_digest: str | None = None,
) -> Verdict:
    lanes = lanes or Lanes()
    lane = lanes.get(lane_id)
    violations: list[str] = []
    warnings: list[str] = []

    sem = ir.semantic_digest(lanes.semantic_fields)

    # ---- 1. semantic digest agreement -------------------------------------
    if group_semantic_digest and sem != group_semantic_digest:
        violations.append(
            f"semantic_digest mismatch: this trial {sem[:19]}… vs comparison group "
            f"{group_semantic_digest[:19]}…. The models are not answering the same question."
        )

    # ---- 2. prohibited constructs -----------------------------------------
    body_text = _stringify(request_body)
    lowered = rendered_prompt.lower()

    for pr in lanes.prohibitions:
        pid = pr["id"]
        if pid not in ir.prohibitions:
            continue
        if adapter_id in (pr.get("exempt_adapters") or []):
            warnings.append(
                f"prohibition '{pid}' waived for adapter '{adapter_id}' "
                f"(declared exemption in config/lanes.yaml)"
            )
            continue
        scope = pr.get("scope", "prompt")
        haystack = body_text.lower() if scope == "request_body" else lowered
        for pat in pr.get("patterns", []) or []:
            if re.search(pat, haystack):
                violations.append(
                    f"prohibited construct '{pid}' matched /{pat}/ in {scope}. {pr.get('why', '').strip()}"
                )
                break
        if pr.get("detector") == "structural" and pid == "added_examples":
            ir_examples = sum(1 for r in ir.reference_material if r.get("kind") in ("rubric", "mockup"))
            rendered_examples = len(re.findall(r"(?im)^\s*(input|example)\s*[:#]", rendered_prompt))
            if rendered_examples > ir_examples:
                violations.append(
                    f"prohibited construct 'added_examples': {rendered_examples} example blocks in the "
                    f"rendered prompt vs {ir_examples} in the IR. Few-shot examples move some families "
                    f"more than others; if the task needs them they belong in the IR."
                )

    # ---- 3. requirement coverage ------------------------------------------
    missing: list[str] = []
    for i, crit in enumerate(ir.success_criteria, 1):
        others = [ir.objective, ir.scope] + [c for j, c in enumerate(ir.success_criteria, 1) if j != i]
        kws = _distinctive(crit, others)
        if not kws:
            # Nothing unique to test against. Say so rather than passing silently:
            # a criterion indistinguishable from its neighbours is a suite-authoring
            # problem, and it is invisible to this check either way.
            warnings.append(
                f"success_criteria[{i}] shares all its vocabulary with the rest of the IR, so "
                f"its presence in the rendered prompt cannot be verified: '{crit[:60]}…'"
            )
            continue
        hits = sum(1 for k in kws if k in lowered)
        if hits < max(1, (len(kws) + 1) // 2):
            missing.append(
                f"success_criteria[{i}] ({hits}/{len(kws)} distinctive terms present): '{crit[:70]}…'"
            )
    if missing:
        violations.append(
            "requirement(s) missing from the rendered prompt — an adapter may rephrase but never drop: "
            + "; ".join(missing)
        )

    for fieldname in ir.response.get("required_fields", []):
        if fieldname.lower() not in lowered and fieldname.lower() not in body_text.lower():
            violations.append(
                f"required output field '{fieldname}' does not appear in the rendered prompt or the "
                f"structured-output schema attached to the request."
            )

    # objective must survive
    obj_kws = _keywords(ir.objective, top=10)
    if obj_kws and sum(1 for k in obj_kws if k in lowered) < max(2, len(obj_kws) // 3):
        violations.append("the objective does not appear to survive into the rendered prompt")

    # ---- 4. lane-specific tightening --------------------------------------
    if lane_id == "parity":
        free = set(lane.get("free_set", []))
        if "reasoning_configuration" not in free:
            for key in ("effort", "reasoning", "thinking_level", "thinking_config"):
                if key in request_body and request_body.get(key) not in (None, {}):
                    warnings.append(
                        f"parity lane: adapter set '{key}'. Parity runs every model at its documented "
                        f"default; confirm this is the default and not a tuned value."
                    )

    # ---- 5. budget integrity ----------------------------------------------
    declared_out = ir.budget.get("max_output_tokens")
    actual_out = (
        request_body.get("max_tokens")
        or request_body.get("max_output_tokens")
        or (request_body.get("generationConfig") or {}).get("maxOutputTokens")
    )
    if declared_out and actual_out and int(actual_out) > int(declared_out):
        violations.append(
            f"budget violation: request asks for {actual_out} output tokens, IR budget allows {declared_out}"
        )

    return Verdict(
        verdict="FAIL" if violations else "PASS",
        violations=violations,
        warnings=warnings,
        semantic_digest=sem,
        residual_digest=residual_digest(ir, rendered_prompt),
    )


def _stringify(obj: Any) -> str:
    import json
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return str(obj)


def check_group(digests: dict[str, str]) -> tuple[bool, str]:
    """Confirm every model in a comparison group shares one semantic digest.

    Returns (ok, message). Called by `mb.py compile --all-models`, which is the
    cheapest possible place to discover that a comparison was never valid.
    """
    uniq = sorted(set(digests.values()))
    if len(uniq) <= 1:
        return True, f"all {len(digests)} models share semantic_digest {uniq[0][:19] if uniq else '—'}…"
    groups: dict[str, list[str]] = {}
    for model, d in digests.items():
        groups.setdefault(d, []).append(model)
    lines = [f"{len(uniq)} distinct semantic digests — this is not a valid comparison:"]
    for d, models in groups.items():
        lines.append(f"  {d[:19]}…  {', '.join(sorted(models))}")
    return False, "\n".join(lines)

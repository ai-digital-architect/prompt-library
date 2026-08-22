"""Normalize provider responses into the canonical findings structure.

Two jobs:

1. **Parse.** Providers wrap JSON differently, and models occasionally fence it
   in markdown or prepend a sentence even under structured output. Recovering
   from that is legitimate; it is a transport artifact, not a capability signal.

2. **Validate.** Schema conformance is a real production property, so the rate
   at which a model returns a first-pass-valid response is measured and
   published. But a validation failure is a `SCHEMA_INVALID` disposition, not a
   silent zero — the distinction is what keeps a formatting problem from being
   read as an inability to find bugs.

The repair path is deliberately narrow: strip fences, take the outermost JSON
object, coerce obvious type slips. It does not invent findings and it does not
fill in missing required fields, because a repair that manufactures content
would make the schema-conformance metric meaningless.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


@dataclass
class NormalizedResult:
    data: dict[str, Any] = field(default_factory=dict)
    schema_valid: bool = False
    first_pass_valid: bool = False
    repairs: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def findings(self) -> list[dict[str, Any]]:
        return list(self.data.get("findings", []) or [])

    @property
    def abstentions(self) -> list[dict[str, Any]]:
        return list(self.data.get("abstentions", []) or [])

    @property
    def answers(self) -> list[dict[str, Any]]:
        return list(self.data.get("answers", []) or [])


def parse(text: str) -> tuple[dict[str, Any] | None, list[str]]:
    repairs: list[str] = []
    if not text or not text.strip():
        return None, ["empty response body"]

    raw = text.strip()
    try:
        return json.loads(raw), repairs
    except json.JSONDecodeError:
        pass

    m = FENCE.search(raw)
    if m:
        repairs.append("stripped markdown code fence")
        try:
            return json.loads(m.group(1).strip()), repairs
        except json.JSONDecodeError:
            raw = m.group(1).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end > start:
        repairs.append("extracted outermost JSON object from surrounding prose")
        try:
            return json.loads(raw[start:end + 1]), repairs
        except json.JSONDecodeError as e:
            return None, repairs + [f"JSON decode failed: {e}"]

    return None, repairs + ["no JSON object found in response"]


def validate(data: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    """Structural validation against the findings contract.

    Implemented directly rather than via jsonschema so the harness stays
    dependency-light. It checks the constraints that actually affect scoring —
    presence, type, enum membership, ranges — and ignores the cosmetic ones.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["top-level value is not an object"]

    for key in ("findings", "abstentions"):
        if key not in data:
            errors.append(f"missing required field '{key}'")
        elif not isinstance(data[key], list):
            errors.append(f"'{key}' must be an array")

    valid_sev = {"critical", "high", "medium", "low", "info"}
    valid_cat = {"semantic", "architecture", "security", "controls", "resiliency",
                 "maintainability", "observability", "testing"}
    valid_compliance = {"COMPLIANT", "NON_COMPLIANT", "NOT_APPLICABLE", "INSUFFICIENT_EVIDENCE"}

    for i, f in enumerate(data.get("findings", []) or []):
        where = f"findings[{i}]"
        if not isinstance(f, dict):
            errors.append(f"{where}: not an object")
            continue
        for req in ("id", "category", "type", "severity", "confidence", "entities", "evidence"):
            if req not in f:
                errors.append(f"{where}: missing '{req}'")
        sev = f.get("severity")
        if sev is not None and sev not in valid_sev:
            errors.append(f"{where}: severity '{sev}' not in {sorted(valid_sev)}")
        cat = f.get("category")
        if cat is not None and cat not in valid_cat:
            errors.append(f"{where}: category '{cat}' not in {sorted(valid_cat)}")
        conf = f.get("confidence")
        if conf is not None and not (isinstance(conf, (int, float)) and 0.0 <= float(conf) <= 1.0):
            errors.append(f"{where}: confidence must be a number in [0,1], got {conf!r}")
        ents = f.get("entities")
        if ents is not None and (not isinstance(ents, list) or not ents):
            errors.append(f"{where}: entities must be a non-empty array")
        cs = f.get("compliance_status")
        if cs is not None and cs not in valid_compliance:
            errors.append(f"{where}: compliance_status '{cs}' not in {sorted(valid_compliance)}")

    for i, a in enumerate(data.get("abstentions", []) or []):
        if not isinstance(a, dict) or "question_id" not in a or "reason" not in a:
            errors.append(f"abstentions[{i}]: needs 'question_id' and 'reason'")

    return errors


def coerce(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Narrow, non-inventive repairs.

    Anything that would ADD content is out of bounds — a repair that manufactures
    a finding, an entity or a confidence value destroys both the schema metric
    and the score it feeds.
    """
    repairs: list[str] = []
    out = dict(data)

    if "findings" not in out and isinstance(out.get("results"), list):
        out["findings"] = out.pop("results")
        repairs.append("renamed 'results' to 'findings'")
    out.setdefault("abstentions", [])
    if "abstentions" not in data:
        repairs.append("added empty 'abstentions' array (absent means none, not invalid)")

    findings_in = out.get("findings")
    fixed = []
    for i, f in enumerate(findings_in or []):
        if not isinstance(f, dict):
            # Keep it. Dropping a malformed element and reporting `schema_valid`
            # would turn a genuine SCHEMA_INVALID into an OK and silently discard
            # content — a repair in the deletion direction, which the contract
            # forbids as much as one in the invention direction.
            fixed.append(f)
            repairs.append(f"findings[{i}] is not an object — kept so validation reports it")
            continue
        g = dict(f)
        if "id" not in g:
            g["id"] = f"F-{i + 1:02d}"
            repairs.append(f"assigned missing id to findings[{i}]")
        if isinstance(g.get("severity"), str):
            g["severity"] = g["severity"].strip().lower()
        if isinstance(g.get("category"), str):
            g["category"] = g["category"].strip().lower()
        c = g.get("confidence")
        if isinstance(c, str):
            try:
                g["confidence"] = float(c.strip().rstrip("%")) / (100.0 if "%" in c else 1.0)
                repairs.append(f"coerced findings[{i}].confidence from string")
            except ValueError:
                pass
        # entities given as bare strings — accepted, since the resolver only
        # needs the ref and the kind is not scored.
        ents = g.get("entities")
        if isinstance(ents, list) and ents and all(isinstance(e, str) for e in ents):
            g["entities"] = [{"kind": "method", "ref": e} for e in ents]
            repairs.append(f"wrapped findings[{i}].entities string list into objects")
        ev = g.get("evidence")
        if isinstance(ev, dict):
            g["evidence"] = [ev]
            repairs.append(f"wrapped findings[{i}].evidence object into an array")
        fixed.append(g)
    if findings_in is not None:
        out["findings"] = fixed
    return out, repairs


def normalize(text: str, schema: dict[str, Any] | None = None) -> NormalizedResult:
    data, repairs = parse(text)
    if data is None:
        return NormalizedResult(schema_valid=False, first_pass_valid=False,
                                repairs=repairs, errors=repairs)

    first_errors = validate(data, schema)
    first_pass_valid = not first_errors and not repairs

    data2, more = coerce(data)
    repairs += more
    errors = validate(data2, schema)

    return NormalizedResult(
        data=data2,
        schema_valid=not errors,
        first_pass_valid=first_pass_valid,
        repairs=repairs,
        errors=errors,
    )

"""Canonical Prompt IR: build it from a task, hash it, split invariant from free.

The IR is the whole basis of the fairness argument. A task is authored once as
structure; adapters render it per provider. The `semantic_digest` covers only
the invariant fields, so two models can receive very different-looking prompts
and still be demonstrably answering the same question.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .util import digest, load_config

IR_VERSION = "1.0.0"
DEFAULT_LANES = "config/lanes.yaml"


@dataclass
class PromptIR:
    task_id: str
    objective: str
    scope: str
    success_criteria: list[str]
    response: dict[str, Any]
    budget: dict[str, Any]
    corpus: dict[str, Any]
    prohibitions: list[str]
    ir_version: str = IR_VERSION
    suite: str | None = None
    suite_version: str | None = None
    role: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    reference_material: list[dict[str, Any]] = field(default_factory=list)
    tools: list[dict[str, Any]] = field(default_factory=list)
    evidence_provider: dict[str, Any] = field(default_factory=dict)
    trial_plan: dict[str, Any] = field(default_factory=dict)
    questions: list[dict[str, Any]] = field(default_factory=list)
    notes_for_adapters: str | None = None

    # -- hashing ------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "ir_version": self.ir_version,
            "task_id": self.task_id,
            "suite": self.suite,
            "suite_version": self.suite_version,
            "role": self.role,
            "objective": self.objective,
            "scope": self.scope,
            "success_criteria": self.success_criteria,
            "context": self.context,
            "reference_material": self.reference_material,
            "response": self.response,
            "tools": self.tools,
            "budget": self.budget,
            "corpus": self.corpus,
            "evidence_provider": self.evidence_provider,
            "trial_plan": self.trial_plan,
            "questions": self.questions,
            "prohibitions": self.prohibitions,
            "notes_for_adapters": self.notes_for_adapters,
        }

    def ir_hash(self) -> str:
        return digest(self.to_dict())

    def semantic_view(self, semantic_fields: list[str]) -> dict[str, Any]:
        """Project the IR onto its invariant fields only.

        `tool_semantics` is derived rather than copied: a tool's *description*
        prose is presentation and may be re-rendered per provider, but its name,
        parameter names, types, enum values and required flags are semantics. If
        those were left free, an adapter could quietly widen or narrow what a
        tool can do.
        """
        d = self.to_dict()
        view: dict[str, Any] = {}
        for f in semantic_fields:
            if f == "tool_semantics":
                view[f] = [_tool_semantics(t) for t in self.tools]
            elif f == "required_output_fields":
                view[f] = sorted(self.response.get("required_fields", []))
            elif f == "response_schema_ref":
                view[f] = self.response.get("schema_ref")
            elif f == "response_schema_version":
                view[f] = self.response.get("schema_version")
            elif f == "evidence_budget":
                view[f] = self.budget
            elif f == "corpus_ref":
                view[f] = self.corpus
            elif f == "evidence_provider_ref":
                view[f] = self.evidence_provider
            elif f == "trial_plan":
                view[f] = self.trial_plan
            else:
                view[f] = d.get(f)
        return view

    def semantic_digest(self, semantic_fields: list[str]) -> str:
        return digest(self.semantic_view(semantic_fields))


def _tool_semantics(tool: dict[str, Any]) -> dict[str, Any]:
    params = tool.get("parameters", {}) or {}
    props = params.get("properties", {}) or {}
    return {
        "name": tool.get("name"),
        "required": sorted(params.get("required", []) or []),
        "params": {
            k: {
                "type": v.get("type"),
                "enum": sorted(v.get("enum", []) or []) or None,
                "minimum": v.get("minimum"),
                "maximum": v.get("maximum"),
            }
            for k, v in sorted(props.items())
        },
    }


class Lanes:
    def __init__(self, path: str = DEFAULT_LANES):
        data = load_config(path)
        self.version = data.get("lanes_version", "0.0.0")
        self.semantic_fields: list[str] = data.get("semantic_fields", [])
        self.prohibitions: list[dict[str, Any]] = data.get("prohibitions", [])
        self._lanes = {l["id"]: l for l in data.get("lanes", [])}
        self.uplift_ladder = data.get("uplift_ladder", [])

    def get(self, lane_id: str) -> dict[str, Any]:
        if lane_id not in self._lanes:
            raise KeyError(f"unknown lane '{lane_id}'. Known: {', '.join(self._lanes)}")
        return self._lanes[lane_id]

    def ids(self) -> list[str]:
        return list(self._lanes)


def build_ir(task: dict[str, Any], *, suite: str, suite_version: str,
             corpus: dict[str, Any], evidence_provider: dict[str, Any],
             budget_override: dict[str, Any] | None = None,
             trials: int = 5, ordering_seed: int = 0,
             lanes: Lanes | None = None) -> PromptIR:
    """Compile an authored task into the canonical IR."""
    lanes = lanes or Lanes()
    p = task.get("prompt", {})
    budget = dict(task.get("budget", {}))
    if budget_override:
        budget.update({k: v for k, v in budget_override.items() if v is not None})

    default_prohibitions = [pr["id"] for pr in lanes.prohibitions]
    task_prohibitions = list(task.get("prohibitions", []) or [])
    # A task may ADD prohibitions but never remove one — otherwise a task author
    # can quietly re-enable a construct the contract bans.
    prohibitions = sorted(set(default_prohibitions) | set(task_prohibitions))

    return PromptIR(
        task_id=task["id"],
        suite=suite,
        suite_version=suite_version,
        role={"persona": p.get("persona"), "domain": p.get("domain")},
        objective=p["objective"],
        scope=p["scope"],
        success_criteria=list(p.get("success_criteria", [])),
        context=p.get("context", {}) or {},
        reference_material=list(p.get("reference_material", []) or []),
        response=task.get("response") or {
            "schema_ref": "schemas/findings-v1.schema.json",
            "schema_version": "1.0.0",
            "required_fields": ["findings", "abstentions"],
        },
        tools=list(task.get("tools", []) or []),
        budget=budget,
        corpus=corpus,
        evidence_provider=evidence_provider,
        trial_plan={"trials": trials, "ordering_seed": ordering_seed},
        questions=list(p.get("questions", []) or []),
        prohibitions=prohibitions,
    )

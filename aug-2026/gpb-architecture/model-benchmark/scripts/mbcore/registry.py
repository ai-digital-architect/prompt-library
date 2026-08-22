"""Model registry: capability facts, status, and the effort ladder.

The registry is deliberately declarative. Every capability fact traces to a
template in the read-only prompt library, and the registry records which one, so
a reviewer can check a claim rather than trust it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .util import load_config

DEFAULT_REGISTRY = "config/models.yaml"


@dataclass
class Model:
    id: str
    provider: str
    adapter: str
    status: str
    enabled: bool
    raw: dict[str, Any] = field(default_factory=dict)

    # ---- convenience accessors -------------------------------------------
    @property
    def display_name(self) -> str:
        return self.raw.get("display_name", self.id)

    @property
    def effort_ladder(self) -> list[str]:
        return list(self.raw.get("effort_ladder", []) or [])

    @property
    def effort_default(self) -> str | None:
        return self.raw.get("effort_default")

    @property
    def effort_param(self) -> str | None:
        return self.raw.get("effort_param")

    @property
    def max_output_tokens(self) -> int:
        return int(self.raw.get("default_max_output_tokens") or self.raw.get("max_output_tokens") or 8000)

    @property
    def derived(self) -> bool:
        return bool(self.raw.get("derived", False))

    @property
    def retention_posture(self) -> str:
        return self.raw.get("retention_posture", "unknown")

    @property
    def rejects(self) -> list[str]:
        return list(self.raw.get("rejects", []) or [])

    @property
    def structured_output(self) -> str | None:
        return self.raw.get("structured_output")

    @property
    def template_ref(self) -> str | None:
        return self.raw.get("template_ref")

    def supports_reasoning_mode(self) -> bool:
        rm = self.raw.get("reasoning_mode") or {}
        return bool(rm.get("documented_for_this_model"))

    def long_prompt_threshold(self) -> int | None:
        lps = self.raw.get("long_prompt_surcharge") or {}
        return lps.get("threshold_input_tokens")


class Registry:
    def __init__(self, path: str = DEFAULT_REGISTRY):
        self.path = path
        data = load_config(path)
        self.version: str = data.get("registry_version", "0.0.0")
        self.verified_against_templates = data.get("verified_against_templates")
        self._models: dict[str, Model] = {}
        for entry in data.get("models", []):
            m = Model(
                id=entry["id"],
                provider=entry["provider"],
                adapter=entry["adapter"],
                status=entry.get("status", "current"),
                enabled=bool(entry.get("enabled", True)),
                raw=entry,
            )
            self._models[m.id] = m
        self.excluded = data.get("excluded", [])

    # ---- lookup -----------------------------------------------------------
    def get(self, model_id: str) -> Model:
        if model_id not in self._models:
            close = [m for m in self._models if model_id.lower() in m.lower()]
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            raise KeyError(f"unknown model '{model_id}'.{hint}")
        return self._models[model_id]

    def all(self, include_disabled: bool = False) -> list[Model]:
        return [m for m in self._models.values() if include_disabled or m.enabled]

    def ids(self, include_disabled: bool = False) -> list[str]:
        return [m.id for m in self.all(include_disabled)]

    def by_provider(self, provider: str) -> list[Model]:
        return [m for m in self._models.values() if m.provider == provider]

    def providers(self) -> list[str]:
        seen: list[str] = []
        for m in self._models.values():
            if m.provider not in seen:
                seen.append(m.provider)
        return seen

    # ---- self-check -------------------------------------------------------
    def validate(self) -> list[str]:
        """Internal consistency only. This cannot validate vendor truth — that is
        what `verified_against_templates` and the pre-round re-verification step
        are for."""
        problems: list[str] = []
        for m in self._models.values():
            if m.effort_default and m.effort_ladder and m.effort_default not in m.effort_ladder:
                problems.append(f"{m.id}: effort_default '{m.effort_default}' not in ladder {m.effort_ladder}")
            if m.derived and not m.raw.get("derived_from"):
                problems.append(f"{m.id}: derived=true but no derived_from")
            if m.derived and not m.raw.get("template_note"):
                problems.append(f"{m.id}: derived profile must carry a template_note explaining the derivation")
            if m.status == "retired" and m.enabled:
                problems.append(f"{m.id}: status=retired must not be enabled by default")
            if not m.template_ref and not m.derived and m.status != "retired":
                problems.append(f"{m.id}: no template_ref and not marked derived")
            mo = m.raw.get("max_output_tokens")
            dmo = m.raw.get("default_max_output_tokens")
            if mo and dmo and dmo > mo:
                problems.append(f"{m.id}: default_max_output_tokens {dmo} exceeds max {mo}")
        return problems

    def sweep_points(self, model_id: str, extra_axes: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Expand a model into its configuration sweep.

        The ladder is walked cheapest-first so that a spend cap truncates the
        expensive end rather than the cheap end — every model then has points at
        the low-cost end of the frontier, which is where iso-cost comparisons at
        $0.05/task actually land.
        """
        m = self.get(model_id)
        ladder = m.effort_ladder or [None]
        points = [{"effort": e} for e in ladder]
        axes = (extra_axes or {}).get(model_id, {}) if extra_axes else {}
        for axis, values in axes.items():
            if axis == "reasoning_mode" and not m.supports_reasoning_mode():
                # Refuse rather than risk a silent behavioural difference on a
                # tier where the parameter is not documented.
                continue
            expanded = []
            for p in points:
                for v in values:
                    q = dict(p)
                    q[axis] = v
                    expanded.append(q)
            points = expanded
        return points

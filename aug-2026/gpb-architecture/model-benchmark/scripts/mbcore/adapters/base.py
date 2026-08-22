"""Model adapter SPI.

An adapter owns everything in the lane's FREE set: prompt syntax, section
placement and ordering, reasoning configuration, the structured-output
mechanism, verbosity control, token ceilings, streaming and cache layout. It
owns none of the semantics. The fairness validator runs between compile() and
invoke() and will refuse a request that crossed the line.

Adding a model: see skills/adapter-authoring/SKILL.md.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from ..ir import PromptIR
from ..registry import Model
from ..util import text_digest


@dataclass
class RunProfile:
    """The knobs a sweep varies. All of these live in the FREE set."""
    effort: str | None = None
    reasoning_mode: str | None = None
    verbosity: str | None = None
    max_output_tokens: int | None = None
    stream: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderRequest:
    model_id: str
    provider: str
    url: str
    headers: dict[str, str]
    body: dict[str, Any]
    rendered_prompt: str
    structured_output_mechanism: str | None = None
    # The IR's output budget. A retry that raises the ceiling clamps to this, so
    # it cannot edit the request past what the fairness validator approved.
    max_output_ceiling: int = 0

    def rendered_prompt_hash(self) -> str:
        return text_digest(self.rendered_prompt)


@dataclass
class ProviderResponse:
    status: int
    body: dict[str, Any]
    text: str = ""
    error: str | None = None
    wall_clock_ms: int = 0
    ttft_ms: int | None = None
    raw_headers: dict[str, str] = field(default_factory=dict)


class ModelAdapter:
    """Base class. Subclasses implement compile/invoke/normalize/usage/disposition."""

    id: str = "base"
    version: str = "0.0.0"
    provider: str = "none"

    # ------------------------------------------------------------- rendering
    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest:
        raise NotImplementedError

    # ------------------------------------------------------------- invoking
    def invoke(self, req: ProviderRequest, timeout: int = 900) -> ProviderResponse:
        """Default transport: plain HTTPS via the standard library.

        Deliberately dependency-free. Provider SDKs move faster than a benchmark
        harness should, and an SDK upgrade silently changing a default is exactly
        the kind of uncontrolled variable this whole design exists to eliminate.
        """
        payload = json.dumps(req.body).encode("utf-8")
        request = urllib.request.Request(req.url, data=payload, headers=req.headers, method="POST")
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                elapsed = int((time.time() - started) * 1000)
                return ProviderResponse(
                    status=resp.status,
                    body=json.loads(raw) if raw else {},
                    text=raw,
                    wall_clock_ms=elapsed,
                    raw_headers=dict(resp.headers),
                )
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            elapsed = int((time.time() - started) * 1000)
            try:
                body = json.loads(raw)
            except Exception:
                body = {"raw": raw}
            return ProviderResponse(status=e.code, body=body, text=raw,
                                    error=f"HTTP {e.code}", wall_clock_ms=elapsed)
        except Exception as e:  # transport, DNS, timeout
            elapsed = int((time.time() - started) * 1000)
            return ProviderResponse(status=0, body={}, error=f"{type(e).__name__}: {e}",
                                    wall_clock_ms=elapsed)

    # ------------------------------------------------------------ extracting
    def extract_text(self, resp: ProviderResponse) -> str:
        raise NotImplementedError

    def usage(self, resp: ProviderResponse):
        raise NotImplementedError

    def refusal(self, resp: ProviderResponse) -> tuple[bool, str | None]:
        """Return (is_safety_refusal, category).

        This is the single most consequential method in the adapter. A safety
        refusal returned as HTTP 200 looks exactly like a successful empty answer
        to any naive harness, and scoring it as recall-zero systematically
        penalizes classifier-bearing models on the security suite.
        """
        return False, None

    def truncated(self, resp: ProviderResponse) -> bool:
        return False

    def resolved_model_version(self, resp: ProviderResponse) -> str | None:
        return None


# --------------------------------------------------------------------------
# Shared rendering helpers
# --------------------------------------------------------------------------

def response_contract_text(ir: PromptIR) -> str:
    fields = ir.response.get("required_fields", [])
    lines = [
        "Return a single JSON object conforming to the "
        f"{ir.response.get('schema_ref')} schema (version {ir.response.get('schema_version')}).",
        "Required top-level fields: " + ", ".join(fields) + ".",
        "Emit findings as structured objects with `entities`, `relations` and `evidence` — "
        "these are checked against the code graph, so name entities precisely.",
        "`abstentions` is a first-class answer. If the material does not support a conclusion, "
        "say so there rather than producing a low-confidence guess.",
        "`confidence` is a calibrated probability in [0,1], scored on its own.",
    ]
    return "\n".join(lines)


def budget_text(ir: PromptIR) -> str:
    b = ir.budget
    parts = []
    if b.get("max_tool_calls") is not None:
        parts.append(f"at most {b['max_tool_calls']} tool calls")
    if b.get("max_graph_queries") is not None:
        parts.append(f"at most {b['max_graph_queries']} graph queries")
    if b.get("max_files_opened") is not None:
        parts.append(f"at most {b['max_files_opened']} files opened")
    if not parts:
        return ""
    return ("Evidence budget for this task: " + ", ".join(parts) +
            ". Spend it where it changes the answer.")


def reference_text(ir: PromptIR) -> list[tuple[str, str, str]]:
    """Return (label, kind, content) triples for reference material."""
    out = []
    for r in ir.reference_material:
        content = r.get("inline")
        if content is None and r.get("path"):
            content = f"[attached: {r['path']}]"
        out.append((r.get("label", "reference"), r.get("kind", "spec"), content or ""))
    return out


def questions_text(ir: PromptIR) -> str:
    if not ir.questions:
        return ""
    lines = ["Questions:"]
    for q in ir.questions:
        lines.append(f"- [{q['id']}] {q['text']}")
    return "\n".join(lines)


def json_schema_for_response(ir: PromptIR, skill_root) -> dict[str, Any] | None:
    """Load the response JSON schema so adapters can attach it natively.

    Attaching the schema through the API rather than describing it in prose frees
    prompt budget and removes the most common source of format drift — and it is
    supported by every model in the roster, so it costs nothing in fairness terms.
    """
    ref = ir.response.get("schema_ref")
    if not ref:
        return None
    from pathlib import Path
    p = Path(skill_root) / ref
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

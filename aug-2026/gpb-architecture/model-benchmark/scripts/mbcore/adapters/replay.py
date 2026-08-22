"""Dry-run and replay transports.

These are not conveniences — they are what makes the harness testable. Grading,
matching, scoring, calibration and statistics are the parts most likely to carry
a subtle bug, and they are also the parts you least want to debug by spending
money on eleven providers. Replay lets the entire pipeline below `invoke()` run
in CI with no keys and no spend.

Cassette selection is keyed on (model_id, task_id, trial). A missing cassette is
an explicit error rather than a silent empty response, because a silently empty
response would score as recall-zero and look like a model failure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..secrets import redact
from ..util import SKILL_ROOT, digest
from .base import ProviderRequest, ProviderResponse

CASSETTE_DIR = SKILL_ROOT / "fixtures" / "cassettes"


class DryRunTransport:
    """Compiles and validates, never calls. Returns a synthetic response marked
    as such so nothing downstream mistakes it for a measurement."""

    mode = "dry-run"

    def invoke(self, req: ProviderRequest, timeout: int = 900) -> ProviderResponse:
        return ProviderResponse(
            status=0,
            body={"_dry_run": True, "model": req.model_id},
            text="",
            error=None,
            wall_clock_ms=0,
        )


class ReplayTransport:
    """Serves recorded responses from fixtures/cassettes/."""

    mode = "replay"

    def __init__(self, cassette_dir: Path | str = CASSETTE_DIR, strict: bool = True):
        self.dir = Path(cassette_dir)
        self.strict = strict

    @staticmethod
    def cassette_name(model_id: str, task_id: str, trial: int) -> str:
        safe = model_id.replace("/", "_")
        return f"{safe}__{task_id}__t{trial}.json"

    def path_for(self, model_id: str, task_id: str, trial: int) -> Path:
        return self.dir / self.cassette_name(model_id, task_id, trial)

    def invoke(self, req: ProviderRequest, timeout: int = 900,
               task_id: str = "", trial: int = 1) -> ProviderResponse:
        p = self.path_for(req.model_id, task_id, trial)
        if not p.exists():
            # Fall back to trial 1 — recording every trial of every model is
            # rarely worth the disk, and reusing trial 1 is honest as long as it
            # is not mistaken for real variance.
            p = self.path_for(req.model_id, task_id, 1)
        if not p.exists():
            if self.strict:
                raise FileNotFoundError(
                    f"no cassette for {req.model_id} / {task_id} / trial {trial}.\n"
                    f"  expected: {self.path_for(req.model_id, task_id, trial)}\n"
                    f"  Record one with `mb.py run --live --record`, or add a fixture.\n"
                    f"  A missing cassette is never treated as an empty response: that "
                    f"would score as recall-zero and look like a model failure."
                )
            return ProviderResponse(status=0, body={}, error="cassette_missing")
        data = json.loads(p.read_text(encoding="utf-8"))
        return ProviderResponse(
            status=int(data.get("status", 200)),
            body=data.get("body", {}),
            text=json.dumps(data.get("body", {})),
            error=data.get("error"),
            wall_clock_ms=int(data.get("wall_clock_ms", 0)),
            ttft_ms=data.get("ttft_ms"),
        )


class Recorder:
    """Writes cassettes during a live run. Everything is redacted first — a
    cassette is a persisted artifact and gets the same treatment as a transcript."""

    def __init__(self, cassette_dir: Path | str = CASSETTE_DIR):
        self.dir = Path(cassette_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def record(self, req: ProviderRequest, resp: ProviderResponse,
               task_id: str, trial: int) -> Path:
        p = self.dir / ReplayTransport.cassette_name(req.model_id, task_id, trial)
        payload: dict[str, Any] = {
            "recorded_for": {"model": req.model_id, "task": task_id, "trial": trial},
            "request_digest": digest(redact(req.body)),
            "status": resp.status,
            "body": redact(resp.body),
            "error": resp.error,
            "wall_clock_ms": resp.wall_clock_ms,
            "ttft_ms": resp.ttft_ms,
        }
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return p

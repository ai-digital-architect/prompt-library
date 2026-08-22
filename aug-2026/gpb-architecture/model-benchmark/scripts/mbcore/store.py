"""Experiment store.

JSONL on disk: no database to stand up, greppable, diffable, and trivially
shipped to whatever warehouse the org already runs. Each run directory is
self-contained so it can be archived as a unit.

Two structural choices matter:

1. **Transcripts are stored separately from identity.** `transcripts/<hash>.json`
   holds content; the manifest holds the model. A reviewer working on blinded
   judging cannot undo the blinding by opening one file.

2. **Everything is redacted on write.** Manifests, transcripts and cassettes all
   pass through the redaction pass, so a credential that reached an artifact by
   accident does not persist into an archive.
"""

from __future__ import annotations

import datetime as _dt
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterator

from .secrets import redact
from .util import digest


def _default(o: Any):
    if is_dataclass(o):
        return asdict(o)
    if isinstance(o, set):
        return sorted(o)
    return str(o)


class RunStore:
    def __init__(self, run_dir: str | Path):
        self.dir = Path(run_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "transcripts").mkdir(exist_ok=True)
        self.manifests = self.dir / "manifests.jsonl"
        self.grades = self.dir / "grades.jsonl"
        self.events = self.dir / "events.jsonl"

    # ------------------------------------------------------------------ meta
    def write_study(self, study: dict[str, Any]) -> Path:
        p = self.dir / "study.json"
        p.write_text(json.dumps(redact(study), indent=2, default=_default), encoding="utf-8")
        return p

    def read_study(self) -> dict[str, Any]:
        p = self.dir / "study.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    # ------------------------------------------------------------- manifests
    def append_manifest(self, manifest: dict[str, Any]) -> None:
        with self.manifests.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(redact(manifest), default=_default) + "\n")

    def iter_manifests(self) -> Iterator[dict[str, Any]]:
        if not self.manifests.exists():
            return
        with self.manifests.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)

    # ---------------------------------------------------------------- grades
    def append_grade(self, grade: dict[str, Any]) -> None:
        with self.grades.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(redact(grade), default=_default) + "\n")

    def iter_grades(self) -> Iterator[dict[str, Any]]:
        if not self.grades.exists():
            return
        with self.grades.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def reset_grades(self) -> None:
        if self.grades.exists():
            self.grades.unlink()

    # ----------------------------------------------------------- transcripts
    def write_transcript(self, payload: dict[str, Any]) -> str:
        """Content-addressed and identity-free. Returns the reference to store in
        the manifest."""
        red = redact(payload)
        ref = digest(red).split(":")[1][:24]
        (self.dir / "transcripts" / f"{ref}.json").write_text(
            json.dumps(red, indent=2, default=_default), encoding="utf-8")
        return ref

    def read_transcript(self, ref: str) -> dict[str, Any]:
        return json.loads((self.dir / "transcripts" / f"{ref}.json").read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- events
    def log(self, kind: str, **fields: Any) -> None:
        rec = {"ts": _dt.datetime.now(_dt.timezone.utc).isoformat(), "kind": kind}
        rec.update(fields)
        with self.events.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(redact(rec), default=_default) + "\n")

    # --------------------------------------------------------------- reports
    def write_report(self, name: str, content: str) -> Path:
        p = self.dir / name
        p.write_text(content, encoding="utf-8")
        return p


def new_run_id(prefix: str = "") -> str:
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    import secrets as _s
    return f"{prefix + '-' if prefix else ''}{ts}-{_s.token_hex(3)}"


def find_latest_run(root: str | Path = "runs") -> Path | None:
    r = Path(root)
    if not r.exists():
        return None
    runs = [d for d in r.iterdir() if d.is_dir() and (d / "study.json").exists()]
    if not runs:
        return None
    return max(runs, key=lambda d: d.stat().st_mtime)

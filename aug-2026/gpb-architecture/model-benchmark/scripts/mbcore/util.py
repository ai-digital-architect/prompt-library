"""Shared utilities: config loading, canonical hashing, small IO helpers.

Canonical hashing matters more than it looks. `semantic_digest` is the artifact
that turns "the comparison was fair" from an assertion into something a reviewer
can check, so the hash has to be stable against irrelevant differences (key
order, trailing whitespace, YAML vs JSON authoring) and sensitive to everything
else.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# Config loading
# --------------------------------------------------------------------------

def _require_yaml():
    try:
        import yaml  # noqa: F401
        return yaml
    except ImportError:  # pragma: no cover
        sys.stderr.write(
            "\nmodel-benchmark needs PyYAML to read suite and config files.\n"
            "  pip install pyyaml        (or: pip install -r scripts/requirements.txt)\n\n"
        )
        raise SystemExit(2)


def load_config(path: str | Path) -> Any:
    """Load a YAML or JSON config file. Path may be absolute or skill-relative."""
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = SKILL_ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"config not found: {path} (looked in {p})")
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".json",):
        return json.loads(text)
    return _require_yaml().safe_load(text)


def write_json(path: str | Path, obj: Any) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=False, default=str), encoding="utf-8")
    return p


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Canonical hashing
# --------------------------------------------------------------------------

def canonicalize(obj: Any) -> Any:
    """Normalize a structure so that irrelevant authoring differences hash alike.

    Dict keys are sorted, strings have their whitespace collapsed, and None is
    distinguished from the empty string (a dropped requirement must not hash the
    same as an empty one).
    """
    if isinstance(obj, dict):
        return {k: canonicalize(obj[k]) for k in sorted(obj)}
    if isinstance(obj, (list, tuple)):
        return [canonicalize(v) for v in obj]
    if isinstance(obj, str):
        return re.sub(r"\s+", " ", obj).strip()
    return obj


def digest(obj: Any) -> str:
    payload = json.dumps(canonicalize(obj), sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def short(d: str, n: int = 12) -> str:
    return d.split(":")[-1][:n]


# --------------------------------------------------------------------------
# Terminal helpers (no dependencies, degrade cleanly when piped)
# --------------------------------------------------------------------------

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def ok(t: str) -> str:
    return c(t, "32")


def warn(t: str) -> str:
    return c(t, "33")


def bad(t: str) -> str:
    return c(t, "31")


def dim(t: str) -> str:
    return c(t, "2")


def table(rows: list[list[str]], headers: list[str]) -> str:
    """Minimal fixed-width table. Good enough for a CLI, stable when piped."""
    cols = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(str(r[i])) if i < len(r) else 0)
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep = "  ".join("-" * widths[i] for i in range(cols))
    out = [line, sep]
    for r in rows:
        out.append("  ".join(str(r[i] if i < len(r) else "").ljust(widths[i]) for i in range(cols)))
    return "\n".join(out)

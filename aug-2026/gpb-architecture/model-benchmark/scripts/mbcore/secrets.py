"""Credential resolution and artifact redaction.

Design rule: a credential is read from the process environment at invoke time,
handed directly to the transport, and never placed in any object that is hashed,
persisted, or printed. Everything the harness writes — manifests, transcripts,
cassettes, logs, reports — passes through `redact()` first.

The second rule is about process environment. Subprocess environments are
CONSTRUCTED rather than inherited, so an OpenAI key is not visible to a
subprocess spawned by the Google adapter. Wholesale `os.environ` inheritance is
the most common way keys leak across provider boundaries in a multi-vendor
harness.
"""

from __future__ import annotations

import os
import re
from typing import Iterable

# Environment variables each provider is allowed to see. Nothing else is passed
# into a provider-scoped subprocess environment.
PROVIDER_ENV = {
    "anthropic": ["ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN"],
    "openai": ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_ORG_ID", "OPENAI_PROJECT"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_GENAI_BASE_URL"],
}

PRIMARY_KEY = {
    "anthropic": ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"],
    "openai": ["OPENAI_API_KEY"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
}

# Shapes that look like credentials. Used both to redact artifacts and to refuse
# to start when a key has been pasted into a config file.
SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)\b(api[_-]?key|auth[_-]?token|secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9._\-]{16,}"),
]

REDACTION = "«redacted»"

# Key names that hold a credential. Deliberately anchored and singular: a naive
# /token|secret|auth/ substring match also eats `output_tokens`,
# `cache_write_tokens` and `max_input_tokens`, which silently destroys every
# usage count in every manifest and makes cost unauditable from the artifact.
_SECRET_KEY_RE = re.compile(
    r"(?i)^(?:x[-_])?(?:"
    r"api[-_]?key|apikey|auth|authorization|auth[-_]?token|access[-_]?token|"
    r"refresh[-_]?token|id[-_]?token|bearer|secret|client[-_]?secret|"
    r"password|passwd|pwd|credential|credentials|private[-_]?key|session[-_]?key"
    r")$"
)
# Suffix rule for names like `openai_api_key` / `service_secret`. Singular only —
# `_tokens` and `_keys` are plural count fields, not credentials.
_SECRET_SUFFIX_RE = re.compile(r"(?i)_(?:api_?key|key|secret|token|password)$")


class MissingCredential(RuntimeError):
    pass


def resolve_key(provider: str) -> str:
    """Return the credential for a provider, or raise with an actionable message.

    The value is returned but never logged. Callers hand it straight to the
    transport layer.
    """
    for name in PRIMARY_KEY.get(provider, []):
        val = os.environ.get(name)
        if val:
            return val
    names = " or ".join(PRIMARY_KEY.get(provider, ["<unknown>"]))
    raise MissingCredential(
        f"No credential found for provider '{provider}'. Set {names} in the "
        f"environment. The harness never reads credentials from config files — "
        f"see references/security.md."
    )


def key_present(provider: str) -> bool:
    return any(os.environ.get(n) for n in PRIMARY_KEY.get(provider, []))


def provider_env(provider: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Construct a minimal environment for a provider-scoped subprocess.

    Deliberately does NOT start from os.environ. PATH, HOME and LANG are carried
    because tooling breaks without them; nothing else crosses the boundary.
    """
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL") if k in os.environ}
    for name in PROVIDER_ENV.get(provider, []):
        if name in os.environ:
            env[name] = os.environ[name]
    if extra:
        env.update(extra)
    return env


def redact(obj):
    """Recursively replace anything credential-shaped. Applied to every artifact
    before it is written or printed."""
    if isinstance(obj, str):
        out = obj
        for pat in SECRET_PATTERNS:
            out = pat.sub(REDACTION, out)
        return out
    if isinstance(obj, dict):
        red = {}
        for k, v in obj.items():
            if isinstance(k, str) and (_SECRET_KEY_RE.match(k) or _SECRET_SUFFIX_RE.search(k)):
                red[k] = REDACTION
            else:
                red[k] = redact(v)
        return red
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


def scan_for_secrets(text: str) -> list[str]:
    """Return the patterns that matched. Used to refuse to start when a key has
    been committed into a config file — a far more common leak than a logging
    mistake."""
    hits = []
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def audit_paths(paths: Iterable[str]) -> list[tuple[str, list[str]]]:
    findings = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                hits = scan_for_secrets(fh.read())
        except OSError:
            continue
        if hits:
            findings.append((p, hits))
    return findings

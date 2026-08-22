"""Google Gemini 3.x adapter — Gemini 3.6 Flash, and Gemini 3 Pro (retired).

Source: templates 26 (3.6 Flash) and 04 (3 Pro, reference-only) in the read-only
prompt library.

Three Gemini-specific rules shape this renderer, and getting any of them wrong
produces either an error or a silently different experiment:

1. **Context first, instruction last.** Google's long-context guidance is
   explicit: documents, code and media at the top, the specific question at the
   very end. This is the ordering freedom the Optimized lane exists to grant.

2. **No sampling parameters.** `temperature`, `top_p` and `top_k` are deprecated
   and silently ignored on this generation, and will return HTTP 400 in future
   versions. Silently ignored is the dangerous case: a harness that sets them
   believes it has control it does not have.

3. **A request may not end on a model-role turn.** Prefill-style steering errors
   out; it has to move into `system_instruction` or the response schema. This
   renderer never emits a trailing model turn.

Depth is steered with `thinking_level` string values, not `thinking_budget`.
"""

from __future__ import annotations

from typing import Any

from ..ir import PromptIR
from ..pricing import Usage
from ..registry import Model
from ..secrets import resolve_key
from ..util import SKILL_ROOT
from .base import (
    ModelAdapter,
    ProviderRequest,
    ProviderResponse,
    RunProfile,
    budget_text,
    json_schema_for_response,
    questions_text,
    reference_text,
    response_contract_text,
)

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _strip_unsupported(schema: Any) -> Any:
    """Reduce a JSON Schema to the subset Gemini's response schema accepts.

    Unsupported keywords are dropped rather than passed through, because an
    unrecognized keyword can cause the whole schema to be rejected — which would
    show up as a SCHEMA_INVALID disposition and be misread as a model weakness.
    """
    if isinstance(schema, dict):
        drop = {"$schema", "$id", "additionalProperties", "definitions", "$ref",
                "const", "examples", "pattern", "minItems", "maxLength", "default"}
        out = {}
        for k, v in schema.items():
            if k in drop:
                continue
            out[k] = _strip_unsupported(v)
        return out
    if isinstance(schema, list):
        return [_strip_unsupported(v) for v in schema]
    return schema


class GoogleGemini3xAdapter(ModelAdapter):
    id = "google-gemini3x"
    version = "1.0.0"
    provider = "google"

    def _headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": resolve_key("google"),
            "content-type": "application/json",
        }

    # ----------------------------------------------------------- rendering
    def _system_instruction(self, ir: PromptIR, model: Model) -> str:
        role = ir.role or {}
        persona = role.get("persona") or "a principal engineer"
        domain = role.get("domain") or "enterprise software systems"

        rules = [
            f"Scope: {ir.scope}",
            "Report coverage, not a shortlist: include uncertain and low-severity findings "
            "with their own confidence and severity.",
            "Cite file, symbol and line range for every finding; distinguish confirmed from inferred.",
            "Where the material does not support a conclusion, record an abstention.",
            "The current year is 2026. For anything newer than your training data, rely on the "
            "provided context rather than memory.",
            "Default to concise output; expand only where the task requires it.",
        ]
        b = budget_text(ir)
        if b:
            rules.append(b)

        lines = [f"You are {persona} specializing in {domain}.", "", "Rules:"]
        lines += [f"- {r}" for r in rules]

        triggers = [t.get("when_to_use") for t in ir.tools if t.get("when_to_use")]
        if triggers:
            lines += ["", "Tool use:"] + [f"- {t}" for t in triggers]
        return "\n".join(lines)

    def _user(self, ir: PromptIR) -> str:
        """Context first, instruction last — the ordering Google's guidance asks for."""
        parts: list[str] = ["## Context"]
        ctx = ir.context or {}
        if ctx.get("why_this_matters"):
            parts.append(ctx["why_this_matters"])
        if ctx.get("audience"):
            parts.append(f"Audience: {ctx['audience']}.")
        for k in ctx.get("known_constraints", []) or []:
            parts.append(f"- {k}")

        for label, kind, content in reference_text(ir):
            parts.append(f"\n### {label} ({kind})\n{content}")

        parts += ["", "## Task", ir.objective.strip()]

        q = questions_text(ir)
        if q:
            parts += ["", q]

        parts += ["", "## Requirements"]
        parts += [f"{i}. {c}" for i, c in enumerate(ir.success_criteria, 1)]

        parts += ["", "## Output Format", response_contract_text(ir)]
        return "\n".join(parts)

    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest:
        system = self._system_instruction(ir, model)
        user = self._user(ir)

        max_out = min(
            profile.max_output_tokens or model.max_output_tokens,
            int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )

        gen_config: dict[str, Any] = {"maxOutputTokens": max_out}
        if profile.effort:
            gen_config["thinkingConfig"] = {"thinkingLevel": profile.effort}

        schema = json_schema_for_response(ir, SKILL_ROOT)
        if schema:
            gen_config["responseMimeType"] = "application/json"
            gen_config["responseSchema"] = _strip_unsupported(schema)

        body: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system}]},
            # The final turn is always the user's. Never append a model turn.
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": gen_config,
        }
        # temperature / topP / topK are deliberately absent.

        url = f"{API_BASE}/{model.id}:generateContent"
        return ProviderRequest(
            model_id=model.id, provider=self.provider, url=url,
            headers=self._headers(), body=body,
            rendered_prompt=system + "\n\n---\n\n" + user,
            structured_output_mechanism="response_mime_type+schema",
            max_output_ceiling=int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )

    # ------------------------------------------------------------- response
    def extract_text(self, resp: ProviderResponse) -> str:
        chunks = []
        for cand in resp.body.get("candidates", []) or []:
            for part in (cand.get("content", {}) or {}).get("parts", []) or []:
                if "text" in part:
                    chunks.append(part["text"])
        return "\n".join(chunks)

    def usage(self, resp: ProviderResponse) -> Usage:
        u = resp.body.get("usageMetadata", {}) or {}
        cached = int(u.get("cachedContentTokenCount", 0) or 0)
        total_in = int(u.get("promptTokenCount", 0) or 0)
        # Search grounding is billed separately from tokens. Leaving it at zero
        # understated Gemini on any grounded suite — exactly what config/pricing.yaml
        # warns about in its own note.
        grounding = 0
        for cand in resp.body.get("candidates", []) or []:
            gm = cand.get("groundingMetadata") or {}
            grounding += len(gm.get("webSearchQueries") or gm.get("searchQueries") or [])
        return Usage(
            input_tokens_uncached=max(0, total_in - cached),
            input_tokens_cached=cached,
            cache_write_tokens=0,
            reasoning_tokens=u.get("thoughtsTokenCount"),
            output_tokens=int(u.get("candidatesTokenCount", 0) or 0),
            grounding_queries=grounding,
        )

    def refusal(self, resp: ProviderResponse) -> tuple[bool, str | None]:
        pf = resp.body.get("promptFeedback") or {}
        if pf.get("blockReason"):
            return True, str(pf["blockReason"])
        for cand in resp.body.get("candidates", []) or []:
            if cand.get("finishReason") in ("SAFETY", "BLOCKLIST", "PROHIBITED_CONTENT"):
                return True, str(cand["finishReason"])
        return False, None

    def truncated(self, resp: ProviderResponse) -> bool:
        for cand in resp.body.get("candidates", []) or []:
            if cand.get("finishReason") == "MAX_TOKENS":
                return True
        return False

    def resolved_model_version(self, resp: ProviderResponse) -> str | None:
        return resp.body.get("modelVersion")

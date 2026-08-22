"""OpenAI GPT-5.6 adapter — Sol, Terra, Luna.

Source: templates 23, 24, 25 in the read-only prompt library.

The rendering convention is markdown-sectioned developer/user messages via the
Responses API. Two rules from the templates drive the design here:

1. **Migrate by shrinking.** OpenAI's own testing found leaner prompts raised
   eval scores roughly 10-15% while cutting total tokens 41-66% on this
   generation. Repeated instructions and elaborate tool descriptions measurably
   lower scores — so this renderer says each thing once.

2. **`reasoning.mode` is an independent axis from `reasoning.effort`.** It is
   documented for Sol and NOT confirmed for Terra or Luna. The adapter refuses to
   set it on the tiers where it is unconfirmed rather than risking a silent
   behavioural difference that would show up as a capability gap.

Static content is placed first and dynamic content last, because cached input on
this family is 10x cheaper than uncached and cache writes bill at 1.25x — the
ordering is worth real money on a multi-thousand-call study.
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

API_URL = "https://api.openai.com/v1/responses"


class OpenAIGpt56Adapter(ModelAdapter):
    id = "openai-gpt56"
    version = "1.0.0"
    provider = "openai"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {resolve_key('openai')}",
            "content-type": "application/json",
        }

    # ----------------------------------------------------------- rendering
    def _developer(self, ir: PromptIR, model: Model) -> str:
        role = ir.role or {}
        persona = role.get("persona") or "a principal engineer"
        domain = role.get("domain") or "enterprise software systems"

        instructions = [
            f"Scope: {ir.scope}",
            "Report coverage, not a shortlist: include uncertain and low-severity findings, "
            "each with its own confidence and estimated severity.",
            "Every finding cites file, symbol and line range, and distinguishes confirmed "
            "from inferred.",
            "Autonomy: read and query freely within the evidence budget. Do not stall on "
            "ambiguity — state the assumption and proceed.",
            "If the material does not support a conclusion, record an abstention rather than "
            "producing a low-confidence guess.",
        ]
        b = budget_text(ir)
        if b:
            instructions.append(b)

        sections = [
            "# Identity",
            f"You are {persona}, an expert in {domain}.",
            "",
            "# Instructions",
            "\n".join(f"- {i}" for i in instructions),
            "",
            "# Success criteria",
            "\n".join(f"{i}. {c}" for i, c in enumerate(ir.success_criteria, 1)),
            "",
            "# Output format",
            response_contract_text(ir),
        ]

        triggers = [t.get("when_to_use") for t in ir.tools if t.get("when_to_use")]
        if triggers:
            sections += ["", "# Tool use", "\n".join(f"- {t}" for t in triggers)]
        return "\n".join(sections)

    def _user(self, ir: PromptIR) -> str:
        parts = [ir.objective.strip()]
        q = questions_text(ir)
        if q:
            parts += ["", q]
        refs = reference_text(ir)
        if refs:
            parts += ["", "Context:"]
            for label, kind, content in refs:
                parts.append(f"\n## {label} ({kind})\n{content}")
        return "\n".join(parts)

    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest:
        developer = self._developer(ir, model)
        user = self._user(ir)

        max_out = min(
            profile.max_output_tokens or model.max_output_tokens,
            int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )

        reasoning: dict[str, Any] = {}
        if profile.effort:
            reasoning["effort"] = profile.effort
        if profile.reasoning_mode:
            if model.supports_reasoning_mode():
                reasoning["mode"] = profile.reasoning_mode
            # else: silently omitted. Setting an undocumented parameter on Terra
            # or Luna could change behaviour in a way we could not attribute.

        body: dict[str, Any] = {
            "model": model.id,
            # Static developer block first so it stays in the cached prefix.
            "input": [
                {"role": "developer", "content": developer},
                {"role": "user", "content": user},
            ],
            "max_output_tokens": max_out,
        }
        if reasoning:
            body["reasoning"] = reasoning
        if profile.verbosity:
            body["text"] = {"verbosity": profile.verbosity}

        schema = json_schema_for_response(ir, SKILL_ROOT)
        if schema:
            fmt = {
                "type": "json_schema",
                "name": "engineering_findings_v1",
                "strict": False,   # the schema uses constructs strict mode rejects
                "schema": schema,
            }
            body.setdefault("text", {})["format"] = fmt

        return ProviderRequest(
            model_id=model.id, provider=self.provider, url=API_URL,
            headers=self._headers(), body=body,
            rendered_prompt=developer + "\n\n---\n\n" + user,
            structured_output_mechanism="structured_outputs",
            max_output_ceiling=int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )

    # ------------------------------------------------------------- response
    def extract_text(self, resp: ProviderResponse) -> str:
        b = resp.body
        if isinstance(b.get("output_text"), str):
            return b["output_text"]
        chunks = []
        for item in b.get("output", []) or []:
            for part in item.get("content", []) or []:
                if part.get("type") in ("output_text", "text"):
                    chunks.append(part.get("text", ""))
        return "\n".join(chunks)

    def usage(self, resp: ProviderResponse) -> Usage:
        u = resp.body.get("usage", {}) or {}
        details = u.get("input_tokens_details", {}) or {}
        out_details = u.get("output_tokens_details", {}) or {}
        cached = int(details.get("cached_tokens", 0) or 0)
        total_in = int(u.get("input_tokens", 0) or 0)
        return Usage(
            input_tokens_uncached=max(0, total_in - cached),
            input_tokens_cached=cached,
            cache_write_tokens=int(details.get("cache_write_tokens", 0) or 0),
            reasoning_tokens=out_details.get("reasoning_tokens"),
            output_tokens=int(u.get("output_tokens", 0) or 0),
        )

    def refusal(self, resp: ProviderResponse) -> tuple[bool, str | None]:
        for item in resp.body.get("output", []) or []:
            for part in item.get("content", []) or []:
                if part.get("type") == "refusal":
                    return True, part.get("refusal", "unspecified")[:120]
        return False, None

    def truncated(self, resp: ProviderResponse) -> bool:
        if resp.body.get("status") == "incomplete":
            reason = (resp.body.get("incomplete_details") or {}).get("reason")
            return reason == "max_output_tokens"
        return False

    def resolved_model_version(self, resp: ProviderResponse) -> str | None:
        return resp.body.get("model")

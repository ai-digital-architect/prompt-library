"""Anthropic adapters.

Two profiles, because the two generations want genuinely different prompts:

  anthropic-claude5   Fable 5, Opus 5, Sonnet 5
  anthropic-claude4x  Opus 4.8, Opus 4.7 (derived), Opus 4.6

Sources: templates 13, 21, 22 (Claude 5) and 12, 14 (Claude 4.x) in the
read-only prompt library. Those templates are the upstream authority; this file
transcribes their rendering rules. Never edit them from here — when one changes
upstream, bump `version` below and record it in CHANGELOG.md.

The Claude 5 rule that matters most: DELETE BEFORE YOU ADD. Anthropic removed
over 80% of Claude Code's system prompt for this generation with no eval loss.
Verification scaffolding, progress-summary scaffolding, severity filters and
enumerated style prohibitions are all net-negative here — which is exactly why
they sit in the prohibition list rather than in this renderer.
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

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


def _xml(tag: str, body: str) -> str:
    return f"<{tag}>\n{body.strip()}\n</{tag}>"


class _AnthropicBase(ModelAdapter):
    provider = "anthropic"

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": resolve_key("anthropic"),
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        }

    # -------------------------------------------------------------- response
    def extract_text(self, resp: ProviderResponse) -> str:
        parts = []
        for block in resp.body.get("content", []) or []:
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)

    def usage(self, resp: ProviderResponse) -> Usage:
        u = resp.body.get("usage", {}) or {}
        return Usage(
            input_tokens_uncached=int(u.get("input_tokens", 0) or 0),
            input_tokens_cached=int(u.get("cache_read_input_tokens", 0) or 0),
            cache_write_tokens=int(u.get("cache_creation_input_tokens", 0) or 0),
            # Anthropic does not return raw chain of thought, and thinking tokens
            # are counted inside output_tokens. Imputing a separate figure would
            # double-count, so this stays None.
            reasoning_tokens=None,
            output_tokens=int(u.get("output_tokens", 0) or 0),
        )

    def refusal(self, resp: ProviderResponse) -> tuple[bool, str | None]:
        # Classifier declines arrive as HTTP 200 with stop_reason "refusal".
        # A harness that only checks status codes scores these as empty answers.
        if resp.status == 200 and resp.body.get("stop_reason") == "refusal":
            cat = (resp.body.get("stop_details") or {}).get("category")
            return True, cat or "unspecified"
        return False, None

    def truncated(self, resp: ProviderResponse) -> bool:
        return resp.body.get("stop_reason") == "max_tokens"

    def resolved_model_version(self, resp: ProviderResponse) -> str | None:
        return resp.body.get("model")

    # ----------------------------------------------------------- rendering
    def _system(self, ir: PromptIR, model: Model) -> str:
        raise NotImplementedError

    def _user(self, ir: PromptIR) -> str:
        blocks = [ir.objective.strip()]
        q = questions_text(ir)
        if q:
            blocks.append(q)
        refs = reference_text(ir)
        if refs:
            inner = "\n".join(_xml(_ref_tag(kind), content) for _label, kind, content in refs)
            blocks.append(_xml("reference_material", inner))
        return "\n\n".join(blocks)

    def _base_body(self, ir: PromptIR, model: Model, profile: RunProfile,
                   system: str, user: str) -> dict[str, Any]:
        max_out = min(
            profile.max_output_tokens or model.max_output_tokens,
            int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )
        body: dict[str, Any] = {
            "model": model.id,
            "max_tokens": max_out,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if profile.effort:
            # effort lives inside output_config, not at the top level.
            body.setdefault("output_config", {})["effort"] = profile.effort

        schema = json_schema_for_response(ir, SKILL_ROOT)
        if schema:
            body.setdefault("output_config", {})["format"] = {
                "type": "json_schema",
                "schema": schema,
            }
        # Never set temperature / top_p / top_k / budget_tokens: all return a 400
        # on this generation, and their presence signals a stale adapter.
        return body


def _ref_tag(kind: str) -> str:
    return {
        "code": "code", "tests": "tests", "spec": "spec", "schema": "schema",
        "logs": "logs", "config": "config", "graph_excerpt": "graph",
        "rubric": "rubric", "mockup": "mockup",
    }.get(kind, "doc")


class AnthropicClaude5Adapter(_AnthropicBase):
    """Fable 5 / Opus 5 / Sonnet 5.

    Lean XML scaffold. No verification block, no progress-summary scaffolding, no
    enumerated style prohibitions — all of them measurably hurt this generation.
    Depth is steered with `output_config.effort`, never with prose.

    One family-specific nuance the templates call out: Sonnet 5 follows
    instructions literally and will not infer the scope of a requirement, so the
    scope statement is rendered as its own guideline line rather than folded into
    the objective.
    """

    id = "anthropic-claude5"
    version = "1.0.0"

    def _system(self, ir: PromptIR, model: Model) -> str:
        role = ir.role or {}
        persona = role.get("persona") or "a principal engineer"
        domain = role.get("domain") or "enterprise software systems"
        head = f"You are {persona}, an expert in {domain}."

        ctx = ir.context or {}
        ctx_lines = []
        if ctx.get("why_this_matters"):
            ctx_lines.append(ctx["why_this_matters"])
        if ctx.get("audience"):
            ctx_lines.append(f"Audience: {ctx['audience']}.")
        for k in ctx.get("known_constraints", []) or []:
            ctx_lines.append(f"- {k}")

        objectives = "\n".join(f"{i}. {c}" for i, c in enumerate(ir.success_criteria, 1))

        guidelines = [
            f"Scope: {ir.scope}",
            "Report coverage, not a shortlist. Include findings you are uncertain about, "
            "each with its own confidence and severity — a separate pass filters them.",
            "Cite file, symbol and line range for every finding. Distinguish what you "
            "confirmed from what you inferred.",
            "Match any code you write to the conventions already present in the reference "
            "material — its error-handling idiom, naming, and comment density.",
        ]
        if model.id == "claude-sonnet-5":
            guidelines.append(
                "Apply every requirement above to the whole corpus in scope, not only to "
                "the first item you examine."
            )
        b = budget_text(ir)
        if b:
            guidelines.append(b)

        parts = [head]
        if ctx_lines:
            parts.append(_xml("context", "\n".join(ctx_lines)))
        parts.append(_xml("objectives", objectives))
        parts.append(_xml("guidelines", "\n".join(f"- {g}" for g in guidelines)))
        parts.append(_xml("output_format", response_contract_text(ir)))
        return "\n\n".join(parts)

    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest:
        system = self._system(ir, model)
        user = self._user(ir)
        body = self._base_body(ir, model, profile, system, user)
        # Thinking is adaptive and on by default across this generation; the field
        # is omitted entirely. On Fable 5 both disabling and budgeting return 400.
        return ProviderRequest(
            model_id=model.id, provider=self.provider, url=API_URL,
            headers=self._headers(), body=body,
            rendered_prompt=system + "\n\n---\n\n" + user,
            structured_output_mechanism="output_config.format",
            max_output_ceiling=int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )


class AnthropicClaude4xAdapter(_AnthropicBase):
    """Opus 4.8 / 4.7 (derived) / 4.6.

    This generation is conservative about reaching for tools and benefits
    measurably from explicit capability triggers ("call this when…"). Those
    triggers come from the canonical tool IR's `when_to_use` field, so every
    adapter renders the same trigger text and the help is not a fairness leak.

    Opus 4.6 also accepts an explicit thinking-instructions block, which later
    generations penalize. `depth_by_prose` is therefore declared as an adapter
    exemption in config/lanes.yaml rather than being silently allowed — the
    waiver appears in the fairness verdict's warnings so a reviewer sees it.
    """

    id = "anthropic-claude4x"
    version = "1.0.0"

    def _system(self, ir: PromptIR, model: Model) -> str:
        role = ir.role or {}
        persona = role.get("persona") or "a principal engineer"
        domain = role.get("domain") or "enterprise software systems"
        parts = [f"You are {persona}, an expert in {domain}."]

        ctx = ir.context or {}
        ctx_lines = [ctx.get("why_this_matters") or ""]
        if ctx.get("audience"):
            ctx_lines.append(f"Audience: {ctx['audience']}.")
        ctx_lines += [f"- {k}" for k in (ctx.get("known_constraints") or [])]
        ctx_lines = [l for l in ctx_lines if l]
        if ctx_lines:
            parts.append(_xml("context", "\n".join(ctx_lines)))

        parts.append(_xml("objectives", "\n".join(
            f"{i}. {c}" for i, c in enumerate(ir.success_criteria, 1))))

        if model.id == "claude-opus-4-6":
            parts.append(_xml("thinking_instructions",
                              "Reason through the system's structure before writing findings. "
                              "Identify assumptions that would invalidate a conclusion, and "
                              "acknowledge uncertainty rather than masking it."))

        guidelines = [
            f"Scope: {ir.scope}",
            "Report EVERY issue you find, including low-severity and uncertain ones, each "
            "with a confidence level and an estimated severity. A separate pass filters them.",
            "Cite file, function and line range. Distinguish confirmed from theoretical.",
            "For minor choices, pick a reasonable option and note it rather than asking.",
        ]
        b = budget_text(ir)
        if b:
            guidelines.append(b)
        parts.append(_xml("guidelines", "\n".join(f"- {g}" for g in guidelines)))

        triggers = [t.get("when_to_use") for t in ir.tools if t.get("when_to_use")]
        if triggers:
            parts.append(_xml("capability_triggers", "\n".join(f"- {t}" for t in triggers)))

        parts.append(_xml("output_format", response_contract_text(ir)))
        return "\n\n".join(parts)

    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest:
        system = self._system(ir, model)
        user = self._user(ir)
        body = self._base_body(ir, model, profile, system, user)
        # 4.x wants the thinking block stated explicitly; budget_tokens is
        # deprecated on 4.6 and rejected from 4.7 onward, so adaptive only.
        if model.raw.get("thinking", {}).get("explicit_thinking_block"):
            body["thinking"] = {"type": "adaptive"}
        return ProviderRequest(
            model_id=model.id, provider=self.provider, url=API_URL,
            headers=self._headers(), body=body,
            rendered_prompt=system + "\n\n---\n\n" + user,
            structured_output_mechanism="output_config.format",
            max_output_ceiling=int(ir.budget.get("max_output_tokens") or model.max_output_tokens),
        )

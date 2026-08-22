"""Pricing oracle.

Cost is the one benchmark number that is trivially auditable and trivially
wrong. This module computes it from the BILLED token categories a provider
returns, applies long-prompt surcharges and cache-write multipliers, flags
imputed and promotional rates, and refuses to silently paper over a missing
rate.

The reported headline is COLD cost — cache-write inclusive, no cache reads —
because that is the honest marginal cost of a genuinely new task. Warm cost is
an operational secondary number; reporting warm as the headline makes every
model look cheaper than it is for novel work, and makes providers with cheap
cache reads look better than they are.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any

from .util import load_config

DEFAULT_PRICING = "config/pricing.yaml"
MTOK = 1_000_000.0


@dataclass
class Usage:
    input_tokens_uncached: int = 0
    input_tokens_cached: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int | None = None   # None where the provider does not expose it
    output_tokens: int = 0
    grounding_queries: int = 0

    def total_input(self) -> int:
        return self.input_tokens_uncached + self.input_tokens_cached + self.cache_write_tokens


@dataclass
class Cost:
    usd: float
    flags: list[str] = field(default_factory=list)
    breakdown: dict[str, float] = field(default_factory=dict)
    pricing_table_version: str = ""
    cache_state: str = "cold"


class PricingOracle:
    def __init__(self, path: str = DEFAULT_PRICING, today: _dt.date | None = None):
        data = load_config(path)
        self.version: str = data.get("pricing_table_version", "unknown")
        self.verified_on = data.get("verified_on")
        self.staleness_warn_days = int(data.get("staleness_warn_days", 45))
        self.models: dict[str, dict[str, Any]] = data.get("models", {})
        self.accounting = data.get("accounting", {})
        self._today = today or _dt.date.today()

    # ---------------------------------------------------------------- checks
    def staleness_days(self) -> int | None:
        if not self.verified_on:
            return None
        try:
            v = _dt.date.fromisoformat(str(self.verified_on))
        except ValueError:
            return None
        return (self._today - v).days

    def is_stale(self) -> bool:
        d = self.staleness_days()
        return d is not None and d > self.staleness_warn_days

    # ----------------------------------------------------------------- rates
    def rates(self, model_id: str) -> dict[str, Any] | None:
        return self.models.get(model_id)

    def _effective_rates(self, model_id: str) -> tuple[dict[str, Any], list[str]]:
        entry = self.models.get(model_id)
        flags: list[str] = []
        if entry is None:
            raise KeyError(
                f"no pricing entry for '{model_id}'. Add one to config/pricing.yaml "
                f"rather than letting the harness invent a number."
            )
        rates = dict(entry)
        if entry.get("imputed"):
            flags.append("imputed")
        promo = entry.get("promotional")
        if promo:
            expires = promo.get("expires")
            active = True
            if expires:
                try:
                    active = self._today <= _dt.date.fromisoformat(str(expires))
                except ValueError:
                    active = False
            if active:
                rates["input_per_mtok"] = promo.get("input_per_mtok", rates.get("input_per_mtok"))
                rates["output_per_mtok"] = promo.get("output_per_mtok", rates.get("output_per_mtok"))
                flags.append("promotional")
        if self.is_stale():
            flags.append("stale_pricing")
        return rates, flags

    # ------------------------------------------------------------------ cost
    def cost(
        self,
        model_id: str,
        usage: Usage,
        cache_state: str = "cold",
        session_input_tokens: int | None = None,
    ) -> Cost:
        """Compute billed cost.

        `session_input_tokens` exists for OpenAI's long-prompt surcharge, which
        applies to the whole SESSION once crossed rather than to the single
        offending call. Each benchmark trial is a single-turn session, so the
        caller may omit it and the per-call total is the session total. A
        multi-turn harness built on this module must pass the running session
        figure, or it will understate cost exactly where the surcharge bites.
        """
        rates, flags = self._effective_rates(model_id)
        in_rate = rates.get("input_per_mtok")
        out_rate = rates.get("output_per_mtok")
        if in_rate is None or out_rate is None:
            return Cost(usd=float("nan"), flags=flags + ["no_published_rate"],
                        pricing_table_version=self.version, cache_state=cache_state)

        in_mult, out_mult = 1.0, 1.0
        lps = rates.get("long_prompt_surcharge") or {}
        threshold = lps.get("threshold_input_tokens")
        if threshold:
            measure = session_input_tokens if session_input_tokens is not None else usage.total_input()
            if measure > threshold:
                in_mult = float(lps.get("input_multiplier", 1.0))
                out_mult = float(lps.get("output_multiplier", 1.0))
                flags.append("long_prompt_surcharge")

        cache_read_rate = rates.get("cache_read_per_mtok")
        cache_write_mult = float(rates.get("cache_write_multiplier", 1.0))

        b: dict[str, float] = {}
        b["input_uncached"] = usage.input_tokens_uncached / MTOK * in_rate * in_mult

        if cache_state == "cold":
            # Cold: nothing is served from cache. Anything the provider reported
            # as cached is billed as a cache WRITE at its multiplier, because on
            # a genuinely new task that is what actually happens.
            # Sum, do not choose. Anthropic returns cache_creation and cache_read
            # together; `or` short-circuits and bills one of them nowhere, which
            # made cold cost come out BELOW warm — inverting the premise that cold
            # is the honest upper bound.
            written = usage.cache_write_tokens + usage.input_tokens_cached
            b["cache_write"] = written / MTOK * in_rate * cache_write_mult * in_mult
            b["input_cached"] = 0.0
        else:
            if cache_read_rate is None:
                # No published cached rate: bill at uncached and say so, rather
                # than quietly assuming a discount.
                b["input_cached"] = usage.input_tokens_cached / MTOK * in_rate * in_mult
                flags.append("imputed_cache_rate")
            else:
                b["input_cached"] = usage.input_tokens_cached / MTOK * cache_read_rate * in_mult
            b["cache_write"] = usage.cache_write_tokens / MTOK * in_rate * cache_write_mult * in_mult

        # Reasoning tokens: billed as output where the provider exposes them.
        # Where it does not, they are already inside output_tokens — adding an
        # imputed figure would double-count.
        b["output"] = usage.output_tokens / MTOK * out_rate * out_mult

        grounding = rates.get("grounding") or {}
        if usage.grounding_queries and grounding.get("per_1000_queries_after") is not None:
            b["grounding"] = usage.grounding_queries / 1000.0 * float(grounding["per_1000_queries_after"])
            flags.append("grounding_billed_separately")

        total = sum(b.values())
        return Cost(usd=round(total, 6), flags=sorted(set(flags)), breakdown=b,
                    pricing_table_version=self.version, cache_state=cache_state)

    # ----------------------------------------------------------- estimation
    def estimate(self, model_id: str, est_input: int, est_output: int) -> Cost:
        """Pre-flight estimate for `mb.py plan --estimate`. Deliberately cold."""
        return self.cost(model_id, Usage(input_tokens_uncached=est_input, output_tokens=est_output),
                         cache_state="cold")


def cost_per_correct_finding(cold_cost_usd: float, credited_true_positives: float) -> float | None:
    """The primary operational metric.

    Returns None rather than infinity when nothing was found: a model that
    produced no correct findings has an undefined cost-per-finding, and printing
    `inf` invites it being read as a very large but real number.
    """
    if credited_true_positives <= 0:
        return None
    return round(cold_cost_usd / credited_true_positives, 6)

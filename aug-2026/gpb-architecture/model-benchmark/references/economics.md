# Economics

Cost is the one benchmark number that is trivially auditable and trivially wrong.

## Three standing rules

1. **Never compare token counts across providers as a capability metric.**
   Tokenizers differ materially — Claude Sonnet 5 emits roughly 30% more tokens
   than Sonnet 4.6 for identical text. Compare cost and wall-clock. Report tokens
   only within a provider family.
2. **Price from a versioned table with an effective date**, computed over billed
   token categories returned by the provider, not from local token counting.
3. **Report cold cost as the headline.** Cold is the honest marginal cost of a
   genuinely new task; warm is an operational secondary number. Leading with warm
   makes every model look cheaper than it is for novel work, and flatters
   providers with cheap cache reads.

## Billed categories

```
input_tokens_uncached
input_tokens_cached
cache_write_tokens
reasoning_tokens      # only where the provider exposes them — never imputed
output_tokens
```

Anthropic counts thinking inside `output_tokens`, so `reasoning_tokens` is `None`
there. Recording `None` says "not observable"; imputing a figure would
double-count and invent a comparison that does not exist.

## Things that move the answer

| Effect | Where it bites |
| --- | --- |
| **Long-prompt surcharge** | GPT-5.6 tiers bill the whole **session** at 2× input / 1.5× output above 272K input tokens — not just the offending call. Gemini 3.1 Pro moves to a higher band above 200K prompt tokens. |
| **Cache-write multiplier** | GPT-5.6 cache writes bill at 1.25× uncached input, attributed to the first (cold) run. |
| **Cached-input tiers** | Vary by an order of magnitude across the GPT-5.6 family ($0.50 / $0.25 / $0.10 per MTok). Static-prefix design is the dominant cost lever on a high-volume workload. |
| **Promotional pricing** | Claude Sonnet 5 carries introductory pricing through 2026-08-31. Figures computed before and after are not comparable, and the report footnotes any that depend on it. |
| **Grounding and tool charges** | Gemini Search grounding is billed separately from tokens (free tier, then per-1000-queries). Folding it into token cost makes Gemini look cheaper than it is; it is a line item. |
| **Context-cache storage** | Gemini charges per MTok per hour of storage. Relevant when a corpus is cached across a long study. |
| **Imputed rates** | Where no separate rate was published (Opus 4.7, Opus 4.6), the table inherits a sibling's and marks `imputed: true`. Every figure derived from it is labelled everywhere it appears. |

## Published metrics

| Metric | Definition |
| --- | --- |
| Cold cost / task | Full price, cache-write inclusive, no cache reads |
| Warm cost / task | Steady state with a populated prefix cache |
| **Cost per correct finding** | Cold cost ÷ credited true positives — the primary operational number |
| Cost per correct finding at iso-quality | Cost to reach a declared quality threshold; blank when unreachable |
| p50 / p95 latency | Wall-clock at the harness boundary |
| Tokens per credited finding | **Within a provider family only** |

Cost per correct finding returns `undefined` rather than infinity when a model
found nothing correct. Printing `inf` invites it being read as a very large but
real number.

## Keeping the table honest

```bash
python3 mb.py doctor        # warns when the table is older than staleness_warn_days
```

Re-verify against vendor pricing pages before every leaderboard round. A stale
table raises a `STALE_PRICING` flag that propagates into the report footnotes, so
a reader can see that a cost figure may be out of date rather than trusting it.

## The utility question

It is tempting to publish a single number:

```
             quality × reliability
Utility = ─────────────────────────
           normalized cost × latency
```

Don't make it the canonical leaderboard score. Weighting cost against quality is a
business decision, not a measurement, and burying it inside an index hides the
choice from the people entitled to make it.

Publish the **Pareto frontier** and let each consumer apply their own budget:

```
QUALITY
  ^
  |                ● Model A
  |        ● Model B
  |                         ● Model C
  +----------------------------------> COST
```

The frontier answers questions a scalar cannot: where a model stops improving,
where two models cross, and which budget points a model can reach at all.

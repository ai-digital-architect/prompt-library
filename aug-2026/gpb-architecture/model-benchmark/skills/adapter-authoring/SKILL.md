---
name: adapter-authoring
description: >
  Add or revise a model adapter — a new model, a new provider, or a prompt-rendering
  change. Covers the adapter SPI, what belongs in the free set versus the invariant
  set, the per-family rendering rules transcribed from the prompt-template library,
  and how to prove an adapter did not smuggle in semantic help.
parent: model-benchmark
---

# Adapter authoring

An adapter's job is to render one canonical task the way a particular model wants
to receive it. Its constraint is that it may change **how** the task is asked and
never **what** is asked.

That line is the whole basis of the Optimized lane. If an adapter can quietly add
a hint, drop a requirement, or widen a tool's parameters, then "model A beats
model B" means "A's adapter is better", and nobody can tell which from the
results.

## The line, precisely

**Free — an adapter is expected to differ here.** This is the point of the lane.

- prompt syntax and delimiters (XML tags, Markdown sections, role blocks)
- which container each IR section lands in (system / developer / user / system_instruction)
- section ordering (Gemini wants context first and the instruction last; Claude wants the full spec up front)
- reasoning configuration (`output_config.effort`, `reasoning.effort`, `reasoning.mode`, `thinking_level`)
- structured-output mechanism (`output_config.format`, Structured Outputs, `response_mime_type` + schema)
- verbosity control and length steering blocks
- token ceilings within the IR budget, streaming, cache layout
- tool schema **presentation**

**Invariant — touching any of these fails the run before it is billed.**

- the objective, scope and success criteria (semantic content)
- required output fields and the response schema version
- the evidence budget
- tool **semantics**: names, parameter names, types, enum values, required flags, constraints
- corpus, commit, mutation id, graph version and hash
- trial plan and ordering seed
- the prohibition list

## The SPI

```python
class ModelAdapter:
    id: str          # "anthropic-claude5"
    version: str     # semver — bump on ANY rendering change
    provider: str

    def compile(self, ir: PromptIR, model: Model, profile: RunProfile) -> ProviderRequest: ...
    def extract_text(self, resp: ProviderResponse) -> str: ...
    def usage(self, resp: ProviderResponse) -> Usage: ...
    def refusal(self, resp: ProviderResponse) -> tuple[bool, str | None]: ...
    def truncated(self, resp: ProviderResponse) -> bool: ...
    def resolved_model_version(self, resp: ProviderResponse) -> str | None: ...
```

`invoke()` is inherited: plain HTTPS through the standard library. That is
deliberate. Provider SDKs move faster than a benchmark harness should, and an SDK
upgrade silently changing a default is exactly the class of uncontrolled variable
this design exists to eliminate.

### `refusal()` deserves the most care

It is a two-line method and the most consequential one in the file. A safety
refusal that arrives as HTTP 200 with an empty-looking body is indistinguishable
from a successful empty answer unless this method catches it — and scoring it as
recall zero systematically penalizes classifier-bearing models on the security
suite. Get this wrong and the leaderboard produces a confident, wrong strategic
conclusion.

Shapes currently handled:

| Provider | Refusal shape |
| --- | --- |
| Anthropic | HTTP 200, `stop_reason: "refusal"`, category in `stop_details.category` |
| OpenAI | a content part with `type: "refusal"` inside `output` |
| Google | `promptFeedback.blockReason`, or a candidate `finishReason` of `SAFETY` / `BLOCKLIST` / `PROHIBITED_CONTENT` |

### `usage()` must not invent numbers

Report only what the provider returns. In particular, `reasoning_tokens` is
`None` where the provider does not expose it — never imputed. Anthropic counts
thinking inside `output_tokens`, so adding a separate figure would double-count;
recording `None` says "not observable here", which is the truth.

## Per-family rendering rules

These are transcribed from the read-only `model-prompt-templates/` library in the
parent folder. **Never edit those templates.** When one changes upstream, update
the adapter, bump its `version`, and record it in `CHANGELOG.md`.

### `anthropic-claude5` — Fable 5, Opus 5, Sonnet 5

Lean XML scaffold. The governing rule for this generation is *delete before you
add*: Anthropic removed over 80% of Claude Code's system prompt with no eval loss,
and verification scaffolding, progress-summary scaffolding, severity filters and
enumerated style prohibitions are all net-negative. That is why they sit in the
prohibition list rather than in the renderer.

- thinking is adaptive and on by default — omit the field entirely
- on Fable 5, both disabling thinking and `budget_tokens` return a 400
- depth is `output_config.effort`, never prose
- machine-readable output via `output_config.format`; assistant-turn prefills return a 400
- **Sonnet 5 nuance**: it follows instructions literally and will not infer the
  scope of a requirement, so the renderer states scope as its own guideline line.
  Its tokenizer also emits ~30% more tokens for identical text than Sonnet 4.6 —
  which is a budgeting fact, never a capability comparison.

### `anthropic-claude4x` — Opus 4.8, 4.7 (derived), 4.6

- thinking is stated explicitly: `thinking: {"type": "adaptive"}`
- `budget_tokens` is deprecated on 4.6 and rejected from 4.7 onward
- this generation is **conservative about reaching for tools** and improves
  measurably with explicit "call this when…" triggers. Those come from the
  canonical tool IR's `when_to_use` field, so every adapter renders the same
  trigger and the help is not a fairness leak.
- Opus 4.6 accepts an explicit thinking-instructions block that later generations
  penalize. That is why `depth_by_prose` carries an adapter exemption in
  `config/lanes.yaml` — the waiver shows up in the fairness verdict's warnings so
  a reviewer sees it rather than it being silently allowed.
- **Opus 4.7 has no upstream template.** Its profile is derived from 4.8, which
  the library states shares its API surface. The registry marks it
  `derived: true` and every report footnotes it.

### `openai-gpt56` — Sol, Terra, Luna

Markdown-sectioned developer/user messages via the Responses API.

- migrate by shrinking: OpenAI's own testing found leaner prompts raised eval
  scores ~10–15% while cutting tokens 41–66% on this generation. Say each thing
  once.
- `reasoning.mode: "pro"` is documented for **Sol only**. The adapter refuses to
  set it on Terra and Luna rather than risking a silent behavioural difference
  that would surface as a capability gap.
- length is `text.verbosity`, not prose
- static content first, dynamic last — cached input is up to 10× cheaper and cache
  writes bill at 1.25×, so ordering is worth real money across a large study
- above 272K input tokens the whole **session** bills at 2× input / 1.5× output

### `google-gemini3x` — Gemini 3.6 Flash, Gemini 3 Pro (retired)

- **context first, instruction last** — the ordering Google's long-context
  guidance asks for, and one of the clearest examples of legitimate free-set
  variation
- `temperature` / `top_p` / `top_k` are deprecated and **silently ignored**, with
  HTTP 400 promised in future versions. Silently ignored is the dangerous case: a
  harness that sets them believes it has control it does not have.
- a request may **not** end on a model-role turn; prefill-style steering must move
  into `system_instruction` or the response schema
- depth is `thinking_level` string values, not `thinking_budget`
- the response schema needs reducing to Gemini's accepted subset — an unsupported
  keyword can cause the whole schema to be rejected, which would surface as a
  `SCHEMA_INVALID` disposition and be misread as a model weakness

## Adding a new model to an existing family

Usually registry-only:

1. Add the entry to `config/models.yaml` with a `template_ref` citing the upstream
   template. If no template exists, mark `derived: true`, name `derived_from`, and
   write a `template_note` explaining the derivation — the registry validator
   rejects a derived profile without one.
2. Add a pricing entry to `config/pricing.yaml` with an `effective_from`. If you
   have to inherit a rate, mark `imputed: true` and name `imputed_from`.
3. `python3 mb.py doctor` — the registry self-check runs here.
4. `python3 mb.py compile --suite … --all-models --dry-run` and confirm the new
   model joins the existing `semantic_digest` group.

## Adding a new provider

1. New module in `scripts/mbcore/adapters/`, subclassing `ModelAdapter`.
2. Register it in `adapters/__init__.py`.
3. Add its credential env var names to `PROVIDER_ENV` and `PRIMARY_KEY` in
   `mbcore/secrets.py`. Nothing outside that list crosses into a provider-scoped
   subprocess environment — a key intended for one provider should never be
   visible to another adapter's tooling.
4. Implement `refusal()` against the provider's actual refusal shape before you
   run anything real.
5. Record a cassette so the pipeline is testable without spend.

## Proving the adapter behaved

```bash
python3 mb.py compile --suite suites/security-v1.yaml --task SEC-0001 \
    --all-models --show my-new-model
```

Read three things:

1. **`fairness` column** — `PASS` on every row.
2. **`semantic` column** — one digest shared by every model. Different digests
   mean different questions.
3. **The rendered prompt itself.** The validator is a lint, not a proof. It
   catches dropped requirements and known-harmful constructs; it cannot tell you
   whether your rendering is *good*. Read it once with fresh eyes and ask whether
   a careful engineer given only this text would produce the answer the oracle
   expects.

Then bump `version` and add a `CHANGELOG.md` entry. Adapter version is stamped
into every manifest, and a rendering change without a version bump makes two
rounds silently incomparable.

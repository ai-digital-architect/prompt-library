---
post_title: "Current AI Model Lists: OpenAI, Anthropic, and Google"
author1: "Prompt Library Team"
post_slug: "current-model-list"
microsoft_alias: "promptlibrary"
featured_image: "https://learn.microsoft.com/en-us/azure/ai-services/openai/media/overview/openai-overview.png"
categories:
  - "AI"
  - "Developer Tools"
tags:
  - "prompt-engineering"
  - "llm"
  - "model-templates"
  - "ai-assisted-engineering"
  - "model-lineup"
  - "reference"
ai_note: "Content created with AI assistance."
summary: >
  Source-of-truth lineup of currently listed OpenAI, Anthropic, and Google
  models with API model IDs, context windows, pricing, and migration notes,
  verified against each provider's official documentation.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

**Date:** June 12, 2026 — *all three provider sections re-scanned and updated July 25, 2026*

This document summarizes the currently listed models from OpenAI, Anthropic, and Google, based on the model information referenced in the prior response.

---

## OpenAI

### Frontier / General Models

| Model         | API Model ID     | Context / Max output | Pricing (in/out/cached in per MTok) | Notes                                                                 |
| ------------- | ---------------- | -------------------- | ----------------------------------- | --------------------------------------------------------------------- |
| GPT-5.6 Sol   | `gpt-5.6-sol`    | 1,050,000 / 128K     | $5.00 / $30.00 / $0.50              | Flagship; `gpt-5.6` and `gpt-5` alias to it; `reasoning.mode: "pro"` documented; knowledge cutoff Feb 16, 2026 |
| GPT-5.6 Terra | `gpt-5.6-terra`  | 1,050,000 / 128K     | $2.50 / $15.00 / $0.25              | Mid-tier; exactly half Sol's price; same context, output, and tool surface |
| GPT-5.6 Luna  | `gpt-5.6-luna`   | 1,050,000 / 128K     | $1.00 / $6.00 / $0.10               | Fast/budget; highest rate-limit ceiling (Tier 5: 30,000 RPM / 180M TPM) |
| GPT-5.5       | `gpt-5.5`        | 1,050,000 / 128K     | $5.00 / $30.00 / $0.50              | No longer listed on the models page — prior flagship                  |
| GPT-5.4 family | `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano` | 1,050,000 / 128K | see prior templates    | No longer listed on the models page                                   |

### Specialized Models

| Category                     | Models Listed                                                               |
| ---------------------------- | --------------------------------------------------------------------------- |
| Image                        | `gpt-image-2`                                                               |
| Realtime voice / translation | `gpt-realtime-2.1`, `gpt-realtime-2.1-mini`, `gpt-realtime-2`, `gpt-realtime-translate`, `gpt-realtime-1.5`, `gpt-realtime-mini` (deprecated) |
| Speech generation            | GPT-4o mini TTS — marked deprecated                                         |
| Transcription                | GPT-Realtime-Whisper, GPT-4o Transcribe, GPT-4o mini Transcribe             |

### Notes

OpenAI’s documentation now lists only the three GPT-5.6 variants and tells developers: “If you’re not sure where to start, use GPT-5.6 Sol, our flagship model for complex reasoning and coding.”

All three tiers share a 1,050,000-token context window, a 128K output ceiling,
a February 16, 2026 knowledge cutoff, and the same built-in tool surface (web
search, file search, code interpreter, computer use, image generation, hosted
shell, apply patch, skills, MCP, tool search). None support fine-tuning.
Requests above 272K input tokens bill at 2× input and 1.5× output for the
session, and cache writes bill at 1.25× uncached input.

`reasoning.effort` accepts a model-dependent subset of `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, and `max`. `reasoning.mode` (`standard` / `pro`) is an independent axis and is documented for `gpt-5.6-sol`; it is not confirmed for Terra or Luna. Programmatic Tool Calling — the model writing JavaScript to orchestrate tool calls — is supported on GPT-5.4 and later.

**Deprecations:** `gpt-5-2025-08-07`, `gpt-5-mini-2025-08-07`, and `gpt-5-nano-2025-08-07` shut down December 11, 2026, with `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` named as their respective replacements. No retirement date has been announced for GPT-5.4 or GPT-5.5, but neither appears on the models page.

**Source:** [OpenAI model documentation](https://developers.openai.com/api/docs/models), [model guidance](https://developers.openai.com/api/docs/guides/latest-model), [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning), and [deprecations](https://developers.openai.com/api/docs/deprecations) — verified July 25, 2026.

---

## Anthropic

| Model                 | API Model ID                                     | Context / Max output | Pricing (in/out per MTok) | Notes                                                              |
| --------------------- | ------------------------------------------------ | -------------------- | ------------------------- | ------------------------------------------------------------------ |
| Claude Fable 5        | `claude-fable-5`                                 | 1M / 128K            | $10 / $50                 | **Flagship** — most capable widely released model; adaptive thinking always on; 30-day retention required (no ZDR); retires no sooner than Jun 9, 2027 |
| Claude Mythos 5       | `claude-mythos-5`                                | 1M / 128K            | $10 / $50                 | Limited availability via Project Glasswing; Fable 5 capabilities without safety classifiers |
| Claude Mythos Preview | `claude-mythos-preview`                          | —                    | —                         | Invitation-only research preview                                   |
| Claude Opus 5         | `claude-opus-5`                                  | 1M / 128K            | $5 / $25                  | Complex agentic coding and enterprise work; below Fable 5; adaptive thinking on by default (disable only at effort ≤ `high`); knowledge cutoff May 2026; retires no sooner than Jul 24, 2027 |
| Claude Sonnet 5       | `claude-sonnet-5`                                | 1M / 128K            | $3 / $15                  | Speed/intelligence balance; adaptive thinking on by default; new tokenizer (~30% more tokens); intro pricing $2 / $10 through Aug 31, 2026 |
| Claude Haiku 4.5      | `claude-haiku-4-5` / `claude-haiku-4-5-20251001` | 200K / 64K           | $1 / $5                   | Fastest current Claude model; no Haiku 5 exists; **retires no sooner than Oct 15, 2026** — nearest retirement in the lineup |
| Claude Opus 4.8       | `claude-opus-4-8`                                | 1M / 128K            | $5 / $25                  | Prior generation, delisted from the current models table — superseded by Opus 5; retires no sooner than May 28, 2027 |
| Claude Sonnet 4.6     | `claude-sonnet-4-6`                              | 1M / 64K             | $3 / $15                  | Prior generation, delisted from the current models table — superseded by Sonnet 5; retires no sooner than Feb 17, 2027 |

### Notes

Anthropic’s documentation states that current Claude models support text and image input, text output, multilingual capabilities, and vision.

**Claude 5 generation (July 2026):** Opus 5 and Sonnet 5 join Fable 5 as the current
lineup, with Haiku 4.5 unchanged as the fast tier. Anthropic designates **Fable 5**
its most capable widely released model — the flagship is not in the Opus line.
Opus 4.5–4.8 and Sonnet 4.5–4.6 remain callable but no longer appear in the
current models table. Note also that `temperature`, `top_p`, and `top_k` are
deprecated on **Opus 4.7 and later**, not only on the Claude 5 generation. Across all three, `temperature` / `top_p` / `top_k`, `budget_tokens`, and
assistant-turn prefills return a 400; use `output_config.effort`
(`low`/`medium`/`high`/`xhigh`/`max`, default `high`) and structured outputs instead.
The prompt-caching minimum drops from 1,024 to 512 tokens, and the beta headers
`effort-2025-11-24`, `interleaved-thinking-2025-05-14`,
`token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`, and
`fine-grained-tool-streaming-2025-05-14` are now GA and should be removed.

**Source:** [Anthropic Claude model documentation](https://docs.anthropic.com/en/docs/about-claude/models/overview)

---

## Google Gemini

### Gemini 3 / Current Generation

| Model                     | API Model ID             | Status  | Context / Max output    | Pricing (in/out per MTok) |
| ------------------------- | ------------------------ | ------- | ----------------------- | ------------------------- |
| Gemini 3.6 Flash          | `gemini-3.6-flash`       | Stable  | 1,048,576 / 65,536      | $1.50 / $7.50             |
| Gemini 3.1 Pro            | `gemini-3.1-pro-preview` | Preview | 1M / 64K                | $2.00 / $12.00 (≤200K prompt); $4.00 / $18.00 above |
| Gemini 3.5 Flash          | `gemini-3.5-flash`       | Stable (superseded) | 1M / 64K    | $1.50 / $9.00             |
| Gemini 3.5 Flash-Lite     | `gemini-3.5-flash-lite`  | Stable  | 1,048,576 / 65,536      | $0.30 / $2.50             |
| Gemini 3.1 Flash-Lite     | `gemini-3.1-flash-lite`  | Stable (superseded; preview variant shut down) | 1M / 64K | $0.25 / $1.50 |
| Gemini 3 Flash            | `gemini-3-flash`         | Preview | 1M / 64K                | $0.50 / $3.00             |
| Gemini Omni Flash         | —                        | Preview | —                       | — (no published specification as of Jul 25, 2026) |
| Gemini 3.5 Flash Cyber    | —                        | Limited-access pilot | —          | —                         |
| Gemini 3.5 Live Translate | —                        | Preview | —                       | —                         |
| Gemini 3.1 Flash Live     | —                        | Preview | —                       | —                         |
| Gemini 3.1 Flash TTS      | —                        | Preview | —                       | —                         |

### Gemini 2.5

| Model                         |
| ----------------------------- |
| Gemini 2.5 Flash              |
| Gemini 2.5 Flash-Lite         |
| Gemini 2.5 Pro                |
| Gemini 2.5 Flash Live Preview |
| Gemini 2.5 Flash TTS Preview  |
| Gemini 2.5 Pro TTS Preview    |

### Media, Agents, Embeddings, and Robotics

| Category     | Models                                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------------------------- |
| Image        | Nano Banana 2, Nano Banana Pro, Nano Banana, Imagen 4                                                           |
| Video        | Veo 3.1 Preview, Veo 3.1 Lite Preview                                                                           |
| Music        | Lyria 3 Pro Preview, Lyria 3 Clip Preview, Lyria RealTime Experimental                                          |
| Tool / Agent | Computer Use Preview, Gemini Deep Research Preview, Gemini Deep Research Max Preview, Antigravity Agent Preview |
| Embeddings   | Gemini Embedding 2, Gemini Embedding                                                                            |
| Robotics     | Gemini Robotics-ER 1.6 Preview                                                                                  |

### Notes

**Gemini 3.6 Flash (July 2026):** Google's recommended Flash-tier model,
positioned as the workhorse "designed for the agentic era." Input modalities
are text, image, video, audio, and PDF; output is text only. It supports code
execution, computer use (Preview), file search, function calling, grounding
with Google Search and Google Maps, structured outputs, thinking, URL context,
the Batch API, context caching, and flex/priority inference. It does not
support audio generation, image generation, or the Live API. The model page
does not publish a knowledge cutoff — see the model card.

**Migration to 3.6 Flash:** `temperature`, `top_p`, and `top_k` are deprecated
and ignored, and will return HTTP 400 in future versions. `thinking_budget` is
superseded by `thinking_level` string values, with the `medium` default
carried over from 3.5 Flash. Requests may no longer end on a model-role turn
(prefilled model turns now error) — move that steering into
`system_instruction` or structured outputs.

**Gemini 3.5 Flash-Lite (July 2026):** Google's recommended Flash-Lite tier,
superseding Gemini 3.1 Flash-Lite and Gemini 2.5 Flash. Stable, 1,048,576
input / 65,536 output tokens, ~350 output tokens per second. Input is priced
uniformly at $0.30/M across text, image, video, and audio; output $2.50/M;
Batch and Flex $0.15 / $1.25; Priority $0.54 / $4.50; context caching $0.03/M
plus $1.00 per million tokens per hour of storage. It supports Search and Maps
grounding, code execution, file search, function calling, structured outputs,
thinking, URL context, context caching, Batch, and flex/priority inference,
but **not** computer use, the Live API, audio generation, or image generation.
`thinking_level` defaults to `"minimal"` — Google advises raising it to
`"medium"` or `"high"` for autonomous subagents that make tool calls, which
otherwise terminate early. The same migration changes as 3.6 Flash apply.

**Pro tier:** Gemini 3.1 Pro (Preview) remains the newest Pro-tier model on the model page. Google has stated that Gemini 3.5 Pro is testing with partners with broader availability "as soon as it's ready," and that Gemini 4 pre-training has begun; neither has a published specification.

**Deprecated or shut down (July 2026 scan):** Gemini 3 Pro Preview, Gemini 3.1 Flash-Lite Preview, Gemini 2.0 Flash, Gemini 2.0 Flash-Lite, and Imagen 4. Note that Gemini 3 Pro Preview moving to this list makes template 04 a reference-only document.

**Flagship:** Google's model page presents **Gemini 3.6 Flash** as its latest and default model. The Pro tier has not moved — Gemini 3.1 Pro is still Preview and still the newest Pro-tier model, and no Gemini 3.5 Pro appears in the public lineup.

**Source:** [Google Gemini API model
documentation](https://ai.google.dev/gemini-api/docs/models), [Gemini 3.6
Flash model page](https://ai.google.dev/gemini-
api/docs/models/gemini-3.6-flash), [pricing](https://ai.google.dev/gemini-
api/docs/pricing), [using the latest Gemini
models](https://ai.google.dev/gemini-api/docs/latest-model), and the [launch
announcement](https://blog.google/innovation-and-ai/models-and-
research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/) —
verified July 25, 2026.

---

## Summary Table

| Provider  | Flagship (vendor-designated) | Primary Current Families                       |
| --------- | ---------------------------- | ---------------------------------------------- |
| OpenAI    | **GPT-5.6 Sol**              | GPT-5.6 (Sol / Terra / Luna), GPT-Realtime, GPT Image |
| Anthropic | **Claude Fable 5**           | Claude Fable, Claude Mythos, Claude Opus, Claude Sonnet, Claude Haiku |
| Google    | **Gemini 3.6 Flash**         | Gemini 3, Gemini 2.5, Imagen, Veo, Lyria, Gemini Embedding, Gemini Robotics |

---

## Source Links

* OpenAI: https://developers.openai.com/api/docs/models
* Anthropic: https://docs.anthropic.com/en/docs/about-claude/models/overview
* Google Gemini: https://ai.google.dev/gemini-api/docs/models

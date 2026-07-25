# Model Prompt Templates

A library of 27 model-specific prompt templates for the current Anthropic,
Google, and OpenAI model families. All three provider lineups were re-scanned
against official documentation on **25 July 2026** — see
[current-model-list.md](./current-model-list.md). Each template contains a model
profile, a fill-in-the-blank prompt scaffold, model-specific prompting
principles, and worked examples.

**Primary use case:** point an AI coding assistant (Claude Code, GitHub
Copilot, etc.) at this folder, state your intent, and have it generate a
ready-to-use prompt tailored to a specific model. The reusable meta-prompt for
that workflow is [00-generate-model-prompt.md](./00-generate-model-prompt.md).

> **Markdown convention:** every template and guide in this folder carries YAML
> front matter and starts at an H2, per
> `.github/instructions/markdown.instructions.md`. This README is the deliberate
> exception — it stays human-facing on GitHub with a plain H1 and no metadata
> block.

---

## Current Flagship by Family

| Provider | Flagship | Template |
|---|---|---|
| Anthropic | **Claude Fable 5** — designated the most capable widely released model | [13](./13-anthropic-claude-fable-5.md) |
| OpenAI | **GPT-5.6 Sol** — the documented starting point for complex reasoning and coding | [23](./23-openai-gpt-5-6-sol.md) |
| Google | **Gemini 3.6 Flash** — presented as the latest and default model | [26](./26-google-gemini-3-6-flash.md) |

Two counterintuitive results from the July 2026 scan. Anthropic's flagship is
**not** in the Opus line — Claude Fable 5 sits above it, so Claude Opus 5 is the
top *Opus-tier* model but not the top Claude. And Google's flagship is a
**Flash**-tier model: there is no Gemini 3.5 Pro in the public lineup, and the
newest Pro-tier model (Gemini 3.1 Pro) is still Preview.

---

## Instructions for AI Assistants

If you are an AI assistant asked to generate a prompt using this folder,
follow these steps. Do not read every template — read only the one you need.

1. **Identify the target model.** If the user named a model, map it to a
   template file using the index below. If the user did not name a model,
   select one using the Model Selection Rules, state which model you chose
   and why, and proceed.
2. **If the user named a legacy or delisted model** (Claude Opus 4.5–4.8,
   Claude Sonnet 4.5/4.6, GPT-5.1–5.5 and the Codex variants, Gemini 3 Pro,
   Gemini 3/3.5 Flash, Gemini 3.1 Flash-Lite), recommend the successor shown in
   the index but honor the user's choice if they confirm it.
3. **Read exactly one template file** — the one matching the chosen model.
4. **Fill the template's scaffold** with the user's intent: role, domain,
   task, context, constraints, and output format. Follow that template's
   "Key Prompting Principles" section — the same intent is phrased differently
   per model (XML tags for Claude, markdown sections for OpenAI,
   context-first/instruction-last for Gemini).
5. **For Claude 5-generation targets** (Fable 5, Opus 5, Sonnet 5), write
   *less*, not more. Do not add verification instructions, "double-check your
   work," progress-summary scaffolding, severity filters like "only report
   high-severity issues," or enumerated style prohibitions — all of them now
   degrade output. Use judgment framing ("match the surrounding code") and pass
   real references (code, tests, mockups, rubrics) instead of prose describing
   them. Each of those templates carries a Steering Block Library; paste only
   the blocks the user's failure mode calls for.
6. **For GPT-5.6 targets** (Sol, Terra, Luna), also write less: OpenAI's own
   testing found leaner prompts raised eval scores roughly 10–15% while cutting
   total tokens 41–66%. Remove repeated instructions and simplify tool
   descriptions, set `reasoning.effort` one rung below the GPT-5.5 baseline
   before escalating, and control length with `text.verbosity` rather than
   prose.
7. **For Gemini 3.5/3.6-generation targets** (3.6 Flash, 3.5 Flash-Lite), drop
   `temperature`, `top_p`, and `top_k` (deprecated and ignored), use
   `thinking_level` string values rather than `thinking_budget`, and never end a
   request on a model-role turn. Defaults differ: `medium` on 3.6 Flash,
   `minimal` on 3.5 Flash-Lite — raise Flash-Lite to `medium` or `high` for
   autonomous subagents or they terminate early.
8. **Return the finished prompt in a single fenced code block**, followed by
   the template's API quick-reference settings (model ID, thinking/reasoning
   and effort parameters) so the user can run it immediately.
9. **Ask at most one round of clarifying questions**, and only if the intent
   is missing something load-bearing (audience, output format, or success
   criteria). Otherwise make reasonable assumptions and note them.

---

## Template Index

### Current models (prefer these)

| File | Model | Pick when… |
|---|---|---|
| [13-anthropic-claude-fable-5.md](./13-anthropic-claude-fable-5.md) | Claude Fable 5 — **Anthropic flagship** | Hardest novel problems, multi-day autonomous agent runs, ~1M-token synthesis, errors are very costly |
| [21-anthropic-claude-opus-5.md](./21-anthropic-claude-opus-5.md) | Claude Opus 5 | Complex agentic coding, multi-file features and refactors, production code review, enterprise document work |
| [22-anthropic-claude-sonnet-5.md](./22-anthropic-claude-sonnet-5.md) | Claude Sonnet 5 | Production coding agents, multi-tool workflows, structured extraction, frontend and computer use |
| [03-anthropic-claude-haiku.md](./03-anthropic-claude-haiku.md) | Claude Haiku 4.5 | High-volume classification/extraction, real-time chat, subagent workers — but see its October 2026 retirement date |
| [23-openai-gpt-5-6-sol.md](./23-openai-gpt-5-6-sol.md) | GPT-5.6 Sol — **OpenAI flagship** | Complex professional work, deep reasoning, production coding, cybersecurity, multi-agent workflows |
| [24-openai-gpt-5-6-terra.md](./24-openai-gpt-5-6-terra.md) | GPT-5.6 Terra | General enterprise and agentic work needing strong capability at half Sol's cost |
| [25-openai-gpt-5-6-luna.md](./25-openai-gpt-5-6-luna.md) | GPT-5.6 Luna | High-volume, low-latency, cost-sensitive workloads and subagent workers |
| [26-google-gemini-3-6-flash.md](./26-google-gemini-3-6-flash.md) | Gemini 3.6 Flash — **Google flagship** (Stable) | Agentic loops, fast code generation, computer use, rapid multimodal tasks |
| [27-google-gemini-3-5-flash-lite.md](./27-google-gemini-3-5-flash-lite.md) | Gemini 3.5 Flash-Lite (Stable) | Highest-throughput bulk processing — document extraction, structured JSON parsing, subagent workers |
| [18-google-gemini-3-1-pro.md](./18-google-gemini-3-1-pro.md) | Gemini 3.1 Pro (Preview) | Deepest multimodal reasoning — images/audio/video/PDF analysis, scientific reasoning, agentic coding |

### Legacy / deprecated models (existing deployments only)

| File | Model | Status |
|---|---|---|
| [14-anthropic-claude-opus-4-8.md](./14-anthropic-claude-opus-4-8.md) | Claude Opus 4.8 | Delisted → prefer Opus 5 (21); retires no sooner than May 28, 2027 |
| [12-anthropic-claude-opus-4-6.md](./12-anthropic-claude-opus-4-6.md) | Claude Opus 4.6 | Delisted → prefer Opus 5 (21); retires no sooner than Feb 5, 2027 |
| [01-anthropic-claude-opus-4-5-4-6.md](./01-anthropic-claude-opus-4-5-4-6.md) | Claude Opus 4.5 / 4.6 | Delisted → prefer Opus 5 (21); 4.5 retires no sooner than Nov 24, 2026 |
| [02-anthropic-claude-sonnet-4-5-4-6.md](./02-anthropic-claude-sonnet-4-5-4-6.md) | Claude Sonnet 4.5 / 4.6 | Delisted → prefer Sonnet 5 (22); 4.5 retires no sooner than Sep 29, 2026 |
| [15-openai-gpt-5-5.md](./15-openai-gpt-5-5.md) | GPT-5.5 | No longer flagship, delisted → prefer GPT-5.6 Sol (23) |
| [11-openai-gpt-5-4.md](./11-openai-gpt-5-4.md) | GPT-5.4 | Delisted → prefer GPT-5.6 Terra (24) |
| [16-openai-gpt-5-4-mini.md](./16-openai-gpt-5-4-mini.md) | GPT-5.4 mini | Delisted → prefer GPT-5.6 Terra (24) or Luna (25) |
| [17-openai-gpt-5-4-nano.md](./17-openai-gpt-5-4-nano.md) | GPT-5.4 nano | Delisted → prefer GPT-5.6 Luna (25) |
| [19-google-gemini-3-5-flash.md](./19-google-gemini-3-5-flash.md) | Gemini 3.5 Flash | Stable but superseded → prefer Gemini 3.6 Flash (26) |
| [20-google-gemini-3-1-flash-lite.md](./20-google-gemini-3-1-flash-lite.md) | Gemini 3.1 Flash-Lite | Stable but superseded → prefer Gemini 3.5 Flash-Lite (27) |
| [04-google-gemini-3-pro.md](./04-google-gemini-3-pro.md) | Gemini 3 Pro | **Shut down** — reference only; Pro tier is Gemini 3.1 Pro (18) |
| [05-google-gemini-3-flash.md](./05-google-gemini-3-flash.md) | Gemini 3 Flash | Preview, two generations behind → prefer 3.6 Flash (26) |
| [06](./06-openai-gpt-5-1.md) / [07](./07-openai-gpt-5-2.md) / [08](./08-openai-gpt-5-3.md) | GPT-5.1 / 5.2 / 5.3 | Deprecated, retiring Jul–Aug 2026 → GPT-5.6 Sol (23) |
| [09](./09-openai-gpt-5-2-codex.md) / [10](./10-openai-gpt-5-3-codex.md) | GPT-5.2 / 5.3 Codex | Deprecated → GPT-5.6 Sol (23) for coding |

> **Nearest retirement:** `claude-haiku-4-5-20251001` retires no sooner than
> **October 15, 2026**. It is the only *current* model in this library with a
> retirement date inside the next six months. Full table in
> [user-guide.md](./user-guide.md#retirement-dates-worth-planning-around).

---

## Model Selection Rules (when the user doesn't name a model)

1. **Provider stated or implied** (existing stack, API keys, mention of
   "Claude"/"GPT"/"Gemini") → stay within that provider's current models.
2. **Multimodal input** (images, audio, video, PDFs) → Gemini 3.6 Flash (speed
   and cost) or Gemini 3.1 Pro (depth). Only the Gemini templates cover native
   audio and video input.
3. **Code-heavy, multi-file, or long-horizon agentic** → Claude Opus 5 or
   GPT-5.6 Sol; escalate to Claude Fable 5 only for the hardest or longest
   autonomous runs.
4. **High volume / cost- or latency-critical** → GPT-5.6 Luna, Claude Haiku 4.5,
   or Gemini 3.5 Flash-Lite.
5. **Balanced everyday production work** → Claude Sonnet 5, GPT-5.6 Terra, or
   Gemini 3.6 Flash.
6. **High-stakes professional analysis or writing** → Claude Opus 5 or
   GPT-5.6 Sol (consider `reasoning.mode: "pro"` on Sol).
7. **Zero Data Retention required** → not Fable 5 (30-day retention is
   mandatory); use Opus 5 or Sonnet 5.
8. **A stable, non-preview Google model is required** → Gemini 3.6 Flash;
   Gemini 3.1 Pro is still Preview.
9. **The workload must outlive 2026 without a migration** → avoid Haiku 4.5;
   use Sonnet 5 at `low` effort or GPT-5.6 Luna instead.
10. **Genuine tie** → present the top two with a one-line trade-off and ask.

---

## Folder Contents

| File | Purpose |
|---|---|
| [00-generate-model-prompt.md](./00-generate-model-prompt.md) | Reusable meta-prompt: pick a model + provide intent → get a finished prompt |
| `01`–`27` `*.md` | Per-model prompt templates (see index above) |
| [user-guide.md](./user-guide.md) | Full selection guidance, flagship and retirement tables, template anatomy, prompting best practices |
| [current-model-list.md](./current-model-list.md) | Source of truth for the current model lineup |

**Scope:** general-purpose text/reasoning models only. Claude Mythos 5
(limited availability), Gemini 3.5 Flash Cyber (limited-access pilot), Gemini
Omni Flash (Preview, no published specification), Gemini 2.5 (previous
generation), and all media/voice/TTS/embedding/robotics models are intentionally
excluded.

**Maintenance:** when a provider ships a new model, add a template following
the checklist in [user-guide.md → Adding New Templates](./user-guide.md#adding-new-templates),
then update the index here and in the user guide.

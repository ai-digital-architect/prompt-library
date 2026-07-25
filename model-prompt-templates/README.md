# Model Prompt Templates

A library of 22 model-specific prompt templates for the current Anthropic,
Google, and OpenAI model families (Anthropic templates refreshed July 2026 for
the Claude 5 generation; see [current-model-list.md](./current-model-list.md)).
Each template contains a model profile, a fill-in-the-blank prompt scaffold,
model-specific prompting principles, and worked examples.

**Primary use case:** point an AI coding assistant (Claude Code, GitHub
Copilot, etc.) at this folder, state your intent, and have it generate a
ready-to-use prompt tailored to a specific model. The reusable meta-prompt for
that workflow is [00-generate-model-prompt.md](./00-generate-model-prompt.md).

---

## Instructions for AI Assistants

If you are an AI assistant asked to generate a prompt using this folder,
follow these steps. Do not read every template — read only the one you need.

1. **Identify the target model.** If the user named a model, map it to a
   template file using the index below. If the user did not name a model,
   select one using the Model Selection Rules, state which model you chose
   and why, and proceed.
2. **If the user named a deprecated/legacy model** (GPT-5.1–5.3, Codex
   variants, Claude Opus 4.5/4.6/4.8, Claude Sonnet 4.5/4.6, Gemini 3
   Pro/Flash), recommend the successor shown in the index but honor the user's
   choice if they confirm it.
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
6. **Return the finished prompt in a single fenced code block**, followed by
   the template's API quick-reference settings (model ID, thinking/reasoning
   and effort parameters) so the user can run it immediately.
7. **Ask at most one round of clarifying questions**, and only if the intent
   is missing something load-bearing (audience, output format, or success
   criteria). Otherwise make reasonable assumptions and note them.

---

## Template Index

### Current models (prefer these)

| File | Model | Pick when… |
|---|---|---|
| [13-anthropic-claude-fable-5.md](./13-anthropic-claude-fable-5.md) | Claude Fable 5 | Hardest novel problems, multi-day autonomous agent runs, ~1M-token synthesis, errors are very costly |
| [21-anthropic-claude-opus-5.md](./21-anthropic-claude-opus-5.md) | Claude Opus 5 | Complex agentic coding, multi-file features and refactors, production code review, enterprise document work |
| [22-anthropic-claude-sonnet-5.md](./22-anthropic-claude-sonnet-5.md) | Claude Sonnet 5 | Production coding agents, multi-tool workflows, structured extraction, frontend and computer use |
| [03-anthropic-claude-haiku.md](./03-anthropic-claude-haiku.md) | Claude Haiku 4.5 | High-volume classification/extraction, real-time chat, subagent workers |
| [15-openai-gpt-5-5.md](./15-openai-gpt-5-5.md) | GPT-5.5 | Complex reasoning and coding on OpenAI, large tool surfaces, expert professional work |
| [11-openai-gpt-5-4.md](./11-openai-gpt-5-4.md) | GPT-5.4 | Affordable frontier work — long-context analysis, multi-step workflows with clear deliverables |
| [16-openai-gpt-5-4-mini.md](./16-openai-gpt-5-4-mini.md) | GPT-5.4 mini | Production pipelines, summarization, mid-complexity coding at lower cost/latency |
| [17-openai-gpt-5-4-nano.md](./17-openai-gpt-5-4-nano.md) | GPT-5.4 nano | Very-high-volume single-step tasks: classification, extraction, routing |
| [18-google-gemini-3-1-pro.md](./18-google-gemini-3-1-pro.md) | Gemini 3.1 Pro (Preview) | Deepest multimodal reasoning — images/audio/video/PDF analysis, scientific reasoning, agentic coding |
| [19-google-gemini-3-5-flash.md](./19-google-gemini-3-5-flash.md) | Gemini 3.5 Flash (Stable) | Fast agentic tool use, interactive assistants, production pipelines with multimodal input |
| [20-google-gemini-3-1-flash-lite.md](./20-google-gemini-3-1-flash-lite.md) | Gemini 3.1 Flash-Lite (Stable) | Lowest-cost/highest-throughput bulk processing |

### Legacy / deprecated models (existing deployments only)

| File | Model | Status |
|---|---|---|
| [14-anthropic-claude-opus-4-8.md](./14-anthropic-claude-opus-4-8.md) | Claude Opus 4.8 | Active legacy → prefer Opus 5 (21) |
| [12-anthropic-claude-opus-4-6.md](./12-anthropic-claude-opus-4-6.md) | Claude Opus 4.6 | Active legacy → prefer Opus 5 (21) |
| [01-anthropic-claude-opus-4-5-4-6.md](./01-anthropic-claude-opus-4-5-4-6.md) | Claude Opus 4.5 / 4.6 | Active legacy → prefer Opus 5 (21) |
| [02-anthropic-claude-sonnet-4-5-4-6.md](./02-anthropic-claude-sonnet-4-5-4-6.md) | Claude Sonnet 4.5 / 4.6 | Active legacy → prefer Sonnet 5 (22) |
| [04-google-gemini-3-pro.md](./04-google-gemini-3-pro.md) | Gemini 3 Pro | Superseded → prefer 3.1 Pro (18) |
| [05-google-gemini-3-flash.md](./05-google-gemini-3-flash.md) | Gemini 3 Flash | Preview → prefer 3.5 Flash (19) |
| [06](./06-openai-gpt-5-1.md) / [07](./07-openai-gpt-5-2.md) / [08](./08-openai-gpt-5-3.md) | GPT-5.1 / 5.2 / 5.3 | Deprecated, retiring Jul–Aug 2026 → GPT-5.5 (15) |
| [09](./09-openai-gpt-5-2-codex.md) / [10](./10-openai-gpt-5-3-codex.md) | GPT-5.2 / 5.3 Codex | Deprecated → GPT-5.5 (15) for coding |

---

## Model Selection Rules (when the user doesn't name a model)

1. **Provider stated or implied** (existing stack, API keys, mention of
   "Claude"/"GPT"/"Gemini") → stay within that provider's current models.
2. **Multimodal input** (images, audio, video, PDFs) → Gemini 3.1 Pro (depth)
   or Gemini 3.5 Flash (speed).
3. **Code-heavy, multi-file, or long-horizon agentic** → Claude Opus 5 or
   GPT-5.5; escalate to Claude Fable 5 only for the hardest or longest
   autonomous runs.
4. **High volume / cost- or latency-critical** → Claude Haiku 4.5,
   Gemini 3.1 Flash-Lite, or GPT-5.4 nano.
5. **Balanced everyday production work** → Claude Sonnet 5, GPT-5.4 (or
   mini), or Gemini 3.5 Flash.
6. **High-stakes professional analysis or writing** → Claude Opus 5 or
   GPT-5.5.
7. **Zero Data Retention required** → not Fable 5 (30-day retention is
   mandatory); use Opus 5 or Sonnet 5.
8. **Genuine tie** → present the top two with a one-line trade-off and ask.

---

## Folder Contents

| File | Purpose |
|---|---|
| [00-generate-model-prompt.md](./00-generate-model-prompt.md) | Reusable meta-prompt: pick a model + provide intent → get a finished prompt |
| `01`–`22` `*.md` | Per-model prompt templates (see index above) |
| [user-guide.md](./user-guide.md) | Full selection guidance, template anatomy, prompting best practices |
| [current-model-list.md](./current-model-list.md) | Source of truth for the current model lineup |

**Scope:** general-purpose text/reasoning models only. Claude Mythos 5
(limited availability), Gemini 2.5 (previous generation), and all
media/voice/TTS/embedding/robotics models are intentionally excluded.

**Maintenance:** when a provider ships a new model, add a template following
the checklist in [user-guide.md → Adding New Templates](./user-guide.md#adding-new-templates),
then update the index here and in the user guide.

---
post_title: "Meta-Prompt — Generate a Model-Specific Prompt from This Library"
author1: "Prompt Library Team"
post_slug: "00-generate-model-prompt"
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
  - "meta-prompt"
  - "prompt-generation"
ai_note: "Content created with AI assistance."
summary: >
  Reusable meta-prompt that turns a plain-language intent into a finished,
  model-specific prompt by routing through this library's README and reading
  exactly one template.
post_date: "2026-03-03"
last_updated: "2026-07-25"
---

Use this document to turn a plain-language intent into a polished,
model-specific prompt built from the templates in this folder.

**How to use it:**

1. Open your coding assistant (Claude Code, GitHub Copilot Chat, etc.) in
   this repository.
2. Copy the meta-prompt below, fill in the `{{...}}` fields (leave
   `{{TARGET_MODEL}}` as `auto` to let the assistant choose), and send it.
3. The assistant reads `README.md`, picks exactly one template, and returns a
   finished prompt plus the API settings to run it with.

> Tip: in Claude Code you can simply say
> *"Using model-prompt-templates/00-generate-model-prompt.md, generate a
> prompt for &lt;model&gt; to &lt;intent&gt;"* — the assistant will apply the
> meta-prompt below to your request.

---

## The Meta-Prompt (copy from here)

```text
You are a prompt engineer. Generate a ready-to-use, model-specific prompt
using the prompt-template library in the model-prompt-templates/ folder.

## My request

- TARGET_MODEL: {{TARGET_MODEL}}            (a specific model, e.g. "Claude Opus 5",
                                             "GPT-5.6 Sol", "Gemini 3.6 Flash" — or "auto"
                                             to have you select the best fit)
- INTENT: {{INTENT}}                        (what the generated prompt must accomplish,
                                             in plain language — be specific)
- AUDIENCE / CONSUMER: {{AUDIENCE}}         (who reads or consumes the model's output,
                                             e.g. "senior engineers", "the CFO",
                                             "a downstream JSON parser" — or "n/a")
- CONTEXT I WILL PROVIDE: {{CONTEXT}}       (what reference material will accompany the
                                             prompt at runtime: code, documents, data,
                                             schemas — or "none")
- HARD CONSTRAINTS: {{CONSTRAINTS}}         (length limits, tone, format rules, things
                                             the model must never do — or "none")
- DESIRED OUTPUT FORMAT: {{OUTPUT_FORMAT}}  (sections, JSON schema, table, slides —
                                             or "you decide")

## Your process (follow exactly)

1. Read model-prompt-templates/README.md. Do NOT read every template.
2. Resolve the target model:
   - If TARGET_MODEL names a model, map it to its template file via the
     README's Template Index. If it is a legacy/deprecated model, tell me the
     recommended successor in one line, then use whichever I confirm (default
     to my original choice if I gave no further instruction).
   - If TARGET_MODEL is "auto", choose using the README's Model Selection
     Rules and state in one or two lines which model you chose and why.
3. Read ONLY the chosen model's template file.
4. Build the prompt by filling that template's scaffold with my request,
   strictly following its "Key Prompting Principles" — use the prompt style
   native to that model (XML tags for Claude, markdown-sectioned system/user
   roles for OpenAI, system_instruction with context-first/instruction-last
   ordering for Gemini). Where my request leaves a placeholder genuinely
   unfillable, keep a clearly marked {{PLACEHOLDER}} for me to complete.
   If the target is a Claude 5-generation model (Fable 5, Opus 5, Sonnet 5) or
   a GPT-5.6 model (Sol, Terra, Luna), keep the prompt lean: no verification or
   double-check instructions, no progress-summary scaffolding, no severity
   filters, no enumerated style prohibitions, no repeated instructions. Use
   judgment framing and add only the Steering Blocks from that template that my
   request actually calls for.
5. If anything load-bearing is missing (success criteria, audience, or output
   format), ask me at most one batch of clarifying questions BEFORE writing
   the prompt. Otherwise proceed and list your assumptions.

## Your output (in this order)

1. **Model & template used** — one line, with the successor note if relevant.
2. **The generated prompt** — one single fenced code block, ready to paste.
3. **Run settings** — the template's API quick-reference adapted to this
   task: exact model ID, thinking/reasoning configuration, effort or
   reasoning_effort level, and a suggested max_tokens.
4. **Assumptions & open placeholders** — short bullet list (omit if none).

Do not explain prompt-engineering theory. Do not produce the model's answer
to the task — produce only the prompt that I will run against the target
model.
```

---

## Worked Example Invocation

Filled-in fields for a real request:

```text
- TARGET_MODEL: auto
- INTENT: Review a Python FastAPI service handling payment webhooks for
  security and concurrency bugs before a production release; findings will
  gate the release decision.
- AUDIENCE / CONSUMER: senior backend engineers and the release manager
- CONTEXT I WILL PROVIDE: full source of the service (~6K lines) and the
  webhook provider's signature-verification spec
- HARD CONSTRAINTS: findings must cite file/function/line; no style nits;
  severity-rated; corrected code snippets for Critical/High
- DESIRED OUTPUT FORMAT: summary, findings by severity, go/no-go verdict
```

Expected behavior: the assistant selects **Claude Opus 5**
(production code review per the README rules), reads only
[21-anthropic-claude-opus-5.md](./21-anthropic-claude-opus-5.md), and
returns an XML-structured review prompt — coverage-first, with no
"double-check your work" scaffolding — with
`{"model": "claude-opus-5", "output_config": {"effort": "xhigh"}}`
as the run settings.

---

## Notes

- This file is the single entry point for prompt generation; the per-model
  knowledge lives in templates `01`–`26`, and the routing logic lives in
  [README.md](./README.md). Update those, not this file, when models change.
- For background on why prompts differ per model (template anatomy, selection
  trade-offs), see [user-guide.md](./user-guide.md).

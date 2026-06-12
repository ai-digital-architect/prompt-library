# Current AI Model Lists: OpenAI, Anthropic, and Google

**Date:** June 12, 2026

This document summarizes the currently listed models from OpenAI, Anthropic, and Google, based on the model information referenced in the prior response.

---

## OpenAI

### Frontier / General Models

| Model        | API Model ID   |
| ------------ | -------------- |
| GPT-5.5      | `gpt-5.5`      |
| GPT-5.4      | `gpt-5.4`      |
| GPT-5.4 mini | `gpt-5.4-mini` |
| GPT-5.4 nano | `gpt-5.4-nano` |

### Specialized Models

| Category                     | Models Listed                                                               |
| ---------------------------- | --------------------------------------------------------------------------- |
| Image                        | GPT Image 2                                                                 |
| Realtime voice / translation | GPT-Realtime-2, GPT-Realtime-Translate, GPT-Realtime-1.5, GPT-Realtime mini |
| Speech generation            | GPT-4o mini TTS — marked deprecated                                         |
| Transcription                | GPT-Realtime-Whisper, GPT-4o Transcribe, GPT-4o mini Transcribe             |

### Notes

OpenAI’s documentation currently recommends **GPT-5.5** for complex reasoning and coding, while the smaller GPT-5.4 variants are positioned for lower latency and lower cost use cases.

**Source:** [OpenAI model documentation](https://platform.openai.com/docs/models)

---

## Anthropic

| Model                 | API Model ID                                     | Notes                                      |
| --------------------- | ------------------------------------------------ | ------------------------------------------ |
| Claude Fable 5        | `claude-fable-5`                                 | Most capable widely released model         |
| Claude Mythos 5       | `claude-mythos-5`                                | Limited availability via Project Glasswing |
| Claude Mythos Preview | `claude-mythos-preview`                          | Invitation-only research preview           |
| Claude Opus 4.8       | `claude-opus-4-8`                                | Most capable Opus-tier model               |
| Claude Sonnet 4.6     | `claude-sonnet-4-6`                              | Speed/intelligence balance                 |
| Claude Haiku 4.5      | `claude-haiku-4-5` / `claude-haiku-4-5-20251001` | Fastest current Claude family model        |

### Notes

Anthropic’s documentation states that current Claude models support text and image input, text output, multilingual capabilities, and vision.

**Source:** [Anthropic Claude model documentation](https://docs.anthropic.com/en/docs/about-claude/models/overview)

---

## Google Gemini

### Gemini 3 / Current Generation

| Model                     | Status  |
| ------------------------- | ------- |
| Gemini 3.1 Pro            | Preview |
| Gemini 3.5 Flash          | Stable  |
| Gemini 3 Flash            | Preview |
| Gemini 3.1 Flash-Lite     | Stable  |
| Gemini 3.5 Live Translate | Preview |
| Gemini 3.1 Flash Live     | Preview |
| Gemini 3.1 Flash TTS      | Preview |

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

Google’s model page was last updated **June 9, 2026** and identifies some previous Gemini 2.0 models and older previews as deprecated or shut down.

**Source:** [Google Gemini API model documentation](https://ai.google.dev/gemini-api/docs/models)

---

## Summary Table

| Provider  | Primary Current Families                                                    |
| --------- | --------------------------------------------------------------------------- |
| OpenAI    | GPT-5.5, GPT-5.4, GPT-Realtime, GPT Image                                   |
| Anthropic | Claude Fable, Claude Mythos, Claude Opus, Claude Sonnet, Claude Haiku       |
| Google    | Gemini 3, Gemini 2.5, Imagen, Veo, Lyria, Gemini Embedding, Gemini Robotics |

---

## Source Links

* OpenAI: https://platform.openai.com/docs/models
* Anthropic: https://docs.anthropic.com/en/docs/about-claude/models/overview
* Google Gemini: https://ai.google.dev/gemini-api/docs/models

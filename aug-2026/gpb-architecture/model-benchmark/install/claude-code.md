# Installing into Claude Code

## Option A — symlink (recommended while developing)

```bash
mkdir -p .claude/skills
ln -s "$(pwd)/model-benchmark" .claude/skills/model-benchmark
```

Edits to the skill take effect immediately, with no copy step to forget.

## Option B — copy (for a pinned version)

```bash
mkdir -p .claude/skills
cp -R model-benchmark .claude/skills/model-benchmark
```

## Verify

```bash
python3 .claude/skills/model-benchmark/scripts/mb.py doctor
```

Then, in Claude Code, any of these should route into the skill:

- "benchmark Opus 5 against GPT-5.6 Sol on our security suite"
- "why aren't these two models' scores comparable?"
- "add Gemini 3.1 Pro to the benchmark"
- "which model should we route architecture review to?"

## Credentials

Export before a live run. The skill never reads credentials from config files, and
`mb.py doctor --check-configs` refuses to proceed if one is committed there.

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
```

`--dry-run` and `--replay` need none of these.

## Relationship to the prompt-template library

The skill sits inside `model-prompt-templates/` and treats the templates around it
as **read-only upstream**. It cites them in `config/models.yaml` and in the adapter
specs; it never edits them.

If your repository points assistants at that folder for prompt generation, note in
its README that `model-benchmark/` is a skill directory rather than a template, so
the "read exactly one template" instruction is not applied to it.

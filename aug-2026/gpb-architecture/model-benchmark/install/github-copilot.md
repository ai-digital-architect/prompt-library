# Installing into GitHub Copilot

Copilot discovers repository skills under `.github/skills/`.

```bash
mkdir -p .github/skills
cp -R model-benchmark .github/skills/model-benchmark
# or, while developing:
ln -s "$(pwd)/model-benchmark" .github/skills/model-benchmark
```

## Verify

```bash
python3 .github/skills/model-benchmark/scripts/mb.py doctor
python3 .github/skills/model-benchmark/scripts/mb.py test
```

`mb.py test` replays the bundled cassettes through the whole pipeline with no keys
and no spend — a good first CI job.

## In CI

```yaml
- name: Benchmark harness self-check
  run: |
    pip install -r .github/skills/model-benchmark/scripts/requirements.txt
    python3 .github/skills/model-benchmark/scripts/mb.py doctor --check-configs
    python3 .github/skills/model-benchmark/scripts/mb.py test
    python3 .github/skills/model-benchmark/scripts/mb.py compile \
        --suite .github/skills/model-benchmark/suites/security-v1.yaml \
        --all-models --dry-run
```

Three things this catches before anyone spends money:

- a credential committed into a config file
- a scoring or matching regression, via the replay pipeline
- an adapter that broke the fairness contract — the compile step exits non-zero
  when the models no longer share one `semantic_digest`

## Note on skill discovery

Copilot reads `SKILL.md` at the skill root. The leaf subskills under `skills/` are
loaded on demand by the orchestrator rather than all at once — that is the whole
point of the layout, and it keeps the always-loaded surface small.

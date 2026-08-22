# Security and data handling

A multi-vendor benchmark harness is an unusually good place to leak a credential:
it holds keys for three providers, writes prompts and responses to disk, and ships
transcripts around for judging. This document is the standing posture.

## Credentials

**Rule: a credential is read from the environment at invoke time, handed straight
to the transport, and never placed in anything that is hashed, persisted or
printed.**

| Provider | Environment variables |
| --- | --- |
| Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` |
| OpenAI | `OPENAI_API_KEY` |
| Google | `GOOGLE_API_KEY`, `GEMINI_API_KEY` |

The harness **never** reads credentials from config files. `mb.py doctor
--check-configs` scans `config/*.yaml` for credential-shaped values and refuses to
proceed if it finds one — a key committed to a config file is a far more common
leak than a logging mistake, and it survives in version-control history long after
it is deleted.

### Process environment is constructed, not inherited

`secrets.provider_env()` builds a minimal environment for any provider-scoped
subprocess: `PATH`, `HOME`, `LANG`, plus only that provider's variables. It does
**not** start from `os.environ`. Wholesale inheritance is how a key intended for
one provider ends up visible to another adapter's tooling, and it is invisible
until it matters.

### Offline modes need no credentials

`--dry-run` and `--replay` set a recognizable non-secret placeholder
(`offline-mode-no-credential-required`) so header construction succeeds. If that
string ever appears in an artifact it is obviously not a key — which is the point
of choosing it rather than a random-looking string.

## Redaction

Every artifact passes through `secrets.redact()` before it is written or printed:
manifests, transcripts, cassettes, event logs, reports. Redaction covers both
value patterns (provider key shapes, bearer tokens) and key names (`api_key`,
`auth`, `token`, `secret`, `password`).

Redaction is a backstop, not the primary control. The primary control is that
credentials never enter these structures in the first place.

## Transcripts and blinding

Transcripts are stored **content-addressed and identity-free** in
`runs/<id>/transcripts/`; the manifest holds the model. A reviewer working on
blinded judging cannot undo the blinding by opening one file.

The label→model mapping produced by `tribunal.blind()` is stored separately from
the transcripts for the same reason.

**Sealed-set transcripts are access-controlled separately from development
transcripts.** A sealed set that prompt authors can read is a development set.

## Benchmark corpora are sensitive artifacts

Suites contain deliberately seeded vulnerabilities and, in a real deployment, real
proprietary code. Treat them accordingly:

- never push a seeded-vulnerability corpus to a public remote
- record which providers received which corpus, with each provider's retention
  posture, in the run manifest
- restrict sealed-corpus access to the people who need it

### Retention posture is a per-model fact

`config/models.yaml` records it, and `mb.py plan` surfaces it in pre-flight:

| Posture | Meaning |
| --- | --- |
| `standard` | the provider's normal retention terms apply |
| `mandatory-30d` | retention is mandatory and **no zero-data-retention arrangement is available** |
| `zdr` | zero data retention is in effect |

Claude Fable 5 currently carries `mandatory-30d`. If the corpus contains
proprietary code or seeded vulnerabilities, sending it to a model under mandatory
retention is a compliance decision before it is a benchmarking one. The harness
records the fact and surfaces it; it does not make the decision.

## Prompt content

Two rules that are as much about correctness as security:

- **Never ask a model to reproduce its internal reasoning.** It triggers a
  reasoning-extraction refusal on current Anthropic models, and raw chain of
  thought is not returned by any of them. `reasoning_extraction` is in the
  prohibition list.
- **Do not put anything in a prompt you would not want in a transcript.** Prompts
  are stored, shipped to judges, and potentially retained by providers.

## Network posture

The harness makes outbound HTTPS calls only to configured provider endpoints, via
the standard library. There is no telemetry, no analytics, and no third-party SDK
in the call path — which also means no SDK upgrade can silently change a request
default, the uncontrolled variable this whole design exists to eliminate.

`--dry-run` and `--replay` make no network calls at all, which is what makes CI
possible without secrets.

## Incident checklist

If a credential is suspected to have reached an artifact:

1. rotate the key at the provider first — before investigating
2. `grep -rIl` the run directory for the key prefix; redaction should have caught
   it, but verify
3. purge affected cassettes and transcripts
4. add the leaked shape to `SECRET_PATTERNS` in `mbcore/secrets.py` if it was not
   matched
5. re-run `mb.py doctor --check-configs` across every branch, not just the tip

# Harness Skill & Plugin Factory — Design & Implementation Guide

A repeatable "software factory" that takes an **intent** (optionally enriched by deep
research) and emits a **portable Agent Skill** packaged for both **Claude Code** (as a
plugin, distributed via a marketplace) and **GitHub Copilot** (as `.github/skills` +
prompt/agent wrappers), gated by **evals**, built on top of Anthropic's **skill-creator**.

> **Stated assumptions** (adjust if wrong): distribution is **internal/enterprise** (private
> marketplace, not public); the factory tooling is **Python** to match `harness-cli`;
> layout is a **monorepo** on **trunk-based** development; generation is **human-in-the-loop
> with hard eval gates**, not fully autonomous. These mirror conventions you already run.

---

## 1. The core insight

| Concern | Portable? | Consequence for the factory |
|---|---|---|
| **The skill** (`SKILL.md` + scripts/references/assets) | **Yes** — open Agent Skills standard | Author **once**. Same artifact ships to both platforms. |
| **Packaging** (plugin manifest, marketplace, repo placement) | No | Per-platform "compile" step. |
| **Human invocation** (slash commands) | No | Claude Code `commands/*.md` ↔ Copilot `.github/prompts/*.prompt.md` — transpile from one source. |
| **Agent dispatch** (subagents) | No | Claude Code `agents/*.md` ↔ Copilot `.github/agents/*.agent.md` — transpile from one source. |
| **Tool access** | Mostly | Both consume MCP; Claude Code via `.mcp.json`, Copilot via MCP config. Your `harness-cli` is invoked by skill scripts in both. |

**Do not maintain two divergent skills.** Maintain one canonical capability and *compile*
it. The only hand-authored per-platform content is wrapper frontmatter, and even that is
generated from neutral definitions.

---

## 2. Mental model: the factory is a compiler that dogfoods skill-creator

```
                 ┌─────────────── intent (capability.yaml | one-line + research) ───────────────┐
                 │                                                                               │
   [scaffold] → [research?] → [author] → [validate] → [eval gate] → [build/transpile] → [package] → [release]
                                  │                        │              │                 │           │
                          skill-creator             skill-creator    target compilers   .skill /     marketplace.json
                          writing guide             eval harness     (CC plugin /        plugin dir   + gh skill /
                                                    + run_loop        Copilot layout)                  seed dir
```

- **Source of truth** = `capabilities/<name>/` (canonical `SKILL.md` + evals + neutral wrappers).
- **Build output** = `dist/claude-code/...` and `dist/copilot/...` (never hand-edited).
- **skill-creator** is vendored and used for three things only: its **writing guide**
  (anatomy, progressive disclosure, "explain the why" style), its **eval harness**
  (`evals.json` → grader → `benchmark.json` + the review viewer), and its **description
  optimizer** (`run_loop.py`, which uses `claude -p` to maximize trigger accuracy).

---

## 3. Opinionated project structure

```
harness-skill-factory/                         # monorepo, trunk-based
├── .claude-plugin/
│   └── marketplace.json                       # catalog: lists built plugins + their sources
├── .claude/
│   ├── settings.json
│   └── skills/
│       └── factory/                           # THE factory skill (the orchestrator)
│           ├── SKILL.md                        #   triggers on "create/build a harness skill/plugin"
│           ├── references/
│           │   ├── intent-schema.md            #   capability.yaml contract
│           │   ├── harness-cli-surface.md      #   11 verbs × 139 resources map (shared)
│           │   ├── packaging-claude-code.md
│           │   ├── packaging-copilot.md
│           │   └── authoring-rules.md          #   house style on top of skill-creator
│           ├── scripts/
│           │   ├── new_capability.py           #   scaffold from template
│           │   ├── validate.py                 #   lint frontmatter, links, line budget, secrets
│           │   ├── build_targets.py            #   compile → dist/claude-code + dist/copilot
│           │   ├── run_evals.py                #   thin wrapper over skill-creator harness
│           │   └── package_release.py          #   .skill files + plugin dirs + catalog update
│           └── agents/
│               ├── intent-researcher.md        #   deep-research path → enriched capability.yaml
│               ├── skill-author.md             #   writes SKILL.md per skill-creator
│               └── eval-grader.md              #   grades assertions
├── vendor/
│   └── skill-creator/                          # pinned (submodule or copy); the build dep
├── templates/
│   ├── capability/                             # cookiecutter for a new capability
│   ├── command.tpl.md / prompt.tpl.md          # neutral → CC command / Copilot prompt
│   └── agent.cc.tpl.md / agent.copilot.tpl.md  # neutral → CC agent / Copilot agent
├── capabilities/                               # ← SOURCE OF TRUTH (one dir per capability)
│   └── harness-pipeline-author/
│       ├── capability.yaml                     # intent contract (factory input)
│       ├── SKILL.md                            # canonical, portable
│       ├── scripts/                            # shell out to harness-cli (dry-run aware)
│       ├── references/                         # e.g. links back to harness-cli-surface.md
│       ├── assets/                             # templates Copilot/CC emit (pipeline YAML, etc.)
│       ├── commands/                           # neutral command defs (compiled both ways)
│       ├── agents/                             # neutral subagent defs (compiled both ways)
│       └── evals/
│           ├── evals.json                      # behavioral evals (skill-creator schema)
│           └── trigger-evals.json              # should/should-not-trigger queries
├── dist/                                       # ← BUILD OUTPUT (release branch or CI artifact)
│   ├── claude-code/plugins/harness-pipeline-author/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/harness-pipeline-author/SKILL.md
│   │   ├── commands/*.md                        # human invocation
│   │   ├── agents/*.md                          # agent dispatch
│   │   └── .mcp.json                            # optional
│   └── copilot/harness-pipeline-author/
│       └── .github/
│           ├── skills/harness-pipeline-author/SKILL.md
│           ├── prompts/*.prompt.md              # human invocation
│           └── agents/*.agent.md                # agent dispatch
├── tests/                                       # factory-level golden fixtures + unit tests
├── pyproject.toml                               # factory tooling (uv/poetry)
├── justfile                                     # new / research / author / validate / eval / build / package / release
└── docs/
```

Why this shape:

- **`capabilities/` vs `dist/`** enforces the compiler discipline: humans only touch source;
  CI owns output. Diffs in `dist/` during review immediately flag a hand-edit smell.
- **Neutral `commands/` and `agents/`** per capability are the single source for the two
  human/agent wrappers, transpiled at build time — no copy-paste drift.
- **`factory/` is itself a skill**, so the whole thing is invokable the same way as the
  capabilities it produces. Recursion is the point.

---

## 4. The intent contract (`capability.yaml`)

This is the factory's *input format* — the thing your "intent in, skill out" pipeline accepts.
A fast path lets a human write it directly; the research path lets a subagent fill it from a
one-liner.

```yaml
name: harness-pipeline-author
summary: Author and validate Harness CI/CD pipelines via harness-cli.
job_to_be_done: >
  When an engineer wants to create or modify a Harness pipeline, generate a correct
  pipeline spec, validate it with harness-cli, and open a PR — without them memorizing
  the CLI or the pipeline schema.

# Triggering contract (becomes/optimizes the SKILL.md description)
trigger_when:
  - "engineer asks to create, scaffold, or modify a Harness pipeline"
  - "mentions stages, steps, triggers, or pipeline YAML in a Harness context"
trigger_not_when:
  - "generic CI question unrelated to Harness (e.g. raw GitHub Actions)"

# harness-cli surface this capability is allowed to touch (keeps skills workflow-scoped)
cli_surface:
  verbs: [get, list, create, apply, validate]
  resources: [pipeline, stage, trigger, connector]
  mode: dry-run-by-default          # never hits prod Harness during evals

outputs:
  - "validated pipeline YAML written to the repo"
  - "summary of harness-cli validate results"

human_invocation:                    # → slash commands / prompts
  - id: new-pipeline
    intent: "scaffold a new pipeline for service {service}"
agent_dispatch:                      # → subagents
  - id: pipeline-builder
    role: "owns end-to-end pipeline authoring; can be delegated to by an orchestrator"

targets: [claude-code, copilot]      # which platforms to compile
eval:
  trigger_threshold: 0.85            # min trigger accuracy on held-out set
  behavioral_threshold: 0.90         # min assertion pass rate
```

The **`cli_surface` block is the key design lever** for your 11×139 `harness-cli`: it forces
each capability to be **workflow-scoped** (pipeline authoring, policy enforcement,
deployment promotion…) rather than one mega-skill that tries to wrap the whole CLI. Smaller,
sharply-described skills trigger far more reliably.

---

## 5. The build pipeline (stages = `just` targets = CI jobs)

| Stage | Command | What it does | Gate |
|---|---|---|---|
| **scaffold** | `just new <name>` | Cookiecutter a capability from `templates/capability/` | — |
| **research** *(optional)* | `just research <name>` | `intent-researcher` subagent reads `harness-cli-surface.md` + existing capabilities, fills/enriches `capability.yaml`, drafts trigger phrasings & edge cases | human signs off on `capability.yaml` |
| **author** | `just author <name>` | `skill-author` subagent writes `SKILL.md` per skill-creator's writing guide; bundles repeated logic into `scripts/` | — |
| **validate** | `just validate <name>` | Frontmatter present, description "pushy" enough, body < ~500 lines, all referenced files exist, no secrets/prod endpoints, scripts shell out to `harness-cli` (not re-implement it) | **hard fail** |
| **eval** | `just eval <name>` | Two layers (§6). Uses skill-creator harness | **hard fail** below thresholds |
| **build** | `just build <name>` | Compile canonical skill → `dist/claude-code` plugin + `dist/copilot` layout; transpile neutral commands/agents to each platform's frontmatter | — |
| **package** | `just package <name>` | `package_skill.py` → `.skill` files; assemble plugin dirs; update `marketplace.json` | — |
| **release** | `just release` | Push marketplace to Git; refresh CI seed dir; commit Copilot `.github/skills` (or publish for `gh skill`) | tag + changelog |

**Eval-before-ship is enforced in CI**: `build`/`package` refuse to run if the latest
`eval` artifact for that capability is missing, stale (older than the current `SKILL.md`
hash), or below threshold.

---

## 6. Evals: two layers, reusing skill-creator

Both layers come from skill-creator; you wrap them so they're non-interactive in CI.

### Layer 1 — Trigger evals (validates *agent dispatch*)
- **Question:** does the skill activate on the right prompts and stay quiet on near-misses?
- **How:** `trigger-evals.json` (8–10 should-trigger, 8–10 tricky should-not), run through
  skill-creator's `run_loop.py` description optimizer (`claude -p`), which splits train/held-out
  and selects the best description by *test* score (avoids overfitting).
- **Output gate:** trigger accuracy ≥ `eval.trigger_threshold` on held-out set.
- **Cross-platform caveat:** triggering is host-model dependent. Run the optimizer on Claude
  Code (fully supported), and run a **lighter smoke check on Copilot agent mode** since the same
  description is shipped to both. Record both numbers in the eval artifact.

### Layer 2 — Behavioral evals (validates *output correctness*)
- **Question:** does the skill drive the right `harness-cli` calls and produce correct artifacts?
- **How:** skill-creator's `evals.json` → with-skill vs baseline runs → `eval-grader`
  subagent scores assertions → `aggregate_benchmark.py` → `benchmark.json` (pass rate, tokens, time).
- **Determinism & safety:** evals run `harness-cli` in **`HARNESS_CLI_PROFILE=sandbox` /
  `--dry-run`** against recorded fixtures — **never production Harness**. Assertions check
  the emitted command lines and rendered artifacts against golden files. This is the single
  most important safety rule for a CLI-wrapping skill factory.
- **Output gate:** assertion pass rate ≥ `eval.behavioral_threshold`.

Because the skill *body* is identical across platforms, behavioral evals are mostly
platform-neutral; the only variation is the host agent's tool-calling, so a Claude Code run
plus a Copilot smoke run is sufficient coverage.

---

## 7. Dual-mode: human invocation **and** agent dispatch

You author each in a **neutral** form per capability; the build transpiles to both platforms.

| Mode | Neutral source | → Claude Code | → Copilot |
|---|---|---|---|
| **Autonomous trigger** | `SKILL.md` description (optimized in §6) | `skills/<name>/SKILL.md` in plugin | `.github/skills/<name>/SKILL.md` |
| **Human slash command** | `commands/*.md` (`human_invocation` in yaml) | `commands/<id>.md` → `/<plugin>:<id>` | `.github/prompts/<id>.prompt.md` → `/<id>` |
| **Agent dispatch / subagent** | `agents/*.md` (`agent_dispatch` in yaml) | `agents/<id>.md` (delegatable subagent) | `.github/agents/<id>.agent.md` (persona + tools + handoffs) |

Notes that matter in practice:

- Claude Code namespaces plugin commands (`/harness-pipeline-author:new-pipeline`). Keep
  command ids short; the plugin name already carries context.
- Copilot prompt files can pin a model in YAML frontmatter and link to instructions to avoid
  duplication — emit those links pointing at the shipped `SKILL.md`/instructions.
- Copilot agents support **handoffs** (Plan → Implement → Review). If your `agent_dispatch`
  defines an ordered set, the transpiler can wire handoffs on the Copilot side; on the Claude
  Code side the orchestrator delegates to the subagents directly.
- For org-wide *defaults* (not per-capability), Copilot also has `.github/copilot-instructions.md`
  and path-scoped `.github/instructions/*.instructions.md` (`applyTo` globs). Reserve those for
  house rules ("always use harness-cli, never curl the Harness API"), not for capability logic.

---

## 8. Packaging & distribution per platform

### Claude Code
- **Plugin manifest** `dist/.../.claude-plugin/plugin.json`: name, description, version,
  author (your platform team), keywords. Skill lives under `skills/`.
- **Catalog** `.claude-plugin/marketplace.json` at the factory repo root references each built
  plugin. Keep marketplace and plugin sources independent so you can version them separately;
  use a Git source (GitHub/GitLab/git URL) — relative paths silently fail over direct-URL
  distribution.
- **Engineer onboarding:** `claude plugin marketplace add <internal-git-url>` once, then
  `claude plugin install harness-pipeline-author@<marketplace>`; updates via
  `/plugin marketplace update`.
- **CI / containers:** build a **seed dir** once at image build (install plugins, copy
  `~/.claude/plugins`), point `CLAUDE_CODE_PLUGIN_SEED_DIR` at it — runners start with all
  Harness plugins preloaded, no runtime clone.

### Copilot
- **Repo-shared skill:** commit `dist/copilot/<name>/.github/skills/<name>/` into target repos
  (or a base repo template). Goes through normal PR review like any code.
- **Discoverable/installable:** publish skills so engineers can `gh skill` discover/install;
  personal/global skills live in `~/.copilot/skills` (or `~/.agents/skills`).
- **Reach:** the same skill works across Copilot cloud agent, code review, Copilot CLI, and VS
  Code agent mode — no extra packaging.

A thin internal "bootstrap" (a `gh` extension or a `harness-skills install` command) that does
both — adds the CC marketplace and drops the Copilot skills — gives engineers one onboarding step.

---

## 9. Wrapping `harness-cli` well (the part that makes skills good vs. flaky)

1. **Skills wrap the CLI; they never re-implement Harness logic.** Scripts in `scripts/` shell
   out to `harness-cli`. The CLI is the deterministic substrate; the skill is the *judgment
   layer* that decides which verbs/resources to call and in what order.
2. **Decompose by job-to-be-done, not by resource.** 139 resources → a handful of
   workflow-scoped skills (pipeline-author, policy-guard, deploy-promote, connector-onboard…),
   each declaring a narrow `cli_surface`. This is what keeps triggering crisp and evals tractable.
3. **One shared reference, many skills.** `harness-cli-surface.md` (the 11×139 map) lives in the
   factory and is *referenced* (progressive disclosure) rather than copied — each skill pulls in
   only the slice it needs.
4. **Sandbox profile is mandatory.** Every script honors `--dry-run` / `HARNESS_CLI_PROFILE`.
   Evals run sandboxed; the skill prints the command it *would* run and asks for confirmation
   before any mutating verb in interactive use.
5. **Capture repeated work into scripts.** If three behavioral-eval transcripts all hand-roll the
   same `harness-cli validate | jq ...` dance, that's the signal to bundle a script — exactly the
   skill-creator "look for repeated work across test cases" heuristic.

---

## 10. Implementation sketch

`justfile` (the operator-facing surface):

```make
new name:        ; python -m factory.scripts.new_capability {{name}}
research name:   ; claude -p "use the factory skill: research intent for {{name}}"
author name:     ; claude -p "use the factory skill: author SKILL.md for {{name}}"
validate name:   ; python -m factory.scripts.validate capabilities/{{name}}
eval name:       ; python -m factory.scripts.run_evals capabilities/{{name}} \
                     --trigger --behavioral --sandbox
build name:      ; python -m factory.scripts.build_targets capabilities/{{name}} \
                     --targets claude-code,copilot
package name:    ; python -m factory.scripts.package_release capabilities/{{name}}
release:         ; python -m factory.scripts.package_release --all --update-marketplace
ship name:       ; just validate {{name}} && just eval {{name}} && just build {{name}} && just package {{name}}
```

`build_targets.py` responsibilities (the compiler core):

```text
1. read capability.yaml + canonical SKILL.md
2. for target in targets:
     claude-code:
       - write .claude-plugin/plugin.json from capability.yaml
       - copy SKILL.md → skills/<name>/SKILL.md
       - transpile commands/* → commands/<id>.md
       - transpile agents/*   → agents/<id>.md
       - emit .mcp.json if capability declares MCP tools
     copilot:
       - copy SKILL.md → .github/skills/<name>/SKILL.md
       - transpile commands/* → .github/prompts/<id>.prompt.md (+ model frontmatter)
       - transpile agents/*   → .github/agents/<id>.agent.md (+ handoffs)
3. assert dist/ has no uncommitted hand-edits (hash check)
```

CI (the gate, conceptually):

```text
on PR touching capabilities/<name>/:
  validate → eval(trigger+behavioral, sandboxed) → build → (artifact) dist preview
on merge to trunk:
  re-eval changed capabilities → package → update marketplace.json → tag release
  → refresh CLAUDE_CODE_PLUGIN_SEED_DIR image → publish Copilot skills
fail-closed: package/release abort if eval artifact is missing/stale/below threshold
```

---

## 11. Rollout phasing

1. **Walking skeleton:** factory skill + one capability (`harness-pipeline-author`), manual
   `just ship`, Claude Code target only. Prove the compile + eval loop end-to-end.
2. **Add Copilot target:** wire `build_targets.py` Copilot branch; confirm the *same* SKILL.md
   triggers in Copilot agent mode; add the Copilot trigger smoke check.
3. **Add the research path:** `intent-researcher` subagent + `capability.yaml` enrichment, so a
   one-liner can seed a capability.
4. **Productionize distribution:** internal marketplace, seed-dir image, `gh skill` publish,
   one-step onboarding bootstrap.
5. **Scale out capabilities:** decompose `harness-cli` into the next workflow skills; the factory
   now amortizes every new one.

---

## 12. Open decisions I made for you (flag any to revisit)

- **Internal-only distribution** (private marketplace + repo-committed Copilot skills). If you
  want public/community distribution, the marketplace + `gh skill` paths already support it.
- **Monorepo + trunk-based.** A polyrepo (one repo per capability, central catalog referencing
  them) is viable since marketplace/plugin sources are independent — but the monorepo gives you
  atomic eval gates and shared references for less ceremony.
- **Human-in-the-loop with hard eval gates** rather than fully autonomous generation. The research
  and author stages produce drafts a human approves; evals are the objective backstop.
- **Python factory tooling** to match `harness-cli`. The skill-creator scripts are Python anyway.

# Choosing the Tech Stack for `toolsmith` — Opinion and Decision Tree

> **TL;DR.** For a CLI that builds and validates tools for coding agents, **Python is the right default**, TypeScript is a close second, and **shell is not the right choice** for this particular product — though shell is genuinely correct for a narrower class of CLIs. Reasoning below, plus a decision tree you can reuse for future projects.

---

## 1. The Recommendation

### For `toolsmith` specifically: build it in Python.

Concretely: the Python spec (`toolsmith-build-spec-python.md`) is the one to hand to Claude Code.

Five reasons, in order of weight:

1. **Schema validation is the core workload, and Python is the best language for it.** Pydantic v2 turns a tool's input definition into runtime validation, JSON Schema, and static type information from a single declaration. The Bash version has to walk JSON with `jq` and gives up strict validation unless the user has `ajv` installed. The TypeScript version is comparable (zod is excellent), so this mostly rules out shell.

2. **The MCP Python SDK is mature and the protocol is first-class.** Wrapping tools as an MCP server is one of `toolsmith`'s primary features. In Python it's ~50 lines using the `mcp` package. In Bash it's an entire subproject you'd have to reimplement in shell — the spec above explicitly punts on it and provides only a `run` subcommand with a Python adapter in `contrib/`. That punt is a real product compromise, not a clever design choice.

3. **The audience is already fluent in Python.** Developers writing tools for coding agents skew heavily Python. Asking them to author tools in TypeScript is a friction tax. Bash-based tool authoring (JSON + separate handler scripts) is usable but alien to this audience.

4. **Distribution via `pipx` is clean and matches user expectations.** `pipx install toolsmith` isolates dependencies, avoids virtualenv juggling, and fits the workflow of developers who already use `pipx` for tools like `ruff`, `poetry`, and `black`. Shell distribution via `curl | bash` works but is a weaker trust model in 2026.

5. **Async is natural, tokenizer support is direct.** The eval loop is I/O-bound (many concurrent API calls, handlers that await on network). `asyncio` + the Anthropic SDK's async client gets you concurrency in two lines. The shell version shells out to `xargs -P` and loses structured concurrency; `curl` retries and backoff have to be hand-rolled.

### When TypeScript would be the right call instead

TypeScript is genuinely competitive. Choose it over Python if:

- Your users' tools themselves are primarily JavaScript/TypeScript (handlers that inspect `package.json`, parse TS ASTs, etc.).
- You're shipping into a Node monorepo where adding a Python dependency is a governance headache.
- You're already maintaining other Node CLIs and want stack consistency.

TypeScript's MCP SDK is the *reference* implementation, so nothing is sacrificed on protocol completeness. Zod is as good as Pydantic for this use case. The main weakness is distribution: `npm install -g` is less tidy than `pipx`, and Node version juggling is more common than Python version juggling on developer machines these days.

### When shell is the right call (but not for `toolsmith`)

Shell is genuinely the best choice when:

- The tool is a thin wrapper around existing Unix commands and composes with pipes.
- State is file-based and ephemeral — no persistent schema, no complex validation, no multi-step state machines.
- Users are sysadmins, SREs, or DevOps engineers who will read the source and expect to see `set -euo pipefail` and `trap`.
- Runtime dependencies are a liability. You want something that runs on a fresh Alpine container with `apk add bash jq curl` and nothing else.

`toolsmith` does not match this profile. Its core logic is schema validation, protocol implementation, and orchestrated API calls — three things shell handles poorly.

---

## 2. What Actually Pushed the Decision

Here are the concrete forces I weighed, ranked by how much they moved the answer.

| Factor | Weight | Favors |
|---|---|---|
| MCP protocol implementation | High | Python / TS (tie) |
| Schema validation depth | High | Python (Pydantic) |
| Token counting accuracy | Medium | Python / TS (both have SDK support) |
| Async concurrency in eval loop | Medium | Python (cleanest async story for I/O-bound code) |
| Audience familiarity | Medium | Python |
| Distribution story | Medium | Python (`pipx`) |
| Runtime-dependency minimalism | Low-for-this-project | Shell |
| Type safety for tool authors | Medium | TS (slightly) / Python (close) |
| Speed of iteration | Low | Comparable across all three |

Shell wins exactly one row, and it's a factor that doesn't matter much for a developer-facing build tool. That's why I'd move shell off the table here.

Python and TypeScript are close. I land on Python because the audience and the schema workload both point the same way. If the audience assumption flipped — say you were building this for a team that lives in Next.js and Deno — I'd switch to TypeScript without hesitation.

---

## 3. Decision Tree for CLI Technology Choices

Use this any time you're starting a CLI project, not just this one.

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Is the CLI primarily a composition of existing Unix commands,    │
│    with no persistent state and no complex schema?                  │
│    (e.g., "wraps rsync + ssh + find", "fronts grep with nicer UX")  │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ YES ──▶ Shell (bash).
              │         Target: < 2000 lines, jq for any JSON,
              │         shellcheck clean, single file distribution.
              │
              └─ NO ──▶ Continue to 2.

┌─────────────────────────────────────────────────────────────────────┐
│ 2. Does the CLI need to implement or speak a non-trivial protocol   │
│    (MCP, LSP, gRPC, custom JSON-RPC)?                               │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ YES ──▶ Check which language has the best SDK for that
              │         protocol. That's your answer. For MCP, Python or
              │         TypeScript — both first-class. Rule out shell.
              │
              └─ NO ──▶ Continue to 3.

┌─────────────────────────────────────────────────────────────────────┐
│ 3. What's the schema / validation workload?                         │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ Heavy (the CLI is itself a schema tool) ──▶
              │         Python (Pydantic) or TypeScript (zod).
              │         Both excellent; decide on other factors.
              │
              ├─ Moderate (validate user config / args) ──▶
              │         Any of Python, TS, or Go work. Continue to 4.
              │
              └─ Light (just flags and positional args) ──▶
                        Continue to 4; language matters less.

┌─────────────────────────────────────────────────────────────────────┐
│ 4. Who installs this, and how?                                      │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ Python-fluent developers ──▶ Python + pipx.
              │
              ├─ JS-fluent developers / Node monorepo ──▶ TypeScript + npm.
              │
              ├─ Non-developers or mixed audience ──▶
              │         Compiled single binary.
              │         Favors Go or Rust.
              │
              ├─ Sysadmins, container base images, CI pipelines ──▶
              │         Shell, or a static binary (Go). Avoid runtime VMs.
              │
              └─ Internal-only, your team only ──▶
                        Whatever your team maintains best.

┌─────────────────────────────────────────────────────────────────────┐
│ 5. Performance requirements?                                        │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ Startup under 50ms matters (e.g., shell prompt helper,
              │  git hook, pre-commit) ──▶
              │         Go or Rust. Python/TS startup is 100–300ms.
              │
              ├─ CPU-bound work (parsing millions of lines, crypto) ──▶
              │         Go or Rust. Not Python for the hot path.
              │
              └─ I/O-bound, interactive ──▶
                        Python, TS, Go all fine.

┌─────────────────────────────────────────────────────────────────────┐
│ 6. Long-term maintenance profile?                                   │
└─────────────────────────────────────────────────────────────────────┘
              │
              ├─ Solo maintainer, occasional updates ──▶
              │         Whatever *you* are fastest in. Seriously.
              │
              ├─ Team of 2–10, years of maintenance ──▶
              │         Favor the language with strictest type checking
              │         your team will tolerate: TS strict, Python + mypy
              │         strict, Go, Rust. Avoid dynamic languages without
              │         types for anything over ~2000 lines.
              │
              └─ OSS project with external contributors ──▶
                        Pick the language most contributors will know.
                        Usually Python or TypeScript for developer tools.
```

### Applying this to `toolsmith`

1. Q1 — NO. It has persistent state (caches, logs), complex schemas.
2. Q2 — YES, MCP. Shell is out. Python or TypeScript.
3. Q3 — Heavy. Confirms Python or TypeScript.
4. Q4 — Python-fluent audience. Favors Python.
5. Q5 — I/O-bound. No strong preference.
6. Q6 — Likely a solo-to-small-team OSS project. Favors Python or TS.

Python wins 3 out of 6 where it's decisive; TypeScript ties on 2 and isn't preferred on any. That's the case for Python.

---

## 4. Honest Anti-Patterns to Avoid

A few things I see people do that usually go badly:

- **Bash past ~1500 lines.** Error messages become incomprehensible, testing is painful, and refactors are dangerous. Rewrite in Python or Go at that point.
- **Python CLIs without `--help` for every subcommand.** Typer / Click make this free; use them.
- **TypeScript CLIs that ship as a monorepo workspace.** Users who `npm install -g` one package do not want to transitively install a 12-package workspace. Bundle properly with `tsup` or `ncc`.
- **Shell CLIs that do JSON.** If the data is non-trivial, you've picked the wrong language. `jq` is good at transforming JSON, not at building coherent data models.
- **Go or Rust "for speed" when speed isn't the bottleneck.** Developer velocity is almost always the actual bottleneck for an internal CLI.
- **Mixed languages for reasons of "using the best tool for each part."** A CLI that requires both Python and Node to run is a distribution nightmare. Pick one.

---

## 5. What Would Change This Recommendation

I'd revisit this if:

- The MCP Python SDK stagnates or is deprecated (unlikely; it's actively maintained).
- You discover the CLI needs to run in environments without Python ≥ 3.11 (then Go, compiling to a static binary, becomes attractive).
- You want `toolsmith` itself to be invokable by Claude Code as a tool. In that case the shell version's simple `run` subcommand is actually a feature, because its stdin/stdout JSON contract is trivially callable from any agent. Worth considering as a complement rather than a replacement.

---

## 6. Suggested Path Forward

1. **Build Python `toolsmith` first.** It's the strongest fit and the spec is ready.
2. **Keep the shell `run` subcommand contract in mind** as a reference — the JSON-in / JSON-out handler protocol it specifies is a good design regardless of implementation language, and it means tools authored for the Python version are trivially reusable from scripts, other agents, and future ports.
3. **Consider a thin TypeScript port later** if demand appears from the Node ecosystem. The Python spec's tool-definition format maps almost 1:1 to a zod-based TypeScript version, so this is a week of work, not a rewrite.
4. **Skip the shell implementation** unless you have a specific user who needs a zero-dependency install. The Python version with `pipx` hits 95% of the "light install" benefit at a tiny fraction of the maintenance cost.

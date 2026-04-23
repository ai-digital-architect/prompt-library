# Stack Selection

Guidance for choosing the implementation language when building `toolsmith`. Use this when the user has not already committed to a stack, or when they ask for a recommendation.

## TL;DR

- **Python is the strongest default.** Best schema ergonomics, mature MCP SDK, natural `pipx` distribution, audience familiarity.
- **TypeScript is a close second.** Choose it when tools must interact with JS/TS codebases or live in a Node monorepo.
- **Shell is the right pick only in narrow cases** — thin Unix-wrapper tools with no persistent state and no need for a real MCP server. Even then, `serve` becomes a `run` subcommand with an external MCP adapter.
- **Go or Rust become attractive** when startup latency under 50 ms matters or when shipping a single static binary is a requirement.

## Decision tree

```
1. Is the CLI primarily a composition of existing Unix commands,
   with no persistent state and no complex schema?
     YES → Shell (bash). Target < 2000 lines, jq for any JSON,
           shellcheck clean, single-file distribution.
     NO  → continue to 2.

2. Does the CLI need to speak a non-trivial protocol
   (MCP, LSP, gRPC, custom JSON-RPC)?
     YES → Check which language has the best SDK for that protocol.
           For MCP: Python or TypeScript. Shell is ruled out.
     NO  → continue to 3.

3. What is the schema / validation workload?
     Heavy (the CLI itself is a schema tool) → Python (Pydantic) or
                                                TypeScript (zod).
     Moderate (validate user config / args)  → any of Python, TS,
                                                or Go work.
     Light (flags and positional args only)  → language matters less.

4. Who installs this, and how?
     Python-fluent developers            → Python + pipx.
     JS-fluent developers / Node monorepo → TypeScript + npm.
     Non-developers or mixed audience    → Compiled single binary
                                            (Go or Rust).
     Sysadmins, container bases, CI      → Shell, or static binary (Go).
     Internal team only                  → Whatever the team maintains
                                            best.

5. Performance requirements?
     Startup under 50 ms matters
       (shell prompt helper, git hook, pre-commit) → Go or Rust.
     CPU-bound work (parse millions of lines)      → Go or Rust.
     I/O-bound, interactive                        → Python, TS,
                                                      or Go all fine.

6. Long-term maintenance profile?
     Solo maintainer, occasional updates → whatever you are fastest in.
     Team of 2–10, years of maintenance  → strict-typed language your
                                            team tolerates (TS strict,
                                            Python + mypy strict, Go,
                                            or Rust).
     OSS with external contributors      → language most contributors
                                            know (usually Python or TS).
```

## How this applies to toolsmith

Walking the tree for the default `toolsmith` use case:

1. **Q1 → No.** toolsmith has persistent state (caches, logs) and complex schemas.
2. **Q2 → Yes, MCP.** Shell is ruled out of the mainline; Python or TypeScript.
3. **Q3 → Heavy.** Confirms Python or TypeScript.
4. **Q4 → Python-fluent audience (developers writing agent tools).** Favors Python.
5. **Q5 → I/O-bound.** No strong preference.
6. **Q6 → Likely solo-to-small-team OSS project.** Favors Python or TS.

Python wins three decisive rows; TypeScript ties on two and is never strictly preferred. That is the case for Python as the default.

## When Python is the right pick

Choose Python when:

- The audience writes Python professionally (data scientists, ML engineers, backend developers).
- Schema validation is core to the CLI's value (toolsmith fits).
- The MCP Python SDK (`mcp` package) covers needed features.
- Distribution via `pipx` is acceptable.
- The team is comfortable with `mypy --strict`.

Typical stack: Python 3.11+, `uv`, Typer, Pydantic, `mcp` SDK, `anthropic` SDK, pytest + `respx`.

## When TypeScript is the right pick

Choose TypeScript when:

- Tools themselves must interact with JS/TS codebases (parsing `package.json`, TS ASTs, etc.).
- The CLI lives in a Node monorepo where adding a Python dependency is a governance headache.
- The team already maintains Node CLIs and wants stack consistency.
- You need the MCP protocol's reference implementation (the TS SDK is the reference).

Typical stack: TypeScript (strict), Node 20+, Commander, zod, `@modelcontextprotocol/sdk`, `@anthropic-ai/sdk`, tsup, vitest.

## When shell is the right pick

Choose shell only when **all** of these are true:

- The tool's core logic composes existing Unix commands and pipes them together.
- State is file-based and ephemeral — no persistent schema, no complex validation, no multi-step state machines.
- Users are sysadmins, SREs, or DevOps engineers who will read the source and expect idiomatic bash.
- Runtime dependencies are a liability. The target environment is bash + jq + curl and nothing else.

For `toolsmith`, shell is **not** the right pick. MCP in bash is impractical, schema validation is weak without `ajv`, and the audience is not primarily sysadmins. If shell is chosen anyway, expect to drop `serve` in favor of a `run` subcommand with a Python MCP adapter in `contrib/`.

Typical stack: bash 4+, jq, curl, shellcheck, optional `ajv-cli`, packaged as a single-file script via `make build`.

## When Go or Rust is the right pick

Choose Go or Rust when:

- Startup latency matters (the CLI runs on every shell prompt, every git commit, or inside a hot loop).
- Distribution is to non-developers who expect a single executable.
- CPU-bound work dominates.
- The binary needs to run in minimal environments (alpine, distroless).

For `toolsmith` specifically, Go becomes interesting if the plan is to ship to a broad developer audience who shouldn't need to install Python or Node. It is not the default because the MCP SDK ecosystems are weaker in Go today than in Python or TypeScript.

## Anti-patterns to avoid

- **Bash past ~1500 lines.** Error messages become incomprehensible, testing is painful, refactors are dangerous. Rewrite in Python or Go at that point.
- **Python CLIs without `--help` for every subcommand.** Typer/Click make this free; use them.
- **TypeScript CLIs shipped as monorepo workspaces.** Users running `npm install -g` one package do not want 12 transitive workspace packages. Bundle properly with `tsup` or `ncc`.
- **Shell CLIs that do non-trivial JSON.** If the data is complex, the language is wrong. `jq` is good at transforming JSON, not at building coherent data models.
- **Go or Rust for "speed" when speed is not the bottleneck.** Developer velocity is almost always the real bottleneck for an internal CLI.
- **Mixed languages for "best tool for each part."** A CLI that needs both Python and Node to run is a distribution nightmare. Pick one.

## When to revisit

Reconsider the stack decision if:

- The MCP Python SDK stagnates or is deprecated (unlikely; it is actively maintained).
- The CLI must run in environments without Python 3.11+ or Node 20+ (then Go becomes attractive for the static binary).
- The CLI itself needs to be invokable by Claude as a tool. In that case the shell version's simple `run` subcommand is actually a feature — its stdin/stdout JSON contract is trivially callable from any agent. Worth considering as a complement rather than a replacement.

## Multi-language coexistence

It is legitimate to maintain more than one implementation — for example, a Python version for the primary audience and a shell `run` binary for scripts and agent-to-agent calls. If doing so:

- Keep the lint rule IDs, command names, and tool definition format identical across implementations.
- Users should feel they are using the same tool regardless of which binary they invoke.
- Document the implementation map explicitly in the README so users know which version to install.

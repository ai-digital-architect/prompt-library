# Locally Hosted Claude Code Plugin Marketplace
## A Cross-Project, User-Scope Plugin Distribution Architecture
### Reference Implementation Guide ｜ Principal Engineer Perspective
#### v1.0 — May 2026

---

## Table of Contents

1. [Purpose and Design Goals](#chapter-1-purpose-and-design-goals)
2. [Architectural Model](#chapter-2-architectural-model)
3. [Directory Layout](#chapter-3-directory-layout)
4. [Marketplace Manifest](#chapter-4-marketplace-manifest)
5. [Plugin Structure Requirements](#chapter-5-plugin-structure-requirements)
6. [Registration and Installation](#chapter-6-registration-and-installation)
7. [Update Lifecycle](#chapter-7-update-lifecycle)
8. [Active Plugin Development Workflow](#chapter-8-active-plugin-development-workflow)
9. [Verification and Control Points](#chapter-9-verification-and-control-points)
10. [Token Cost Considerations](#chapter-10-token-cost-considerations)
11. [Security and Operational Practices](#chapter-11-security-and-operational-practices)
12. [Anti-patterns](#chapter-12-anti-patterns)
13. [Appendix A — Command Reference](#appendix-a-command-reference)
14. [Appendix B — Known Caveats and Open Verifications](#appendix-b-known-caveats)
15. [Change Log](#change-log)

---

## Chapter 1: Purpose and Design Goals

This document specifies a **locally hosted Claude Code plugin marketplace** that satisfies the following requirements:

| # | Requirement | Mechanism |
|---|---|---|
| R1 | Plugins load automatically in **every** Claude Code session, in **any** project | User-scope plugin installation (`~/.claude/settings.json` → `enabledPlugins`) |
| R2 | No remote hosting, no public marketplace, no network dependency | Local-path marketplace registration |
| R3 | Multiple plugins distributed from a single source of truth | One marketplace root containing N plugins as subdirectories |
| R4 | Versioned, auditable, recoverable | Marketplace root is a git repository |
| R5 | No per-project setup and no launch flags | One-time user-level registration + install |
| R6 | Fast iteration loop during plugin development | `claude --plugin-dir` bypassing the install cache |

**The key insight that makes R1 and R5 work:** both marketplace registration and plugin installation **default to user scope** in Claude Code. A single setup sequence makes every plugin available in every project automatically — there is no per-project configuration and no launch-time invocation needed.

---

## Chapter 2: Architectural Model

The architecture separates four concerns, each with a distinct location and lifecycle:

```
┌─────────────────────────────────────────────────────────────────┐
│  SOURCE OF TRUTH                                                 │
│  ~/claude-marketplace/  (git repository)                         │
│  Marketplace manifest + plugin sources. You edit here.           │
└───────────────────────────┬─────────────────────────────────────┘
                            │  claude plugin marketplace update
                            │  claude plugin install / update
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPLOYED ARTIFACT                                               │
│  ~/.claude/plugins/cache/<plugin-id>/                            │
│  Verified copy made at install time. Never hand-edit.            │
└───────────────────────────┬─────────────────────────────────────┘
                            │  read at session start
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ACTIVATION SWITCH                                               │
│  ~/.claude/settings.json → enabledPlugins                        │
│  User scope = enabled across ALL projects. CLI-managed.          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PERSISTENT STATE                                                │
│  ~/.claude/plugins/data/<plugin-id>/   (${CLAUDE_PLUGIN_DATA})   │
│  Dependencies, caches, generated files. Survives updates.        │
└─────────────────────────────────────────────────────────────────┘
```

> **Architectural principle:** the marketplace is your versioned source of truth, the cache is the deployed artifact, user-scope `enabledPlugins` is the global activation switch, and `--plugin-dir` is your development loop. Keeping these four roles distinct is what makes the system predictable.

---

## Chapter 3: Directory Layout

One marketplace root. Plugins live as subdirectories. The entire tree is a single git repository.

```
~/claude-marketplace/                      ← git repository root
├── .claude-plugin/
│   └── marketplace.json                   ← marketplace manifest (Chapter 4)
├── README.md                              ← what this marketplace contains; how to use it
├── CHANGELOG.md                           ← marketplace-level change history
└── plugins/
    ├── eda-toolkit/                       ← plugin 1
    │   ├── .claude-plugin/
    │   │   └── plugin.json                ← name + version (authoritative)
    │   ├── skills/
    │   │   ├── generate-asyncapi/
    │   │   │   ├── SKILL.md
    │   │   │   └── templates/
    │   │   └── validate-events/
    │   │       └── SKILL.md
    │   ├── agents/
    │   │   ├── event-schema-reviewer.md
    │   │   └── saga-auditor.md
    │   ├── hooks/
    │   │   └── hooks.json
    │   ├── .mcp.json                      ← developer-tooling MCP servers only
    │   └── scripts/
    │       └── lint-asyncapi.sh           ← reference via ${CLAUDE_PLUGIN_ROOT}
    │
    ├── review-suite/                      ← plugin 2
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── agents/
    │   │   ├── security-reviewer.md       ← read-only; plugin agents cannot carry
    │   │   ├── perf-reviewer.md           ←   hooks / mcpServers / permissionMode
    │   │   └── style-reviewer.md
    │   └── skills/
    │       └── full-review/
    │           └── SKILL.md
    │
    └── doc-generators/                    ← plugin 3
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
            ├── write-adr/
            │   ├── SKILL.md
            │   └── adr-template.md
            └── architecture-doc/
                └── SKILL.md
```

**Layout rules:**

- The marketplace manifest lives at `.claude-plugin/marketplace.json` **in the marketplace root** — not inside any plugin.
- Each plugin's manifest lives at `<plugin>/.claude-plugin/plugin.json`. All component directories (`skills/`, `agents/`, `hooks/`, etc.) sit at the **plugin root**, not inside `.claude-plugin/`.
- Plugin `source` entries in the marketplace manifest use **relative paths** (`./plugins/<name>`) — this is exactly what local marketplaces are designed for.

---

## Chapter 4: Marketplace Manifest

`~/claude-marketplace/.claude-plugin/marketplace.json`:

```json
{
  "name": "local-plugins",
  "owner": {
    "name": "Digital Architect"
  },
  "metadata": {
    "description": "Personal cross-project plugin marketplace"
  },
  "plugins": [
    {
      "name": "eda-toolkit",
      "source": "./plugins/eda-toolkit",
      "description": "EDA development workflows: AsyncAPI generation, event schema validation, saga auditing"
    },
    {
      "name": "review-suite",
      "source": "./plugins/review-suite",
      "description": "Read-only review agents: security, performance, style"
    },
    {
      "name": "doc-generators",
      "source": "./plugins/doc-generators",
      "description": "Architecture documents and ADR generators"
    }
  ]
}
```

**Schema notes:**

| Field | Required | Notes |
|---|---|---|
| `name` | ✅ | The marketplace identifier. Used in install references: `plugin-name@local-plugins` |
| `owner` | ✅ | Owner object; `name` at minimum |
| `plugins[].name` | ✅ | Must match each plugin's own `plugin.json` name |
| `plugins[].source` | ✅ | Relative path from marketplace root, starting with `./` |
| `plugins[].description` | Recommended | Shown in the `/plugin` discovery UI |
| `plugins[].version` | Optional | **Prefer setting `version` in each plugin's own `plugin.json` instead** — it takes priority over the marketplace entry, so version is maintained in exactly one place |

> **Single-source-of-version principle:** version lives in `plugin.json`, not in `marketplace.json`. Maintaining it in both places is a cascading-consistency failure waiting to happen.

---

## Chapter 5: Plugin Structure Requirements

Each plugin follows the standard plugin layout. Minimum viable plugin:

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json        ← {"name": "<name>", "version": "1.0.0"}
└── skills/
    └── <skill>/
        └── SKILL.md
```

`plugin.json` for each plugin:

```json
{
  "name": "eda-toolkit",
  "version": "1.0.0",
  "description": "EDA development workflows",
  "license": "Proprietary"
}
```

**Component constraints to respect (these are enforced, not advisory):**

| Constraint | Detail |
|---|---|
| Plugin agent frontmatter is restricted | Plugin-shipped agents **cannot** declare `hooks`, `mcpServers`, or `permissionMode`. Allowed: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation: worktree` |
| No path traversal | Paths reaching outside the plugin root (`../shared`) break after install, because only the plugin directory is copied to the cache. Symlinks **inside** the plugin are honored during the copy — use them for shared utilities |
| Bundled file references | Scripts and templates inside the plugin must be referenced via `${CLAUDE_PLUGIN_ROOT}` so paths resolve in the cache |
| Persistent state | Anything that must survive plugin updates (installed dependencies, generated indexes) goes to `${CLAUDE_PLUGIN_DATA}`, never `${CLAUDE_PLUGIN_ROOT}` |
| Namespacing | Components are exposed as `local-plugins:<component>`, so name collisions with project or user skills cannot occur |
| MCP boundary | Per the established architectural decision: MCP servers bundled in these plugins are **developer-tooling servers only**. Anything coupled to a specific project belongs in that project's `.mcp.json`, not here |

---

## Chapter 6: Registration and Installation

The entire cross-project setup is four commands, run **once**:

```bash
# 1. One-time: register the marketplace.
#    Registration is user-level — the marketplace is known in every project.
claude plugin marketplace add ~/claude-marketplace

# 2–4. Install each plugin.
#    User scope is the DEFAULT install scope. Each install writes to
#    ~/.claude/settings.json → enabledPlugins → enabled across ALL projects.
claude plugin install eda-toolkit@local-plugins
claude plugin install review-suite@local-plugins
claude plugin install doc-generators@local-plugins
```

The resulting activation state in `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "eda-toolkit@local-plugins": true,
    "review-suite@local-plugins": true,
    "doc-generators@local-plugins": true
  }
}
```

> ⚠️ **Let the CLI write `enabledPlugins`.** Hand-editing risks drift between the settings entry, the cache, and the marketplace registration. The CLI keeps all three consistent.

From this point forward, every `claude` launch in any directory loads all three plugins. **No flags. No per-project configuration. No repeated invocation.**

---

## Chapter 7: Update Lifecycle

Installed plugins are **copied into `~/.claude/plugins/cache` at install time** for security verification. Edits to the marketplace source do **not** propagate to live sessions. The update cycle is:

```bash
# 1. Edit plugin source under ~/claude-marketplace/plugins/<name>/
# 2. Bump "version" in that plugin's plugin.json
# 3. Commit to the marketplace git repo
git -C ~/claude-marketplace add -A && git -C ~/claude-marketplace commit -m "eda-toolkit 1.1.0: add CDC validation skill"

# 4. Refresh Claude Code's view of the marketplace
claude plugin marketplace update local-plugins

# 5. Pull the new version into the cache
claude plugin update eda-toolkit
```

**Optional:** enable marketplace auto-updates so step 5 happens automatically at session start. Trade-off: convenience vs. explicit, reviewable rollout. For a single-operator local marketplace, auto-update is reasonable; for a team-shared one, prefer explicit updates.

**Sequence diagram:**

```
Source (git)          Marketplace registry        Cache                Session
     │                        │                     │                     │
     │── commit v1.1.0 ──────▶│                     │                     │
     │                        │                     │                     │
     │   marketplace update   │                     │                     │
     │◀───── re-read ─────────│                     │                     │
     │                        │                     │                     │
     │                        │── plugin update ───▶│  (copy v1.1.0)      │
     │                        │                     │                     │
     │                        │                     │──── next launch ───▶│ v1.1.0 active
```

---

## Chapter 8: Active Plugin Development Workflow

The cache copy makes the marketplace path the wrong loop for rapid iteration. During active development, bypass the cache and load the plugin **live from source**:

```bash
claude --plugin-dir ~/claude-marketplace/plugins/eda-toolkit
```

| Property | `--plugin-dir` (dev loop) | Marketplace install (deployment) |
|---|---|---|
| Source edits take effect | Immediately (next session; skills hot-reload) | Only after `marketplace update` + `plugin update` |
| Persistence | Per-session flag only | Persistent across all sessions/projects |
| Cache involvement | None — runs from source | Copied to `~/.claude/plugins/cache` |
| Use for | Building and debugging a plugin | Day-to-day consumption |

**Recommended flow:** develop with `--plugin-dir` → stabilize → bump version → commit → `marketplace update` + `plugin update` → consume everywhere via user-scope activation.

---

## Chapter 9: Verification and Control Points

| Check | Command / Location | What it tells you |
|---|---|---|
| What's installed and from where | `claude plugin list` or `/plugin` | Plugin inventory, versions, marketplace origin, errors |
| Marketplace registration | `claude plugin marketplace list` | Registered marketplaces and their sources |
| Live token cost | `/context` | Per-category context usage, including plugin skill/agent descriptions |
| Skills actually available | `/skills` | Skills from project + user + plugin sources, namespaced |
| Agents actually available | `/agents` | Includes `local-plugins:*` agents |
| Hook health | `/plugin` Errors tab | Plugin hook and MCP failures surface here |
| Config diagnostics | `/doctor` | Installation and configuration sanity |

**Per-project opt-out.** A project that should *not* load a globally enabled plugin can disable it in its own `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "eda-toolkit@local-plugins": false
  }
}
```

Project scope overrides user scope for this key. *(See Appendix B — verify this inversion path against the docs for your installed version; it follows the documented precedence model but I have not exercised it directly.)*

---

## Chapter 10: Token Cost Considerations

Every enabled plugin's skill descriptions and agent descriptions load into **every session in every project**. With a cross-project marketplace, idle token cost multiplies across your entire working day. Apply the lean-injection principle:

| Technique | Effect |
|---|---|
| `disable-model-invocation: true` on heavy/explicit-only skills (e.g., `/full-review`, deploy-style workflows) | **Zero idle tokens** — the description is not loaded; the user can still invoke explicitly |
| Front-load skill descriptions, keep under 250 characters | Descriptions above 250 chars are truncated in the listing anyway |
| Keep agent `description` fields tight and trigger-focused | Each agent costs ~30–80 idle tokens in the index |
| Audit with `/context` after each plugin install | Catch bloat at the moment it's introduced, not three plugins later |
| Split "always useful" from "occasionally useful" into separate plugins | Disable the occasional plugin per-project rather than paying for it everywhere |

> **Budget heuristic:** if the combined idle cost of all marketplace plugins exceeds ~500 tokens, restructure — usually by flipping more skills to `disable-model-invocation: true`.

---

## Chapter 11: Security and Operational Practices

| Practice | Rationale |
|---|---|
| **Git the marketplace root** | Versioned policy across all plugins, reviewable diffs, rollback. The same structure works unchanged via `claude plugin marketplace add github:you/claude-marketplace` if you ever share it |
| **Never hand-edit `~/.claude/plugins/cache`** | It's a managed deployment artifact; edits are overwritten and break verification |
| **Never hard-code credentials in plugin configs** | Use `${ENV_VAR}` references in `.mcp.json` and hook configs; use `userConfig` with `sensitive: true` for install-time secrets (stored in keychain) |
| **Review plugin agent files like production code** | Plugin agents are sandboxed by frontmatter restrictions, but their prompts still steer behavior |
| **Pin tool versions inside plugins** | `npx -y package@1.2.3`, not `@latest` — deterministic behavior across machines and time |
| **Keep the MCP boundary** | Developer-tooling MCP servers in plugins; project-coupled MCP servers in each project's `.mcp.json` |
| **Tag releases** | `git tag eda-toolkit/v1.1.0` in the marketplace repo gives you a recoverable history per plugin |

---

## Chapter 12: Anti-patterns

| ❌ Anti-pattern | ✅ Correct approach |
|---|---|
| Copying a plugin folder into `.claude/plugins/` expecting auto-discovery | No such discovery location exists. Use the marketplace install or `--plugin-dir` |
| Hand-editing `enabledPlugins` in settings | Let `claude plugin install` / `uninstall` keep settings, cache, and registry consistent |
| Maintaining `version` in both `marketplace.json` and `plugin.json` | Version in `plugin.json` only — it takes priority anyway |
| Editing source and wondering why the session doesn't change | The cache is the deployed artifact. Run `marketplace update` + `plugin update`, or use `--plugin-dir` for the dev loop |
| Relative paths escaping the plugin root (`../shared-utils`) | Symlink the shared content **into** the plugin directory; symlinks are honored during the cache copy |
| Project-specific MCP servers bundled in marketplace plugins | Those belong in that project's `.mcp.json` |
| Default-invocable heavy skills in always-on plugins | `disable-model-invocation: true`; the idle cost is paid in every session in every project |
| Writing persistent state to `${CLAUDE_PLUGIN_ROOT}` | That path is replaced on every update. Use `${CLAUDE_PLUGIN_DATA}` |

---

## Appendix A: Command Reference

```bash
# ── Setup (once) ─────────────────────────────────────────────────
claude plugin marketplace add ~/claude-marketplace
claude plugin install <plugin>@local-plugins          # user scope = default

# ── Inspection ───────────────────────────────────────────────────
claude plugin list
claude plugin marketplace list
# In-session: /plugin  /skills  /agents  /context  /doctor

# ── Update cycle ─────────────────────────────────────────────────
claude plugin marketplace update local-plugins
claude plugin update <plugin>

# ── Development loop ─────────────────────────────────────────────
claude --plugin-dir ~/claude-marketplace/plugins/<plugin>

# ── Removal ──────────────────────────────────────────────────────
claude plugin disable <plugin>                        # keep installed, deactivate
claude plugin uninstall <plugin>                      # remove from cache
claude plugin uninstall <plugin> --keep-data          # preserve ${CLAUDE_PLUGIN_DATA}
claude plugin marketplace remove local-plugins
```

---

## Appendix B: Known Caveats and Open Verifications

| # | Item | Status |
|---|---|---|
| 1 | **Per-project opt-out** (`"<plugin>@<marketplace>": false` in project `.claude/settings.json`) | Follows the documented settings-precedence model (project overrides user), but verify against the docs for your installed Claude Code version before relying on it operationally |
| 2 | **`enabledPlugins` exact shape** | Shown here as a `"plugin@marketplace": boolean` map, consistent with current behavior — but the CLI is the supported writer; treat the JSON shape as an implementation detail |
| 3 | **Marketplace auto-update behavior** | Configurable; default behavior may differ across versions. Check `claude plugin marketplace list` output and `/plugin` settings after setup |
| 4 | **Managed-settings interaction** | If your organization deploys `strictKnownMarketplaces` or `blockedMarketplaces`, local-path marketplaces may be restricted. Confirm with `/doctor` in a managed environment |
| 5 | **Skill hot-reload under `--plugin-dir`** | Skills support live change detection; other components (hooks, MCP) may require a session restart to pick up edits |

Authoritative references:

- Plugin marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces>
- Plugins reference (schemas, CLI): <https://code.claude.com/docs/en/plugins-reference>
- Plugin development: <https://code.claude.com/docs/en/plugins>
- Settings and scopes: <https://code.claude.com/docs/en/settings>

---

## Change Log

| Version | Date | Changes |
|---|---|---|
| 1.0 | May 2026 | Initial document. Converted from conversational design discussion; aligned with current Claude Code documentation. Establishes source-of-truth/artifact/activation/state separation, user-scope activation pattern, update lifecycle, dev loop, token budget heuristic, and anti-pattern catalogue |

---

*— END —*

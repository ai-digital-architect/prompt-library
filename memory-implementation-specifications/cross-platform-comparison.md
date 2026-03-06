# Cross-Platform Memory Comparison: GitHub Copilot vs Claude Code

## Executive Summary

Both GitHub Copilot and Claude Code can implement a six-type memory architecture (episodic, semantic, procedural, working, short-term, long-term), but they differ significantly in native capabilities. Claude Code has stronger file-based memory primitives — its auto-loaded `CLAUDE.md` and `MEMORY.md`, direct filesystem access, and built-in TodoWrite make Track A (file-based) highly effective out of the box. GitHub Copilot has a more structured native memory system with explicit scopes (`/memories/`, `/memories/session/`, `/memories/repo/`), but these scopes are opaque and lack programmatic access. For semantic memory, Copilot's `.github/instructions/` auto-loading is comparable to Claude Code's `CLAUDE.md`. For working memory, Claude Code's TodoWrite and full conversation context are significantly stronger than Copilot's session-scoped memories. Both platforms benefit from Track B (vector store) at scale, but Claude Code's MCP integration provides a cleaner path to vector search than Copilot's current limited MCP support. Teams starting from scratch should begin with Track A on either platform and add Track B when memory exceeds ~100 entries.

## Side-by-Side Comparison: All Six Memory Types

| Memory Type | GitHub Copilot | Claude Code | Native Primitive (Copilot) | Native Primitive (Claude) | Recommended Track | Maturity |
|---|---|---|---|---|---|---|
| **Episodic** | `/memories/repo/` + `.github/memory/episodic/` files | `.claude/memory/episodic/` files via Read/Write | Repo-scoped native memories (create-only by Copilot) | Direct file access (full CRUD) | Track A (both) | Copilot: Medium, Claude: High |
| **Semantic** | `.github/instructions/` (auto-loaded) + `/memories/repo/` | `CLAUDE.md` (auto-loaded) + `.claude/memory/semantic/` | Instruction files with `applyTo` glob patterns | CLAUDE.md always loaded; detail files read on demand | Track A (both) | Copilot: High, Claude: High |
| **Procedural** | `.github/skills/` + `/memories/` (user) + `.github/memory/procedural/` | `CLAUDE.md` workflows + `.claude/memory/procedural/` + Bash | Skill files define executable procedures | CLAUDE.md instructions + direct shell execution | Track A (both) | Copilot: High, Claude: High |
| **Working** | `/memories/session/` | Conversation context + TodoWrite | Session-scoped native memories | Built-in structured task tracking + full conversation | Track A (both) | Copilot: Low, Claude: High |
| **Short-term** | `/memories/session/` | Conversation context (auto-compressed) | Session-scoped native memories | Automatic context management with compression | Track A (both) | Copilot: Low, Claude: High |
| **Long-term** | `/memories/` (user-scoped) | `MEMORY.md` at `~/.claude/projects/*/memory/` | User-scoped persistent memories across all repos | Auto-loaded personal memory file per project | Track A (both) | Copilot: Medium, Claude: High |

## Detailed Comparison by Memory Type

### Episodic Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Storage** | `/memories/repo/` + file archive | `.claude/memory/episodic/` files |
| **Read access** | Copilot retrieves from repo memories (opaque relevance) | Direct file read with Glob + Read tools |
| **Write access** | Chat-based: ask Copilot to create repo memory | File-based: Write tool creates entry directly |
| **Search** | No search API; depends on Copilot's internal matching | Glob (filename) + Grep (content) + Track B (semantic) |
| **Version history** | None for native memories; git for files | Git for all files |
| **Verdict** | Workable but opaque | Strong native support |

### Semantic Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Auto-loading** | `.github/instructions/*.instructions.md` with `applyTo` patterns | `CLAUDE.md` always loaded |
| **Conditional loading** | File-glob-based (`applyTo: "src/**/*.ts"`) | Directory-based (subdirectory CLAUDE.md files) |
| **Detail access** | Read from `.github/memory/semantic/` (indirect) | Direct Read from `.claude/memory/semantic/` |
| **Update** | Edit instruction files via IDE; repo memories via chat | Edit tool modifies any file directly |
| **Verdict** | Strong auto-loading with glob patterns | Strong auto-loading, simpler model |

### Procedural Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Workflow definition** | `.github/skills/*.skill.md` (structured format) | `CLAUDE.md` + `.claude/memory/procedural/*.md` |
| **Execution** | Copilot follows skill steps in agent mode | Claude Code executes via Bash + file operations |
| **Automation** | Skill triggers, but no confidence thresholds | Instruction-based: always follow documented workflows |
| **Cross-repo** | User-scoped memories persist workflows across repos | MEMORY.md is per-project; cross-repo requires duplication |
| **Verdict** | Skill files are well-structured | More powerful execution (direct shell access) |

### Working Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Mechanism** | `/memories/session/` entries | Conversation context + TodoWrite |
| **Structure** | Free-text session memories | Structured todo list with states (pending/in_progress/completed) |
| **Capacity** | Unknown (no visibility into limits) | Full conversation history, auto-compressed |
| **Problem tracking** | Manual: create `[WORKING]` tagged entries | Native: TodoWrite provides task decomposition |
| **Verdict** | Minimal native support | Significantly stronger |

### Short-term Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Mechanism** | `/memories/session/` entries | Conversation context |
| **Management** | Manual creation of `[SESSION]` entries | Automatic — conversation is the short-term memory |
| **Compression** | No compression; limited by session scope | Auto-compression when approaching context limits |
| **Verdict** | Manual effort required | Handled automatically |

### Long-term Memory

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Mechanism** | `/memories/` (user-scoped) | `MEMORY.md` at `~/.claude/projects/*/memory/` |
| **Scope** | All repos (single user memory space) | Per-project (separate MEMORY.md per project) |
| **Auto-loading** | Copilot considers user memories (opaque) | MEMORY.md loaded every session (first 200 lines) |
| **Update** | Chat-based: ask Copilot to create/update | Direct: Write/Edit tool modifies MEMORY.md |
| **Cross-repo** | Native: user memories apply everywhere | Requires duplication or `~/.claude/CLAUDE.md` |
| **Verdict** | Better cross-repo reach | Better transparency and control |

## Platform Strengths

### GitHub Copilot Strengths
1. **Three distinct memory scopes**: User, session, repo — clear lifecycle semantics
2. **Instruction file glob patterns**: `applyTo` enables context-sensitive semantic memory loading
3. **Skill file format**: Structured, well-defined format for procedural memory
4. **Cross-repo user memories**: Personal preferences apply across all repositories automatically
5. **IDE integration**: Memory operates within the IDE workflow naturally

### Claude Code Strengths
1. **Direct filesystem access**: Read/Write any file — memory operations are first-class
2. **Auto-loaded CLAUDE.md**: Most effective semantic memory vehicle — always in context
3. **TodoWrite**: Purpose-built working memory tool for task decomposition
4. **Conversation-as-memory**: Full conversation history with smart compression
5. **MCP integration**: Clean path to vector store search via MCP servers
6. **Shell execution**: Procedural memory can be directly executed (git commands, build scripts)
7. **Transparency**: All memory is in files you can inspect, edit, and version-control

## Track B (Vector Store) Comparison

> The Track B cross-platform comparison table has been moved to
> [mem-impl-vector/README.md](../mem-impl-vector/README.md).

## Recommended Adoption Sequence for New Teams

### Phase 1: Foundation (Week 1)

**Both platforms**:
1. Create the memory directory structure
2. Write the core semantic memory file (CLAUDE.md or `.github/instructions/`)
3. Document 2-3 key workflows (procedural memory)
4. Record at least one past architectural decision (episodic memory)

### Phase 2: Habits (Weeks 2-4)

**Both platforms**:
1. After every significant decision, create an episodic entry
2. When standards emerge, add them to semantic memory
3. When workflows stabilize, document them in procedural memory
4. Seed personal preferences in long-term memory

### Phase 3: Scale (Month 2+)

**If memory entries exceed ~100**:
1. Evaluate Track B based on team size and search needs — see [mem-impl-vector/](../mem-impl-vector/)
2. Set up vector store infrastructure (start with Qdrant Docker)
3. Build and run the sync pipeline
4. For Claude Code: configure MCP server — see [mem-impl-vector/claude-code/track-b-vector-store-guide.md](../mem-impl-vector/claude-code/track-b-vector-store-guide.md)
5. For Copilot: configure pre-fetch scripts or MCP integration — see [mem-impl-vector/github-copilot/track-b-vector-store-guide.md](../mem-impl-vector/github-copilot/track-b-vector-store-guide.md)

### Phase 4: Optimization (Month 3+)

1. Review memory health: remove stale entries, resolve contradictions
2. Consolidate repeated episodic patterns into semantic rules
3. Refine procedural guides based on team feedback
4. Evaluate cross-project memory needs

## Maturity Ratings

| Rating | Definition |
|---|---|
| **High** | Native platform support, minimal workarounds, production-ready |
| **Medium** | Workable with documented patterns, some manual effort required |
| **Low** | Requires significant workarounds or has notable limitations |

| Memory Type | Copilot Maturity | Claude Code Maturity | Notes |
|---|---|---|---|
| Episodic | Medium | High | Claude's direct file access is more reliable than Copilot's opaque repo memories |
| Semantic | High | High | Both have strong auto-loading mechanisms |
| Procedural | High | High | Copilot has skill files; Claude has shell execution |
| Working | Low | High | Claude's TodoWrite and conversation context far exceed Copilot's session memories |
| Short-term | Low | High | Claude handles this automatically; Copilot requires manual session entries |
| Long-term | Medium | High | Both work, but Claude's MEMORY.md is more transparent and controllable |

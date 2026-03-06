# Known Gaps and Limitations: Claude Code Memory

## Platform Limitations

- **MEMORY.md 200-line truncation**: The auto-loaded `MEMORY.md` file is truncated after 200 lines. Long-term memory must be kept concise with links to detail files. Detail files are not auto-loaded — they require explicit Read calls.

- **No automatic memory consolidation**: Claude Code does not automatically merge, deduplicate, or summarize memory entries across sessions. Memory maintenance is manual or instruction-driven.

- **No structured memory metadata**: Memory files are plain Markdown. There is no native support for structured fields (tags, dates, confidence scores) that would enable filtered retrieval. Parsing relies on Markdown conventions.

- **CLAUDE.md is project-scoped only**: There is no organization-level or team-level CLAUDE.md. Standards shared across multiple repos must be duplicated or managed via git submodules/symlinks.

- **Context window limits**: While Claude Code auto-compresses conversation history, very long sessions may lose early context. Working memory and short-term memory degrade in extended sessions.

- **No event-triggered memory writes**: Claude Code cannot automatically create memory entries based on external events (PR merged, CI failed, deployment completed). All writes require in-session instruction or manual triggering.

- **No memory search API**: There is no built-in search across memory files beyond Glob (filename patterns) and Grep (content search). Semantic/fuzzy search requires Track B infrastructure.

- **Session isolation**: Each Claude Code session starts fresh. There is no mechanism to "resume" a previous session's working memory. CLAUDE.md and MEMORY.md provide continuity, but conversation context does not persist.

- **No multi-user memory coordination**: Claude Code operates single-user. There is no mechanism for multiple team members' MEMORY.md preferences to be merged or for team-shared preferences to override individual ones.

- **MCP server startup latency**: Track B's MCP server adds startup time to each Claude Code session. Complex MCP servers with embedding model loading can add 5-30 seconds.

## Migration Risks from Existing Templates

The `co-pilot-memory-implementation/` templates were designed for GitHub Copilot's three modes (Ask, Edit, Agent). Adapting them to Claude Code introduces these risks:

- **Mode-specific instructions are irrelevant**: The original templates include detailed "Ask Mode", "Edit Mode", and "Agent Mode" sections. Claude Code is always an agent — it doesn't have separate modes. Strip mode-specific sections entirely.

- **Confidence scoring doesn't apply natively**: The original procedural memory defines four automation confidence levels (95%+, 80-94%, 60-79%, <60%). Claude Code doesn't have configurable confidence thresholds. Simplify to: "follow established procedures automatically, suggest alternatives for new patterns."

- **Over-engineered testing frameworks**: The original templates include quantitative test metrics (e.g., "Context Capture Accuracy > 90%", "Retrieval Relevance > 80%"). These are aspirational guidelines, not executable tests. In Claude Code, replace with qualitative validation checklists.

- **Copilot `/memories/` scopes don't exist**: The original system relies on Copilot's `/memories/`, `/memories/session/`, and `/memories/repo/` scopes. Claude Code has no equivalent native scopes. Replace with: CLAUDE.md (repo), MEMORY.md (user), conversation (session), files (permanent).

- **Cross-memory coordination hooks are manual**: The original system defines automated hooks between memory types (e.g., "episodic feeds into semantic via pattern validation"). In Claude Code, these must be instruction-based in CLAUDE.md ("after resolving a problem, check if the solution should become a semantic rule").

- **Template verbosity wastes context window**: The original templates are 500-1000+ lines each, designed as reference documentation. Loading all of them into Claude Code's context would be wasteful. Extract only the actionable rules and structures. Keep reference material in `.claude/memory/` files, read on demand.

- **Multi-perspective capture doesn't map**: Episodic memory templates include "other perspectives" and "relationship context mapping." Claude Code interacts with one user and doesn't capture team dynamics. Remove these sections.

## Capabilities Not Yet Available

- **Automatic memory versioning**: MEMORY.md changes are not tracked unless the file is in a git repo. `~/.claude/` is typically not version-controlled.

- **Memory expiration/TTL**: No way to set time-to-live on memory entries. Stale entries must be manually cleaned during maintenance.

- **Cross-project memory sharing**: MEMORY.md is per-project. Preferences that apply across all projects must be duplicated or managed at `~/.claude/CLAUDE.md` (if supported).

- **Memory import/export**: No built-in mechanism to migrate memory between projects, machines, or team members.

- **Feedback on memory quality**: No way to mark a memory entry as "helpful" or "outdated" that Claude Code would use to prioritize retrieval.

- **Automatic memory from git history**: Claude Code doesn't automatically extract memory from commit messages, PR descriptions, or issue discussions. This context must be manually captured in episodic entries.

- **Concurrent session coordination**: If multiple Claude Code sessions run simultaneously (different terminals), they may write conflicting memory entries. No locking or coordination mechanism exists.

## Workarounds

| Gap | Workaround |
|---|---|
| MEMORY.md truncation | Keep under 200 lines. Link to detail files. Read detail files explicitly when needed. |
| No structured metadata | Use consistent Markdown headers and frontmatter patterns. Parse with Grep. |
| No team-level CLAUDE.md | Use git submodules or a shared `.claude-shared/` directory synced across repos. |
| Session isolation | Write session summaries to `.claude/memory/episodic/` before ending significant sessions. |
| No memory search | Track A: Use Glob + Grep. Track B: Use MCP vector search. |
| No memory versioning for ~/.claude | Symlink `~/.claude/projects/*/memory/` to a git-tracked location. |
| No event-triggered writes | Use GitHub Actions to generate memory entry templates on events (PR merge, deploy). |
| Context window limits | Keep CLAUDE.md and MEMORY.md concise. Read detail files on demand, not preemptively. |

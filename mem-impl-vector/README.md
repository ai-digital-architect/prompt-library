# Vector Store (Track B) Memory Implementation

This folder contains Track B (vector store) implementation guides and extracted content for both GitHub Copilot and Claude Code memory architectures.

## What Is Track B?

Track B extends the file-based memory system (Track A) in `../memory-implementation-specifications/` with a vector embedding store for semantic similarity search at scale. It does not replace Track A — it adds a retrieval layer on top.

Use Track B when your project has 100+ memory entries, needs fuzzy/similarity search, or requires cross-project memory aggregation.

## Relationship to `memory-implementation-specifications/`

| Folder | Contains |
|---|---|
| `../memory-implementation-specifications/` | **Track A (file-based)** implementation guides, cross-platform comparison, memory clearing policy, and full memory architecture specifications. Cross-references here for Track B content. |
| `mem-impl-vector/` (this folder) | **Track B (vector store)** implementation guides, infrastructure setup, sync pipelines, MCP server code, and migration paths from Track A. |

## Files Moved Here

| New Location | Original Location | Notes |
|---|---|---|
| `github-copilot/track-b-vector-store-guide.md` | `memory-implementation-specifications/github-copilot/track-b-vector-store-guide.md` | Full Track B guide for Copilot (Qdrant, Pinecone, pgvector, sync pipeline, Copilot integration) |
| `github-copilot/trade-offs.md` | Extracted from `memory-implementation-specifications/github-copilot/trade-offs.md` | Track B migration path extracted; Track A/B comparison matrix remains in original |
| `claude-code/track-b-vector-store-guide.md` | `memory-implementation-specifications/claude-code/track-b-vector-store-guide.md` | Full Track B guide for Claude Code (MCP server, Qdrant, sync pipeline, CLAUDE.md integration) |
| `claude-code/trade-offs.md` | Extracted from `memory-implementation-specifications/claude-code/trade-offs.md` and `claude-memory.instructions.md` | Track B migration path and agent instructions extracted |

## Track B (Vector Store) Cross-Platform Comparison

| Aspect | GitHub Copilot | Claude Code |
|---|---|---|
| **Integration path** | Pre-fetch scripts, MCP (limited), VS Code tasks | MCP server (native tool integration) |
| **Tool visibility** | Indirect — context injection, not native tools | Direct — `memory_recall`/`memory_store` appear as tools |
| **Query initiation** | Manual or scripted pre-session | Agent can invoke during reasoning |
| **Maturity** | Emerging (Copilot MCP support is early) | Mature (MCP is core to Claude Code's extensibility) |

## Folder Structure

```
mem-impl-vector/
  README.md                         ← This file
  github-copilot/
    track-b-vector-store-guide.md   ← Qdrant/Pinecone/pgvector setup, sync pipeline, Copilot integration
    trade-offs.md                   ← Migration path: Track A → Track B (Copilot)
  claude-code/
    track-b-vector-store-guide.md   ← MCP server, Qdrant setup, sync pipeline, Claude Code integration
    trade-offs.md                   ← Migration path: Track A → Track B + agent instructions (Claude Code)
```

## Quick Navigation

- **Start here for Copilot**: [github-copilot/track-b-vector-store-guide.md](github-copilot/track-b-vector-store-guide.md)
- **Start here for Claude Code**: [claude-code/track-b-vector-store-guide.md](claude-code/track-b-vector-store-guide.md)
- **Compare Track A vs Track B (Copilot)**: [memory-implementation-specifications/github-copilot/trade-offs.md](../memory-implementation-specifications/github-copilot/trade-offs.md)
- **Compare Track A vs Track B (Claude Code)**: [memory-implementation-specifications/claude-code/trade-offs.md](../memory-implementation-specifications/claude-code/trade-offs.md)
- **Memory clearing policy**: [memory-implementation-specifications/memory-clearing-policy.md](../memory-implementation-specifications/memory-clearing-policy.md)

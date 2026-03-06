# Track B Trade-offs and Migration: Claude Code

> This file contains Track B (vector store) specific content extracted from
> [memory-implementation-specifications/claude-code/trade-offs.md](../../memory-implementation-specifications/claude-code/trade-offs.md)
> and [memory-implementation-specifications/claude-code/claude-memory.instructions.md](../../memory-implementation-specifications/claude-code/claude-memory.instructions.md).
> The full Track A vs Track B comparison matrix remains in those files.

## Migration Path: Track A → Track B

1. Start with Track A — it's the foundation regardless
2. When file-based search becomes insufficient (~100+ entries), set up infrastructure:
   - `docker compose up qdrant`
   - `ollama pull nomic-embed-text`
3. Install the MCP server: copy `.claude/scripts/memory-mcp-server.py` and configure `.claude/mcp.json`
4. Run the sync script to index existing files
5. Claude Code now has both file access AND vector search

**Critical rule**: Track A files remain the source of truth. The vector store is a derived index. Never write to the vector store without a corresponding file.

## Vector Store Integration (Track B Only)

If an MCP memory server is configured (see `.claude/mcp.json`):

- **`memory_recall(query, memory_type?, limit?)`**: Use before architectural decisions to search for relevant past context across all memory entries. Supplements file-based search with semantic similarity.
- **`memory_store(content, memory_type, title, ...)`**: Use after storing a file-based entry to also index it in the vector store. The file remains the source of truth.
- **`memory_stats()`**: Check memory health and entry counts.

The vector store is a search index, not a primary store. Always write to files first, then optionally index into the vector store.

## See Also

- [track-b-vector-store-guide.md](track-b-vector-store-guide.md) — Full setup guide (MCP server, Qdrant, sync pipeline, GitHub Actions)
- [Track A vs Track B comparison matrix](../../memory-implementation-specifications/claude-code/trade-offs.md) — Full comparison including Claude Code native advantages for Track A

# Track B Trade-offs and Migration: GitHub Copilot

> This file contains Track B (vector store) specific content extracted from
> [memory-implementation-specifications/github-copilot/trade-offs.md](../../memory-implementation-specifications/github-copilot/trade-offs.md).
> The full Track A vs Track B comparison matrix remains in that file.

## Migration Path: Track A → Track B

Track B builds on Track A. The migration is additive, not replacement:

1. Start with Track A (file-based memory in `.github/memory/`)
2. When search becomes painful (~100+ entries), add the sync pipeline
3. Deploy a vector store (start with Qdrant Docker locally)
4. Run the sync script to index existing files
5. Add the GitHub Action to auto-sync on push
6. Query the vector store alongside file-based reads

**Important**: Track A files remain the source of truth. The vector store is a derived index. If the vector store is lost, rebuild from files. Never write to the vector store without a corresponding file in Track A.

## See Also

- [track-b-vector-store-guide.md](track-b-vector-store-guide.md) — Full setup guide (Qdrant, Pinecone, pgvector, sync pipeline)
- [Track A vs Track B comparison matrix](../../memory-implementation-specifications/github-copilot/trade-offs.md) — Full comparison including Markdown vs JSON decision

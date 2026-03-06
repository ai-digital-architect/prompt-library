# Trade-offs: Track A (File-Based) vs Track B (Vector Store via MCP)

## Comparison Matrix

| Criterion | Track A (File-Based) | Track B (Vector Store via MCP) | Winner |
|---|---|---|---|
| **Setup Time** | Minutes. Create directories, write CLAUDE.md. | Hours. Deploy vector DB, build MCP server, configure embeddings. | Track A |
| **Cost** | $0. No infrastructure. | $0-200/month. Self-hosted (compute) or managed service + embedding API. | Track A |
| **Retrieval Quality (< 50 entries)** | Excellent. Glob + Read finds known files instantly. | Overkill. Semantic search adds complexity without meaningful quality gain. | Track A |
| **Retrieval Quality (50-500 entries)** | Good with organized naming. Manual browsing slows down. | Very good. Similarity search finds related entries even with different terminology. | Track B |
| **Retrieval Quality (500+ entries)** | Poor. Glob/Grep misses conceptually related entries. | Excellent. Vector similarity shines at scale. | Track B |
| **Latency** | ~0ms. Direct file read from disk. | 50-200ms per query (embedding + vector search). | Track A |
| **Version Control** | Full. All files in git. History, blame, diff all work. | Partial. Source files in git, vector index is ephemeral/rebuilt. | Track A |
| **Offline Support** | Full. No network needed. | Partial. Self-hosted + Ollama works offline. Cloud backends need network. | Track A |
| **Cross-Project Memory** | Limited. Copy files or git submodules. | Native. Single vector store indexes multiple repos. | Track B |
| **Native Integration** | Perfect. CLAUDE.md auto-loaded. Read/Write are built-in tools. | Good. MCP tools appear as native tools. Requires server process. | Track A |
| **Operability** | Minimal. Standard file operations. No monitoring. | Moderate. MCP server health, vector DB monitoring, embedding pipeline. | Track A |
| **Fuzzy/Semantic Search** | None. Exact file/keyword matching via Glob/Grep. | Full. "How did we handle X?" finds conceptually related entries. | Track B |
| **Storage Limits** | Practical limit ~500 files before navigation degrades. | 100K+ vectors. Scales to millions. | Track B |
| **Data Privacy** | Full control. Files in your repo and local disk. | Depends on backend. Self-hosted: full control. Cloud: data leaves environment. | Track A (self-hosted B ties) |
| **Maintenance Burden** | Low. Occasional file organization. | Medium. MCP server updates, embedding model updates, index rebuilds. | Track A |
| **Disaster Recovery** | Trivial. Clone repo. MEMORY.md is on local disk. | Moderate. Rebuild index from source files. | Track A |
| **Auto-loading** | CLAUDE.md + MEMORY.md loaded every session automatically. | MCP tools available but require explicit invocation. | Track A |

## Claude Code Specific Advantages for Track A

Claude Code has several features that make Track A particularly effective:

1. **Direct file access**: Unlike Copilot, Claude Code can read any file on the filesystem. No need for a retrieval layer to access memory files.
2. **Auto-loaded CLAUDE.md**: Core semantic and procedural memory is always in context. No setup needed.
3. **Auto-loaded MEMORY.md**: Long-term preferences are always available. Claude Code manages this natively.
4. **TodoWrite for working memory**: Built-in structured task tracking replaces the need for session-scoped memory stores.
5. **Conversation context**: Full conversation history serves as natural working and short-term memory with automatic compression.

## Recommendation by Profile

| Profile | Recommended Track | Rationale |
|---|---|---|
| Solo developer, any project size | Track A only | Claude Code's native file access makes Track A powerful enough |
| Small team (2-5), single repo | Track A only | File-based memory with git is sufficient |
| Medium team (5-15), growing memory | Track A primary + Track B search | Add vector search when Glob/Grep becomes insufficient |
| Large team (15+), multi-repo | Track A + Track B | Cross-project memory and semantic search are essential |
| Privacy-sensitive environment | Track A primary, self-hosted Track B only | No data leaves the network |
| Open-source project | Track A only | Zero infrastructure barrier for contributors |

## Migration Path: Track A → Track B

1. Start with Track A — it's the foundation regardless
2. When file-based search becomes insufficient (~100+ entries), set up infrastructure:
   - `docker compose up qdrant`
   - `ollama pull nomic-embed-text`
3. Install the MCP server: copy `.claude/scripts/memory-mcp-server.py` and configure `.claude/mcp.json`
4. Run the sync script to index existing files
5. Claude Code now has both file access AND vector search

**Critical rule**: Track A files remain the source of truth. The vector store is a derived index. Never write to the vector store without a corresponding file.

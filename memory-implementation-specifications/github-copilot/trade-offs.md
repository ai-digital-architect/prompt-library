# Trade-offs: Track A (File-Based) vs Track B (Vector Store)

## Comparison Matrix

| Criterion | Track A (File-Based) | Track B (Vector Store) | Winner |
|---|---|---|---|
| **Setup Time** | Minutes. Create directories and markdown files. | Hours to days. Deploy vector DB, configure embeddings, build sync pipeline. | Track A |
| **Cost** | $0. No infrastructure required. | $0-200/month. Self-hosted (server cost) or managed service (Pinecone/Qdrant Cloud). | Track A |
| **Retrieval Quality (< 50 entries)** | Excellent. Keyword search in known files is fast and accurate. | Overkill. Semantic search adds latency without meaningful quality gain. | Track A |
| **Retrieval Quality (50-500 entries)** | Good. Requires organized file structure and disciplined naming. Manual browsing becomes slow. | Very good. Semantic similarity finds related entries even with different terminology. | Track B |
| **Retrieval Quality (500+ entries)** | Poor. Keyword search misses conceptually related entries. File browsing doesn't scale. | Excellent. Vector similarity search shines at scale with fuzzy matching. | Track B |
| **Latency** | ~0ms (local file read). | 50-200ms per query (embedding generation + vector search). | Track A |
| **Version Control** | Full. All memory files tracked in git. History, blame, diff all work. | Partial. Source files in git, but vector index is ephemeral and rebuilt from files. | Track A |
| **Offline Support** | Full. No network needed. | Partial. Self-hosted Qdrant works offline. Cloud backends require network. Local embeddings (Ollama) work offline. | Track A |
| **Cross-Project Memory** | Limited. Copy files between repos or use git submodules. | Native. Single vector store indexes multiple repos. Query across all projects. | Track B |
| **Multi-User Collaboration** | Good. Git PRs for memory changes. Merge conflicts possible. | Good. Concurrent writes supported. No merge conflicts. But less visibility into changes. | Tie |
| **Operability** | Minimal. Standard git workflow. No monitoring needed. | Moderate. Vector DB monitoring, embedding pipeline health, index maintenance. | Track A |
| **Copilot Integration** | Native. `.github/instructions/` auto-loaded. `/memories/` scopes work directly. | Indirect. Requires pre-fetch scripts, MCP server, or manual context injection. | Track A |
| **Fuzzy/Semantic Search** | None. Exact keyword matching only. | Full. "How did we handle X?" finds conceptually related entries. | Track B |
| **Storage Limits** | Practical limit ~500 files before navigation degrades. Git handles thousands but human browsing doesn't. | 100K+ vectors easily. Scales to millions with managed services. | Track B |
| **Data Privacy** | Full control. Files stay in your repo. | Depends on backend. Self-hosted: full control. Cloud: data leaves your environment. | Track A (self-hosted Track B ties) |
| **Maintenance Burden** | Low. Occasional file cleanup and reorganization. | Medium. Embedding model updates, index rebuilds, sync pipeline monitoring. | Track A |
| **Disaster Recovery** | Trivial. Memory is in git. Clone the repo and you're done. | Moderate. Rebuild from git-tracked source files. Vector index is derived, not primary. | Track A |

## Recommendation by Team/Project Profile

| Profile | Recommended Track | Rationale |
|---|---|---|
| Solo developer, small project | Track A only | Zero overhead, sufficient for < 100 memories |
| Small team (2-5), single repo | Track A first, evaluate Track B at 6 months | Start simple, add vectors when search becomes painful |
| Medium team (5-15), mono-repo | Track A + Track B | File-based for authoritative source, vectors for search |
| Large team (15+), multi-repo | Track B with Track A as source | Cross-project memory essential, semantic search critical |
| Regulated environment (SOC2, HIPAA) | Track A primary, self-hosted Track B only | Data residency requirements rule out cloud vector stores |
| Open-source project | Track A only | Contributors need zero setup to participate |

## Migration Path: Track A → Track B

Track B builds on Track A. The migration is additive, not replacement:

1. Start with Track A (file-based memory in `.github/memory/`)
2. When search becomes painful (~100+ entries), add the sync pipeline
3. Deploy a vector store (start with Qdrant Docker locally)
4. Run the sync script to index existing files
5. Add the GitHub Action to auto-sync on push
6. Query the vector store alongside file-based reads

**Important**: Track A files remain the source of truth. The vector store is a derived index. If the vector store is lost, rebuild from files. Never write to the vector store without a corresponding file in Track A.

## Markdown vs JSON for Track A

### Decision Summary

All Track A memory files use **Markdown**. Episodic entries additionally use **YAML frontmatter** for structured metadata. A derived `_index.json` file enables jq-based queries on episodic entries. JSON is not used as a primary storage format for any memory type.

### Per-Memory-Type Verdict

| Memory Type | Format | Rationale |
|---|---|---|
| **Episodic** | Markdown + YAML frontmatter | Entries contain narrative (context, rationale, lessons) that is unreadable in JSON strings. Frontmatter provides structured fields (date, category, impact, tags) for scripted queries. One file per event gives clean git diffs. |
| **Semantic** | Markdown (plain) | Documentation by nature: architecture descriptions, domain models, coding standards. Queried by topic/filename, not filtered by fields. JSON would make these files un-authorable. |
| **Procedural** | Markdown (plain) | Step-by-step guides with embedded code blocks. Putting bash/TypeScript inside JSON string fields (with escape sequences) is hostile to authors and reviewers. |
| **Working** | N/A (session-only) | Not persisted to files on either platform. |
| **Short-term** | N/A (session-only) | Not persisted to files on either platform. |
| **Long-term** | Markdown (plain) | Must align with native platform format. Copilot `/memories/` are plain text. A format mismatch would add friction for no benefit. |

### Detailed Criterion Comparison

| Criterion | Markdown (+ frontmatter for episodic) | JSON |
|---|---|---|
| **Agent parseability** | Good. Agents read Markdown natively. Frontmatter is parseable YAML. | Excellent for structured data. Poor for narrative content (strings lose formatting). |
| **Human readability** | Excellent. Natural reading and authoring experience. | Poor for memory entries. Narrative in string fields, escaped newlines, no formatting. |
| **jq support** | None on raw Markdown. Full on derived `_index.json`. | Full and native. jq is built for JSON. |
| **Git diff quality** | Excellent. One file per entry, clean per-line diffs. | Poor for arrays in a single file. Adequate for one-file-per-entry JSON but still noisier than Markdown. |
| **Schema enforcement** | Moderate (YAML frontmatter keys are convention-enforced, not schema-validated). | Full (JSON Schema validation possible). |
| **Copilot compatibility** | Native. `.github/instructions/` are Markdown. `/memories/` are text. | Incompatible with native mechanisms. Would require a translation layer. |
| **Authoring friction** | Low. Standard Markdown editing. | High. Must maintain valid JSON syntax. Missing commas or quotes break the file. |

### Why Not a Hybrid (Some Types as JSON)?

A split where some memory types use JSON and others use Markdown would:

1. **Increase cognitive load**: Contributors must remember which format applies to which type.
2. **Fragment tooling**: Different read/write patterns per type. Agents need format-detection logic.
3. **Break Copilot integration**: `.github/instructions/` files must be Markdown. Native `/memories/` are text. JSON files would sit outside the native memory pipeline.
4. **Gain little**: The only memory type that benefits from structured querying (episodic) is served well by YAML frontmatter + a derived JSON index.

### The `_index.json` Compromise

For teams that need jq-based automation on episodic memory (clearing scripts, dashboards, CI reporting), a derived `_index.json` file is auto-generated from YAML frontmatter. This gives full jq queryability without changing the authoring format. See the Track A guide for the generation script and example queries.

# Track B: Vector Store Memory Implementation for Claude Code via MCP

## Overview

This track extends file-based memory (Track A) with a vector embedding store exposed to Claude Code through an MCP (Model Context Protocol) server. Claude Code gains `memory_store` and `memory_recall` tools for semantic similarity search across all memory entries.

Track B does **not** replace Track A. The `.claude/memory/` files and `CLAUDE.md` remain the source of truth. The vector store adds fuzzy retrieval at scale.

## When to Choose Track B Over Track A

| Signal | Track A Sufficient | Track B Needed |
|---|---|---|
| Memory entries | < 100 total | 100+ entries |
| Search pattern | Known file, keyword | "Find decisions similar to..." |
| Team size | 1-5 developers | 5+ developers |
| Cross-project memory | Not needed | Share patterns across repos |
| Budget | Zero | Self-hosted or $20-200/month managed |

## Step 1: Choose a Vector Store Backend

### Option A: Qdrant (Recommended for Self-Hosted)

```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:v1.12.1
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

```bash
docker compose up -d qdrant
```

### Option B: Pinecone (Managed Cloud)

```bash
pip install pinecone-client
python3 -c "
import pinecone
pc = pinecone.Pinecone(api_key='YOUR_API_KEY')
pc.create_index(
    name='claude-memory',
    dimension=1536,
    metric='cosine',
    spec=pinecone.ServerlessSpec(cloud='aws', region='us-east-1')
)
"
```

### Option C: pgvector (If You Already Use PostgreSQL)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    repo_slug VARCHAR(255),
    user_id VARCHAR(255)
);

CREATE INDEX ON memory_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX ON memory_embeddings (memory_type, repo_slug);
```

## Step 2: Choose an Embedding Model

| Model | Dimensions | Cost | Latency |
|---|---|---|---|
| `text-embedding-3-small` (OpenAI) | 1536 | $0.02/1M tokens | ~100ms |
| `nomic-embed-text` (Ollama, local) | 768 | Free | ~50ms |
| `all-MiniLM-L6-v2` (sentence-transformers) | 384 | Free | ~20ms |

**Recommendation**: `nomic-embed-text` via Ollama for privacy and zero cost. `text-embedding-3-small` for cloud setups.

```bash
# Local embedding setup
ollama pull nomic-embed-text
```

## Step 3: Build the MCP Memory Server

Claude Code connects to MCP servers defined in `.claude/mcp.json`. The MCP server exposes `memory_store` and `memory_recall` as tools.

### File: `.claude/scripts/memory-mcp-server.py`

```python
#!/usr/bin/env python3
"""
MCP server that provides memory_store and memory_recall tools to Claude Code.
Connects to a Qdrant vector store for semantic similarity search.

Usage:
    python .claude/scripts/memory-mcp-server.py
"""

import json
import hashlib
import os
import sys
from datetime import datetime

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool, TextContent

# Vector store
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
)

# Embedding
import requests


# --- Configuration ---

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "claude_memory")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "ollama")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


# --- Embedding ---

def get_embedding(text: str) -> list[float]:
    if EMBEDDING_PROVIDER == "openai":
        import openai
        client = openai.OpenAI()
        response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
        return response.data[0].embedding
    else:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
        )
        return response.json()["embedding"]


def get_vector_size() -> int:
    """Detect vector size from the embedding model."""
    test = get_embedding("test")
    return len(test)


# --- Qdrant ---

qdrant = QdrantClient(url=QDRANT_URL)


def ensure_collection():
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in collections:
        size = get_vector_size()
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# --- MCP Server ---

server = Server("memory-server")


@server.tool("memory_store")
async def memory_store(
    content: str,
    memory_type: str,
    title: str = "",
    category: str = "",
    tags: list[str] | None = None,
    impact: str = "medium",
    repo_slug: str = "",
) -> list[TextContent]:
    """
    Store a memory entry in the vector store.

    Args:
        content: The memory content to store.
        memory_type: One of: episodic, semantic, procedural, long_term.
        title: Short title for the memory.
        category: Category code (e.g., ARCH, TECH, INC for episodic).
        tags: List of tags for filtering.
        impact: Impact level (critical, high, medium, low).
        repo_slug: Repository identifier.
    """
    ensure_collection()

    embed_text = f"{title} {content}" if title else content
    embedding = get_embedding(embed_text)

    point_id = content_hash(content)
    payload = {
        "memory_type": memory_type,
        "title": title,
        "content": content,
        "category": category,
        "tags": tags or [],
        "impact": impact,
        "repo_slug": repo_slug,
        "created_at": datetime.utcnow().isoformat(),
    }

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=point_id, vector=embedding, payload=payload)],
    )

    return [TextContent(
        type="text",
        text=f"Stored {memory_type} memory: '{title or content[:50]}' (id: {point_id})"
    )]


@server.tool("memory_recall")
async def memory_recall(
    query: str,
    memory_type: str = "",
    limit: int = 5,
    min_score: float = 0.7,
) -> list[TextContent]:
    """
    Recall memories similar to the query using semantic search.

    Args:
        query: Natural language query to search for.
        memory_type: Filter by type (episodic, semantic, procedural, long_term). Empty for all.
        limit: Maximum number of results.
        min_score: Minimum similarity score (0.0 to 1.0).
    """
    ensure_collection()

    query_embedding = get_embedding(query)

    query_filter = None
    if memory_type:
        query_filter = Filter(must=[
            FieldCondition(key="memory_type", match=MatchValue(value=memory_type))
        ])

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=limit,
    )

    if not results:
        return [TextContent(type="text", text="No matching memories found.")]

    output_lines = []
    for i, result in enumerate(results, 1):
        if result.score < min_score:
            continue
        p = result.payload
        output_lines.append(
            f"{i}. [{p.get('memory_type', '?')}] {p.get('title', 'Untitled')} "
            f"(score: {result.score:.3f})\n"
            f"   Category: {p.get('category', '-')} | Impact: {p.get('impact', '-')} | "
            f"Tags: {', '.join(p.get('tags', []))}\n"
            f"   {p.get('content', '')[:300]}\n"
        )

    if not output_lines:
        return [TextContent(type="text", text=f"No memories above score threshold {min_score}.")]

    return [TextContent(
        type="text",
        text=f"Found {len(output_lines)} matching memories:\n\n" + "\n".join(output_lines)
    )]


@server.tool("memory_stats")
async def memory_stats() -> list[TextContent]:
    """Get statistics about stored memories."""
    ensure_collection()

    info = qdrant.get_collection(collection_name=COLLECTION_NAME)
    count = info.points_count

    # Get counts by type
    type_counts = {}
    for mtype in ["episodic", "semantic", "procedural", "long_term"]:
        results = qdrant.count(
            collection_name=COLLECTION_NAME,
            count_filter=Filter(must=[
                FieldCondition(key="memory_type", match=MatchValue(value=mtype))
            ]),
        )
        type_counts[mtype] = results.count

    lines = [
        f"Total memories: {count}",
        f"  Episodic: {type_counts.get('episodic', 0)}",
        f"  Semantic: {type_counts.get('semantic', 0)}",
        f"  Procedural: {type_counts.get('procedural', 0)}",
        f"  Long-term: {type_counts.get('long_term', 0)}",
    ]

    return [TextContent(type="text", text="\n".join(lines))]


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_server(server))
```

### Requirements File: `.claude/scripts/requirements.txt`

```
mcp>=1.0.0
qdrant-client>=1.12.0
requests>=2.31.0
```

## Step 4: Configure the MCP Server

### File: `.claude/mcp.json`

```json
{
  "servers": {
    "memory": {
      "command": "python3",
      "args": [".claude/scripts/memory-mcp-server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "claude_memory",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "OLLAMA_URL": "http://localhost:11434"
      }
    }
  }
}
```

For OpenAI embeddings instead:

```json
{
  "servers": {
    "memory": {
      "command": "python3",
      "args": [".claude/scripts/memory-mcp-server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "claude_memory",
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## Step 5: Build the Sync Pipeline

Index existing Track A files into the vector store.

### File: `.claude/scripts/sync-memory-to-vector.py`

```python
#!/usr/bin/env python3
"""
Sync .claude/memory/ files to the vector store.

Usage:
    python .claude/scripts/sync-memory-to-vector.py
    python .claude/scripts/sync-memory-to-vector.py --dry-run
"""

import argparse
import hashlib
import os
import re
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Reuse embedding from MCP server
import sys
sys.path.insert(0, os.path.dirname(__file__))


QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("COLLECTION_NAME", "claude_memory")
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "ollama")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")


def get_embedding(text: str) -> list[float]:
    if EMBEDDING_PROVIDER == "openai":
        import openai
        client = openai.OpenAI()
        response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
        return response.data[0].embedding
    else:
        import requests
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
        )
        return response.json()["embedding"]


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def parse_episodic(path: Path) -> dict | None:
    content = path.read_text()
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    date_match = re.search(r'\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    category_match = re.search(r'\*\*Category\*\*:\s*(\w+)', content)
    impact_match = re.search(r'\*\*Impact\*\*:\s*(\w+)', content)

    return {
        "memory_type": "episodic",
        "title": title_match.group(1) if title_match else path.stem,
        "content": content,
        "category": category_match.group(1) if category_match else "",
        "impact": (impact_match.group(1).lower() if impact_match else "medium"),
        "tags": [],
        "source_file": str(path),
    }


def parse_sections(path: Path, memory_type: str) -> list[dict]:
    content = path.read_text()
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    entries = []
    for section in sections[1:]:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if body:
            entries.append({
                "memory_type": memory_type,
                "title": title,
                "content": body,
                "category": "",
                "impact": "medium",
                "tags": [],
                "source_file": str(path),
            })
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-root", default=".claude/memory")
    parser.add_argument("--repo-slug", default=os.environ.get("GITHUB_REPOSITORY", "local/repo"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.memory_root)
    entries = []

    # Episodic
    for f in sorted((root / "episodic").glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        entry = parse_episodic(f)
        if entry:
            entry["repo_slug"] = args.repo_slug
            entries.append(entry)

    # Semantic
    for f in sorted((root / "semantic").glob("*.md")):
        for entry in parse_sections(f, "semantic"):
            entry["repo_slug"] = args.repo_slug
            entries.append(entry)

    # Procedural
    for f in sorted((root / "procedural").glob("*.md")):
        for entry in parse_sections(f, "procedural"):
            entry["repo_slug"] = args.repo_slug
            entries.append(entry)

    print(f"Found {len(entries)} entries to index.")

    if args.dry_run:
        for e in entries:
            print(f"  [{e['memory_type']}] {e['title']}")
        return

    # Generate embeddings
    for entry in entries:
        embed_text = f"{entry['title']} {entry['content']}"
        entry["embedding"] = get_embedding(embed_text)

    # Upsert to Qdrant
    client = QdrantClient(url=QDRANT_URL)
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        dim = len(entries[0]["embedding"])
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    points = []
    for entry in entries:
        embedding = entry.pop("embedding")
        points.append(PointStruct(
            id=content_hash(entry["content"]),
            vector=embedding,
            payload=entry,
        ))

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Indexed {len(points)} entries into '{COLLECTION}'.")


if __name__ == "__main__":
    main()
```

## Step 6: Update CLAUDE.md for Vector Store Integration

Add to your `CLAUDE.md`:

```markdown
## Vector Memory (MCP)
This project has a vector memory store accessible via MCP tools:
- `memory_recall(query, memory_type?, limit?)` — Find memories similar to a query
- `memory_store(content, memory_type, title, category?, tags?)` — Store a new memory
- `memory_stats()` — Get memory entry counts

Use `memory_recall` before architectural decisions to check for relevant past decisions.
Use `memory_store` after significant decisions to record them for future recall.

The vector store supplements file-based memory in `.claude/memory/`. For authoritative
records, always write to files. The vector store is a derived search index.
```

## Step 7: Automate Sync with GitHub Actions

### File: `.github/workflows/sync-claude-memory.yml`

```yaml
name: Sync Claude Memory to Vector Store

on:
  push:
    branches: [main]
    paths:
      - '.claude/memory/**'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    services:
      qdrant:
        image: qdrant/qdrant:v1.12.1
        ports:
          - 6333:6333
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install qdrant-client requests openai
      - name: Sync memories
        env:
          QDRANT_URL: http://localhost:6333
          EMBEDDING_PROVIDER: openai
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python .claude/scripts/sync-memory-to-vector.py --repo-slug ${{ github.repository }}
```

## Step 8: Validate the Setup

### Validation Steps

```bash
# 1. Start infrastructure
docker compose up -d qdrant
ollama serve &
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip install -r .claude/scripts/requirements.txt

# 3. Sync existing memory files
python .claude/scripts/sync-memory-to-vector.py

# 4. Test MCP server manually
echo '{"method": "tools/list"}' | python .claude/scripts/memory-mcp-server.py

# 5. Start Claude Code — it should load the MCP server from .claude/mcp.json
claude

# 6. Test in Claude Code session:
#    - Ask: "What past architectural decisions have we made?"
#    - Claude Code should use memory_recall tool
#    - Ask: "Record that we decided to use Redis for caching"
#    - Claude Code should use memory_store tool
```

## Working Example: Semantic Recall at Scale

### Scenario: 200+ episodic memories over 18 months

**Query**: "How have we handled breaking changes in our API?"

**Track A alone**: Grep through `.claude/memory/episodic/` files. Finds exact matches for "breaking changes" but misses entries about "API versioning", "deprecation policy", or "backward compatibility."

**Track B (vector search)**:

```
Claude Code uses memory_recall("handling breaking API changes", memory_type="episodic", limit=3)

Results:
1. [episodic] API v2 Migration Strategy (score: 0.912)
   Category: ARCH | Impact: high
   Decided on 6-month deprecation window with sunset headers...

2. [episodic] Payment API Contract Change Incident (score: 0.887)
   Category: INC | Impact: critical
   Breaking change in payment processor webhook caused 2-hour outage...

3. [episodic] GraphQL Schema Evolution Policy (score: 0.845)
   Category: ARCH | Impact: medium
   Adopted @deprecated directive with minimum 3-release deprecation cycle...
```

Claude Code incorporates these memories into its response, providing historically-grounded guidance.

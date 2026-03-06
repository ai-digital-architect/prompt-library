# Track B: Vector Store Memory Implementation for GitHub Copilot

## Overview

This track extends the file-based memory system (Track A) with a vector embedding store for semantic retrieval at scale. Use this when your project has hundreds of memory entries, needs fuzzy/similarity search, or requires cross-project memory aggregation.

Track B does **not** replace Track A. It adds a retrieval layer on top. The `.github/instructions/` files and `/memories/` scopes still function as primary context. The vector store handles overflow and similarity-based recall.

## When to Choose Track B Over Track A

| Signal | Track A Sufficient | Track B Needed |
|---|---|---|
| Memory entries | < 100 total | 100+ entries |
| Search pattern | Exact keyword, known file | "Find decisions similar to..." |
| Team size | 1-5 developers | 5+ developers |
| Cross-project memory | Not needed | Share patterns across repos |
| Budget | Zero | $20-200/month or self-hosted |
| Setup time | Minutes | Hours to days |

## Step 1: Choose a Vector Store Backend

### Option A: Qdrant (Recommended for Self-Hosted)

```yaml
# docker-compose.yml (add to your project or run standalone)
services:
  qdrant:
    image: qdrant/qdrant:v1.12.1
    ports:
      - "6333:6333"    # REST API
      - "6334:6334"    # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

volumes:
  qdrant_data:
```

**Pros**: Free, local, no data leaves your machine, fast.
**Cons**: You manage the infrastructure.

### Option B: Pinecone (Managed Cloud)

```bash
# Install Pinecone CLI
pip install pinecone-client

# Create index (run once)
python3 -c "
import pinecone
pc = pinecone.Pinecone(api_key='YOUR_API_KEY')
pc.create_index(
    name='copilot-memory',
    dimension=1536,  # text-embedding-3-small
    metric='cosine',
    spec=pinecone.ServerlessSpec(cloud='aws', region='us-east-1')
)
"
```

**Pros**: Zero ops, scales automatically, free tier available (100K vectors).
**Cons**: Data in cloud, latency for retrieval, costs at scale.

### Option C: pgvector (If You Already Use PostgreSQL)

```sql
-- Run in your PostgreSQL database
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type VARCHAR(20) NOT NULL, -- episodic, semantic, procedural, long_term
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    repo_slug VARCHAR(255),
    user_id VARCHAR(255)
);

-- HNSW index for fast similarity search
CREATE INDEX ON memory_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Index for filtering by type and repo
CREATE INDEX ON memory_embeddings (memory_type, repo_slug);
```

**Pros**: No new infrastructure if you have PostgreSQL, SQL-native queries.
**Cons**: Scaling limits vs purpose-built vector DBs, manual index tuning.

## Step 2: Choose an Embedding Model

| Model | Dimensions | Cost | Quality | Latency |
|---|---|---|---|---|
| `text-embedding-3-small` (OpenAI) | 1536 | $0.02/1M tokens | Good | ~100ms |
| `text-embedding-3-large` (OpenAI) | 3072 | $0.13/1M tokens | Best | ~150ms |
| `nomic-embed-text` (local, Ollama) | 768 | Free | Good | ~50ms local |
| `all-MiniLM-L6-v2` (local, sentence-transformers) | 384 | Free | Adequate | ~20ms local |

**Recommendation**: `text-embedding-3-small` for cloud setups, `nomic-embed-text` via Ollama for local/private setups.

### Local Embedding Setup (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Test embedding generation
curl http://localhost:11434/api/embeddings \
  -d '{"model": "nomic-embed-text", "prompt": "Architecture decision: use microservices"}'
```

### OpenAI Embedding Setup

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Test embedding
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "Architecture decision: use microservices", "model": "text-embedding-3-small"}'
```

## Step 3: Design the Schema Per Memory Type

### Collection/Table Schema

```json
{
  "collection_name": "copilot_memory",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "memory_type": { "type": "keyword", "values": ["episodic", "semantic", "procedural", "long_term"] },
    "category": { "type": "keyword" },
    "repo_slug": { "type": "keyword" },
    "user_id": { "type": "keyword" },
    "date": { "type": "datetime" },
    "impact": { "type": "keyword", "values": ["critical", "high", "medium", "low"] },
    "confidence": { "type": "float" },
    "title": { "type": "text" },
    "content": { "type": "text" },
    "tags": { "type": "keyword" },
    "related_ids": { "type": "keyword" },
    "source_file": { "type": "keyword" }
  }
}
```

### Memory Type Specific Payloads

**Episodic**:
```json
{
  "memory_type": "episodic",
  "category": "ARCH",
  "repo_slug": "myorg/myrepo",
  "date": "2025-01-15T00:00:00Z",
  "impact": "high",
  "title": "Adopted pgroll for zero-downtime migrations",
  "content": "Team decided to use pgroll for database migrations after evaluating manual expand-contract and feature flags. First migration completed with zero downtime, reducing migration time from 15min to 45sec.",
  "tags": ["database", "migration", "architecture"],
  "related_ids": ["issue-142"],
  "source_file": ".github/memory/episodic/2025-01-15-database-migration-strategy.md"
}
```

**Semantic**:
```json
{
  "memory_type": "semantic",
  "category": "standard",
  "repo_slug": "myorg/myrepo",
  "title": "API Response Format",
  "content": "All API responses must use the shape { data: T, error?: { code: string, message: string }, meta?: { page: number, total: number } }. Authentication uses Bearer JWT. Rate limit: 100 req/min per user.",
  "tags": ["api", "standards", "rest"],
  "confidence": 1.0,
  "source_file": ".github/instructions/project-knowledge.instructions.md"
}
```

**Procedural**:
```json
{
  "memory_type": "procedural",
  "category": "workflow",
  "title": "Feature Branch Workflow",
  "content": "1. Branch from main as feat/ISSUE-short-desc. 2. Draft PR immediately. 3. Conventional commits. 4. Request review after CI green. 5. Squash-merge. 6. Delete branch.",
  "tags": ["git", "workflow", "feature"],
  "confidence": 0.95
}
```

**Long-term**:
```json
{
  "memory_type": "long_term",
  "category": "preference",
  "user_id": "user-123",
  "title": "Coding Style Preferences",
  "content": "Prefers early returns over nested conditionals. Descriptive variable names over comments. Small functions (< 20 lines). Composition over inheritance.",
  "tags": ["style", "preference"],
  "confidence": 0.9
}
```

## Step 4: Build the Sync Pipeline

The sync pipeline reads Track A files and indexes them into the vector store.

### Sync Script: `.github/scripts/sync-memory-to-vector.py`

```python
#!/usr/bin/env python3
"""
Sync .github/memory/ files to vector store.
Run on commit or on a schedule.

Usage:
    python .github/scripts/sync-memory-to-vector.py --backend qdrant
    python .github/scripts/sync-memory-to-vector.py --backend pinecone
    python .github/scripts/sync-memory-to-vector.py --backend pgvector
"""

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# --- Embedding ---

def get_embedding_openai(text: str, model: str = "text-embedding-3-small") -> list[float]:
    import openai
    client = openai.OpenAI()
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding

def get_embedding_ollama(text: str, model: str = "nomic-embed-text") -> list[float]:
    import requests
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text},
    )
    return response.json()["embedding"]

def get_embedding(text: str) -> list[float]:
    provider = os.environ.get("EMBEDDING_PROVIDER", "ollama")
    if provider == "openai":
        return get_embedding_openai(text)
    return get_embedding_ollama(text)

# --- File Parsing ---

def parse_episodic_file(path: Path) -> dict[str, Any]:
    content = path.read_text()
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    date_match = re.search(r'\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    category_match = re.search(r'\*\*Category\*\*:\s*(\w+)', content)
    impact_match = re.search(r'\*\*Impact\*\*:\s*(\w+)', content)

    return {
        "memory_type": "episodic",
        "category": category_match.group(1) if category_match else "UNKNOWN",
        "date": date_match.group(1) if date_match else None,
        "impact": impact_match.group(1).lower() if impact_match else "medium",
        "title": title_match.group(1) if title_match else path.stem,
        "content": content,
        "tags": extract_tags(content),
        "source_file": str(path),
    }

def parse_semantic_file(path: Path) -> list[dict[str, Any]]:
    content = path.read_text()
    # Split by H2 headings to create separate entries per section
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    entries = []
    for section in sections[1:]:  # skip preamble
        lines = section.strip().split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if body:
            entries.append({
                "memory_type": "semantic",
                "category": "knowledge",
                "title": title,
                "content": body,
                "tags": extract_tags(body),
                "confidence": 1.0,
                "source_file": str(path),
            })
    return entries

def parse_procedural_file(path: Path) -> list[dict[str, Any]]:
    content = path.read_text()
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    entries = []
    for section in sections[1:]:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if body:
            entries.append({
                "memory_type": "procedural",
                "category": "workflow",
                "title": title,
                "content": body,
                "tags": extract_tags(body),
                "confidence": 0.95,
                "source_file": str(path),
            })
    return entries

def extract_tags(text: str) -> list[str]:
    """Extract potential tags from content based on common technical terms."""
    tag_patterns = [
        r'(?:TypeScript|JavaScript|Python|Go|Rust|Java)',
        r'(?:React|Next\.js|Express|FastAPI|Django)',
        r'(?:PostgreSQL|MongoDB|Redis|MySQL)',
        r'(?:AWS|GCP|Azure|Docker|Kubernetes)',
        r'(?:REST|GraphQL|gRPC)',
        r'(?:CI/CD|GitHub Actions|deployment|migration)',
        r'(?:authentication|authorization|security)',
        r'(?:testing|performance|optimization)',
    ]
    tags = set()
    for pattern in tag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        tags.update(m.lower() for m in matches)
    return list(tags)

def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]

# --- Vector Store Backends ---

def upsert_qdrant(entries: list[dict], collection: str = "copilot_memory"):
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance

    client = QdrantClient(url="http://localhost:6333")

    # Ensure collection exists
    collections = [c.name for c in client.get_collections().collections]
    if collection not in collections:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=len(entries[0]["embedding"]), distance=Distance.COSINE),
        )

    points = []
    for entry in entries:
        point_id = content_hash(entry["content"])
        embedding = entry.pop("embedding")
        points.append(PointStruct(id=point_id, vector=embedding, payload=entry))

    client.upsert(collection_name=collection, points=points)
    print(f"Upserted {len(points)} points to Qdrant collection '{collection}'")

def upsert_pinecone(entries: list[dict], index_name: str = "copilot-memory"):
    import pinecone
    pc = pinecone.Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(index_name)

    vectors = []
    for entry in entries:
        vid = content_hash(entry["content"])
        embedding = entry.pop("embedding")
        vectors.append({"id": vid, "values": embedding, "metadata": entry})

    # Upsert in batches of 100
    for i in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[i:i+100])
    print(f"Upserted {len(vectors)} vectors to Pinecone index '{index_name}'")

def upsert_pgvector(entries: list[dict], conn_string: str = None):
    import psycopg2
    conn_string = conn_string or os.environ.get(
        "DATABASE_URL", "postgresql://localhost:5432/memory"
    )
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    for entry in entries:
        embedding = entry.pop("embedding")
        cur.execute(
            """
            INSERT INTO memory_embeddings (id, memory_type, content, metadata, embedding, repo_slug)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
            """,
            (
                entry["memory_type"],
                entry["content"],
                json.dumps(entry),
                embedding,
                entry.get("repo_slug", ""),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Upserted {len(entries)} rows to pgvector")

# --- Main ---

def collect_entries(memory_root: Path, repo_slug: str) -> list[dict]:
    entries = []

    # Episodic
    episodic_dir = memory_root / "episodic"
    if episodic_dir.exists():
        for f in episodic_dir.glob("*.md"):
            if f.name == "TEMPLATE.md":
                continue
            entry = parse_episodic_file(f)
            entry["repo_slug"] = repo_slug
            entries.append(entry)

    # Semantic
    semantic_dir = memory_root / "semantic"
    if semantic_dir.exists():
        for f in semantic_dir.glob("*.md"):
            for entry in parse_semantic_file(f):
                entry["repo_slug"] = repo_slug
                entries.append(entry)

    # Also index instruction files
    instructions_dir = memory_root.parent / "instructions"
    if instructions_dir.exists():
        for f in instructions_dir.glob("*.instructions.md"):
            for entry in parse_semantic_file(f):
                entry["repo_slug"] = repo_slug
                entries.append(entry)

    # Procedural
    procedural_dir = memory_root / "procedural"
    if procedural_dir.exists():
        for f in procedural_dir.glob("*.md"):
            for entry in parse_procedural_file(f):
                entry["repo_slug"] = repo_slug
                entries.append(entry)

    return entries

def main():
    parser = argparse.ArgumentParser(description="Sync memory files to vector store")
    parser.add_argument("--backend", choices=["qdrant", "pinecone", "pgvector"], default="qdrant")
    parser.add_argument("--repo-slug", default=os.environ.get("GITHUB_REPOSITORY", "local/repo"))
    parser.add_argument("--memory-root", default=".github/memory")
    args = parser.parse_args()

    memory_root = Path(args.memory_root)
    if not memory_root.exists():
        print(f"Memory root {memory_root} not found. Nothing to sync.")
        return

    entries = collect_entries(memory_root, args.repo_slug)
    if not entries:
        print("No memory entries found. Nothing to sync.")
        return

    print(f"Found {len(entries)} memory entries. Generating embeddings...")

    for entry in entries:
        # Combine title and content for embedding
        embed_text = f"{entry.get('title', '')} {entry['content']}"
        entry["embedding"] = get_embedding(embed_text)

    upsert_fn = {
        "qdrant": upsert_qdrant,
        "pinecone": upsert_pinecone,
        "pgvector": upsert_pgvector,
    }[args.backend]

    upsert_fn(entries)
    print("Sync complete.")

if __name__ == "__main__":
    main()
```

## Step 5: Build the Query Interface

### Query Script: `.github/scripts/query-memory.py`

```python
#!/usr/bin/env python3
"""
Query the vector memory store for similar memories.

Usage:
    python .github/scripts/query-memory.py "How did we handle database migrations?"
    python .github/scripts/query-memory.py --type episodic "payment failures"
    python .github/scripts/query-memory.py --type semantic "API standards"
"""

import argparse
import json
import os
import sys

# Reuse embedding function from sync script
sys.path.insert(0, os.path.dirname(__file__))
from sync_memory_to_vector import get_embedding


def query_qdrant(query_embedding: list[float], memory_type: str = None,
                 limit: int = 5, collection: str = "copilot_memory") -> list[dict]:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = QdrantClient(url="http://localhost:6333")

    query_filter = None
    if memory_type:
        query_filter = Filter(must=[
            FieldCondition(key="memory_type", match=MatchValue(value=memory_type))
        ])

    results = client.search(
        collection_name=collection,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=limit,
    )

    return [{"score": r.score, **r.payload} for r in results]


def query_pinecone(query_embedding: list[float], memory_type: str = None,
                   limit: int = 5, index_name: str = "copilot-memory") -> list[dict]:
    import pinecone
    pc = pinecone.Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(index_name)

    filter_dict = {}
    if memory_type:
        filter_dict["memory_type"] = {"$eq": memory_type}

    results = index.query(
        vector=query_embedding,
        top_k=limit,
        include_metadata=True,
        filter=filter_dict if filter_dict else None,
    )

    return [{"score": m.score, **m.metadata} for m in results.matches]


def query_pgvector(query_embedding: list[float], memory_type: str = None,
                   limit: int = 5) -> list[dict]:
    import psycopg2
    conn_string = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/memory")
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    if memory_type:
        cur.execute(
            """
            SELECT content, metadata, 1 - (embedding <=> %s::vector) as score
            FROM memory_embeddings
            WHERE memory_type = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, memory_type, query_embedding, limit),
        )
    else:
        cur.execute(
            """
            SELECT content, metadata, 1 - (embedding <=> %s::vector) as score
            FROM memory_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, limit),
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"content": r[0], "score": r[2], **json.loads(r[1])} for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Query vector memory store")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument("--type", choices=["episodic", "semantic", "procedural", "long_term"],
                        help="Filter by memory type")
    parser.add_argument("--backend", choices=["qdrant", "pinecone", "pgvector"], default="qdrant")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    query_embedding = get_embedding(args.query)

    query_fn = {
        "qdrant": query_qdrant,
        "pinecone": query_pinecone,
        "pgvector": query_pgvector,
    }[args.backend]

    results = query_fn(query_embedding, memory_type=args.type, limit=args.limit)

    print(f"\n--- Top {len(results)} results for: '{args.query}' ---\n")
    for i, result in enumerate(results, 1):
        score = result.get("score", 0)
        title = result.get("title", "Untitled")
        mtype = result.get("memory_type", "unknown")
        source = result.get("source_file", "")
        print(f"{i}. [{mtype}] {title} (score: {score:.3f})")
        if source:
            print(f"   Source: {source}")
        print(f"   {result.get('content', '')[:200]}...")
        print()


if __name__ == "__main__":
    main()
```

## Step 6: Automate Sync with GitHub Actions

### File: `.github/workflows/sync-memory.yml`

```yaml
name: Sync Memory to Vector Store

on:
  push:
    branches: [main]
    paths:
      - '.github/memory/**'
      - '.github/instructions/**'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install openai qdrant-client pinecone-client psycopg2-binary

      - name: Sync memory entries
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          EMBEDDING_PROVIDER: openai
          GITHUB_REPOSITORY: ${{ github.repository }}
          # Choose one backend and set its config:
          # PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          # DATABASE_URL: ${{ secrets.DATABASE_URL }}
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
        run: |
          python .github/scripts/sync-memory-to-vector.py \
            --backend qdrant \
            --repo-slug ${{ github.repository }}
```

## Step 7: Integrate with Copilot Chat

Copilot cannot directly query the vector store natively. Integration happens through a **retrieval-augmented context** approach:

### Approach A: Pre-fetch and Inject via Instructions

Before a coding session, query the vector store for relevant context and add it to a temporary instructions file:

```bash
# Pre-session context injection
python .github/scripts/query-memory.py "current sprint goals" --limit 3 > /tmp/context.md
python .github/scripts/query-memory.py "recent architectural decisions" --type episodic --limit 3 >> /tmp/context.md

# Copilot will pick up .github/instructions/ files automatically
cp /tmp/context.md .github/instructions/session-context.instructions.md
```

### Approach B: MCP Server (Copilot MCP Support)

If your Copilot version supports MCP (Model Context Protocol) servers, you can expose the vector store as an MCP tool:

```json
// .vscode/mcp.json
{
  "servers": {
    "memory": {
      "command": "python",
      "args": [".github/scripts/memory-mcp-server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "EMBEDDING_PROVIDER": "ollama"
      }
    }
  }
}
```

The MCP server script would expose `recall_memory(query, type, limit)` and `store_memory(content, type, metadata)` as tools.

### Approach C: VS Code Extension Command

Create a VS Code task that queries memory and copies results to clipboard:

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Query Memory",
      "type": "shell",
      "command": "python .github/scripts/query-memory.py '${input:query}' --type ${input:memoryType} --limit 5",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "query",
      "type": "promptString",
      "description": "What are you looking for?"
    },
    {
      "id": "memoryType",
      "type": "pickString",
      "description": "Memory type filter",
      "options": ["episodic", "semantic", "procedural", "long_term", "all"],
      "default": "all"
    }
  ]
}
```

## Step 8: Validate the Setup

### Validation Script

```bash
#!/bin/bash
# .github/scripts/validate-vector-setup.sh

echo "=== Vector Memory Validation ==="

# 1. Check vector store connectivity
echo -n "Vector store connection: "
curl -s http://localhost:6333/collections | grep -q "copilot_memory" && echo "OK" || echo "FAIL"

# 2. Check embedding generation
echo -n "Embedding generation: "
python3 -c "
from sync_memory_to_vector import get_embedding
e = get_embedding('test')
print(f'OK ({len(e)} dimensions)')
" 2>/dev/null || echo "FAIL"

# 3. Check entry count
echo -n "Indexed entries: "
curl -s http://localhost:6333/collections/copilot_memory | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['result']['points_count'])
" 2>/dev/null || echo "FAIL"

# 4. Test query
echo -n "Query test: "
python3 .github/scripts/query-memory.py "architecture decisions" --limit 1 2>/dev/null | head -3

echo "=== Validation Complete ==="
```

## Working Example: Semantic Recall at Scale

### Scenario: 500+ episodic memories across 2 years

**Problem**: Developer asks "How have we handled breaking API changes in the past?"

**Track A alone**: Would require manually searching through `.github/memory/episodic/` files. Keyword search misses entries that describe the concept without using the exact phrase "breaking API changes."

**Track B adds**: Semantic similarity search finds related entries:

```
$ python .github/scripts/query-memory.py "handling breaking API changes" --type episodic --limit 3

--- Top 3 results for: 'handling breaking API changes' ---

1. [episodic] API v2 Migration Strategy (score: 0.912)
   Source: .github/memory/episodic/2024-06-20-api-v2-migration.md
   Decided on 6-month deprecation window with sunset headers. All v1 endpoints get...

2. [episodic] Payment API Contract Change Incident (score: 0.887)
   Source: .github/memory/episodic/2024-09-03-payment-api-breakage.md
   Breaking change in payment processor webhook format caused 2-hour outage. Root cause...

3. [episodic] GraphQL Schema Evolution Policy (score: 0.845)
   Source: .github/memory/episodic/2025-01-10-graphql-schema-policy.md
   Adopted @deprecated directive with minimum 3-release deprecation cycle. Automated...
```

Copilot can now use these retrieved memories as context for its response, providing historically-informed guidance.

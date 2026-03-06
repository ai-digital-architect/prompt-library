# GitHub Copilot Memory Architecture Implementation

## Overview

This guide provides a complete memory architecture for GitHub Copilot that integrates six cognitive memory paradigms with Copilot's native `@copilot` memory system. It bridges the gap between the theoretical memory frameworks in `co-pilot-memory-implementation/` and Copilot's production capabilities.

## Memory Type Mapping Summary

| Memory Type | Purpose | Native Copilot Scope | Primary Mechanism |
|---|---|---|---|
| **Episodic** | Event/decision recall | `/memories/repo/` | Repo-scoped memory entries |
| **Semantic** | Facts, rules, standards | `/memories/repo/` + `.github/instructions/` | Instruction files + repo memories |
| **Procedural** | Automated workflows | `/memories/` (user) + `.github/instructions/` | Skill files + user memories |
| **Working** | Active problem-solving | `/memories/session/` | Session-scoped entries |
| **Short-term** | Session context | `/memories/session/` | Session-scoped entries |
| **Long-term** | Persistent preferences | `/memories/` (user) | User-scoped memories |

## Implementation Tracks

- **Track A (File-based)**: Zero infrastructure. Markdown files in the repository + native `/memories/` scopes. Version-controllable, works offline.
- **Track B (Vector store)**: External embedding store (Qdrant/Pinecone/pgvector) for semantic retrieval at scale. See [mem-impl-vector/github-copilot/](../../mem-impl-vector/github-copilot/) for the full Track B implementation guide.

## File Index

| File | Description |
|---|---|
| [memory-type-mapping.md](memory-type-mapping.md) | Detailed mapping of each memory type to Copilot primitives |
| [track-a-file-based-guide.md](track-a-file-based-guide.md) | Step-by-step file-based implementation |
| [track-b-vector-store-guide.md](../../mem-impl-vector/github-copilot/track-b-vector-store-guide.md) | Step-by-step vector store implementation (moved to mem-impl-vector/) |
| [copilot-memory.instructions.md](copilot-memory.instructions.md) | Drop-in `.instructions.md` for any repository |
| [copilot-memory.skill.md](copilot-memory.skill.md) | SKILL.md file for memory operations |
| [trade-offs.md](trade-offs.md) | Track A vs Track B comparison |
| [known-gaps.md](known-gaps.md) | Limitations and migration risks |

## Quick Start

1. Read [memory-type-mapping.md](memory-type-mapping.md) to understand how each memory type maps to Copilot
2. Choose Track A or Track B based on [trade-offs.md](trade-offs.md)
3. Follow the chosen track's guide step by step
4. Copy [copilot-memory.instructions.md](copilot-memory.instructions.md) into your repository's `.github/instructions/` folder
5. Optionally add [copilot-memory.skill.md](copilot-memory.skill.md) to `.github/skills/`

## Prerequisites

- GitHub Copilot with `@copilot` memory enabled (GA as of early 2025)
- VS Code or compatible IDE with Copilot extension
- For Track B: Docker (for self-hosted vector store) or cloud account (for managed service)

## Native Copilot Memory Primer

GitHub Copilot's native memory system (`@copilot` memory) provides three scopes:

| Scope | Path | Persistence | Visibility | Write Access |
|---|---|---|---|---|
| **User** | `/memories/` | Permanent (until deleted) | All repos, all sessions | User + Copilot |
| **Session** | `/memories/session/` | Current conversation only | Current session | User + Copilot |
| **Repo** | `/memories/repo/` | Permanent per-repo | This repo only | Copilot (create-only) |

**Operations**: `view`, `create`, `str_replace`, `insert`, `delete`, `rename` (repo scope is create-only by Copilot).

These scopes map directly to memory persistence needs: session-scoped for volatile memory (working, short-term), repo-scoped for project knowledge (episodic, semantic), and user-scoped for personal patterns (long-term, procedural).

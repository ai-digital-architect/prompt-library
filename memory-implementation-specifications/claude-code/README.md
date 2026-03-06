# Claude Code Memory Architecture Implementation

## Overview

This guide provides a complete memory architecture for Claude Code that integrates six cognitive memory paradigms with Claude Code's native mechanisms: `CLAUDE.md` files, the Read/Write tools, MCP servers, and the `.claude/` project directory.

Claude Code's architecture is fundamentally different from GitHub Copilot's. It is a CLI-based agent with direct file system access, persistent project configuration, and extensible tool integrations. This creates both stronger native memory primitives and different constraints.

## Memory Type Mapping Summary

| Memory Type | Purpose | Claude Code Mechanism | Storage Location |
|---|---|---|---|
| **Episodic** | Event/decision recall | Read/Write tools | `.claude/memory/episodic/*.md` |
| **Semantic** | Facts, rules, standards | CLAUDE.md (auto-loaded) + files | `CLAUDE.md` + `.claude/memory/semantic/*.md` |
| **Procedural** | Automated workflows | CLAUDE.md instructions + bash | `CLAUDE.md` + `.claude/memory/procedural/*.md` |
| **Working** | Active problem-solving | Conversation context + TodoWrite | In-session (not persisted) |
| **Short-term** | Session context | Conversation context | In-session (auto-compressed) |
| **Long-term** | Persistent preferences | `~/.claude/` auto-memory + CLAUDE.md | `~/.claude/projects/*/memory/` + `CLAUDE.md` |

## Implementation Tracks

- **Track A (File-based)**: Zero infrastructure. Markdown files + CLAUDE.md + Claude's auto-memory. Uses Read/Write tools for memory operations.
- **Track B (Vector store)**: MCP server connecting Claude Code to a vector embedding store (Qdrant/Pinecone/pgvector) for semantic retrieval at scale.

## File Index

| File | Description |
|---|---|
| [memory-type-mapping.md](memory-type-mapping.md) | Detailed mapping of each memory type to Claude Code primitives |
| [track-a-file-based-guide.md](track-a-file-based-guide.md) | Step-by-step file-based implementation |
| [track-b-vector-store-guide.md](track-b-vector-store-guide.md) | Step-by-step vector store implementation via MCP |
| [CLAUDE.md](CLAUDE.md) | Drop-in CLAUDE.md snippet for any repository |
| [claude-memory.instructions.md](claude-memory.instructions.md) | Reusable agent instructions block |
| [trade-offs.md](trade-offs.md) | Track A vs Track B comparison |
| [known-gaps.md](known-gaps.md) | Limitations and migration risks |

## Quick Start

1. Read [memory-type-mapping.md](memory-type-mapping.md) to understand native mechanism mapping
2. Choose Track A or Track B based on [trade-offs.md](trade-offs.md)
3. Follow the chosen track's guide
4. Copy the [CLAUDE.md](CLAUDE.md) content into your project's root `CLAUDE.md`
5. Review [claude-memory.instructions.md](claude-memory.instructions.md) for detailed agent protocols

## Prerequisites

- Claude Code CLI installed and authenticated
- A project directory (git repo recommended but not required)
- For Track B: Docker (for self-hosted vector store) or cloud account, plus MCP server setup

## Claude Code Native Memory Primer

### CLAUDE.md Files
The `CLAUDE.md` file at the project root is automatically loaded into every Claude Code conversation. It serves as the persistent system prompt for the project. Claude Code also reads `CLAUDE.md` files in subdirectories when working in those paths.

**Loaded automatically**: Always, at conversation start.
**Writable by agent**: Yes, via the Write/Edit tools.
**Scope**: Project-level (per repository).

### Auto-Memory (`~/.claude/`)
Claude Code maintains a personal memory directory at `~/.claude/projects/<project-path>/memory/`. The `MEMORY.md` file in this directory is loaded into every conversation for that project. Additional files can be created and linked from `MEMORY.md`.

**Loaded automatically**: `MEMORY.md` is loaded (first 200 lines). Other files must be explicitly read.
**Writable by agent**: Yes, via Write/Edit tools.
**Scope**: User-level, per-project.

### Read/Write/Edit Tools
Claude Code has direct file system access. It can read any file, write new files, and edit existing files. This makes file-based memory fully native — no workarounds needed.

### MCP Servers
Claude Code supports Model Context Protocol servers, enabling connections to external tools and data sources. MCP servers can expose vector stores, databases, or any other memory backend as tools.

**Configuration**: `.claude/mcp.json` (project-level) or `~/.claude/mcp.json` (user-level).

### TodoWrite Tool
Built-in task tracking tool that maintains a structured todo list during the session. Functions as native working memory for task decomposition and progress tracking.

### Conversation Context
Claude Code maintains full conversation history within a session, with automatic compression when approaching context limits. This serves as natural working memory and short-term memory.

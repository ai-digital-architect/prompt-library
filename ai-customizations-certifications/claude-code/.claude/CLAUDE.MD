# Claude Code Customization Patterns

## Scope

This folder (ai-customizations-certifications/claude-code/) is a self-contained workspace for applying the Claude Code Customization Architecture to concrete architectural patterns. Minimize reviewing or modifying files outside this folder. The rest of the repository is unrelated reference material.

## Architecture Guide

The authoritative reference for all work in this folder is:

- architecture/claude-code-customization-architecture.md

Read this file before implementing any pattern. It defines the six core components (Memory, Sub-agents, Hooks, MCP Servers, Slash Commands, Skills) and their correct placement, configuration, and composition rules.

## Patterns

Each subfolder under patterns/ contains a distinct architectural pattern to be implemented using Claude Code customization primitives:

- patterns/cell-baased-architecture/ : Cell-based architecture pattern
- patterns/component-based-design/ : Component-based design pattern
- patterns/hexagonal-architecture/ : Hexagonal (ports and adapters) architecture pattern
- patterns/memory-implementation/ : Memory system implementation pattern
- patterns/workflow-patterns/ : Workflow orchestration patterns (see below)

### Workflow Patterns (Special Role)

patterns/workflow-patterns/ does not produce its own standalone reference architecture. Instead, it augments claude-code-customization-architecture.md to describe how workflows (Skills, Slash Commands, Hooks, Sub-agent orchestration) are composed when implementing the other four patterns. Reference workflow patterns when building out cell-based, component-based, hexagonal, or memory-implementation artifacts.

## Output: Reference Architecture Artifacts

For each pattern (except workflow-patterns), generate a complete reference architecture under:

    architecture/reference-architecture/<pattern-name>/

Each pattern folder should contain the Claude Code customization artifacts that implement that pattern, for example CLAUDE.md, AGENTS.md, sub-agent definitions, hook configurations, skill definitions, MCP server configs, and a README explaining the mapping from architectural pattern to Claude Code primitives.

## Workflow

1. Read architecture/claude-code-customization-architecture.md for component definitions and rules
2. Read the relevant patterns/<pattern>/ folder for pattern-specific guidance
3. Consult patterns/workflow-patterns/ for orchestration and workflow composition
4. Create artifacts under architecture/reference-architecture/<pattern-name>/
5. Stay within this folder and do not modify files elsewhere in the repository

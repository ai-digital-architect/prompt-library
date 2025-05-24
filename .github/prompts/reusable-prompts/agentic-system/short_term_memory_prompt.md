---
title: "GitHub Copilot Short-term Memory Implementation"
description: "Session-based context management across all Copilot modes"
version: "1.0.0"
memory_type: "Short-term Memory"
implementation_priority: "Foundation Level"
---

# GitHub Copilot Short-term Memory Implementation

I'm implementing a short-term memory system for GitHub Copilot that manages session-based context across all three agent modes (Ask, Edit, and Agent) during long-running coding sessions.

## Target Implementation
**File Location**: `.github/instructions/short-term-memory.md`

**Purpose**: Temporary context that persists during active coding sessions but resets between sessions - like holding chat history until you close the tab.

## My Project Structure Context
```
Project-root/
├── .github/
    ├── instructions/
    │   └── short-term-memory.md  ← FOCUS OF THIS IMPLEMENTATION
    ├── workflows/
    ├── prompts/
    ├── tools/
    └── copilot-instructions.md
```

## Implementation Requirements

Provide **step-by-step tutorial with configuration examples** for implementing short-term memory:

### Core Implementation Details:
1. **Short-term Memory Strategy** (optimal approach for session-based context retention)
2. **Markdown Template** (complete configuration for short-term-memory.md)
3. **Copilot-Instructions Integration** (how to reference and activate short-term memory)
4. **Cross-Mode Optimization** (specific configurations for Ask, Edit, and Agent modes)
5. **Session Management** (how context persists and resets appropriately)

### Short-term Memory Specific Features:
- **Session Context Tracking** (maintaining relevant information during active coding)
- **Context Prioritization** (what information to keep vs. discard during sessions)
- **Mode Transition Handling** (preserving context when switching between Ask/Edit/Agent)
- **Memory Refresh Mechanisms** (when and how to update session context)
- **Context Size Management** (preventing memory overflow in long sessions)

### Success Metrics & Validation:

For short-term memory, provide:
- **Performance Indicators** (signs that session context is being maintained effectively)
- **Testing Methods** (how to validate short-term memory is working)
- **Success Metrics** (measurable improvements in context awareness)
- **Troubleshooting Guide** (common short-term memory issues and solutions)
- **Optimization Checkpoints** (when to refine short-term memory configuration)

## Special Requirements:

- **Multi-Mode Integration**: How short-term memory enhances context continuity across Ask, Edit, and Agent modes
- **Session Boundaries**: Clear definition of when memory should persist vs. reset
- **Long-Running Session Focus**: Optimized for extended coding sessions without context degradation
- **Markdown-First Approach**: Pure markdown solution with future enhancement possibilities
- **Foundation for Other Memory Types**: How short-term memory supports future memory implementations

## Expected Deliverables:

1. **Complete short-term-memory.md Template** (ready-to-use configuration)
2. **Copilot-Instructions Integration** (exact syntax for activating short-term memory)
3. **Testing Framework** (how to validate short-term memory effectiveness)
4. **Usage Examples** (practical scenarios showing short-term memory in action)
5. **Maintenance Guidelines** (keeping short-term memory optimized)
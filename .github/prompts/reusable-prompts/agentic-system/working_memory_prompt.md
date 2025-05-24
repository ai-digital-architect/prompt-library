---
title: "GitHub Copilot Working Memory Implementation"
description: "Real-time problem-solving scratchpad for active task execution"
version: "1.0.0"
memory_type: "Working Memory"
implementation_priority: "Core Operational"
---

# GitHub Copilot Working Memory Implementation

I'm implementing a working memory system for GitHub Copilot that serves as a mental scratchpad for real-time problem-solving and step execution across all three agent modes (Ask, Edit, and Agent).

## Target Implementation
**File Location**: `.github/instructions/working-memory.md`

**Purpose**: AI's mental scratchpad that solves problems and executes steps in real time, then moves on - active task state tracking and intermediate step management.

## My Project Structure Context
```
Project-root/
├── .github/
    ├── instructions/
    │   ├── short-term-memory.md  ← FOUNDATION (if implemented)
    │   └── working-memory.md     ← FOCUS OF THIS IMPLEMENTATION
    ├── workflows/
    ├── prompts/
    ├── tools/
    └── copilot-instructions.md
```

## Implementation Requirements

Provide **step-by-step tutorial with configuration examples** for implementing working memory:

### Core Implementation Details:
1. **Working Memory Strategy** (optimal approach for real-time problem-solving support)
2. **Markdown Template** (complete configuration for working-memory.md)
3. **Copilot-Instructions Integration** (how to reference and activate working memory)
4. **Cross-Mode Optimization** (specific configurations for Ask, Edit, and Agent modes)
5. **Task State Management** (tracking current problems and solution steps)

### Working Memory Specific Features:
- **Problem Decomposition Templates** (breaking down complex coding tasks)
- **Step-by-Step Tracking** (maintaining current position in multi-step processes)
- **Context Switching Support** (managing multiple concurrent problem spaces)
- **Solution Path Recording** (tracking attempted approaches and outcomes)
- **Active Task Focus** (prioritizing current work while maintaining background context)

### Success Metrics & Validation:

For working memory, provide:
- **Performance Indicators** (signs that problem-solving support is effective)
- **Testing Methods** (how to validate working memory functionality)
- **Success Metrics** (measurable improvements in task execution efficiency)
- **Troubleshooting Guide** (common working memory issues and solutions)
- **Optimization Checkpoints** (when to refine working memory configuration)

## Special Requirements:

- **Multi-Mode Integration**: How working memory enhances problem-solving across Ask, Edit, and Agent modes
- **Real-time Updates**: Dynamic updating of working memory during active coding
- **Long-Running Session Focus**: Maintaining problem-solving context during extended sessions
- **Integration with Short-term Memory**: How working memory complements session context
- **Markdown-First Approach**: Pure markdown solution with structured problem-solving templates

## Expected Deliverables:

1. **Complete working-memory.md Template** (ready-to-use configuration)
2. **Problem-Solving Frameworks** (structured approaches for different task types)
3. **Copilot-Instructions Integration** (exact syntax for activating working memory)
4. **Testing Framework** (how to validate working memory effectiveness)
5. **Usage Examples** (practical scenarios showing working memory in complex tasks)
6. **Maintenance Guidelines** (keeping working memory optimized for problem-solving)
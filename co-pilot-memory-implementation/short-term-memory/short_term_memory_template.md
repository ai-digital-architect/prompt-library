# Short-term Memory System
*Session-based context management for GitHub Copilot*

## Current Session Context

### Active Task Focus
**Primary Objective**: 
- [ ] Current main task or feature being worked on

**Secondary Tasks**: 
- [ ] Background tasks or upcoming priorities

### Recent Decisions & Changes
**Last 3 Significant Decisions**:
1. [Decision] - [Reasoning] - [Timestamp]
2. [Decision] - [Reasoning] - [Timestamp] 
3. [Decision] - [Reasoning] - [Timestamp]

**Recent Code Changes**:
- **Files Modified**: List of recently changed files
- **Key Changes**: Brief description of significant modifications
- **Impact**: How changes affect current session goals

### Context Stack
**Current Working Context** (Most Important):
```
- Current file/function being edited
- Immediate problem being solved
- Current debugging session details
- Active error messages or issues
```

**Background Context** (Supporting):
```
- Related files that may need updates
- Dependencies being considered
- Architecture decisions affecting current work
- Testing considerations for current changes
```

## Session State Management

### Context Prioritization
**High Priority** (Always maintain):
- Current file and function being edited
- Active error messages and debugging info
- Immediate task objectives
- Recent decisions affecting current work

**Medium Priority** (Maintain when space allows):
- Related file changes in current session
- Background tasks and considerations
- Recent discussions or decisions
- Architecture context for current work

**Low Priority** (Expire first when memory full):
- Historical context from earlier in session
- Completed tasks and resolved issues
- Detailed decision reasoning
- Non-critical background information

### Context Refresh Triggers
**Auto-refresh when**:
- Switching between major files/modules
- Starting new features or debugging sessions
- Encountering errors or blockers
- Moving between different types of tasks

**Manual refresh needed for**:
- Major context switches (different projects/branches)
- After breaks or interruptions
- When context becomes stale or irrelevant
- Complex multi-step task completion

## Mode-Specific Context

### Ask Mode Context
- Recent questions and answers
- Current exploration topics
- Clarifications needed
- Research findings relevant to current task

### Edit Mode Context  
- Files currently being modified
- Recent edit patterns and preferences
- Active refactoring or formatting tasks
- Code style decisions for current session

### Agent Mode Context
- Multi-step task progress
- Current step in complex workflows
- Dependencies between automated tasks
- Success/failure status of recent agent actions

## Session Boundaries

### Context Persists During:
- File switching within same project
- Mode transitions (Ask → Edit → Agent)
- Short breaks or interruptions
- Error investigation and resolution

### Context Resets When:
- Ending coding session
- Switching to different project/repository
- Major context shift (different programming language)
- Explicit reset requested

## Memory Size Management

### Context Limits:
- **Maximum Context Items**: 15-20 items
- **Auto-Prune Threshold**: When reaching 18 items
- **Minimum Retained**: Always keep 5 most recent high-priority items

### Pruning Strategy:
1. Remove completed tasks first
2. Compress detailed decision reasoning
3. Merge related context items
4. Archive to long-term memory if applicable

## Quick Context Templates

### Starting New Task
```
**New Task**: [Task Name]
**Goal**: [What you're trying to accomplish]
**Files**: [Primary files involved]
**Approach**: [Initial strategy]
**Blockers**: [Known issues or dependencies]
```

### Context Switch
```
**Previous Context**: [Brief summary of what was happening]
**New Context**: [What you're switching to]
**Handoff Notes**: [Important info to remember]
**Return Strategy**: [How to pick up previous work]
```

### Debug Session
```
**Issue**: [Problem description]
**Symptoms**: [What you're observing]
**Investigation**: [Steps taken so far]
**Hypotheses**: [Current theories]
**Next Steps**: [What to try next]
```

---

**Last Updated**: [Auto-update timestamp]
**Session Duration**: [Current session length]
**Context Health**: [Good/Needs Pruning/Overloaded]
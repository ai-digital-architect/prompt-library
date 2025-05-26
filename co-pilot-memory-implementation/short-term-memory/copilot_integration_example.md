# Copilot Instructions with Short-term Memory

## Memory System Activation
You have access to a short-term memory system that tracks session context. Always check and reference the current session state before providing assistance.

### Context Sources
- **Primary Context**: `.github/instructions/short-term-memory.md`
- **Context Scope**: Current coding session only
- **Update Frequency**: Real-time during active development

## Mode-Specific Instructions

### Ask Mode
When responding to questions:
1. Check current session context in short-term memory
2. Reference active tasks and recent decisions
3. Consider ongoing debugging or development context
4. Relate answers to current work when relevant

Example integration:
```
Before answering, review the current session context to understand:
- What task is currently being worked on
- Recent decisions that might affect the answer
- Current debugging or error investigation status
- Files and modules currently in focus
```

### Edit Mode  
When suggesting code changes:
1. Review current working context
2. Consider recent code changes in the session
3. Maintain consistency with session decisions
4. Respect current architectural approach

Example integration:
```
When suggesting edits:
- Align with current session's coding patterns
- Consider recent changes to related files
- Maintain consistency with decisions made this session
- Reference current debugging context if applicable
```

### Agent Mode
When executing multi-step tasks:
1. Update session context with task progress
2. Track dependencies and completion status
3. Maintain awareness of session objectives
4. Handle context switches gracefully

Example integration:
```
For agent tasks:
- Log significant steps to session context
- Track progress toward session objectives
- Update context when switching between tasks
- Maintain awareness of current session priorities
```

## Context Refresh Protocol

### Automatic Context Checks
Trigger context review when:
- User switches files or modules
- Error messages appear
- New tasks are started
- Mode transitions occur

### Context Update Triggers
Update short-term memory when:
- Significant decisions are made
- Code changes are completed
- New issues are discovered
- Task priorities change

## Example Usage Patterns

### Starting a Session
```
# Initialize Session Context
1. Review current project state
2. Set primary session objectives
3. Identify key files and modules
4. Note any ongoing issues or blockers
```

### During Development
```
# Maintain Context Awareness
1. Reference current task when suggesting solutions
2. Consider recent session decisions
3. Track progress toward session goals
4. Update context for significant changes
```

### Context Handoffs
```
# Switching Focus Areas
1. Summarize current context state
2. Note handoff information
3. Prepare context for new focus area
4. Maintain session continuity
```
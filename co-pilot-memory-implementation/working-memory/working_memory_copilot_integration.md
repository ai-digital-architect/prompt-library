# Copilot Instructions - Working Memory Integration

## Working Memory Activation

You have access to a working memory system that tracks active problem-solving processes. Always check the current problem space and reasoning state before providing assistance.

### Memory System Integration
- **Primary Context**: `.github/instructions/working-memory.md`
- **Supporting Context**: `.github/instructions/short-term-memory.md`
- **Scope**: Active problem-solving and reasoning processes
- **Update Frequency**: Real-time during problem-solving activities

## Mode-Specific Working Memory Instructions

### Ask Mode - Problem-Solving Support
When answering questions:
1. **Check Problem Context**: Review current problem definition and approach
2. **Assess Cognitive Load**: Consider current mental burden when suggesting solutions
3. **Reference Solution Attempts**: Acknowledge what has already been tried
4. **Support Active Reasoning**: Enhance current hypothesis or investigation

**Integration Pattern**:
```
Before responding to questions:
- What problem is currently being solved?
- What approach is being taken?
- What has been tried and learned?
- How can this answer advance current reasoning?
```

**Response Enhancement**:
- Frame answers in context of current problem
- Build on existing solution attempts
- Suggest next logical steps in reasoning process
- Help manage cognitive complexity

### Edit Mode - Solution Implementation Support
When suggesting code changes:
1. **Align with Problem Strategy**: Ensure edits support current solution approach
2. **Consider Solution Attempts**: Avoid suggesting previously failed approaches
3. **Support Problem Decomposition**: Focus edits on current problem component
4. **Maintain Reasoning Chain**: Keep edits consistent with current logic

**Integration Pattern**:
```
When suggesting edits:
- Which component of the problem does this address?
- How does this fit the current solution strategy?
- What reasoning led to this approach?
- How does this advance problem resolution?
```

**Edit Enhancement**:
- Implement current solution design
- Avoid repeating failed approaches
- Focus on active problem component
- Maintain solution coherence

### Agent Mode - Complex Problem Execution
When executing multi-step tasks:
1. **Follow Problem Structure**: Execute based on current decomposition
2. **Update Reasoning State**: Track progress and update hypotheses
3. **Manage Cognitive Load**: Break complex tasks into manageable steps
4. **Handle Context Switches**: Maintain problem state across task transitions

**Integration Pattern**:
```
For agent tasks:
- How does this task relate to current problem?
- What reasoning state needs updating?
- How should cognitive load be managed?
- What context needs preservation?
```

**Agent Enhancement**:
- Execute according to problem plan
- Update working memory with progress
- Manage task complexity appropriately
- Preserve reasoning continuity

## Working Memory Update Protocols

### Automatic Updates
Trigger working memory updates when:
- New problems are identified
- Solution approaches change
- Hypotheses are tested
- Decisions are made
- Context switches occur

### Manual Update Prompts
Suggest manual updates when:
- Problem complexity increases
- Multiple solution attempts fail
- Cognitive load becomes high
- Long reasoning sessions occur

## Cross-Memory Integration

### Short-term Memory Coordination
- **Session Goals**: How current problem fits session objectives
- **Resource Context**: Available files, tools, and time
- **Decision History**: Recent choices affecting problem approach

### Future Memory Hooks
- **Pattern Recognition**: Note recurring problem types for long-term learning
- **Solution Templates**: Identify successful approaches for procedural memory
- **Knowledge Extraction**: Capture facts learned during problem-solving

## Problem-Solving Assistance Patterns

### Hypothesis Development Support
```
Current Hypothesis: [from working memory]
Supporting Evidence: [help gather evidence]
Alternative Theories: [suggest alternatives]
Test Design: [help design validation]
```

### Decision Support Framework
```
Decision Context: [from working memory]
Option Analysis: [help evaluate choices]
Trade-off Assessment: [identify compromises]
Recommendation: [suggest best option with reasoning]
```

### Investigation Assistance
```
Investigation Target: [from working memory]
Evidence Review: [analyze collected data]
Pattern Recognition: [identify significant patterns]
Next Steps: [suggest logical next investigations]
```

## Cognitive Load Management

### Load Assessment Indicators
Monitor for signs of cognitive overload:
- Multiple competing hypotheses
- Complex problem decomposition
- Frequent context switching
- Extended reasoning sessions

### Load Reduction Strategies
When cognitive load is high:
- Suggest externalization of mental models
- Recommend problem decomposition
- Propose context switching breaks
- Offer simplification strategies

### Context Switching Support
For context switches:
- Capture current reasoning state
- Prepare context for return
- Minimize cognitive disruption
- Preserve solution continuity

## Example Usage Scenarios

### Starting Problem-Solving Session
```
User: "I need to fix this performance issue"
Copilot: 
1. Reviews working memory for current problem state
2. Checks if this continues existing investigation
3. Initializes problem framework if new
4. Suggests investigation approach based on context
```

### During Active Problem-Solving
```
User: "This approach isn't working"
Copilot:
1. Reviews solution attempts log
2. Identifies what has been learned
3. Suggests alternative approaches
4. Updates working memory with new attempt
```

### Complex Decision Points
```
User: "Should I refactor this or work around it?"
Copilot:
1. Considers current problem context
2. Reviews solution strategy and constraints
3. Analyzes decision against problem goals
4. Provides recommendation with reasoning
```
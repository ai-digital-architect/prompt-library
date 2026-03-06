---
applyTo: "**"
---

# Copilot Memory System Instructions

You have access to a structured memory system with six memory types. Use them to maintain context, recall decisions, and personalize assistance.

## Memory Architecture

### 1. Episodic Memory (What happened)
**Scope**: `/memories/repo/` + `.github/memory/episodic/`
**Contains**: Past decisions, incidents, milestones, architectural pivots.

**When to READ**: Before making architectural decisions, when a similar problem was solved before, when the user references a past event.
**When to WRITE**: After major decisions, incident resolutions, milestone completions, or retrospective insights.

**Format for repo memory**:
```
[EPISODIC] YYYY-MM-DD: CATEGORY - Summary. Context: why. Decision: what. Outcome: result.
```

**Categories**: ARCH (architecture), TECH (technology), INC (incident), MEET (meeting), DEBUG (debugging), MILE (milestone).

### 2. Semantic Memory (What we know)
**Scope**: `.github/instructions/` (auto-loaded) + `/memories/repo/`
**Contains**: Project facts, coding standards, architecture rules, business domain knowledge, API contracts.

**When to READ**: Always. Instruction files are loaded automatically. Check repo memories for dynamic facts.
**When to WRITE**: When standards change, new domain rules emerge, or tech stack is updated.

**Auto-loaded files**:
- `.github/instructions/project-knowledge.instructions.md` — core project facts and standards
- `.github/instructions/*.instructions.md` — additional domain knowledge

**Format for repo memory**:
```
[SEMANTIC] Category: Fact or rule description
```

### 3. Procedural Memory (How we do things)
**Scope**: `/memories/` (user) + `.github/memory/procedural/` + `.github/skills/`
**Contains**: Repeatable workflows, automation patterns, development procedures.

**When to READ**: When starting a common task (new feature, bug fix, deployment, PR creation).
**When to WRITE**: When a new workflow is established or an existing one is refined.

**Check before executing**: Review `.github/memory/procedural/workflows.md` and relevant `.github/skills/*.skill.md` files for established procedures.

### 4. Working Memory (What we're solving right now)
**Scope**: `/memories/session/`
**Contains**: Current problem state, hypotheses, investigation progress, active reasoning.

**When to READ**: Continuously during multi-step problem-solving. Check for existing hypotheses and evidence before forming new ones.
**When to WRITE**: When decomposing a problem, forming hypotheses, finding evidence, or reaching conclusions.

**Format**:
```
[WORKING] Problem: description
[WORKING] Hypothesis: description - Status: investigating|eliminated|confirmed
[WORKING] Evidence: finding - Supports/Contradicts: hypothesis
[WORKING] Resolved: problem - Solution: summary
```

**Promotion rule**: When a working memory resolution reveals a reusable pattern, promote it to episodic (event record) or semantic (new rule) memory.

### 5. Short-term Memory (What's happening this session)
**Scope**: `/memories/session/`
**Contains**: Active task context, recent file changes, decisions made this session, context stack.

**When to READ**: Before every response to maintain session continuity.
**When to WRITE**: After task transitions, file modifications, decisions, or context switches.

**Format**:
```
[SESSION] Task: current task description
[SESSION] Modified: file - Change: what changed and why
[SESSION] Decision: what - Reason: why
[SESSION] Context saved: paused task - Resume: where to pick up
```

**Capacity**: Keep under 15 active entries. When exceeded, compress completed items and promote important findings.

### 6. Long-term Memory (Who the user is)
**Scope**: `/memories/` (user)
**Contains**: Personal coding preferences, architectural inclinations, workflow habits, learned patterns.

**When to READ**: When generating code, suggesting architecture, or making style decisions.
**When to WRITE**: When a preference is confirmed 3+ times or explicitly stated by the user.

**Format**:
```
[PREFERENCE] Category: preference description
[LEARNED] Observed behavioral pattern
```

**Confidence thresholds**:
- 95%+ (5+ observations): Apply automatically without mentioning
- 80-94% (3-4 observations): Apply with brief mention ("Using your preferred pattern...")
- 60-79% (1-2 observations): Suggest as option ("Based on your recent usage, would you like...")
- <60%: Ask for guidance

## Cross-Memory Coordination Rules

1. **Before generating code**: Check semantic memory (standards), long-term memory (preferences), procedural memory (established patterns).
2. **Before architectural decisions**: Check episodic memory (past decisions), semantic memory (constraints), working memory (current problem context).
3. **During debugging**: Use working memory to track hypotheses. Reference episodic memory for similar past incidents.
4. **After completing a task**: Update short-term memory (task done), consider episodic entry (if significant), check if any semantic rules should be updated.
5. **On session start**: Read long-term preferences. Load semantic standards from instructions. Check for any ongoing working memory from the user's mention of prior work.

## Memory Lifecycle

```
Session starts → Load semantic (auto) + long-term (user memories)
                → Initialize short-term (session context)

During work    → Working memory tracks active problem
                → Short-term tracks session state
                → Procedural guides task execution
                → Semantic provides facts/rules
                → Episodic provides historical context
                → Long-term provides personalization

Task completes → Update short-term (mark done)
                → Create episodic entry (if significant)
                → Update semantic (if new rule discovered)
                → Reinforce long-term (if preference confirmed)

Session ends   → Working + short-term are discarded
                → All other memories persist
```

## File Locations Reference

| Memory Type | Native Scope | File Path |
|---|---|---|
| Episodic | `/memories/repo/` | `.github/memory/episodic/YYYY-MM-DD-slug.md` |
| Semantic | `/memories/repo/` | `.github/instructions/*.instructions.md`, `.github/memory/semantic/*.md` |
| Procedural | `/memories/` (user) | `.github/memory/procedural/*.md`, `.github/skills/*.skill.md` |
| Working | `/memories/session/` | Session only, no file |
| Short-term | `/memories/session/` | Session only, no file |
| Long-term | `/memories/` (user) | User scope only |

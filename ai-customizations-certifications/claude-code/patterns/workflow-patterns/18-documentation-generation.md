# Pattern 18: Documentation Generation

## Category
Generation & Scaffolding Workflows

## Overview

A read-only sub-agent reads source files, existing tests, and commit history, then produces API reference documentation, a README, and an architecture decision record. Since it is read-only, it can be safely invoked on any branch without risk of side effects.

## Architecture Diagram

```
User invokes /generate-docs
        │
        ▼
┌───────────────────────────┐
│  Documentation Generator   │
│  (READ-ONLY sub-agent)     │
│  - Reads source files      │
│  - Reads test files        │
│  - Reads git log           │
│  - Produces:               │
│    • API reference         │
│    • README updates        │
│    • Architecture ADR      │
│                            │
│  Tools: Read, Bash         │
│  disallowed: Write, Edit   │
└───────────────────────────┘
        │
        ▼
  .claude/docs/ output directory
```

## Complete File Implementations

### Skill — `.claude/skills/generate-docs/SKILL.md`

```yaml
---
name: generate-docs
description: >
  Generates API documentation, README content, and architecture decision
  records from source code, tests, and git history. Read-only analysis
  with structured output. Use after completing a feature or before a release.
argument-hint: "[scope: module-name or 'all'] [doc-type: api|readme|adr|all]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

Generate documentation: $ARGUMENTS

Invoke the `doc-generator` sub-agent to:

1. Read all source files in scope
2. Read corresponding test files to understand behavior
3. Read git log for recent changes: `git log --oneline -20`
4. Produce documentation:
   - **API Reference**: endpoint descriptions, parameters, response shapes, examples
   - **README Section**: feature overview, quick start, configuration
   - **ADR (Architecture Decision Record)**: if significant design decisions were made

Output to `.claude/docs/`:
- `api-reference.md`
- `readme-section.md`
- `adr-NNNN.md` (numbered sequentially)
```

### Sub-agent — `.claude/agents/doc-generator.md`

```yaml
---
name: doc-generator
description: >
  Generates documentation from source code analysis. Reads source, tests,
  and git history to produce API references, README content, and ADRs.
  Strictly read-only.
model: claude-opus-4-5
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
  - MultiEdit
maxTurns: 20
---

You are a technical documentation specialist.

For API Reference:
1. Read each route handler and extract: path, method, parameters, response shape
2. Read JSDoc comments for descriptions
3. Read tests for usage examples
4. Produce Markdown with tables and code examples

For README:
1. Identify the module's purpose from its service layer
2. Extract configuration options from environment variable usage
3. Create a quick-start guide based on test setup patterns

For ADR:
1. Read recent git log for the module
2. Identify significant architectural decisions from commit messages and code structure
3. Follow the standard ADR format: Title, Status, Context, Decision, Consequences

Write all output to `.claude/docs/`.
```

### Settings — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(find * -name *.ts)",
      "Bash(grep -rn * src/)",
      "Bash(wc -l *)",
      "Bash(mkdir -p .claude/docs)"
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Generator modifies source files | `disallowedTools: [Write, Edit, MultiEdit]` — strictly read-only |
| Documentation exposes internal secrets | Generator should skip environment variable values; document keys only |
| Safe to run on any branch | Read-only guarantee means no unintended side effects |

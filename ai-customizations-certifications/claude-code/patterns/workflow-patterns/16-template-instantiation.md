# Pattern 16: Template Instantiation

## Category
Generation & Scaffolding Workflows

## Overview

A skill accepts a feature description as `$ARGUMENTS` and invokes a sub-agent that fills a project scaffold template — creating all boilerplate files, wiring up routes, registering the new module — based on the project's established conventions in `CLAUDE.md`.

## Architecture Diagram

```
User invokes /scaffold [feature-name]
        │
        ▼
┌──────────────────────┐
│  Scaffolder Sub-agent │
│  - Reads CLAUDE.md    │
│    conventions        │
│  - Reads template     │
│    files              │
│  - Creates all        │
│    boilerplate        │
│  - Registers module   │
│  - Wires routes       │
└──────────┬───────────┘
           │
    PostToolUse Hook
    (lint + compile
     after each write)
           │
           ▼
    New module ready
```

## Complete File Implementations

### Skill — `.claude/skills/scaffold/SKILL.md`

```yaml
---
name: scaffold
description: >
  Scaffolds a complete new module with all boilerplate: entity, repository,
  service, route handler, tests, and module registration. Follows project
  conventions from CLAUDE.md. Use when creating a new feature module.
argument-hint: "[module-name] [brief description]"
allowed-tools: Read, Write, Bash
---

Scaffold new module: $ARGUMENTS

1. Read project conventions from `CLAUDE.md`
2. Read the template structure from `.claude/skills/scaffold/template.md`
3. Create all files for the new module:
   - `src/entities/$1.entity.ts`
   - `src/repositories/$1.repository.ts`
   - `src/services/$1.service.ts`
   - `src/routes/$1.routes.ts`
   - `src/routes/$1.routes.test.ts`
4. Register the new module in `src/routes/index.ts`
5. Run `pnpm build && pnpm test`
6. Present list of created files with a brief description of each
```

### Template — `.claude/skills/scaffold/template.md`

```markdown
## Module Template Structure

### Entity: `src/entities/{name}.entity.ts`
- Export TypeScript types/interfaces for the entity
- Include all fields with JSDoc comments
- Use Drizzle `InferSelectModel` / `InferInsertModel` for DB types

### Repository: `src/repositories/{name}.repository.ts`
- Export functions: `findById`, `findAll`, `create`, `update`, `delete`
- All queries use Drizzle ORM
- Return `Result<T, RepositoryError>` types

### Service: `src/services/{name}.service.ts`
- Business logic only
- Depends on repository via function parameters (dependency injection)
- Return `Result<T, AppError>` types
- JSDoc on every exported function

### Routes: `src/routes/{name}.routes.ts`
- Thin handlers: validate → call service → return response
- OpenAPI annotations on each handler
- Standard error response format

### Tests: `src/routes/{name}.routes.test.ts`
- Happy path for each endpoint
- Validation error cases
- Auth failure cases
- Use Supertest for HTTP assertions
```

### Settings — `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-format.sh"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Scaffold creates files outside expected directories | Skill instructions scope to `src/` paths; could add path-validation hook |
| Generated code has security gaps | PostToolUse hook runs lint; conventions in CLAUDE.md enforce security patterns |
| Template diverges from actual conventions | Template lives in version control alongside code; reviewed in PRs |

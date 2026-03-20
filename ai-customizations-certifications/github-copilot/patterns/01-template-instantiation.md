# Pattern 6.1 — Template Instantiation

> A prompt command accepts a feature description and invokes a sub-agent that fills a project scaffold template based on established conventions.

---

## Architecture Mapping

| Claude Code Component | GitHub Copilot Equivalent |
|---|---|
| Slash Command with `$ARGUMENTS` | `.prompt.md` file invoked via `/command` |
| Sub-agent fills scaffold | Sub-agent creates boilerplate based on conventions |
| `CLAUDE.md` conventions | `copilot-instructions.md` + Skill references |

## Implementation Fidelity: ✅ High

---

## File Structure

```
.github/
├── prompts/
│   └── scaffold-feature.prompt.md
├── agents/
│   └── scaffolder.agent.md
└── skills/
    └── project-scaffold/
        ├── SKILL.md
        └── templates/
            ├── component.tsx.template
            ├── api-route.ts.template
            └── test.spec.ts.template
```

## Prompt File

### `.github/prompts/scaffold-feature.prompt.md`

```yaml
---
mode: agent
description: Scaffold a new feature with all boilerplate files, routes, and tests
tools: ['search', 'editFiles', 'codebase', 'terminalLastCommand']
---

Scaffold a complete feature for: {{ user request }}

Follow the project-scaffold skill for templates and conventions.

1. Create the component/module files from templates
2. Wire up routes and navigation
3. Register the module in the app's entry points
4. Create placeholder test files
5. Run the build to verify everything compiles
6. Report all files created
```

## Supporting Skill

### `.github/skills/project-scaffold/SKILL.md`

```yaml
---
name: project-scaffold
description: >
  Project scaffolding templates and conventions. Use when creating new
  features, modules, or components to ensure consistency with the project structure.
---

## Feature Structure Convention

Every feature lives in `src/features/<feature-name>/` with:
- `index.ts` — public API exports
- `<Feature>.tsx` — main component
- `<Feature>.test.tsx` — component tests
- `api.ts` — API integration
- `types.ts` — TypeScript types
- `hooks/` — feature-specific hooks

## Registration Steps
1. Add route in `src/routes.ts`
2. Add navigation entry in `src/components/Nav.tsx`
3. Add feature flag in `src/config/features.ts`

## Templates
See `templates/` directory for file templates with placeholders.
```

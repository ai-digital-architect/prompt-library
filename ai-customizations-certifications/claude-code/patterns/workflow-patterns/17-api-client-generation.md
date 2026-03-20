# Pattern 17: API Client Generation

## Category
Generation & Scaffolding Workflows

## Overview

A sub-agent reads an OpenAPI or gRPC spec and generates fully typed API clients in one or more target languages. A `PostToolUse` hook runs the type-checker for each generated client before the session completes.

## Architecture Diagram

```
User invokes /generate-client
        │
        ▼
┌──────────────────────┐
│  Client Generator     │
│  (write-capable)      │
│  - Reads spec file    │
│  - Generates typed    │
│    client code        │
│  - One file per       │
│    resource/endpoint  │
└──────────┬───────────┘
           │
    PostToolUse Hook
    (type-checker after
     each generated file)
           │
           ▼
    Typed API clients ready
```

## Complete File Implementations

### Skill — `.claude/skills/generate-client/SKILL.md`

```yaml
---
name: generate-client
description: >
  Generates fully typed API clients from an OpenAPI or gRPC spec. Runs
  type-checking after each generated file. Use when a new API spec is
  available or the spec has been updated.
argument-hint: "[spec-file-path] [target-language: ts|python|go]"
allowed-tools: Read, Write, Bash
---

Generate API client from spec: $ARGUMENTS

1. Read the spec file at `$1`
2. Parse all endpoints, request/response schemas, and auth requirements
3. For each resource/endpoint group, generate a typed client module:
   - TypeScript: `src/clients/<resource>.client.ts`
   - Python: `clients/<resource>_client.py`
   - Go: `clients/<resource>.go`
4. Generate a barrel/index file that exports all clients
5. Generate types/interfaces for all request/response schemas
6. Run the type-checker (`pnpm typecheck` / `mypy` / `go vet`)
7. Present list of generated files with endpoint coverage
```

### Sub-agent — `.claude/agents/client-generator.md`

```yaml
---
name: client-generator
description: >
  Generates typed API client code from an OpenAPI or gRPC specification.
  Produces one module per resource group with full type definitions.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Bash
disallowedTools:
  - Edit
  - MultiEdit
maxTurns: 25
---

Generate API clients from the provided specification.

For each endpoint:
1. Create typed request/response interfaces
2. Create a client function with proper error handling
3. Include JSDoc/docstring with endpoint description, parameters, and return type
4. Handle authentication (Bearer token, API key) based on spec security schemes
5. Use `Result<T, ApiError>` pattern for error handling

Generate a barrel file that re-exports all clients for clean imports.
Run the type-checker after generating all files.
```

### Hook — `.claude/hooks/typecheck-generated.sh`

```bash
#!/usr/bin/env bash
# PostToolUse hook: runs type-checker after writing client files

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only check generated client files
case "$file_path" in
  src/clients/*.ts|clients/*.py|clients/*.go)
    ;;
  *)
    exit 0
    ;;
esac

# Run appropriate type-checker
case "$file_path" in
  *.ts)  pnpm typecheck 2>/dev/null || { echo '{"reason": "TypeScript type-check failed"}' >&2; exit 2; } ;;
  *.py)  mypy "$file_path" 2>/dev/null || { echo '{"reason": "mypy type-check failed"}' >&2; exit 2; } ;;
  *.go)  go vet ./clients/... 2>/dev/null || { echo '{"reason": "go vet failed"}' >&2; exit 2; } ;;
esac

exit 0
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
            "command": "bash .claude/hooks/typecheck-generated.sh"
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
| Generated client hardcodes credentials | Generator uses auth scheme from spec; credentials via env vars only |
| Type-checker misses runtime errors | PostToolUse hook blocks on type failures; add integration test generation as follow-up |
| Spec contains injection payloads in descriptions | Audit spec descriptions; generator treats them as documentation only |

# Pattern 14: Spec-First Verification

## Category
Validation & Verification Workflows

## Overview

An OpenAPI or GraphQL spec is written first. A sub-agent generates tests directly from the spec. A second sub-agent verifies that the existing implementation satisfies every generated test, reporting any endpoints or fields that are missing or incorrectly implemented.

## Architecture Diagram

```
         OpenAPI/GraphQL Spec
                │
                ▼
┌──────────────────────┐
│  Test Generator       │
│  (write-capable)      │
│  - Reads spec         │
│  - Generates test     │
│    cases for every    │
│    endpoint/field     │
└──────────┬───────────┘
           │ generated tests
           ▼
┌──────────────────────┐
│  Spec Verifier        │
│  (read-only + Bash)   │
│  - Runs generated     │
│    tests              │
│  - Reports coverage   │
│  - Identifies gaps    │
└──────────────────────┘
```

## Complete File Implementations

### Skill — `.claude/skills/spec-verify/SKILL.md`

```yaml
---
name: spec-verify
description: >
  Generates tests from an API spec (OpenAPI/GraphQL) and verifies the
  implementation satisfies them. Reports missing or incorrect endpoints.
  Use after writing or updating an API spec.
argument-hint: "[path-to-spec-file]"
allowed-tools: Read, Write, Bash
---

Verify implementation against spec: $ARGUMENTS

1. Invoke `spec-test-generator` with the spec file path
   → Generates test files in `tests/spec-verification/`
2. Invoke `spec-verifier` to run the generated tests
   → Produces verification report
3. Present results: passed endpoints, failed endpoints, missing endpoints
```

### Sub-agent — `.claude/agents/spec-test-generator.md`

```yaml
---
name: spec-test-generator
description: >
  Generates test cases from an OpenAPI or GraphQL specification. Creates
  one test per endpoint/field covering request validation, response shape,
  and status codes.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Bash
maxTurns: 20
---

Read the API spec and generate comprehensive test cases.

For each endpoint in the spec:
1. Generate a test for the happy path (correct request → expected response shape)
2. Generate tests for validation errors (missing required fields, wrong types)
3. Generate tests for auth requirements
4. Verify response matches the documented schema exactly

Write tests to `tests/spec-verification/<endpoint-name>.test.ts`.
Use the project's test framework (Vitest/Jest/Supertest).
```

### Sub-agent — `.claude/agents/spec-verifier.md`

```yaml
---
name: spec-verifier
description: >
  Runs spec-generated tests against the implementation and reports which
  endpoints pass, fail, or are missing. Read-only except for running tests.
model: claude-sonnet-4-6
tools:
  - Read
  - Bash
disallowedTools:
  - Write
  - Edit
maxTurns: 10
---

Run all tests in `tests/spec-verification/` and produce a report.

1. Execute: `pnpm test -- tests/spec-verification/ --reporter=json`
2. Parse results and categorize:
   - **Passed**: endpoint exists and matches spec
   - **Failed**: endpoint exists but behavior doesn't match spec
   - **Missing**: endpoint in spec but not implemented (404 or route not found)
3. Write report to `.claude/spec/verification-report.json`
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Test generator creates tests with side effects | Tests should use mock/test database; test framework config enforces isolation |
| Verifier modifies source to make tests pass | `disallowedTools: [Write, Edit]` — can only read and run commands |
| Spec contains sensitive endpoint info | Spec files tracked in version control; audit access controls |

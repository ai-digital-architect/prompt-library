---
name: port-adapter-review
description: >
  Use this skill when the user mentions: review adapter, port contract, adapter
  correctness, check port implementation, validate adapter, adapter review, does this
  adapter implement the port correctly. Performs a systematic review of an adapter
  against its port interface contract.
version: 1.0.0
---

## What This Skill Does

This skill performs a systematic review of an adapter implementation against its port interface: verifying method signature completeness, error handling correctness, absence of business logic, constructor injection pattern, mapper separation, and retry logic — then produces a structured review report with severity-rated findings.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "review adapter", "adapter review", "adapter correctness"
- "port contract", "check port implementation", "validate adapter"
- "does this adapter implement the port correctly"
- "port adapter review", "adapter compliance check"

## Prerequisites

Before this skill executes, the following must be true:
- The adapter file path is known
- The port interface file that the adapter implements is locatable
- The adapter file exists and has been committed or saved

## Step-by-Step Procedure

1. **Read the port interface**
   - Read the port interface file completely
   - Document every method: name, parameter types, return type, declared error types
   - Note any doc comments specifying contract expectations

2. **Read the adapter implementation**
   - Read the adapter class file completely
   - Identify the `implements` clause — verify it references exactly one port interface

3. **Validate method signatures** (CRITICAL if violations found)
   - For each port method, verify adapter has: identical method name, identical parameter types (domain types only), compatible return type (domain type — not raw SDK response)
   - Missing method implementation = CRITICAL violation

4. **Check error handling** (HIGH if violations found)
   - All SDK exceptions must be caught within the adapter
   - Caught exceptions must be translated to typed domain exceptions before propagating
   - `throw err` or re-thrown infrastructure exceptions = HIGH violation (infrastructure leaks into domain)

5. **Verify no business logic** (CRITICAL if found)
   - Scan adapter methods for conditional logic based on business rules
   - Business logic in adapter = CRITICAL violation
   - Acceptable: retry logic, type mapping, error translation

6. **Check constructor injection** (HIGH if violated)
   - Infrastructure client must be injected via constructor — not instantiated inside methods
   - Static client instantiation inside adapter methods = HIGH violation

7. **Verify mapper separation** (MEDIUM if violated)
   - Domain ↔ infrastructure type translation must be in a separate mapper class
   - Inline mapping logic in adapter methods = MEDIUM violation

8. **Check retry logic** (MEDIUM if missing for outbound adapters)
   - Outbound adapters must implement retry with exponential backoff for transient failures

9. **Produce review report**
   - Overall verdict: PASS | CONDITIONAL PASS (medium only) | FAIL (critical or high)
   - Compliant items checklist
   - Violations table: severity, file:line, description, required fix
   - Required actions before merge-ready

## Output Artifacts

- **Review report** (inline or saved to `docs/reviews/<adapter-name>-review-<YYYY-MM-DD>.md`):
  - Overall verdict: PASS | CONDITIONAL PASS | FAIL
  - Compliant items: methods correctly implemented, error handling correct, no business logic
  - Violations table: severity (CRITICAL/HIGH/MEDIUM/LOW), location (file:line), description, required fix
  - Merge gate: any CRITICAL or HIGH finding blocks merge

## References

- [Implementation Guide: Port Adapter Standards](../../guides/agent-swarm-implementation-guide.md)
- [Scaffold Hexagonal Module Skill](../scaffold-hexagonal-module/SKILL.md)

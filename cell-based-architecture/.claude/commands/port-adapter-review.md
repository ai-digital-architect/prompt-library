---
description: >
  Perform a systematic review of an adapter against its port interface contract. Trigger phrases:
  review adapter, port contract, adapter correctness, check port implementation, validate adapter,
  adapter review, does this adapter implement the port correctly, port adapter review.
---

## Purpose

Perform a systematic review of an adapter implementation against its port interface contract, verifying method signatures, error handling, business logic absence, and domain type correctness.

## Inputs

Before execution, collect the following:

1. **Adapter file path** — path to the adapter class file to review (e.g., `src/order/adapter/outbound/DynamoOrderAdapter.ts`)
2. **Port interface path** — path to the port interface this adapter implements (e.g., `src/order/application/port/outbound/OrderRepository.ts`)
3. **Review scope** — `full` (all checks) or specific: `signatures`, `error-handling`, `business-logic`, `types`

## Procedure

1. **Read the port interface**
   - Read the port interface file completely
   - Document every method signature: name, parameter types, return type, error types declared
   - Note any doc comments explaining the contract expectations

2. **Read the adapter implementation**
   - Read the adapter class file completely
   - Identify the `implements` clause — verify it references exactly one port interface

3. **Validate method signatures**
   - For each method in the port interface, verify the adapter has an implementation with:
     - Identical method name (no aliasing, no renaming)
     - Identical parameter types (domain types — no infrastructure types in parameters)
     - Compatible return type (domain type — not a raw SDK response type)
   - Flag any missing method implementations as CRITICAL violations

4. **Check error handling**
   - Verify that all infrastructure SDK exceptions are caught within the adapter
   - Verify that caught exceptions are translated into typed domain exceptions before propagating
   - Flag any `throw err` or re-thrown infrastructure exceptions as HIGH violations (infrastructure leaks into domain)

5. **Verify no business logic in adapter**
   - Scan adapter methods for conditional logic based on business rules (not infrastructure concerns)
   - Business logic in an adapter (e.g., "if order total > 1000 then apply discount") is a CRITICAL violation
   - Acceptable: retry logic for transient failures, type mapping, error translation

6. **Check constructor injection**
   - Verify the infrastructure client is injected via the constructor — not instantiated inside methods
   - Flag static client instantiation inside adapter methods as HIGH violations

7. **Verify mapper separation**
   - Check that domain ↔ infrastructure type translation is in a separate mapper class
   - Inline mapping logic in adapter methods is a MEDIUM violation

8. **Check retry logic**
   - For outbound adapters: verify retry with exponential backoff is present for transient failures
   - Missing retry logic is a MEDIUM violation

9. **Produce review report**
   - Write the report to standard output (not a file, unless the user requests a saved report)
   - Structure: overall verdict (PASS / CONDITIONAL PASS / FAIL), compliant items, violations table, required fixes

## Output

- **Review report** — structured markdown with:
  - Overall verdict: PASS | CONDITIONAL PASS (medium violations only) | FAIL (critical or high violations)
  - Compliant items checklist
  - Violations table: severity, location (file:line), description, required fix
  - Summary of required actions before this adapter is merge-ready
- **Saved report** (if requested): `docs/reviews/<adapter-name>-review-<YYYY-MM-DD>.md`

---
description: >
  Generate an Architecture Decision Record in MADR format. Trigger phrases: architecture decision,
  ADR, document decision, record architectural choice, decision record, MADR, capture design choice.
---

## Purpose

Produce a structured Architecture Decision Record (ADR) in MADR format capturing the architectural context, decision drivers, options considered, and consequences of a design choice.

## Inputs

Before execution, collect the following:

1. **Decision title** — a short imperative phrase describing what was decided (e.g., "Use DynamoDB as the cell-local data store")
2. **Context** — the architectural situation: what system, what team, what constraints triggered this decision
3. **Decision drivers** — the quality attributes and constraints that must be satisfied (blast radius reduction, data residency, deployment independence, testability, cost)
4. **Options considered** — at least two alternatives that were evaluated
5. **Chosen option** — which option was selected
6. **Affected cells or modules** — which cell contracts, port interfaces, or bounded contexts this decision touches

## Procedure

1. **Collect context**
   - Describe the architectural situation in 2–4 sentences: what system, what team, what constraint or capability triggered the need for this decision
   - Identify the date and the decision participants

2. **List decision drivers**
   - Enumerate the quality attributes that must be satisfied: blast radius reduction, data residency, deployment independence, testability, cost per request, operational complexity
   - Order drivers by priority — the chosen option must satisfy the top-priority drivers

3. **Enumerate options considered**
   - List at least two alternatives
   - For each option: one-sentence description, pros, cons against the decision drivers

4. **Create comparison table**
   - Table rows: options; columns: each decision driver
   - Score each option against each driver: ✅ satisfies, ⚠️ partial, ❌ does not satisfy

5. **Write structured ADR in MADR format**
   - Title: `# NNN. <Decision Title>`
   - Status: `Accepted` | `Proposed` | `Superseded by NNN`
   - Context and Problem Statement
   - Decision Drivers (bulleted list)
   - Considered Options (bulleted list)
   - Decision Outcome (chosen option and rationale)
   - Pros and Cons of the Options (subsection per option)
   - Links (to affected cell contracts or port interfaces)

6. **Determine ADR number**
   - Read existing `adr/` directory to find the highest existing ADR number
   - Assign the next sequential number

7. **Write ADR file**
   - Write to `adr/NNN-<decision-title-in-kebab-case>.md`

8. **Add cross-references**
   - Append ADR reference to any affected `cell-contract.yaml` or port interface file

## Output

- **ADR file**: `adr/NNN-<decision-title>.md` in MADR format
- **Cross-references**: ADR number appended to affected cell contract files and port interface files
- **Summary**: one-line summary of the decision for the session log

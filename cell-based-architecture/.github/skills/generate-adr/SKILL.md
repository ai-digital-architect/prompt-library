---
name: generate-adr
description: >
  Use this skill when the user mentions: architecture decision, ADR, document
  decision, record architectural choice, decision record, MADR. Produces a
  structured Architecture Decision Record in MADR format capturing context,
  drivers, options, and consequences.
version: 1.0.0
---

## What This Skill Does

This skill produces a structured Architecture Decision Record (ADR) in MADR format, capturing the architectural context, decision drivers, options considered with trade-off analysis, and the chosen outcome with rationale — then writes the file to the `adr/` directory with the next sequential number.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "architecture decision", "ADR", "MADR"
- "document decision", "record architectural choice"
- "decision record", "capture design choice"
- "architectural trade-off", "record this decision"

## Prerequisites

Before this skill executes, the following must be true:
- A specific architectural decision has been made or is being evaluated
- At least two options were or are being considered
- The decision context (what system, what constraint, what triggered the decision) is known

## Step-by-Step Procedure

1. **Collect context**
   - Describe the architectural situation in 2–4 sentences: what system, what team, what constraint triggered the need
   - Identify the date and the relevant decision participants

2. **List decision drivers**
   - Enumerate quality attributes and constraints that must be satisfied:
     - Blast radius reduction, data residency, deployment independence, testability, cost per request, operational complexity
   - Order drivers by priority — the chosen option must satisfy the top-priority drivers

3. **Enumerate options considered**
   - At least two alternatives; each with:
     - One-sentence description
     - Pros against the decision drivers
     - Cons against the decision drivers

4. **Create trade-off comparison table**
   - Rows: options; Columns: each decision driver
   - Score each: ✅ satisfies, ⚠️ partial, ❌ does not satisfy

5. **Determine ADR number**
   - Scan `adr/` directory for the highest existing ADR number
   - Assign the next sequential number (zero-padded to 4 digits, e.g., `0012`)

6. **Write ADR in MADR format**
   ```
   # NNN. <Decision Title>
   **Status:** Accepted
   **Date:** YYYY-MM-DD

   ## Context and Problem Statement
   ## Decision Drivers
   ## Considered Options
   ## Decision Outcome
   ### Pros and Cons of the Options
   ### Option 1: <Name>
   ### Option 2: <Name>
   ## Links
   ```

7. **Write ADR file**
   - Write to `adr/NNN-<decision-title-in-kebab-case>.md`

8. **Add cross-references**
   - Append ADR reference to any affected `cell-contract.yaml` or port interface file

## Output Artifacts

- `adr/NNN-<decision-title>.md` — complete MADR-format ADR
- Cross-references appended to affected cell contract and port interface files
- One-line decision summary for session context

## References

- [Implementation Guide: Architecture Decisions](../../guides/agent-swarm-implementation-guide.md)
- [Design Cell Boundaries Skill](../design-cell-boundaries/SKILL.md)

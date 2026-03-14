---
name: brownfield-extract-cell
description: >
  Use this skill when the user mentions: extract cell, extract bounded context,
  decompose monolith, strangler fig, legacy decomposition, cell extraction, migrate
  service to cell. Produces a phased extraction plan with coupling graph analysis,
  seam identification, and scaffolded target cell structure.
version: 1.0.0
---

## What This Skill Does

This skill analyzes an existing codebase to map its coupling graph, identifies low-risk seam points for bounded context extraction, produces a phased migration plan with rollback procedures for each step, and scaffolds the target cell structure — all before a single line of existing code is modified.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "extract cell", "extract bounded context", "cell extraction"
- "decompose monolith", "strangler fig", "legacy decomposition"
- "migrate service to cell", "brownfield migration"
- "strangler fig pattern", "seam identification"

## Prerequisites

Before this skill executes, the following must be true:
- The target bounded context to extract has been identified (e.g., `Order`, `Payment`)
- The source codebase path is accessible for reading
- The extraction goal is stated (blast radius isolation, independent deployment, compliance boundary)
- The maximum rollback time constraint is known (default: 5 minutes per step)

## Step-by-Step Procedure

1. **Map the coupling graph**
   - Read `src/` to identify direct dependencies of the target bounded context:
     - Afferent coupling (Ca): which other modules call into it
     - Efferent coupling (Ce): which other modules it calls out to
     - Shared database tables with other modules
     - Events produced and consumed
   - Document all coupling points

2. **Calculate coupling metrics and rank candidates**
   - Instability: `I = Ce / (Ca + Ce)` — higher instability = better extraction candidate
   - Shared table count — fewer shared tables = lower extraction risk
   - Rank: fewest callers + fewest shared tables = first extraction target

3. **Identify seam points**
   - Best: service method boundary with no shared state
   - Good: existing repository interface (just move the implementation)
   - Acceptable: HTTP API boundary that can be proxied
   - Avoid: shared database tables (requires dual-write), distributed transactions

4. **Propose extraction sequence**
   - Step 1: Additive — introduce port interface at seam (no existing code changes)
   - Step 2: Legacy adapter — implement port by delegating to existing code
   - Step 3: Route tests through adapter; verify all pass
   - Step 4: Build new hexagonal domain in target cell
   - Step 5: Dual-write period — write to both old and new path; verify parity
   - Step 6: Cut over — update routing; monitor 48 hours
   - Step 7: Delete legacy path after validation period

5. **Produce migration plan document**
   - Write `migration/<bounded-context>-extraction-plan.md`
   - For each step: what changes, legacy adapter spec, rollback (< 5 minutes), acceptance criteria

6. **Generate ADR**
   - Invoke `generate-adr` skill: why this bounded context, why this seam, what temporary adapter strategy

7. **Scaffold target cell**
   - Invoke `greenfield-cell-setup` skill to create `cells/<cell-name>/` directory structure

8. **Specify first implementation task**
   - State exactly what `DeveloperAgent` should implement first: the port interface at the seam point

## Output Artifacts

- `migration/<bounded-context>-extraction-plan.md` — phased extraction plan with all steps detailed
- `migration/<bounded-context>-coupling-graph.md` — coupling analysis with metrics and rankings
- `adr/NNN-extract-<bounded-context>.md` — MADR-format extraction decision record
- `cells/<cell-name>/` — target cell directory structure (via greenfield-cell-setup skill)
- First implementation task specification for DeveloperAgent

## References

- [Implementation Guide: Brownfield Migration](../../guides/agent-swarm-implementation-guide.md)
- [Greenfield Cell Setup Skill](../greenfield-cell-setup/SKILL.md)
- [Generate ADR Skill](../generate-adr/SKILL.md)

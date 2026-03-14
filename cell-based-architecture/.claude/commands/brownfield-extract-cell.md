---
description: >
  Produce a phased extraction plan for extracting a bounded context from a monolith into a cell.
  Trigger phrases: extract cell, extract bounded context, decompose monolith, strangler fig,
  legacy decomposition, cell extraction, migrate service to cell, brownfield migration.
---

## Purpose

Produce a phased extraction plan with coupling graph analysis, seam identification, and scaffolded target cell structure for extracting a bounded context from an existing monolith or distributed system.

## Inputs

Before execution, collect the following:

1. **Target bounded context** — the domain concept to extract (e.g., `Order`, `Payment`, `Inventory`)
2. **Source codebase path** — root directory of the existing system to analyze
3. **Extraction goal** — what business outcome requires this extraction (blast radius isolation, independent deployment, compliance boundary, performance)
4. **Acceptable migration duration** — maximum time budget for the extraction in weeks or sprints
5. **Rollback constraint** — maximum time to roll back each extraction step (default: 5 minutes)

## Procedure

1. **Map the coupling graph**
   - Read `src/` to identify all direct dependencies of the target bounded context:
     - Which other modules call into it (afferent coupling)
     - Which other modules it calls (efferent coupling)
     - Which database tables it shares with other modules
     - Which events it produces and which modules consume them

2. **Identify seam points**
   - Find locations where a clean interface can be introduced without breaking existing callers:
     - Service method boundaries that have no shared state
     - Repository interfaces already in place
     - HTTP API boundaries that can be proxied
   - Avoid seams that require coordinated distributed transactions during the migration period

3. **Rank extraction complexity**
   - Score each candidate seam on: number of callers, shared table dependencies, test coverage, data migration risk
   - Order extraction steps from lowest total risk score to highest

4. **Propose the extraction sequence**
   - Step 1: Additive only — introduce port interface without changing existing code
   - Step 2: Wire a legacy adapter — implement the port by delegating to existing code
   - Step 3: Move tests — verify existing functionality passes through the adapter
   - Step 4: Implement new domain — build the new hexagonal module in the target cell
   - Step 5: Dual-write period — write to both old and new path; verify parity
   - Step 6: Cut over — update routing to use new cell; monitor for 48 hours
   - Step 7: Remove legacy path — delete old code after validation period

5. **Generate migration plan document**
   - Write `migration/<bounded-context>-extraction-plan.md` with each step detailed
   - For each step: what changes, what adapter wraps legacy code, rollback procedure, acceptance criteria

6. **Generate ADR for the extraction decision**
   - Invoke `/project:generate-adr` with: why this bounded context, why this seam, what the temporary adapter strategy is

7. **Scaffold the target cell structure**
   - Invoke `/project:greenfield-cell-setup` to create the target cell directory with health contract and CI/CD stub

8. **Identify first implementation task**
   - Specify exactly what `developer-agent` should implement first: the port interface at the identified seam point

## Output

- **Extraction plan**: `migration/<bounded-context>-extraction-plan.md` with phased steps
- **Coupling graph summary**: `migration/<bounded-context>-coupling-graph.md` with dependency analysis
- **Extraction ADR**: `adr/NNN-extract-<bounded-context>.md` in MADR format
- **Target cell scaffold**: `cells/<cell-name>/` directory structure (via greenfield-cell-setup)
- **First task specification**: precise description for `developer-agent` of what to implement first

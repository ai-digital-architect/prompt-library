---
name: design-cell-boundaries
description: >
  Use this skill when the user mentions: cell boundaries, partition strategy, cell
  design, blast radius planning, cell topology, how to partition the system, tenant
  isolation design. Guides the process from domain requirements through to a
  documented cell topology with ADR.
version: 1.0.0
---

## What This Skill Does

This skill guides the complete cell boundary design process: collecting domain requirements, evaluating partitioning key candidates, calculating blast radius tolerance, proposing a cell topology, and generating the Architecture Decision Record that locks in the decision.

## When This Skill Is Invoked

Invoke this skill when the user mentions any of the following:
- "cell boundaries", "design cell boundaries", "partition strategy"
- "blast radius planning", "blast radius tolerance"
- "cell topology", "cell design", "how to partition the system"
- "tenant isolation design", "cell partitioning"

## Prerequisites

Before this skill executes, the following must be true:
- The bounded context or system to be partitioned has been identified
- A high-level list of business capabilities is available
- The tenant model is known (single-tenant, multi-tenant shared, or multi-tenant isolated)
- The blast radius tolerance has been stated or a default of 5% will be used

## Step-by-Step Procedure

1. **Intake domain requirements**
   - Collect: business capabilities, expected traffic volume, tenant model, regulatory constraints (data residency, HIPAA, PCI, SOC 2)
   - Confirm whether this is a greenfield design or brownfield overlay

2. **Evaluate partitioning key candidates**
   - **Customer ID / Tenant ID**: natural for multi-tenant; enables per-tenant isolation; requires stable ID at request time
   - **Geographic region**: required for data residency; adds routing complexity; cells per region
   - **Tenant tier**: separates premium from standard capacity pools; simpler routing; risk of uneven load
   - **Hash-based shard**: even load distribution; no business meaning; harder to drain specific tenants
   - For each candidate, document: blast radius impact, routing complexity, data migration risk

3. **Calculate target cell count**
   - Formula: `cell_count = ceil(1 / blast_radius_tolerance)`
   - Example: 5% tolerance → minimum 20 cells; 2% tolerance → minimum 50 cells
   - Adjust for geographic distribution and regulatory isolation requirements

4. **Propose cell topology**
   - Specify: number of initial cells, regional placement, which services are cell-local vs. global
   - Define routing layer design: path-based, header-based, or DNS-based cell assignment
   - Specify inter-cell communication: events via shared EventBridge bus; no direct cell-to-cell invocation

5. **Draft cell contract template**
   - Define: required components per cell, required metrics, required alarms, capacity ceiling
   - Reference the `cell-health-check` skill for the full contract validation procedure

6. **Generate ADR**
   - Invoke the `generate-adr` skill to record: chosen partitioning key, options considered, blast radius calculation, topology decision

## Output Artifacts

- `docs/architecture/cell-topology.md` — topology diagram, partitioning key rationale, cell count calculation
- `adr/NNN-cell-partitioning-key.md` — MADR-format ADR for the partitioning decision
- `cells/template/cell-contract.yaml` — health contract template for new cells
- Partitioning key trade-off table — evaluating each candidate against all requirements

## References

- [Implementation Guide: Cell-Based Architecture](../../guides/agent-swarm-implementation-guide.md)
- [Cell Health Check Skill](../cell-health-check/SKILL.md)
- [Generate ADR Skill](../generate-adr/SKILL.md)

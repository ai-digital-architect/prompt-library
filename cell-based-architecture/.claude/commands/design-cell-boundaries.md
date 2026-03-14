---
description: >
  Design cell boundaries for a system. Trigger phrases: cell boundaries, partition strategy,
  blast radius planning, cell topology, how to partition the system, tenant isolation design,
  cell design, design cell architecture.
---

## Purpose

Guide the complete cell boundary design process from domain requirements through to a documented cell topology with an Architecture Decision Record.

## Inputs

Before execution, collect the following from the user:

1. **Business capabilities** — list of the core capabilities the system must deliver
2. **Traffic model** — expected request volume per day, peak load, and traffic distribution
3. **Tenant model** — single-tenant, multi-tenant (shared infrastructure), or multi-tenant (isolated per tenant)
4. **Blast radius tolerance** — maximum acceptable percentage of users impacted by a single cell failure (default: 5%)
5. **Regulatory constraints** — data residency requirements, compliance boundaries (HIPAA, PCI, SOC 2)
6. **Existing system context** — greenfield or brownfield; if brownfield, description of current topology

## Procedure

1. **Intake domain requirements**
   - Collect the business capabilities, traffic volume, tenant model, and regulatory constraints listed in Inputs
   - Identify whether this is a greenfield design or a brownfield decomposition

2. **Identify partitioning key candidates**
   - Evaluate these candidate keys against the intake requirements:
     - **Customer ID / Tenant ID** — natural for multi-tenant systems; enables per-tenant isolation
     - **Geographic region** — required when data residency constraints exist
     - **Tenant tier** — separates premium from standard capacity pools
     - **Hash-based shard** — distributes load evenly when tenants are homogeneous
   - Document trade-offs for each candidate: blast radius impact, routing complexity, data migration risk

3. **Calculate target cell count**
   - Formula: `cell_count = ceil(1 / blast_radius_tolerance)`
   - Example: 5% tolerance → minimum 20 cells
   - Adjust for geographic distribution and tenant isolation requirements

4. **Evaluate blast radius tolerance per candidate**
   - For each partitioning key, calculate: what percentage of total traffic does a single cell serve?
   - Confirm this percentage is within the stated tolerance

5. **Propose cell topology**
   - Specify: number of initial cells, their region placement
   - Define: which services are cell-local vs. global (shared routing layer, shared identity provider)
   - Design: routing layer strategy (path-based, header-based, or DNS-based cell assignment)
   - Specify: inter-cell communication pattern (events only via shared EventBridge bus; no direct calls)

6. **Document cell contracts**
   - For each cell type, draft the `cell-contract.yaml` structure (capacity ceiling, health endpoint, required alarms)
   - Identify cell-local data stores vs. global data stores

7. **Generate ADR**
   - Invoke the `generate-adr` command to record:
     - The chosen partitioning key and the options that were considered
     - The blast radius calculation and tolerance decision
     - The cell topology and routing layer design

## Output

- **Cell topology document**: `docs/architecture/cell-topology.md` with topology diagram and rationale
- **Partitioning key ADR**: `adr/NNN-cell-partitioning-key.md` in MADR format
- **Cell contract templates**: `cells/template/cell-contract.yaml` with required fields
- **Routing layer design**: section in topology document specifying routing rules and fallback behavior

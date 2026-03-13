---
name: cell-based-architecture
description: |
  Guide for designing and implementing cell-based architecture patterns. Use this skill whenever the user mentions: cell-based architecture, blast radius reduction, fault isolation, cellular deployment, multi-tenant isolation, regional deployment strategies, horizontal scaling via cells, routing layers, cell assignment, or resilient distributed systems. Also trigger when discussing AWS multi-region deployments with isolated workloads, reducing failure blast radius, or scaling by adding deployment units rather than scaling up. This skill provides both architect-level strategic guidance and developer-level implementation patterns.
---

# Cell-Based Architecture Skill

Cell-based architecture organizes systems into isolated, self-contained deployment units called "cells." Each cell operates independently with its own resources, creating natural fault boundaries that limit the blast radius of failures.

## When to Use This Skill

- Designing highly resilient distributed systems
- Planning multi-region AWS deployments
- Reducing blast radius for failures and bad deployments
- Scaling systems horizontally by adding cells
- Isolating tenants or customer groups
- Implementing canary deployment strategies

## Audience-Specific Guides

This skill contains two reference guides tailored to different roles:

### For Architects
Read `references/architect-guide.md` when making strategic decisions about:
- Cell topology and partitioning strategies
- Global vs. cell-local component placement
- Cross-cell coordination patterns
- Trade-off analysis (cost, complexity, resilience)
- Integration with existing bounded contexts

### For Developers
Read `references/developer-guide.md` when implementing:
- Cell infrastructure modules using Terraform
- Routing layer implementation with Terraform
- Cell assignment services
- Cross-cell event replication
- Observability per cell
- Multi-region Terraform workspace strategies

## Core Concepts Quick Reference

| Concept | Definition |
|---------|------------|
| **Cell** | Self-contained deployment unit with all resources needed to serve a subset of traffic |
| **Routing Layer** | Global component that directs requests to the appropriate cell |
| **Cell Assignment** | Service/data that maps customers to their assigned cell |
| **Blast Radius** | Scope of impact when something fails—cells limit this to affected cell only |
| **Cell Capacity** | Fixed upper bound of what a single cell can handle |

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   GLOBAL LAYER                          │
│  • Routing (Route 53, CloudFront, Global Accelerator)   │
│  • Cell Assignment Service                              │
│  • Shared Auth (Cognito)                                │
│  • Global Observability Dashboards                      │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     CELL A      │ │     CELL B      │ │     CELL C      │
│  (us-east-1)    │ │  (us-east-1)    │ │  (eu-west-1)    │
│                 │ │                 │ │                 │
│  • Compute      │ │  • Compute      │ │  • Compute      │
│  • Storage      │ │  • Storage      │ │  • Storage      │
│  • Events       │ │  • Events       │ │  • Events       │
│  • Queues       │ │  • Queues       │ │  • Queues       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Key Decision Points

Before diving into the detailed guides, answer these questions:

1. **Partitioning key**: What defines cell boundaries? (Customer ID, region, tenant, shard key)
2. **Cell granularity**: One cell per region, or multiple cells per region?
3. **Shared services**: What must remain global? (Auth, billing, onboarding)
4. **Cross-cell data**: Does any data need to span cells?
5. **Event strategy**: Do events need to flow between cells?

## Integration with Hexagonal Architecture

Cell-based architecture complements hexagonal architecture:

- **Hexagonal** defines *what runs inside* each cell (domain logic, ports, adapters)
- **Cell-based** defines *how cells are deployed and coordinated* (routing, assignment, isolation)

The hexagonal domain remains identical across cells. Only adapter configurations change per cell (region-specific endpoints, cell-specific resource names).

See the `hexagonal-architecture` skill for domain design patterns that work well within cells.

## Next Steps

1. Read the appropriate guide based on your role
2. Map your bounded contexts to potential cells
3. Identify your global layer components
4. Define your partitioning strategy
5. Design your routing and cell assignment approach

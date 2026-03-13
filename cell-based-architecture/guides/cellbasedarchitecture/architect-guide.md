# Cell-Based Architecture: Architect Guide

This guide covers strategic decisions, patterns, and trade-offs for architects designing cell-based systems.

## Table of Contents

1. [Strategic Positioning](#strategic-positioning)
2. [Cell Topology Decisions](#cell-topology-decisions)
3. [Global Layer Design](#global-layer-design)
4. [Cross-Cell Coordination](#cross-cell-coordination)
5. [Trade-Off Analysis](#trade-off-analysis)
6. [Migration Strategies](#migration-strategies)
7. [Governance and Standards](#governance-and-standards)

---

## Strategic Positioning

### When Cell Architecture Makes Sense

Cell architecture adds complexity. Justify it when:

- **Scale demands it**: You're operating at scale where a single deployment unit can't handle load
- **Blast radius matters**: Failures in production have caused significant business impact
- **Regulatory requirements**: Data residency or isolation requirements exist
- **Multi-tenant SaaS**: Tenants require isolation guarantees
- **Deployment velocity**: You need to deploy changes incrementally with low risk

### When to Avoid Cells

- Early-stage products where simplicity trumps resilience
- Systems with heavy cross-tenant data access patterns
- Teams without operational maturity to manage multiple deployment units

---

## Cell Topology Decisions

### Partitioning Strategies

| Strategy | Best For | Trade-offs |
|----------|----------|------------|
| **Customer/Tenant ID** | SaaS platforms, B2B | Clean isolation; customer migration between cells is complex |
| **Geographic Region** | Data residency requirements | Natural fit for regional services; cross-region queries are hard |
| **Hash-based Sharding** | Even load distribution | No semantic meaning; debugging harder |
| **Tiered (VIP cells)** | Premium customer isolation | Operational overhead of managing tiers |

### Cell Sizing Principles

**Fixed capacity ceiling**: Each cell should have a known maximum capacity (requests/sec, customers, data volume). When a cell approaches 70-80% capacity, provision a new cell.

**Right-sizing considerations**:
- Too small: Operational overhead of managing many cells
- Too large: Blast radius benefits diminish
- Sweet spot: Typically 1-5% of total traffic per cell

### Region vs. Cell Distinction

Regions and cells are orthogonal concepts:

```
Region: us-east-1
├── Cell: us-east-1-cell-01  (customers A-M)
├── Cell: us-east-1-cell-02  (customers N-Z)
└── Cell: us-east-1-cell-03  (VIP customers)

Region: eu-west-1
├── Cell: eu-west-1-cell-01  (EU customers)
└── Cell: eu-west-1-cell-02  (UK customers post-Brexit)
```

A region may contain multiple cells. A cell exists in exactly one region.

---

## Global Layer Design

The global layer is the critical shared infrastructure. It must be:
- Highly available (this is a single point of failure for all cells)
- Stateless or use globally replicated state
- Extremely simple (complexity here affects everyone)

### Routing Layer Architecture

**Option 1: DNS-based (Route 53)**
```
customer-123.api.example.com → CNAME → cell-02.us-east-1.api.example.com
```
- Pros: Simple, leverages DNS caching
- Cons: TTL delays for failover, limited routing logic

**Option 2: Edge-based (CloudFront + Lambda@Edge)**
```
api.example.com → CloudFront → Lambda@Edge (lookup cell) → Origin cell
```
- Pros: Flexible routing logic, fast failover
- Cons: Added latency, Lambda@Edge cold starts

**Option 3: Global Accelerator**
```
api.example.com → Global Accelerator → Endpoint group per cell
```
- Pros: Anycast IP, health-based routing
- Cons: Cost, less flexible than Lambda@Edge

### Cell Assignment Service

This service maintains the customer → cell mapping. Design options:

**DynamoDB Global Tables**
```
PK: CUSTOMER#{customer_id}
Attributes: cell_id, region, assigned_at, status
```
- Global replication built-in
- Single-digit millisecond lookups
- Handles cell migrations with status field

**Route 53 Records**
```
customer-123.cell-assignment.internal → TXT "cell-02.us-east-1"
```
- No custom service to maintain
- Limited to DNS record constraints
- Good for simple cases

### Shared Services Placement

| Service | Global or Cell-Local? | Rationale |
|---------|----------------------|-----------|
| Authentication | Global (Cognito) | Tokens must work across cells |
| Authorization | Cell-local | Permissions may be cell-specific |
| Customer Onboarding | Global | Must assign customer to cell |
| Billing/Metering | Global aggregation, cell-local collection | Aggregate for invoicing |
| Observability | Cell-local data, global dashboards | Data stays in cell, dashboards aggregate |

---

## Cross-Cell Coordination

### Event Flow Patterns

**Pattern 1: Cell-Local Events Only**
Events never leave the cell. Simplest model.
- Use when: Domains are fully isolated per cell
- Avoid when: Central systems need to react to cell events

**Pattern 2: Event Replication to Central Bus**
```
Cell EventBridge → EventBridge Rule → Cross-region EventBridge (central)
```
- Use when: Central analytics, billing, or audit systems exist
- Consider: Event ordering is not guaranteed cross-region

**Pattern 3: Fan-out from Central**
Central system publishes; cells subscribe.
```
Central EventBridge → SNS → SQS (per cell)
```
- Use when: Broadcasting configuration changes, feature flags

### Cross-Cell Data Access

**General principle**: Avoid cross-cell queries. If you need them frequently, your cell boundaries are wrong.

**When unavoidable**:
- **Scatter-gather**: Query all cells, aggregate results (expensive, last resort)
- **Replicated read models**: Project data to a global read store (DynamoDB Global Tables)
- **Customer data portability**: API for customers to export/import their data

---

## Trade-Off Analysis

### Cost Implications

| Factor | Impact |
|--------|--------|
| Infrastructure duplication | Each cell has its own DynamoDB tables, Lambda functions, etc. |
| Baseline costs | Minimum cost per cell even at zero traffic |
| Operational tooling | Investment in multi-cell deployment, monitoring, alerting |
| Team scaling | May need cell-aware on-call rotations |

**Cost model**: `Total Cost = (Fixed cost per cell × Number of cells) + (Variable cost × Total traffic)`

### Complexity Matrix

| Dimension | Single Deployment | Cell-Based |
|-----------|------------------|------------|
| Deployment | Simple | Multi-cell orchestration needed |
| Debugging | Straightforward | Must identify which cell first |
| Data model | Standard | Partitioned, migration complexity |
| Testing | Standard | Must test cell isolation, routing |
| DR/Failover | Region-level | Cell-level (more granular) |

### Resilience Gains

Quantify the value:
- **MTTR reduction**: Failures affect fewer customers, faster recovery
- **Deployment safety**: Canary to one cell, limited blast radius
- **Capacity planning**: Add cells vs. vertical scaling limits

---

## Migration Strategies

### Greenfield Approach

Start with cells from day one. Define:
1. Partitioning key (usually customer ID)
2. Initial cell count (start with 2-3)
3. Global layer components
4. Cell provisioning automation

### Brownfield Migration

Migrate existing monolith to cells incrementally:

**Phase 1: Shadow Cell**
- Deploy a cell alongside existing system
- Route a small percentage of traffic (1-5%)
- Compare behavior

**Phase 2: Customer Migration**
- Migrate customers batch by batch
- Start with low-risk customers
- Build confidence

**Phase 3: Cell Multiplication**
- Once first cell is stable, provision additional cells
- Distribute customers across cells

**Phase 4: Retire Monolith**
- Route remaining traffic to cells
- Decommission original deployment

---

## Governance and Standards

### Cell Contracts

Define what every cell must have:

```yaml
cell_contract:
  required_components:
    - api_gateway
    - compute (lambda or container)
    - primary_datastore
    - event_bus
    - dead_letter_queue
    - cloudwatch_alarms
    - xray_tracing
  
  required_metrics:
    - request_count
    - error_rate
    - latency_p99
    - cell_capacity_utilization
  
  required_alarms:
    - error_rate > 1%
    - latency_p99 > 500ms
    - capacity > 80%
```

### Cell Lifecycle

| State | Description |
|-------|-------------|
| Provisioning | Infrastructure deploying |
| Warming | Accepting test traffic only |
| Active | Accepting production traffic |
| Draining | No new assignments, serving existing |
| Decommissioned | All customers migrated out |

### Cell Health Indicators

Each cell should expose:
- `/health` endpoint for routing layer
- Capacity metrics (current vs. max)
- Error budget consumption
- Deployment version

### Naming Conventions

Consistent naming aids operations:

```
{service}-{region}-{cell-number}

Examples:
- payments-us-east-1-cell-01
- payments-eu-west-1-cell-01
- payments-us-east-1-cell-02
```

---

## Checklist: Ready for Cell Architecture?

Before committing to cell-based architecture:

- [ ] Identified partitioning key with clear customer → cell mapping
- [ ] Defined global layer components and their availability requirements
- [ ] Documented cross-cell data access patterns (ideally: none)
- [ ] Calculated cost model for N cells vs. current architecture
- [ ] Designed cell provisioning automation (Infrastructure as Code)
- [ ] Established cell health contracts and SLOs
- [ ] Planned routing layer implementation
- [ ] Defined cell migration strategy for existing customers
- [ ] Trained operations team on multi-cell debugging
- [ ] Built observability that spans cells (global dashboards)

# AWS Multi-Region DR Strategy — Decision Tree for Application Teams

A structured framework to route any application to the right disaster recovery strategy: **Backup & Restore**, **Pilot Light**, **Warm Standby**, or **Multi-Site Active/Active**. Work through the gates in order — each gate either terminates with a recommendation or passes you to the next.

---

## Guiding Principle

> **Pick the simplest, cheapest strategy that still meets your measured RTO/RPO.**
> Tighter objectives cost more, monotonically. "Zero RTO / zero RPO for everything" usually means no one did the business impact analysis. An RTO that has never been proven in a failover drill is an aspiration, not an objective.

---

## Gate 0 — Do You Even Need Multi-Region?

Multi-AZ within a single Region already protects against data center failure and is the AWS-recommended baseline for high availability.

```
Q0.1: Does the workload have a regulatory/contractual mandate for
      regional isolation or geographic redundancy?
        YES → Multi-region required. Go to Gate 1.
        NO  ↓
Q0.2: Would a full regional outage (rare, but historically multi-hour)
      cause unacceptable business damage per your BIA?
        YES → Multi-region required. Go to Gate 1.
        NO  ↓
Q0.3: Do you need low-latency access for globally distributed users?
        YES → Consider multi-region for performance; DR comes "free."
              Go to Gate 1 (bias toward Active/Active).
        NO  → ✅ STOP: Multi-AZ + cross-region backups
              (AWS Backup copy rules, S3 CRR) is sufficient.
              This IS Backup & Restore. Done.
```

**Anti-pattern:** Teams jumping to multi-region before their single-region architecture is Multi-AZ resilient. Fix that first.

---

## Gate 1 — Classify the Workload (Business Impact Analysis)

Answer with the **business owner**, not just engineering:

| Question | Output |
|---|---|
| Max tolerable downtime before unacceptable damage? | **RTO** |
| Max tolerable data loss (time since last recovery point)? | **RPO** |
| Revenue / safety / compliance impact per hour of outage? | Criticality tier |
| What % of production cost is DR worth? | Budget ceiling |

Map to a tier:

| Tier | Typical workloads | Target RTO | Target RPO |
|---|---|---|---|
| **T1 – Mission critical** | Payments, auth, order capture, patient safety | < 15 min (or near-zero) | Seconds to near-zero |
| **T2 – Business critical** | Core APIs, fulfillment, customer portal | 15 min – 1 hr | Seconds – minutes |
| **T3 – Important** | Internal tools, reporting, batch | 1 – 24 hrs | Minutes – hours |
| **T4 – Deferrable** | Dev/test, archives, sandboxes | > 24 hrs | Hours – 24 hrs |

---

## Gate 2 — The Core Decision Matrix (RTO Band × RPO Class)

Every application arrives with **two** registry-assigned classifications:

**RTO bands:** ≤ 2h · 2–4h · 4–24h · 24–48h · 48–72h

**RPO classes:**

| Class | Meaning | Data posture it dictates |
|---|---|---|
| **POF** (Point-of-Failure) | Recover to the moment of failure — near-zero data loss | Continuous cross-region replication of *every* stateful store (Aurora Global DB, DynamoDB Global Tables, DRS, MSK mirroring…) |
| **SOD** (Start-of-Day) | Recover to the start of the business day — intraday loss is acceptable | Daily SOD-cut backup with cross-region copy. Continuous replication is over-spend |
| **No Recovery** | No data restoration required (stateless, transient, or reconstructable from upstream feeds) | None. Rebuild from IaC + pipelines; Gate 3 is waived |

Because both axes are pre-assigned, **11 of the 15 matrix cells are deterministic** — no questions needed. Only Band 1 (all three classes) and Band 2 × SOD carry residual gates.

### The Matrix

| RTO ↓ \ RPO → | **POF** | **SOD** | **No Recovery** |
|---|---|---|---|
| **≤ 2h** | Near-zero? → *multi-region writes capable?* → **Active/Active**, else **Hot Warm Standby**. Not near-zero → **Warm Standby** (↓ **Pilot Light** if drilled automation proves < 2h stand-up) | Near-zero → **Hot Warm Standby** (standby data refreshed daily from SOD backup); else → **Warm Standby** (SOD refresh) | Near-zero → **Active/Active** (stateless — no data conflicts; the cheapest A/A there is); else → **Warm Standby** (stateless) |
| **2–4h** | **Pilot Light** | SOD-backup restore *proven* < 4h? → **Backup & Restore**; else → **Pilot Light** (daily SOD data refresh) | **IaC Rebuild** |
| **4–24h** | **Pilot Light** | **Backup & Restore** | **IaC Rebuild** |
| **24–48h** | **Pilot Light** | **Backup & Restore** | **IaC Rebuild** |
| **48–72h** | **Pilot Light** | **Backup & Restore (economy)** | **IaC Rebuild (economy)** |

### Residual gate questions

```
BAND 1 × POF
  Q: Near-zero (< 15 min) effective requirement?
     YES → Q: Data layer supports multi-region WRITES?
              YES → ACTIVE/ACTIVE      NO → HOT WARM STANDBY
     NO  → Q: IaC provisioning drilled to complete < 2 hrs?
              YES → PILOT LIGHT (cost downgrade)    NO → WARM STANDBY

BAND 1 × SOD
  Q: Near-zero (< 15 min)?
     YES → HOT WARM STANDBY (SOD-refreshed standby data)
     NO  → WARM STANDBY (SOD-refreshed standby data)
  (Active/Active never applies here — A/A implies live replicated
   data, which is POF-grade spend an SOD classification doesn't
   justify.)

BAND 1 × NO RECOVERY
  Q: Near-zero (< 15 min)?
     YES → ACTIVE/ACTIVE (stateless)   NO → WARM STANDBY (stateless)

BAND 2 × SOD
  Q: Full restore of the SOD backup PROVEN < 4 hrs in a drill,
     largest dataset included?
     YES → BACKUP & RESTORE            NO → PILOT LIGHT (SOD refresh)
```

### Three rules the matrix encodes

1. **RPO class sets the data posture — floor *and* ceiling.** POF forces continuous replication in every band (Pilot Light minimum, even at a 72-hour RTO). SOD caps justified data spend at daily backups — Aurora Global DB on an SOD-classified app is an automatic over-engineering flag for the CFO register. No Recovery deletes the data question entirely.
2. **RTO band sets the compute posture.** Strategy = data posture × compute posture; the matrix is just that product written out.
3. **Pilot Light vs Warm Standby (per AWS Well-Architected):** Pilot Light *cannot* serve requests until provisioned/scaled; Warm Standby *can* serve immediately at reduced capacity. Mislabeling this in Band 1 means a missed RTO.

*Note: this matrix supersedes generic Gate 1 tiering — with band and class pre-assigned, Gate 1 reduces to confirming the registry values are correct and disputing them through the data-correction workflow if not.*


---

## Gate 3 — Dependency Reality Check (The Real Constraint)

Your strategy is capped not by intent but by what your **dependencies** can do across regions. Three sub-inventories, all recorded as DDR evidence. *(3A is waived for No Recovery apps; 3B applies to every app — compute still fails over; 3C applies wherever a SaaS product sits in the critical path.)*

### 3A — AWS Data Stores

| Data store | Cross-region capability | Supports → |
|---|---|---|
| S3 | Cross-Region Replication (async, seconds–minutes) | All strategies |
| DynamoDB | Global Tables (active-active, last-writer-wins) | Up to Active/Active |
| Aurora | Global Database (~<1s replica lag; managed/planned failover; write forwarding) | Up to Active/Active-ish (single write master) |
| RDS (non-Aurora) | Cross-region read replicas (async, promote on failover) | Up to Warm Standby |
| ElastiCache Redis | Global Datastore | Up to Warm Standby / read-active |
| Self-managed DBs / EC2 | AWS Elastic Disaster Recovery (DRS) — continuous block replication | Backup & Restore / Pilot Light |
| Kafka/MSK, queues | Mirroring is hard; often the true RPO bottleneck | Audit carefully |

```
Q3A.1: Can every stateful AWS dependency meet the assigned RPO class?
        POF → continuous replication on EVERY store, or the class fails.
        SOD → daily SOD-cut backup with cross-region copy on every store.
Q3A.2: Chosen Active/Active — can writes conflict?
        YES with no partitioning/resolution → downgrade to hot Warm Standby.
Q3A.3: Does replication protect against corruption/deletion?
        NO — replication faithfully replicates a bad write. ALWAYS pair
        any strategy with point-in-time backups (mandatory for POF & SOD).
```

### 3B — AWS Service Scope & Static Stability

Classify **every** AWS dependency by scope — this is where regional failovers quietly fail:

| Scope | Examples | DR implication | DDR evidence to record |
|---|---|---|---|
| **Global** | IAM, Route 53, CloudFront, ACM (CloudFront certs live in us-east-1), Organizations | *Not* "safe by default": global services typically have a **control plane homed in one region** (commonly us-east-1) with a globally distributed **data plane**. Failover must depend on data planes only | Which global services are used; whether failover requires any of their control planes |
| **Regional** | EC2, Lambda, EKS, RDS, SQS/SNS, Secrets Manager, KMS, ECR, VPC endpoints | Each needs a configured **peer in the DR region**: config parity, quotas, AMIs, endpoints, keys | Per-service pairing status; quota parity verified; replication mechanism (KMS multi-region keys, Secrets Manager secret replication, ECR replication, IaC redeploy) |
| **Zonal / local** | EBS, instance store, single-AZ subnets, Local Zones, Outposts, Wavelength | Pinned to a physical location; recovery = snapshot/rebuild, never replication-in-place | Snapshot cadence + cross-region copy per zonal resource |

```
Q3B.1: Does failover require ANY control-plane call in — or homed in —
       the failed region (updating Route 53 via API, launching ASG
       capacity, creating IAM roles, raising quotas)?
        YES → static-stability flag for Band-1 / near-zero strategies.
              Prefer data-plane mechanisms (Route 53 ARC routing
              controls, pre-provisioned capacity).
Q3B.2: Are KMS keys multi-region and secrets replicated, so replicated
       data is actually DECRYPTABLE in the DR region?  NO → flag.
Q3B.3: Is every regional service offered — and quota'd — in the chosen
       DR region? (Service availability differs by region.)
        NO → the region pair is invalid; re-select.
```

### 3C — SaaS Data Planes (MongoDB Atlas, Snowflake, Starburst, …)

SaaS products sit outside your AWS account but **inside your RTO/RPO math**. Record per product:

| Evidence | Why it matters |
|---|---|
| Vendor, product, plan/edition | DR features are edition-gated — e.g. Snowflake failover groups + Client Redirect require Business Critical |
| Homed cloud + region(s) | **Correlated failure:** a SaaS homed in your primary AWS region, without replication configured, makes your regional DR strategy fiction |
| Native multi-region capability, and whether it is **configured** | Atlas: multi-region clusters with cross-region electable nodes, automatic failover. Snowflake: scheduled replication + failover groups — **your RPO is the refresh cadence**. Starburst: federated query engine, largely stateless — DR = redeploy + catalog config; the *data* DR lives in its underlying sources |
| Contractual / achievable RPO & RTO | Vendor SLA credits ≠ recovery. Record what the contract commits and what a test proved |
| Network path DR-ready | PrivateLink / VPC endpoints are **regional** — are they pre-provisioned in the DR region? |
| Auth path DR-ready | SSO/IdP dependency at failover time |
| Vendor DR evidence | Attestation, SOC 2, date of last joint failover test |

```
Q3C.1: Is any critical-path SaaS homed in the same region as the app's
       primary, with multi-region NOT configured?  YES → high-severity
       flag (hidden coupling defeats the whole strategy).
Q3C.2: POF class — does every SaaS data plane provide configured
       continuous/native replication meeting point-of-failure?
        NO → effective RPO class downgrades; flag.
Q3C.3: Are DR-region network + auth paths to each SaaS tested?
```

**Effective objectives are computed, not declared:** effective RPO = worst across 3A + 3C data planes; effective RTO = max(own failover, slowest vendor failover). The DDR persists these server-computed values next to the targets.

**Program note:** vendors are shared across hundreds of the 500 apps. Capability facts (what Atlas/Snowflake/Starburst *can* do per edition) live once in a central, architect-maintained **Vendor DR Catalog**; each DDR records only the app's *configuration* against that catalog entry — 500 teams never re-research the same vendor.


---

## Gate 4 — Modifiers (Can Move You Up or Down One Level)

| Modifier | Effect |
|---|---|
| **Compliance / data residency** limits which Region pairs are legal | Constrains region choice; may force in-country pairs |
| **Ops maturity**: no IaC, no runbooks, never run a game day | ⬇ Downgrade one level — you can't operate what you can't drill |
| **Everything in IaC + automated pipelines** | Pilot Light gets much cheaper/faster; RTO shrinks |
| **DR budget < ~25% of prod cost** | Backup & Restore or Pilot Light territory |
| **DR budget tolerates 100%+ of prod** | Active/Active viable |
| **Hard dependency on a single-region third party or AWS service** | Your DR is capped by theirs; document it, don't pretend |
| **Static stability required** (failover must not depend on the failing region or on control-plane calls) | Pre-provision capacity; prefer data-plane failover (Route 53 ARC) |

Rough cost bands (of production spend): Backup & Restore ~10–20%, Pilot Light ~20–40%, Warm Standby ~40–70%, Active/Active ~100–200%+.

---

## Gate 5 — Failover Mechanics & Anti-Patterns

Whatever strategy you land on:

- **Traffic shift:** Route 53 health-check failover or, for critical tiers, **Route 53 Application Recovery Controller** (data-plane routing controls that work even when the primary region's control plane is degraded). Set sane TTLs; test client DNS-caching behavior.
- **Decide who pulls the trigger:** automated failover for T1 (with guardrails against flapping), human-approved for lower tiers. Write the runbook either way.
- **Static stability:** at failover time, avoid depending on launching new resources via control-plane APIs in the surviving region if your RTO is tight — pre-provision or pre-scale.
- **Failback is a plan, not an afterthought:** data reconciliation after failover is often harder than failover itself.
- **Common failure modes:** untested IAM/quotas/AMIs in the DR region; secrets not replicated; DNS TTLs ignored; "warm standby" that was never scaled up under load; backups that were never restore-tested; replication of corruption with no PITR.

---

## Gate 6 — Prove It (or You Don't Have It)

```
Q6.1: Have you executed a full failover drill in the last 6–12 months
      and MEASURED actual RTO/RPO?
        NO → Your effective strategy is one level below what you built.
Q6.2: Do drills include the data layer (promote replicas, verify
      integrity), not just compute?
Q6.3: Is drift between regions prevented (same IaC, same pipeline
      deploys to both regions)?
```

Cadence: T1 quarterly game days; T2 semi-annual; T3/T4 annual restore tests.

---

## One-Page Worksheet (per application)

1. Tier: ___ RTO: ___ RPO: ___ DR budget ceiling: ___% of prod
2. Gate 0 result: Multi-AZ only / Multi-region required
3. Gate 2 candidate strategy: ___
4. Worst data-layer RPO across dependencies: ___ → strategy confirmed / revised to: ___
5. Modifiers applied (Gate 4): ___
6. Failover trigger: automated / manual — owner: ___
7. Last measured drill: date ___ actual RTO ___ actual RPO ___

## Quick Reference

| Strategy | RPO | RTO | Cost | Failover action |
|---|---|---|---|---|
| Backup & Restore | Hours | Hours–24h | $ | Restore + rebuild from IaC |
| Pilot Light | Minutes | 10s of min–hrs | $$ | Provision/scale, then shift traffic |
| Warm Standby | Seconds–min | Minutes | $$$ | Scale up + shift traffic |
| Multi-Site Active/Active | Near-zero | Near-zero | $$$$ | Remove failed region from rotation |

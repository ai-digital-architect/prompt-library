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

## Gate 2 — The Core Decision Tree

```
START: What is the workload's RTO?
│
├─ RTO > 4 hours (T3/T4)?
│    └─ Is RPO ≥ ~1 hour acceptable?
│         YES → ✅ BACKUP & RESTORE
│         NO (RPO minutes but slow recovery OK)
│             → ✅ PILOT LIGHT (data replicated live, infra dormant)
│
├─ RTO 30 min – 4 hours (T2/T3)?
│    └─ Can you tolerate manual/scripted provisioning at failover time?
│         YES → ✅ PILOT LIGHT
│         NO  → ✅ WARM STANDBY
│
├─ RTO 5 – 30 min (T1/T2)?
│    └─ ✅ WARM STANDBY
│       (scaled-down but *functional* stack, serving-capable immediately;
│        failover = scale up + shift traffic)
│
└─ RTO < 5 min / near-zero (T1)?
     └─ Q: Can the data layer support multi-region WRITES?
        (conflict resolution, or writes partitioned by region/user,
         or write-to-one-region with fast regional read replicas)
          YES, and team can operate it
              → ✅ MULTI-SITE ACTIVE/ACTIVE
          NO
              → ✅ WARM STANDBY AT (NEAR) FULL CAPACITY
                 ("hot standby" / active-passive) with automated
                 failover via Route 53 ARC. Honest near-zero RTO
                 without distributed-write complexity.
```

**Key distinction (per AWS Well-Architected):** Pilot Light *cannot* serve requests until action is taken (provision/scale); Warm Standby *can* serve immediately at reduced capacity. If your "warm standby" needs manual steps before serving any traffic, it's actually pilot light — label it honestly.

---

## Gate 3 — Data Layer Reality Check (The Real Constraint)

Your compute strategy is capped by what your **data layer** can replicate. Verify before committing:

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
Q3.1: Can every stateful dependency meet the target RPO cross-region?
        NO → Your real RPO = worst dependency. Either fix that
             dependency or relax the objective. Loop back to Gate 2.
Q3.2: Chosen Active/Active — can writes conflict?
        YES, and no partitioning/resolution scheme
             → Downgrade to hot Warm Standby (active-passive).
Q3.3: Does replication protect against corruption/deletion?
        NO — replication faithfully replicates a bad write.
             ALWAYS pair any strategy with point-in-time backups
             (this is mandatory even for Active/Active).
```

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

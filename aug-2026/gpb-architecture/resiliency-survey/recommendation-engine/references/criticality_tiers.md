# Criticality Tiers

| Tier | Name | AWS DR Strategy | RTO | Failure Behavior |
|---|---|---|---|---|
| **Tier 1** | Standard | Single-Region, Multi-AZ | > 48h | AZ failover, region impact. |
| **Tier 2** | Enhanced | Multi-Region, Active / Passive | 4h < RTO < 48h | Regional failover, Passive to Active Transition, Directional Replication from Active to Passive. |
| **Tier 3** | Critical | Multi-Region, Active / Active | RTO < 4h | Continuous Operation, No user Impact, Seamless Redirection. |
| **Tier 4** | Mission Critical | Multi-Region, Advanced Resilience | CPOF | Self healing, multi-site Active / Active, geometric resilience. |

*(Note: Tier 3 is mapped to Active/Active to resolve the architectural conflict regarding "Continuous Operation")*

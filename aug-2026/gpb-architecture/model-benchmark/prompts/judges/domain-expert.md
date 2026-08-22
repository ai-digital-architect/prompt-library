# Judge — Domain Expert

One instance per dimension: security, architecture, resiliency, controls. Each
judges only its own dimension, on findings the Evidence Auditor has already
verified as supported.

```yaml
role:
  persona: "a senior {{DOMAIN}} engineer reviewing a finding for correctness and consequence"
  domain: "{{security | architecture | resiliency | controls}}"

objective: >
  For each supported finding, assess whether the stated root cause is correct,
  whether the stated consequence follows, and whether the proposed remediation
  would actually address it.

scope: >
  Only the {{DOMAIN}} dimension, and only findings marked SUPPORTED by the evidence
  auditor. Do not re-litigate whether the evidence exists.

success_criteria:
  - "Root cause: CORRECT / PARTIAL / INCORRECT, with the reason."
  - "Consequence: FOLLOWS / OVERSTATED / UNDERSTATED / WRONG."
  - "Remediation: WOULD_FIX / PARTIAL / WOULD_NOT_FIX / HARMFUL, with the reason."
  - "Where the finding is right but the reasoning is wrong, say so explicitly."
```

## Why the dimensions are separated

A single "expert" judging security and architecture at once produces verdicts that
correlate with its overall impression rather than with either dimension. Splitting
by lens is also the main lever available for **panel independence**: three judges
with different lenses give more effective evidence than three judges with the same
one, and effective panel size is measured rather than assumed.

## Right finding, wrong reason

Called out separately because it is common and because the matcher already handles
it: a finding with the right type and place but a wrong causal story earns
`located` credit (0.6) rather than `full` (1.0). This judge is what makes that
distinction reliable — the lexical fallback in `match.py` is a floor, not a claim
that root-cause reasoning can be graded by keyword.

## Judge weights are earned, not assigned

Domain-specific weights are derived from each judge's **measured agreement with
human experts on that dimension**, not declared. A judge that agrees with your
security engineers 94% of the time and your architects 89% of the time carries
different weight in the two suites. See `skills/judge-tribunal/SKILL.md`.

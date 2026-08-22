# Canonical prompt — security review

```yaml
role:
  persona: "a principal engineer performing a pre-release security review"
  domain: "application security in enterprise services"

objective: >
  Review the attached corpus for security vulnerabilities. For each one, identify
  the vulnerable code, the path by which attacker-controlled input reaches it, the
  root cause, and a remediation.

scope: >
  The attached corpus only. Cover every file in it, not only the first file you
  examine.

success_criteria:
  - "Every vulnerability present in the corpus is reported."
  - "Each finding names the vulnerable symbol and its evidence location."
  - "Each finding states the source-to-sink path as structured relations."
  - "Each finding carries a calibrated confidence and an estimated severity."
  - "Exploitability is marked confirmed or theoretical."
  - "Findings that cannot be confirmed from the corpus are marked SUSPECTED rather than omitted."
```

## Phrasing this defensively matters

This is the suite most likely to trigger provider safety classifiers, and
classifier coverage differs by vendor. Two practical consequences:

1. **Ask for identification and remediation, never for exploit construction.** The
   task is "find and fix", not "weaponize". A defensively-phrased review gets
   through classifiers that an offensively-phrased one does not, and it is also
   what the benchmark actually wants to measure.
2. **Refusals are dispositioned, never scored as recall zero.** A harness that
   scored them as empty finding sets would systematically rank
   classifier-bearing models lower on security — a wrong strategic conclusion
   drawn from a parsing bug. Refusal rates are published beside the scores, with
   categories.

`beta = 1.5` on this suite: recall-leaning, because a missed vulnerability costs
more than a false alarm. Declared in the suite manifest and versioned, so the
policy choice is visible rather than buried in a default.

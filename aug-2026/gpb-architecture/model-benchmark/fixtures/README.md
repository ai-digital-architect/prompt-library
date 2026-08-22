# Fixtures

## `sample-repo/`

A deliberately small, deliberately flawed Java corpus. The defects in it are the
oracle for the bundled suites:

| File | Seeded defect | Suite |
| --- | --- | --- |
| `OrderRepository.java` | CWE-89 — string concatenation into SQL, reachable from `PaymentController.search` | security-v1 |
| `PaymentClient.java` | no timeout on an external synchronous call; unbounded retry policy — two findings sharing one call site | resiliency-v1, controls-v1 |
| `ReportingService.java` | bounded-context leakage — reporting reads the payments repository directly | semantic-v1, architecture-v1 |
| `PaymentController.java` | layer violation — controller reaches a repository directly | architecture-v1 |
| `FraudService.java`, `KafkaPublisher.java` | **clean** — the clean-file control | security-v1 SEC-0002 |

The clean files matter as much as the flawed ones. A suite where every item
contains a defect teaches models to always find one, and the clean-file control is
the single most informative item for measuring over-claiming.

## `cassettes/`

**Synthetic. Not measurements of any model.** Every cassette is stamped
`"synthetic": true` and the report footnotes them.

Their job is to exercise the paths that are easy to get wrong:

| Path | Where |
| --- | --- |
| well-formed high-quality answer | most models on SEM-0001 |
| partially-correct answer (located / adjacent credit) | mid-tier models on SEC-0001 |
| over-claiming on an unanswerable item | low-quality models on SEM-0001 Q-03 |
| speculative finding on the clean-file control | low-quality models on SEC-0002 |
| **safety refusal** on the security suite | `claude-fable-5` / SEC-0001 |
| **schema-invalid** prose response | `gpt-5.6-luna` / SEM-0002 |
| **truncated** response | `claude-opus-4-6` / SEC-0001 |

Regenerate:

```bash
python3 fixtures/make_cassettes.py
```

Record real ones:

```bash
python3 scripts/mb.py run --benchmark config/my-study.yaml --live --record
```

Cassettes are keyed on `(model, task, trial)` and fall back to trial 1. They do
**not** vary by effort level, so an effort sweep in replay mode will show identical
quality across the ladder — expected, and not a bug in the sweep.

A missing cassette is a hard error rather than an empty response: an empty response
would score as recall zero and look like a model failure.

## `graph.json` (optional)

If a corpus ships one, `local_graph` loads it in preference to regex extraction:

```json
{
  "nodes": [{ "id": "PaymentService.charge", "name": "charge", "kind": "method",
              "file": "PaymentService.java", "line": 11, "owner": "PaymentService" }],
  "edges": [{ "subject": "PaymentService", "predicate": "CALLS",
              "object": "PaymentClient.callGateway" }]
}
```

This is the cheapest way to give a suite richer ground truth without standing up
the full platform integration.

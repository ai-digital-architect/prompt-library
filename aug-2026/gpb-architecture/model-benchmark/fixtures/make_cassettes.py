#!/usr/bin/env python3
"""Generate SYNTHETIC replay cassettes for the bundled fixtures.

These are NOT measurements. They are hand-shaped responses whose only job is to
exercise the pipeline: normalization, entity resolution, claim verification,
finding matching, credit tiers, calibration, abstention, dispositions, cost
accounting and statistics. Every cassette is stamped `"synthetic": true` and the
report footnotes them.

The set is designed to hit the paths that are easy to get wrong:

  * a well-formed high-quality answer                (scores well)
  * a partially-correct answer                       (located / adjacent credit)
  * an over-claiming answer on an unanswerable item  (over-claim penalty)
  * a speculative answer on the clean-file control   (false positive pressure)
  * a SAFETY REFUSAL on the security suite           (excluded, not zeroed)
  * a schema-invalid response                        (SCHEMA_INVALID disposition)
  * a truncated response                             (TRUNCATED disposition)

Re-record real cassettes with:  mb.py run --benchmark <study> --live --record
"""

from __future__ import annotations

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "cassettes"
OUT.mkdir(exist_ok=True)

MODELS = {
    "claude-fable-5": ("anthropic", 0.92),
    "claude-opus-5": ("anthropic", 0.88),
    "claude-sonnet-5": ("anthropic", 0.80),
    "claude-opus-4-8": ("anthropic", 0.74),
    "claude-opus-4-7": ("anthropic", 0.70),
    "claude-opus-4-6": ("anthropic", 0.64),
    "gpt-5.6-sol": ("openai", 0.90),
    "gpt-5.6-terra": ("openai", 0.78),
    "gpt-5.6-luna": ("openai", 0.62),
    "gemini-3.6-flash": ("google", 0.82),
}

# Models that decline the security suite in this fixture set, so the disposition
# path is exercised. Any resemblance to real classifier behaviour is incidental —
# the point is that the harness must not score these as recall zero.
REFUSERS = {("claude-fable-5", "SEC-0001")}
SCHEMA_BREAKERS = {("gpt-5.6-luna", "SEM-0002")}
TRUNCATORS = {("claude-opus-4-6", "SEC-0001")}


def sem_0001(quality: float) -> dict:
    rels = [
        ("PaymentService", "CALLS", "PaymentRepository.save", "synchronous"),
        ("PaymentService", "CALLS", "FraudService.assess", "synchronous"),
        ("PaymentService", "CALLS", "KafkaPublisher.publish", "asynchronous"),
        ("PaymentService", "CALLS", "PaymentClient.callGateway", "synchronous"),
        ("PaymentController", "CALLS", "PaymentService.charge", None),
    ]
    keep = max(2, int(len(rels) * quality))
    chosen = rels[:keep]
    answers = [{
        "question_id": "Q-01",
        "answer": "PaymentService calls the repository, fraud service, Kafka publisher and gateway client.",
        "confidence": round(min(0.97, quality + 0.05), 2),
        "entities": [{"kind": "method", "ref": r[2]} for r in chosen],
        "relations": [
            {"subject": r[0], "predicate": r[1], "object": r[2],
             **({"modality": r[3]} if r[3] else {})} for r in chosen
        ],
    }, {
        "question_id": "Q-02",
        "answer": "No. The Kafka publisher does not write to the payment repository.",
        "confidence": round(min(0.95, quality), 2),
        "entities": [{"kind": "class", "ref": "KafkaPublisher"}],
        "relations": [],
    }]
    abstentions = []
    if quality >= 0.75:
        # Correct behaviour: Q-03 is unanswerable from the corpus.
        abstentions.append({
            "question_id": "Q-03",
            "reason": "The corpus contains no telemetry or latency measurements.",
            "what_would_resolve_it": "Production latency metrics for the gateway dependency.",
        })
    else:
        # Over-claim: answers an item the oracle marks unanswerable.
        answers.append({
            "question_id": "Q-03",
            "answer": "Roughly 250ms p99.",
            "confidence": 0.71,
            "entities": [{"kind": "external_system", "ref": "gateway.example.com"}],
            "relations": [],
        })
    if quality < 0.7:
        # Hallucinated structure — the suite's FALSE relations exist to catch this.
        answers[0]["relations"].append(
            {"subject": "KafkaPublisher", "predicate": "CALLS", "object": "PaymentRepository.save"})
    return {"schema_version": "1.0.0", "findings": [], "abstentions": abstentions,
            "answers": answers,
            "coverage_notes": "Examined every file in the payments package."}


def sem_0002(quality: float) -> dict:
    findings = []
    if quality >= 0.6:
        findings.append({
            "id": "F-01", "category": "architecture", "type": "shared_datastore",
            "severity": "medium" if quality >= 0.75 else "low",
            "confidence": round(min(0.93, quality), 2),
            "status": "ASSERTED",
            "entities": [{"kind": "class", "ref": "ReportingService", "role": "site"},
                         {"kind": "class", "ref": "PaymentRepository", "role": "dependency"}],
            "relations": [{"subject": "ReportingService", "predicate": "DEPENDS_ON",
                           "object": "PaymentRepository"}],
            "evidence": [{"file": "ReportingService.java", "symbol": "build", "lines": "4-9"}],
            "root_cause": ("ReportingService reads the payments repository directly, which is "
                           "cross_context_datastore_access — a bounded_context_leakage."
                           if quality >= 0.75 else
                           "ReportingService and PaymentService both use the same repository."),
            "impact": "Extracting reporting into its own service becomes a distributed coupling problem.",
            "recommendation": "Expose a published read interface from the payments context.",
        })
    if quality < 0.7:
        # A speculative extra finding, unmatched — exercises the `unverifiable`
        # bucket rather than being counted as a false positive.
        findings.append({
            "id": "F-02", "category": "architecture", "type": "cyclic_dependency",
            "severity": "high", "confidence": 0.66, "status": "ASSERTED",
            "entities": [{"kind": "class", "ref": "PaymentService"}],
            "relations": [],
            "evidence": [{"file": "PaymentService.java", "lines": "1-20"}],
            "root_cause": "Suspected cycle between service and repository layers.",
            "impact": "Difficult to test in isolation.",
            "recommendation": "Introduce an interface.",
        })
    return {"schema_version": "1.0.0", "findings": findings, "abstentions": [],
            "answers": [{
                "question_id": "Q-01",
                "answer": "PaymentService and ReportingService reference PaymentRepository.",
                "confidence": round(min(0.95, quality + 0.03), 2),
                "entities": [{"kind": "class", "ref": "PaymentService"},
                             {"kind": "class", "ref": "ReportingService"}],
                "relations": [
                    {"subject": "PaymentService", "predicate": "DEPENDS_ON", "object": "PaymentRepository"},
                    {"subject": "ReportingService", "predicate": "DEPENDS_ON", "object": "PaymentRepository"},
                ],
            }]}


def sec_0001(quality: float) -> dict:
    findings = []
    if quality >= 0.55:
        findings.append({
            "id": "F-01", "category": "security",
            "type": "CWE-89" if quality >= 0.7 else "injection",
            "severity": "high" if quality >= 0.7 else "medium",
            "confidence": round(min(0.96, quality + 0.04), 2),
            "status": "ASSERTED",
            "entities": [{"kind": "method", "ref": "OrderRepository.findOrders", "role": "sink"},
                         {"kind": "method", "ref": "PaymentController.search", "role": "source"}],
            "relations": [{"subject": "PaymentController.search", "predicate": "CALLS",
                           "object": "OrderRepository.findOrders"}],
            "evidence": [{"file": "OrderRepository.java", "symbol": "findOrders", "lines": "8-12",
                          "excerpt": "\"SELECT * FROM orders WHERE customer_name = '\" + query"}],
            "root_cause": ("String concatenation into SQL — an unparameterized_query reachable "
                           "from an untrusted request parameter."
                           if quality >= 0.7 else
                           "User input reaches the database layer."),
            "impact": "Full read access to the orders table, and potentially write access.",
            "recommendation": "Use a parameterized statement with a bound parameter for query.",
            "exploitability": "confirmed" if quality >= 0.8 else "theoretical",
        })
    if quality < 0.68:
        findings.append({
            "id": "F-02", "category": "security", "type": "CWE-798",
            "severity": "high", "confidence": 0.81, "status": "ASSERTED",
            "entities": [{"kind": "method", "ref": "PaymentClient.callGateway"}],
            "relations": [],
            "evidence": [{"file": "PaymentClient.java", "lines": "18"}],
            "root_cause": "Hardcoded gateway endpoint suggests embedded credentials.",
            "impact": "Credential exposure.",
            "recommendation": "Move to a secret manager.",
        })
    return {"schema_version": "1.0.0", "findings": findings, "abstentions": [],
            "coverage_notes": "Reviewed every file in the payments package."}


def sec_0002(quality: float) -> dict:
    """Clean-file control. The correct answer is an empty findings array."""
    if quality >= 0.78:
        return {"schema_version": "1.0.0", "findings": [], "abstentions": [],
                "coverage_notes": ("Reviewed FraudService and KafkaPublisher. No vulnerability "
                                   "found; both delegate without handling untrusted input.")}
    finding = {
        "id": "F-01", "category": "security", "type": "CWE-862",
        "severity": "medium" if quality >= 0.65 else "high",
        "confidence": 0.42 if quality >= 0.65 else 0.79,
        "status": "SUSPECTED" if quality >= 0.65 else "ASSERTED",
        "entities": [{"kind": "method", "ref": "FraudService.assess"}],
        "relations": [],
        "evidence": [{"file": "FraudService.java", "lines": "3-6"}],
        "root_cause": "No authorization check before scoring a request.",
        "impact": "Unauthorized risk scoring.",
        "recommendation": "Add an authorization check.",
    }
    return {"schema_version": "1.0.0", "findings": [finding], "abstentions": [],
            "coverage_notes": "Reviewed FraudService and KafkaPublisher."}


BUILDERS = {"SEM-0001": sem_0001, "SEM-0002": sem_0002,
            "SEC-0001": sec_0001, "SEC-0002": sec_0002}


def wrap(provider: str, payload: dict, tokens_in: int, tokens_out: int) -> dict:
    body_text = json.dumps(payload)
    if provider == "anthropic":
        return {"model": "recorded", "stop_reason": "end_turn",
                "content": [{"type": "text", "text": body_text}],
                "usage": {"input_tokens": tokens_in, "output_tokens": tokens_out,
                          "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}
    if provider == "openai":
        return {"model": "recorded", "status": "completed",
                "output": [{"content": [{"type": "output_text", "text": body_text}]}],
                "usage": {"input_tokens": tokens_in, "output_tokens": tokens_out,
                          "input_tokens_details": {"cached_tokens": 0},
                          "output_tokens_details": {"reasoning_tokens": int(tokens_out * 0.4)}}}
    return {"modelVersion": "recorded",
            "candidates": [{"finishReason": "STOP",
                            "content": {"parts": [{"text": body_text}]}}],
            "usageMetadata": {"promptTokenCount": tokens_in,
                              "candidatesTokenCount": tokens_out,
                              "cachedContentTokenCount": 0,
                              "thoughtsTokenCount": int(tokens_out * 0.3)}}


def refusal(provider: str) -> dict:
    if provider == "anthropic":
        return {"model": "recorded", "stop_reason": "refusal",
                "stop_details": {"category": "offensive_cybersecurity"},
                "content": [], "usage": {"input_tokens": 4200, "output_tokens": 12}}
    if provider == "openai":
        return {"model": "recorded", "status": "completed",
                "output": [{"content": [{"type": "refusal", "refusal": "declined"}]}],
                "usage": {"input_tokens": 4200, "output_tokens": 12,
                          "input_tokens_details": {"cached_tokens": 0},
                          "output_tokens_details": {"reasoning_tokens": 0}}}
    return {"modelVersion": "recorded", "promptFeedback": {"blockReason": "SAFETY"},
            "candidates": [], "usageMetadata": {"promptTokenCount": 4200,
                                                "candidatesTokenCount": 0}}


def main():
    rng = random.Random(20260822)
    written = 0
    for model, (provider, quality) in MODELS.items():
        for task, builder in BUILDERS.items():
            key = (model, task)
            tokens_in = rng.randint(3500, 6000)
            tokens_out = rng.randint(900, 2600)

            if key in REFUSERS:
                body = refusal(provider)
            elif key in SCHEMA_BREAKERS:
                # Prose where JSON was required — a real, common failure mode.
                body = wrap(provider, {}, tokens_in, 300)
                body_text = ("Here is my analysis:\n\nPaymentService and ReportingService both "
                             "reference PaymentRepository. I was unable to produce the requested "
                             "JSON structure.")
                if provider == "anthropic":
                    body["content"] = [{"type": "text", "text": body_text}]
                elif provider == "openai":
                    body["output"] = [{"content": [{"type": "output_text", "text": body_text}]}]
                else:
                    body["candidates"] = [{"finishReason": "STOP",
                                           "content": {"parts": [{"text": body_text}]}}]
            elif key in TRUNCATORS:
                body = wrap(provider, builder(quality), tokens_in, tokens_out)
                if provider == "anthropic":
                    body["stop_reason"] = "max_tokens"
                elif provider == "openai":
                    body["status"] = "incomplete"
                    body["incomplete_details"] = {"reason": "max_output_tokens"}
                else:
                    body["candidates"][0]["finishReason"] = "MAX_TOKENS"
            else:
                jitter = rng.uniform(-0.04, 0.04)
                body = wrap(provider, builder(max(0.0, min(1.0, quality + jitter))),
                            tokens_in, tokens_out)

            payload = {
                "synthetic": True,
                "note": "Hand-shaped fixture. NOT a measurement of this model.",
                "recorded_for": {"model": model, "task": task, "trial": 1},
                "status": 200,
                "body": body,
                "error": None,
                "wall_clock_ms": rng.randint(4000, 90000),
                "ttft_ms": rng.randint(400, 4000),
            }
            path = OUT / f"{model}__{task}__t1.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            written += 1
    print(f"wrote {written} synthetic cassettes to {OUT}")


if __name__ == "__main__":
    main()

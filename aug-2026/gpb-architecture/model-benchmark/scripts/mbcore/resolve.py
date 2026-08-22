"""Entity resolution and claim verification, applied to a whole response.

Wraps the evidence provider and produces the two numbers that make evidence
grounding objective:

  resolution_rate  — of the entities a model named, how many exist
  claim_verdicts   — of the relations it asserted, how many the graph confirms

The rule that keeps these honest: UNRESOLVED is reported separately from WRONG.
A model that names a real thing imprecisely, a model that invents a symbol, and
a resolver that failed are three different situations. Collapsing them makes
`EvidenceScore` unfalsifiable, because our own matcher's failures disappear into
the model's score.

FUZZY matches are capped for exactly this reason: a finding whose identity rests
on more than one fuzzy match is demoted to UNRESOLVED rather than being allowed
to accumulate credit from near-misses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .evidence.base import EvidenceProvider, MatchKind, Verdict


@dataclass
class ResolutionReport:
    referenced: int = 0
    exact: int = 0
    located: int = 0
    fuzzy: int = 0
    unresolved: int = 0
    per_finding: dict[str, list[str]] = field(default_factory=dict)
    unresolved_refs: list[str] = field(default_factory=list)
    demoted_findings: list[str] = field(default_factory=list)

    @property
    def resolution_rate(self) -> float:
        if not self.referenced:
            return 0.0
        return round((self.exact + self.located + self.fuzzy) / self.referenced, 4)

    def to_dict(self) -> dict:
        return {
            "referenced": self.referenced,
            "exact": self.exact,
            "located": self.located,
            "fuzzy": self.fuzzy,
            "unresolved": self.unresolved,
            "resolution_rate": self.resolution_rate,
            "unresolved_refs": self.unresolved_refs[:25],
            "demoted_findings": self.demoted_findings,
        }


@dataclass
class ClaimReport:
    asserted: int = 0
    verified_true: int = 0
    contradicted: int = 0
    unknown: int = 0
    source: str = "EMITTED"
    extractor_version: str | None = None
    details: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "asserted": self.asserted,
            "verified_true": self.verified_true,
            "contradicted": self.contradicted,
            "unknown": self.unknown,
            "source": self.source,
            "extractor_version": self.extractor_version,
        }


MAX_FUZZY_PER_FINDING = 1


def resolve_response(findings: list[dict[str, Any]],
                     provider: EvidenceProvider,
                     answers: list[dict[str, Any]] | None = None) -> ResolutionReport:
    """Resolve every entity the model named, on findings AND on answers."""
    rep = ResolutionReport()
    for f in list(findings) + list(answers or []):
        fid = f.get("id", "?")
        nodes: list[str] = []
        fuzzy_here = 0
        hint_file = None
        hint_lines = None
        ev = f.get("evidence") or []
        if ev and isinstance(ev[0], dict):
            hint_file = ev[0].get("file")
            hint_lines = ev[0].get("lines")

        for e in f.get("entities") or []:
            ref = e.get("ref") if isinstance(e, dict) else str(e)
            if not ref:
                continue
            rep.referenced += 1
            r = provider.resolve(ref, hint_file=hint_file, hint_lines=hint_lines)
            if r.kind is MatchKind.EXACT:
                rep.exact += 1
                nodes.append(r.node_id or ref)
            elif r.kind is MatchKind.LOCATED:
                rep.located += 1
                nodes.append(r.node_id or ref)
            elif r.kind is MatchKind.FUZZY:
                rep.fuzzy += 1
                fuzzy_here += 1
                nodes.append(r.node_id or ref)
            else:
                rep.unresolved += 1
                rep.unresolved_refs.append(ref)

        if fuzzy_here > MAX_FUZZY_PER_FINDING:
            # Identity resting on several near-misses is not identity. Move the
            # counts as well as the nodes: leaving them in `fuzzy` let a demoted
            # finding keep full evidence credit while being denied location
            # credit in matching — grounding and matching disagreeing about the
            # same finding.
            rep.fuzzy -= fuzzy_here
            rep.unresolved += fuzzy_here
            rep.demoted_findings.append(fid)
            nodes = []
        rep.per_finding[fid] = nodes
    return rep


def verify_claims(findings: list[dict[str, Any]], provider: EvidenceProvider,
                  source: str = "EMITTED",
                  extractor_version: str | None = None,
                  answers: list[dict[str, Any]] | None = None) -> ClaimReport:
    """Verify every relation the model asserted, on findings AND on answers.

    Question-style suites carry their checkable assertions on `answers`; skipping
    those would score the semantic suite as if the model had claimed nothing.
    """
    rep = ClaimReport(source=source, extractor_version=extractor_version)
    for f in list(findings) + list(answers or []):
        for rel in f.get("relations") or []:
            if not isinstance(rel, dict):
                continue
            rep.asserted += 1
            v = provider.verify(
                rel.get("subject", ""), rel.get("predicate", ""), rel.get("object", ""),
                modality=rel.get("modality"), negated=bool(rel.get("negated")),
            )
            if v is Verdict.TRUE:
                rep.verified_true += 1
            elif v is Verdict.FALSE:
                rep.contradicted += 1
            else:
                rep.unknown += 1
            rep.details.append({
                "finding": f.get("id"),
                "claim": f"{rel.get('subject')} -{rel.get('predicate')}-> {rel.get('object')}",
                "negated": bool(rel.get("negated")),
                "verdict": v.value,
            })
    return rep


def verify_oracle_relations(answers: list[dict[str, Any]],
                            oracle_relations: list[dict[str, Any]],
                            provider: EvidenceProvider) -> dict[str, Any]:
    """Score a semantic-suite answer against TRUE/FALSE oracle relations.

    Suites pair true and false relations over the same structure deliberately.
    Asserting the true ones measures recall; asserting the false ones measures
    hallucination. A suite with only true relations rewards a model that asserts
    everything.
    """
    asserted: set[tuple[str, str, str]] = set()
    for a in answers:
        for rel in a.get("relations") or []:
            if isinstance(rel, dict):
                asserted.add((
                    _n(rel.get("subject")), _n(rel.get("predicate")), _n(rel.get("object"))
                ))

    tp = fn = fp_on_false = tn = 0
    for orel in oracle_relations:
        key = (_n(orel.get("subject")), _n(orel.get("predicate")), _n(orel.get("object")))
        claimed = key in asserted
        if orel.get("truth"):
            tp += 1 if claimed else 0
            fn += 0 if claimed else 1
        else:
            fp_on_false += 1 if claimed else 0
            tn += 0 if claimed else 1

    total_true = tp + fn
    total_false = fp_on_false + tn
    return {
        "true_relations_recalled": tp,
        "true_relations_total": total_true,
        "false_relations_asserted": fp_on_false,
        "false_relations_total": total_false,
        "recall": round(tp / total_true, 4) if total_true else None,
        "hallucination_rate": round(fp_on_false / total_false, 4) if total_false else None,
    }


def _n(s: Any) -> str:
    return str(s or "").strip().lower().replace("#", ".").replace("::", ".")

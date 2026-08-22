"""Evidence provider SPI.

The code graph is the differentiator of this benchmark — it is what turns "did
the model sound right?" into "did the model say true things about this system?"
But the harness has to run before that integration exists, and a benchmark that
cannot run is not a benchmark.

Hence an interface with a bundled fallback. `local_graph` builds a lightweight
symbol and call graph straight from the corpus, so every suite runs standalone
today. Pointing `evidence.provider` at the platform is a one-line configuration
change, and the provider's version and hash are recorded in every manifest so a
result from the fallback is never confused with a result from the real thing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"      # provider cannot decide — never counted against the model


class MatchKind(str, Enum):
    EXACT = "EXACT"
    LOCATED = "LOCATED"
    FUZZY = "FUZZY"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class Resolution:
    kind: MatchKind
    node_id: str | None = None
    rung: str = ""            # which ladder rung matched — R0..R6
    candidates: list[str] = field(default_factory=list)
    score: float = 0.0

    @property
    def resolved(self) -> bool:
        return self.kind is not MatchKind.UNRESOLVED


@dataclass
class GraphVersion:
    provider: str
    version: str
    graph_hash: str
    node_count: int = 0
    edge_count: int = 0


class EvidenceProvider:
    """Implement this to plug the platform's code graph in."""

    name = "base"

    def resolve(self, ref: str, hint_file: str | None = None,
                hint_lines: str | None = None) -> Resolution:
        raise NotImplementedError

    def verify(self, subject: str, predicate: str, obj: str,
               modality: str | None = None, negated: bool = False) -> Verdict:
        """Verify one relation claim.

        Returning UNKNOWN is a first-class outcome and is NOT counted against the
        model. A provider that cannot decide has produced no evidence, and
        treating "we don't know" as "the model was wrong" quietly converts every
        gap in our own graph into an apparent model weakness.
        """
        raise NotImplementedError

    def neighbors(self, node_id: str, edge: str = "CALLS", depth: int = 1) -> list[str]:
        raise NotImplementedError

    def blast_radius(self, node_id: str) -> set[str]:
        raise NotImplementedError

    def version(self) -> GraphVersion:
        raise NotImplementedError

    # Query accounting, so the evidence budget can actually be enforced rather
    # than merely described.
    def query_count(self) -> int:
        return 0

    def reset_counter(self) -> None:
        pass


def get_provider(name: str, **kwargs: Any) -> EvidenceProvider:
    if name in ("local_graph", "local", "bundled"):
        from .local_graph import LocalGraphProvider
        return LocalGraphProvider(**kwargs)
    if name in ("codegraph", "platform"):
        raise NotImplementedError(
            "The platform code-graph provider is not wired up in this package. "
            "Implement EvidenceProvider against your graph API and register it "
            "here. Until then, `local_graph` runs every suite standalone — but "
            "label those results as fallback-graph results, because the whole "
            "uplift argument depends on the difference."
        )
    raise KeyError(f"unknown evidence provider '{name}'")

"""Bundled fallback evidence provider.

Builds a lightweight symbol and call graph from the corpus with regex-based
extraction. It is deliberately modest: enough to run every suite standalone, not
a replacement for a real semantic graph.

Two design choices matter for score integrity:

1. **The resolution ladder is generous about presentation and strict about
   identity.** A model should not lose points for writing `PaymentClient.charge`
   instead of `com.acme.payments.PaymentClient#charge(ChargeRequest)`. It should
   lose points for naming a symbol that does not exist. Those are different
   failures and the ladder keeps them apart.

2. **UNKNOWN is used freely.** This provider knows about calls, imports and file
   membership. Asked about something it cannot see — an async topic subscription,
   a datastore shared across bounded contexts — it says UNKNOWN rather than
   FALSE. Answering FALSE from ignorance converts a gap in our tooling into an
   apparent model hallucination, which is the fastest way to make a benchmark
   lie.

A graph loaded from `graph.json` (if the corpus ships one) takes precedence over
regex extraction, so a suite can supply richer ground truth without needing the
platform.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from ..util import digest
from .base import EvidenceProvider, GraphVersion, MatchKind, Resolution, Verdict

SOURCE_SUFFIXES = {".java", ".py", ".ts", ".tsx", ".js", ".go", ".cs", ".kt", ".rb", ".scala"}

DECL_PATTERNS = [
    # Java / C# / Kotlin / Scala style
    re.compile(r"(?m)^\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:final\s+)?"
               r"(?:class|interface|record|enum)\s+(\w+)"),
    re.compile(r"(?m)^\s*(?:public|private|protected|internal)\s+(?:static\s+)?(?:final\s+)?"
               r"[\w<>\[\],\s.]+?\s+(\w+)\s*\("),
    # Python
    re.compile(r"(?m)^\s*(?:async\s+)?def\s+(\w+)\s*\("),
    re.compile(r"(?m)^\s*class\s+(\w+)"),
    # TS / JS
    re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\("),
    re.compile(r"(?m)^\s*(?:export\s+)?class\s+(\w+)"),
    # Go
    re.compile(r"(?m)^\s*func\s+(?:\([^)]*\)\s*)?(\w+)\s*\("),
]

CALL_PATTERN = re.compile(r"\b([A-Za-z_][\w]*)\s*\.\s*([A-Za-z_][\w]*)\s*\(")
BARE_CALL = re.compile(r"\b([A-Za-z_][\w]*)\s*\(")

# Predicates this provider can actually decide. Anything else returns UNKNOWN.
DECIDABLE = {"CALLS", "DEPENDS_ON", "DEFINED_IN", "CONTAINS"}


class LocalGraphProvider(EvidenceProvider):
    name = "local_graph"

    def __init__(self, corpus_root: str = "fixtures/sample-repo", version: str = "0.1.0"):
        from ..util import SKILL_ROOT
        root = Path(corpus_root)
        if not root.is_absolute() and not root.exists():
            root = SKILL_ROOT / corpus_root
        self.root = root
        self._version = version
        self._queries = 0

        self.symbols: dict[str, dict] = {}       # node_id -> {name, kind, file, line}
        self.by_simple: dict[str, list[str]] = {}
        self.edges: set[tuple[str, str, str]] = set()   # (subject, predicate, object)
        self.files: dict[str, list[str]] = {}    # file -> node ids

        prebuilt = self.root / "graph.json" if self.root.exists() else None
        if prebuilt and prebuilt.exists():
            self._load_prebuilt(prebuilt)
        elif self.root.exists():
            self._build_from_source()

    # ------------------------------------------------------------- building
    def _add_symbol(self, name: str, kind: str, file: str, line: int, owner: str | None = None):
        node_id = f"{owner}.{name}" if owner else name
        self.symbols[node_id] = {"name": name, "kind": kind, "file": file, "line": line,
                                 "owner": owner}
        self.by_simple.setdefault(name, []).append(node_id)
        self.files.setdefault(file, []).append(node_id)

    def _load_prebuilt(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        for node in data.get("nodes", []):
            nid = node["id"]
            self.symbols[nid] = node
            simple = node.get("name") or nid.split(".")[-1]
            self.by_simple.setdefault(simple, []).append(nid)
            if node.get("file"):
                self.files.setdefault(node["file"], []).append(nid)
        for e in data.get("edges", []):
            self.edges.add((e["subject"], e["predicate"], e["object"]))

    def _build_from_source(self):
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
                continue
            rel = str(path.relative_to(self.root))
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            current_type = None
            for lineno, line in enumerate(text.splitlines(), 1):
                for pat in DECL_PATTERNS:
                    m = pat.match(line)
                    if not m:
                        continue
                    name = m.group(1)
                    is_type = bool(re.search(r"\b(class|interface|record|enum)\b", line))
                    if is_type:
                        current_type = name
                        self._add_symbol(name, "class", rel, lineno)
                    else:
                        self._add_symbol(name, "method", rel, lineno, owner=current_type)
                    break
            # call edges, attributed to the enclosing type when we know it
            owner = None
            for lineno, line in enumerate(text.splitlines(), 1):
                tm = re.search(r"\b(?:class|interface|record|enum)\s+(\w+)", line)
                if tm:
                    owner = tm.group(1)
                for recv, meth in CALL_PATTERN.findall(line):
                    subj = owner or rel
                    self.edges.add((subj, "CALLS", f"{recv}.{meth}"))
                    self.edges.add((subj, "DEPENDS_ON", recv))

    # ------------------------------------------------------------- resolving
    def resolve(self, ref: str, hint_file: str | None = None,
                hint_lines: str | None = None) -> Resolution:
        self._queries += 1
        if not ref:
            return Resolution(MatchKind.UNRESOLVED, rung="R-empty")

        # R0 — exact node id
        if ref in self.symbols:
            return Resolution(MatchKind.EXACT, ref, "R0", score=1.0)

        # R1 — normalized: strip package prefixes, unify separators and signatures
        norm = _normalize(ref)
        for nid in self.symbols:
            if _normalize(nid) == norm:
                return Resolution(MatchKind.EXACT, nid, "R1", score=1.0)

        # R2 — simple name plus enclosing type, unique
        if "." in norm or "#" in norm:
            parts = re.split(r"[.#]", norm)
            if len(parts) >= 2:
                owner, simple = parts[-2], parts[-1]
                cands = [n for n in self.by_simple.get(simple, [])
                         if (self.symbols[n].get("owner") or "").lower() == owner.lower()]
                if len(cands) == 1:
                    return Resolution(MatchKind.EXACT, cands[0], "R2", score=1.0)

        # R3 — simple name unique in corpus
        simple = re.split(r"[.#(]", norm)[-1] or norm
        cands = self.by_simple.get(simple) or []
        if len(cands) == 1:
            return Resolution(MatchKind.EXACT, cands[0], "R3", score=0.95)

        # R4 — ambiguous simple name, disambiguated by the finding's evidence file
        if len(cands) > 1 and hint_file:
            in_file = [c for c in cands if _same_file(self.symbols[c].get("file"), hint_file)]
            if len(in_file) == 1:
                return Resolution(MatchKind.EXACT, in_file[0], "R4", candidates=cands, score=0.9)

        # R5 — evidence file plus line range intersects exactly one symbol
        if hint_file and hint_lines:
            lo, hi = _line_range(hint_lines)
            hits = [
                nid for nid, s in self.symbols.items()
                if _same_file(s.get("file"), hint_file) and lo <= int(s.get("line", 0)) <= hi
            ]
            if len(hits) == 1:
                return Resolution(MatchKind.LOCATED, hits[0], "R5", score=0.8)

        # R6 — fuzzy, single strong candidate only
        best, best_score = None, 0.0
        for nid in self.symbols:
            s = SequenceMatcher(None, norm, _normalize(nid)).ratio()
            if s > best_score:
                best, best_score = nid, s
        if best and best_score >= 0.88:
            return Resolution(MatchKind.FUZZY, best, "R6", candidates=[best], score=best_score)

        return Resolution(MatchKind.UNRESOLVED, None, "R-none",
                          candidates=cands[:5], score=best_score)

    # ------------------------------------------------------------- verifying
    def verify(self, subject: str, predicate: str, obj: str,
               modality: str | None = None, negated: bool = False) -> Verdict:
        self._queries += 1
        pred = (predicate or "").upper()
        if pred not in DECIDABLE:
            # Say so rather than guessing. See the module docstring.
            return Verdict.UNKNOWN

        s = self.resolve(subject)
        o = self.resolve(obj)
        if not s.resolved or not o.resolved:
            return Verdict.UNKNOWN

        subj_aliases = self._aliases(s.node_id or subject)
        present = any(
            p == pred
            and _normalize(a) in subj_aliases
            and _endpoint_matches(b, o.node_id or obj)
            for a, p, b in self.edges
        )
        if negated:
            # A negated claim ("no timeout is configured") is TRUE when the
            # relation is absent — but only when we would have been able to see
            # it. Absence of evidence is treated as evidence of absence ONLY for
            # predicates this provider can actually decide.
            return Verdict.TRUE if not present else Verdict.FALSE
        return Verdict.TRUE if present else Verdict.FALSE

    def _aliases(self, node_id: str) -> set[str]:
        """Names an edge may legitimately use for this node.

        The regex extractor attributes call edges to the enclosing type, while a
        model naturally names the calling METHOD. Both refer to the same fact, so
        the enclosing type and the bare simple name are accepted as the subject.
        """
        out = {_normalize(node_id)}
        info = self.symbols.get(node_id) or {}
        owner = info.get("owner")
        if owner:
            out.add(_normalize(owner))
        if info.get("file"):
            out.add(_normalize(info["file"]))
        head = _normalize(node_id).split(".")[0]
        if head:
            out.add(head)
        return out

    def neighbors(self, node_id: str, edge: str = "CALLS", depth: int = 1) -> list[str]:
        self._queries += 1
        frontier = {node_id}
        seen: set[str] = set()
        for _ in range(max(1, depth)):
            nxt: set[str] = set()
            for a, p, b in self.edges:
                if p == edge.upper() and a in frontier and b not in seen:
                    nxt.add(b)
            seen |= nxt
            frontier = nxt
            if not frontier:
                break
        return sorted(seen)

    def blast_radius(self, node_id: str) -> set[str]:
        self._queries += 1
        reached: set[str] = set()
        frontier = {node_id}
        for _ in range(6):   # bounded: an unbounded walk on a dense graph is a hang
            nxt = {a for a, p, b in self.edges if b in frontier and a not in reached}
            if not nxt:
                break
            reached |= nxt
            frontier = nxt
        return reached

    # -------------------------------------------------------------- metadata
    def version(self) -> GraphVersion:
        h = digest({
            "nodes": sorted(self.symbols),
            "edges": sorted(f"{a}|{p}|{b}" for a, p, b in self.edges),
        })
        return GraphVersion(provider=self.name, version=self._version, graph_hash=h,
                            node_count=len(self.symbols), edge_count=len(self.edges))

    def query_count(self) -> int:
        return self._queries

    def reset_counter(self) -> None:
        self._queries = 0


# --------------------------------------------------------------------------

def _normalize(ref: str) -> str:
    r = re.sub(r"\(.*?\)", "", ref or "")          # drop signatures
    r = r.replace("#", ".").replace("::", ".").replace("/", ".")
    r = re.sub(r"\s+", "", r)
    return r.lower().strip(".")


def _same_file(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return Path(a).name.lower() == Path(b).name.lower()


def _line_range(spec: str) -> tuple[int, int]:
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        try:
            return int(lo), int(hi)
        except ValueError:
            return 0, 0
    try:
        n = int(spec)
        return n, n
    except ValueError:
        return 0, 0


def _endpoint_matches(edge_target: str, resolved: str) -> bool:
    a, b = _normalize(edge_target), _normalize(resolved)
    return a == b or a.endswith("." + b) or b.endswith("." + a)

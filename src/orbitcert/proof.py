"""The proof format: what a certified enumeration writes down, and what it omits.

A proof is a stream of line-oriented records replaying a depth-first traversal of
the orderly-generation tree.  It is designed around a single question: *what is
the smallest thing a sceptic must be handed in order to be convinced?*

What the proof must contain
---------------------------
Exactly one thing: a permutation witness for every candidate the generator threw
away on canonicity grounds.  Deciding "is this graph the lexicographic minimum of
its isomorphism class?" is the only step in the whole enumeration that is
expensive and non-obvious, so it is the only step whose answer must be justified
rather than recomputed.

What the proof deliberately omits
---------------------------------
Everything the checker can cheaply redo itself:

* candidates discarded for violating the hereditary constraint — the checker
  re-tests the constraint directly, in time linear in the forbidden-subgraph
  size, and does not need to be told;
* the tree structure — it follows from the accepted children;
* the codes of the nodes — they follow from the root and the accepted
  neighbourhood masks.

Leaving these out is not a size optimisation, it is a trust argument: every byte
in the proof is a claim the checker must *believe after verifying*, so the fewer
kinds of claim there are, the smaller the trusted base.  Here there is one kind.

The asymmetry that makes this work
----------------------------------
Verifying a permutation witness costs ``O(k^2)``.  Finding one costs, in the
worst case, a search over ``k!``.  So checking a proof is asymptotically cheaper
than producing it — the checker never searches, it only applies permutations and
compares.  This is the same bargain SAT solvers strike with DRAT, transplanted
to isomorph-free generation.

Grammar
-------
::

    orbitcert-proof 1                 # magic + format version
    problem <name> <key=value>...     # the claim being certified
    order <n>                         # target number of vertices
    root <mask>                       # always 0; the one-vertex graph
    D <mask>                          # descend into accepted child <mask>
    X <mask> <p0> <p1> ... <p_k>      # child <mask> pruned: non-canonical, witness perm
    U                                 # ascend (finished the current node)
    empty <depth>                     # assertion: this node had no accepted children
    qed <nodes> <witnesses>           # end of proof + tallies for cross-checking

``mask`` is a hexadecimal bitmask over the vertices of the *current* node,
naming the neighbourhood of the vertex being appended.  The permutation in an
``X`` record is written as ``p[0] p[1] ... p[k]`` where ``p[u]`` is the new label
of vertex ``u``, and it applies to the child graph (``k+1`` vertices).
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Iterator, Optional, Sequence, TextIO

MAGIC = "orbitcert-proof"
VERSION = 1


@dataclass
class ProofStats:
    """Tallies emitted in the ``qed`` line so a checker can cross-check coverage."""

    nodes: int = 0
    witnesses: int = 0
    property_rejects: int = 0
    accepted: int = 0
    max_depth: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "nodes": self.nodes,
            "witnesses": self.witnesses,
            "property_rejects": self.property_rejects,
            "accepted": self.accepted,
            "max_depth": self.max_depth,
        }


class ProofWriter:
    """Streams proof records to a text sink.

    Nothing is buffered beyond the sink's own buffering, so a proof may be many
    times larger than memory.
    """

    def __init__(self, sink: TextIO, problem: str, order: int, **params: object) -> None:
        self._sink = sink
        self.stats = ProofStats()
        kv = " ".join(f"{k}={v}" for k, v in sorted(params.items()))
        sink.write(f"{MAGIC} {VERSION}\n")
        sink.write(f"problem {problem}{' ' + kv if kv else ''}\n")
        sink.write(f"order {order}\n")
        sink.write("root 0\n")

    def descend(self, mask: int) -> None:
        self._sink.write(f"D {mask:x}\n")
        self.stats.accepted += 1

    def ascend(self) -> None:
        self._sink.write("U\n")

    def witness(self, mask: int, perm: Sequence[int]) -> None:
        self._sink.write(f"X {mask:x} " + " ".join(map(str, perm)) + "\n")
        self.stats.witnesses += 1

    def note_property_reject(self) -> None:
        """Counted but not written: the checker re-derives these itself."""
        self.stats.property_rejects += 1

    def note_node(self, depth: int) -> None:
        self.stats.nodes += 1
        self.stats.max_depth = max(self.stats.max_depth, depth)

    def empty(self, depth: int) -> None:
        self._sink.write(f"empty {depth}\n")

    def qed(self) -> None:
        s = self.stats
        self._sink.write(f"qed {s.nodes} {s.witnesses}\n")
        self._sink.flush()


@dataclass
class Record:
    kind: str
    mask: int = 0
    perm: tuple[int, ...] = ()
    depth: int = 0
    fields: dict[str, str] = field(default_factory=dict)


class ProofSyntaxError(ValueError):
    """Raised when a proof stream is malformed."""


def parse(stream: TextIO) -> Iterator[Record]:
    """Parse a proof stream lazily into :class:`Record` objects.

    Header records are yielded first (``header``, ``problem``, ``order``,
    ``root``), then the traversal records in order.
    """
    first = stream.readline()
    if not first:
        raise ProofSyntaxError("empty proof stream")
    parts = first.split()
    if len(parts) != 2 or parts[0] != MAGIC:
        raise ProofSyntaxError(f"bad magic line: {first!r}")
    if parts[1] != str(VERSION):
        raise ProofSyntaxError(f"unsupported proof version {parts[1]!r}")
    yield Record("header", fields={"version": parts[1]})

    for lineno, line in enumerate(stream, start=2):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tok = line.split()
        head = tok[0]
        try:
            if head == "problem":
                fields = {}
                for kv in tok[2:]:
                    k, _, v = kv.partition("=")
                    fields[k] = v
                fields["name"] = tok[1]
                yield Record("problem", fields=fields)
            elif head == "order":
                yield Record("order", depth=int(tok[1]))
            elif head == "root":
                yield Record("root", mask=int(tok[1], 16))
            elif head == "D":
                yield Record("descend", mask=int(tok[1], 16))
            elif head == "U":
                yield Record("ascend")
            elif head == "X":
                yield Record("witness", mask=int(tok[1], 16),
                             perm=tuple(int(x) for x in tok[2:]))
            elif head == "empty":
                yield Record("empty", depth=int(tok[1]))
            elif head == "qed":
                yield Record("qed", fields={"nodes": tok[1], "witnesses": tok[2]})
            else:
                raise ProofSyntaxError(f"line {lineno}: unknown record {head!r}")
        except ProofSyntaxError:
            raise
        except (IndexError, ValueError) as exc:
            raise ProofSyntaxError(f"line {lineno}: malformed {head!r} record: {exc}") from exc


def parse_string(text: str) -> list[Record]:
    return list(parse(io.StringIO(text)))

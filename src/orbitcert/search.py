"""Orderly generation with proof emission.

The enumeration
---------------
Start from the one-vertex graph and repeatedly append a vertex.  A graph is kept
only if it is the lexicographic minimum of its isomorphism class under the
prefix-structured code of :mod:`orbitcert.graph`, and only if it still satisfies
the hereditary property.  At depth ``n`` the surviving graphs are exactly one
representative of every isomorphism class of ``n``-vertex graphs with the
property.

Why the pruning is safe (the completeness theorem)
--------------------------------------------------
Two facts, both proved in ``docs/theory.md`` and both checked exhaustively by
``tests/test_theory.py``:

**Prefix-heredity.**  If ``G`` on ``[k]`` is lexicographically minimal in its
isomorphism class, so is ``G`` induced on ``[k-1]``.  *Proof.*  If some ``sigma``
made the induced subgraph smaller, extending ``sigma`` by fixing vertex ``k-1``
would make the first ``(k-1)(k-2)/2`` bits of ``code(G)`` strictly smaller; since
those bits are a prefix of the whole code, the whole code would be smaller too,
contradicting minimality of ``G``.  This is where the column-major encoding earns
its keep — in row-major order the prefix relationship does not exist and the
argument collapses.

**Completeness.**  Let ``G`` be the lexicographic minimum of any isomorphism
class of ``n``-vertex graphs with the hereditary property.  By prefix-heredity
applied repeatedly, every induced prefix ``G[[1]], G[[2]], ..., G[[n]] = G`` is
also lexicographically minimal, and by heredity every one of them satisfies the
property.  So that chain is a root-to-leaf path in the pruned tree, and ``G`` is
reached.  Nothing is missed.

The consequence that matters: **if the search reaches depth ``n`` and finds
nothing, no graph on ``n`` vertices has the property.**  That is a nonexistence
theorem, and it is what the proof stream certifies.

One-sided error
---------------
The canonicity test may be given a ``node_limit``, after which it gives up and
reports "no witness found".  That makes the generator keep a graph it might have
pruned — the search does more work and the output may contain isomorphic
duplicates, but nothing is ever lost.  Completeness therefore does not depend on
the canonicity search being correct, only on the witnesses it *does* produce
being valid, and those are checked.  A subtly buggy canonicity engine cannot
produce a wrong nonexistence result here; it can only produce a slow one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, Optional, TextIO

from .canon import find_smaller
from .graph import Graph, code, empty, extend
from .problems import HereditaryProperty
from .proof import ProofWriter


@dataclass
class SearchResult:
    """Outcome of an enumeration."""

    order: int
    counts: list[int]
    """``counts[k]`` = number of kept graphs on ``k+1`` vertices."""
    witnesses: list[Graph]
    """Graphs found at the target order (empty for a nonexistence result)."""
    nodes: int
    canonicity_witnesses: int
    property_rejects: int

    @property
    def nonexistence(self) -> bool:
        return not self.witnesses

    def summary(self) -> str:
        head = (f"order {self.order}: "
                f"{'NO graph exists' if self.nonexistence else f'{len(self.witnesses)} graph(s) found'}")
        per_level = ", ".join(f"n={i + 1}:{c}" for i, c in enumerate(self.counts))
        return (f"{head}\n  per level: {per_level}\n"
                f"  nodes={self.nodes} witnesses={self.canonicity_witnesses} "
                f"property-rejects={self.property_rejects}")


def enumerate_graphs(
    prop: HereditaryProperty,
    order: int,
    *,
    proof: Optional[TextIO] = None,
    node_limit: int = 0,
    collect: bool = True,
    on_level: Optional[Callable[[int, int], None]] = None,
) -> SearchResult:
    """Enumerate all graphs up to ``order`` vertices satisfying ``prop``.

    When ``proof`` is given, a certificate is streamed to it as the search runs.
    The certificate justifies the *completeness* of the search — that no graph on
    ``order`` vertices was missed — which is exactly what a nonexistence claim
    needs.  See :mod:`orbitcert.proof` for the format and its rationale.
    """
    if order < 1:
        raise ValueError("order must be at least 1")

    writer = None
    if proof is not None:
        writer = ProofWriter(proof, prop.name, order, **prop.params())

    counts = [0] * order
    found: list[Graph] = []
    stats = {"nodes": 0, "witnesses": 0, "prejects": 0}

    def visit(g: Graph) -> None:
        k = len(g)
        counts[k - 1] += 1
        stats["nodes"] += 1
        if writer is not None:
            writer.note_node(k)
        if k == order:
            if collect:
                found.append(g)
            return

        accepted: list[tuple[int, Graph]] = []
        pending: list[tuple[int, tuple[int, ...]]] = []
        for mask in range(1 << k):
            if not prop.admits_extension(g, mask):
                # The checker re-derives this itself; nothing goes in the proof.
                stats["prejects"] += 1
                if writer is not None:
                    writer.note_property_reject()
                continue
            child = extend(g, mask)
            perm = find_smaller(child, node_limit=node_limit)
            if perm is not None:
                stats["witnesses"] += 1
                pending.append((mask, perm))
            else:
                accepted.append((mask, child))

        if writer is not None:
            # Witnesses first, then descents: the checker can then account for
            # every candidate mask in one left-to-right pass over the node.
            for mask, perm in pending:
                writer.witness(mask, perm)
            if not accepted:
                writer.empty(k)

        for mask, child in accepted:
            if writer is not None:
                writer.descend(mask)
            visit(child)
            if writer is not None:
                writer.ascend()

        if on_level is not None and k == 1:
            on_level(k, counts[k - 1])

    visit(empty(1))

    if writer is not None:
        writer.qed()

    return SearchResult(
        order=order,
        counts=counts,
        witnesses=found,
        nodes=stats["nodes"],
        canonicity_witnesses=stats["witnesses"],
        property_rejects=stats["prejects"],
    )


def iter_level(prop: HereditaryProperty, order: int, *, node_limit: int = 0) -> Iterator[Graph]:
    """Yield one representative of every isomorphism class at exactly ``order`` vertices.

    Breadth-first, so memory is proportional to the widest level rather than the
    whole tree.  Useful for counting; :func:`enumerate_graphs` is the one that
    produces certificates.
    """
    level: list[Graph] = [empty(1)]
    for k in range(1, order):
        nxt: list[Graph] = []
        for g in level:
            for mask in range(1 << k):
                if not prop.admits_extension(g, mask):
                    continue
                child = extend(g, mask)
                if find_smaller(child, node_limit=node_limit) is None:
                    nxt.append(child)
        level = nxt
        if not level:
            return
    yield from level

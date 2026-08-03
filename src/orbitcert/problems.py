"""Hereditary graph properties that orderly generation can enumerate under.

A property is *hereditary* when it is inherited by induced subgraphs.  That is
the only condition orderly generation needs, and the reason is worth stating
because it is the whole justification for pruning the search tree at all: if the
property can only be lost by adding vertices, never by removing them, then every
graph satisfying it sits at the end of a chain of ever-smaller graphs that all
satisfy it — so growing one vertex at a time cannot miss anything.

Each property exposes an *incremental* test.  When a vertex is appended, the only
new forbidden configurations are those containing the new vertex, so the test
never re-examines the old graph.  This is what keeps the checker linear in the
number of candidates rather than quadratic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .graph import Graph

__all__ = ["HereditaryProperty", "RamseyProperty", "TriangleFree", "CliqueFree", "GirthAtLeast"]


def _has_clique_in(g: Graph, subset: int, size: int) -> bool:
    """True when the subgraph induced on the bitmask ``subset`` contains a ``K_size``."""
    if size <= 0:
        return True
    if size == 1:
        return subset != 0

    def grow(cand: int, need: int) -> bool:
        if need == 0:
            return True
        # Not enough vertices left to finish the clique.
        if bin(cand).count("1") < need:
            return False
        rest = cand
        while rest:
            v = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            # Only vertices after v, and adjacent to v, can extend this clique.
            if grow(cand & g[v] & ~((1 << (v + 1)) - 1), need - 1):
                return True
            # v is exhausted; drop it so later branches do not revisit it.
            cand &= ~(1 << v)
            if bin(cand).count("1") < need:
                return False
        return False

    return grow(subset, size)


def _has_independent_set_in(g: Graph, subset: int, size: int) -> bool:
    """True when the subgraph induced on ``subset`` contains ``size`` pairwise non-adjacent vertices."""
    if size <= 0:
        return True
    if size == 1:
        return subset != 0

    def grow(cand: int, need: int) -> bool:
        if need == 0:
            return True
        if bin(cand).count("1") < need:
            return False
        rest = cand
        while rest:
            v = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            if grow(cand & ~g[v] & ~((1 << (v + 1)) - 1), need - 1):
                return True
            cand &= ~(1 << v)
            if bin(cand).count("1") < need:
                return False
        return False

    return grow(subset, size)


class HereditaryProperty(ABC):
    """A property closed under taking induced subgraphs."""

    name: str = "property"

    @abstractmethod
    def params(self) -> dict[str, object]:
        """Parameters recorded in the proof header."""

    @abstractmethod
    def admits_extension(self, g: Graph, mask: int) -> bool:
        """True when appending a vertex with neighbourhood ``mask`` keeps the property.

        ``g`` is assumed to satisfy the property already, so only configurations
        involving the new vertex need testing.
        """

    def holds(self, g: Graph) -> bool:
        """Non-incremental test, used by tests to cross-check the fast path."""
        cur: Graph = ()
        for k in range(len(g)):
            mask = g[k] & ((1 << k) - 1)
            if not self.admits_extension(cur, mask):
                return False
            from .graph import extend
            cur = extend(cur, mask)
        return True


class RamseyProperty(HereditaryProperty):
    """(s, t)-Ramsey graphs: no clique of size ``s``, no independent set of size ``t``.

    A graph on ``n`` vertices with this property witnesses ``R(s, t) > n``.  If no
    such graph exists on ``n`` vertices, then ``R(s, t) <= n``.  Both halves are
    hereditary — deleting a vertex can neither create a clique nor create an
    independent set — so the class is exactly what orderly generation wants.
    """

    name = "ramsey"

    def __init__(self, s: int, t: int) -> None:
        if s < 2 or t < 2:
            raise ValueError("Ramsey parameters must satisfy s, t >= 2")
        self.s = s
        self.t = t

    def params(self) -> dict[str, object]:
        return {"s": self.s, "t": self.t}

    def admits_extension(self, g: Graph, mask: int) -> bool:
        k = len(g)
        # A new K_s must use the new vertex, so it needs a K_{s-1} in its neighbourhood.
        if _has_clique_in(g, mask, self.s - 1):
            return False
        # A new independent t-set must use the new vertex, so it needs an
        # independent (t-1)-set among the vertices it is *not* joined to.
        non = ~mask & ((1 << k) - 1)
        if _has_independent_set_in(g, non, self.t - 1):
            return False
        return True

    def __repr__(self) -> str:
        return f"RamseyProperty(s={self.s}, t={self.t})"


class CliqueFree(HereditaryProperty):
    """Graphs with no clique of size ``s``."""

    name = "clique-free"

    def __init__(self, s: int) -> None:
        if s < 2:
            raise ValueError("s must be at least 2")
        self.s = s

    def params(self) -> dict[str, object]:
        return {"s": self.s}

    def admits_extension(self, g: Graph, mask: int) -> bool:
        return not _has_clique_in(g, mask, self.s - 1)


class TriangleFree(CliqueFree):
    """Graphs with no triangle."""

    name = "triangle-free"

    def __init__(self) -> None:
        super().__init__(3)

    def params(self) -> dict[str, object]:
        return {}


class GirthAtLeast(HereditaryProperty):
    """Graphs whose shortest cycle has length at least ``g`` (acyclic counts)."""

    name = "girth"

    def __init__(self, girth: int) -> None:
        if girth < 3:
            raise ValueError("girth must be at least 3")
        self.girth = girth

    def params(self) -> dict[str, object]:
        return {"girth": self.girth}

    def admits_extension(self, g: Graph, mask: int) -> bool:
        k = len(g)
        if k == 0:
            return True
        nbrs = [v for v in range(k) if mask >> v & 1]
        if len(nbrs) < 2:
            return True
        # A new cycle through the appended vertex has length 2 + d(u, v) for some
        # pair of its neighbours, so the girth condition is a distance condition.
        need = self.girth - 2
        for i, u in enumerate(nbrs):
            # Breadth-first search from u, bounded at depth `need - 1`.
            seen = 1 << u
            frontier = 1 << u
            for dist in range(1, need):
                nxt = 0
                rest = frontier
                while rest:
                    x = (rest & -rest).bit_length() - 1
                    rest &= rest - 1
                    nxt |= g[x]
                nxt &= ~seen & ((1 << k) - 1)
                if nxt == 0:
                    break
                for v in nbrs[i + 1:]:
                    if nxt >> v & 1:
                        return False
                seen |= nxt
                frontier = nxt
        return True

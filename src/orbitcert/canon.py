"""Canonicity testing by branch-and-bound, with witness extraction.

The search asks one question: *is there a relabelling of ``G`` whose code is
lexicographically smaller than ``code(G)``?*  If yes it returns the permutation
that proves it; if no, ``G`` is by definition the lexicographic minimum of its
isomorphism class, i.e. canonical.

Why the answer is cheap to *disprove* but expensive to *prove*
--------------------------------------------------------------
Returning a witness is a one-line claim that anyone can check in ``O(k^2)``:
apply the permutation, compare the codes.  Proving that *no* permutation works
is a statement about all ``k!`` of them.  :mod:`orbitcert.search` is built so
that only the cheap direction ever has to be trusted — see the module docstring
there.  This module still needs both directions, because the generator uses the
expensive direction to decide *whether* to prune; but a bug in the expensive
direction can only make the generator prune less, never more.

The search
----------
A relabelling is chosen as a sequence ``v_0, v_1, ..., v_{k-1}`` of the original
vertices, where ``v_i`` receives the new label ``i``.  Column ``j`` of the
resulting code is then

    ( adj(v_0, v_j), adj(v_1, v_j), ..., adj(v_{j-1}, v_j) )

so after choosing the prefix ``v_0..v_j`` the code's first ``j(j+1)/2`` bits are
fully determined.  That makes an incremental lexicographic comparison against
the target possible, and it drives the two pruning rules:

* the moment the partial code falls strictly *below* the target, every
  completion is below it too, so we can stop and return a witness immediately;
* the moment the partial code rises strictly *above* the target, no completion
  can help, so the branch dies.

Only branches that have matched the target exactly so far stay alive, and there
are usually very few of those — they correspond to partial automorphisms.
"""

from __future__ import annotations

from typing import Optional, Sequence

from .graph import Graph, code, relabel

__all__ = ["find_smaller", "is_canonical", "canonical_form", "automorphisms", "verify_witness"]


def _target_columns(g: Graph) -> list[tuple[int, ...]]:
    """Split ``code(g)`` into its columns, as the search consumes it column-wise."""
    return [tuple(g[i] >> j & 1 for i in range(j)) for j in range(1, len(g))]


def find_smaller(g: Graph, *, node_limit: int = 0) -> Optional[tuple[int, ...]]:
    """Return a permutation ``p`` with ``code(relabel(g, p)) < code(g)``, else ``None``.

    ``None`` means ``g`` is canonical (lexicographically minimal in its class).

    ``node_limit`` optionally caps the number of search nodes.  On exhausting the
    cap the function returns ``None`` — i.e. it reports "found no witness", which
    is the *conservative* answer: the caller will decline to prune.  Soundness of
    the enumeration never depends on this search being complete.
    """
    k = len(g)
    if k <= 1:
        return None

    target = _target_columns(g)
    # placement[v] = new label of original vertex v, or -1 if unplaced
    placement = [-1] * k
    chosen: list[int] = []
    nodes = 0

    def search(depth: int) -> Optional[list[int]]:
        """Extend the prefix at `depth`, given every earlier column tied the target."""
        nonlocal nodes
        if depth == k:
            return None  # a full tie: this is an automorphism, not a smaller code
        remaining = [v for v in range(k) if placement[v] == -1]

        # Score each candidate for position `depth` by the column it would create.
        scored: list[tuple[tuple[int, ...], int]] = []
        for v in remaining:
            col = tuple(g[chosen[i]] >> v & 1 for i in range(depth))
            scored.append((col, v))
        scored.sort()

        want = target[depth - 1] if depth >= 1 else ()
        for col, v in scored:
            nodes += 1
            if node_limit and nodes > node_limit:
                return None
            if depth >= 1:
                if col > want:
                    # Columns are sorted ascending, so every later candidate is
                    # also too large. Nothing in this branch can tie or beat.
                    break
                if col < want:
                    # Strictly smaller at the first differing position: any
                    # completion of this prefix beats the target outright.
                    placement[v] = depth
                    chosen.append(v)
                    rest = [u for u in range(k) if placement[u] == -1]
                    for i, u in enumerate(rest):
                        placement[u] = depth + 1 + i
                    result = placement[:]
                    for u in rest:
                        placement[u] = -1
                    chosen.pop()
                    placement[v] = -1
                    return result
            # col == want: still tied, recurse.
            placement[v] = depth
            chosen.append(v)
            found = search(depth + 1)
            chosen.pop()
            placement[v] = -1
            if found is not None:
                return found
        return None

    # Position 0 creates no column, so every vertex is a legitimate start.
    for v0 in range(k):
        placement[v0] = 0
        chosen.append(v0)
        found = search(1)
        chosen.pop()
        placement[v0] = -1
        if found is not None:
            return tuple(found)
        if node_limit and nodes > node_limit:
            return None
    return None


def is_canonical(g: Graph, *, node_limit: int = 0) -> bool:
    """True when ``g`` is the lexicographic minimum of its isomorphism class.

    With a ``node_limit`` in force this may return ``True`` for a non-canonical
    graph (the search gave up).  That direction of error is safe everywhere in
    this package: it costs work, not correctness.
    """
    return find_smaller(g, node_limit=node_limit) is None


def canonical_form(g: Graph) -> Graph:
    """The canonical (lexicographically minimal) representative of ``g``'s class."""
    cur = g
    while True:
        p = find_smaller(cur)
        if p is None:
            return cur
        cur = relabel(cur, p)


def automorphisms(g: Graph) -> list[tuple[int, ...]]:
    """Every automorphism of ``g``, as permutations. Exponential; for tests only."""
    k = len(g)
    target = _target_columns(g)
    placement = [-1] * k
    chosen: list[int] = []
    out: list[tuple[int, ...]] = []

    def search(depth: int) -> None:
        if depth == k:
            out.append(tuple(placement))
            return
        for v in range(k):
            if placement[v] != -1:
                continue
            col = tuple(g[chosen[i]] >> v & 1 for i in range(depth))
            if depth >= 1 and col != target[depth - 1]:
                continue
            placement[v] = depth
            chosen.append(v)
            search(depth + 1)
            chosen.pop()
            placement[v] = -1

    search(0)
    return out


def verify_witness(g: Graph, perm: Sequence[int]) -> bool:
    """Independently check that ``perm`` really proves ``g`` non-canonical.

    This is the *entire* trusted computation behind a pruning step, and it is
    deliberately written to be obvious rather than fast: permute, compare.
    """
    k = len(g)
    if sorted(perm) != list(range(k)):
        return False
    return code(relabel(g, perm)) < code(g)

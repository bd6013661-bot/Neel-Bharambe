"""Shared test utilities: brute-force oracles and generators.

Everything here is deliberately naive.  These are the reference implementations
the fast code is checked against, so they are written to be obviously correct
rather than efficient.
"""

from __future__ import annotations

import itertools
import random
from typing import Iterator

from orbitcert.graph import Graph, code, from_edges, relabel

# Reference counts, used to pin the enumeration against published data.
# Number of graphs on n unlabelled vertices -- OEIS A000088.
A000088 = [1, 1, 2, 4, 11, 34, 156, 1044, 12346, 274668]
# Number of triangle-free graphs on n unlabelled vertices -- OEIS A006785.
A006785 = [1, 1, 2, 3, 7, 14, 38, 107, 410, 1897, 12172]
# Number of connected/all graphs with girth >= 5 etc. are added where needed.


def all_labelled_graphs(k: int) -> Iterator[Graph]:
    """Every labelled graph on ``k`` vertices. 2**(k choose 2) of them."""
    pairs = list(itertools.combinations(range(k), 2))
    for mask in range(1 << len(pairs)):
        yield from_edges(k, [e for b, e in enumerate(pairs) if mask >> b & 1])


def random_graph(k: int, p: float = 0.5, rng: random.Random | None = None) -> Graph:
    rng = rng or random
    return from_edges(k, [e for e in itertools.combinations(range(k), 2)
                          if rng.random() < p])


def brute_canonical_code(g: Graph) -> tuple[int, ...]:
    """The lexicographically minimal code over all relabellings. O(k!)."""
    k = len(g)
    return min(code(relabel(g, p)) for p in itertools.permutations(range(k)))


def brute_is_canonical(g: Graph) -> bool:
    return code(g) == brute_canonical_code(g)


def brute_iso_classes(k: int, predicate=None) -> set[tuple[int, ...]]:
    """Canonical codes of every isomorphism class on ``k`` vertices, optionally filtered."""
    out = set()
    for g in all_labelled_graphs(k):
        if predicate is None or predicate(g):
            out.add(brute_canonical_code(g))
    return out


def nauty_available() -> bool:
    import shutil
    return bool(shutil.which("nauty-geng") and shutil.which("nauty-labelg"))


def _labelg(graph6_lines: list[str]) -> set[str]:
    """Canonise a batch of graph6 strings with nauty, returning the distinct forms."""
    import subprocess
    if not graph6_lines:
        return set()
    proc = subprocess.run(["nauty-labelg", "-q"], input="\n".join(graph6_lines),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"nauty-labelg failed: {proc.stderr}")
    return set(proc.stdout.split())


def nauty_iso_classes(n: int, *flags: str) -> set[str]:
    """Isomorphism classes on ``n`` vertices according to nauty, as canonical graph6.

    This is an oracle written by someone else, in another language, using a
    completely different algorithm (McKay's canonical augmentation rather than
    orderly generation).  Agreeing with it is far stronger evidence than agreeing
    with a brute force we wrote ourselves.
    """
    import subprocess
    proc = subprocess.run(["nauty-geng", "-q", *flags, str(n)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"nauty-geng failed: {proc.stderr}")
    return _labelg(proc.stdout.split())


def our_iso_classes(graphs) -> set[str]:
    """Canonise our own output through nauty so the two sets are comparable."""
    from orbitcert.graph import to_graph6
    return _labelg([to_graph6(g) for g in graphs])


def brute_has_clique(g: Graph, size: int) -> bool:
    k = len(g)
    return any(all(g[u] >> v & 1 for u, v in itertools.combinations(c, 2))
               for c in itertools.combinations(range(k), size))


def brute_has_independent_set(g: Graph, size: int) -> bool:
    k = len(g)
    return any(not any(g[u] >> v & 1 for u, v in itertools.combinations(c, 2))
               for c in itertools.combinations(range(k), size))


def brute_girth(g: Graph) -> float:
    """Length of the shortest cycle, or infinity if acyclic."""
    k = len(g)
    best = float("inf")
    for start in range(k):
        # BFS from `start`, tracking parents, detecting the shortest cycle through it.
        dist = {start: 0}
        parent = {start: -1}
        queue = [start]
        while queue:
            u = queue.pop(0)
            for v in range(k):
                if not (g[u] >> v & 1):
                    continue
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    best = min(best, dist[u] + dist[v] + 1)
    return best

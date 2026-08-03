"""Bitset graph representation and the prefix-structured canonical code.

The whole certified-enumeration design rests on one encoding choice, so it lives
alone in this module and is documented in full.

A simple graph ``G`` on the vertex set ``[k] = {0, ..., k-1}`` is stored as a
tuple of ``k`` integers, where bit ``v`` of ``rows[u]`` is set exactly when
``{u, v}`` is an edge.  The representation is redundant (each edge appears in two
rows) because the redundancy makes neighbourhood intersection a single ``&``.

The *code* of ``G`` is the bit string obtained by walking columns left to right::

    col(1) = G[0][1]
    col(2) = G[0][2] G[1][2]
    col(3) = G[0][3] G[1][3] G[2][3]
    ...
    col(k-1) = G[0][k-1] ... G[k-2][k-1]

and concatenating them.  Equivalently, ``code(G)`` reads the strict upper
triangle of the adjacency matrix in column-major order.

The point of column-major order — and the reason row-major order would break
everything — is the *prefix property*:

    for every m <= k,  code(G restricted to [m])  is a prefix of  code(G).

Deleting the highest-numbered vertex chops whole columns off the end of the code
and leaves the earlier columns untouched.  In row-major order, deleting a vertex
would puncture every row, and no prefix relationship would survive.  Every
soundness argument in :mod:`orbitcert.search` is ultimately an appeal to this
one property, which is why it is stated here rather than buried in the search.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Iterator, Sequence

Graph = tuple[int, ...]
"""A graph on ``k`` vertices: ``k`` bitmasks, bit ``v`` of ``rows[u]`` = edge ``uv``."""


def empty(k: int) -> Graph:
    """The edgeless graph on ``k`` vertices."""
    return (0,) * k


def from_edges(k: int, edges: Iterable[tuple[int, int]]) -> Graph:
    """Build a graph on ``k`` vertices from an iterable of edges."""
    rows = [0] * k
    for u, v in edges:
        if u == v:
            raise ValueError(f"loop at vertex {u}: simple graphs only")
        if not (0 <= u < k and 0 <= v < k):
            raise ValueError(f"edge ({u}, {v}) out of range for k={k}")
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return tuple(rows)


def edges(g: Graph) -> Iterator[tuple[int, int]]:
    """Yield each edge once, as ``(u, v)`` with ``u < v``."""
    for u, row in enumerate(g):
        rest = row >> (u + 1)
        v = u + 1
        while rest:
            if rest & 1:
                yield (u, v)
            rest >>= 1
            v += 1


def num_edges(g: Graph) -> int:
    return sum(bin(row).count("1") for row in g) // 2


def has_edge(g: Graph, u: int, v: int) -> bool:
    return bool(g[u] >> v & 1)


def degree(g: Graph, v: int) -> int:
    return bin(g[v]).count("1")


def code(g: Graph) -> tuple[int, ...]:
    """The prefix-structured code: strict upper triangle in column-major order.

    ``code(induced(g, m))`` is a prefix of ``code(g)`` for every ``m <= len(g)``.
    """
    return tuple(g[i] >> j & 1 for j in range(1, len(g)) for i in range(j))


def code_int(g: Graph) -> int:
    """The code packed into a single integer, most significant bit first.

    Comparing two ``code_int`` values of graphs on the *same* number of vertices
    orders them exactly as ``code`` does lexicographically, but in one machine
    operation.  Values for different vertex counts are not comparable.
    """
    acc = 0
    for j in range(1, len(g)):
        col = g[j] & ((1 << j) - 1)
        # Reverse the j low bits of column j so that vertex 0 lands in the most
        # significant position, matching the left-to-right reading of `code`.
        rev = 0
        for i in range(j):
            rev = rev << 1 | (col >> i & 1)
        acc = acc << j | rev
    return acc


def induced(g: Graph, m: int) -> Graph:
    """The subgraph induced on ``{0, ..., m-1}``."""
    mask = (1 << m) - 1
    return tuple(row & mask for row in g[:m])


def extend(g: Graph, neighbourhood: int) -> Graph:
    """Append one vertex joined to the vertices selected by ``neighbourhood``.

    ``neighbourhood`` is a bitmask over the existing vertices ``0..k-1``.  The new
    vertex receives index ``k``, so this appends exactly one column to the code
    and leaves the existing prefix untouched.
    """
    k = len(g)
    if neighbourhood >> k:
        raise ValueError(f"neighbourhood {neighbourhood:#x} names vertices outside [0,{k})")
    bit = 1 << k
    rows = [row | (bit if neighbourhood >> u & 1 else 0) for u, row in enumerate(g)]
    rows.append(neighbourhood)
    return tuple(rows)


def relabel(g: Graph, perm: Sequence[int]) -> Graph:
    """Apply a permutation: the result ``H`` has ``H[p[u]][p[v]] == g[u][v]``."""
    k = len(g)
    if len(perm) != k:
        raise ValueError(f"permutation has length {len(perm)}, expected {k}")
    rows = [0] * k
    for u in range(k):
        pu = perm[u]
        row = g[u]
        while row:
            v = (row & -row).bit_length() - 1
            row &= row - 1
            rows[pu] |= 1 << perm[v]
    return tuple(rows)


def complement(g: Graph) -> Graph:
    k = len(g)
    full = (1 << k) - 1
    return tuple((~g[u] & full) & ~(1 << u) for u in range(k))


def is_clique(g: Graph, vertices: Sequence[int]) -> bool:
    return all(has_edge(g, u, v) for u, v in combinations(vertices, 2))


def is_independent(g: Graph, vertices: Sequence[int]) -> bool:
    return not any(has_edge(g, u, v) for u, v in combinations(vertices, 2))


def to_graph6(g: Graph) -> str:
    """Encode in nauty's graph6 format, so results can be fed to external tools."""
    k = len(g)
    if k < 1 or k > 62:
        raise ValueError("graph6 encoding here supports 1 <= k <= 62 vertices")
    bits = [g[i] >> j & 1 for j in range(1, k) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    out = [chr(k + 63)]
    for i in range(0, len(bits), 6):
        val = 0
        for b in bits[i:i + 6]:
            val = val << 1 | b
        out.append(chr(val + 63))
    return "".join(out)


def from_graph6(s: str) -> Graph:
    """Decode nauty's graph6 format."""
    s = s.strip()
    if not s:
        raise ValueError("empty graph6 string")
    k = ord(s[0]) - 63
    if k < 0 or k > 62:
        raise ValueError(f"unsupported graph6 order byte {s[0]!r}")
    bits: list[int] = []
    for ch in s[1:]:
        val = ord(ch) - 63
        bits.extend(val >> b & 1 for b in range(5, -1, -1))
    rows = [0] * k
    idx = 0
    for j in range(1, k):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                rows[i] |= 1 << j
                rows[j] |= 1 << i
            idx += 1
    return tuple(rows)

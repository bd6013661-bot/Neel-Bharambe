"""orbitcert — certified isomorph-free exhaustive generation.

Exhaustive computer searches underpin a lot of discrete mathematics: the claim
"no object with these properties exists" is often established by enumerating one
representative of every isomorphism class and finding none.  The enumeration
engines that do this are fast and mature, but they emit no evidence.  A referee
who wants to check such a result has one option: read and trust several thousand
lines of highly optimised C.

This package makes those searches *certifying*.  The generator streams a proof as
it runs; an independent checker replays it and either confirms the claim or
points at the exact node where the search went wrong.  The checker never
searches — it only applies permutations and compares codes — so verification is
asymptotically cheaper than the original computation.

Quick start::

    from orbitcert import RamseyProperty, enumerate_graphs, check_file

    with open("r33.proof", "w") as fh:
        result = enumerate_graphs(RamseyProperty(3, 3), 6, proof=fh)
    assert result.nonexistence           # no (K3, I3)-free graph on 6 vertices
    print(check_file("r33.proof").summary())   # VERIFIED: ... hence R(3,3) <= 6
"""

from .canon import automorphisms, canonical_form, find_smaller, is_canonical, verify_witness
from .check import CheckResult, check_file, check_stream
from .graph import (
    Graph,
    code,
    edges,
    empty,
    extend,
    from_edges,
    from_graph6,
    induced,
    num_edges,
    relabel,
    to_graph6,
)
from .problems import CliqueFree, GirthAtLeast, HereditaryProperty, RamseyProperty, TriangleFree
from .proof import ProofSyntaxError, ProofWriter
from .search import SearchResult, enumerate_graphs, iter_level

__version__ = "0.1.0"

__all__ = [
    "Graph",
    "empty",
    "extend",
    "from_edges",
    "edges",
    "code",
    "induced",
    "relabel",
    "num_edges",
    "to_graph6",
    "from_graph6",
    "find_smaller",
    "is_canonical",
    "canonical_form",
    "automorphisms",
    "verify_witness",
    "HereditaryProperty",
    "RamseyProperty",
    "CliqueFree",
    "TriangleFree",
    "GirthAtLeast",
    "ProofWriter",
    "ProofSyntaxError",
    "enumerate_graphs",
    "iter_level",
    "SearchResult",
    "check_stream",
    "check_file",
    "CheckResult",
    "__version__",
]

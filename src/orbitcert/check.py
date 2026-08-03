"""The proof checker: the only component that has to be trusted.

Everything else in this package is free to be clever, heuristic, buggy or
adversarial.  The checker is the one piece a sceptic reads, so it does exactly
four things and nothing else:

1. re-derives which candidate extensions violate the hereditary property;
2. verifies each permutation witness by applying it and comparing codes;
3. insists that *every* candidate mask is accounted for — accepted, witnessed,
   or property-violating — with no gaps and no duplicates;
4. checks that the traversal reaches the target order and finds nothing there.

Point 3 is what makes the proof a proof.  A generator that silently skipped a
subtree would leave masks unaccounted for, and the checker would reject.  It is
not possible to certify a false nonexistence claim without either producing an
invalid permutation or leaving a hole, and both are caught here.

The checker never searches for a permutation, never computes a canonical form,
and never calls into :mod:`orbitcert.canon`.  Its cost per node is the cost of
the property test plus ``O(k^2)`` per witness — strictly less than the
generator's, which had to *find* those witnesses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TextIO

from .graph import Graph, code, empty, extend, relabel
from .problems import HereditaryProperty, RamseyProperty, CliqueFree, TriangleFree, GirthAtLeast
from .proof import ProofSyntaxError, Record, parse

__all__ = ["CheckResult", "check_stream", "check_file", "build_property"]


@dataclass
class CheckResult:
    """Verdict of a proof check."""

    ok: bool
    claim: str = ""
    order: int = 0
    problem: str = ""
    params: dict[str, str] = field(default_factory=dict)
    nodes: int = 0
    witnesses: int = 0
    property_rejects: int = 0
    max_depth: int = 0
    error: Optional[str] = None

    def summary(self) -> str:
        if not self.ok:
            return f"REJECTED: {self.error}"
        return (f"VERIFIED: {self.claim}\n"
                f"  nodes={self.nodes} witnesses-checked={self.witnesses} "
                f"property-rejects-rederived={self.property_rejects} depth={self.max_depth}")


def build_property(name: str, params: dict[str, str]) -> HereditaryProperty:
    """Reconstruct the property from the proof header.

    The checker builds its *own* property object from the header rather than
    accepting one from the caller, so the claim being verified is fixed by the
    proof itself and cannot be quietly weakened.
    """
    if name == "ramsey":
        return RamseyProperty(int(params["s"]), int(params["t"]))
    if name == "clique-free":
        return CliqueFree(int(params["s"]))
    if name == "triangle-free":
        return TriangleFree()
    if name == "girth":
        return GirthAtLeast(int(params["girth"]))
    raise ProofSyntaxError(f"unknown problem {name!r} in proof header")


def _claim_text(name: str, params: dict[str, str], order: int, found_none: bool) -> str:
    if name == "ramsey":
        s, t = params["s"], params["t"]
        if found_none:
            return (f"no (K{s}, I{t})-free graph exists on {order} vertices, "
                    f"hence R({s},{t}) <= {order}")
        return f"(K{s}, I{t})-free graphs on {order} vertices were enumerated"
    verb = "no graph exists" if found_none else "graphs were enumerated"
    ps = " ".join(f"{k}={v}" for k, v in sorted(params.items()) if k != "name")
    return f"{verb} on {order} vertices with property {name}{' ' + ps if ps else ''}"


def check_stream(stream: TextIO, *, verbose: bool = False) -> CheckResult:
    """Verify a proof stream. Returns a :class:`CheckResult`; never raises on bad proofs."""
    res = CheckResult(ok=False)
    try:
        return _check(stream, res, verbose=verbose)
    except ProofSyntaxError as exc:
        res.error = str(exc)
        return res
    except (ValueError, IndexError, KeyError, RecursionError) as exc:
        res.error = f"{type(exc).__name__}: {exc}"
        return res


def _check(stream: TextIO, res: CheckResult, *, verbose: bool) -> CheckResult:
    records = parse(stream)

    prop: Optional[HereditaryProperty] = None
    order = 0
    saw_root = False

    # The DFS stack of graphs. stack[-1] is the node currently being described.
    stack: list[Graph] = []
    # Per-node bookkeeping: which masks have been accounted for, and how.
    accounted: list[set[int]] = []
    # Masks accepted at the current node, in the order the proof descends into them.
    pending_descents: list[list[int]] = []
    reached_target = False
    found_at_target = 0
    closed_root = False

    for rec in records:
        if rec.kind == "header":
            continue

        if rec.kind == "problem":
            res.problem = rec.fields["name"]
            res.params = {k: v for k, v in rec.fields.items() if k != "name"}
            prop = build_property(res.problem, res.params)
            continue

        if rec.kind == "order":
            order = rec.depth
            res.order = order
            if order < 1:
                raise ProofSyntaxError(f"order must be >= 1, got {order}")
            continue

        if rec.kind == "root":
            if prop is None or order == 0:
                raise ProofSyntaxError("root record before problem/order header")
            if rec.mask != 0:
                raise ProofSyntaxError("root must be the one-vertex graph (mask 0)")
            stack = [empty(1)]
            accounted = [set()]
            pending_descents = [[]]
            saw_root = True
            res.nodes += 1
            res.max_depth = max(res.max_depth, 1)
            if order == 1:
                reached_target = True
                found_at_target += 1
            continue

        if not saw_root:
            raise ProofSyntaxError(f"record {rec.kind!r} before root")
        assert prop is not None

        if rec.kind == "witness":
            g = stack[-1]
            k = len(g)
            if rec.mask >> k:
                raise ProofSyntaxError(f"witness mask {rec.mask:#x} names vertices outside [0,{k})")
            if rec.mask in accounted[-1]:
                raise ProofSyntaxError(f"mask {rec.mask:#x} accounted for twice at depth {k}")
            if not prop.admits_extension(g, rec.mask):
                raise ProofSyntaxError(
                    f"depth {k}: mask {rec.mask:#x} already fails the property; "
                    "a canonicity witness for it is meaningless")
            child = extend(g, rec.mask)
            if len(rec.perm) != k + 1 or sorted(rec.perm) != list(range(k + 1)):
                raise ProofSyntaxError(
                    f"depth {k}: witness for mask {rec.mask:#x} is not a permutation of "
                    f"0..{k}: {rec.perm}")
            if not code(relabel(child, rec.perm)) < code(child):
                raise ProofSyntaxError(
                    f"depth {k}: witness for mask {rec.mask:#x} does not produce a "
                    "lexicographically smaller code")
            accounted[-1].add(rec.mask)
            res.witnesses += 1
            continue

        if rec.kind == "empty":
            g = stack[-1]
            if rec.depth != len(g):
                raise ProofSyntaxError(
                    f"empty record claims depth {rec.depth} but node has {len(g)} vertices")
            continue

        if rec.kind == "descend":
            g = stack[-1]
            k = len(g)
            if k >= order:
                raise ProofSyntaxError(f"descend past the target order {order}")
            if rec.mask >> k:
                raise ProofSyntaxError(f"descend mask {rec.mask:#x} names vertices outside [0,{k})")
            if rec.mask in accounted[-1]:
                raise ProofSyntaxError(f"mask {rec.mask:#x} accounted for twice at depth {k}")
            if not prop.admits_extension(g, rec.mask):
                raise ProofSyntaxError(
                    f"depth {k}: descended into mask {rec.mask:#x}, which violates the property")
            accounted[-1].add(rec.mask)
            pending_descents[-1].append(rec.mask)
            child = extend(g, rec.mask)
            stack.append(child)
            accounted.append(set())
            pending_descents.append([])
            res.nodes += 1
            res.max_depth = max(res.max_depth, len(child))
            if len(child) == order:
                reached_target = True
                found_at_target += 1
            continue

        if rec.kind == "ascend":
            if len(stack) == 1:
                raise ProofSyntaxError("ascend above the root")
            child = stack.pop()
            closed = accounted.pop()
            pending_descents.pop()
            # The node we just left must have accounted for every candidate mask,
            # unless it was at the target order (where no extension is required).
            if len(child) < order:
                res.property_rejects += _require_full_coverage(child, prop, closed)
            continue

        if rec.kind == "qed":
            if len(stack) != 1:
                raise ProofSyntaxError(
                    f"proof ended with {len(stack) - 1} unclosed node(s)")
            if order > 1:
                res.property_rejects += _require_full_coverage(stack[0], prop, accounted[0])
            closed_root = True
            declared_nodes = int(rec.fields["nodes"])
            declared_w = int(rec.fields["witnesses"])
            if declared_nodes != res.nodes:
                raise ProofSyntaxError(
                    f"qed declares {declared_nodes} nodes, checker counted {res.nodes}")
            if declared_w != res.witnesses:
                raise ProofSyntaxError(
                    f"qed declares {declared_w} witnesses, checker counted {res.witnesses}")
            continue

        raise ProofSyntaxError(f"unexpected record {rec.kind!r}")

    if not closed_root:
        raise ProofSyntaxError("proof stream ended without a qed record")

    res.ok = True
    res.claim = _claim_text(res.problem, res.params, order, found_at_target == 0)
    return res


def _require_full_coverage(g: Graph, prop: HereditaryProperty, seen: set[int]) -> int:
    """Every extension of ``g`` must be accepted, witnessed, or property-violating.

    Returns the number of masks the checker re-derived as property-violating —
    the records the proof was allowed to leave out.  Raises if any mask is
    unaccounted for, which is precisely the signature of a search that skipped a
    subtree.
    """
    k = len(g)
    rederived = 0
    for mask in range(1 << k):
        if mask in seen:
            continue
        if prop.admits_extension(g, mask):
            raise ProofSyntaxError(
                f"depth {k}: extension by mask {mask:#x} satisfies the property but the "
                "proof neither descends into it nor supplies a canonicity witness — "
                "the search has a hole here")
        rederived += 1
    return rederived


def check_file(path: str, *, verbose: bool = False) -> CheckResult:
    with open(path, "r", encoding="utf-8") as fh:
        return check_stream(fh, verbose=verbose)

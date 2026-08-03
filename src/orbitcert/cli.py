"""Command line interface: ``python -m orbitcert``.

Two subcommands mirroring the two halves of the system.

``prove``  runs the (untrusted) search and writes a certificate.
``check``  verifies a certificate, trusting nothing that produced it.

They are separate commands on purpose. Nothing stops you piping one into the
other — ``orbitcert prove ... --proof - | orbitcert check`` verifies without the
certificate ever touching disk, which matters once certificates outgrow storage —
but the separation is the point: the thing that checks must not be the thing that
searched.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
import time
from typing import Iterator, Optional, TextIO

from .check import check_stream
from .graph import to_graph6
from .problems import CliqueFree, GirthAtLeast, HereditaryProperty, RamseyProperty, TriangleFree
from .search import enumerate_graphs


def _build_property(args: argparse.Namespace) -> HereditaryProperty:
    if args.ramsey:
        return RamseyProperty(args.ramsey[0], args.ramsey[1])
    if args.clique_free:
        return CliqueFree(args.clique_free)
    if args.girth:
        return GirthAtLeast(args.girth)
    if args.triangle_free:
        return TriangleFree()
    raise SystemExit("choose a property: --ramsey S T, --clique-free S, "
                     "--girth G, or --triangle-free")


@contextlib.contextmanager
def _open_out(path: Optional[str]) -> Iterator[Optional[TextIO]]:
    """Open a sink, treating ``-`` as stdout and ``None`` as 'no output'."""
    if path is None:
        yield None
    elif path == "-":
        yield sys.stdout
    else:
        with open(path, "w", encoding="utf-8") as fh:
            yield fh


def cmd_prove(args: argparse.Namespace) -> int:
    prop = _build_property(args)
    # Progress and results go to stderr whenever the certificate is on stdout, so
    # that piping into the checker stays clean.
    report = sys.stderr if args.proof == "-" else sys.stdout

    with _open_out(args.proof) as proof_fh:
        t0 = time.time()
        result = enumerate_graphs(prop, args.order, proof=proof_fh,
                                  node_limit=args.budget, collect=True)
        elapsed = time.time() - t0

    if args.graphs:
        with _open_out(args.graphs) as gfh:
            assert gfh is not None
            for g in result.witnesses:
                gfh.write(to_graph6(g) + "\n")

    if not args.quiet:
        print(f"problem: {prop.name} {prop.params()}, target order {args.order}", file=report)
        print("counts by order: " + " ".join(str(c) for c in result.counts), file=report)
        if result.nonexistence:
            print(f"RESULT: no such graph on {args.order} vertices", file=report)
            if isinstance(prop, RamseyProperty):
                print(f"        hence R({prop.s},{prop.t}) <= {args.order}", file=report)
        else:
            print(f"RESULT: {len(result.witnesses)} graph(s) on {args.order} vertices",
                  file=report)
        print(f"nodes={result.nodes} witnesses={result.canonicity_witnesses} "
              f"property-rejects={result.property_rejects} time={elapsed:.2f}s", file=report)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    stream = sys.stdin if args.proof in (None, "-") else open(args.proof, "r", encoding="utf-8")
    try:
        t0 = time.time()
        res = check_stream(stream)
        elapsed = time.time() - t0
    finally:
        if stream is not sys.stdin:
            stream.close()

    print(res.summary())
    if res.ok and not args.quiet:
        print(f"  check time: {elapsed:.2f}s")
    return 0 if res.ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="orbitcert",
        description="Certified isomorph-free exhaustive generation.")
    sub = p.add_subparsers(dest="command", required=True)

    pr = sub.add_parser("prove", help="run the search and emit a certificate")
    pr.add_argument("--ramsey", nargs=2, type=int, metavar=("S", "T"),
                    help="(K_S, I_T)-free graphs; nonexistence gives R(S,T) <= order")
    pr.add_argument("--clique-free", type=int, metavar="S", help="graphs with no K_S")
    pr.add_argument("--triangle-free", action="store_true", help="graphs with no triangle")
    pr.add_argument("--girth", type=int, metavar="G", help="graphs of girth at least G")
    pr.add_argument("--order", type=int, required=True, help="target number of vertices")
    pr.add_argument("--proof", metavar="FILE", help="write the certificate here ('-' for stdout)")
    pr.add_argument("--graphs", metavar="FILE", help="write graphs at the target order, in graph6")
    pr.add_argument("--budget", type=int, default=0,
                    help="node budget for the canonicity search (0 = unlimited). "
                         "Lowering it only ever costs time, never correctness.")
    pr.add_argument("--quiet", action="store_true")
    pr.set_defaults(func=cmd_prove)

    ck = sub.add_parser("check", help="verify a certificate")
    ck.add_argument("proof", nargs="?", help="certificate file (default: stdin)")
    ck.add_argument("--quiet", action="store_true")
    ck.set_defaults(func=cmd_check)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

"""Measure the scaling claim: is checking cheaper than generating, and increasingly so?

The central claim of the project is not that certificates exist — it is that
verifying one costs asymptotically less than producing it, because the checker
skips the canonicity search entirely. That is a quantitative claim, so it gets
measured rather than asserted.

Both halves are timed in the *same* implementation (the Python reference), so the
ratio is like-for-like and no cross-language factor contaminates it. The C tools
are ~100x faster on both sides and give the same ratio.

Usage:
    python3 prototype/benchmark.py                 # default instance family
    python3 prototype/benchmark.py --max-seconds 60
    python3 prototype/benchmark.py --csv results/scaling.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import time
from dataclasses import asdict, dataclass

sys.path.insert(0, "src")

from orbitcert import RamseyProperty, TriangleFree, check_stream, enumerate_graphs


@dataclass
class Row:
    family: str
    order: int
    nodes: int
    witnesses: int
    property_rejects: int
    certificate_bytes: int
    generate_seconds: float
    check_seconds: float
    ratio: float
    verdict: str


def measure(prop, order: int, family: str) -> Row:
    buf = io.StringIO()
    t0 = time.perf_counter()
    res = enumerate_graphs(prop, order, proof=buf, collect=False)
    gen = time.perf_counter() - t0

    proof = buf.getvalue()
    t0 = time.perf_counter()
    chk = check_stream(io.StringIO(proof))
    chk_t = time.perf_counter() - t0

    return Row(
        family=family,
        order=order,
        nodes=res.nodes,
        witnesses=res.canonicity_witnesses,
        property_rejects=res.property_rejects,
        certificate_bytes=len(proof),
        generate_seconds=round(gen, 4),
        check_seconds=round(chk_t, 4),
        ratio=round(chk_t / gen, 4) if gen > 0 else float("nan"),
        verdict="VERIFIED" if chk.ok else f"REJECTED: {chk.error}",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-seconds", type=float, default=45.0,
                    help="stop a family once a single instance exceeds this")
    ap.add_argument("--csv", metavar="FILE", help="also write results as CSV")
    args = ap.parse_args()

    families = [
        ("R(3,4)", lambda: RamseyProperty(3, 4), range(4, 10)),
        ("R(3,5)", lambda: RamseyProperty(3, 5), range(6, 15)),
        ("R(4,4)", lambda: RamseyProperty(4, 4), range(6, 15)),
        ("triangle-free", lambda: TriangleFree(), range(4, 12)),
    ]

    rows: list[Row] = []
    header = (f"{'family':>14} {'n':>3} {'nodes':>9} {'witnesses':>10} "
              f"{'cert bytes':>11} {'gen s':>8} {'chk s':>8} {'chk/gen':>8}  verdict")
    print(header)
    print("-" * len(header))

    for name, make, orders in families:
        for n in orders:
            row = measure(make(), n, name)
            rows.append(row)
            print(f"{row.family:>14} {row.order:>3} {row.nodes:>9,} {row.witnesses:>10,} "
                  f"{row.certificate_bytes:>11,} {row.generate_seconds:>8.3f} "
                  f"{row.check_seconds:>8.3f} {row.ratio:>8.3f}  {row.verdict}", flush=True)
            if row.verdict != "VERIFIED":
                print("  ABORTING: a certificate failed to verify", file=sys.stderr)
                return 1
            if row.generate_seconds > args.max_seconds:
                print(f"  (stopping {name}: exceeded {args.max_seconds}s)", flush=True)
                break

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(asdict(rows[0])))
            w.writeheader()
            for r in rows:
                w.writerow(asdict(r))
        print(f"\nwrote {args.csv}")

    # The claim needs stating carefully, because the raw trend is not monotone.
    #
    # While the search tree is still growing, each extra vertex costs the
    # generator a canonicity search on exponentially many more candidates, and
    # costs the checker only bookkeeping -- so the ratio falls.
    #
    # Once the property becomes unsatisfiable the tree stops growing: further
    # orders add empty levels. The generator's work plateaus, while the checker
    # still pays its per-node coverage sweep, so the ratio drifts back up. That
    # is saturation, not a failure of the claim, and reporting the endpoints
    # without separating the two regimes would misstate the result.
    print("\nratio trend by family:")
    print("  (growth phase = orders where the search tree is still expanding)")
    for name, _, _ in families:
        fam = [r for r in rows if r.family == name and r.generate_seconds > 0.01]
        if len(fam) < 2:
            continue
        peak = max(r.nodes for r in fam)
        growth = [r for r in fam if r.nodes < peak] or fam[:1]
        growth.append(next(r for r in fam if r.nodes == peak))
        first, last = growth[0], growth[-1]
        direction = "falls" if last.ratio < first.ratio else "does NOT fall"
        best = min(fam, key=lambda r: r.ratio)
        saturated = [r for r in fam if r.nodes == peak]
        print(f"  {name:>14}: growth n={first.order} ({first.ratio:.3f}) -> "
              f"n={last.order} ({last.ratio:.3f})  [{direction}]"
              f"   best {best.ratio:.3f} at n={best.order}"
              + (f"   then {len(saturated) - 1} saturated order(s)"
                 if len(saturated) > 1 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""End-to-end check: enumerate, certify, and verify classical Ramsey numbers.

Every number here is cross-checked against Radziszowski's *Small Ramsey Numbers*
dynamic survey (Electronic Journal of Combinatorics, DS1), including the counts
of critical graphs, which is a far sharper test than the Ramsey value alone: a
search that pruned too aggressively would still report nonexistence at R(s,t) but
would undercount the critical graphs at R(s,t)-1.
"""

import io
import sys
import time

sys.path.insert(0, "src")

from orbitcert import RamseyProperty, check_stream, enumerate_graphs, to_graph6

# (s, t, R(s,t), number of critical graphs on R-1 vertices)  -- all from DS1.
CASES = [
    (3, 3, 6, 1),
    (3, 4, 9, 3),
    (3, 5, 14, 1),
    (4, 4, 18, 2),
    (3, 6, 18, 7),
]

limit = float(sys.argv[1]) if len(sys.argv) > 1 else 1e18
failures = 0

for s, t, R, ncrit in CASES:
    prop = RamseyProperty(s, t)
    print(f"=== R({s},{t}) = {R} ===", flush=True)

    t0 = time.time()
    crit = enumerate_graphs(prop, R - 1, collect=True)
    dt = time.time() - t0
    ok = len(crit.witnesses) == ncrit
    failures += not ok
    print(f"  critical graphs on {R-1} vertices: {len(crit.witnesses)} "
          f"(DS1 says {ncrit}) {'OK' if ok else 'MISMATCH'}  [{dt:.1f}s]", flush=True)
    print(f"  per-level counts: {crit.counts}", flush=True)
    if 0 < len(crit.witnesses) <= 8:
        for g in crit.witnesses:
            print(f"    {to_graph6(g)}", flush=True)

    buf = io.StringIO()
    t0 = time.time()
    res = enumerate_graphs(prop, R, proof=buf, collect=True)
    gen_dt = time.time() - t0
    proof = buf.getvalue()
    ok = res.nonexistence
    failures += not ok
    print(f"  order {R}: {len(res.witnesses)} graphs -> nonexistence={res.nonexistence} "
          f"{'OK' if ok else 'MISMATCH'}  [generate {gen_dt:.1f}s]", flush=True)
    print(f"  proof: {len(proof):,} bytes, {proof.count(chr(10)):,} records, "
          f"{res.canonicity_witnesses:,} witnesses", flush=True)

    t0 = time.time()
    chk = check_stream(io.StringIO(proof))
    chk_dt = time.time() - t0
    failures += not chk.ok
    if chk.ok:
        print(f"  CHECK: VERIFIED -- {chk.claim}  [{chk_dt:.1f}s]", flush=True)
        if gen_dt > 0:
            print(f"  check/generate time ratio: {chk_dt / gen_dt:.2f}x", flush=True)
    else:
        print(f"  CHECK: REJECTED -- {chk.error}", flush=True)
    print(flush=True)

    if time.time() > limit:
        break

print("FAILURES:", failures)
sys.exit(1 if failures else 0)

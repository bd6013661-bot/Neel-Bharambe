from rtd_probe import search  # run from prototype/rtd/
import time
for n in [6,7,8]:
    maxm = 1+n+n*(n-1)//2
    for m in range(16, maxm+1):
        t0=time.time()
        sat, el, rows, nc = search(n, m, 2, 4)
        print(f"n={n} m={m}: {'SAT' if sat else 'UNSAT'}  {el:.1f}s  clauses={nc}", flush=True)
        if sat:
            print("\n".join(rows), flush=True)

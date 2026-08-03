# Certified results

Each certificate is produced by the untrusted generator (`bin/ocgen`) and verified
by the independent checker (`bin/occheck`), which never searches — it only applies
permutations, compares codes, and re-derives the property tests itself.

| Result | Nodes | Witnesses | Certificate | Generate | Verify |
|---|---|---|---|---|---|
| R(3,3) ≤ 6  | 9 | 7 | 220 B | <0.01 s | <0.01 s |
| R(3,4) ≤ 9  | 48 | 173 | 3.3 KB | <0.01 s | <0.01 s |
| R(3,5) ≤ 14 | 1,029 | 9,060 | 220 KB | 0.04 s | 0.02 s |
| R(3,6) ≤ 18 | 761,692 | 9,863,537 | 358 MB | 443 s | 152 s |

R(3,6) additionally re-derived 9,399,540,422 property rejections during checking —
these are deliberately absent from the certificate, because recomputing them is
cheaper than reading them.

## Cross-checks against the literature

Per-level counts are the sharp test: a search that pruned too aggressively would
still report nonexistence at R(s,t) but would undercount the critical graphs.

- R(3,5), counts by order: 1, 2, 3, 7, 13, 32, 71, 179, 290, 313, 105, 12, 1 —
  matches McKay's published enumeration; the unique 13-vertex graph is the
  4-regular circulant C13(1,5).
- R(3,6), counts by order: 1, 2, 3, 7, 14, 37, 100, 356, 1407, 6657, 30395,
  116792, 275086, 263520, 64732, 2576, **7** — the 7 critical graphs on 17
  vertices match Radziszowski's dynamic survey DS1.
- Critical-graph counts for R(3,3), R(3,4), R(3,5) are 1, 3, 1 — all matching DS1.

## Reproducing

```bash
make -C csrc
./bin/ocgen --ramsey 3 6 --order 18 --proof R36.proof && ./bin/occheck R36.proof
```

Certificates need not be stored. Piping the generator straight into the checker
verifies in one pass with nothing on disk:

```bash
./bin/ocgen --ramsey 3 5 --order 14 --quiet --proof /dev/stdout | ./bin/occheck
```

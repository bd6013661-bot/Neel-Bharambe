# orbitcert — certified isomorph-free exhaustive generation

Exhaustive computer search establishes a large share of the nonexistence results
in discrete mathematics. "No such graph exists on $n$ vertices" is proved by
enumerating one representative of every isomorphism class and finding none.

The engines that do this are fast, mature, and **emit no evidence**. A referee who
wants to check such a result has exactly one option: read and trust several
thousand lines of highly optimised C.

`orbitcert` makes those searches *certifying*. The generator streams a proof as it
runs. An independent checker replays it and either confirms the claim or points
at the exact node where the search went wrong. The checker never searches — it
only applies permutations and compares codes — so **verification is cheaper than
the original computation**, and gets relatively cheaper as instances grow.

Related work, honestly stated: the MathCheck project (Bright, Ganesh et al.) has
published certificates for SAT+CAS searches — including verified certificates for
R(3,8)/R(3,9) at IJCAI 2025 — with a trusted base of a SAT solver plus a patched
DRAT-trim. `orbitcert` certifies the enumeration itself, with no solver anywhere:
the entire trusted base is the ~300-line checker in `csrc/occheck.c`. See
`PLAN.md` §4 for the full positioning.

```
$ ./bin/ocgen --ramsey 3 5 --order 14 --proof R35.proof
problem: (K3, I5)-free graphs, target order 14
counts by order: 1 2 3 7 13 32 71 179 290 313 105 12 1 0
RESULT: no such graph on 14 vertices -> R(3,5) <= 14
nodes=1029 witnesses=9060 property-rejects=788810 time=0.04s

$ ./bin/occheck R35.proof
VERIFIED: no (K3, I5)-free graph exists on 14 vertices, hence R(3,5) <= 14
  nodes=1029 witnesses-checked=9060 property-rejects-rederived=788810
```

## The idea

Every step of an orderly-generation search is cheap and deterministic except one:
deciding whether a graph is the lexicographic minimum of its isomorphism class.
That step has a sharp asymmetry.

|  | cost |
|---|---|
| Proving a graph is **not** canonical | exhibit one permutation — $O(k^2)$ to verify |
| Proving a graph **is** canonical | rule out all $k!$ permutations |

So the certificate records **only the permutations, and only for rejections**.
Everything else the checker recomputes, because recomputing is cheaper than
reading. That single design decision is what makes the certificate small, the
checker tiny, and checking cheaper than searching.

It has a second consequence. Because the generator may only prune when it *holds*
a witness, a buggy, heuristic, or deliberately crippled canonicity engine cannot
produce a false result — only a slow one. Errors are **strictly one-sided**. The
generator is free to be fast and untrusted; the trusted base stays at a few
hundred readable lines.

The mathematics is in [`docs/theory.md`](docs/theory.md): three short theorems,
each machine-checked exhaustively at small sizes.

## Install and run

No dependencies beyond a C compiler. Python 3.11+ for the reference
implementation and tests.

```bash
make -C csrc                    # builds bin/ocgen and bin/occheck
python3 -m pytest               # 110 tests
```

```bash
# certify a Ramsey upper bound
./bin/ocgen --ramsey 3 4 --order 9 --proof R34.proof
./bin/occheck R34.proof

# enumerate rather than refute: emit the graphs at the target order
./bin/ocgen --ramsey 3 5 --order 13 --graphs crit.g6
```

From Python:

```python
from orbitcert import RamseyProperty, enumerate_graphs, check_file

with open("R33.proof", "w") as fh:
    result = enumerate_graphs(RamseyProperty(3, 3), 6, proof=fh)

assert result.nonexistence
print(check_file("R33.proof").summary())
# VERIFIED: no (K3, I3)-free graph exists on 6 vertices, hence R(3,3) <= 6
```

## Results

Each certificate below is verified by **two independent checkers** — the C one in
`csrc/occheck.c` and the Python one in `src/orbitcert/check.py`.

| Result | Certificate | Witnesses | Generate | Check | Check/generate |
|---|---|---|---|---|---|
| $R(3,3) \le 6$ | 220 B | 7 | 0.00 s | 0.00 s | 0.49× |
| $R(3,4) \le 9$ | 3.3 KB | 173 | 0.03 s | 0.01 s | 0.33× |
| $R(3,5) \le 14$ | 220 KB | 9,060 | 5.9 s | 1.4 s | 0.25× |

*(times from the Python reference implementation, so both halves are measured
like-for-like; the C tools are ~100× faster on both sides and give the same
ratio.)*

### How the ratio actually behaves

The honest version of the scaling claim, from `prototype/benchmark.py`:

| family | growth phase | best ratio |
|---|---|---|
| triangle-free | $n{=}6$: 0.144 → $n{=}9$: **0.023** | 0.023 |
| $R(4,4)$ | $n{=}6$: 0.283 → $n{=}9$: 0.203 | 0.203 |
| $R(3,5)$ | $n{=}6$: 0.187 → $n{=}10$: 0.145 | 0.129 |

While the search tree is still growing, each extra vertex costs the generator a
canonicity search over exponentially more candidates and costs the checker only
bookkeeping — so the ratio falls, reaching a **43× advantage** for triangle-free
graphs at $n = 9$.

It is **not monotone**, and pretending otherwise would misstate the result. Once
the property becomes unsatisfiable the tree stops growing — for $R(3,5)$ the node
count plateaus at 1,029 from $n = 13$ onward — so the generator's work levels off
while the checker still pays its per-node coverage sweep, and the ratio drifts
back up. That is saturation, not a failure of the mechanism, and the benchmark
reports the two regimes separately rather than quoting endpoints.

## Correctness

The claim "this search missed nothing" deserves more than the author's word.

**Against independent implementations.** The enumeration agrees *exactly* with
[nauty](https://pallini.di.uniroma1.it/) — a different algorithm, written by
other people, in another language — on all graphs to $n = 8$, triangle-free
graphs to $n = 9$, and girth-$\ge 5$ graphs to $n = 8$.

**Against published data.** Counts match OEIS A000088 and A006785. Critical-graph
counts match Radziszowski's *Small Ramsey Numbers* survey. The per-level counts
for $R(3,5)$ — 1, 2, 3, 7, 13, 32, 71, 179, 290, 313, 105, 12, 1 — match McKay's
published enumeration.

**Against itself.** The C and Python implementations agree to the node, witness
and rejection count.

**Against tampering.** This is the one that matters. Valid certificates are
corrupted twelve ways — deleting a witness, deleting a whole subtree, replacing a
permutation with the identity, supplying a non-bijection, truncating the stream,
inflating the tallies, strengthening the claim in the header, duplicating a
record. Both checkers reject every one, naming the offending node:

```
$ ./bin/occheck tampered.proof
REJECTED: depth 5: extension by mask 1 satisfies the property but is neither
          descended into nor witnessed -- the search has a hole here
```

**Against a broken generator.** The canonicity engine is deliberately crippled to
a one-node budget; the tests confirm no isomorphism class is lost and the
certificates still verify. One-sided error, demonstrated rather than asserted.

## What is and isn't certified

Certified: **completeness** — the search missed nothing. That is exactly what
nonexistence claims need.

Not certified: **irredundancy** — that no two retained graphs are isomorphic.
Proving that needs certified *non*-isomorphism, which has no short witness of this
kind and buys nothing for nonexistence. A reported count is therefore an upper
bound on the number of isomorphism classes unless you additionally trust the
canonicity engine.

Being precise about this is the difference between a proof system and a claim.

## Layout

```
src/orbitcert/     Python reference implementation
  graph.py         bitset graphs; the prefix-structured code
  canon.py         canonicity by branch-and-bound, with witness extraction
  problems.py      hereditary properties (Ramsey, clique-free, girth)
  search.py        orderly generation with certificate emission
  proof.py         the certificate format
  check.py         the checker  <-- the trusted component
csrc/
  ocgen.c          fast generator (untrusted by design)
  occheck.c        independent checker, ~300 lines, no dependencies
docs/theory.md     theorems and proofs
tests/             110 tests, including the tampering battery
prototype/         exhaustive machine-checks of the underlying lemmas
```

## Limitations

- Vertex-augmentation only, so properties must be hereditary under *induced*
  subgraphs.
- Orderly generation prunes less aggressively than McKay's canonical
  augmentation. Whether that method's acceptance test admits short witnesses is
  the natural next question.
- The trusted base is small but not zero: it is `occheck.c`. Reducing it further
  means porting the checker to a proof assistant — see `docs/theory.md` §8.

## License

MIT.

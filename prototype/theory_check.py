"""
Empirical validation of the two lemmas the certified-enumeration design rests on.

Encoding: a graph G on vertex set [k] is encoded as the concatenation, for
j = 1..k-1, of its j-th "column" (G[0][j], G[1][j], ..., G[j-1][j]).
This makes the code of an induced subgraph on [m] a strict PREFIX of the code
of G, which is what makes orderly generation work.

LEMMA 1 (prefix-heredity): if G on [k] is lex-minimal in its isomorphism class,
                           then G induced on [k-1] is lex-minimal in ITS class.
LEMMA 2 (completeness):    every isomorphism class of graphs on [n] closed under
                           a hereditary constraint is reachable by a root-to-leaf
                           path consisting entirely of lex-minimal graphs.
"""
from itertools import permutations, combinations


def code(adj, k):
    """Prefix-structured code: column j = edges from {0..j-1} to j."""
    return tuple(adj[i][j] for j in range(1, k) for i in range(j))


def apply_perm(adj, k, p):
    """Relabel: new graph H with H[p[u]][p[v]] = G[u][v]."""
    H = [[0] * k for _ in range(k)]
    for u in range(k):
        for v in range(u + 1, k):
            H[p[u]][p[v]] = H[p[v]][p[u]] = adj[u][v]
    return H


def is_lexmin(adj, k):
    c = code(adj, k)
    for p in permutations(range(k)):
        if code(apply_perm(adj, k, p), k) < c:
            return False
    return True


def witness(adj, k):
    """Return a permutation proving non-minimality, or None if lex-minimal."""
    c = code(adj, k)
    for p in permutations(range(k)):
        if code(apply_perm(adj, k, p), k) < c:
            return p
    return None


def induced(adj, m):
    return [row[:m] for row in adj[:m]]


def all_graphs(k):
    pairs = list(combinations(range(k), 2))
    for mask in range(1 << len(pairs)):
        adj = [[0] * k for _ in range(k)]
        for b, (u, v) in enumerate(pairs):
            if mask >> b & 1:
                adj[u][v] = adj[v][u] = 1
        yield adj


print("LEMMA 1 — prefix-heredity of lex-minimality")
print("  (if G is lex-min on k vertices, G[0..k-2] is lex-min on k-1 vertices)")
for k in range(2, 7):
    checked = viol = lexmin_ct = 0
    for adj in all_graphs(k):
        if is_lexmin(adj, k):
            lexmin_ct += 1
            checked += 1
            if not is_lexmin(induced(adj, k - 1), k - 1):
                viol += 1
    total = 1 << (k * (k - 1) // 2)
    print(f"  k={k}: {total:>6} labelled graphs, {lexmin_ct:>4} lex-minimal, "
          f"{checked:>4} checked, violations={viol}  {'OK' if viol == 0 else 'FAIL'}")

print()
print("LEMMA 1b — lex-min representatives are exactly one per isomorphism class")
for k in range(2, 7):
    classes = {}
    for adj in all_graphs(k):
        best = min(code(apply_perm(adj, k, p), k) for p in permutations(range(k)))
        classes.setdefault(best, 0)
        classes[best] += 1
    nlexmin = sum(1 for adj in all_graphs(k) if is_lexmin(adj, k))
    print(f"  k={k}: iso classes={len(classes):>4}  lex-min graphs={nlexmin:>4}  "
          f"{'OK' if len(classes) == nlexmin else 'FAIL'}")

print()
print("LEMMA 2 — completeness of orderly search under a hereditary constraint")
print("  constraint: triangle-free (K3-free). Orderly search must find every")
print("  triangle-free isomorphism class on n vertices.")


def triangle_free(adj, k):
    return not any(adj[a][b] and adj[a][c] and adj[b][c]
                   for a, b, c in combinations(range(k), 3))


def orderly(n):
    """Grow lex-min, triangle-free graphs one vertex at a time."""
    level = [[[0]]]  # the single graph on 1 vertex
    for k in range(1, n):
        nxt = []
        for adj in level:
            for mask in range(1 << k):
                H = [row[:] + [0] for row in adj] + [[0] * (k + 1)]
                for i in range(k):
                    if mask >> i & 1:
                        H[i][k] = H[k][i] = 1
                if triangle_free(H, k + 1) and is_lexmin(H, k + 1):
                    nxt.append(H)
        level = nxt
    return level


for n in range(2, 8):
    found = orderly(n)
    # ground truth: brute-force count of triangle-free isomorphism classes
    truth = set()
    for adj in all_graphs(n):
        if triangle_free(adj, n):
            truth.add(min(code(apply_perm(adj, n, p), n) for p in permutations(range(n))))
    ok = len(found) == len(truth) and {code(g, n) for g in found} == truth
    print(f"  n={n}: orderly found {len(found):>4}, brute force {len(truth):>4}  "
          f"{'OK' if ok else 'FAIL'}")

print()
print("WITNESS CHECK — every pruned graph has a 1-permutation certificate")
bad = 0
for k in range(2, 7):
    for adj in all_graphs(k):
        w = witness(adj, k)
        if w is None:
            continue
        # the witness must genuinely produce a lex-smaller code
        if not code(apply_perm(adj, k, w), k) < code(adj, k):
            bad += 1
print(f"  invalid witnesses across k=2..6: {bad}  {'OK' if bad == 0 else 'FAIL'}")

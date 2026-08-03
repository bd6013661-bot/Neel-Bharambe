/*
 * ocgen -- certifying orderly generator for hereditary graph properties.
 *
 * Enumerates one representative of every isomorphism class of graphs with a
 * hereditary property, growing one vertex at a time and keeping only graphs that
 * are lexicographically minimal in their class (see docs/theory.md).  As it
 * runs it streams a certificate that `occheck` can verify without repeating any
 * of the search.
 *
 * This program is deliberately NOT trusted.  It may be as clever, as heuristic
 * and as fast as it likes: every pruning decision it makes must be accompanied
 * by a permutation witness, and a wrong or missing witness is caught by the
 * checker.  The worst a bug here can do is make the search slower or the
 * certificate rejected -- never make a false claim believed.
 *
 * Usage:
 *   ocgen --ramsey S T --order N [--proof FILE] [--graphs FILE] [--quiet]
 *
 * Exit: 0 = the search completed (see the summary for what it found).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 64

typedef uint64_t u64;

/* ------------------------------------------------------------------ *
 * Graphs                                                              *
 * ------------------------------------------------------------------ */

typedef struct { u64 row[MAXN]; int n; } Graph;

static void g_extend(const Graph *src, u64 mask, Graph *dst)
{
    int k = src->n, u;
    memcpy(dst->row, src->row, (size_t)k * sizeof(u64));
    for (u = 0; u < k; u++)
        if (mask >> u & 1) dst->row[u] |= (u64)1 << k;
    dst->row[k] = mask;
    dst->n = k + 1;
}

/* ------------------------------------------------------------------ *
 * Canonicity: search for a relabelling with a smaller code            *
 * ------------------------------------------------------------------ */

/*
 * A relabelling is a sequence v_0, ..., v_{n-1} of original vertices, where v_i
 * receives new label i.  Column d of the resulting code is
 *
 *     ( adj(v_0, v_d), adj(v_1, v_d), ..., adj(v_{d-1}, v_d) )
 *
 * read with v_0 most significant, so after fixing a prefix the code's leading
 * columns are determined and can be compared against the target incrementally.
 *
 * At each depth we take the minimum achievable column:
 *   - strictly below the target  -> every completion beats it: witness found;
 *   - strictly above the target  -> no completion can catch up: branch dead;
 *   - equal                      -> still tied, recurse on each vertex achieving it.
 *
 * Only tied branches survive, and those correspond to partial automorphisms, of
 * which there are usually very few.
 */

typedef struct {
    const Graph *g;
    int n;
    u64 target[MAXN];      /* target[d] = column d of the graph's own code */
    int chosen[MAXN];
    int perm[MAXN];        /* filled in when a witness is found */
    long long budget;      /* node budget; <= 0 means unlimited */
    long long spent;
    int found;
} CanonSearch;

static u64 column_of(const CanonSearch *cs, int v, int d)
{
    u64 col = 0;
    int i;
    for (i = 0; i < d; i++)
        col = (col << 1) | (cs->g->row[cs->chosen[i]] >> v & 1);
    return col;
}

/* Complete a winning prefix into a full permutation and record it. */
static void emit_witness(CanonSearch *cs, int v, int d)
{
    int i, next = d + 1;
    unsigned char used[MAXN];
    memset(used, 0, sizeof used);
    for (i = 0; i < d; i++) { cs->perm[cs->chosen[i]] = i; used[cs->chosen[i]] = 1; }
    cs->perm[v] = d; used[v] = 1;
    for (i = 0; i < cs->n; i++)
        if (!used[i]) cs->perm[i] = next++;
    cs->found = 1;
}

static void canon_search(CanonSearch *cs, int d, u64 usedmask)
{
    if (cs->found) return;
    if (d == cs->n) return;                 /* a full tie: an automorphism */
    if (cs->budget > 0 && cs->spent >= cs->budget) return;
    cs->spent++;

    int v, n = cs->n;
    u64 best = ~(u64)0;
    for (v = 0; v < n; v++) {
        if (usedmask >> v & 1) continue;
        u64 col = column_of(cs, v, d);
        if (col < best) best = col;
    }
    if (best == ~(u64)0) return;            /* nothing left to place */

    if (d > 0) {
        if (best < cs->target[d]) {
            for (v = 0; v < n; v++)
                if (!(usedmask >> v & 1) && column_of(cs, v, d) == best) {
                    emit_witness(cs, v, d);
                    return;
                }
        }
        if (best > cs->target[d]) return;   /* dead: cannot tie or beat */
    }

    for (v = 0; v < n && !cs->found; v++) {
        if (usedmask >> v & 1) continue;
        if (d > 0 && column_of(cs, v, d) != cs->target[d]) continue;
        cs->chosen[d] = v;
        canon_search(cs, d + 1, usedmask | (u64)1 << v);
    }
}

/*
 * Returns 1 and fills perm[] with a code-shrinking permutation, or 0 when none
 * was found.  A 0 does not prove canonicity when a budget is in force -- and it
 * does not need to: retaining a non-canonical graph costs work, never
 * correctness (docs/theory.md, Proposition 5.1).
 */
static int find_smaller(const Graph *g, int *perm, long long budget)
{
    CanonSearch cs;
    int d, i;
    cs.g = g; cs.n = g->n; cs.budget = budget; cs.spent = 0; cs.found = 0;
    for (d = 1; d < g->n; d++) {
        u64 col = 0;
        for (i = 0; i < d; i++) col = (col << 1) | (g->row[i] >> d & 1);
        cs.target[d] = col;
    }
    canon_search(&cs, 0, 0);
    if (cs.found) memcpy(perm, cs.perm, (size_t)g->n * sizeof(int));
    return cs.found;
}

/* ------------------------------------------------------------------ *
 * The Ramsey property                                                  *
 * ------------------------------------------------------------------ */

static int has_clique(const Graph *g, u64 cand, int need)
{
    if (need <= 0) return 1;
    if (__builtin_popcountll(cand) < need) return 0;
    while (cand) {
        u64 low = cand & (~cand + 1);
        int v = __builtin_ctzll(low);
        if (has_clique(g, cand & g->row[v] & ~((low << 1) - 1), need - 1)) return 1;
        cand &= ~low;
        if (__builtin_popcountll(cand) < need) return 0;
    }
    return 0;
}

static int has_indep(const Graph *g, u64 cand, int need)
{
    if (need <= 0) return 1;
    if (__builtin_popcountll(cand) < need) return 0;
    while (cand) {
        u64 low = cand & (~cand + 1);
        int v = __builtin_ctzll(low);
        if (has_indep(g, cand & ~g->row[v] & ~((low << 1) - 1), need - 1)) return 1;
        cand &= ~low;
        if (__builtin_popcountll(cand) < need) return 0;
    }
    return 0;
}

static int R_S = 3, R_T = 3;

static int admits(const Graph *g, u64 mask)
{
    u64 all = (g->n >= 64) ? ~(u64)0 : (((u64)1 << g->n) - 1);
    if (has_clique(g, mask, R_S - 1)) return 0;
    if (has_indep(g, all & ~mask, R_T - 1)) return 0;
    return 1;
}

/* ------------------------------------------------------------------ *
 * Orderly generation with certificate emission                         *
 * ------------------------------------------------------------------ */

static FILE *proof_out = NULL;
static FILE *graph_out = NULL;
static int target_order = 6;
static long long canon_budget = 0;

static long long stat_nodes = 0, stat_witnesses = 0, stat_prejects = 0;
static long long level_count[MAXN + 1];
static long long found_at_target = 0;

static void write_graph6(FILE *fh, const Graph *g)
{
    int k = g->n, i, j, nb = 0, val = 0;
    fputc(k + 63, fh);
    for (j = 1; j < k; j++)
        for (i = 0; i < j; i++) {
            val = (val << 1) | (int)(g->row[i] >> j & 1);
            if (++nb == 6) { fputc(val + 63, fh); nb = 0; val = 0; }
        }
    if (nb) { fputc((val << (6 - nb)) + 63, fh); }
    fputc('\n', fh);
}

static void visit(const Graph *g)
{
    int k = g->n, i;
    stat_nodes++;
    level_count[k]++;

    if (k == target_order) {
        found_at_target++;
        if (graph_out) write_graph6(graph_out, g);
        return;
    }

    u64 lim = (u64)1 << k;
    u64 mask;
    /* Accepted masks are buffered so that all witnesses for this node are
     * written before the first descent, which lets the checker account for the
     * whole node in a single pass. */
    u64 *accepted = malloc((size_t)lim * sizeof(u64));
    if (!accepted) { fprintf(stderr, "out of memory at depth %d\n", k); exit(3); }
    size_t naccept = 0;
    int perm[MAXN];

    for (mask = 0; mask < lim; mask++) {
        if (!admits(g, mask)) { stat_prejects++; continue; }
        Graph child;
        g_extend(g, mask, &child);
        if (find_smaller(&child, perm, canon_budget)) {
            stat_witnesses++;
            if (proof_out) {
                fprintf(proof_out, "X %llx", (unsigned long long)mask);
                for (i = 0; i <= k; i++) fprintf(proof_out, " %d", perm[i]);
                fputc('\n', proof_out);
            }
        } else {
            accepted[naccept++] = mask;
        }
    }

    if (proof_out && naccept == 0) fprintf(proof_out, "empty %d\n", k);

    for (size_t a = 0; a < naccept; a++) {
        Graph child;
        g_extend(g, accepted[a], &child);
        if (proof_out) fprintf(proof_out, "D %llx\n", (unsigned long long)accepted[a]);
        visit(&child);
        if (proof_out) fputs("U\n", proof_out);
    }
    free(accepted);
}

int main(int argc, char **argv)
{
    const char *proof_path = NULL, *graph_path = NULL;
    int quiet = 0, i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--ramsey") && i + 2 < argc) {
            R_S = atoi(argv[++i]); R_T = atoi(argv[++i]);
        } else if (!strcmp(argv[i], "--order") && i + 1 < argc) {
            target_order = atoi(argv[++i]);
        } else if (!strcmp(argv[i], "--proof") && i + 1 < argc) {
            proof_path = argv[++i];
        } else if (!strcmp(argv[i], "--graphs") && i + 1 < argc) {
            graph_path = argv[++i];
        } else if (!strcmp(argv[i], "--budget") && i + 1 < argc) {
            canon_budget = atoll(argv[++i]);
        } else if (!strcmp(argv[i], "--quiet")) {
            quiet = 1;
        } else {
            fprintf(stderr,
                "usage: %s --ramsey S T --order N [--proof FILE] [--graphs FILE]\n"
                "          [--budget NODES] [--quiet]\n", argv[0]);
            return 2;
        }
    }
    if (R_S < 2 || R_T < 2) { fprintf(stderr, "ramsey parameters must be >= 2\n"); return 2; }
    if (target_order < 1 || target_order > MAXN) {
        fprintf(stderr, "order must be in 1..%d\n", MAXN); return 2;
    }

    if (proof_path && !(proof_out = fopen(proof_path, "w"))) { perror(proof_path); return 2; }
    if (graph_path && !(graph_out = fopen(graph_path, "w"))) { perror(graph_path); return 2; }

    if (proof_out) {
        fprintf(proof_out, "orbitcert-proof 1\n");
        fprintf(proof_out, "problem ramsey s=%d t=%d\n", R_S, R_T);
        fprintf(proof_out, "order %d\n", target_order);
        fprintf(proof_out, "root 0\n");
    }

    Graph root;
    memset(root.row, 0, sizeof root.row);
    root.n = 1;

    clock_t t0 = clock();
    visit(&root);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;

    if (proof_out) {
        fprintf(proof_out, "qed %lld %lld\n", stat_nodes, stat_witnesses);
        fclose(proof_out);
    }
    if (graph_out) fclose(graph_out);

    if (!quiet) {
        printf("problem: (K%d, I%d)-free graphs, target order %d\n", R_S, R_T, target_order);
        printf("counts by order:");
        for (i = 1; i <= target_order; i++) printf(" %lld", level_count[i]);
        printf("\n");
        if (found_at_target == 0)
            printf("RESULT: no such graph on %d vertices -> R(%d,%d) <= %d\n",
                   target_order, R_S, R_T, target_order);
        else
            printf("RESULT: %lld graph(s) on %d vertices -> R(%d,%d) > %d\n",
                   found_at_target, target_order, R_S, R_T, target_order);
        printf("nodes=%lld witnesses=%lld property-rejects=%lld time=%.2fs\n",
               stat_nodes, stat_witnesses, stat_prejects, secs);
    }
    return 0;
}

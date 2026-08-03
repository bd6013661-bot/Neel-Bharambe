/*
 * occheck -- independent checker for orbitcert certificates.
 *
 * This is the trusted base of the whole system, so it is written to be read.
 * It has no dependencies beyond the C standard library, allocates nothing that
 * is not bounded by the proof's declared order, performs no search of any kind,
 * and implements Theorem 4.4 of docs/theory.md clause by clause:
 *
 *   a certificate is accepted exactly when it is rooted at the one-vertex
 *   graph, every node it visits accounts for all 2^k candidate extensions,
 *   every canonicity witness verifies, and no node is reached at the target
 *   order.
 *
 * Deliberately absent: canonical forms, permutation search, graph isomorphism,
 * heuristics, and optimisation that would obscure the correspondence with the
 * theorem. Its cost per node is one property test per candidate plus O(k^2)
 * per witness -- strictly less than the generator, which had to *find* those
 * witnesses.
 *
 * Usage:  occheck < proof
 *         occheck proof-file
 * Exit:   0 = VERIFIED, 1 = REJECTED, 2 = usage/IO error.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>

#define MAXN 64

typedef uint64_t u64;

/* ------------------------------------------------------------------ *
 * Graphs: rows[u] has bit v set iff {u,v} is an edge.                 *
 * ------------------------------------------------------------------ */

typedef struct { u64 row[MAXN]; int n; } Graph;

static void g_init1(Graph *g) { memset(g->row, 0, sizeof g->row); g->n = 1; }

/* Append a vertex joined to the vertices selected by `mask`. */
static void g_extend(const Graph *src, u64 mask, Graph *dst)
{
    int k = src->n, u;
    memcpy(dst->row, src->row, sizeof dst->row);
    for (u = 0; u < k; u++)
        if (mask >> u & 1) dst->row[u] |= (u64)1 << k;
    dst->row[k] = mask;
    dst->n = k + 1;
}

/* Apply a permutation: result has H[p[u]][p[v]] == G[u][v]. */
static void g_relabel(const Graph *g, const int *p, Graph *out)
{
    int n = g->n, u, v;
    memset(out->row, 0, sizeof out->row);
    out->n = n;
    for (u = 0; u < n; u++)
        for (v = u + 1; v < n; v++)
            if (g->row[u] >> v & 1) {
                out->row[p[u]] |= (u64)1 << p[v];
                out->row[p[v]] |= (u64)1 << p[u];
            }
}

/*
 * Compare codes: the strict upper triangle read column by column, with vertex 0
 * most significant within each column. Returns <0, 0, >0 like memcmp.
 * Both graphs must have the same order.
 */
static int code_cmp(const Graph *a, const Graph *b)
{
    int n = a->n, j, i, x, y;
    for (j = 1; j < n; j++)
        for (i = 0; i < j; i++) {
            x = (int)(a->row[i] >> j & 1);
            y = (int)(b->row[i] >> j & 1);
            if (x != y) return x - y;
        }
    return 0;
}

/* ------------------------------------------------------------------ *
 * Hereditary properties. Only the Ramsey family is needed so far; each *
 * new family adds one incremental test and nothing else.               *
 * ------------------------------------------------------------------ */

static int popcount_u64(u64 x) { return __builtin_popcountll(x); }

/* Does the subgraph induced on `cand` contain a clique of `need` vertices? */
static int has_clique(const Graph *g, u64 cand, int need)
{
    if (need <= 0) return 1;
    if (popcount_u64(cand) < need) return 0;
    while (cand) {
        u64 low = cand & (~cand + 1);
        int v = __builtin_ctzll(low);
        /* Only later vertices adjacent to v can extend this clique. */
        u64 next = cand & g->row[v] & ~((low << 1) - 1);
        if (has_clique(g, next, need - 1)) return 1;
        cand &= ~low;
        if (popcount_u64(cand) < need) return 0;
    }
    return 0;
}

/* Does the subgraph induced on `cand` contain `need` pairwise non-adjacent vertices? */
static int has_indep(const Graph *g, u64 cand, int need)
{
    if (need <= 0) return 1;
    if (popcount_u64(cand) < need) return 0;
    while (cand) {
        u64 low = cand & (~cand + 1);
        int v = __builtin_ctzll(low);
        u64 next = cand & ~g->row[v] & ~((low << 1) - 1);
        if (has_indep(g, next, need - 1)) return 1;
        cand &= ~low;
        if (popcount_u64(cand) < need) return 0;
    }
    return 0;
}

typedef struct { int s, t; } Ramsey;

/*
 * Adding a vertex with neighbourhood `mask` keeps the (s,t)-Ramsey property iff
 * its neighbourhood holds no K_{s-1} and its non-neighbourhood holds no
 * independent (t-1)-set: any new forbidden configuration must use the new vertex.
 */
static int ramsey_admits(const Ramsey *r, const Graph *g, u64 mask)
{
    u64 all = (g->n == 64) ? ~(u64)0 : (((u64)1 << g->n) - 1);
    if (has_clique(g, mask, r->s - 1)) return 0;
    if (has_indep(g, all & ~mask, r->t - 1)) return 0;
    return 1;
}

/* ------------------------------------------------------------------ *
 * Certificate checking                                                 *
 * ------------------------------------------------------------------ */

static void reject(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    fputs("REJECTED: ", stdout);
    vprintf(fmt, ap);
    fputc('\n', stdout);
    va_end(ap);
    exit(1);
}

int main(int argc, char **argv)
{
    FILE *in = stdin;
    if (argc > 2) { fprintf(stderr, "usage: occheck [proof-file]\n"); return 2; }
    if (argc == 2 && !(in = fopen(argv[1], "r"))) { perror(argv[1]); return 2; }

    char line[1 << 16];
    int version = -1, order = -1, have_root = 0, closed = 0;
    Ramsey prop = { 0, 0 };
    int have_prop = 0;

    /* DFS state: the chain of graphs from the root to the current node, and for
     * each, the set of candidate masks already accounted for. */
    static Graph stack[MAXN + 1];
    static unsigned char *seen[MAXN + 1];
    int depth = -1;

    long long nodes = 0, witnesses = 0, rederived = 0;
    int reached_target = 0;

    while (fgets(line, sizeof line, in)) {
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || *p == '\0') continue;

        if (version < 0) {
            if (sscanf(p, "orbitcert-proof %d", &version) != 1 || version != 1)
                reject("bad magic or unsupported version");
            continue;
        }

        if (!strncmp(p, "problem ", 8)) {
            char name[64];
            if (sscanf(p + 8, "%63s", name) != 1) reject("malformed problem record");
            if (strcmp(name, "ramsey")) reject("unknown problem '%s'", name);
            char *s = strstr(p, "s="), *t = strstr(p, "t=");
            if (!s || !t) reject("ramsey problem needs s= and t=");
            prop.s = atoi(s + 2); prop.t = atoi(t + 2);
            if (prop.s < 2 || prop.t < 2) reject("ramsey parameters must be >= 2");
            have_prop = 1;
        } else if (!strncmp(p, "order ", 6)) {
            order = atoi(p + 6);
            if (order < 1 || order > MAXN) reject("order out of range: %d", order);
        } else if (!strncmp(p, "root ", 5)) {
            if (!have_prop || order < 0) reject("root before problem/order header");
            if (strtoull(p + 5, NULL, 16) != 0) reject("root must be the one-vertex graph");
            depth = 0;
            g_init1(&stack[0]);
            seen[0] = calloc(1, 1);            /* 2^0 candidate masks at the root */
            if (!seen[0]) reject("out of memory");
            have_root = 1;
            nodes++;
            if (order == 1) reached_target = 1;
        } else if (*p == 'X') {
            if (!have_root) reject("witness before root");
            u64 mask; int perm[MAXN + 1], i, k = stack[depth].n;
            char *end;
            mask = strtoull(p + 1, &end, 16);
            if (k < MAXN && mask >> k) reject("witness mask names vertices outside the node");
            if (seen[depth][mask]) reject("mask %llx accounted for twice at depth %d",
                                          (unsigned long long)mask, k);
            if (!ramsey_admits(&prop, &stack[depth], mask))
                reject("depth %d: canonicity witness for mask %llx, which already "
                       "fails the property", k, (unsigned long long)mask);
            /* Read the permutation of 0..k (the child has k+1 vertices). */
            unsigned char used[MAXN + 1];
            memset(used, 0, sizeof used);
            for (i = 0; i <= k; i++) {
                perm[i] = (int)strtol(end, &end, 10);
                if (perm[i] < 0 || perm[i] > k || used[perm[i]])
                    reject("depth %d: witness for mask %llx is not a permutation",
                           k, (unsigned long long)mask);
                used[perm[i]] = 1;
            }
            Graph child, moved;
            g_extend(&stack[depth], mask, &child);
            g_relabel(&child, perm, &moved);
            if (code_cmp(&moved, &child) >= 0)
                reject("depth %d: witness for mask %llx does not produce a "
                       "lexicographically smaller code", k, (unsigned long long)mask);
            seen[depth][mask] = 1;
            witnesses++;
        } else if (*p == 'D') {
            if (!have_root) reject("descend before root");
            int k = stack[depth].n;
            if (k >= order) reject("descend past the target order");
            u64 mask = strtoull(p + 1, NULL, 16);
            if (k < MAXN && mask >> k) reject("descend mask names vertices outside the node");
            if (seen[depth][mask]) reject("mask %llx accounted for twice at depth %d",
                                          (unsigned long long)mask, k);
            if (!ramsey_admits(&prop, &stack[depth], mask))
                reject("depth %d: descended into mask %llx, which violates the property",
                       k, (unsigned long long)mask);
            seen[depth][mask] = 1;
            g_extend(&stack[depth], mask, &stack[depth + 1]);
            depth++;
            if (stack[depth].n < order) {
                size_t sz = (size_t)1 << stack[depth].n;
                seen[depth] = calloc(sz, 1);
                if (!seen[depth]) reject("out of memory at depth %d", stack[depth].n);
            } else {
                seen[depth] = NULL;
                reached_target = 1;
            }
            nodes++;
        } else if (*p == 'U') {
            if (depth <= 0) reject("ascend above the root");
            /* Coverage: every candidate mask must have been accounted for. */
            int k = stack[depth].n;
            if (k < order) {
                u64 m, lim = (u64)1 << k;
                for (m = 0; m < lim; m++)
                    if (!seen[depth][m]) {
                        if (ramsey_admits(&prop, &stack[depth], m))
                            reject("depth %d: extension by mask %llx satisfies the property "
                                   "but is neither descended into nor witnessed -- the "
                                   "search has a hole here", k, (unsigned long long)m);
                        rederived++;
                    }
            }
            free(seen[depth]);
            seen[depth] = NULL;
            depth--;
        } else if (!strncmp(p, "empty ", 6)) {
            if (!have_root) reject("empty before root");
            if (atoi(p + 6) != stack[depth].n)
                reject("empty record disagrees with the current depth");
        } else if (!strncmp(p, "qed ", 4)) {
            if (depth != 0) reject("proof ended with %d unclosed node(s)", depth);
            /* The root still needs its coverage check. */
            if (order > 1) {
                u64 m, lim = (u64)1 << stack[0].n;
                for (m = 0; m < lim; m++)
                    if (!seen[0][m]) {
                        if (ramsey_admits(&prop, &stack[0], m))
                            reject("depth %d: root extension by mask %llx is unaccounted for",
                                   stack[0].n, (unsigned long long)m);
                        rederived++;
                    }
            }
            long long dn = 0, dw = 0;
            if (sscanf(p + 4, "%lld %lld", &dn, &dw) != 2) reject("malformed qed record");
            if (dn != nodes) reject("qed declares %lld nodes, checker counted %lld", dn, nodes);
            if (dw != witnesses) reject("qed declares %lld witnesses, checker counted %lld",
                                        dw, witnesses);
            closed = 1;
        } else {
            reject("unknown record: %.32s", p);
        }
    }

    if (!closed) reject("proof stream ended without a qed record");

    /* Reaching the target order means the search *found* a graph there, so the
     * certificate establishes completeness of an enumeration rather than
     * nonexistence. Saying which is which is the checker's job, not the
     * reader's. */
    if (reached_target)
        printf("VERIFIED: the enumeration of (K%d, I%d)-free graphs on %d vertices is "
               "complete; graphs exist at this order, so no nonexistence claim is made\n",
               prop.s, prop.t, order);
    else
        printf("VERIFIED: no (K%d, I%d)-free graph exists on %d vertices, "
               "hence R(%d,%d) <= %d\n", prop.s, prop.t, order, prop.s, prop.t, order);
    printf("  nodes=%lld witnesses-checked=%lld property-rejects-rederived=%lld\n",
           nodes, witnesses, rederived);
    return 0;
}

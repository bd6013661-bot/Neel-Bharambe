# Theory: certified isomorph-free exhaustive generation

This document states and proves the results the implementation depends on. Every
theorem here has a corresponding exhaustive machine check in `tests/`, noted at
the end of each proof.

---

## 1. Setting

Let $\mathcal{G}_k$ denote the set of simple graphs on the labelled vertex set
$[k] = \{0, 1, \dots, k-1\}$. The symmetric group $S_k$ acts on $\mathcal{G}_k$
by relabelling: for $\pi \in S_k$, the graph $G^\pi$ has

$$\{\pi(u), \pi(v)\} \in E(G^\pi) \iff \{u,v\} \in E(G).$$

Two graphs are *isomorphic* when they lie in the same $S_k$-orbit. An
enumeration problem asks for exactly one representative of each orbit satisfying
some property.

### 1.1 The code

**Definition 1.1.** The *code* of $G \in \mathcal{G}_k$ is the binary string

$$c(G) \;=\; \mathrm{col}_1(G) \,\Vert\, \mathrm{col}_2(G) \,\Vert\, \cdots \,\Vert\, \mathrm{col}_{k-1}(G),$$

where $\mathrm{col}_j(G) = \big(A_{0j}, A_{1j}, \dots, A_{j-1,j}\big)$ is the
$j$-th column of the strict upper triangle of the adjacency matrix $A$ of $G$.

So $c(G)$ reads the strict upper triangle **column by column**, and
$|c(G)| = \binom{k}{2}$.

Codes are compared lexicographically with $0 < 1$, written $\preceq$.

**Definition 1.2.** $G$ is *canonical* if $c(G) \preceq c(G^\pi)$ for every
$\pi \in S_k$; that is, $G$ is the lexicographic minimum of its isomorphism
class.

Every orbit contains at least one canonical graph (the minimum exists, the orbit
being finite), and the minimum is unique as a *code*, so:

**Fact 1.3.** The canonical graphs in $\mathcal{G}_k$ are in bijection with the
isomorphism classes of graphs on $k$ vertices.

*Machine-checked:* `tests/test_canon.py::test_canonical_count_matches_oeis_a000088`
counts canonical graphs for $k \le 6$ and matches OEIS A000088 $(1, 2, 4, 11, 34, 156)$.

### 1.2 Why column-major

Write $G[m]$ for the subgraph of $G$ induced on $\{0, \dots, m-1\}$.

**Lemma 1.4 (Prefix property).** For every $G \in \mathcal{G}_k$ and every
$m \le k$, the string $c(G[m])$ is a prefix of $c(G)$.

*Proof.* $c(G[m]) = \mathrm{col}_1 \Vert \cdots \Vert \mathrm{col}_{m-1}$
computed inside $G[m]$. For $j < m$, the $j$-th column of $G[m]$ involves only
the entries $A_{ij}$ with $i < j < m$, which are exactly the entries of
$\mathrm{col}_j(G)$. So the first $\binom{m}{2}$ symbols of $c(G)$ are precisely
$c(G[m])$. $\blacksquare$

This is the one place the column-major choice is used, and everything downstream
rests on it. Row-major order does **not** have the prefix property: deleting the
last vertex shortens every row, so the entries of $c(G)$ are interleaved rather
than truncated, and no prefix relationship survives.

*Machine-checked:* `tests/test_graph.py::test_prefix_property` verifies this for
all graphs on up to 7 vertices.

---

## 2. Prefix-heredity of canonicity

This is the structural theorem that makes orderly generation work.

**Theorem 2.1 (Prefix-heredity).** If $G \in \mathcal{G}_k$ is canonical, then
$G[k-1]$ is canonical in $\mathcal{G}_{k-1}$.

*Proof.* Suppose not. Then there is $\sigma \in S_{k-1}$ with

$$c\big((G[k-1])^{\sigma}\big) \prec c\big(G[k-1]\big). \tag{2.1}$$

Extend $\sigma$ to $\pi \in S_k$ by setting $\pi(v) = \sigma(v)$ for $v < k-1$
and $\pi(k-1) = k-1$. Since $\pi$ fixes $k-1$ and permutes $\{0,\dots,k-2\}$
among themselves, it maps the induced subgraph on the first $k-1$ vertices to
itself as a set, giving

$$(G^{\pi})[k-1] = (G[k-1])^{\sigma}.$$

By Lemma 1.4 applied to both $G$ and $G^\pi$ with $m = k-1$, the first
$\binom{k-1}{2}$ symbols of $c(G^\pi)$ are $c\big((G[k-1])^\sigma\big)$, and the
first $\binom{k-1}{2}$ symbols of $c(G)$ are $c\big(G[k-1]\big)$.

By (2.1) these two prefixes differ, and the first position at which they differ
carries a $0$ in $c(G^\pi)$ and a $1$ in $c(G)$. Lexicographic order is decided
at the first difference, so $c(G^\pi) \prec c(G)$ — contradicting the canonicity
of $G$. $\blacksquare$

*Machine-checked:* `tests/test_search.py::test_every_prefix_of_an_emitted_graph_is_canonical`
verifies that **every** induced prefix of every emitted graph is canonical, for
all $n \le 6$; `prototype/theory_check.py` verifies the theorem directly against
brute force over all labelled graphs for $k \le 6$.

**Remark 2.2.** The converse fails: a canonical graph on $k-1$ vertices generally
has extensions that are not canonical. That is exactly what makes pruning
necessary — and what the certificates account for.

---

## 3. Hereditary properties and completeness

**Definition 3.1.** A graph property $P$ is *hereditary* if it is preserved by
induced subgraphs: $P(G)$ and $H = G[S]$ for $S \subseteq V(G)$ implies $P(H)$.
$P$ must also be isomorphism-invariant.

The relevant example:

**Lemma 3.2.** For fixed $s, t \ge 2$, the property
$$P_{s,t}(G) \;\equiv\; \text{$G$ has no clique of size $s$ and no independent set of size $t$}$$
is hereditary and isomorphism-invariant.

*Proof.* An induced subgraph of $G$ containing a clique of size $s$ would exhibit
that clique in $G$; likewise for independent sets. Isomorphism-invariance is
immediate since cliques and independent sets are defined by adjacency alone.
$\blacksquare$

A graph on $n$ vertices satisfying $P_{s,t}$ is a *Ramsey $(s,t)$-graph*, and its
existence is precisely the statement $R(s,t) > n$.

### 3.1 The search tree

**Definition 3.3.** Given a hereditary property $P$, the *orderly search tree*
$T_P$ has as its nodes at level $k$ the graphs $G \in \mathcal{G}_k$ such that
$G$ is canonical and $P(G)$ holds. The parent of $G$ at level $k$ is $G[k-1]$.

Definition 3.3 is well posed: by Theorem 2.1 the parent is canonical, and by
heredity it satisfies $P$, so the parent really is a node.

**Theorem 3.4 (Completeness).** Let $P$ be hereditary and let $G$ be any graph on
$n$ vertices with $P(G)$. Then the canonical representative of the isomorphism
class of $G$ occurs at level $n$ of $T_P$, and is reachable from the root by
following parents.

*Proof.* Let $G^\star$ be the canonical representative of $[G]$; then $P(G^\star)$
holds by isomorphism-invariance. Applying Theorem 2.1 repeatedly gives that
$G^\star[m]$ is canonical for every $m \le n$, and heredity gives $P(G^\star[m])$
for every $m$. Hence

$$G^\star[1], \; G^\star[2], \; \dots, \; G^\star[n] = G^\star$$

is a chain of nodes of $T_P$ in which each is the parent of the next, starting at
the unique graph on one vertex. $\blacksquare$

**Corollary 3.5 (Nonexistence).** If level $n$ of $T_P$ is empty, then **no**
graph on $n$ vertices satisfies $P$.

*Proof.* Contrapositive of Theorem 3.4. $\blacksquare$

Corollary 3.5 is the engine of every result this system certifies. Specialised
to $P_{s,t}$: if the search reaches level $n$ and finds nothing, then
$R(s,t) \le n$.

*Machine-checked:* `tests/test_search.py` compares the enumeration against
brute force over all labelled graphs ($n \le 5$), against OEIS A000088 and
A006785 ($n \le 8$), and against **nauty** — an independent implementation of a
different algorithm — for all graphs ($n \le 8$), triangle-free graphs
($n \le 9$), and graphs of girth $\ge 5$ ($n \le 8$).

---

## 4. The certificate

The search tree is enormous, and a referee cannot be asked to re-run it. What
they can be asked to do is check a transcript. The design question is: *what is
the least that must be written down?*

### 4.1 The asymmetry

Consider a node $G$ at level $k$ and a candidate extension by a new vertex with
neighbourhood $N \subseteq [k]$, producing $G' \in \mathcal{G}_{k+1}$. The
generator discards $G'$ for one of two reasons.

**(a) $P(G')$ fails.** Deciding this is cheap and deterministic — for
$P_{s,t}$ it is a bounded-depth clique/independent-set search inside $N$ and
$[k] \setminus N$ respectively. A checker can simply redo it.

**(b) $G'$ is not canonical.** Deciding this in the affirmative requires
exhibiting $\pi \in S_{k+1}$ with $c(G'^{\pi}) \prec c(G')$. Deciding it in the
negative requires ruling out all $(k+1)!$ permutations.

The asymmetry is the crux:

> Verifying "$G'$ is not canonical" costs $O(k^2)$ given the permutation.
> Discovering the permutation costs, in the worst case, a search over $(k+1)!$.

So the certificate records **only** the permutations, and only for case (b).
Nothing else is written down, because nothing else is expensive.

**Definition 4.1.** A *rejection witness* for $G'$ is a permutation
$\pi \in S_{k+1}$ with $c(G'^{\pi}) \prec c(G')$.

**Lemma 4.2 (Witness soundness).** If a rejection witness for $G'$ exists, then
$G'$ is not canonical, and the canonical representative of $[G']$ is a distinct
node at the same level.

*Proof.* Immediate from Definition 1.2: $c(G'^\pi) \prec c(G')$ exhibits a
strictly smaller element of the orbit, so $G'$ is not the minimum. The minimum
of the orbit is canonical, satisfies $P$ by invariance, and by Theorem 2.1 its
own prefix chain places it in $T_P$ at level $k+1$. $\blacksquare$

Lemma 4.2 is what makes pruning safe: discarding $G'$ loses nothing, because an
isomorphic copy is retained elsewhere in the tree, and by Theorem 3.4 the subtree
below that copy covers everything the discarded subtree would have.

### 4.2 The coverage condition

A transcript that merely contained valid witnesses would prove nothing: a
dishonest generator could omit an entire subtree and say nothing about it. The
checker therefore enforces a **coverage condition** at every node.

**Definition 4.3.** A transcript *covers* a node $G$ at level $k < n$ if every
one of the $2^{k}$ candidate neighbourhoods $N \subseteq [k]$ is accounted for in
exactly one of three ways:

1. the transcript descends into $N$ (so $G'$ is claimed canonical and $P$-satisfying);
2. the transcript supplies a valid rejection witness for $G'$;
3. the checker itself verifies that $P(G')$ fails.

**Theorem 4.4 (Certificate soundness).** Suppose a transcript

* is rooted at the one-vertex graph,
* covers every node it visits at levels $1, \dots, n-1$,
* has all its rejection witnesses verify, and
* descends into no node at level $n$.

Then no graph on $n$ vertices satisfies $P$.

*Proof.* We show by downward induction that every node of $T_P$ at level $k$ is
visited by the transcript. At level 1 this holds by the rooting condition. Let
$G$ be a node of $T_P$ at level $k+1 \le n$ and let $H = G[k]$ be its parent,
which is a node of $T_P$ at level $k$ by Theorem 2.1 and heredity, hence visited
by induction. Let $N$ be the neighbourhood by which $G$ extends $H$. Since $G$ is
a node of $T_P$, $P(G)$ holds, so possibility 3 of Definition 4.3 is unavailable.
Since $G$ is canonical, no rejection witness for it can exist (Lemma 4.2), so
possibility 2 is unavailable — and any witness offered would fail verification.
By coverage, possibility 1 must apply: the transcript descends into $G$.

Hence every level-$n$ node of $T_P$ is visited. The transcript descends into
none, so level $n$ of $T_P$ is empty, and Corollary 3.5 gives the result.
$\blacksquare$

Theorem 4.4 is the specification the checker implements, clause by clause, in
`src/orbitcert/check.py`.

*Machine-checked:* `tests/test_check.py` corrupts valid certificates in twelve
distinct ways — deleting a witness, deleting a subtree, replacing a permutation
with the identity, supplying a non-bijection, truncating the stream, inflating
the tallies, relabelling the header to a stronger claim, and others — and
asserts that every one is rejected.

### 4.3 What is *not* claimed

Theorem 4.4 certifies **completeness**: nothing was missed. It deliberately does
not certify **irredundancy**: that no two retained graphs are isomorphic.

This is the right trade. Nonexistence results — "$R(s,t) \le n$", "no such design
exists", "the search space is exhausted" — depend only on completeness. Proving
irredundancy would require certifying *non*-isomorphism, which has no short
witness of this kind, and would buy nothing for those claims.

The practical consequence is stated in §5.

---

## 5. One-sided error, and why the canonicity engine need not be trusted

The generator calls a canonicity routine to decide whether to prune. Suppose
that routine is buggy, heuristic, or deliberately truncated by a search budget.

**Proposition 5.1.** Let the generator prune $G'$ only when it has produced a
permutation $\pi$ that it emits as a witness. Then regardless of the canonicity
routine's behaviour:

1. every emitted certificate that the checker accepts implies a true
   nonexistence statement; and
2. the enumeration never loses an isomorphism class.

*Proof.* (1) The checker verifies each $\pi$ from scratch (Definition 4.1) and
enforces coverage; Theorem 4.4 then applies and makes no reference to how $\pi$
was found. (2) If the routine fails to find a witness for a non-canonical $G'$,
the generator retains $G'$ and explores its subtree. By Theorem 3.4 that subtree
is a superset of what was required, so retained output may contain isomorphic
duplicates but cannot omit a class. $\blacksquare$

So errors are strictly one-sided: a defective canonicity engine costs time and
may inflate the output with duplicates, but it can neither produce a false
nonexistence result nor silently drop a graph. This is what allows the generator
to use fast, aggressive, unverified heuristics — including, in principle, an
external tool such as nauty used purely as a witness *source* — while the trusted
base stays confined to the checker.

*Machine-checked:* `tests/test_search.py::test_node_limit_never_loses_graphs`
cripples the canonicity search to a one-node budget and confirms that every
isomorphism class still appears;
`tests/test_search.py::test_node_limit_still_produces_a_verifiable_certificate`
confirms the resulting certificate still verifies;
`tests/test_canon.py::test_node_limit_errs_only_towards_keeping_graphs`
confirms that a truncated search never invents an invalid witness.

---

## 6. Cost

Let $\mathcal{N}$ be the set of nodes visited and let $w$ be the number of
witnesses emitted.

**Generator.** For each node at level $k$ it considers $2^{k}$ candidates. Each
candidate costs a property test plus, when the property holds, a canonicity
search whose worst case is exponential in $k$ (in practice: small, since the
branch-and-bound in `canon.py` prunes as soon as a partial code diverges from the
target).

**Checker.** For each node at level $k$ it considers the same $2^{k}$ candidates,
paying a property test for each, plus $O(k^2)$ for each of the $w$ witnesses. It
performs **no search whatsoever** — no canonical form is computed, no permutation
is looked for.

The gap between the two is exactly the canonicity search, which is the dominant
cost of the generator. Hence:

> Checking is asymptotically cheaper than generating.

Measured (`prototype/benchmark.py`), the ratio of check time to generate time
falls while the search tree is still growing: from $0.144$ to $0.023$ for
triangle-free graphs between $n = 6$ and $n = 9$, a 43-fold advantage, and
similarly for $R(4,4)$ and $R(3,5)$. This is the predicted behaviour — the
canonicity search the checker skips grows faster than the bookkeeping it still
performs.

The ratio is **not** monotone in $n$, and the theory says it should not be. Once
the property becomes unsatisfiable the tree stops growing and further orders add
only empty levels: for $R(3,5)$ the node count is constant at $1{,}029$ from
$n = 13$ onward. The generator's work plateaus while the checker still performs
its per-node coverage sweep over all $2^k$ candidate masks, so the ratio drifts
back up. The advantage therefore tracks *search effort avoided* rather than $n$
itself, which is precisely what §4.1 predicts.

**Certificate size.** One record per emitted witness, each $O(k \log k)$ bytes.
The transcript is written and consumed as a stream, so neither generator nor
checker ever holds it in memory.

---

## 7. Scope and limitations

* **Nonexistence and completeness only.** As noted in §4.3, irredundancy is not
  certified. A count reported by the generator is an upper bound on the number of
  isomorphism classes unless the canonicity engine is assumed correct.
* **Vertex-augmentation only.** The tree grows one vertex at a time, so the
  hereditary property must be with respect to *induced subgraphs*. Properties
  hereditary only under edge deletion need a different augmentation.
* **The trusted base is not zero.** It is the checker: the property test, the
  permutation application, the code comparison, and the coverage loop. That is a
  few hundred lines with no heuristics and no optimisation, which is the point —
  it is small enough to read, and §8 sketches making it smaller still.
* **Orderly generation is not the fastest known enumeration.** McKay's canonical
  augmentation prunes better in practice. §8 discusses the trade.

---

## 8. Open directions

1. **Certifying canonical augmentation.** McKay's method accepts an augmentation
   when the added vertex lies in the canonical orbit of the child. Whether that
   acceptance test admits short witnesses — as the rejection test does here — is
   the natural next question, and would close the performance gap with the
   fastest engines.
2. **A formally verified checker.** The checker's specification is Theorem 4.4,
   which is short and has no analytic content. Transcribing it into Lean 4 or
   CakeML would reduce the trusted base to a proof assistant's kernel.
3. **Beyond graphs.** Nothing in §§1–5 uses graph structure beyond the prefix
   property of the code and heredity of the property. Designs, codes, hypergraphs
   and matrices all admit column-major codes with the prefix property, so the
   same certificate scheme should transfer.
4. **Interfacing with pseudo-Boolean proof logging.** Certificates in this format
   could plausibly be translated into VeriPB's dominance rule, letting a single
   checker validate both SAT-derived and enumeration-derived combinatorial
   results.

# Research Plan — Certified Isomorph-Free Exhaustive Generation

**Working title.** *Certificates for Exhaustive Search: Making Isomorph-Free
Generation Verifiable*

**Candidate ISEF category.** Systems Software → Algorithms (SOFT/ALG), with
Mathematics → Combinatorics & Graph Theory (MATH/CGG) as the alternative. See §9.

---

## 0. Three honest things, before anything else

I want to be straight with you, because a plan that oversells is worse than no
plan.

**1. Nothing guarantees an ISEF qualification.** Not this project, not any
project. Qualification runs through your regional and state fairs, against
whoever else shows up that year, judged by people with their own tastes. What a
project can do is maximise the chance: be genuinely novel, be rigorous, produce a
result that is *checkable on the spot*, and be something you can defend under
questioning. That is what this plan optimises for. Anyone who promises you more
than that is selling something.

**2. ISEF's rules on AI are strict, and this project is exactly the shape that
gets scrutinised.** Generative AI may not write your research plan, your
abstract, or your poster, and may not generate your citations. All AI use must be
disclosed. Violations are disqualifying. What *is* permitted is using AI as an
engineering tool — the same way you'd use a compiler or a library — provided you
say so and provided the intellectual content is yours. Concretely, for this
project: **you must be able to derive the two theorems in §3 on a whiteboard,
unprompted.** They are not hard. They are, in fact, the most beautiful part of
the project, and they are short. But the 25-point interview is the single largest
scoring block on the ISEF rubric, and a student who cannot reconstruct their own
central argument will be found out. §10 sets out the division of labour that
keeps you honest and safe.

**3. The prior-art survey behind this plan is partly unverified.** The research
agents I ran hit an egress policy that blocked most direct page fetches, so a
number of findings come from search summaries rather than full texts, and several
cited arXiv identifiers could not be confirmed to exist. I verified the one that
matters most — LeanSMS — by reading its source directly (§4). **Before you commit
serious time, re-run the prior-art check from an unrestricted machine.** §5,
Phase 0 makes this the first task, and it is not optional.

---

## 1. The research question

> Exhaustive computer searches establish a large fraction of the nonexistence
> results in discrete mathematics. The engines that perform them emit no
> evidence. **Can isomorph-free exhaustive generation be made to produce a
> certificate that an independent, small, auditable checker can verify — without
> re-running the search, and without trusting the search at all?**

And the sharper, quantitative form that makes it a science project rather than a
software project:

> Is checking such a certificate *asymptotically cheaper* than producing it, and
> by how much, measured across a family of instances of growing size?

---

## 2. Why this matters

Take a concrete claim: $R(4,5) = 25$. The upper bound rests on an exhaustive
computer search published by McKay and Radziszowski in 1995. The lower bound is a
graph you can check by hand in an afternoon. The two halves have radically
different epistemic status:

| | evidence a referee can inspect | time to check |
|---|---|---|
| $R(4,5) > 24$ | an explicit 24-vertex graph | seconds |
| $R(4,5) \le 25$ | several thousand lines of 1990s C | ∞ |

This asymmetry is everywhere in combinatorics. Constructions come with witnesses;
nonexistence comes with source code and a request for trust. The SAT community
solved its version of this problem in the 2000s with DRAT proof logging — today
no serious SAT result is published without a machine-checkable proof. **The
enumeration community has no equivalent**, and enumeration is how most of the
classical catalogues were actually computed.

That gap is the project.

### The technical insight

Every step in an orderly-generation search is cheap and deterministic *except
one*: deciding whether a graph is the lexicographic minimum of its isomorphism
class. And that one step has a sharp asymmetry:

- Proving a graph is **not** canonical: exhibit one permutation. Verified in $O(k^2)$.
- Proving a graph **is** canonical: rule out all $k!$ permutations.

The certificate records **only the permutations, only for the rejections**.
Everything else the checker recomputes, because recomputing it is cheaper than
reading it. This is what makes the certificate small, the checker tiny, and
verification cheaper than search.

And there is a second, subtler payoff. Because the generator may only prune when
it *has* a witness, a buggy or deliberately crippled canonicity engine cannot
cause a false result — it can only cause a slow one. The errors are **strictly
one-sided**. That is what lets the generator be fast and untrusted while the
trusted base stays at a few hundred readable lines.

---

## 3. The mathematics

Two theorems, both short, both fully proved in `docs/theory.md`, both verified
exhaustively by machine. **These are the ones you must own.**

**Setup.** Encode a graph on $[k]$ by reading the strict upper triangle of its
adjacency matrix *column by column*. Write $c(G)$ for that bit string and $G[m]$
for the subgraph induced on the first $m$ vertices. The encoding is chosen so
that $c(G[m])$ is a **prefix** of $c(G)$ — deleting the last vertex chops columns
off the end rather than puncturing every row. Row-major order does not have this
property, and the whole construction fails without it.

**Theorem A (prefix-heredity).** *If $G$ is lexicographically minimal in its
isomorphism class, so is $G[k-1]$.*

The proof is four lines: a permutation improving $G[k-1]$ extends, by fixing the
last vertex, to one improving the *prefix* of $c(G)$ — and lexicographic order is
decided at the first difference.

**Theorem B (completeness).** *For a hereditary property $P$, every isomorphism
class of $n$-vertex graphs with $P$ is reached by a root-to-leaf path in the
pruned search tree.*

Apply Theorem A repeatedly: the canonical representative's whole prefix chain is
canonical, and heredity keeps $P$ along it. So the chain is a path in the tree.
**Corollary: if the search reaches level $n$ and finds nothing, nothing exists.**

**Theorem C (certificate soundness)** — proved in `docs/theory.md` §4.2 — turns
this into a specification for the checker: a certificate is sound iff it is
rooted correctly, every node accounts for all $2^k$ candidate extensions, and
every permutation verifies.

---

## 4. Positioning against prior art

This is the section a judge will press hardest on, so it is the one that has to
be airtight.

**LeanSMS** (`github.com/leansolving/leansms`) is the closest work and the real
competitor. I read its source. It compiles graph properties to CNF with
Lean-verified encodings, runs SAT-modulo-symmetries, and checks the LRAT proof in
Lean 4 — genuinely impressive, with the strongest possible trust story. Its
shipped verified theorems are:

| LeanSMS theorem | size |
|---|---|
| Turán: $ex(7, C_4) \le 6$ | $n = 7$ |
| Murty–Simon | $n = 5$ |
| No 3-regular girth-5 graph | $n = 8$ |

It requires Lean, Mathlib, SMS, CaDiCaL, LRAT and `native_decide`.

**The niche is clear.** LeanSMS buys maximal trust at toy scale with a heavy
dependency stack. This project buys near-minimal trust (a ~300-line C checker, no
solver, no proof assistant, no dependencies) at substantially larger scale.
Already, today, the prototype certifies $R(3,5) \le 14$ — a 14-vertex exhaustive
result, roughly twice the vertex count of anything LeanSMS ships — and the
certificate verifies in 1.4 seconds.

They are complementary, not competing, and §5 Phase 4 proposes the synthesis:
port the checker into Lean 4 and get both. That is tractable precisely because
this checker's specification (Theorem C) is a page of combinatorics with no
analytic content, whereas verifying a CNF *encoding* is a large undertaking.

**Other prior art, and why it doesn't close the gap:**

- **SAT + DRAT/LRAT** (Heule et al.). Certifies SAT-based search. Symmetry is the
  bottleneck: $R(4,4) \le 18$ is 153 variables and an 8.4 MB DRAT proof, and this
  is near the practical frontier for the family. Schur number five needed ~2 PB.
- **SMS** (Kirchweger & Szeider). Dynamic symmetry breaking inside the solver;
  fast, but the enumeration itself is not certified without the Lean layer above.
- **nauty / canonical augmentation** (McKay). The performance benchmark —
  ~3.5 million isomorphism classes per second on this hardware — and emits no
  certificate whatsoever. Used here as an *independent oracle* for cross-checking.
- **VeriPB** pseudo-Boolean proof logging with dominance rules. Certifies
  symmetry breaking in a solver context; certifying *isomorph-free generation* is
  a different object.
- **PAG** (Krcadinac, GAP). Automates Kramer–Mesner prescribed-group search. This
  is why the project does **not** claim "automated group selection" as a novelty —
  that idea is already shipped, and an earlier draft of this plan was killed on
  exactly that point.

---

## 5. The plan

Phases are ordered so that **the risky things fail early**, and so that a
presentable result exists from Phase 2 onward regardless of what any search finds.

### Phase 0 — Verify the ground (first, and non-negotiable)

- Re-run the prior-art check from an unrestricted network. Read the LeanSMS paper
  and repo in full; read the CP 2026 proof-logging-for-enumeration work in full.
- Email Stanisław Radziszowski (maintainer of the *Small Ramsey Numbers* dynamic
  survey) describing the approach and asking whether certified enumeration for
  these values exists. A maintainer's reply is both a sanity check and excellent
  evidence to show a judge.
- **Kill criterion:** if certified isomorph-free generation has been published,
  stop and pivot to the Phase 4 synthesis as the primary contribution.

### Phase 1 — Theory *(done)*

Theorems A, B, C stated and proved; every one machine-checked exhaustively at
small sizes. `docs/theory.md`, `prototype/theory_check.py`.

### Phase 2 — Reference implementation *(done)*

Python package (`src/orbitcert/`): graph codes, canonicity engine with witness
extraction, orderly generation with certificate emission, independent checker.
**110 tests passing**, including exact agreement with nauty.

### Phase 3 — Scale

- C generator and C checker *(done — `csrc/`)*. Already ~100× the Python
  reference.
- Certify progressively larger instances. Current status in §6.
- Optimise the canonicity search: cheap transposition pre-filter before the full
  branch-and-bound; invariant-based candidate ordering; parallel subtree search.
- Binary certificate format with streaming compression.

### Phase 4 — The trust ceiling *(stretch)*

Port the checker to Lean 4. The specification is Theorem C. Success means: a
Lean-verified checker that accepts a certificate for a result an order of
magnitude larger than anything currently verified in a proof assistant. This is
the synthesis with LeanSMS, and the single highest-value stretch goal.

### Phase 5 — Generality *(stretch)*

Nothing in Theorems A–C uses graph structure beyond the prefix property and
heredity. Designs, codes, hypergraphs and matrices all admit column-major codes
with the prefix property. Demonstrating the scheme transfers — for instance
re-certifying the 80 Steiner triple systems of order 15 — turns a graph result
into a general method.

---

## 6. Current status — what is already built and verified

This is not a proposal for work that might happen. The core exists, is tested,
and produces verified certificates today.

**Certified results, each verified by two independent checkers (Python and C):**

| Result | Certificate | Generate | Check | Check/generate |
|---|---|---|---|---|
| $R(3,3) \le 6$ | 220 B, 7 witnesses | 0.00 s | 0.00 s | 0.49× |
| $R(3,4) \le 9$ | 3.3 KB, 173 witnesses | 0.00 s | 0.00 s | 0.38× |
| $R(3,5) \le 14$ | 220 KB, 9,060 witnesses | 5.9 s | 1.4 s | **0.24×** |

The falling check/generate ratio is the central empirical claim of §1 showing up
in measurement: as instances grow, the canonicity search the checker *skips*
grows faster than the bookkeeping it still performs. This is the headline graph
for the poster, and it needs more points along the curve.

**Correctness evidence:**

- Critical-graph counts match Radziszowski's survey exactly (1, 3, 1 for
  $R(3,3), R(3,4), R(3,5)$).
- Per-level counts for $R(3,5)$ — 1, 2, 3, 7, 13, 32, 71, 179, 290, 313, 105, 12,
  1 — match McKay's published enumeration.
- Enumeration agrees **exactly with nauty** on all graphs to $n = 8$,
  triangle-free graphs to $n = 9$, and girth-$\ge 5$ graphs to $n = 8$.
- Counts match OEIS A000088 and A006785.
- The C and Python implementations agree to the node, witness and rejection count.

**Adversarial evidence — the part that makes it a proof system rather than a
logger.** Valid certificates are corrupted in twelve ways (delete a witness,
delete a subtree, substitute the identity permutation, supply a non-bijection,
truncate the stream, inflate the tallies, strengthen the header claim, duplicate
a record, …). **Both checkers reject all of them**, with a diagnostic naming the
exact node. This demonstration — corrupt the proof live, watch it get caught — is
the single most persuasive thing you can do at a poster.

---

## 7. Evaluation

The rubric rewards defined variables and controls, so the experiments are
designed as experiments:

1. **Scaling.** Check time vs generate time across a family of instances of
   growing size. Prediction: the ratio decreases. Control: instance family held
   fixed, only $n$ varies.
2. **Certificate size.** Bytes per witness and total size vs $n$. Prediction:
   linear in witnesses, and witnesses grow much more slowly than the search tree.
3. **Robustness (the one-sided-error claim).** Cripple the canonicity engine to a
   fixed node budget and confirm: no isomorphism class is ever lost, certificates
   still verify, cost rises. *Already implemented as a test.*
4. **Soundness.** The twelve-way corruption battery, as an automated suite.
5. **Independent agreement.** Against nauty, OEIS, and the published Ramsey
   literature, at every size where those exist.
6. **Trusted-base size.** Lines of code a sceptic must read, compared with the
   alternatives. This is a real metric and the comparison is favourable.

---

## 8. Risks, honestly

| Risk | Severity | Mitigation |
|---|---|---|
| Someone publishes certified isomorph-free generation first | High | Phase 0 checks now; Phase 4 synthesis is the fallback contribution. This field publishes monthly — re-check before the fair. |
| $R(4,4)$ and larger don't finish on available hardware | Medium | The contribution is the *method and the scaling law*, not any single value. Results at $n = 14$ already exceed the certified state of the art. Report honestly what completed. |
| Lean port (Phase 4) doesn't land | Low | It is explicitly a stretch goal. Phases 1–3 stand alone. |
| Judges see it as "just software" | Medium | Lead with Theorems A–C. Category choice matters — see §9. |
| The prefix-heredity argument has a hole | Low but fatal | Already proved *and* exhaustively machine-checked. Re-derive it yourself from scratch as a check on me. |

**The structural safeguard:** every deliverable in Phases 1–3 exists regardless of
what any search returns. There is no lottery here. Compare this with the
record-chasing projects the adversarial review killed — Costas arrays of order 32,
OGR-29, MOLS(10), Hadwiger–Nelson — where the modal outcome is months of compute
and nothing to show.

---

## 9. ISEF logistics

**Rubric** (100 points): Research Question 10 · Design & Methodology 15 ·
Execution 20 · Creativity 20 · **Presentation 35** (poster 10 + **interview 25**).

Presentation is the largest block and the interview is the largest sub-block.
Plan accordingly: the live corruption demo (§6) is worth more than another table.

**Category.** Systems Software → Algorithms (SOFT/ALG) is the primary
recommendation. Precedent: the 2024 Regeneron Young Scientist Award ($50,000)
went to a project on solving second-order cone programs in matrix-multiplication
time — a pure algorithms-and-complexity result, entered in Systems Software.
That is this project's shape.

Choose Mathematics → Combinatorics/Graph Theory (MATH/CGG) instead if the
finished work leads with Theorems A–C and treats the software as their
instantiation. Note that affiliate guidance describes software as an
oversubscribed field, which cuts slightly toward MATH.

**Paperwork.** Pure computational project, no human or animal subjects, no
hazardous materials: Forms 1, 1A, 1B and a Research Plan. No SRC pre-approval
expected. Confirm with your fair director.

**AI disclosure.** See §0.2. Write the plan, abstract and poster yourself.
Disclose AI-assisted implementation. Keep a logbook from day one — judges use it
specifically to assess what came from the student.

---

## 10. Division of labour

For this to be *your* project in the way ISEF requires:

**Yours, non-negotiably.** The theorems and their proofs — derive Theorem A
yourself before reading mine, it's four lines. Every experimental design choice.
The research plan, abstract and poster. The decision about what to claim and what
to hedge. The Phase 0 literature verification.

**Legitimately AI-assisted, and disclosed.** Implementation of the C and Python
engines, the test harness, the build system, refactoring, documentation drafting.

**A good test:** can you explain, without notes, why column-major encoding is
required and row-major fails? Why over-accepting in the canonicity test is safe
but over-rejecting is fatal? Why the checker rebuilds the property test itself
instead of reading it from the certificate? If yes, the project is yours. Those
three questions are also, almost certainly, what a sharp judge will ask.

---

## 11. Immediate next steps

1. Phase 0 verification (§5) — do this before anything else.
2. Re-derive Theorem A yourself; compare with `docs/theory.md`.
3. Run the test suite: `make -C csrc && python3 -m pytest`.
4. Reproduce the certificates: `./bin/ocgen --ramsey 3 5 --order 14 --proof r.proof && ./bin/occheck r.proof`.
5. Push the scaling curve further and plot it — that curve is the poster.

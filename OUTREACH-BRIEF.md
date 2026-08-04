# Outreach Brief — paste this into a chat to find people to contact

**How to use this file.** Paste the whole thing into a fresh AI chat (one with web
search) and ask it to find researchers to contact, with their public faculty
pages and institutional email addresses. Everything the assistant needs is here:
what the project is, what makes it technically distinctive, who has already been
identified, and what still needs finding. Section 7 is the literal request to
make.

---

## 1. Who I am and what I need

I am a high-school student doing an independent research project for ISEF (the
International Science and Engineering Fair). I have already built and tested a
working research system — this is not a proposal or a plan. I am looking for:

1. a research **mentor** who could advise the project over the next few months, and
2. **experts to sanity-check specific technical questions** by email.

I need names, current institutions, public faculty-page URLs, and public
institutional email addresses. Academic emails are published on faculty pages for
exactly this purpose. I do **not** want guessed or pattern-inferred addresses —
only ones actually listed on a page, with the page cited.

---

## 2. The project in plain language

Mathematicians often prove things like *"no object with these properties
exists"* by having a computer check every possibility exhaustively. That
technique establishes a large share of the known results in discrete mathematics.

The problem: those programs produce **no evidence**. They run for hours and print
"none found," and the only way to check the claim is to read and trust thousands
of lines of someone's optimised C code. Constructions come with a witness you can
verify in seconds; nonexistence comes with source code and a request for trust.

The SAT-solving community fixed its version of this in the 2000s with DRAT proof
logging — no serious SAT result is published now without a machine-checkable
proof. **Exhaustive enumeration has no equivalent**, even though enumeration is
how most of the classical catalogues were actually computed.

I built a system that makes such searches **certifying**: the search emits a
proof as it runs, and a small independent checker replays that proof without
repeating the search and without trusting the search at all.

## 3. The technical core

The system is called **orbitcert**. It performs *orderly generation* — building
combinatorial objects one element at a time, keeping only the lexicographically
minimal representative of each isomorphism class.

The key idea is an asymmetry. Every step in the search is cheap and deterministic
except one: deciding whether an object is the lexicographic minimum of its
isomorphism class. And that step is:

- cheap to **refute** — exhibit one permutation, verified in O(k²);
- expensive to **confirm** — rule out all k! permutations.

So the certificate records **only the permutations, and only for rejections**.
Everything else the checker recomputes, because recomputing is cheaper than
reading. This is what keeps the certificate small and the checker tiny.

This is provably the only possible design: deciding lexicographic-leader status
is **coNP-complete** (a corollary of Babai–Luks 1983 on the NP-hardness of
lex-least canonical forms), so the accepting direction admits no short
certificates unless NP = coNP.

A second consequence: because the generator may only prune when it *holds* a
witness, a buggy or deliberately crippled canonicity engine produces a **slow**
search, never a wrong answer. Errors are strictly one-sided. That is what lets
the trusted base stay at ~300 lines while the generator stays fast and untrusted.

### What is verified and working

| Result | Search nodes | Witnesses | Status |
|---|---|---|---|
| R(3,3) ≤ 6 | 9 | 7 | certified, verified by two independent checkers |
| R(3,4) ≤ 9 | 48 | 173 | certified, verified |
| R(3,5) ≤ 14 | 1,029 | 9,060 | certified, verified |
| R(3,6) ≤ 18 | 761,692 | 9,863,537 | certified, verified (358 MB proof, 152 s check) |
| R(4,4) ≤ 18 | 3,432,184 | 39,065,756 | certified, verified, streamed with zero disk use |

- **194 tests pass.** C and Python implementations agree to the node.
- Enumeration agrees **exactly with nauty** (an independent implementation of a
  different algorithm) on all graphs to n = 8, triangle-free to n = 9, girth ≥ 5
  to n = 8. Counts match OEIS A000088/A006785 and the published Ramsey
  literature, including critical-graph counts.
- **Twelve distinct certificate corruptions** — deleted witnesses, deleted
  subtrees, substituted identity permutations, truncated streams, inflated
  tallies — are all rejected, each naming the exact offending node.
- Checking is measurably cheaper than generating: a 43× advantage for
  triangle-free graphs at n = 9, in the regime where the search tree is growing.

### Honest prior art

The closest existing work is the **MathCheck** project (Curtis Bright, Vijay
Ganesh and collaborators). They published *Verified Certificates via SAT and
Computer Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems* (IJCAI 2025,
arXiv:2502.06055) — **larger Ramsey instances than mine** — and their 2020 paper
*Nonexistence Certificates for Ovals in a Projective Plane of Order Ten*
(arXiv:2001.11974) already couples a SAT solver with nauty for certificate-logged
symmetry breaking.

So my system is not the first certified combinatorial search. What is distinctive:
it certifies the **enumeration itself** rather than a SAT encoding, so it uses **no
solver and no computer algebra system** — the entire trusted base is a ~300-line
dependency-free C program, versus MathCheck's SAT solver plus patched DRAT-trim.
It also measures the check-versus-generate cost asymmetry, which that line of work
does not.

A second related project is **LeanSMS** (github.com/leansolving/leansms), a Lean 4
frontend to SAT-modulo-symmetries producing formally verified impossibility
proofs. Its shipped theorems are at much smaller scale (n = 5 to 8).

## 4. Where the project is going — the actual research question

Re-certifying known Ramsey numbers is a good demonstration but produces no new
mathematics. So the engine is being pointed at a genuinely open problem.

**Target: the Simon–Zilles open problem on recursive teaching dimension versus VC
dimension** (Hans Ulrich Simon and Sandra Zilles, *Open Problem: Recursive
Teaching Dimension Versus VC Dimension*, COLT 2015).

- **VC dimension (VCD)** measures the complexity of a concept class — the central
  quantity in statistical learning theory.
- **Recursive teaching dimension (RTD)** measures how many examples are needed, in
  the worst case, to identify a concept by teaching.
- They appear to track each other, but nobody knows how tightly. **No concept
  class is known with RTD > (3/2)·VCD.** The best general upper bound is quadratic
  (Hu, Wu, Li, Wang, COLT 2017, arXiv:1702.05677).

The concrete instance being attacked: **the maximum RTD over classes of VC
dimension exactly 2 is a single unknown integer.** The lower bound is 3
(Warmuth's class). Nobody knows the true value. Every bound the search certifies
is new by construction.

The reduction: RTD(C) ≥ 4 for some class iff some class D with VCD(D) ≤ 2 has
minimum teaching dimension TDmin(D) ≥ 4 — because VC dimension is monotone under
taking subclasses. So the search enumerates concept classes (0/1 matrices, rows
distinct) up to permutation of the domain, hunting for VCD ≤ 2 with TDmin ≥ 4.

**Current data:** a SAT prototype has exhausted n = 6 entirely (no such class
exists) and n = 7 through m = 27 of a possible 29, on four cores.

**Honest limitation, stated up front:** the ground set is unbounded. Sauer's lemma
bounds the number of concepts in terms of n, but nothing bounds n, so exhausting
n ≤ 9 does not settle the conjecture. The certified statements ("no witness on
≤ N points") are each new, but the real prize is **structure in the extremal
classes** that would suggest an analytic proof.

**Relevant recent work I have read:** Liu and Li, *The No-Clash Teaching Dimension
is Bounded by VC Dimension* (arXiv:2603.23561, April 2026) — a different, smaller
quantity than RTD (NCTD ≤ RTD), so it does not settle the Simon–Zilles problem,
and it is an unrefereed preprint. Also Simon, *RTD-Conjecture and Concept Classes
Induced by Graphs* (arXiv:2502.09453, February 2025), and
Compton–Pabbaraju–Zhivotovskiy, *Lower Bounds for Greedy Teaching Set
Constructions* (COLT 2025, arXiv:2505.03223).

## 5. The fields that define who is relevant

Anyone strongly matching **either** cluster is worth surfacing:

**Cluster A — computational learning theory.** Teaching dimension, recursive
teaching dimension, non-clashing / no-clash teaching, sample compression schemes,
VC dimension combinatorics, maximum and maximal classes, teaching complexity,
COLT/ALT community.

**Cluster B — certified combinatorial search.** Proof logging, DRAT/LRAT, VeriPB
and pseudo-Boolean proofs, certified symmetry breaking, SAT + computer algebra
(SAT+CAS), isomorph-free exhaustive generation, canonical augmentation, orderly
generation, nauty, SAT modulo symmetries, computer-assisted proofs and their
auditing, formal verification of combinatorial results in Lean 4.

## 6. People already identified (do not re-derive these — extend the list)

Affiliations verified as of August 2026 unless noted.

**Tier 1 — highest priority**
- **Hans Ulrich Simon** — Ruhr-Universität Bochum, emeritus since 2020, still
  publishing solo on this exact conjecture. Co-poser of the open problem.
- **Curtis Bright** — University of Waterloo, Cheriton School of Computer Science,
  Associate Professor (teaching stream). **Moved from University of Windsor in
  September 2025 — the Windsor page still resolves and is a dead letter.** Leads
  MathCheck; gave talks titled *SAT + Isomorph-free Generation* and *Auditing
  Computer-Assisted Proofs*.
- **Chirag Pabbaraju** — Stanford CS, PhD student 2021–2026, may have moved.
  Co-author of the COLT 2025 greedy teaching-set lower bound.

**Tier 2**
- **Sandra Zilles** — University of Regina, Tier 1 Canada Research Chair in
  Computational Learning Theory, CIFAR AI Chair at Amii. Co-poser of the problem;
  introduced recursive teaching dimension.
- **Lunjia Hu** — Northeastern University, Khoury College, Assistant Professor
  since Fall 2025. First author of the quadratic RTD upper bound.
- **Nikita Zhivotovskiy** — UC Berkeley, Department of Statistics.

**Tier 3**
- **Marijn Heule** — Carnegie Mellon. Created the DRAT/LRAT tradition.
- **Ciaran McCreesh** — University of Glasgow. Proof logging for constraint
  programming.
- **Jakob Nordström** — University of Copenhagen (also Lund). Created VeriPB.
- **Bart Bogaerts** — KU Leuven (primary), VUB (guest). Certified symmetry breaking.
- **Markus Kirchweger** and **Stefan Szeider** — TU Wien. SAT Modulo Symmetries,
  LeanSMS.
- **Vijay Ganesh** — Georgia Tech (moved from Waterloo in 2023). Co-leads MathCheck.
- **Brendan McKay** — ANU, emeritus. Wrote nauty.
- **Stanisław Radziszowski** — RIT. Maintains the *Small Ramsey Numbers* dynamic
  survey, which accepts contributed bounds from anyone.
- **Shay Moran** — Technion. Sample compression.
- **Manfred Warmuth** — UC Santa Cruz, emeritus. The VCD-2 / RTD-3 example is his.

---

## 7. What I am asking you to do

1. For **every person in section 6**, find their current public faculty page and
   the **institutional email address listed on it**. Cite the page URL you took
   each address from. Flag anyone whose affiliation appears to have changed. Do
   not guess or infer addresses from naming patterns — if an address is not
   publicly listed, say so and give the contact form or department address instead.

2. **Find people I have missed.** Search recent literature (2023–2026) in both
   clusters in section 5 — arXiv listings for math.CO, cs.DM, cs.LO, cs.LG, and
   the proceedings of COLT, ALT, SAT, CP, CADE, IJCAI, AAAI and ITP. I especially
   want: anyone who has published on recursive teaching dimension since 2024;
   anyone working on proof logging for enumeration or model counting; and any
   researcher **geographically near the United States** who works in either
   cluster, since a local mentor is far easier to sustain than a remote one.

3. **Prioritise by likely responsiveness, not seniority.** Emeritus professors and
   senior PhD students reply to cold email at meaningfully higher rates than
   mid-career stars with full labs. Flag which category each person is in.

4. **Find structured programs**, not just individuals: high-school research
   programs with open applications, REU-adjacent opportunities that accept
   pre-university students, and any public research community in these areas that
   welcomes outside contributors (the Lean prover Zulip and the Busy Beaver
   Challenge community are examples of the type).

5. For each person, suggest **one specific technical question** they personally
   could answer in one or two sentences from memory, drawn from their own
   published work. A cold email asking for mentorship outright almost never
   works; a cold email asking one sharp question about the recipient's own paper
   works far better.

**Constraints to respect:** I am in high school and will say so in the first
sentence of any email. I want short, specific, honest emails — never mass-sent
templates. I need accurate current affiliations, because writing to a stale
address signals I did not check.

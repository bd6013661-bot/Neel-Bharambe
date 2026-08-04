# HANDOFF — read this first

This file briefs a fresh Claude Code session (VS Code, desktop) on everything it
needs to continue this project without any prior conversation context. It is the
single source of truth for: what exists, what is verified, what was corrected,
what to build next, and the constraints that must never be violated.

## 0. Getting the code

Everything described below is already committed and pushed. Clone it:

```bash
git clone https://github.com/bd6013661-bot/Neel-Bharambe.git
cd Neel-Bharambe
git checkout claude/isef-cs-project-h1wncp
```

Then set up and confirm the environment is healthy — this should take under a
minute and must be green before any new work starts:

```bash
pip install python-sat pytest pytest-timeout      # numpy/sympy/networkx optional
sudo apt-get install -y nauty                     # for the independent cross-checks
make -C csrc                                      # builds bin/ocgen and bin/occheck
python3 -m pytest -q                              # expect 194 passed
./bin/ocgen --ramsey 3 5 --order 14 --quiet --proof /dev/stdout | ./bin/occheck
# expect: VERIFIED: no (K3, I5)-free graph exists on 14 vertices, hence R(3,5) <= 14
```

If `nauty` is unavailable the cross-check tests skip rather than fail; install it
anyway, because those tests are the strongest correctness evidence in the repo.

---

## 1. What this project is

**orbitcert** — certified isomorph-free exhaustive generation. Exhaustive
searches establish nonexistence results in discrete math ("no such graph exists
on n vertices"), but enumeration engines emit no evidence; checking a result
means trusting thousands of lines of someone's C. This system makes the search
*certifying*: the untrusted generator streams a proof; a ~300-line dependency-free
checker replays it without repeating the search.

The load-bearing idea: in orderly generation every step is cheap except deciding
lexicographic minimality, and that step is cheap to **refute** (one permutation,
verified in O(k²)) but expensive to **confirm** (rule out k!). So the certificate
records only the permutations, only for rejections; the checker recomputes
everything else. Consequence: a buggy canonicity engine yields a slow search,
never a wrong answer — errors are strictly one-sided, so the trusted base stays
tiny. Full theory with proofs: `docs/theory.md` (Theorems 2.1, 3.4, 4.4).

### Verified state (all reproducible)

| Result | Nodes | Witnesses | Status |
|---|---|---|---|
| R(3,3) ≤ 6 | 9 | 7 | certified + verified (C and Python checkers) |
| R(3,4) ≤ 9 | 48 | 173 | certified + verified |
| R(3,5) ≤ 14 | 1,029 | 9,060 | certified + verified |
| R(3,6) ≤ 18 | 761,692 | 9,863,537 | certified + verified (358 MB, 152 s check) |
| R(4,4) ≤ 18 | 3,432,184 | 39,065,756 | certified + verified, streamed, zero disk |

- **194 tests pass** (`python3 -m pytest`, needs `pip install python-sat pytest pytest-timeout`).
- Enumeration agrees **exactly with nauty** (independent implementation, different
  algorithm) on all graphs n ≤ 8, triangle-free n ≤ 9, girth ≥ 5 n ≤ 8; counts
  match OEIS A000088/A006785 and the published Ramsey literature including
  critical-graph counts (7 at n = 17 for R(3,6)).
- **Adversarial suite**: 12 distinct certificate corruptions, all rejected by both
  checkers with a diagnostic naming the exact node (`tests/test_check.py`).
- Scaling: check/generate ratio falls in the growth regime (0.144 → 0.023 for
  triangle-free n = 6→9, a 43× advantage) and rises after saturation. It is NOT
  monotone; `prototype/benchmark.py` separates the regimes. Never quote endpoints.

### Repo map

```
src/orbitcert/    Python reference (graph.py canon.py problems.py search.py proof.py check.py cli.py)
csrc/             ocgen.c (fast untrusted generator), occheck.c (THE TRUSTED BASE), Makefile
docs/theory.md    theorems + proofs, each machine-checked
tests/            194 tests incl. nauty cross-checks and the corruption battery
prototype/        theory_check.py (brute-force lemma validation), benchmark.py, e2e_ramsey.py
prototype/rtd/    the RTD SAT prototype (see §3) — rtd_probe.py, rtd_sweep.py, rtd_sweep.log
results/          small certificates committed; RESULTS.md has the tables
PLAN.md           research plan (prior-art section CORRECTED — see §2)
```

Quick start: `make -C csrc && ./bin/ocgen --ramsey 3 5 --order 14 --quiet --proof /dev/stdout | ./bin/occheck`

---

## 2. The prior-art correction (do not undo this)

The original framing — "enumeration emits no evidence; closest prior art is
LeanSMS at n = 5–8" — was **falsified** by a network-enabled check:

- **MathCheck** (Bright, Ganesh et al.): *Verified Certificates via SAT and
  Computer Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems*,
  **IJCAI 2025** — ijcai.org/proceedings/2025/0292.pdf, arXiv:2502.06055.
  Ahead of this project on headline Ramsey numbers.
- Same group, 2020: *Nonexistence Certificates for Ovals in a Projective Plane of
  Order Ten* (arXiv:2001.11974) — SAT solver coupled **with nauty**, learning
  symmetry-breaking clauses on the fly, certificate-logged.

What survives, and is the only defensible framing: orbitcert is **solver-free
with a ~300-line trusted base** (MathCheck's TCB = SAT solver + CAS coupling +
patched DRAT-trim); it **measures the check-vs-generate asymmetry**; and its
design is **provably optimal** (canonicity is coNP-complete — corollary of
Babai–Luks 1983, cite it, never claim it as new). `PLAN.md` §4 and `README.md`
already say this correctly. Any text claiming novelty over MathCheck is a bug.

**Consequence** (this drove the pivot in §3): eight independent research agents
converged on the same sentence — *the project has not produced a single number
that was not already known*. The instrument is excellent; it must now be pointed
at something unknown.

---

## 3. THE MISSION: the Simon–Zilles RTD problem

### The target

**Open problem** (Simon & Zilles, COLT 2015 — proceedings.mlr.press/v40/Simon15b.html):
how large can the recursive teaching dimension (RTD) of a concept class be as a
function of its VC dimension? No class is known with RTD > (3/2)·VCdim; the best
general upper bound is quadratic (Hu, Wu, Li, Wang, COLT 2017 —
arXiv:1702.05677).

**The concrete instance**: the maximum RTD over classes of VC dimension 2 is a
single unknown integer. Lower bound 3 (Warmuth's class, VCD 2 / RTD 3, in
Doliwa–Fan–Simon–Zilles, JMLR 2014). Upper end: the research sweep reported the
window as {3,4,5,6} — **[VERIFY in week 1]** the exact best published upper bound
for d = 2 from Hu et al. 2017 and anything later (check arXiv:2502.09453, Simon
2025, and citations of it). Every bound this search certifies is **new by
construction** — that is the whole point of the pivot.

### Definitions (get these exactly right in code and docs)

- Concept class: C ⊆ 2^[n], concepts as 0/1 rows of an m×n matrix, rows distinct.
- Teaching set of c ∈ C: a set T ⊆ [n] such that no other c' ∈ C agrees with c
  on all of T. TD(c; C) = min |T|. TDmin(C) = min over c ∈ C of TD(c; C).
- RTD(C) = max over subclasses C' ⊆ C of TDmin(C') (the recursive-elimination
  definition is equivalent — state and test this identity).
- Key reduction (verify, then lean on it): max-RTD over VCD ≤ 2 classes ≥ k iff
  **some class D with VCdim(D) ≤ 2 has TDmin(D) ≥ k** — because subclasses
  inherit VCdim ≤ 2 (VCdim is monotone under subclass) and RTD ≥ TDmin of any
  subclass. So the search hunts D with VCdim ≤ 2, TDmin ≥ 4.
- Useful known bound: TDmin(C) ≤ log₂|C| **[VERIFY attribution — Doliwa et al.
  2014]**, hence any witness for TDmin ≥ 4 needs m ≥ 16.

### What already exists: `prototype/rtd/`

`rtd_probe.py` — a PySAT/CaDiCaL encoding of "∃ class of m distinct concepts on
n points with VCdim ≤ vcd and TDmin ≥ tdmin". Encoding, verified sound by
reading: rows lex-increasing (breaks row-permutation symmetry, enforces
distinctness); VCdim ≤ 2 as "every 3-subset of points misses ≥ 1 of the 8
patterns"; TDmin ≥ 4 as "for every concept and every 2-point set T some other
concept agrees on T" (note: it uses |T| = tdmin−1 = 3 — re-derive why size-
exactly-(k−1) subsets suffice and write the lemma down). `rtd_sweep.log` shows on
4 cores: **n = 6 fully exhausted (all UNSAT), n = 7 UNSAT through m = 27 of 29**.
So at n ≤ 6 there is NO VCD-2 class with TDmin ≥ 4 — already a new (tiny,
uncertified) fact.

### Honest structural caveat — engrave it everywhere

The ground set is unbounded: Sauer bounds m ≤ 1 + n + C(n,2) in terms of n, but
nothing bounds n. Exhausting n ≤ 9 does **not** settle the open problem. Never
claim it does. The headline results are (a) certified exact statements "no
witness on ≤ N points", each new, and (b) the real prize: **structure in the
extremal classes** (the TDmin = 3, VCD = 2 classes at each n) that suggests an
analytic proof of "VCD ≤ 2 ⇒ TDmin ≤ 3". Pattern first, compute second.

---

## 4. Roadmap (phases, each with a definition of done)

### Phase 0 — Verify ground truth (½ day, blocks everything)
1. Read Simon–Zilles 2015, Doliwa et al. 2014, Hu et al. 2017, arXiv:2502.09453.
   Pin the exact known window for d = 2 with citations. Fix every [VERIFY] above.
2. Read the two MathCheck papers in full. Confirm §2's characterization.
3. Rerun the full test suite + one streamed R(3,5) certify as an environment check.
**Done when**: a `docs/rtd-background.md` exists with precise, cited statements.

### Phase 1 — Native RTD in orbitcert (the core build)
Extend the engine from graphs to concept classes (m×n 0/1 matrices, rows
distinct) and certify the search.
- Object: grow one **concept (row)** at a time. VCdim ≤ 2 is hereditary under
  removing concepts (a set shattered by a subclass is shattered by the class) —
  that is the pruning property, and the only one.

- **TDmin is non-monotone in BOTH directions — corrected 2026-08-04.** An earlier
  draft of this file justified "TDmin ≥ 4 is not hereditary" by saying *removing
  concepts shrinks teaching sets*. That reason is **wrong**, and the wrong reason
  misleads about which way the failure goes. Removing a concept does shrink each
  surviving concept's *individual* teaching set, but TDmin is a **minimum over an
  index set that also shrinks** — delete the concept achieving the minimum and
  TDmin goes *up*.

  Verified counterexample on 3 points: for
  `C = {000, 100, 010, 110, 001}` the individual values are
  TD(000)=3, TD(100)=TD(010)=TD(110)=2, TD(001)=1, so **TDmin(C) = 1**.
  Delete `001` and every surviving concept has TD = 2, so **TDmin(C′) = 2** —
  removal *raised* it. Exhaustively over all classes on 3 points, removing one
  concept moves TDmin by at most ±1 and both signs occur.

  Consequence for the search: TDmin ≥ 4 can hold at a node of **any** size, so it
  is a per-node target test, never a pruning rule, and it may never prune at all.

- **The conclusion changes shape, and so must the certificate.** For Ramsey the
  claim was "level n is empty". Here it is "**no node anywhere passes the target
  test**". That imposes a **per-node target obligation**: the certificate must
  account for the target at every node — neither asserting it unverified nor
  omitting it. A proof that silently skips the test at one node is exactly the
  hole the checker exists to catch, and the Ramsey-era format has no slot for it.

  Design note (mirrors the canonicity asymmetry, §1): "this node fails the target"
  has a **short witness** — a concept together with a teaching set of size ≤ 3 for
  it. Verifying that is O(m·n): check no other concept agrees on those points.
  Confirming TDmin ≥ 4 instead requires sweeping all concepts against all small
  subsets. So emit a (concept, teaching-set) witness per node for the common
  failing case, exactly as rejections carry permutations. Both directions are
  polynomial here — unlike canonicity — so the checker *could* recompute; the
  witness is a cost optimisation that preserves "checking cheaper than
  generating", not a soundness requirement. State which you chose and why.
- Symmetry: minimum is column (point) permutations S_n plus row order. Decide and
  PROVE the invariance of VCdim and TDmin under whatever group you quotient by
  (S_n is safe; per-column label flips are probably safe — prove it before use).
- Prefix-structured code for matrices so prefix-heredity survives (theory.md §8.3
  sketches this; write the analogue of Theorem 2.1 and machine-check it
  exhaustively at small sizes, exactly as `prototype/theory_check.py` does).
- New problem type in `problems.py` + `occheck.c` (`problem rtd n=... vcd=2 tdmin=4`).
  The C checker must re-derive the VC test itself; witnesses stay permutations
  (now acting on rows/columns).
- Cross-validate against `rtd_probe.py` (SAT) at every (n, m) both can reach, and
  against brute force at tiny sizes.
**Done when**: certified "no VCD-2 class with TDmin ≥ 4 on n ≤ 7" verifies in
both checkers, agreeing with the SAT prototype; corruption battery extended to
the new problem type; tests green.

### Phase 2 — Scale and extract structure
- Push n = 8, 9 (parallel subtree search; the generator is untrusted, so
  parallelize aggressively — certificates from workers concatenate per subtree).
- Enumerate and store ALL extremal classes (VCD 2, TDmin = 3) at each n; analyze
  automorphisms, point degrees, closure properties. This table is the discovery
  instrument.
**Done when**: certified statements for the largest reachable n + a structured
dataset of extremal classes with an analysis notebook.

### Phase 3 — The completeness theorem (this is what wins)
Every 1st-place MATH calibration point said "for ALL". Pick a restricted family
and close it completely — candidates: maximum classes (|C| meets Sauer with
equality), classes induced by graphs (arXiv:2502.09453 proves RTD ∈
{VCD−1, VCD} there — extend or sharpen), intersection-closed classes, or
extremal classes found in Phase 2. Target theorem shape: *"For all classes in
family F, RTD ≤ 3"* — proved by hand, discovered by the engine.
**Done when**: one complete characterization with a written proof the student can
derive on a whiteboard.

### Phase 4 — Stretch (only after 1–3)
Lean 4 port of the checker (spec = theory.md Theorem 4.4); or the proof-
complexity question (does this certificate format p-simulate DRAT on these
instances — genuinely open, nobody has posed it for enumeration certificates).

---

## 5. Engineering standards (non-negotiable, inherited from the build so far)

- Checker stays tiny, solver-free, and boring: no heuristics in `occheck.c`, ever.
- Every soundness lemma gets an exhaustive machine-check at small sizes AND an
  independent-oracle cross-check (nauty played that role for graphs; the SAT
  prototype and brute force play it for RTD).
- Every new proof format feature gets corruption tests before results are trusted.
- Errors one-sided by construction: prune only on a held witness.
- Streaming first: `generator | checker` must always work; certificates must
  never need to fit on disk.
- Report the scaling data with the growth/saturation split. Never cherry-pick.

---

## 6. ISEF constraints and strategy (context for every decision)

- **AI rules**: generative AI must not write the research plan, abstract, or
  poster, and all AI use must be disclosed; violations disqualify. Claude's role
  is implementation + literature legwork, disclosed. The student must own: the
  two theorems in `docs/theory.md` §2–3, the RTD definitions and reduction, the
  Phase 3 proof, and every experimental design choice. The 25-point interview is
  the largest scoring block; the test is deriving prefix-heredity and the RTD
  reduction on a whiteboard, cold.
- **Calibration** (from verified winner data): depth does not win — completeness
  does. Graduate algebra placed 4th in MATH 2024 behind an invented billiard law
  proved "for ALL slopes". Say "for ALL" about something (Phase 3).
- **Category**: file Systems Software → Algorithms, not MATH (precedent: Michelle
  Wei's SOCP complexity theorem won SOFT 1st + $50k in 2024). A theory result is
  a giant among applied-ML projects.
- **The demo**: let the judge corrupt a certificate themselves and watch the
  checker name the broken node. No finalist in the calibration set had anything
  like it. Rehearse it.
- **Mentor**: every deep MATH winner traced had one. For this project ask a
  learning-theory or formal-methods person; the leanprover Zulip and COLT
  community are reachable. Also email Radziszowski (Ramsey survey) and the
  MathCheck group — a maintainer/author reply is evidence judges respect.
- **Logbook** from day one; it is how judges assess what the student did.

## 7. Session hygiene for the desktop Claude

- Work on branch `claude/isef-cs-project-h1wncp`; never force-push over the
  session history.
- `make -C csrc && python3 -m pytest` must be green before and after every
  commit; add tests with every feature, corruption tests with every format change.
- When citing, link the primary source; anything marked [VERIFY] here must be
  resolved in Phase 0 before it appears in any student-facing document.
- The standard: finished, tested, documented, reproducible — or explicitly listed
  as not done. No silent gaps.

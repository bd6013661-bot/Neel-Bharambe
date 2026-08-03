# Topic Menu — 14 Vetted Directions

Every topic below passed four filters: (1) a **genuinely open** question — not homework in
disguise; (2) **tractable in 6–9 months** on a laptop + free compute (Colab/Kaggle), with
VS Code/Cursor as the toolchain; (3) **recent precedent** of a student, amateur, or tiny
team succeeding with exactly this method; (4) an **externally verifiable** deliverable —
a proof certificate, a published table entry, a leaderboard, or a merged contribution —
so the novelty claim doesn't rest on your own say-so. Filter (4) matters most: it is what
separates "judge is awed" from "judge is suspicious."

Categories: **MATH** = ISEF Mathematics; **SOFT/ROBO** = Systems Software / Robotics &
Intelligent Machines.

---

## Tier 1 — Recommended (highest expected value)

### T1. Certified SAT computation of unknown Rado / generalized Schur numbers 🥇 *primary recommendation* (MATH)

**The open problem.** For a linear equation like `x + y = 3z`, the *Rado number* `R_k(E)`
is the smallest `n` such that every k-coloring of `{1,…,n}` contains a monochromatic
solution to `E`. Chang, De Loera & Wesley (ISSAC 2022, arXiv:2210.03262) used SAT solvers
to prove exact formulas — e.g. they resolved a conjecture of Myers by proving
`R_3(x−y=(m−2)z) = m³−m²−m−1`. **Infinitely many equations and parameter families have
uncomputed 3- and 4-color Rado numbers.** Each one is open, finite, and attackable.

**What you'd actually do.** Pick a structured family of equations. For each member:
encode "no monochromatic solution in {1..n}" as CNF → SAT solver finds the extremal
coloring (lower bound) → UNSAT run with a **DRAT/LRAT proof certificate** proves the upper
bound → exact value, machine-checkably proved. Then the real mathematics: stare at the
extremal colorings across the family, conjecture the closed-form formula, and *prove it in
general* (the lower-bound construction usually generalizes by hand; the 2025 follow-up
literature, "Symbolic Sets for Proving Bounds on Rado Numbers," shows how to automate
certified general lower bounds).

**Why this wins.** (a) Every intermediate milestone is a permanent contribution — even
three new exact values is a citable table-entry result, and a proved family formula is a
publishable paper (that's literally what the ISSAC paper is). (b) Rigor is unimpeachable:
you hand judges a proof certificate that a 1,000-line verified checker can re-check — no
one can argue with it. (c) It's the "confluence" story judges rewarded in 2023–2026:
combinatorics + logic + high-performance computation. (d) The interview is unloseable *if
you did the work*: you'll understand every clause of your own encoding.

**Tools.** Kissat/CaDiCaL (solvers), `drat-trim` (certificate checking), Python for CNF
generation, symmetry-breaking techniques from the Heule literature. All free, all laptop-scale
(hard instances can go to a university cluster or cheap cloud later).

**Risk: LOW-MEDIUM.** The floor (several new exact values) is highly likely; the ceiling
(new proved formula for a family) is a real research outcome. Main risk: chosen family
turns out to have been computed already — mitigated by a literature sweep in week 1.

**Sources.** arXiv:2210.03262; the 2025 "Symbolic Sets" follow-up; Heule's vdW repo
(github.com/marijnheule/vdWaerden); Radziszowski's dynamic survey DS1 for the adjacent
Ramsey landscape.

---

### T2. New certified lower bounds for Ramsey-type numbers (MATH)

**The open problem.** Small Ramsey numbers remain famously unknown: `R(3,10) ∈ {40,41}`
(upper bound improved to 41 in 2024), `R(4,6) ∈ [36,40]`, `R(5,5) ≤ 46` (Angeltveit–McKay,
Sept 2024). The realistic student-scale wins are **new lower bounds**: find one coloring
(often block-circulant) that avoids the forbidden monochromatic structures at a size nobody
has achieved, and you have permanently improved a published table. Active work in exactly
this vein appeared in Sept 2025 (arXiv:2509.03784, multicolor/off-diagonal lower bounds via
structured SAT/IP search) and Oct 2024 (book Ramsey numbers via SAT, arXiv:2410.03625) —
this genre is alive and its authors are often solo or pairs.

**What you'd do.** Target the softest entries in Radziszowski's dynamic survey (rev. #18,
Jan 2026) — multicolor numbers like `R(3,3,4)`, book and wheel Ramsey numbers, off-diagonal
cases — and run structured search (circulant/block-circulant symmetry + SAT + local search)
for record colorings. Verification of a lower bound is trivial (exhibit the coloring; a
checker script confirms it), which makes the contribution bulletproof.

**Why this wins.** A new entry in *the* canonical survey table is unambiguous, permanent,
and citable. The story ("this number has resisted everyone since Erdős; I moved the known
bound") lands instantly with judges and needs no trust in your benchmarks.

**Risk: MEDIUM.** Records exist because they're hard; you may search for months and match
but not beat the record. Mitigation: attack 5–8 table entries in parallel (the tooling is
shared), and pair with T1 — same toolchain, guaranteed-yield fallback.

**Sources.** Electronic J. Combinatorics DS1 (dynamic survey); arXiv:2401.00392;
arXiv:2409.15709; arXiv:2509.03784; arXiv:2410.03625; cs.rit.edu/~spr/ramsey.

---

### T3. ML-guided counterexample hunting against published conjectures (MATH, CS-flavored)

**The open problem.** Adam Wagner's 2021 breakthrough (arXiv:2104.14516) used simple deep
reinforcement learning (cross-entropy method) to *construct counterexamples* to several
published open conjectures in extremal and spectral graph theory. The method has since been
systematized and improved (arXiv:2306.07956 found *simpler* counterexamples with adaptive
Monte Carlo search; arXiv:2406.12667 reimplemented the framework), and **PatternBoost**
(Charton–Ellenberg–Wagner–Williamson, Nov 2024, arXiv:2411.00566) — local search alternating
with a transformer — found best-known constructions for several long-standing problems and
killed a ~30-year-old conjecture. Its authors explicitly pitch it as usable by
"mathematicians with modest coding skills." The target pool is huge: hundreds of
machine-generated and human conjectures (Graffiti / AutoGraphiX lineage) relating graph
invariants, most never seriously attacked.

**What you'd do.** Build the search harness once (score function = "how badly does this
graph violate the conjecture"), then run it against a curated list of 20–30 published
conjectures. One violated conjecture = one complete result. Along the way you'll produce
best-known extremal constructions even where conjectures survive — also reportable.

**Why this wins.** It's a genuine research outcome ("Conjecture 7 of [X, 2009] is false;
here is the 37-vertex counterexample, verified exactly") plus a methodologically exciting
demo — the judges watch the search *discover* structure. Strong "creativity" rubric fit.

**Risk: MEDIUM.** No single conjecture is guaranteed to fall; the portfolio approach (many
targets, shared harness) converts it into a numbers game with good odds. Exact verification
of any candidate counterexample (rational arithmetic, not floats) is mandatory and easy.

**Sources.** arXiv:2104.14516; arXiv:2411.00566; arXiv:2306.07956; arXiv:2406.12667;
zawagner22.github.io.

---

### T4. Mechanistic interpretability of small transformers (SOFT/ROBO)

**The open problem.** How do trained neural networks actually compute? The field's leaders
maintain *public lists of open problems sized for exactly your budget*: Neel Nanda's "200
Concrete Open Problems in Mechanistic Interpretability" (difficulty-rated; he released 12
toy models specifically for this) and the 30-author "Open Problems in Mechanistic
Interpretability" (arXiv:2501.16496) — which confirms the basics are still unsettled: no
rigorous definition of "feature," unvalidated evaluation of sparse autoencoders, unexplained
training-dynamics phenomena (grokking). GPT-2-small fits in <1 GB of VRAM; grokking-scale
transformers train in minutes; pretrained SAEs (Gemma Scope, Neuronpedia) are downloadable.

**What you'd do (pick one).** (a) Extend the grokking progress-measures line (Nanda's ICLR
2023 paper ships an annotated Colab): new task families, a new progress measure that
predicts the phase transition, causal evidence via activation patching. (b) Stress-test SAE
evaluation: design an objective benchmark for whether SAE "features" are real (the 2025
open-problems paper says this is unsettled). (c) Fully reverse-engineer a 1–2-layer
attention-only model on an algorithmic task nobody has done.

**Why this wins.** AI interpretability is simultaneously scientifically deep, societally
resonant (judges know why understanding AI matters), and honest at small scale — your
experiments are causal (ablations, patching), replicable (public Colab), and yours. This
is the strongest CS-category pick if you prefer building to proving.

**Risk: MEDIUM.** The field moves fast — a literature check against the 2025 paper is
needed to avoid staleness ("I trained an SAE and found pretty features" is explicitly a
dead genre; DeepMind deprioritized SAEs after negative results). Causal rigor is the moat.

**Sources.** Nanda's 200 Open Problems (LessWrong/Alignment Forum); arXiv:2501.16496;
arXiv:2301.05217 (grokking progress measures); TransformerLens; ARENA curriculum;
arXiv:2409.04478.

---

## Tier 2 — Strong alternatives

### T5. Push the minimum Kochen–Specker problem from 24 toward 25 (MATH, physics crossover)

A 55-year-old open problem in quantum foundations: the minimum number of 3-D vectors
witnessing quantum contextuality. Known: ≥ 24 (Li–Bright–Ganesh, IJCAI 2024, SAT +
computer algebra, 40-TiB certificate) and ≤ 31 (Conway–Kochen). Each +1 on the lower bound
is a standalone publishable increment, and the SAT+CAS pipeline (MathCheck) is open-source.
**Risk: HIGH** — the next increment may need serious compute — but the story ("a teenager
moved a 55-year-old quantum problem") is a top-award story. Pair only with a safe fallback
like T1. *Sources: arXiv:2306.13319; IJCAI 2024 proceedings.*

### T6. A smaller 5-chromatic unit-distance graph (Hadwiger–Nelson problem) (MATH)

After de Grey's 2018 breakthrough (1567 vertices), the record for the smallest 5-chromatic
unit-distance graph fell repeatedly — and one of the record-holders, Jaan Parts, is an
independent amateur publishing in Geombinatorics (arXiv:2010.12665). Better local
search + SAT on subgraph minimization is exactly a strong student's game. Verification is
exact and easy; the problem statement ("how many colors does the plane need?") is the most
explainable open problem in mathematics — a poster gift. **Risk: MEDIUM.**
*Sources: arXiv:2010.12665; arXiv:1805.00157; Polymath16 threads.*

### T7. Prove a batch of Ramanujan Machine conjectures (MATH)

The Ramanujan Machine (Nature 2021) auto-generates continued-fraction identities for π, e,
ζ-values and explicitly solicits proofs; machine generation outpaces human proving. One
2024 paper (arXiv:2403.09729) proved 38 of them and generalized 31 — by a newcomer to the
area. Proving a batch via the known toolkit (matrix products, Euler-continued-fraction
transformations, telescoping) is real, publishable number theory with an infinite target
list. **Risk: LOW-MEDIUM** (floor: a few proofs; ceiling: a unifying family theorem).
*Sources: ramanujanmachine.com/prove-our-conjectures; arXiv:2403.09729; Nature 2021.*

### T8. PACE 2026 challenge: Maximum Agreement Forest solver (SOFT)

The annual PACE algorithm-engineering competition (2026 problem: Maximum Agreement Forest,
from phylogenetics) has exact/heuristic/lower-bound tracks, evaluation on 100 *private*
instances, and — crucially — an **official Student ranking**. Top solvers become IPEC
papers. The announce-fall/submit-spring cycle matches the ISEF timeline exactly, and a
leaderboard placement is externally verified novelty. **Risk: LOW-MEDIUM** (floor: a
ranked solver + engineering study; ceiling: podium + proceedings paper).
*Sources: pacechallenge.org/2026; arXiv:2411.17596 (a PACE 2024 solver paper).*

### T9. SAT Competition Hack Track: improve CaDiCaL in <1000 characters (SOFT)

The Hack Track exists "to lower the threshold for students to enter the SAT Competition":
beat stock CaDiCaL with a tiny source diff, scored by PAR-2 on hidden instances. The 2025
main track was won by *heuristic tweaks* (multi-armed-bandit restart adaptation), proving
small ideas still win. Deep synergy with T1/T2 — same solver internals. **Risk: MEDIUM**
(most tweaks regress; honest per-family benchmarking is the differentiator).
*Sources: satcompetition.github.io; SAT Competition 2025 proceedings.*

### T10. Fuzz the unfuzzed: real bugs in real scientific software (SOFT)

Write AFL++/libFuzzer harnesses for widely-used but never-fuzzed niche libraries
(scientific file formats, GIS parsers, font/protocol decoders); report reproducible bugs
upstream; contribute the harness to OSS-Fuzz so Google's cluster fuzzes it forever.
Deliverable: N merged fixes (occasionally CVEs) — externally verified by definition, plus
a responsible-disclosure story judges respect. **Risk: LOW** for the floor (a laptop core
on a never-fuzzed C library reliably finds crashes); the ceiling is a fuzzing-methodology
improvement entered into the SBFT competition (evaluated free on FuzzBench).
**Requires:** strict responsible-disclosure discipline — this plan includes it.
*Sources: google.github.io/oss-fuzz; SBFT competition; AFL++ docs.*

---

## Tier 3 — Viable, different flavor

### T11. Union-closed sets conjecture: the computational frontier (MATH)

Two concrete handles on a famous conjecture: (a) exhaustive/SAT verification currently
stops at ground sets of size n=12 — extend to n=13 with symmetry reduction + certificates;
(b) the post-Gilmer entropy constant is stuck at ≈0.3827, and the recent improvements
reduce to computer-checked one-variable inequalities — verified numerics (interval
arithmetic) territory. **Risk: MEDIUM-HIGH** (n=13 may be a wall; constant-pushing needs
a new inequality). *Sources: arXiv:2211.11504; EJC v31i3p35; Aldridge's survey blog.*

### T12. The Lean ladder: formal verification as the contribution (MATH/SOFT)

Formalization is now a first-class research contribution (the empty-hexagon SAT proof's
Lean verification is a standalone ITP 2024 paper). Live on-ramps with explicit task lists:
mathlib PRs → ccchallenge.org (formalizing the Collatz literature, 358 papers) →
DeepMind's Formal Conjectures repo / Erdős-problem statement formalization → the hard
cells of a Tao-style crowdsourced project (the Equational Theories Project's ~50 coauthors
explicitly included students and amateurs). Highest-probability path to *coauthorship on
real mathematics*; weaker as a solo "wow" unless combined with T1 (formally verify your
own SAT encoding — the Heule–Scheucher–Carneiro pattern, which would be a genuinely
state-of-the-art combination for a student). **Risk: LOW floor, slow ramp.**
*Sources: LIPIcs.ITP.2024.35; xenaproject.wordpress.com (Dec 2025); teorth.github.io/equational_theories.*

### T13. Externally-scored epidemic forecasting: a season on CDC FluSight (SOFT/ROBO)

The CDC FluSight Forecast Hub accepts weekly quantile forecasts of flu hospitalizations
from any team, scored publicly against the CDC baseline and the ensemble. A full season
(Nov→May — matches ISEF exactly) of beating the baseline with a novel model is externally
verified applied science with obvious societal weight. The anti-pattern this avoids: past
winning environmental-ML projects all had an external-validation angle (deployment,
novel sensing, leaderboard) — never "a CNN on a Kaggle dataset with 99% accuracy."
**Risk: MEDIUM** (you can't control where you place; honest uncertainty quantification is
the science). *Sources: github.com/cdcepi/FluSight-forecast-hub; NOAA ISEF award lists.*

### T14. A small numbered Erdős problem (MATH)

Thomas Bloom's erdosproblems.com now tracks ~1,179 numbered Erdős problems (~41% solved),
with a forum flagging which open ones are computation-amenable, and a live
Bloom–Tao-adjacent ecosystem (OEIS crosslinking, formal statements repo). Fully resolving
even a "small" one is headline-grade; improving a bound or completing a finite
verification is solid. Also the arena where humans and AI systems are now visibly
competing — framing your work there is timely. **Risk: HIGH variance** — treat as a
stretch goal bolted onto T1/T2 tooling, not a primary. *Sources: erdosproblems.com;
github.com/teorth/erdosproblems.*

---

## The Graveyard — tempting directions this plan deliberately rejects

| Direction | Why it's rejected |
|---|---|
| "Solve Collatz / Riemann / twin primes" | No ISEF winner ever did this; attempts produce nothing presentable. The *adjacent computational* problems (T14, verification frontiers) are the honest version. |
| "AI that does X" wrapper apps | No research question; judges see ChatGPT-wrapper projects constantly now. Zero novelty score. |
| Yet another CNN on a public dataset | The documented losing pattern in every recent fair. No external validation, no novelty. |
| "Novel" cryptography schemes | Amateur crypto is a negative signal to any qualified judge; breaking things responsibly (T10) is the credible security direction. |
| Presenting AI-generated research as yours | Fails to qualify under the Ethics Statement; unravels in interview #1 of four. See `RULES-AND-AI.md`. |

## Recommended portfolio

**Primary: T1** (guaranteed-yield, unimpeachable rigor) **+ shared-tooling stretch: T2 or
T5** (record-hunting on the same stack) **+ optional capstone: the T12 combination**
(formally verify your own encoding in Lean — if reached, this puts the project at the
genuine state of the art of computer-assisted mathematics).
If the CS category fits you better: **T4 primary, T8 secondary** (both externally scored,
opposite risk profiles).

The decision procedure, with dates and kill-criteria, is in [`TIMELINE.md`](TIMELINE.md).

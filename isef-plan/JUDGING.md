# How ISEF Judging Actually Works — and How to Win It

Verified against the current official Grand Award Judging Criteria
(societyforscience.org/isef/grand-award/criteria — confirmed current as of 2026, mirrored
by affiliated fairs). Older 30/30/15/15/10 "Creative Ability / Scientific Thought /
Thoroughness / Skill / Clarity" weights still circulate in some fairs' guides; the rubric
below is what ISEF Grand Award judging officially uses.

## The 100-point rubric

| Component | Points | Sub-items |
|---|---|---|
| Research Question | 10 | Clear focused purpose (4); identifies contribution to field (3); testable by scientific methods (3) |
| Design & Methodology | 15 | Well-designed plan & data collection (8); variables/controls defined & complete (7) |
| Execution: data collection, analysis, interpretation | 20 | Systematic collection/analysis (5); reproducibility (5); appropriate math & statistics (5); sufficient data for conclusions (5) |
| Creativity | 20 | Imagination & inventiveness; different perspectives opening new possibilities; emphasis on research *outcomes* |
| Presentation: Poster | 10 | Logical organization, clarity of graphics/legends, documentation supports |
| **Presentation: Interview** | **25** | "Understanding of the project's basic science, interpretation and limitations of the results and conclusions" |

Process facts: each project is judged **at least four times** in ~15-minute
**question-driven interviews** (finalists in contention typically get more, plus special
award judges — AMS, NSA, Mu Alpha Theta all judge the math category separately). Judges
are instructed to ask questions rather than sit through a speech, to weigh the student's
understanding over the physical display, and to judge **current-year work only**.

## What each line item means for the recommended project (T1-style)

- **Research Question (10):** "Determine the 3-color Rado numbers of family E(m) and prove
  a closed form" is exactly a clear, focused, testable-by-method question with an explicit
  contribution to a named literature. Say the sentence "this fills entries that are open in
  [the published table/survey]" — that *is* sub-item 2.
- **Design & Methodology (15):** your encoding, symmetry-breaking choices, solver
  configuration, and — crucially — the **verification design** (independent proof
  certificates, `make verify`). Controls in a math-computation project = correctness
  safeguards: checker independence, replicated runs, exact arithmetic.
- **Execution (20):** the reproducibility sub-item is a gift to this project type — few
  fair projects can hand a judge a one-command re-verification of every claimed result.
  Sufficient data = the full table across the family, not two cherry-picked values.
- **Creativity (20):** scored on outcomes with imagination — the conjecture you extracted
  from extremal-coloring structure, the encoding trick that made instances feasible, the
  cross-field synthesis (combinatorics ↔ logic ↔ verification). Winners' language from
  recent years is literally "a confluence of ideas" — build one deliberate bridge between
  two areas and make it visible.
- **Poster (10):** one figure that explains the problem to a 12-year-old (colorings of
  {1..n} as a colored number line with a monochromatic solution highlighted), one figure
  showing the method pipeline, the results table with **new values in bold**, limitations
  stated plainly. Written by you; see `RULES-AND-AI.md`.
- **Interview (25):** see below — this is a quarter of the score and the whole game at the
  top of the field.

## Interview preparation protocol

The interview is where identical-looking projects separate. Prepare like it's an exam
worth 25% with four different examiners.

**Build the three versions:** 30 seconds (elevator: problem, result, why it matters),
2 minutes (adds method and one insight), 10 minutes (whiteboard-ready full walk).

**The question bank to drill (minimum 6 mock rounds, per `TIMELINE.md`):**
1. Why this problem? Why is it *not* already done? Who cares?
2. Walk me through your encoding. Why this one? What failed before it?
3. How do you *know* the result is correct? (Answer ends with the certificate + independent
   checker; be able to explain what a DRAT proof is to a non-logician.)
4. What was YOUR contribution versus your tools'? — the ownership probe; answer with the
   instrument framing and the `ai-log.md` (see `RULES-AND-AI.md` §6), without defensiveness.
5. What did you try that failed? (Have three real answers. Judges trust failure stories.)
6. Limitations? What can't your method do? Where does it stop scaling and why?
7. What would you do with 12 more months?
8. Cold math checks: state the relevant definitions and the smallest nontrivial example
   from memory; re-derive one lower-bound construction on paper.

**Rules of engagement learned from past winners:** never bluff — "I don't know, but here's
how I'd find out" scores better than a wrong answer defended; bridge every answer back to
something you *did*; bring the failure stories unprompted when asked about process; the
2025 math winner also took the science-communication special award — treat explanation
quality as part of the research, not decoration.

## Where projects die (observed failure modes)

| Failure mode | Vaccine |
|---|---|
| Unverifiable novelty ("my accuracy is 97%") | External verification by construction: certificates, survey-table entries, leaderboards, merged fixes |
| Can't answer "what's YOUR contribution?" | The understanding rule + honest AI log; nothing in the project you can't re-derive |
| Polished poster, hollow interview | 6+ mock rounds; the 25-point item gets 25% of prep time |
| Scope inflation ("towards solving Collatz") | Claim exactly what you proved; ambition goes in the future-work section |
| Demo breaks / can't show the pipeline | `make verify` rehearsed offline on your own laptop, screenshots as backup |
| Judged work predates eligibility window / stale continuation | Current-year work only; date everything in the notebook |

## Special awards to explicitly aim for (math track)

Beyond the category Grand Awards: **AMS Karl Menger Memorial Prize** (professional
mathematicians judge it; proof-quality and rigor dominate — recent winners include exactly
the computer-assisted and pure-proof profiles in this plan), **Mu Alpha Theta**, and the
**NSA Research Directorate math awards**. These are judged by *domain experts*, which
favors this plan's certificate-backed rigor over showmanship. A project that sweeps
category + special awards is what historically precedes the top overall prizes.

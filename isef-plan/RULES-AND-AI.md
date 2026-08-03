# ISEF Rules, AI Policy, and a Working Compliance System

Everything here was verified against the current International Rules for Pre-College
Science Research (2025–26 edition) and the published **Final Rule Modifications for
2026–27** — i.e., the rules in force for the ISEF 2027 season. The load-bearing claims
below were independently re-verified against official excerpts. Where wording is quoted,
it is verbatim or near-verbatim from Society for Science sources; spot-check the exact
PDFs at societyforscience.org/isef/international-rules before filing forms.

---

## 1. Ownership: what the rules actually require

From **Roles and Responsibilities of Students and Adults**:

> "The student researcher is responsible for all aspects of the research project:
> enlisting the aid of any required supervisory adults, obtaining necessary approvals,
> following the International Rules & Guidelines, and completing all appropriate
> documentation. **Students are responsible for performing the project**, which may include
> but is not limited to experimentation, data collection, engineering, data analysis, and
> any other process or procedures related to the project."

From **Rules for All Projects**:

> "A student is expected to do independent work and **all materials presented must be in
> the researcher's own words**."

If the project touches a larger study (e.g., you work within a professor's group), you may
present **only your own portion**, and the Research Plan must "describe only your project
and do not include work done by mentor or others."

Adults have defined supervisory roles: an **Adult Sponsor** (teacher, parent, professor —
solid scientific background, monitors safety and rules) is required for every project; a
**Qualified Scientist** is required only for regulated research areas (none of the topics
in this plan trigger that).

## 2. The AI rules (verbatim, confirmed in force for the 2027 season)

> "Artificial Intelligence (AI) may be used as a project resource **but must be cited and
> given proper acknowledgment**."

> "A student **may not use generative AI to write the research plan, abstract, poster or
> to create citations** (it is known to hallucinate and falsify references)."

The official companion document — *Use of generative AI to support a research project*
(Generative-AI-Use-Table.pdf, published with the ISEF Scientific Review Committee) — sets
task-by-task conditions. The confirmed key rows:

| Use of AI | Status |
|---|---|
| Brainstorming topics, summarizing sources, learning background | Acceptable **with acknowledgment** |
| Writing initial project code | Acceptable **only with explicit citation of which portions were AI-generated** |
| Refining a document *after* you wrote it | Acceptable **with explicit citation and a log of the AI interaction** |
| Grammar/syntax-only edits | Acceptable without explicit citation (grammar/syntax **only**) |
| Writing the research plan, abstract, or poster | **Prohibited** |
| Creating citations | **Prohibited** |

The ISEF abstract is run through a plagiarism checker.

## 3. The Ethics Statement and what's at stake

Current formulation (Rules for All Projects):

> "The presentation of fraudulent data, the evidence of plagiarism **or the inappropriate
> use of AI** are prohibited and grounds for the project to **fail to qualify**. A violation
> of this ethics statement may result in disqualification from participating in ISEF and
> ISEF-affiliated fairs, and **forfeiture of any awards, prizes, and acknowledgment
> received**."

The long-standing rules also reserve the right to revoke recognition of a project
*subsequently* found fraudulent — i.e., retroactively, after the trophy.

**The practical enforcement mechanism isn't the plagiarism checker — it's the interview.**
Judging is at least four 15-minute question-driven interviews (25 of 100 points, the
largest single item; see `JUDGING.md`). Official guidance tells judges to probe *how well
the finalist understands the project*, why each methodological choice was made, and the
limitations of the results. Work you didn't do is work you can't defend for an hour of
adversarial questioning by professionals.

## 4. The compliance system this project will run

This turns the rules into habits. Adopt all five from day one.

**(a) AI-usage log.** A single append-only file (`ai-log.md`) in the project repo. One
line per session: date, tool (e.g., "Claude"), what was asked, what was produced, what you
did with it. This satisfies the "log of the AI interaction" condition and becomes an
exhibit of integrity at your booth rather than a liability.

**(b) Code attribution convention.** Every source file carries a header: `// Author: <you>`,
`// AI-assisted portions: <list or 'none'>`. AI-assisted functions get a one-line marker.
Your poster and paper carry one citation line, e.g.: *"Portions of the tooling code were
developed with the assistance of Claude (Anthropic); all AI-assisted code is marked in the
public repository. AI was not used to write the research plan, abstract, or poster."*

**(c) The understanding rule.** Nothing ships that you cannot re-derive on a whiteboard.
Concretely: for every AI-assisted component, you re-implement or line-by-line annotate it
before it enters the pipeline. If a proof step came from a discussion with an AI or a
mentor, you write your own proof from scratch and have the hole-hunting done on *your*
version. This is both the rule ("own words") and the interview-survival strategy.

**(d) Documents you write cold.** Research Plan, abstract, poster: drafted by you, from
your own outline, in an editor with no AI assistance. Allowed afterward: grammar/syntax
suggestions only. Non-negotiable — these are the three artifacts the rules name.

**(e) Certificates over trust.** Prefer deliverables that carry their own proof: DRAT/LRAT
certificates, exact-arithmetic verification scripts, public Colabs, leaderboard entries,
merged upstream fixes. Then your integrity story is airtight *and* your rigor score is too.

## 5. Paperwork map (all topics in this plan = "unregulated" track)

| Form | What | When |
|---|---|---|
| Form 1 | Adult Sponsor checklist | Before experimentation |
| Form 1A | Student checklist: title, sponsor, where conducted, actual start/end dates | Before experimentation |
| Research Plan | Rationale; research question/hypothesis/goals; procedures; risk & safety; data analysis; bibliography | **Written before experimentation begins** |
| Form 1B | Approval form (signatures) | Before experimentation |
| Abstract | ≤250 words, own words, current year's work only | After research concludes, via the finalist questionnaire |

Rules of scope to remember: **max 12 months of continuous research**; judged on the
**current year's work only**; team max 3 (this plan assumes solo); you compete through
**one** affiliated fair. Starting experimentation in Sept–Oct 2026 puts the entire project
comfortably inside the eligibility window for ISEF May 2027 — but confirm the exact
research-start cutoff date in the 2027 rulebook when your affiliated fair opens
registration, and confirm your fair's own local deadlines (they are often months before
the fair).

Note for CS/math projects: no human participants, no vertebrates, no biohazards — so no
SRC/IRB pre-approval complexity. One caveat: if a project ever surveys people (don't),
human-participant rules now require written parental permission for minors. Keep the
project purely computational and the paperwork stays minimal.

## 6. What "AI as a project resource" looks like in this project, concretely

Legitimate and logged: Claude teaches you SAT encodings until you can write one cold;
suggests literature to read; reviews your proof and finds a gap; helps debug your CNF
generator (marked AI-assisted in the repo); drills you with mock interview questions;
critiques your poster draft's clarity *after* you wrote it.

Not happening, per the rules: Claude choosing your research question for you, producing
results you present as yours, writing any part of the research plan/abstract/poster,
generating your bibliography.

The distinction to internalize: **AI as instrument** (like Mathematica, like a SAT solver
— cited, controlled by you, understood by you) versus **AI as ghost-author** (fails to
qualify). Everything in `TOPICS.md` was chosen so that the instrument framing is natural:
in computer-assisted mathematics, *the machine doing heavy lifting under your direction is
the methodology* — you just have to actually be the one directing it.

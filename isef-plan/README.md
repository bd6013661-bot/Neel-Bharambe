# ISEF 2027 Project Plan — Mathematics & Computer Science

**Prepared:** August 2026 · **Target:** Regeneron ISEF, May 2027 (via an affiliated regional/state fair, typically Jan–Mar 2027)

This folder is a complete research-backed plan for choosing and executing an ISEF project
capable of competing for a category First Award — and, if it goes exceptionally well, a top
overall award. Every factual claim in these documents was researched against primary sources
in August 2026 (winner lists 2023–2026, the current International Rules, and the current
state of each proposed research area). Sources are cited inline.

## Read this first: the honest premise this plan is built on

You asked for something "genuinely revolutionary and unheard of" that "solves unsolved
problems." Here is what the evidence actually says, and it should change your target —
in a way that makes winning *more* likely, not less:

**1. No first-place ISEF math or CS project in the last four years solved a famous open
problem.** Not one. The 2026 Mathematics winner (and $75,000 Young Scientist Award winner)
Nikola Veselinov proved a *new but well-scoped theorem* about when equations can't be solved
in elementary functions. The 2026 $100,000 top-prize winner Hikaru Kuribayashi built an MCMC
sampler for origami configuration spaces — a genuinely new *method*, not a resolved
conjecture. The 2023 knot-theory standout (Nicholas Hagedorn) proved new crossing-number
inequalities and published them in a peer-reviewed journal. The winning formula is a
**complete, rigorous, genuinely new contribution to a real research area** — publishable-tier,
tightly scoped. "Revolutionary" is what the press release says afterward; it is not the
selection criterion. See [`JUDGING.md`](JUDGING.md) for the actual 100-point rubric.

**2. The project must be yours, and ISEF's rules on AI are explicit and enforced.** The
current International Rules (verified in force for the 2027 season) say, verbatim:

> "Artificial Intelligence (AI) may be used as a project resource but must be cited and
> given proper acknowledgment."
>
> "A student may not use generative AI to write the research plan, abstract, poster or to
> create citations."

and the Ethics Statement makes "the inappropriate use of AI" explicit grounds for a project
to **fail to qualify**, with forfeiture of awards possible retroactively. The single largest
item on the judging rubric is the **interview (25/100 points)** — at least four 15-minute
interviews where judges probe whether you understand and performed the work. A project I
build and you present is not a winning strategy; it is a disqualification with extra steps,
and it would not survive the first interview. Full rules, quotes, and a practical compliance
system (AI-usage log, code-attribution convention) are in [`RULES-AND-AI.md`](RULES-AND-AI.md).

**3. The good news: the honest version of this project is stronger than the fantasy
version.** There is a class of problems — computer-assisted combinatorics, ML-guided
conjecture discovery, mechanistic interpretability — where a determined high-school student
with serious tooling skills competes on nearly equal footing with professionals, where
*new, certified, citable results* are realistically achievable in 6–9 months, and where
students and amateurs have recent, documented wins. Hannah Cairo disproved a 40-year-old
conjecture at 17 (2025). Jaan Parts, an independent amateur, repeatedly held the world
record for the smallest 5-chromatic unit-distance graph. Tao's Equational Theories Project
lists students and amateurs among its ~50 coauthors. That is the arena this plan puts you in.

## My role vs. your role

Under the rules, here is the legitimate division of labor — and it is a *lot* of help:

| I can (cited & logged) | Only you can |
|---|---|
| Teach you the background math/CS, at any depth | Choose the research question |
| Help you survey literature and find open targets | Write the Research Plan, abstract, poster |
| Review your proofs and hunt for holes | Construct and understand the proofs |
| Help you write/debug tooling code (cited as AI-assisted) | Run the experiments, own the pipeline |
| Red-team your claims before judges do | Answer every interview question |
| Mock-interview you relentlessly | Sign the ethics attestation |

## The recommendation (short version)

Full menu with 14 vetted topics: [`TOPICS.md`](TOPICS.md). The top-line recommendation:

- **Primary track (Mathematics): certified SAT-solver attack on uncomputed Rado /
  generalized Schur numbers**, following the Chang–De Loera–Wesley template — compute new
  exact values with machine-checkable DRAT/LRAT proof certificates, find the pattern across
  a parameter family, and prove the general formula. Every milestone is a permanent,
  citable contribution; rigor is unimpeachable (the proof is a certificate anyone can
  re-check); and it is exactly the "confluence of ideas" (combinatorics + logic +
  large-scale computation) that the last four years of winning projects share.
- **Secondary/backup track: ML-guided counterexample search** (Wagner / PatternBoost
  pipeline) against published conjectures in spectral and extremal graph theory — one found
  counterexample is a complete paper, and the method itself demos beautifully at a fair.
- **If you'd rather compete in a CS category: mechanistic interpretability of small
  transformers** — laptop-scale, an explicitly published menu of open problems, and a
  results format (causal, replicable, public Colab) that maps perfectly onto the rubric.

Why not the flashier things: see the "Graveyard" section at the end of `TOPICS.md` for
the honest reasons famous open problems, "novel cryptography," and "yet another CNN on a
Kaggle dataset" are losing plays.

## Files in this plan

| File | What's in it |
|---|---|
| [`TOPICS.md`](TOPICS.md) | 14 vetted topics in 3 tiers, each with the open problem, why it's genuinely novel, deliverables, tools, risk, and sources |
| [`RULES-AND-AI.md`](RULES-AND-AI.md) | Verbatim ISEF rules on ownership, AI, and ethics; forms; a working compliance system |
| [`TIMELINE.md`](TIMELINE.md) | Month-by-month plan, Aug 2026 → ISEF May 2027, with decision gates and fallbacks |
| [`JUDGING.md`](JUDGING.md) | The current 100-point rubric, what wins each line item, interview-prep protocol, failure modes |

## The next three moves

1. Read `TOPICS.md` and pick **two** Tier-1 candidates (a primary and a hedge).
2. Spend the next 2–3 weeks on the *exploration sprints* defined per-topic in `TIMELINE.md`
   — cheap, fast experiments that tell you which problem has give in it.
3. Find your Adult Sponsor and (ideally) a university mentor now — before school starts —
   and register intent with your affiliated regional fair. Winners in 2024 and 2025 both
   had professor mentors; the outreach email template is in `TIMELINE.md`.

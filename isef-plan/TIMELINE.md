# Execution Timeline — August 2026 → ISEF May 2027

Assumes the recommended portfolio (T1 primary + T2/T5 stretch + optional T12 capstone;
see `TOPICS.md`). The same skeleton works for the CS-category portfolio (T4 + T8) — the
per-phase deliverables just swap. Dates for your affiliated regional/state fair are
placeholders: **look up your actual fair's registration and paperwork deadlines in
September; they are commonly due months before the fair itself.**

The single most important structural rule: **the Research Plan must be written before
experimentation begins** (see `RULES-AND-AI.md` §5). The plan below is sequenced around
that — August–September is *exploration and training* (learning tools, replicating known
results), and the formal research window opens in October after the plan is filed.

---

## Phase 0 — Exploration sprints (Aug 4 – Sep 14, 2026)

Goal: choose the primary track with evidence, not vibes. Run two cheap sprints in
parallel. Everything here is *training and replication*, not the project's experiments.

**Sprint A — SAT track (T1/T2):**
- Learn the stack: install Kissat, CaDiCaL, drat-trim; write a CNF generator for a toy
  problem; **replicate a known result** — e.g., reproduce a small known Rado number or
  Schur number with a certificate, end to end.
- Literature sweep (with AI help, logged): read arXiv:2210.03262 and its 2025 follow-up;
  list every equation family with published Rado numbers; identify 3 candidate families
  with uncomputed values and no evidence anyone is working on them.
- Exit artifact: a one-page "target dossier" per candidate family.

**Sprint B — ML-search track (T3) [or T4 if leaning CS]:**
- Reimplement Wagner's cross-entropy method on one *known* result from his paper;
  confirm your harness rediscovers his counterexample.
- Curate 20 candidate published conjectures with cheap score functions.
- Exit artifact: working harness + ranked conjecture target list.

**Also in Phase 0 (parallel, low effort):**
- **Mentor outreach (week 1–2).** Email 5–8 professors within reach (combinatorics /
  SAT / discrete math; or interpretability if CS track) — the 2024 and 2025 math winners
  both had professor mentors. Template: short, specific, shows the replication you already
  did, asks for 30 minutes monthly + a sanity-check role. A "yes" also fills the Adult
  Sponsor slot if no teacher fits.
- **Fair logistics.** Identify your ISEF-affiliated regional fair, its registration window,
  and its SRC paperwork deadlines. Put every date on a calendar.

### DECISION GATE 1 (Sep 14): commit to the primary track
Choose by evidence: which sprint produced a working pipeline + the richest target list?
Kill-criterion: any track whose week-6 exit artifact doesn't exist gets dropped, no
sentiment. Then draft the **Research Plan yourself, cold** (see `RULES-AND-AI.md` §4),
have sponsor/mentor review it, file Forms 1/1A/1B.

---

## Phase 1 — First blood (Sep 15 – Nov 30, 2026)

Goal: get the floor result — the guaranteed-yield contribution — fully banked.

- **Oct:** run the T1 campaign on family #1: encode → solve → certify, marching `n`
  upward per parameter value. First new exact values should land this month (these are
  publishable-tier table entries *the day you certify them*).
- **Nov:** extend across the family; build the conjecture table (extremal colorings vs.
  parameter); start the general-formula proof attempt. In parallel, background-run T2
  record searches on shared tooling (cluster/Colab overnight jobs).
- Infrastructure discipline throughout: every result reproducible by `make verify` — one
  command that re-checks every certificate. This becomes a booth demo.
- **Documentation:** lab notebook (dated entries) + `ai-log.md` from day one.

### DECISION GATE 2 (Nov 30): scope the headline
Bank status check. If ≥3 new certified values: pursue the general formula proof as the
headline (Dec–Jan). If the family resists: pivot the headline to breadth (more families /
a T2 record) — the floor result already makes a complete, honest project.

---

## Phase 2 — The headline result (Dec 1, 2026 – Jan 31, 2027)

- **Dec:** the mathematics push — prove the general lower-bound construction; automate
  certified upper bounds across the family (the "symbolic sets" method); attempt the
  closed-form theorem. This is where mentor conversations matter most.
- **Jan:** freeze experiments for the regional fair. Write the paper-style report (you,
  cold; AI for logged post-draft critique only). If the theorem landed, consider arXiv
  posting with mentor guidance — external validation of exactly the kind past winners had.
- **Stretch (only if ahead of schedule):** begin the T12 capstone — Lean-verify the
  encoding correctness for one family (the Heule–Scheucher–Carneiro pattern).

---

## Phase 3 — Regional fair & iteration (Feb – Mar 2027)

- Build the poster (you, cold — then grammar-only polish). Structure in `JUDGING.md`.
- **Mock interviews: minimum 6 rounds.** Mentor, teachers, and AI-drilled question banks
  (that use of AI is a resource use — log it). Practice the 30-second, 2-minute, and
  10-minute versions of the project.
- Compete at the affiliated fair → ISEF qualification.
- Post-fair: judges' questions you fumbled become February's work items. You have ~8 weeks
  between regional and ISEF — winners use them: extend results (another family, another
  record attempt, the Lean capstone), tighten every weak answer.

## Phase 4 — ISEF (Apr – May 2027)

- **Apr:** finalize ISEF paperwork; write the 250-word abstract (you, cold); refresh the
  poster with post-regional results; assemble the booth kit (certificate-verification live
  demo, extremal-coloring visualizations, the printed `ai-log.md` — transparency as a
  strength).
- **May:** ISEF. Judging is ~4+ interviews × 15 minutes, questions-driven. You'll have
  spent nine months being the only person who did the work — which at that point is your
  decisive advantage over every polished-but-hollow project in the hall.

---

## Standing weekly rhythm (all phases)

| Slot | What |
|---|---|
| ~6 h/wk | Core research work (the only non-negotiable) |
| ~2 h/wk | Reading: one paper/week from the topic's source list, notes in repo |
| 30 min/wk | Lab notebook + `ai-log.md` hygiene, repo commit of the week's state |
| Monthly | Mentor check-in; recalibrate against the current decision gate |

## Failure playbook

| If… | Then… |
|---|---|
| No mentor says yes by Oct | Proceed anyway — T1's certificates don't need authority to be true. Retry outreach in Dec with results in hand (results convert "no reply" into "yes"). |
| Family #1 fully computed already (found in week 1 sweep) | Move to dossier family #2 — that's why three were prepared. |
| Solver walls out at some n | That boundary is itself reportable ("computed through n=…, certified"); switch to the next parameter value, report the frontier. |
| Both stretch goals miss | The floor project (new certified values + breadth) is still a complete, rigorous, novel entry — present it with full confidence. |
| A result turns out to duplicate prior work discovered late | Disclose immediately in the report, credit it, and present the independent method honestly. Integrity is scored; cover-ups end projects. |

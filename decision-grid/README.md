# Xero Decision Grid — proof of concept

*2026-10-13. Built from Casey's 2026-10-12 seed (filed in the zero-agent
notes, "calculator-maker-alarm"): **a big model breaks work down into
decisions; little models make those decisions; Jevs set the gates on the
decisions.** The big model works inside a spreadsheet of live instances,
working itself out of a job as cells are re-staffed with smaller and
smaller models.*

## The mechanism, as built

- **DECOMPOSE** — the workload (survey triage of 395 sampled SuperInstance
  repos) is cut into four decision cells per repo: `FAM` (survey family),
  `TRAP` (is the name honest), `PILLAR` (which zero pillars), `DISP`
  (disposition — reads the FAM/PILLAR cells, spreadsheet-style chaining).
  Each cell has bounded inputs, one definite question, enumerated outputs.
- **DECIDE** — three decider tiers staff the cells: `ALGO` (hand-written
  rules, the zero-model floor), `SMALL` (MiniMax-Text-01 via the minimax
  skill), `BIG` (a strong-model labeling pass — 119 repos × 4 cells,
  labeled by hand; doubles as the REF standard).
- **GATE** — Jev (TypeSafe) calibrates gate policy from measured evidence
  and judges individual decisions: pos = accept, zero = deadband/escalate,
  neg = reject. Every call is logged (`judgment-log.md`).
- **PRUNE** — per cell type, staffing descends the staircase (BIG → SMALL →
  ALGO) wherever fidelity holds; the sheet records the final staffing of
  all 1,580 cells.

## Status

Run 2026-10-13, initially **partial by provider rate-limit** (see
RESULTS.md "The deficit") — then **completed the same day by a paced
re-run** (RESULTS.md "Re-run (paced)"): one call in flight, backoff on
429, **zero 429s**, SMALL coverage 395/395 on all four cells plus three
new subsample cells (SUBSTANCE, COLLISION, VAGUE). All staircases are
now closed: FAM pruned to rule + small model in the tail; TRAP closed
negatively (cannot prune — and neither can its re-cut halves, COLLISION
and VAGUE, both measured below the always-NO floor); PILLAR closed
toward the floor (the name-keyword ALGO is the confirmed staffing;
SMALL's tags measured worse than the floor and demoted to candidates);
DISP's formula ceiling of 80.7% reconfirmed and shown not to move with
a SUBSTANCE cell — the residual is representativeness, not substance.
Headline results: staffed grid runs at 8.6% of all-BIG cost; Jev's gate
accepted 11/11 correctly and let zero wrong SMALL decisions through on
the gated set.

## Layout

```
README.md            this file
RESULTS.md           full results: accuracy, gates, staircase, mis-cuts
judgment-log.md      every Jev call: calibration + 36 instance gates
code/
  sample.py          stratified sample + GOLD labels from the survey data
  standards.py       pillar definitions, SILVER standards, disposition rule
  algo.py            ALGO tier decider
  minimax_run.py     SMALL tier decider (per cell type; resumable)
  minimax_paced.py   PACED re-run runner (concurrency 1, 429 backoff,
                     per-call log; also runs SUBSTANCE/COLLISION/VAGUE)
  score2.py          re-run metrics incl. DISP/SUBSTANCE/TRAP-recut
  finalize2.py       rebuilds the sheet + economics with closed staircases
  jev_rerun.py       executes data/jev_rerun_plan.json (Jev gate calls)
  big_sample.py      draws the 119-repo strong-model subsample
  score.py           all accuracy/fidelity metrics -> data/scores.json
  jev_gates.py       Jev calibration + instance gates -> data/jev_calls.jsonl
  finalize.py        builds the sheet + economics with staircase staffing
data/
  sample.jsonl       the 395 repos (name, desc, lang, fork, GOLD, stratum)
  big_sample.jsonl   the 119-repo subsample
  big_labels.jsonl   BIG tier decisions = REF standard
  decisions_algo.jsonl / decisions_small.jsonl   tier outputs per repo
  small_<CELL>.jsonl per-cell SMALL raw outputs ("MISSING" = 429 casualty
                     in run 1; after the paced re-run: zero MISSING anywhere)
  small_SUBSTANCE/COLLISION/VAGUE.jsonl   re-run cells on the REF subsample
  trap_recut_labels.jsonl   REF2 hand labels for the TRAP re-cut
  minimax_calls_rerun.log   every re-run MiniMax invocation, on record
  rerun_summary.json / scores2.json / jev_rerun_plan.json /
  jev_rerun_results.json    re-run artifacts
  scores.json        computed metrics
  jev_calls.jsonl    full Jev call log (context, question, verdict)
  jev_instance_results.json   gated-set outcomes
  sheet.csv / sheet.jsonl     THE SHEET: 1,580 live-instance rows with every
                       decider's output, gate verdicts, final staffing,
                       and correctness vs the applicable standard
  economics.json     staffed-grid cost vs all-BIG
```

## How to run

```
python3 code/sample.py          # rebuild the sample (seeded, deterministic)
python3 code/algo.py            # ALGO tier over the full sample
python3 code/big_sample.py      # draw the BIG subsample (labels are committed)
python3 code/minimax_run.py FAM # SMALL tier, one cell type at a time —
python3 code/minimax_run.py TRAP   # PACED: do NOT run these concurrently;
python3 code/minimax_run.py PILLAR # the provider's 429 is a hard stop.
python3 code/minimax_run.py DISP   # (DISP chains on SMALL's FAM/PILLAR)
# The paced re-run that completed the grid (sequential; safe to re-run —
# it only fills MISSING cells and normalizes the cell files):
python3 code/minimax_paced.py FAM TRAP PILLAR DISP
python3 code/minimax_paced.py SUBSTANCE COLLISION VAGUE
python3 code/score2.py && python3 code/finalize2.py
python3 code/score.py           # metrics
python3 code/jev_gates.py       # Jev calibration + instance gates
python3 code/finalize.py        # the sheet + economics
```

Data source: `~/workspace/xero-research/superinstance/.scratch/all-repos.jsonl`
(the survey's full 5,231-repo enumeration). No GitHub push; no secrets
anywhere in the tree (MiniMax/Jev credentials stay inside their skill CLIs).

## The one-paragraph version

The grid works, and its failures are the interesting part. Family
classification pruned cleanly to a rule plus a small model in the tail (the
big tier staffs zero production FAM cells). Name-honesty refused to prune at
any cheap tier — a mis-cut cell, caught by the grid's own measurements and
demoted to a watch by Jev's gate. Disposition turned out to be a formula
with a measurable 80.7% ceiling and one missing input. And the judgment
layer's verdict on the whole arrangement: distrust blanket rules, judge
instances with evidence in hand — its accept band went 11 for 11.

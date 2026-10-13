# Decision-Grid PoC — Results

*2026-10-13. The converged seed from Casey's 2026-10-12 rambles, built and run:
a big model decomposes work into decision cells in a spreadsheet of live
instances; little models make the decisions; Jev sets the gates; cells are
re-staffed down a staircase of smaller and smaller deciders.*

## The workload

**Survey triage of the SuperInstance library.** Sample: 395 of 5,231 repos
(stratified, seeded: 160 big-family, 128 tail, 48 no-description, 48 forks,
11 spotlight anchors). Each repo is one spreadsheet row-set of four decision
cells:

| Cell | Question | Outputs |
|---|---|---|
| FAM | Which survey family is this repo in? | 41 families, or OTHER |
| TRAP | Is the name an honest guide to the content? | TRUST / SUSPECT |
| PILLAR | Which zero-program pillars does it touch? | up to 2 of 9, or none |
| DISP | Survey disposition? (reads FAM+PILLAR cells — grid chaining) | DEEP / COLLAPSE / TAIL |

**Standards.** GOLD = the survey's programmatic family clustering (first
name-token). SILVER = keyword rules over name+description. REF = strong-model
reference labels (the parent agent labeled all 4 cells for 119 repos by hand).
**Tiers.** ALGO = hand-written rules (the zero-model floor). SMALL =
MiniMax-Text-01, batched 16 repos/call. BIG = the strong-model labeling pass.

## The deficit (perfect minus fuck-ups, first)

**The SMALL tier is incomplete: MiniMax returned HTTP 429 mid-run and the
run stopped there, per the hard-stop rule — no retries at any rate, through
any route.** Cause: my own orchestration — I ran three batch loops against
the provider concurrently. Coverage when the stop hit: FAM 239/395 answered,
TRAP 138/395, PILLAR 16/395, DISP 0/395 (never started). Consequences, all
carried through the numbers below:

- Every SMALL metric is computed **only on answered instances** (n always
  shown), and the answered set is big-family-heavy: SMALL has *zero* FAM
  coverage of the fork and spotlight strata.
- The PILLAR and DISP staircases **cannot close** in this run. Their ALGO
  floors, standards analysis, and gate calibrations are delivered instead.
- The sheet records the un-answered cells as `RATE-LIMITED` / `NOT-RUN` —
  the grid's own log shows where the fuel ran out.

Usage before the stop: 58 MiniMax batch calls logged (25 FAM + 25 TRAP +
8 PILLAR), each failed batch retried once (≈80 invocations). Jev: 44 calls,
all logged in `judgment-log.md` / `data/jev_calls.jsonl`.

## Accuracy

### FAM — a formula wearing a decision's coat (in families), a real decision (in the tail)

| Comparison | Result |
|---|---|
| ALGO vs GOLD | 395/395 = 100% (by construction — the token rule *is* the clustering key; sanity check, not a victory) |
| SMALL vs GOLD | 203/239 = **84.9%** — bigfam 97.5% (155/159), tail **50.0%** (32/64), no-desc 100% (16/16) |
| BIG vs GOLD | 117/119 = 98.3% — both divergences are fused names: `jeviter`→jev, `quiltcall`→quilt |
| SMALL fidelity to BIG | 62/68 = 91.2% |
| ALGO fidelity to BIG | 117/119 = 98.3% |

SMALL's 36 "errors" against GOLD are almost all in the tail, and they are
*semantic* family assignments to repos GOLD calls OTHER by construction
(`jeviter`→jev, `cot-quilt`→quilt, `garden`→cocapn). GOLD cannot judge them;
against REF, SMALL's tail behavior is 91% faithful. The cell is really two
cells — see mis-cuts.

### TRAP — the cell that couldn't be staffed

REF base rate: SUSPECT is **4/119 (3.4%)**. Both cheap deciders flag an order
of magnitude more often and are usually wrong:

| Decider | Accuracy vs REF | SUSPECT caught | False SUSPECT flags |
|---|---|---|---|
| SMALL (n=49) | 65.3% | 1/2 in subset | 16 |
| ALGO (n=119) | 70.6% | 2/4 | 33 |

SMALL flag precision ≈ 6%. SMALL and ALGO agree with each other only 53.6%
of the time — the cell isn't just hard, it's *unstable* at cheap tiers.

### PILLAR — the standard is weaker than the deciders

SMALL is effectively unmeasured (16 answers vs SILVER: 12.5% exact-set;
6 vs REF: 1/6 — anecdote, not evidence). What the run did measure is the
standards: ALGO (name-only keywords) vs SILVER (name+description keywords)
agrees 70.9% exact / 75.4% any-overlap (n=395) — but **BIG vs SILVER is only
59.7% exact / 68.1% overlap**. SILVER over-fires badly: 76
pyramid-orchestration tags across the sample where REF finds the pillar in
6/119 repos; 51 memory-grid tags vs REF's 11/119 rate. Any future PILLAR
staircase needs a real labeled standard first (the 119 REF labels are the
seed of one).

### DISP — a formula with a ceiling, and the ceiling is measurable

SMALL never ran. Formula variants against REF (n=119; REF base: DEEP 14,
COLLAPSE 56, TAIL 49):

| Formula inputs | Accuracy vs REF |
|---|---|
| GOLD family + SILVER pillars | 63.9% |
| ALGO's own cells (chained) | 78.2% |
| **BIG's own FAM/PILLAR (perfect inputs)** | **80.7%** |

Even with perfect upstream cells, my disposition rule reproduces strong-model
dispositions only 80.7% of the time. The residual ~19% is a judgment the rule
doesn't carry — *instance substance* (pillar-bearing but a mere instance →
TAIL, e.g. `jc1-research`, `openmind-conductor`; fork-carried but
pattern-bearing → DEEP, e.g. `MerkleMesh`). DISP is not mis-staffed; it is
**mis-fed**: it needs one more upstream cell (SUBSTANCE) that the
decomposition didn't have.

## Gates (Jev) — what the judgment layer said and did

Calibration calls (policy from measured evidence; full text in
`judgment-log.md`):

- **pos 0.90** — SUSPECT flags are watches that escalate, never verdicts.
- **pos 0.96** — keyword pillar tags are candidates requiring confirmation.
- **neg 0.38** — Jev *rejected* staffing big-family FAM cells by the naming
  rule alone, against 98.3% fidelity evidence. A genuine judge/decomposer
  disagreement; the staircase followed the measurements, and the dissent is
  logged, not buried.
- **zero 0.64** — fused-name escalation: inside the deadband, leaning yes.
- **zero 0.49** — DISP formula-by-default: true deadband.
- **neg 0.37** — blanket no-description escalation: rejected (names carry
  signal; FAM no-desc was 16/16).
- **neg 0.20** — "disagreement alone is a sufficient escalation trigger":
  rejected. Yet in the allocation *choice*, Jev weakly picked disagreements
  (0.51, confidence 0.35) as the least-bad place to spend the budget. Both
  verdicts stand in the log; the tension is a finding, not an error.

Instance gates (36 SMALL decisions from the REF subsample, picked
disagreement-enriched — 18 intended errors/disagreements, 18 agreement
controls; this set is **not** a natural stream):

- SMALL alone on the set: 18/36 = 50%. **Jev-gated pipeline: 36/36 = 100%.**
- Jev accepted (pos) 11 decisions — **all 11 correct (accept precision
  11/11)**. Of the 18 wrong SMALL decisions, **zero were accepted**: 7 landed
  neg (reject), 11 in the zero band (escalate). The deadband did the work —
  on TRAP especially, Jev's probabilities on wrong calls clustered at
  0.39–0.57: not confident enough to reject, never confident enough to
  accept.
- Cost of that perfection on this set: 69% of gated instances escalated or
  were rejected to the big tier. On a natural stream the rates would be far
  lower (FAM disagreement-with-BIG rate ≈ 9%; TRAP's ≈ 35%) — the
  transferable claim is not the 100%, it's that **Jev's pos band is
  trustworthy and its zero band routes cost to exactly the instances the
  cheap tier gets wrong**.

## The staircase (prune results)

| Cell | Final staffing | Big tier worked out of |
|---|---|---|
| FAM | ALGO for token-family repos; SMALL for token-OTHER tail; BIG only as fused-name watch (2 cells) + validation | **395/395 production cells** |
| TRAP | **Not pruned.** BIG keeps every verdict; cheap tiers demoted to watch-flags (per Jev, 0.90) | 0% |
| PILLAR | Unresolved — ALGO candidates stand unconfirmed (per Jev, 0.96) pending a SMALL re-run and a real standard | unmeasured |
| DISP | Formula over ALGO cells by default; pillar-bearing tail/fork escalate | ~85% (formula + targeted escalation), capped at the 80.7% ceiling |

Whole sheet (1,580 cells): ALGO 1,356 (85.8%), BIG 126 (8.0%), SMALL 62
(3.9%), Jev-gated 36 (2.3%). Staffed-sheet correctness: FAM 367/395 vs GOLD
(the 28 misses are semantic-vs-token divergences plus the 2 deliberate
BIG-watch overrides GOLD scores wrong and REF scores right), PILLAR 280/395
vs SILVER, DISP 304/395 vs SILVER, TRAP 119/119 vs REF (BIG-staffed
subsample; the other 276 are watches, not verdicts).

**Economics** (illustrative relative units — ALGO 0.001, SMALL 1, BIG 25,
Jev 2/gated cell; the ratios are the content, not the units): all-BIG grid =
39,500 units; the staffed grid = **3,285 units (8.3%)**. Honest caveat: part
of that saving is cells staffed at *unconfirmed* quality (PILLAR candidates,
TRAP watches). The saving at *confirmed* quality — FAM and DISP — is real
but smaller; the unconfirmed part is a loan against the re-run.

## What the decomposition got wrong (mis-cut findings)

1. **FAM is two cells wearing one coat.** In big families it is a formula
   (the naming convention); in the tail it is a semantic judgment. One cell
   type, two jobs — every metric, gate, and staffing rule only makes sense
   per-stratum. The next decomposition should split it.
2. **TRAP conflates *vague* with *misleading*, on a 3.4% base rate.** Cheap
   deciders flag 29–35% of repos because an under-informative name *feels*
   suspect. Worse, TRAP as cut (name vs description) **cannot catch the
   famous trap**: `zero-knowledge` passes TRAP cleanly — its name and
   description agree; the trap is program-relevance, which lives in
   FAM/PILLAR. The survey's own §C catch would sail through this cell.
3. **A cell is only as checkable as its standard.** PILLAR's keyword silver
   standard is weaker than the deciders it would judge (BIG agrees with it
   only 59.7%). We built a gate before building the yardstick.
4. **DISP is missing an input, not a decider.** Perfect upstream cells cap
   the formula at 80.7%; the residual is instance-substance (stub vs
   substantive, pattern vs instance). Add a SUBSTANCE cell or accept the
   ceiling.
5. **The output enums lack NO-SIGNAL.** For the 48 no-description repos,
   TRAP/PILLAR have literally no evidence; every decider was forced to
   guess in-band. (Jev rejected blanket escalation for them — but the honest
   cell output is "no signal," a value the decomposition never offered.)
6. **Gates belong on instances, not cell types.** Jev rejected or deadbanded
   4 of 7 blanket policy rules, then went 11/11 on instance accepts. Policy
   is a prior; the gate is a per-instance act with evidence in hand. (This
   answers the seed notes' open question on gate granularity — with data.)
7. **Operational: batch pacing is a gate too.** The run's one excursion was
   self-inflicted — three concurrent batch loops tripped the provider's
   429. The provider has a deadband; hammering it is an excursion like any
   other, and the sheet records it.

## Open questions

1. **Re-run SMALL, paced** (one loop, sequential batches): PILLAR + DISP +
   the 367 unanswered FAM/TRAP cells. ≈100 calls. Until then two
   staircases stay open.
2. **Re-cut TRAP**: split COLLISION (famous-word/program traps — the
   zero-knowledge shape) from VAGUE (name under-specifies)? Or retire TRAP
   to a pure watch, as Jev's 0.90 suggests?
3. **Add the SUBSTANCE cell** upstream of DISP — or is 80.7% the right
   price for a formula?
4. **Jev's FAM dissent**: token-family matched semantics on 98.3% of the
   labeled subsample — but the tail is 45% of the account and largely
   unlabeled. Is GOLD itself due to be re-based on semantic labels?
5. **NO-SIGNAL as a first-class output** on every cell — and should a
   NO-SIGNAL cell escalate by definition?
6. **Rule vs allocation**: when Jev's rule-verdict (disagreement alone:
   neg 0.20) and its budget choice (spend on disagreements: 0.51) conflict,
   which governs the gate policy?

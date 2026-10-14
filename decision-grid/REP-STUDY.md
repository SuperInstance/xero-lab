# REP Study — can representativeness lift the DISP ceiling?

*2026-10-13, appendix to RESULTS.md (which is unchanged). Question, from the
re-run's open question 1: the DISP formula fed perfect upstream cells caps at
**80.7%** against the strong-model reference (REF, n=119), and the SUBSTANCE
cell did not move it — the residual was diagnosed as **representativeness**:
substantive family members the reference rates *representative, not
exceptional*. This study defines a cheap REP signal, computes it for all 395
sample repos, and tests whether DISP + REP beats the ceiling.*

## Verdict, first

**Yes — the ceiling lifts, and the lift survives held-out testing.** DISP +
REP scores **89.9%** on the perfect-input chain (was 80.7%) and **89.1%** on
the production ALGO chain (was 78.2%). Split-half validation (thresholds
tuned on one half, tested on the other) reads **89.8% / 90.0%** held out,
against 79.7% / 81.7% for the base formula on the same halves. Across both
chains REP's combined rule makes 27 flips against the base formula: 25
errors fixed, 1 error moved to a different wrong label, and exactly **1
correct call broken** (`quilt-matrix`, on the perfect chain only).

The residual 12 errors (perfect chain) are a different problem than the one
REP solves: 6 are family-less instances, where representativeness has no
family to be relative to and no cheap feature separates instance from
pattern-bearer; 3 are marginal family members; 2 are family cases no
component sees. **The ceiling moves from 80.7% to ≈90%; it does not
dissolve.**

Recommendation: **adopt REP as a fifth cell** — Jev `choice` on the
adoption form: fifth_cell 0.63 (confidence 0.51) over clause-in-DISP 0.33,
fold-into-FAM 0.02, drop 0.02; Jev `noul` on the final three-component
signal: **0.76** (the accept band). Both calls logged in
`data/jev_rep_call.json`.

## What the data can and cannot support

`data/sample.jsonl` carries exactly six fields per repo: `name`, `d`
(one-line description), `l` (language), `fork`, `gold_family`, `stratum`.
Candidate REP signals, audited against that reality:

| Candidate signal | Computable? | Finding |
|---|---|---|
| Pillar-typicality within family | yes | works (component 1) |
| Description overlap with family centroid | yes | works (component 2) |
| Language = family's modal language | yes | works, strongest single component (component 3) — mechanism caveat below |
| Name shape vs family (bare / family-led / fused) | yes | no separation on any boundary; not used |
| Fork status ("stray fork" gate) | yes | **net zero** — fixes `agentkernel`, breaks `MerkleMesh`; rejected |
| **Size / file count / LOC vs family median** | **no — not in the data** | — |
| **Activity (commits, last push, stars, issues)** | **no — not in the data** | — |
| **Content beyond the one-line description** | **no — not in the data** | — |
| Full-account family statistics | no — only the 395 sample is published; in-sample family sizes are the denominators (small for some families; hermes has no modal language at all) | — |
| Dependency/usage centrality | no — not in the data | — |

`stratum` was deliberately **not** used as a feature: it records how the
sample was drawn (spotlight repos were hand-picked), so it would leak the
sampling design into the signal.

## The REP signal

Representativeness, made relational and mechanical — *a repo is
representative of its family to the extent that its marks are the family's
mainstream marks*:

1. **REP-typicality**: for a family member with pillar tags, the maximum
   over its pillars of that pillar's prevalence among the family's sampled
   members (keyword tags). A `plato-*` repo whose memory-grid tag is shared
   by 58% of sampled plato repos is carrying the family line, not exceeding
   it.
2. **REP-overlap**: the share of the repo's description words appearing in
   the leave-self-out family centroid (words used by ≥2 other members).
3. **REP-tongue**: the repo's language is its family's modal language —
   it is written in the family's common tongue, one of the family's
   regular production members. (The reference's family DEEPs are
   disproportionately the language-odd artifacts: theory cores, kernels,
   spec repos with no language at all.)

**REP class**: `ROUTINE` if typicality ≥ 0.30, or overlap ≥ 0.30, or the
tongue fires; `DISTINCT` if it has readings and none fire; **NO-SIGNAL**
for family-less repos and the rare member with no readings at all
(186 of 395 — REP is silent there, by construction).

Use in DISP (the only rule tested): formula says DEEP, repo is a family
member, repo is not a curated anchor, REP = ROUTINE → **COLLAPSE**.
Anchors are exempt: curated knowledge outranks the statistic (`zero-poc`
is a fork SMALL called a stub, and it is DEEP; no statistic in this study
overrules the anchor list).

Cost: **zero model calls.** REP is ALGO-tier arithmetic over data already
in the sheet, computed for all 395 repos in `data/rep_values.jsonl`
(class mix: ROUTINE 182, DISTINCT 27, NO-SIGNAL 186). The three
components are recorded as separate columns precisely so any one of them
can be pruned without touching the others — this matters most for the
tongue (see caveats).

## The error anatomy REP had to work on

Base formula on perfect inputs, reproduced exactly: 96/119 = 80.7%.
Confusion: pred DEEP 34 (14 right), pred COLLAPSE 45 (42 right), pred
TAIL 40 (40 right). **The formula never misses a reference DEEP and never
wrongly says TAIL — every one of the 23 errors is an over-call**, in
three classes:

| Error class | n | Shape |
|---|---|---|
| DEEP → COLLAPSE | 14 | family members whose pillar tags fired the DEEP clause; reference: representative, not exceptional |
| DEEP → TAIL | 6 | family-less, pillar-bearing; reference: mere instances (`jc1-research`, `openmind-conductor`) |
| COLLAPSE → TAIL | 3 | marginal family members (`fleet-automation-early-version`, `quilt-jev-toolkit-push`, `quiltcall`) |

## Results — DISP with and without REP (vs REF, n=119)

| Chain | Base | + typicality | + overlap | + tongue | + REP (all three) |
|---|---|---|---|---|---|
| Perfect inputs (BIG FAM/PILLAR) | 96/119 = **80.7%** | 84.9% | 83.2% | 87.4% | **107/119 = 89.9%** |
| Production (ALGO cells; REP from ALGO tags) | 93/119 = **78.2%** | — | — | — | **106/119 = 89.1%** |

(Two-component REP — typicality + overlap — scores 86.6% perfect /
84.0% production. The tongue is what carries the result from "solid" to
"ceiling moved"; it is also the least understood component. Both facts
are on the record, in that order.)

Flip accounting (every changed call, counted):

- **Perfect chain, all three components**: 13 flips vs base — **12 fixes,
  1 break**. Fixes: `hermes-memory-mcp`, `plato-adapters`,
  `plato-provenance`, `plato-room-phi`, `plato-tile-fountain`,
  `plato-tile-split`, `substrate-forge`, `ternary-mesh`,
  `agent-polyrhythm`, `flux-compiler-agentic`,
  `flux-cooperative-intelligence`, `oxide-constructs` (all DEEP→COLLAPSE,
  all matching REF). Break: **`quilt-matrix`** — the quilt family's
  flagship, correctly DEEP, downgraded by the tongue (it is written in
  the family's modal language, Python). It is the price tag on component
  3, named rather than averaged away.
- **Production chain**: 14 flips vs base — 13 errors fixed, 1 moved
  (`fleet-automation-early-version`: DEEP→COLLAPSE, REF is TAIL; wrong
  before, wrong after), **0 correct calls broken**. The fleet line is the
  showcase: ALGO tags every `fleet-*` name with a pillar, so the whole
  family reads DEEP to the base formula; REP reads typicality 1.0 and the
  Python tongue and collapses them, as REF does.

Validation against self-deception:

- **Split-half, each component and the combination** (thresholds tuned on
  one half only, tested on the other; halves split by name parity):
  typicality alone +2/+2 repos held out; tongue alone +4/+4; the full
  combination held out at **89.8% and 90.0%** vs base 79.7% / 81.7%, and
  ≥ the two-component REP in both directions. The independently tuned
  thresholds landed at (0.30, 0.25) and (0.25, 0.25), next to the
  pre-registered (0.30, 0.30) — not a knife's edge.
- **Per-family replication of the tongue** (the component most likely to
  be one family's artifact): its 10 in-sample flips span 6 families —
  agent 1 fix / 0 breaks, flux 2/0, oxide 1/0, plato 4/0, ternary 1/0,
  quilt 0/1. Positive in 5 of 6 families it touches.

## The residual — where REP is silent, and why

12 errors remain on the perfect chain: 6 DEEP→TAIL (family-less), 3
COLLAPSE→TAIL (marginal members), 2 DEEP→COLLAPSE (`flux-stigmergy-c`,
`plato-runtime-kernel`), 1 COLLAPSE→DEEP (`quilt-matrix`, REP's own
break). Notes on each silence:

- **The family-less boundary is feature-blind.** REP is undefined there
  by construction, and nothing else cheap separates it either:
  `agentkernel` (REF TAIL) and `reposphere` (REF DEEP) have near-identical
  cheap profiles (1-token names, 15–17 description words, top-decile
  description distinctiveness); fork status splits 1–1 (`agentkernel`
  vs `MerkleMesh`). The re-run's suspicion — *a representativeness cell
  that is the decision itself is not a decomposition* — is **confirmed
  for the tail**: with no family to be representative *of*, the question
  collapses into the disposition judgment. It stays BIG/escalation work.
- **Marginal members** (COLLAPSE→TAIL): no feature separates the 3 from
  the 42 correct COLLAPSEs; a no-description rule would break 8 correct
  calls to fix 1.
- **`flux` is REP's blind family**: its members' pillars are rare
  in-family and its routine members write distinctively — two of three
  flux errors needed the tongue to fall, and `flux-stigmergy-c` (a fork,
  in C) still stands.

## Caveats, on the record

1. **n=119 is the whole evidence.** The lift survives split-half at two
   different splits and per-family replication, but read 89.9% as
   "≈88–90%", not as a constant of nature.
2. **The tongue's mechanism is post hoc.** It is an empirical regularity
   of *this* library and *this* reference rater (pattern-bearers skew
   language-odd). On a differently styled account it could weaken or
   invert. It is therefore recorded as its own component, and it is the
   first thing to re-validate when the REF labels are extended (the
   re-run's open question 3 — more labels — is now also REP's top
   dependency).
3. **Typicality is only as good as the tagger it counts.** The
   perfect-chain test counts prevalence with SILVER keyword tags while
   the repos' own pillars are BIG's (deliberate asymmetry: prevalence is
   a library statistic); the production test is tier-consistent (ALGO
   throughout), where typicality partly measures ALGO's own keyword echo.
   Both chains improve; neither reading is the pure one a BIG-tagged
   library would give.
4. **Small denominators.** In-sample family sizes are stratified samples;
   hermes' typicality of 1.0 rests on a handful of members (and hermes
   has no modal language, so the tongue cannot fire there). Removing
   hermes from the perfect-chain result leaves 11 fixes, 1 break — the
   conclusion does not rest on it.
5. **REP inherits the grid's yardstick problem.** All scoring is fidelity
   to REF. REP is validated as "reproduces the reference's dispositions
   better," nothing more metaphysical.

## Recommendation

**Adopt REP as a fifth cell**, ALGO-staffed, formula-computed, with
NO-SIGNAL as its honest output for the 186 repos it cannot speak about —
which also gives the grid its first working instance of the NO-SIGNAL
output class (open question 5). It has one consumer today (DISP), but as
a cell it is inspectable, watchable, and re-staffable in the way the
grid's doctrine asks of everything in the sheet; buried as a clause
inside `disp_rule`, the same arithmetic would be invisible to gates.
Jev's gates, asked twice (form on two-component evidence; adoption on
final evidence), concur: **choice fifth_cell 0.63** (conf 0.51), then
**noul 0.76** on the three-component signal.

Disposition of the re-run's open question 1: representativeness *is*
the DISP residual's name for family members, and there it is relational,
cheap, and decomposable — a real cell, not the decision in disguise.
For the family-less tail it is the decision in disguise, and this study
leaves it there, with the boundary now measured instead of suspected:
**14 of the 23 ceiling errors were the DEEP→COLLAPSE family-member
class, and REP fixes 12 of those 14 at the cost of 1 break.**

## Method / artifacts

- Code (new, appendix only; no published file modified):
  `code/rep_study.py` (ceiling reproduction + error anatomy),
  `code/rep_study2.py` (features + variants + split-half),
  `code/rep_study3.py` (flip accounting, production chain, REP for 395).
- Data (new): `data/rep_values.jsonl` (REP, per component, for all 395),
  `data/jev_rep_call.json` (both Jev calls, full context).
- Model calls in this study: **MiniMax 0** (no labeling was needed — REP
  is deterministic; the pacing gate was therefore never engaged),
  **Jev 2** (1 `choice`, 1 `noul`).
- RESULTS.md and all published grid code/data: untouched.

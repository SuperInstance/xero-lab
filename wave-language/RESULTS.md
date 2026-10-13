# RESULTS — the wave-language proof of concept

*Run 2026-10-13. Reader: MiniMax-Text-01, zero-shot, temperature 0.2,
JSON-only answers. 36 synthetic seas, each generated once and read
under four encodings. Jev consulted once at the end (receipt below).*

## Headline

Casey's claim splits in two, and the two halves score differently:

- **Compactness: CONFIRMED, decisively.** Letters cost **6.5× fewer
  tokens** per reading than numeric grids (15× at coarse
  resolution). And a whole day at sea, written down: 46 MB as raw
  numeric text, **9.98 MB as full letter frames, 0.99 MB as a
  logbook letter log** (12×12 at a 5 s pulse, ≈0.12 MB/hour) —
  a file any edge computer can hold whole, with room for a season.
- **Zero-shot legibility: NOT confirmed.** The untuned model reads
  the sea poorly in *every* encoding — period and set-pattern at
  chance, direction weakly above chance, trend destroyed by a prior.
  **But letters lose nothing to numbers**: on every question the
  letter encodings match or beat the raw numeric grids that cost
  6.5–15× more. The rendering is not where the information dies.
  The reader is. Which is what the seed actually prescribes: the
  model must be *tuned* to waveforms as a language — this test
  measures the floor before any tuning, and the floor is low.

## A scar on this run (read before quoting any number)

MiniMax rate-limited the run hard: **59 of 144 calls died on HTTP
429** despite in-harness retries (12–18 per condition). Every call
that completed returned clean, parseable JSON (0 parse failures).
Results below are therefore **answered-only** (n = 24 / 22 / 21 / 18
per condition), the pairing across conditions is partially broken,
and the answered subsets' truth mixes differ slightly. Effect sizes
should be read as indicative, not precise. A re-run at lower
concurrency would tighten everything here; the qualitative pattern
is consistent enough across four independent conditions that the
conclusions below are unlikely to flip.

## Reading accuracy (answered-only; chance in brackets)

| condition | n | direction [12.5%] | dir ±45° [37.5%] | period [—] | trend [33%] | sets [25%] | prompt tokens |
|---|---|---|---|---|---|---|---|
| letters 20×20 | 24 | **0.21** | 0.50 | 0.00 | 0.38 | 0.29 | 11,300 |
| letters 12×12 | 22 | **0.23** | 0.41 | 0.09 | 0.32 | 0.18 | 4,866 |
| numeric 20×20 | 21 | 0.14 | 0.48 | 0.05 | 0.24 | **0.38** | 73,582 |
| summary (buoy+stats) | 18 | 0.22 | 0.61 | 0.00 | **0.44** | 0.17 | 1,971 |

- **Direction** is the letters' best question: exact-match ~1.7×
  chance at both resolutions, and the compass-distance histogram
  shows a real bump at 0–1 steps with **no clustering at the
  opposite point** — the model is not systematically reporting the
  mariner's "from" direction; it sees *some* motion, weakly.
  (The summary control's 0.61 at ±45° has no spatial information to
  stand on and is treated as small-n luck, n=18.)
- **Period is unreadable zero-shot, everywhere** (0–9%). From grids
  the model guesses systematically *short* (median error −2.6 to
  −3.5 s on 6–10 s seas); from the buoy series it guesses *long*
  (+3.9 s), apparently latching onto set-group or beat rhythms.
  Counting seconds between crests across 45 text frames is simply
  not something the untuned reader does.
- **Sets are pattern-completed, not counted.** The model almost
  never answers "none" — in letters20, 0 of 24, against 6 continuous
  seas in the truth mix. It answers "3" or "4" the way it might
  answer "a few": as the generic sea.

## The failure that explains the trend row

**The model believes seas build.** In letters20 it answered
"building" for **24 of 24** streams (truths: 9 building, 9 easing,
6 steady); in numeric 18 of 21; it answered "easing" essentially
never in any grid condition. Its trend score is just the base rate
of "building" in the sample. Two candidate causes, both filed
honestly: (1) a genuine prior in the model — seas in its training
text are usually described as building; (2) a confound in my
generator — every stream opens at the start of a set envelope
(envelope phase 0), so the first thing any reader sees is a set
growing. The summary condition shows the same bias (13/18 building)
even where max-height visibly halves, which points mostly at (1),
but (2) is a real design flaw: a v2 should randomize the stream's
starting phase in the group cycle.

Quoted failures (verbatim answers in `runs/reading_results.jsonl`):

- letters20, stream 0 — truth: NW, 9 s, **easing**, sets of 3.
  Answered: **SE, 5.0 s, building, sets of 5.** Wrong on all four.
- letters20, stream 31 — truth period 7.0 s; answered 12.5 s.
- summary, stream 1 — truth sets: **none** (continuous sea);
  answered sets of 4, period 12.5 s, "building". The reader invents
  the rhythm it expects.

## Compactness — a day at sea (8 h, SW swell, T = 8 s, sets of 5, building)

Stream cadence = frames every 1.25 s at 20×20 (23,041 frames).
Logbook pulse = frames every 5 s at 12×12 (5,761 frames).

| encoding | stream cadence | logbook pulse | vs raw numeric (stream) |
|---|---|---|---|
| raw numeric text | 46,386,706 B | 4,234,652 B | 1.00× |
| letters, full frames | 9,981,926 B | **985,448 B** | 0.22× |
| naive per-cell delta | 49,306,397 B | 4,526,645 B | 1.06× |
| deadband delta (≥2 levels) | 25,988,815 B | 3,034,478 B | 0.56× |
| letters + gzip | 2,807,112 B | 310,322 B | 0.06× |

Per hour: stream-cadence letters ≈ 1.25 MB/h; **logbook letters
≈ 0.12 MB/h**. A season of logbook days is a few hundred MB. The
day-log as training set is entirely practical — that half of the
vision has no numbers problem.

*(Correction, 2026-10-13: an earlier draft of this table carried
figures ~45× too large, from a corrupted first pricing run. The
numbers above were re-measured and verified two independent ways,
including hand-checkable per-frame arithmetic: 431 chars/frame
letters, 2,011 chars/frame numeric.)*

## The delta verdict (a doctrine takes a hit)

The delta-vector idea — *emit only what changed* — **loses** on wave
fields in its naive form, and it isn't close: a coordinate token
(`r12c17#`, ~6 chars) costs ~6× the single letter it replaces, and a
wave field in motion changes 60–88% of its letters between frames at
any cadence tried. The deadband repair (re-emit a cell only after it
moves ≥2 letter levels — the gate doctrine applied to logging)
recovers a lot (naive 49.3 MB → 26.0 MB at stream cadence) but still
loses to just writing the frames (9.98 MB), because the changes are
*broad and coherent*, not sparse. Delta encoding pays on sparse,
event-like change; a sea is the opposite — everything moves, a
little, all the time. Where the compactness actually comes from, in
order: **letters ≪ numbers (4.7×), cadence × resolution (another
~18× to the logbook), gzip (~2.3× more)**. If a v2 wants real delta
savings it should delta in a motion-compensated or spectral basis,
not cell-by-cell — or accept frames and let the compressor work.

## Jev receipt

Asked (TypeSafe Jev, `noul`, 2026-10-13) whether the evidence
justifies "the bottleneck is the untuned reader, not the letter
rendering; next step is tuning a reader on labeled synthetic seas":
**0.73 — yes.**

## What this PoC actually produced

The durable asset is not the scores; it's the **generator**: an
endless supply of seas with exact labels (direction, period, trend,
sets) at any resolution and cadence. That is precisely the training
set Casey's seed calls for — tune a small reader on generator
output, grade it against ground truth, prune what it doesn't need.
Zero-shot was the control condition for that program, and its
result is the program's justification: the language is cheap and
lossless-enough; the reader must be raised, not found.

## Open questions / v2 list

1. **Tuning run**: fine-tune or distill a small reader on generator
   streams; how few examples until direction/period clear 80%? Does
   trend survive once the "building" prior is trained against
   balanced labels?
2. **Let the reader reason**: JSON-only answers forbade chain-of-
   thought. Does a short visible work-through (count the crests,
   track one crest line) lift period/sets?
3. **Fix the confounds**: randomize set-envelope start phase; rerun
   at concurrency ≤3 with a retry budget so n=36 pairs stay intact.
4. **Phase rendering**: the notes ask whether the grid should render
   *phase* rather than height (crest lines as trajectories). A
   crest-line-only rendering is far sparser — does the reader do
   better with the motion pre-extracted, or is that rebuilding the
   signal processing the seed wants to skip?
5. **Throw**: this test covered direction/period/trend/sets. The
   helmsman's third gist — how the sea *throws* the boat — needs a
   boat-response model in the generator before it can be tested.

## v2 — raising the reader (2026-10-13)

The v2 list above asked three things: fix the confounds, let the
reader reason, and tune it with labeled examples. All three were
done. The result is sharper than a simple win: **examples teach
exactly one of the four skills, and the work-through exposes why
the other three fail.**

### Confound fixes (generator v2)

- **Set-envelope phase randomized.** v1 opened every stream at
  envelope phase 0 — the start of a set (diagnostic: 100% of v1
  streams opened in-set, envelope(0) = 0.30 ± 0.00). Generator v2
  (`sea.py`, `GENERATOR_VERSION = "2"`) draws a uniform starting
  phase per sea; v2 streams open in-set 76% of the time with
  envelope(0) spread 0.60 ± 0.27 across the cycle. The phase is
  drawn *after* every v1 draw, so `env_phase0=0.0` reproduces all
  144/144 v1 streams bit-for-bit (verified against the seed-4242
  battery) — v1 stays reproducible, v2 is honest.
- **Balanced labels.** The held-out set is exactly balanced by
  construction (asserted in code): trends 12 building / 12 easing /
  12 steady; sets 9 each of 3 / 4 / 5 / none; directions 4–5 per
  point; periods spread over 6–10 s. Under v1's unbalanced
  answering, a label prior could masquerade as skill; here it can't.
- **Pairs stay intact.** Strictly sequential calls (concurrency 1),
  ≥3 s between calls, exponential backoff 30/60/120/240 s armed on
  any 429 with a hard abort if one survived. **Outcome: 126/126
  calls recorded, 126/126 parsed, zero 429s, zero backoffs** — the
  v1 scar (59/144 lost) did not recur. (One call was lost to a
  service restart mid-run; the resumable runner re-did exactly that
  pair. Total tokens: 3.40M prompt, 50k completion.)

### Route chosen

Few-shot prompting with *worked* examples + a visible work-through
before the JSON — the strongest lever available without training
infrastructure, and the one v1's list prescribed. The four examples
(`authoring.py`) are generator seas whose work-throughs are
**measured from the frames** by deterministic estimators (FFT
direction, buoy-peak period, bright-cell trend, SET/LULL set
structure); an example enters the pool only if every estimate
agrees with ground truth, so no worked solution teaches a wrong
number. Doses are nested (K=1 ⊂ K=2 ⊂ K=4): K=0 is the
work-through instruction alone. Held-out: 36 fresh v2 seas
(seed 90210), letters 20×20, scored with v1's scorer unchanged.

### The dose curve (accuracy; v1 zero-shot floor in the first row)

| dose | n | direction | dir ±45° | period | trend | sets |
|---|---|---|---|---|---|---|
| v1 (JSON only) | 24 | 0.21 | 0.50 | 0.00 | 0.38 | 0.29 |
| K=0 (work-through only) | 36 | 0.14 | 0.33 | 0.08 | 0.36 | 0.22 |
| K=1 | 18 | 0.17 | 0.33 | 0.33 | 0.33 | 0.11 |
| K=2 | 36 | 0.03 | 0.14 | 0.50 | 0.31 | 0.25 |
| K=4 | 36 | 0.14 | 0.39 | **0.61** | 0.44 | 0.19 |
| chance | | 0.125 | 0.375 | — | 0.33 | 0.25 |

**Period is the one real win, and it is dose-shaped**: 0.00 → 0.08
→ 0.33 → 0.50 → 0.61, mean error falling 4.2 s → 1.2 s. Counting
peaks at the centre cell is a procedure the reader can actually
execute on a letter grid — discrete peak times in one column are
legible — and the examples genuinely teach it.

**The "seas always build" prior did not die; it moved.** Under
balanced labels the trend answers are prior-driven at every dose,
and the prior's *label follows the prompt*: K=1 (one example,
building) → "building" 14/18; K=2 (last example easing) →
"easing" 30/36; K=4 → "steady" 27/36; K=0 → "steady" 32/36.
Trend accuracy never beats 0.44. The reader is not measuring the
bright-cell counts its work-through recites — the counts in its
text are round, repeated, and asserted (≈150 vs ≈150 → "steady")
— it is adopting whichever label the prompt makes salient. v1's
"building prior" was this same mechanism wearing v1's prompt.

**Direction gets worse with a work-through, not better**
(0.21 v1 → 0.03–0.17), because band-tracking is theatre: the model
writes a plausible shift and the compass follows the prose. At K=4
it answered **SE on 36 of 36 streams** (its 0.14 is exactly the
share of SE truths); at K=2 the attractor rotated to SW/NW. A
typical dose-4 reading, truth SW:

> "we notice that the pattern shifts approximately 1 cell east and
> 1 cell south. This indicates that the wave train is traveling in
> the **SE** direction."

**Sets never reach v1's floor.** The marker procedure is recited
correctly and executed on a misread marker structure. Dose-4,
truth sets of 5:

> "The stream has a single '--- SET ---' marker at the beginning
> and a '~~~ LULL ~~~' marker at t = 7.5 seconds. The time between
> these markers is 7.5 seconds, which corresponds to less than one
> complete wave cycle … so sets = none."

("none" flooded 19/36 at K=4 against 9 truths; at K=0 the model
instead divided stream length by period and answered 18 waves per
set.) Part of this is real task hardness — a 55 s window against
set cycles up to 64 s often shows no complete group — but the
reader neither notices the truncation nor falls back the way its
own instructions describe.

The pattern across all four: **the work-through transfers the
script, not the measurement.** Where the measurement is executable
in text (count peaks in one column), accuracy climbs with dose.
Where it is not (track bands across 44 frames, count hundreds of
cells, reconstruct marker runs), the model produces the *form* of
the procedure with fabricated numbers, and a label prior decides
the answer. More examples sharpen the script; they do not give
the reader eyes.

### What this means / what's next

- **Prompting is pruned as the reader route** — this is the prune
  the dose curve was bought for. K=8 would polish the theatre.
- The two live routes are the ones that change *who measures*:
  (a) a deterministic pre-reader that computes the four statistics
  (the authoring estimators already do, exactly) and renders them
  as text for the LLM to judge — separating measurement from
  judgement; or (b) a genuinely trained small reader on generator
  data (the generator is an unlimited labeled training set; the
  jev-student pattern), which v1's list already pointed at.
- Phase rendering (v2-list item 4) stays open and now looks
  better-motivated: if the motion is pre-extracted, the reader's
  job shrinks toward the period task — the one it proved it can do.

**Jev receipt (v2).** Asked (TypeSafe Jev, `noul`, 2026-10-13)
whether the dose-curve evidence justifies "worked examples teach
the reader only the skill it can actually execute in text (period);
the other work-throughs are recited scripts with fabricated
measurements decided by a label prior; prompt-tuning the reader is
therefore exhausted — the measurement must move out of the LLM":
**0.59 — yes.** Cooler than v1's 0.73, as it should be: the period
half of the claim is measured fact, the "script, not measurement"
half is an inference — from the answer distributions and the
readings quoted above — and the receipt prices it that way.

## v3 — who measures (2026-10-13)

The v2 section left a fork: (A) a deterministic pre-reader measures
and the LLM judges, or (B) a genuinely trained small reader learns
to measure. v3 ran **both, head-to-head, on the same 36 fresh seas**
(seed 777001, generator v2, balanced labels, v1's scorer unchanged).
Pacing held again: the route-A judge's 36/36 calls completed with
zero 429s; everything else in v3 is local compute.

### The comparison (accuracy; chance: dir .125, dir±45 .375, trend .33, sets .25)

| condition | n | direction | dir ±45° | period | trend | sets | cost / reading |
|---|---|---|---|---|---|---|---|
| v1 zero-shot, letters 20×20 * | 24 | 0.21 | 0.50 | 0.00 | 0.38 | 0.29 | 11,300 tok |
| v2 K=4 worked examples * | 36 | 0.14 | 0.39 | 0.61 | 0.44 | 0.19 | 45,230 tok |
| **A — estimators alone** | 36 | **1.00** | **1.00** | **1.00** (err 0.3 s) | **0.67** | **0.75** | 0 tok, 21 ms CPU |
| **A — estimators + LLM judge** | 36 | **1.00** | **1.00** | **1.00** (err 0.3 s) | **0.67** | **0.75** | 371 tok |
| B1 student @512 seas | 36 | 0.08 | 0.31 | 0.61 (err 1.5 s) | 0.36 | 0.22 | 0 tok, <1 ms |
| B1 student @2048 | 36 | 0.17 | 0.31 | 0.44 (err 2.0 s) | 0.36 | 0.19 | 0 tok, <1 ms |
| B1 student @8192 | 36 | 0.11 | 0.36 | 0.39 (err 2.1 s) | 0.33 | 0.25 | 0 tok, <1 ms |
| B2 student +motion @2048 | 36 | 0.81 | 0.89 | 0.97 (err 0.2 s) | 0.33 | 0.31 | 0 tok, <1 ms |
| B2 student +motion @8192 | 36 | 0.92 | 0.94 | **1.00** (err 0.1 s) | 0.53 | 0.50 | 0 tok, <1 ms |

\* v1/v2 rows are the published baselines on their own held-out sets
(v1 seed 4242, pairs partially broken by the 429 scar; v2 seed
90210). Every v3 row shares seed 777001 — the route comparison
inside v3 is exactly paired.

### Route A — the instrument measures; the judge speaks

The pre-reader (`prereader.py`) wires the v2 authoring estimators
into a standalone instrument: FFT direction and buoy-peak period
from the field, bright-cell trend, set structure from the rendered
marker channel and the *estimated* period. Nothing is admitted or
rejected against ground truth — dead zones are reported, not hidden.

- **Direction and period are solved** on synthetic seas: 36/36
  each, period mean error 0.3 s. These were the LLM's two worst
  questions across v1 and v2.
- **Trend 0.67, with structured errors.** Misses bleed to the
  adjacent class (building→steady 3, easing→steady 4, steady split
  both ways) — the slope statistic fighting the set envelope, not a
  prior: answers run 10/14/12 against a 12/12/12 truth mix. There
  is no "building" flood anywhere on route A.
- **Sets 0.75 = 27/27 when callable + 9 honest unknowns.** Every
  miss is the estimator declining to call a window-truncated group
  ("no complete set fits"). When it answers, it is right.
- **The judge's measured added value is exactly zero.** Given only
  the brief (371 tokens — 30× cheaper than v1's frame-reading,
  120× cheaper than v2's K=4), MiniMax **fixed 0 and broke 0** on
  every question. It overrode the instrument only where the brief
  declared a dead zone — the 9 unknown sets — and there it guessed
  "none" 9/9 times, all wrong: in a dead zone, the LLM's default is
  a prior wearing a uniform. What the judge *does* produce is the
  tongue: fluent one-line seamanship, faithful to the instrument
  including its errors ("…a steady 10-second period and consistent
  4-wave sets" for an easing sea the instrument misread as steady;
  its prose once rendered direction in the mariner's FROM
  convention while its JSON held the correct TO).

### Route B — the student must be fed motion

The student (`student.py`) is a numpy MLP — 439,604 parameters,
letter frames 2×2-pooled to 4500 inputs, four softmax heads —
trained locally on generator seas (pool seed 555000, disjoint from
every test seed). **As specified, it fails**: direction, trend and
sets sit at chance at all three doses, and the dose curve is flat
because the model underfits its own training seas (final training
accuracy on direction 0.11–0.19). Its period row (0.39–0.61) is a
tolerance artifact — exact-class accuracy is ≈chance and mean
error is 1.5–2.1 s; an always-≈8 s answer scores ~0.60 under v1's
tolerance on a uniform 6–10 s mix, so read this table's period
column by mean error. More data changed nothing: the bind was the
representation, not the dose.

The diagnostic variant (`student_motion.py`, B2) adds one thing —
pooled frame-to-frame letter differences as a motion channel
(862,004 parameters, 30 epochs) — and the two *phase* questions
fall immediately: direction 0.81 → **0.92** and period 0.97 →
**1.00** (error 0.2 → 0.1 s, matching the FFT instrument) across
2048 → 8192 seas. Trend and sets climb more slowly (0.33 → 0.53,
0.31 → 0.50) and remain well behind the estimators (0.67 / 0.75);
the student is still fitting them (training accuracy 0.66 / 0.58),
and its trend answers spread 15/13/8 — no flood, no language prior,
just weaker envelope extraction. This is v2's law from the other
side: **a student learns what its input makes executable.** Static
letters hid the motion; explicit differences handed it over.
Envelope questions need whole-window integration, which is what
the estimators were built to do and this MLP does poorly.

### The settlement

- **Who measures: the algorithms, today, on all four questions** —
  at ceiling on direction/period, in front on trend/sets, with
  honest unknowns instead of guesses, at 21 ms and zero tokens.
- **A trained reader is real but narrower**: with motion-explicit
  input it matches the instrument on direction/period and then
  runs in <1 ms with no instrument code — the candidate to replace
  the pre-reader exactly where silicon must be smallest. It has
  not earned trend or sets.
- **The LLM judges and speaks; it does not measure.** Its brief-
  only seat costs 371 tokens, transmits the measurements
  faithfully, writes the seaman's line — and must never be allowed
  to fill a dead zone, where its contribution is a confident
  default. The architecture that falls out is the decision brief's
  sequence, now measured rather than argued: pre-reader → brief →
  LLM as judge/tongue, with the student distilled later from the
  pre-reader's own labeled output (A is B's teacher; nothing here
  is wasted).
- **The "building" prior is a language artifact.** It appears in
  every LLM condition (v1's flood, v2's prompt-following floods,
  the judge's dead-zone "none") and nowhere in either measuring
  route — not in the estimators' symmetric errors, not in the
  trained student's spread answers.

**Jev receipt (v3).** Asked (TypeSafe Jev, `noul`, 2026-10-13)
whether the evidence justifies the per-question settlement above
— estimators measure, a trained reader can match them on
direction/period only with motion-explicit input, the LLM's added
measurement value over the brief is zero so it should judge and
speak but never measure: **0.83 — yes.** The warmest of the three
receipts (0.73, 0.59, 0.83), tracking how much of each claim was
measurement rather than inference.

### What's next

1. **Trend and sets are the open measurement problem**, now
   precisely located: an envelope-aware trend statistic (the
   slope-vs-envelope fight costs ~0.33), and a sets estimator for
   truncated windows (25% of seas) that reasons about partial
   groups instead of declining.
2. **Route B's envelope problem**: recurrence or envelope-scale
   features for trend/sets; the student replaces the pre-reader
   question-by-question as it earns each one.
3. **Throw** (carried from v1's list, still open): the helmsman's
   third gist needs a boat-response model in the generator.

## Files

`sea.py` (generator), `render.py` (renderer + delta encoders),
`reading_test.py` (paired test), `daylog.py` (compactness),
`make_samples.py`, `samples/` (viewable streams),
`runs/reading_results.jsonl` (every call: truth, answer, scores,
token usage), `runs/reading_log.txt`.
v2 additions: `authoring.py` (measured-work-through example
authoring), `tuning_test.py` (dose-curve tuning run),
`runs/v2_tuning_results.jsonl`, `runs/v2_tuning_log.txt`.
v3 additions: `prereader.py` (route A instrument: estimators +
brief), `route_a_test.py` (estimators-alone + brief-only judge run),
`student.py` (route B numpy-MLP student, doses 512/2048/8192),
`student_motion.py` (B2 diagnostic: motion-channel student),
`runs/v3_heldout_truths.json` (seed-777001 ground truth),
`runs/v3_routeA_results.jsonl`, `runs/v3_routeA_log.txt`,
`runs/v3_routeB_results.json`, `runs/v3_routeB_log.txt`,
`runs/v3_routeB2_results.json`, `runs/v3_routeB2_log.txt`.

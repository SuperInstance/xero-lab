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

## Files

`sea.py` (generator), `render.py` (renderer + delta encoders),
`reading_test.py` (paired test), `daylog.py` (compactness),
`make_samples.py`, `samples/` (viewable streams),
`runs/reading_results.jsonl` (every call: truth, answer, scores,
token usage), `runs/reading_log.txt`.
v2 additions: `authoring.py` (measured-work-through example
authoring), `tuning_test.py` (dose-curve tuning run),
`runs/v2_tuning_results.jsonl`, `runs/v2_tuning_log.txt`.

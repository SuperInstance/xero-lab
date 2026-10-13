# Wave v3 — who measures? Decision brief (prepared 2026-10-13, ~09:55 AKDT)

Question left open by the Xero lane (2026-10-13 17:07 UTC): in wave v3, who
measures direction / period / trend — (A) a deterministic pre-reader that
computes them exactly and leaves the model to judge and speak, or (B) a
genuinely trained small reader raised on the generator's labeled seas?

## What v2 actually established

- Period was genuinely learned from worked examples: 0.00 zero-shot → 0.61,
  mean error 4.2 s → 1.2 s. Reason: counting crest peaks at the centre cell
  is a procedure a text reader can execute on a letter grid.
- Direction and trend were theatre: direction got *worse* with teaching
  (36/36 "southeast" at top dose, with fabricated narration); the
  "seas always build" prior did not die under balanced labels, it moved to
  whichever label the examples leaned toward.
- Law drawn by the lane: teaching transfers the script, not the
  measurement. A student can only learn what it can actually do in its
  medium. Tracking a diagonal band across 45 frames is not executable in
  that medium; peak-counting is.
- Method receipts are clean: pacing gate 126/126 MiniMax calls, zero rate
  limits; new generator reproduces all 144 v1 seas bit-for-bit, so v1/v2
  comparison is untainted. Jev repriced the reader claim 0.73 → 0.59.

## Recommendation: A now, B later — sequenced, not either/or

1. **v3 = deterministic pre-reader.** Direction (dominant wave-vector /
   spectral peak), period (zero-crossing / FFT on the centre-cell series —
   cross-check against the peak-counting the model *did* learn), and trend
   (height envelope slope) are all exactly computable from the same fields
   the generator produces. The model's job shrinks to what v2 proved it can
   do: judge and speak seamanship over true numbers. This is the
   gauge-not-agent shape: a calibrated instrument, then a tongue.
2. **Decisive cheap test first:** run the pre-reader over v2's fresh-water
   set. Expect direction/trend at or near ceiling. If it is not, the bug is
   in the estimator/generator match and is found in an afternoon on CPU —
   no GPU, no training run.
3. **B stays alive as v4, gated on hardware anyway.** A trained small
   reader needs the ProArt GPU; the ProArt tunnel was still dark as of
   2026-10-13 15:32 UTC (WSL session closed 2026-10-12 18:07 AKDT) and the
   door-return deploy cron is waiting on it. Choosing B today chooses a
   blocked queue. Choosing A today also produces the exact labeled
   measurements a future trained reader would be distilled from — A is
   B's teacher, so no work is wasted either way.

## What Casey is actually deciding

Only the sequencing: pre-reader first (recommended, unblocked, one
afternoon to a verdict) with the trained reader as its student later —
or hold v3 until the GPU returns and train first. Everything else in the
Xero "Go" thread is closed: grid staircases closed at the corrected 8.6%
of all-big cost, landing page swept and matching the record (b64d067).

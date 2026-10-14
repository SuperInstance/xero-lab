# Verification — Playthrough Tile #2: The Patient Dictation Agent

*2026-10-13 · `segmenter.js` is verified against the Python
prototype (`voice-block/segmenter/segmenter.py`) the same way
Tile #1's engine was: same inputs, recorded outputs, no claim
without a receipt. **Verdict: zero divergences.** The port was not
adjusted after the first full run — every check below passed as
written.*

## Method

Python's PRNG is not JavaScript's, so the two implementations
cannot generate the same fixture streams independently. The
streams were therefore generated **once**, by the real
`fixtures.py` (seeded, deterministic), and exported as data
(`fixtures.json`, via `gen_fixtures.py`) — both sides consume
byte-identical inputs, the arrangement Tile #1 used for its
fixture. `ground_truth.py` then ran the **unmodified Python
prototype** over those streams and recorded everything it did
(`ground-truth.json`): every chunk's trigger, word count, rendered
markdown, `end_pause`, and boundary words, under the default config
and the naive baseline; the size-isolated run; the modes
simulator's own summaries (imported and run unmodified); and
`demo.py`'s stats.

`node verify.js` checks the port in four sections:

## A. The prototype's 16 tests, ported assertion-for-assertion

All 16 tests from `test_segmenter.py` re-expressed in the Node
harness over the same streams — **16/16 pass**. Highlights:

- gap trigger: 11 gap chunks on the 12-burst stream, every
  `end_pause` > 5 s, flush last;
- best break: the planted pause + sentence boundary at word 480
  wins over the size trigger point at 500 — first chunk is
  `size`, 480 words, ends a sentence;
- markup: paragraph break + casing (`"Alpha beta.\n\nGamma
  delta."`), emphasis on the held word only (`*w5*`, not `*w4*`);
- `tick()`: silent at 2.35 s of gap, emits at 5.35 s, never twice;
- invariants: zero word loss in all five fixtures, 500-word cap,
  time ordering.

## B. Chunk-for-chunk equality with the Python prototype

For all 8 exported streams, the JS chunk sequence equals the
Python prototype's recorded output **exactly** — trigger, word
count, boundary words, mid-sentence flag, and the **rendered
markdown text byte-for-byte** (segmenter: 22 + 40 + 11 + 3 + 10 +
12 + 7 + 10 chunks; naive baseline likewise; size-isolated
rapid-fire: 4 chunks). `end_pause` agrees to within 1e-9 (in
practice the same doubles).

## C. The modes simulator, ported — its published numbers reproduce

`modes/simulate.py` ported faithfully (wall-clock tick
interleaving, +0.3 s processing, talked-over rule, the async job
model) and run over the same fixtures: all 9 mode summaries equal
the Python simulator's — the numbers in `modes/RESULTS.md`:

- **walk / patient: 2 chunks, first response 549.0 s, max
  buffered 499 words, talked over 0** — the tile's headline,
  reproduced by the port;
- walk / eager: 45 chunks, talked over 30; monologue / eager:
  talked over 64 of 75; stop-and-think / eager: 4 of 50;
- walk / async: 10 chunks, first response 64.2 s, 9 jobs done
  while talking, 9 nudge points; monologue / async: 84 nudges.

## D. demo.py's stats, recomputed from JS chunks

Segmenter vs naive, per fixture — identical to Python: **0
mid-sentence endings for the segmenter on every fixture**, naive
at 9/11, 11/11, 6/6, 9/9 (the published "0% vs 82–100%").

## Totals

**46 checks, 46 pass, 0 divergences** (`node verify.js`, exit 0).
The live pad in `player.html` runs this same `segmenter.js`, and
its boot check re-runs sections B/C's core comparisons in the
browser before it calls itself live.

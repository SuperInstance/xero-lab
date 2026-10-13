# xero-wave-language — can a model read the sea from letters?

A synthetic, testable proof of concept for Casey's 2026-10-12 seed
(filed in the zero-agent design notes): render waves into **letter
grids at adaptive resolution, pulsed like speech** (sets and lulls),
and the information a helmsman needs — **rhythm, height, throw, swell
direction** — survives in incredibly compact form that a language
model can **read as a first-class language**, with no hand-built
signal processing between the water and the reader.

Everything here is synthetic. No boat, no hardware, no sensors:
a procedural sea whose every parameter is known exactly, so every
reading has an exact right answer.

## The claim under test

1. **Legibility** — an untuned language model (MiniMax-Text-01) can
   read direction / period / trend / set-pattern from letter frames
   at least as well as from the raw numbers the letters replace.
2. **Compactness** — the letter form is drastically smaller than the
   numeric form, small enough that a whole day at sea is a file a
   small computer can hold and learn from.

## Pieces

| file | what it is |
|---|---|
| `sea.py` | Procedural sea generator. Dominant swell train + weaker secondary train + wind chop, modulated by a set/lull envelope and a building/easing/steady trend ramp. Deep-water dispersion (λ ≈ 1.56·T²). Ground truth is exact by construction. |
| `render.py` | The letter renderer. Fixed height scale (±1.8 m) across a whole stream — so a building sea literally brightens; 10-letter ramp ` .: -=+*#%@`. Pulsed stream format: frames grouped under `--- SET ---` / `~~~ LULL ~~~` markers (the lull is the break, as the pause is in speech). Plus delta encoders: naive per-cell, and a **deadband delta** (a cell is re-emitted only after moving ≥2 letter levels — a gate on the log). |
| `reading_test.py` | Paired reading test: the same 36 seas under 4 encodings — `letters20`, `letters12` (coarse), `numeric` (raw control), `summary` (per-frame stats + centre buoy, the instrument control). Four exact-answer questions per sea; real token usage captured per call. |
| `daylog.py` | Prices an 8-hour day at sea under each encoding (bytes). |
| `make_samples.py` | Writes the viewable sample streams in `samples/`. |
| `samples/` | A few streams a human can open and try to read before peeking at the truth printed at the top. |
| `runs/` | Raw results (`reading_results.jsonl`) and logs. |
| `RESULTS.md` | Accuracy by condition, token costs, compactness, failure examples, verdict. |

## Design decisions a reader should know

- **Fixed scale, not per-frame normalization.** Normalizing each
  frame would make every sea look equally bright and erase the trend
  — the encoding would delete one of the four things it is tested on.
- **Structure held constant across encodings.** Frame times and the
  SET/LULL markers are identical in every condition, so the test
  compares *encodings*, not stream formats.
- **The summary control is honest about what instruments know.** A
  buoy + frame statistics carry period, trend and sets, but a single
  point cannot see direction. If letters beat it on direction, the
  grid itself is earning its keep.
- **Zero-shot reader.** The model is untuned — this tests the floor
  of Casey's claim. His stronger form is a reader *tuned* to the
  letter language and then pruned; that training loop is not built
  here (see RESULTS.md open questions).

## Run it

```bash
python3 sea.py                 # generator smoke test
python3 make_samples.py        # sample streams -> samples/
python3 reading_test.py --streams 36   # the reading test (MiniMax)
python3 daylog.py              # 8-hour compactness pricing
```

No GitHub push; built as a seed — labeled, prunable, ready to grow.

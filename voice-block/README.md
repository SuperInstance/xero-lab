# The Voice Block — proof-of-concept seeds

*2026-10-12 · Built from Casey's building-block sketch of the same
day. Status: **SEEDS, not constraints.** Variants in parallel,
everything labeled and prunable. The purpose is learning the shape
of the space — how big the pottery is — not committing to a design.*

## The block

The most basic voice agent: **transcribe English speech to text.**
Just a transcriber, plus two tools and a pulse:

1. **Segmenter** — splits a word-timed transcript stream into
   markdown chunks of at most ~3/4 of a page (~500 words). An
   algorithmic assembler adds light markup the timing signal
   supports (paragraph breaks, sentence casing, emphasis on
   duration-lengthened words) and picks the **best break** —
   scored `min(pause, 3 s) + 2 × sentence-end`, ties to the later
   boundary — instead of cutting wherever the trigger fires.
2. **Cadence (the pulse)** — emit a chunk when ANY fires:
   **≥60 s** elapsed, **≥3/4 page** accumulated, or a **speech gap
   >5 s**. The gaps are the interrupt surface.
3. **Modes** — the same block under different cadence + initiative
   configs. A toggle, not three products:

| Mode | Config | Character |
|---|---|---|
| **Eager** | gap 0.8 s · page 120 wds · clock 15 s | Responds at the first short pause. The chatbot that makes you keep feeding it words. |
| **Patient** | gap ∞ · page 500 wds · clock 20 min | Accumulates while the speaker stops, thinks, looks out the window. The 20-minute walk mode. |
| **Async-parallel** | Casey's spec (gap 5 s · page 500 · clock 60 s) + a work model | The agent *works* on each chunk while the speaker keeps talking; progress surfaces live; the speaker can interrupt or nudge mid-stream. |

## Layout & how to run

```
segmenter/   Python reference implementation (stdlib only)
             segmenter.py    triggers, best-break, markup, tick()
             fixtures.py     seeded synthetic word-timed streams
             test_segmenter.py   16 tests — from segmenter/: python3 -m unittest test_segmenter
             demo.py         segmenter vs naive baseline, measured (run from segmenter/)
modes/       simulate.py     replays fixtures through the 3 configs
             RESULTS.md      the numbers + how the modes feel
worker/      Cloudflare Worker variant (TypeScript) — see worker/README.md
             npm test (from worker/)  → 8 tests; wrangler deploy-ready, NOT deployed
research.md  prior art with sources (endpointing, barge-in, captions,
             dictation, the eager/patient tension in big products)
```

## Status of each variant

| Variant | Label | State |
|---|---|---|
| Python segmenter | seedling | Working; 16/16 tests pass |
| Modes simulator | seedling | Working; results filed in `modes/RESULTS.md` |
| Cloudflare Worker | seedling, deploy-ready | 8/8 tests pass, `tsc` clean, `wrangler deploy --dry-run` bundles (6.04 KiB). **Not deployed** — no account touched. State is an in-memory Map; the Durable Object production path is sketched in `worker/src/session-do.ts` |
| Research | filed | MiniMax synthesis used as a checklist only — its numbers were partly invented (documented in §D); every load-bearing figure is independently sourced |

## What the seeds taught us

- **Best-break is nearly free and worth a lot:** 0% of chunks end
  mid-sentence across all fixtures, vs 82–100% for a naive
  fixed-window cutter. Mean pause at the chosen break: 0.87 s vs
  0.21 s (monologue).
- **At real speech rates, the clock beats the page.** 500 words
  takes ~2.5 min to say, so the 60 s TIME trigger fires at ~180
  words (≈1/4 page). The 3/4-page SIZE rule only binds when word
  events arrive faster than real time — batch/file transcription.
  Which one *should* bind live is an open question below.
- **Gaps are only visible late unless you have a clock.** A purely
  stream-driven segmenter learns about a silence when speech
  resumes; adding a wall-clock `tick()` cut async's first response
  on the sparse walk from 169 s → 64 s and moved its work *into*
  the silences.
- **Eagerness is about where the pauses are.** Eager mode talked
  over resumed speech 64/75 times inside flowing monologue but
  only 4/50 times between thoughts. Same threshold.
- **Prior art (research.md §B):** Deepgram Flux already runs the
  async pattern — a low *eager* threshold starts speculative work,
  a higher one commits, resume discards it — with a 5,000 ms
  silence backstop. LiveKit's eot-bench: learned turn detection
  answers in 543 ms at 5% false-cutoffs; VAD-only at a 300 ms
  budget false-cuts 55.6%. Dictation tools (Wispr, Superwhisper)
  are push-to-talk **batch** — patience there is an explicit end
  signal, not inference. Nothing published addresses chunking at
  this block's scale (500 wds / 60 s), and no big product ships a
  user-facing eager/patient dial — the toggle is this block's own
  contribution.

## Deliberately not built (pruned at seed stage)

- **No audio/STT front end.** The block consumes word-timed
  streams; a microphone/Web Speech/Whisper feeder is a separate
  block that plugs into the same stream shape.
- **No live Cloudflare deploy** (per instructions) and no Durable
  Object binding — sketch only.
- **No amplitude/prosody emphasis.** Markup uses word *duration*
  only, the one stress cue a word-timed stream carries.
- **Patient mode conflates two things** the research says to
  separate: *turn patience* (when to respond) vs *chunk cadence*
  (when to surface text — captioning argues text should arrive at a
  readable cadence regardless). Refinement noted, not yet built.

## Open questions for Casey

1. Live speech makes TIME the binding trigger (~180 words/chunk).
   Is the 3/4-page rule really a batch-transcription rule, or
   should the live page cap shrink to match the clock?
2. Should PATIENT split into patient *responses* over punctual
   *chunks* (research pattern), or is silent accumulation the
   point of the mode?
3. Async nudge semantics: can a nudge **redirect** in-flight work
   on the current chunk (barge-in cancellation), or only append
   instructions after it?
4. Add an explicit end-signal ("I'm done" / key release) as a
   fourth input, stolen from push-to-talk dictation?
5. Production tick rate for the silence watchdog — polls cost
   money on Workers; how fresh does gap detection need to be?

*Nothing here is pushed to GitHub. Parent reviews first.*

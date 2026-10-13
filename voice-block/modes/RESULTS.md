# Modes simulator — results

*2026-10-12 · Seed-stage measurements over synthetic fixtures.
Reproduce: `python3 simulate.py` (fixtures are seeded; numbers are
deterministic).*

**Method.** Each fixture is a word-timed stream from
`../segmenter/fixtures.py`, replayed through the same segmenter with
three configs. Emissions are timed with wall-clock ticks
(`Segmenter.tick`): a silence is noticed `gap_trigger` seconds into
it, as a live system would, not when speech resumes. Responses add a
nominal 0.3 s processing delay; model latency is out of scope. The
async work model: each emitted chunk starts a job lasting
5 s + 0.02 s/word of stream time, with progress ticks at
25/50/75%.

## The 20-minute sparse walk — 886 words over 19 min

| mode    | 1st response | chunks | responses | max buffered | talked over | jobs done* | nudges |
|---------|-------------:|-------:|----------:|-------------:|------------:|-----------:|-------:|
| eager   |          10s |     45 |        45 |       35 wds |          30 |          — |      — |
| patient |         549s |      2 |         2 |      499 wds |           0 |          — |      — |
| async   |          64s |     10 |        10 |      128 wds |           — |        9/9 |      9 |

## Steady monologue — 1,542 words over 12 min

| mode    | 1st response | chunks | responses | max buffered | talked over | jobs done* | nudges |
|---------|-------------:|-------:|----------:|-------------:|------------:|-----------:|-------:|
| eager   |          16s |     75 |        75 |       35 wds |          64 |          — |      — |
| patient |         231s |      5 |         5 |      499 wds |           4 |          — |      — |
| async   |          61s |     22 |        22 |      132 wds |           — |       21/21 |     84 |

## Stop-and-think dictation — 810 words over 12 min

| mode    | 1st response | chunks | responses | max buffered | talked over | jobs done* | nudges |
|---------|-------------:|-------:|----------:|-------------:|------------:|-----------:|-------:|
| eager   |           5s |     50 |        50 |       32 wds |           4 |          — |      — |
| patient |         470s |      2 |         2 |      499 wds |           1 |          — |      — |
| async   |          14s |     40 |        40 |       32 wds |           — |       39/39 |     62 |

\* jobs finished before the speaker finished talking. Nudges =
moments the speaker could interrupt or steer: a mid-stream emission,
a >5 s gap with a job in flight, a progress tick surfacing during
speech. Talked-over = a spoken response that lands after the speaker
has already resumed (async doesn't speak, so n/a).

## How the modes feel, in numbers

**Eager is not rude — it's impatient, and you can measure the
difference.** Between thoughts (stop-and-think), it collides with
resumed speech only 4 times in 50 responses: it answers inside your
pauses, then holds the floor, and the conversation feels snappy.
Inside flowing speech (monologue) it starts talking into your next
sentence 64 of 75 times — every sentence-final breath ≥0.85 s is
treated as a full stop. That is the "I have to keep feeding it
words" feeling, quantified: eagerness is a property of *where the
pauses are*, not just the threshold.

**Patient is total recall and zero companionship.** On the walk,
nothing comes back for 9 minutes (first response at 549 s, 55×
eager's 10 s), exactly 2 responses land in 19 minutes, and up to
499 words sit buffered and unacknowledged. Nothing is lost — every
word is eventually in a chunk — but there is no signal that anyone
is listening. Patient is a recorder with good filing, not a partner.

**Async's personality depends on speech density.** On the sparse
walk, its 9 jobs all finish before the stream ends, mostly *inside
the silences* (see the tick finding below) — it works while you
think. On the dense monologue, 21/21 jobs also finish mid-stream,
but now the work genuinely overlaps your talking, and the steerable
surface explodes: 84 nudge points in 12 minutes, vs 9 on the walk.
Same config — the mode's feel is an interaction between cadence and
the speaker's rhythm.

**The tick finding (design-relevant).** A purely stream-driven
segmenter only learns about a gap when speech resumes; with
stream-only detection, async's first response on the walk was
169 s. Adding a wall-clock tick cut it to 64 s and moved the work
into the silences themselves. Any real deployment of this block
needs the tick (or an equivalent silence watchdog); stream-driven
endpointing systematically answers one thought late.

## Caveats

- Fixtures are synthetic, drawn from a 15-sentence pool with regular
  rhythms; real dictation is burstier and less grammatical.
- The job-duration model (5 s + 0.02 s/word) is a placeholder for
  "an agent doing something with the chunk"; real work varies.
- Talked-over counts responses, not perceived rudeness — a response
  the speaker *wanted* still counts if they resumed first.

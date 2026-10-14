# player.md — the Patient Dictation Agent player: integrator spec

`player.html` renders `playthrough.json` (the bootstrap record) and,
at the record's final step, boots `segmenter.js` into a live
dictation pad. This file is the integrator contract: what the player
expects, how it behaves, and what was verified how.

## Files the player loads (same folder, relative paths)

| File | Role |
|---|---|
| `playthrough.json` | The record. All step/state/chat content renders from it; the player computes no record state. |
| `segmenter.js` | The engine (UMD: `window.VoiceSegmenter` in the browser, `module.exports` under Node). Loaded via `<script src>` before the inline script. |
| `fixtures.json` | The five fixture streams (word events `{word, start, end}`), exported from the Python prototype's `fixtures.py`. Used only by the boot check. |
| `VERIFY.md` | Linked from the footer; not loaded by the player. |

Serving: any static server over the tile folder
(`python3 -m http.server` in the folder is enough). The player
fetches `playthrough.json` and `fixtures.json`; opening via
`file://` will fail the fetches and the player says so.

## The record's shape (what the player consumes)

- Top level: `title`, `gallery`, `promise`, `agent`,
  `config.note`, `honesty` (masthead + footer),
  `finalState.checks` (boot check, below), `steps[]`.
- Step: `id`, `chapter`, `title`, `narration`, `chat[]`,
  `action`, `delta{filesAdded, measurementsAdded, fourth{value,
  label}}`, `state{files, tree[], tests, modes, measurements[]}`.
- Chat turn: `speaker` — exactly `"Casey"`, `"The brief"`, or
  `"The builder"` — `text`, optional `coined[]` (terms first named
  in this turn; highlighted in the text and tagged),
  optional `note` (a sourcing caption under the turn).

## Rendering model

- **Chat is the main stage.** Turns accumulate across steps
  (steps 0..current), grouped under a divider naming the step each
  group caused. Casey = brass right-aligned bubbles; The brief =
  document block with a brass rule; The builder = dashed-green
  monospace receipts. Coined terms are highlighted by splitting
  text nodes (never `innerHTML`), so record text is always inert.
- **The rail is labelled "Effects — what the chat caused"**:
  counts (Files / Tests passing / Modes on the toggle / the step's
  `delta.fourth`), the file tree (`state.tree`, this step's
  additions pulse), a receipts ticker (cumulative
  `delta.measurementsAdded` lines; the current step's are lit),
  and a reading pane (live-mode chunk reader, below).
- Transport: restart / back / play-pause / step / scrubber, plus
  Slow (2.4 s) / Fast (0.6 s) and arrow keys. Same pattern as
  Tile #1 (`../filing-agent/player.html`).

## The boot check (runs on reaching the final step)

Before the pad calls itself live, the player's own code:

1. Runs `segmenter.js` (default config) over all five fixtures and
   compares chunks / words / mid-sentence ends (last chunk
   excluded, the demo's convention) against
   `record.finalState.checks.fixtures`.
2. Re-runs the modes simulator port (in the page) on the walk for
   all three modes and compares chunks, max buffered, first
   response (±1e-6 s), talked-over / jobs / nudges against
   `record.finalState.checks.walkModes`.
3. Prints the verdict into `#boot-status` — on success, the
   patient-on-the-walk headline (2 chunks, 499 words held, first
   response 549 s of stream time); on any mismatch, the actual
   differing values, in red. The pad still runs either way; the
   page never claims a pass it didn't get.

`boot_sim.js` executes this exact code headlessly (it extracts the
functions from `player.html` verbatim) — see VERIFY.md §5.

## The live pad (the end state)

- **What it is:** the verified segmenter on a simulated word-timed
  stream. The visitor's text is scheduled as word events
  (deterministic per-word durations; sentence-final pauses ≈
  0.87 s at the default 150 wpm) and released against a stream
  clock that advances 1:1 with wall time. After every release the
  driver calls `segmenter.tick(streamNow)` — the wall-clock
  watchdog pattern from the build — so gaps are noticed *during*
  the silence, exactly as a live deployment would notice them.
- **Modes** (one block, three configs — switching restarts the
  session): Patient `{500 words, 1200 s, gap never}` (default),
  Eager `{120, 15 s, 0.8 s}`, Async-parallel `{500, 60 s, 5 s}`.
  Async's job/nudge work model is the simulator's layer and is
  labelled as such on the mode note; the pad runs its cadence.
- **Thinking pause** inserts 6 s of stream-time silence:
  remaining scheduled words shift by the silence's actual length;
  the tick keeps running through it, so Eager answers mid-silence,
  Async files at 5 s, Patient does nothing — visibly. "Skip" ends
  the silence early (the shift uses the elapsed part).
- **End session** = `flush()`. In Patient mode this (or a full
  500-word page) is the only way it ever answers — the RESULTS.md
  finding, made touchable.
- **Pace:** 90 / 150 / 240 wpm, applied to the next session's
  schedule. **Pause the stream** freezes the stream clock (and
  therefore the segmenter) — labelled as a simulation convenience.
- **Displays:** stream clock, words spoken, words held now, peak
  held, chunks filed; a live transcript (words land as the
  segmenter hears them; silences are marked); filed-chunk cards
  with trigger badges — click one to read it in the rail's
  reading pane. All visitor text renders via `textContent` only.
- **No persistence:** unlike Tile #1's filing store, the pad is a
  session toy — nothing is stored, and the page says the words
  never leave it.

## Honesty labels on the page

- Footer: the record's `config.note` (modes are configurations,
  not products; the stream is simulated text, not audio) and its
  `honesty` note (chat sourced from the 2026-10-12 design record;
  numbers sliced from the prototype's runs and asserted).
- Live panel: the stream is simulated text with timings, not
  audio; quoted numbers are the Python prototype's measured ones;
  the pad runs the verified port (link to VERIFY.md).

## Verification status (2026-10-13)

- `node --check` clean on `segmenter.js` and on the player's
  extracted inline script.
- `node verify.js`: 46/46 — VERIFY.md.
- `node boot_sim.js`: ALL PASS — the player's own boot code
  reproduces the record (86 fixture chunks + the walk three ways);
  pad sanity on the sample script: Patient files 0 chunks before
  the session-end flush, Eager files 8 gap chunks, words conserved
  in all three modes.
- Static serving: 200s for player.html, playthrough.json,
  segmenter.js, fixtures.json, VERIFY.md from the tile folder.

**Needs a real browser (not verifiable on this VM — no headless
browser/DOM shim):** actual DOM rendering and layout of the chat,
rail, and pad; the turn/pulse animations; live pad interaction
timing (the 50 ms driver against real `performance.now`); chunk
click-to-read; mode/pace toggles in situ. Verified instead by code
path, syntax checks, and the Node simulations above — the same
standing caveat as Tile #1. First real-browser test is the
integrator's (or the user's phone).

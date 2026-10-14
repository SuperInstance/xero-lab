# Player spec — Playthrough Tile #1: The Filing Agent

For the parent agent integrating this tile into the Xero landing
page (Bootcamp Gallery). Everything here is static-page
implementable: two assets, no build step, no server.

## Assets

- `playthrough.json` — the bootstrap record (fetch or inline).
- `cascade.js` — the filing engine. Loads as a classic script
  (`window.FilingCascade`) or a Node/CommonJS module. No
  dependencies. The live tool at the end of the tile runs on this —
  the same engine whose output is verified byte-for-byte against
  the Python prototype (VERIFY.md).

## The record (what the player consumes)

```
record.title / .promise / .agent      header copy
record.config                          gate sizes (replay 1000 B, production 60000 B), topicK
record.honesty                         sourcing note (state data AND chat)
record.steps[]                         10 steps, in order:
  .id, .chapter, .title, .narration    display copy (narration is one line)
  .chat[]                              the conversation that caused the step:
    .speaker                           "Casey" | "The brief" | "The builder"
    .text                              the turn (briefs may be multi-line)
    .coined[]                          vocabulary first named in this turn
                                       (deposit, cascade, gate, refine, ledger)
    .note                              optional sourcing caption
  .action                              none | init | deposits | deposits+cascade | refine | handoff
  .delta.deposits                      deposits ticked in this step
  .delta.filesAdded / .filesRemoved    paths, for tree highlighting
  .delta.ledgerAdded[]                 ledger lines this step appends (verbatim)
  .state.tree[]                        full sorted file list at end of step
  .state.{files, entriesTotal, entriesByChat, archiveFiles, topicViews, commits}
```

## Layout — chat first

The chat is the main stage; the state is its consequence rail. The
conversation that built the agent is what's impressive — the files
are what's happening *because* of the chat.

- **Main stage**: the chat thread. For step `i`, render the turns of
  steps 0..i **cumulatively** (earlier turns stay visible, scrolled
  to the newest; stepping back re-renders the shorter thread). Turn
  kinds: **Casey** — brass, right-aligned bubbles; **The brief** —
  a document-style block; **The builder** — a receipt-style block
  (mono, the ✅/counts). Group turns under a small divider naming
  the step they caused. Where a turn's `coined[]` names a term,
  highlight the term's first occurrence in that turn's text and
  tag the turn "coined here" — the vocabulary visibly develops:
  sketch → named verbs → numbered brief → receipts.
- **Consequence rail** (side on desktop, below on mobile), headed
  as the effects of the chat: the **counts strip**, the **file
  tree**, the **ledger ticker**, and the **reading pane**, rendered
  from the record exactly as below — visually demoted, same data.

During replay the player **renders record state; it never computes
state**. `state` is cumulative and complete at every step, so any
position is directly renderable — that is what makes scrubbing
trivial and honest.

## Tick model

- Position = step index `i` (0–9). Controls: **play/pause**,
  **step back**, **step forward**, **restart**, a **scrubber**
  (range input over steps), and **speed**: at minimum two rates —
  slow ≈ 1 step / 2.4 s, fast ≈ 1 step / 0.6 s (a "quickly or
  slowly" toggle is the requirement; exact values are taste).
- On entering step `i`, render:
  - the **file tree** from `steps[i].state.tree` (nested by `/`;
    files in `delta.filesAdded` get a brief highlight/pulse so the
    eye sees what this step bought);
  - the **counts strip**: files · entries · ledger entries
    (use `state.files`, `state.entriesTotal`, `state.commits`);
  - the **narration** line and the **chapter** label;
  - the **ledger ticker**: append `delta.ledgerAdded` lines to a
    scrolling ledger pane (on scrub/jump, rebuild it as the
    concatenation of `ledgerAdded` over steps 0..i — order is the
    prototype's git-log order).
- Stepping back is pure re-render from the record (state is stored
  per step; nothing to undo).
- Steps with `delta.deposits > 0` may sub-tick the deposit count in
  the counts strip (e.g. count entries up within the step) — pure
  garnish; the step boundary values must be the record's.

## End state — the boot (step 9, `action: "handoff"`)

The replay lands on the working tool. Boot it **with the engine
itself**, not with canned contents:

```js
const store = new FilingCascade.FilingStore({ splitBytes: 1000, topicK: 8 });
store.init();
// replay the fixture (fixture.json — the demo's 35 deposits) so the
// visitor starts from exactly the state the playthrough built:
for (const d of fixture) store.deposit(d.chat, d.text, d.ts, d.source);
store.refine("telegram-main"); store.refine("zero-lab");
// store.snapshot() now equals the record's final state (verified).
```

(Equivalently: boot on first arrival at step 9, or pre-boot hidden
and reveal. Booting takes milliseconds.)

Live interaction, all in-page:

- A textarea: **"Paste your own notes — one thought per line."**
  A *File them* button deposits each non-empty line into a chat
  named `your-notes` (source `"you"`, current timestamps) via
  `store.deposit(...)`, then runs `store.refine("your-notes")`.
  The cascade fires live: paste enough lines and the size gate
  splits their inbox into daily and topic files in front of them.
  (Gate for the live store is the replay gate, 1,000 bytes, so a
  paste visibly cascades; footnote it — production default is
  60,000. Honest label, same as the record's config note.)
- The **tree + counts + ledger** panes switch from record state to
  the live store (`store.snapshot()`, `store.status()`), and keep
  updating per deposit. Ledger continues from 42 — the visitor's
  deposits extend the same ledger the replay built.
- Clicking any file shows its content in a reading pane
  (`store.files.get(path)`). **Render with `textContent` only** —
  visitor text is untrusted input; never inject it as HTML.
- Topic views and `INDEX.md` are just files in the map, so the
  filed views render through the same click-to-read path — no
  special casing.
- Optional persistence: `localStorage` the visitor store's
  `snapshot()` (files + ledger) and offer *Reset to the built
  state*. (Design note leaves persist-vs-reset open; local-first
  leans persist. Flag it, don't hide it.)

## Honesty constraints for the integrator

- The tile may carry the gallery's strongest label — its claim is
  its replay. Suggested tile promise (from the record): *"Watch it
  build; then it's yours."*
- Do not restyle the numbers: counts, ledger lines, and narrations
  come from the record verbatim; the record is sliced from the
  prototype's real run (see record.honesty).
- The replay gate footnote (1,000 B replay vs 60,000 B production)
  must survive integration — it's in `record.config.note`.

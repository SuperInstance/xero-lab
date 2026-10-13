# xero-lab

The lab for **Xero** — the production release line of the zero agent
(release repo: [SuperInstance/xero](https://github.com/SuperInstance/xero);
when it graduates, the shelf is the `si-ready` org).

SuperInstance is the sketchbook. This repo is where Xero's pieces get
built and proven before any of them earn a place in the release.
Everything here is public as it is made — the push history is the
timestamp, and the receipts are in the folders.

## Run something in two minutes

```bash
git clone https://github.com/SuperInstance/xero-lab && cd xero-lab
cd filing-loop && python3 demo.py        # the filing loop, end to end
cd ../voice-block/segmenter && python3 -m unittest test_segmenter   # 16 tests
```

Every folder's README is the authority for its own commands.

## What's here

### `filing-loop/` — chat-to-git filing loop prototype ✅ working

The memory system that sits between the chat interface and the agent:
chat **tosses** utterances in, the loop **refines** them, everything
**checks in** to git — the git log is the ledger.

- Deposit → inbox file; size gate fires → cascade split (daily files,
  then per-topic files inside a huge day); idle refine pass builds
  topic views + an index.
- Verified end-to-end: 35/35 synthetic deposits survive the full
  cascade; refine is idempotent. Receipts in
  [`filing-loop/DEMO-OUTPUT.md`](filing-loop/DEMO-OUTPUT.md).
- Topic assignment is a deterministic keyword heuristic — the marked
  seam where an LLM iteration-box pass slots in.

### `voice-block/` — the voice segmentation block ✅ working

Turns a word-timed speech stream into well-broken markdown chunks:
emit on a 60-second clock, a ~¾-page cap, or a >5 s silence — cutting
at the best break, not the limit. Three modes behind one toggle:
**eager** (answer at the first pause), **patient** (keep listening
through thinking gaps — the walking mode), **async-parallel** (work
on each chunk while the speaker keeps talking).

- Python segmenter (stdlib only, 16/16 tests), a modes simulator
  with measured numbers, and a Cloudflare Worker variant
  (deploy-ready, not deployed). `research.md` is the prior-art
  survey — including where its own sources were wrong.
- Headline finding: live, the clock beats the page — 500 words is
  ~2.5 minutes of speech, so the 60 s trigger fires first, at ~180
  words. The ¾-page rule binds only faster-than-real-time feeds.

### `decision-grid/` — decompose → decide → gate, measured ✅

The spreadsheet pattern, run for real: a big model decomposes work
into small decision cells, small models (or plain algorithms) staff
the cells, and a three-valued gate (negative / zero / positive —
stop / hold / go) judges the seams. Workload: triage of 395
real repositories × 4 decision types = 1,580 cells.

- Staffing the cells by measurement cost **8.6% of an all-big-model
  run** — and the receipts show which tier earned which cell, and
  which two plausible re-designs the data rejected.
- Gates belong on instances, not cell types: a three-valued judge
  accepted 11/11 correct small-model decisions and 0/18 wrong ones.

### `wave-language/` — can a model read the sea in letters? ✅ settled

Wave fields rendered as letter grids (height → character), tested
across three versions: zero-shot reading, worked-example teaching,
then a head-to-head on *who should measure*.

- Letters cost 6.5× fewer tokens than numeric grids, and a day of
  letter-logs is ~1 MB — but the untuned reader is the bottleneck,
  not the rendering.
- v3 settlement: **the instrument measures, the model speaks.**
  Small deterministic estimators score 36/36 on direction and
  period; the big model, given their brief, adds exactly zero
  measurement — and in the instrument's dead zones it guesses
  (9/9 wrong). A trained small reader matches the instrument on
  direction/period once its input makes motion explicit.

### `research/` — the working library

Start at [`research/INDEX.md`](research/INDEX.md) — the address
table. Hardware ladder with the Arduino UNO Q **confirmed** as the
dual-brain target (Linux MPU + real-time MCU), Telegram's bot
constraints from primary sources, the PLATO/TUTOR recovery,
tiered-orchestration economics, and `nuggets.md` — the design
corpus's load-bearing sentences, each with a judgment receipt.

- [`research/superinstance/`](research/superinstance/) — a survey
  of all **5,231 public SuperInstance repos**: the family map, the
  lowest-level (orientation) candidates tested by removal, and the
  greatest hits priced by what they buy and what they spend.

### `notes/` — the design record

- `2026-10-10-z-zero-agentic-terminal.md` — the founding ramble,
  decomposed: ~35 timestamped sections. Folders as places, two logs
  (state + contracts), gates with deadbands, watch-means-note, the
  minimum agent (*a perception check in a loop with an I/O*).
- `NOTES-2026-10-10-zero-uno-q-architecture.md` — the one-page
  synthesis: the redshirt split (cloud builds, metal syncs),
  simulate-then-project, the desert-island learning loop.
- `2026-10-10-xero-production-line.md` — the two-track model
  (Z-zero repos are the lab, Xero is the release) and the si-ready
  decision.
- `2026-10-12-calculator-maker-alarm.md` — calculator maker, not
  calculator; the alarm definition of agency; componentize, don't
  augment (1 big : 20 medium : 100 small); grid, not tape;
  orientation vs alignment; the voice block and wave-language seeds.

### The two pages

- [`landing.html`](landing.html) — what Xero is, as eight working
  situation demos (dictation, the 3 a.m. bilge alarm, the grid,
  the sea, the combadge, filing, the redshirt, the clones). Every
  demo is labeled: **Measured** (numbers from a real run),
  **Real prototype** (working code, shown as a simulation of
  itself), or **Simulation** (a designed behavior, illustrated).
  Download and open in a browser.
- [`deployment.html`](deployment.html) — how a Xero is built in git
  and last-mile-projected onto hardware, with the placement
  negotiation simulated. Download and open in a browser.

## The program in one paragraph

An agent is a set of files; the harness is just the crank that turns
them. You build the product by talking to the agent that will *become*
the product — conversations, linked harnesses, and code all in one git,
so anybody could walk your commands and build it again. Then it
last-mile-projects onto whatever hardware fits the job: an LED and
buttons, an ESP32, a Pi, a Jetson, a pin you click to talk. The human
is the harness today, and what he builds is building him out of a job —
one rung of the memory ladder at a time.

## License

MIT — see [`LICENSE`](LICENSE).

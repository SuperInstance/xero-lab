# xero-lab

The lab for **Xero** — the production release line of the zero agent
(release repo: [SuperInstance/xero](https://github.com/SuperInstance/xero);
when it graduates, the shelf is the `si-ready` org).

SuperInstance is the sketchbook. This repo is where Xero's pieces get
built and proven before any of them earn a place in the release.

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

### `notes/` — the design record (2026-10-10)

- `NOTES-2026-10-10-zero-uno-q-architecture.md` — the one-page
  synthesis: the redshirt split (cloud builds, metal syncs), the
  product inversion (you're talking to the product, mid-assembly),
  simulate-then-project, the desert-island learning loop, and the
  verified Telegram substrate constraints.
- `2026-10-10-z-zero-agentic-terminal.md` — the full ramble,
  decomposed: ~35 timestamped sections (outline, implications, open
  questions). Folders as places, two logs (state + contracts), gates
  with deadbands, watch-means-note, the minimum Turing-machine agent
  (*a perception check in a loop with an I/O*), interface/data/logic,
  pathos/logos/ethos.
- `2026-10-10-xero-production-line.md` — the two-track model (Z-zero
  repos are the lab, Xero is the release) and the si-ready decision.

## The program in one paragraph

An agent is a set of files; the harness is just the crank that turns
them. You build the product by talking to the agent that will *become*
the product — conversations, linked harnesses, and code all in one git,
so anybody could walk your commands and build it again. Then it
last-mile-projects onto whatever hardware fits the job: an LED and
buttons, an ESP32, a Pi, a Jetson, a pin you click to talk. The human
is the harness today, and what he builds is building him out of a job —
one rung of the memory ladder at a time.

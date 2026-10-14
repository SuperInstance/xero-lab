# Verification — cascade.js vs the Python prototype

The tile's right to exist: the in-browser cascade must reproduce the
Python prototype's verified behavior on the same fixture. This file is
the method and the receipts.

## What is compared

- **Fixture** (`fixture.json`): the 35 synthetic deposits from the
  prototype's `demo.py` — same texts, same timestamps, same order,
  exported mechanically from `demo.py`'s own data arrays (no
  transcription).
- **Ground truth** (`ground-truth.json`): produced by `trace.py`,
  which runs the actual `filing_loop.py` against a throwaway git
  store with the demo's gate (`FILING_SPLIT_BYTES=1000`) and dumps
  every file's full content, the git log (commit subjects, in order),
  and per-chat counts — plus a second-refine state for the
  idempotence comparison.
- **The port** (`cascade.js`): run in Node on the same fixture, same
  gate (1,000 bytes), same topic K (8), by `verify.js`. The port's
  "ledger" is the in-memory list of the prototype's commit messages;
  its store is an in-memory file map.

## Commands

```
python3 trace.py ground-truth.json     # Python prototype -> ground truth
node verify.js                         # JS port -> diff against it
```

## Receipts

Ground truth (matches the prototype's published DEMO-OUTPUT.md:
35/35 entries, telegram-main 7 archive files / 8 topic views,
zero-lab 2 archive files / 8 topic views, 42 commits):

```
wrote ground-truth.json: 30 files, 42 ledger entries, idempotent=True
```

Port comparison (`node verify.js`, exit 0):

```
PASS  final file map byte-identical to Python — 30 files
PASS  ledger identical to Python git log — 42 commits
PASS  35/35 entries survive the full cascade — telegram-main 20, zero-lab 15, deposited 35
PASS  status counts match the prototype — {"telegram-main":{"entries":20,"archiveFiles":7,"topicViews":8},"zero-lab":{"entries":15,"archiveFiles":2,"topicViews":8}}, commits 42
PASS  topic assignments identical (telegram-main) — compass, autopilot, seas, deadband, rams, xero, telegram, heavy
PASS  topic assignments identical (zero-lab) — agent, compass, files, heavy, seas, rams, invoice, brandons
PASS  refine idempotent (JS state unchanged by second refine) — ledger still 42 commits
PASS  second-refine state also byte-identical to Python

ALL CHECKS PASSED
```

"Byte-identical" means exactly that: all 30 files' full text —
inbox, daily archive files, the L2 topic files, all 16 topic views
and both indexes — plus the 42 ledger lines, equal to the Python
run's, character for character. Topic assignments are additionally
asserted on their own (check 5) because they are the heuristic's
observable output.

## Divergences found

**None.** The port passed all checks on its first verification run;
no fix to the port was needed, and no claim was softened. The
semantics that had to be carried across carefully, and were:

- **File size is bytes, not characters** (the size gate). The port
  measures UTF-8 byte length (`TextEncoder`), as `os.path.getsize`
  does — entry headers contain an em dash, so this matters.
- **Tie-breaking in topic selection** follows Python's documented
  `Counter.most_common` rule (count desc, then first-encounter
  order), reproduced via insertion-ordered `Map` + stable sort.
- **`primary_topic` is a strict-greater scan** in topic order, with
  `"misc"` as the zero-count fallback — ported as-is.
- **Commit gating**: the prototype commits only when the tree
  changed; the port fingerprints the file map and records a ledger
  line only on change — this is what makes the second refine a
  no-op in both implementations, ledger included.

## Reproduce in this folder

```
python3 trace.py ground-truth.json   # needs ~/workspace/xero-filing-prototype
python3 make_playthrough.py          # rebuilds playthrough.json from the trace
node verify.js                       # the 8 checks above
```

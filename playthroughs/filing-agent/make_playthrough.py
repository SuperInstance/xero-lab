#!/usr/bin/env python3
"""
make_playthrough.py — build playthrough.json from the ground truth.

Titles and narrations are curated here; every number, file list, and
ledger line is sliced mechanically from ground-truth.json (the trace of
the real Python prototype run), so the record cannot drift from the
receipts. Re-run trace.py, then this, to regenerate.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
gt = json.load(open(os.path.join(HERE, "ground-truth.json")))
snaps = gt["snapshots"]
ledger = gt["final"]["ledger"]

# (chapter, title, narration, action, snapshot index, ledger slice)
STEPS = [
    ("0 · The blank page", "The blank page",
     "The zero agent starts as a blank page — no files, no memory, "
     "nothing spent. Everything after this is additions.",
     "none", None, (0, 0)),
    ("1 · A place to stand", "Init — the store appears",
     "The store appears: one README and the first ledger entry. "
     "From here, nothing moves without being written down.",
     "init", 0, (0, 1)),
    ("2 · Talk lands", "Day one — talk lands in the inbox",
     "Ten deposits land — five per chat, one an hour through day one. "
     "Each is its own ledger entry in the real run; the replay ticks "
     "them as a group. Talk becomes files: everything waits in the inbox.",
     "deposits", 1, (1, 11)),
    ("2 · Talk lands", "Day two — the size gate fires",
     "Ten more deposits. Mid-day, each inbox crosses the size gate — "
     "1,000 bytes in this replay, 60,000 (≈20 pages) in production — "
     "and the cascade rolls both days into daily archive files. "
     "The inbox drains; nothing is lost.",
     "deposits+cascade", 2, (11, 23)),
    ("3 · The burst", "Day three — the burst splits by topic",
     "A ten-message burst, all on one day, one chat. The day alone "
     "crosses the gate, so it splits twice: out of the inbox into a "
     "daily file, then by topic into five files. The flat daily file "
     "exists only inside this step — created by the first split, "
     "consumed by the second.",
     "deposits+cascade", 3, (23, 35)),
    ("3 · The burst", "Day three — the quiet channel waits",
     "Five quieter deposits on the other chat. No gate fires; they "
     "wait in the inbox. Filing is patient — the cascade only moves "
     "what crosses a gate.",
     "deposits", 4, (35, 40)),
    ("4 · Idle churn", "Refine — telegram-main gets topic views",
     "Idle churn: refine reads every source entry — inbox plus "
     "archive, never the views — and builds topic views with an "
     "index. Topics here are a word-frequency heuristic: the marked "
     "seam where a smarter pass slots in later.",
     "refine", 5, (40, 41)),
    ("4 · Idle churn", "Refine — zero-lab completes the build",
     "Refine does the same for the second chat. Thirty files, "
     "thirty-five entries, forty-two ledger entries: the build "
     "is complete.",
     "refine", 6, (41, 42)),
    ("5 · Proof", "Refine again — nothing moves",
     "Run refine again and nothing moves — every regenerated view "
     "is byte-identical, so the ledger stays at 42. A filing system "
     "you can re-run without fear.",
     "refine", 7, (42, 42)),
    ("6 · Working state", "Working state — it's yours",
     "This is the working state, not a picture of it. The same "
     "cascade engine that just replayed the build is live below: "
     "paste your own notes and watch them file themselves.",
     "handoff", 7, (42, 42)),
]


def state_of(snap):
    if snap is None:
        return {"files": 0, "tree": [], "entriesTotal": 0,
                "entriesByChat": {"telegram-main": 0, "zero-lab": 0},
                "archiveFiles": 0, "topicViews": 0, "commits": 0}
    return {
        "files": len(snap["files"]),
        "tree": snap["files"],
        "entriesTotal": snap["entries_total"],
        "entriesByChat": snap["entries"],
        "archiveFiles": sum(snap["archive_files"].values()),
        "topicViews": sum(snap["topic_views"].values()),
        "commits": snap["commits"],
    }


steps = []
prev_files = []
for i, (chapter, title, narration, action, snap_i, (a, b)) in enumerate(STEPS):
    snap = snaps[snap_i] if snap_i is not None else None
    state = state_of(snap)
    files_now = state["tree"]
    added = [f for f in files_now if f not in prev_files]
    removed = [f for f in prev_files if f not in files_now]
    step_ledger = ledger[a:b]
    steps.append({
        "id": i,
        "chapter": chapter,
        "title": title,
        "narration": narration,
        "action": action,
        "delta": {
            "deposits": sum(1 for m in step_ledger if m.startswith("deposit:")),
            "filesAdded": added,
            "filesRemoved": removed,
            "ledgerAdded": step_ledger,
        },
        "state": state,
    })
    prev_files = files_now

record = {
    "title": "The Filing Agent",
    "kind": "playthrough",
    "gallery": "Xero Bootcamp Gallery",
    "promise": "Watch it build; then it's yours.",
    "agent": "A filing agent built from the zero agent: chat tosses "
             "utterances in, a gated cascade files them by day and "
             "topic, and an idle refine pass keeps topic views over "
             "everything. The ledger is the memory.",
    "source": {
        "prototype": "SuperInstance/xero-lab — filing-loop/ "
                     "(filing_loop.py, demo.py)",
        "engine": "cascade.js — a faithful port of the prototype, "
                  "verified byte-for-byte on this fixture (VERIFY.md)",
        "recordDerivedFrom": "trace.py — an instrumented run of the "
                             "Python prototype on the demo fixture",
    },
    "config": {
        "splitBytesReplay": 1000,
        "splitBytesProduction": 60000,
        "topicK": 8,
        "note": "The replay tightens the size gate to 1,000 bytes "
                "(the prototype demo's own setting) so the cascade "
                "fires on a 35-deposit fixture; production default "
                "is 60,000 bytes ≈ 20 pages.",
    },
    "fixture": {
        "deposits": 35,
        "chats": ["telegram-main", "zero-lab"],
        "days": ["2026-10-10", "2026-10-11", "2026-10-12"],
        "note": "The prototype demo's synthetic deposits, replayed "
                "in their original order with their original "
                "timestamps.",
    },
    "honesty": "Steps compress groups of deposits into single ticks; "
               "the narration says so where it happens. Every count, "
               "file list, and ledger line in this record is sliced "
               "from the trace of the real run — none is invented. "
               "The end state is the working cascade.",
    "finalState": steps[-1]["state"],
    "steps": steps,
}

out = os.path.join(HERE, "playthrough.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(record, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"wrote {out}: {len(steps)} steps, "
      f"{sum(s['delta']['deposits'] for s in steps)} deposits, "
      f"{sum(len(s['delta']['ledgerAdded']) for s in steps)} ledger lines")

#!/usr/bin/env python3
"""
trace.py — ground-truth harness for the Filing Agent playthrough tile.

Runs the Python prototype (filing_loop.py) on the demo's exact committed
fixture (the deposit plan built from demo.py's own data arrays) against a
throwaway store, and dumps:
  - the final store state: every file (relpath -> content), the git ledger
    (commit subjects, oldest -> newest), per-chat counts;
  - snapshots at curated beats (init / each deposit day / each refine /
    a second refine) for curating playthrough.json;
  - an idempotence check: file map + ledger after refine #2 vs refine #1.

Output: JSON on stdout (or to the path in argv[1]).
Usage: python3 trace.py [out.json]
"""
import json
import os
import subprocess
import sys
import tempfile

os.environ["FILING_SPLIT_BYTES"] = "1000"  # same gate as demo.py
PROTO = os.path.expanduser("~/workspace/xero-filing-prototype")
sys.path.insert(0, PROTO)
import filing_loop as fl  # noqa: E402
import demo as demo_mod  # noqa: E402  (data arrays only; run() is not called)

CHATS = ("telegram-main", "zero-lab")


def build_plan():
    """Rebuild demo.py's deposit plan verbatim (same order, same stamps)."""
    plan = []
    for i in range(5):
        plan.append(("telegram-main", demo_mod.ts(10, i),
                     demo_mod.AUTOPILOT[i], "telegram"))
        plan.append(("zero-lab", demo_mod.ts(10, i),
                     demo_mod.XERO[i], "telegram"))
    for i in range(5):
        plan.append(("telegram-main", demo_mod.ts(11, i),
                     demo_mod.BOAT[i], "telegram"))
        plan.append(("zero-lab", demo_mod.ts(11, i),
                     demo_mod.AUTOPILOT[i], "telegram"))
    for i, text in enumerate(demo_mod.BURST):
        plan.append(("telegram-main", demo_mod.ts(12, i), text, "telegram"))
    for i in range(5):
        plan.append(("zero-lab", demo_mod.ts(12, i),
                     demo_mod.BOAT[i], "telegram"))
    return plan


def file_map(store):
    out = {}
    for root, dirs, files in os.walk(store):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            p = os.path.join(root, name)
            with open(p, encoding="utf-8") as f:
                out[os.path.relpath(p, store)] = f.read()
    return dict(sorted(out.items()))


def ledger(store):
    r = subprocess.run(["git", "-C", store, "log", "--reverse",
                        "--format=%s"], capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def snapshot(store, label):
    fm = file_map(store)
    led = ledger(store)
    counts = {c: len(fl.all_source_entries(store, c)) for c in CHATS}
    arch = {}
    for c in CHATS:
        d = os.path.join(store, "archive", c)
        arch[c] = sum(1 for root, _, fs in os.walk(d)
                      for f in fs if f.endswith(".md")) if os.path.isdir(d) else 0
    topics = {}
    for c in CHATS:
        d = os.path.join(store, "topics", c)
        topics[c] = sum(1 for f in os.listdir(d)
                        if f.endswith(".md") and f != "INDEX.md") \
            if os.path.isdir(d) else 0
    return {
        "label": label,
        "files": sorted(fm.keys()),
        "entries": counts,
        "entries_total": sum(counts.values()),
        "archive_files": arch,
        "topic_views": topics,
        "commits": len(led),
        "last_commit": led[-1] if led else None,
    }


def main():
    store = tempfile.mkdtemp(prefix="filing-gt-")
    plan = build_plan()
    assert len(plan) == 35, len(plan)
    beats = []

    fl.init_store(store)
    beats.append(snapshot(store, "init"))

    # deposit in the demo's order; snapshot at each day boundary
    cuts = [(10, "day 1 deposits (2026-10-10)"),
            (20, "day 2 deposits (2026-10-11)"),
            (30, "day 3 burst (2026-10-12, telegram-main)"),
            (35, "day 3 deposits (2026-10-12, zero-lab)")]
    done = 0
    for n, label in cuts:
        for chat, when, text, source in plan[done:n]:
            fl.deposit(store, chat, text, ts=when, source=source)
        done = n
        beats.append(snapshot(store, label))

    fl.refine(store, "telegram-main")
    beats.append(snapshot(store, "refine telegram-main"))
    fl.refine(store, "zero-lab")
    beats.append(snapshot(store, "refine zero-lab"))

    state_after_refine = {"files": file_map(store), "ledger": ledger(store)}

    # idempotence: refine both again — nothing may change
    fl.refine(store, "telegram-main")
    fl.refine(store, "zero-lab")
    state_after_refine2 = {"files": file_map(store), "ledger": ledger(store)}
    beats.append(snapshot(store, "refine again (idempotence check)"))

    out = {
        "fixture_deposits": len(plan),
        "final": state_after_refine,
        "after_second_refine": state_after_refine2,
        "idempotent": state_after_refine == state_after_refine2,
        "snapshots": beats,
    }
    text = json.dumps(out, indent=1, ensure_ascii=False)
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {sys.argv[1]}: {len(state_after_refine['files'])} files, "
              f"{len(state_after_refine['ledger'])} ledger entries, "
              f"idempotent={out['idempotent']}")
    else:
        print(text)


if __name__ == "__main__":
    main()

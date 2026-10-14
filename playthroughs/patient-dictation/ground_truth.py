#!/usr/bin/env python3
"""ground_truth.py — run the Python prototype over the exported
streams and record exactly what it does, as ground truth for the
JavaScript port.

    python3 ground_truth.py        # writes ground-truth.json

Records, per stream: the full chunk sequence under the default
config (trigger, word count, rendered markdown text, end_pause,
mid-sentence flag, boundary words), the naive baseline's chunks,
and — for rapid_fire — the size-isolated run the SIZE test uses.
Also records the modes simulator's own summaries (modes/simulate.py
imported and run unmodified) for the three fixtures it reports on,
and demo.py's stats for its four fixtures.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VB = os.path.expanduser("~/workspace/xero-voiceblock")
sys.path.insert(0, os.path.join(VB, "segmenter"))
sys.path.insert(0, os.path.join(VB, "modes"))

import fixtures as py_fixtures  # noqa: E402
from segmenter import Segmenter, SegmenterConfig, WordEvent, naive_fixed_window  # noqa: E402
import simulate as modes_sim  # noqa: E402

streams = json.load(open(os.path.join(HERE, "fixtures.json")))


def evs(name):
    return [WordEvent(e["word"], e["start"], e["end"]) for e in streams[name]]


def run_stream(events, config=None):
    seg = Segmenter(config)
    chunks = []
    for ev in events:
        chunks.extend(seg.feed(ev))
    tail = seg.flush()
    if tail is not None:
        chunks.append(tail)
    return chunks


def chunk_rec(c):
    return {
        "trigger": c.trigger,
        "wordCount": c.word_count,
        "text": c.text,
        "endPause": c.end_pause,
        "endsMidSentence": c.ends_mid_sentence,
        "firstWord": c.words[0].word,
        "lastWord": c.words[-1].word,
    }


gt = {"streams": {}, "modes": {}, "demo": {}}

for name in streams:
    events = evs(name)
    gt["streams"][name] = {
        "words": len(events),
        "default": [chunk_rec(c) for c in run_stream(events)],
        "naive": [chunk_rec(c) for c in naive_fixed_window(events)],
    }

# The SIZE test isolates the size trigger by disabling TIME.
gt["streams"]["rapid_fire"]["sizeIsolated"] = [
    chunk_rec(c) for c in run_stream(evs("rapid_fire"),
                                     SegmenterConfig(max_seconds=10**9))
]

# Modes simulator — the module itself, unmodified, on its fixtures.
for name in ("walk", "monologue", "stop_and_think"):
    events = py_fixtures.ALL_FIXTURES[name]()
    gt["modes"][name] = {mode.name: modes_sim.simulate(mode, events)
                         for mode in modes_sim.MODES}

# demo.py's stats, its own logic, for its four fixtures.
def demo_stats(chunks, events):
    mid = sum(c.ends_mid_sentence for c in chunks[:-1])
    pauses, n = [], 0
    for c in chunks:
        n += c.word_count
        if n < len(events):
            pauses.append(events[n].start - events[n - 1].end)
    return {
        "chunks": len(chunks),
        "midSentenceEnds": mid,
        "midSentenceOf": len(chunks) - 1,
        "meanBreakPause": (sum(pauses) / len(pauses)) if pauses else 0.0,
    }


for name in ("monologue", "stop_and_think", "rapid_fire", "walk"):
    events = py_fixtures.ALL_FIXTURES[name]()
    gt["demo"][name] = {
        "words": len(events),
        "segmenter": demo_stats(run_stream(events), events),
        "naive": demo_stats(naive_fixed_window(events), events),
    }

path = os.path.join(HERE, "ground-truth.json")
with open(path, "w") as f:
    json.dump(gt, f)
print(f"wrote {path}")
for name, rec in gt["streams"].items():
    print(f"  {name}: {rec['words']} words -> "
          f"{len(rec['default'])} chunks (default), "
          f"{len(rec['naive'])} (naive)")
for name, modes in gt["modes"].items():
    print(f"  modes/{name}: " + ", ".join(
        f"{m}={r['chunks']} chunks/maxbuf {r['max_buffered_words']}"
        for m, r in modes.items()))

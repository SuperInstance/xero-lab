#!/usr/bin/env python3
"""gen_fixtures.py — export the Python fixtures as JSON event streams.

Python's PRNG is not JavaScript's, so the two implementations cannot
generate the same streams independently. Instead the streams are
generated ONCE, here, by the real fixtures.py (seeded, deterministic)
and shipped as data: the Python ground-truth run and the Node verify
harness then consume byte-identical inputs — the same arrangement as
Tile #1 (fixture.json sliced from the prototype).

    python3 gen_fixtures.py        # writes fixtures.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = os.path.expanduser("~/workspace/xero-voiceblock/segmenter")
sys.path.insert(0, SEG)

import fixtures  # noqa: E402

STREAMS = {
    # default-argument streams (the invariant tests use these)
    "monologue": fixtures.monologue(),
    "stop_and_think": fixtures.stop_and_think(),
    "rapid_fire": fixtures.rapid_fire(),
    "metronome": fixtures.metronome(),
    "walk": fixtures.walk(),
    # the argument variants individual tests use
    "stop_and_think_12": fixtures.stop_and_think(n_bursts=12),
    "monologue_60": fixtures.monologue(n_sentences=60),
    "monologue_80": fixtures.monologue(n_sentences=80),
}

out = {
    name: [{"word": e.word, "start": e.start, "end": e.end} for e in events]
    for name, events in STREAMS.items()
}
path = os.path.join(HERE, "fixtures.json")
with open(path, "w") as f:
    json.dump(out, f)
print(f"wrote {path}: " +
      ", ".join(f"{k}={len(v)} words" for k, v in out.items()))

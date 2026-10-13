#!/usr/bin/env python3
"""Day-log compactness — what does a day at sea cost to write down?

Simulates an 8-hour day (one fixed sea character, T=8s, sets of 5,
slowly building) and prices the log under several encodings:
  raw numeric text   : full 20x20 grids, 1-decimal metres, 1.25s cadence
  letters (stream)   : full 20x20 letter frames, 1.25s cadence
  letters (logbook)  : 12x12 letters at a 5s pulse — the logbook gist
  naive delta        : keyframe + per-cell change tokens (20x20 letters)
  deadband delta     : same, but a cell is re-emitted only after moving
                       >=2 letter levels (gates on the log)
  letters + gzip     : the stream letters through a plain compressor
Tokens are estimated at the rates MEASURED in the reading test
(prompt_tokens / prompt_chars per encoding); bytes are exact.
"""
import zlib
import numpy as np
from sea import Sea, sample_stream
from render import (assemble_stream, to_letters, delta_encode,
                    deadband_delta_encode)

HOURS = 8
rng = np.random.default_rng(99)
sea = Sea(rng, direction="SW", period_s=8.0, trend="building", sets=5)

rows = []
for label, n, dt in (("stream cadence 1.25s, 20x20", 20, 1.25),
                     ("logbook pulse 5s, 12x12", 12, 5.0)):
    duration = HOURS * 3600
    times, frames = sample_stream(sea, duration=duration, dt=dt, n=n)
    letters_txt = assemble_stream(times, frames, sea.period_s, sea.sets, "letters")
    numeric_txt = assemble_stream(times, frames, sea.period_s, sea.sets, "numeric")
    lf = [to_letters(f) for f in frames]
    naive = delta_encode(lf)
    dd, dd_stats = deadband_delta_encode(frames, deadband=2)
    gz = zlib.compress(letters_txt.encode(), 9)
    rows.append((label, len(frames), {
        "raw numeric text": len(numeric_txt),
        "letters full frames": len(letters_txt),
        "naive delta": len(naive),
        "deadband delta (db=2)": len(dd),
        "letters + gzip": len(gz),
    }))
    print(f"[{label}] frames={len(frames)} deadband changed/frame="
          f"{dd_stats['mean_changed_cells_per_frame']:.0f}/{dd_stats['cells_per_frame']}")

print(f"\n=== 8-HOUR DAY AT SEA — bytes on the page ===")
hdr = f"{'encoding':26s}" + "".join(f"{r[0][:22]:>24s}" for r in rows)
print(hdr)
keys = list(rows[0][2].keys())
for k in keys:
    print(f"{k:26s}" + "".join(f"{r[2][k]:>24,d}" for r in rows))
base = rows[0][2]["raw numeric text"]
for k in keys:
    print(f"  ratio vs raw numeric (stream): {k:24s} {rows[0][2][k]/base:6.2f}x   "
          f"(logbook: {rows[1][2][k]/base:6.3f}x)")
# per-hour at stream cadence
print(f"\nstream-cadence letters: {rows[0][2]['letters full frames']//HOURS:,} bytes/hour; "
      f"logbook letters: {rows[1][2]['letters full frames']//HOURS:,} bytes/hour")

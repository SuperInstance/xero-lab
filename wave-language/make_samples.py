#!/usr/bin/env python3
"""Generate a few viewable sample streams into samples/."""
import numpy as np
from sea import Sea, sample_stream
from render import assemble_stream, summary_stream, to_letters, delta_encode

OUT = "samples"

# Sample 1: a clean, readable sea — sets of 4, NE swell, 8s, building
rng = np.random.default_rng(101)
sea = Sea(rng, direction="NE", period_s=8.0, trend="building", sets=4)
times, frames = sample_stream(sea)
with open(f"{OUT}/sample1-letters-20x20.txt", "w") as f:
    f.write(f"# Sample sea 1 — letter stream, 20x20 grid, north up\n"
            f"# truth (do not peek before reading!): {sea.truth()}\n\n")
    f.write(assemble_stream(times, frames, sea.period_s, sea.sets, "letters"))
with open(f"{OUT}/sample1-numeric-excerpt.txt", "w") as f:
    f.write("# Same sea, numeric encoding — first 6 frames only (it is long)\n\n")
    f.write(assemble_stream(times[:6], frames[:6], sea.period_s, sea.sets, "numeric"))
with open(f"{OUT}/sample1-summary.txt", "w") as f:
    f.write("# Same sea, summary control: per-frame stats + centre buoy\n\n")
    f.write(summary_stream(times, frames, sea.period_s, sea.sets))
lf = [to_letters(fr) for fr in frames]
with open(f"{OUT}/sample1-delta.txt", "w") as f:
    f.write("# Same sea, delta-encoded letters (keyframe + changed cells)\n\n")
    f.write(delta_encode(lf))

# Sample 2: same sea at coarse resolution — adaptive resolution demo
times12, frames12 = sample_stream(sea, n=12)
with open(f"{OUT}/sample2-letters-12x12.txt", "w") as f:
    f.write("# Sample sea 1 again at 12x12 (coarse) — same truth\n\n")
    f.write(assemble_stream(times12, frames12, sea.period_s, sea.sets, "letters"))

# Sample 3: a harder sea — S swell, 6s, easing, continuous (no sets)
rng = np.random.default_rng(202)
sea3 = Sea(rng, direction="S", period_s=6.0, trend="easing", sets=None)
times3, frames3 = sample_stream(sea3)
with open(f"{OUT}/sample3-letters-20x20.txt", "w") as f:
    f.write(f"# Sample sea 3 — letter stream\n# truth: {sea3.truth()}\n\n")
    f.write(assemble_stream(times3, frames3, sea3.period_s, sea3.sets, "letters"))

print("samples written")
for name, s, fr in [("sample1", sea, frames), ("sample3", sea3, frames3)]:
    full = assemble_stream(times if name == "sample1" else times3, fr,
                           s.period_s, s.sets, "letters")
    num = assemble_stream(times if name == "sample1" else times3, fr,
                          s.period_s, s.sets, "numeric")
    d = delta_encode([to_letters(x) for x in fr])
    print(f"{name}: letters={len(full)} chars, numeric={len(num)} chars, delta={len(d)} chars")

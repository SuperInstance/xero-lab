"""Demo / measurement: segmenter vs naive fixed-window baseline.

    python3 demo.py

For each fixture: chunk count, % of chunks ending mid-sentence,
mean pause at the chosen break point, and the trigger histogram.
The naive baseline cuts at exactly 500 words / 60 s wherever the
stream happens to be — no gap trigger, no break search.
"""

from __future__ import annotations

import fixtures
from segmenter import Chunk, Segmenter, SegmenterConfig, WordEvent, \
    naive_fixed_window


def run(events: list[WordEvent],
        cfg: SegmenterConfig | None = None) -> list[Chunk]:
    seg = Segmenter(cfg)
    out: list[Chunk] = []
    for ev in events:
        out.extend(seg.feed(ev))
    tail = seg.flush()
    if tail:
        out.append(tail)
    return out


def stats(chunks: list[Chunk], events: list[WordEvent]) -> dict:
    ends = {i: ev for i, ev in enumerate(events)}
    mid = sum(c.ends_mid_sentence for c in chunks[:-1])  # last is flush
    pauses = []
    n = 0
    for c in chunks:
        n += c.word_count
        # Pause that follows this chunk in the original stream.
        if n < len(events):
            pauses.append(events[n].start - events[n - 1].end)
    return {
        "chunks": len(chunks),
        "mid_sentence_endings": f"{mid}/{len(chunks) - 1}",
        "mid_pct": (100.0 * mid / max(1, len(chunks) - 1)),
        "mean_break_pause": (sum(pauses) / len(pauses)) if pauses else 0.0,
    }


def main() -> None:
    for name in ("monologue", "stop_and_think", "rapid_fire", "walk"):
        events = fixtures.ALL_FIXTURES[name]()
        smart = run(events)
        naive = naive_fixed_window(events)
        ss, ns = stats(smart, events), stats(naive, events)
        trig: dict[str, int] = {}
        for c in smart:
            trig[c.trigger] = trig.get(c.trigger, 0) + 1
        span = events[-1].end
        print(f"\n== {name}: {len(events)} words over {span:,.0f}s ==")
        print(f"  {'':10s} {'chunks':>6s} {'mid-sentence ends':>18s} "
              f"{'mean break pause':>17s}")
        print(f"  {'segmenter':10s} {ss['chunks']:>6d} "
              f"{ss['mid_sentence_endings']:>18s} "
              f"{ss['mean_break_pause']:>16.2f}s")
        print(f"  {'naive':10s} {ns['chunks']:>6d} "
              f"{ns['mid_sentence_endings']:>18s} "
              f"{ns['mean_break_pause']:>16.2f}s")
        print(f"  triggers: {trig}")


if __name__ == "__main__":
    main()

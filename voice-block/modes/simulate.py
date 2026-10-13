"""Modes simulator: the same voice block, three cadence+initiative
configs, replayed over the same word-timed streams.

    python3 simulate.py

Modes
-----
EAGER    gap 0.8 s, page 120 words, clock 15 s — responds at the
         first short pause. The chatbot that makes you keep feeding
         it words.
PATIENT  gap effectively never, page 500, clock 20 min — accumulates
         while the speaker stops, thinks, looks out the window.
         Responds when a page fills or the session ends.
ASYNC    Casey's spec cadence (gap 5 s / page 500 / clock 60 s),
         plus a work model: every emitted chunk starts a job
         (duration 5 s + 0.02 s/word of stream time) whose progress
         ticks surface live while the speaker keeps talking. Gaps
         with a job in flight are nudge points — the interrupt
         surface.

All times are stream time (seconds into the recording). A nominal
0.3 s processing delay is added to responses; model latency is out of
scope — this measures the block's cadence behavior, not a model.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "segmenter"))

import fixtures  # noqa: E402
from segmenter import Chunk, Segmenter, SegmenterConfig, WordEvent  # noqa: E402

PROCESSING_S = 0.3
NEVER = 10**9


class Mode:
    def __init__(self, name: str, config: SegmenterConfig, work: bool):
        self.name = name
        self.config = config
        self.work = work  # async-parallel: chunks start jobs


MODES = [
    Mode("eager", SegmenterConfig(max_words=120, max_seconds=15.0,
                                  gap_trigger=0.8), work=False),
    Mode("patient", SegmenterConfig(max_words=500, max_seconds=1200.0,
                                    gap_trigger=NEVER), work=False),
    Mode("async", SegmenterConfig(), work=True),
]


def silences(events: list[WordEvent], min_gap: float = 2.0):
    """Intervals (start, end) of silence longer than min_gap."""
    return [(a.end, b.start) for a, b in zip(events, events[1:])
            if b.start - a.end > min_gap]


def in_silence(t: float, sils) -> bool:
    return any(s <= t <= e for s, e in sils)


def simulate(mode: Mode, events: list[WordEvent]) -> dict:
    seg = Segmenter(mode.config)
    stream_end = events[-1].end
    sils = silences(events)

    emissions: list[tuple[float, Chunk]] = []  # (emit stream-time, chunk)
    max_buffered = 0
    prev_end: float | None = None
    for ev in events:
        # Wall-clock tick: a real deployment notices a long silence
        # while it is happening (Segmenter.tick), not only when the
        # next word arrives. Fire it just past the gap threshold.
        if prev_end is not None and \
                ev.start - prev_end > mode.config.gap_trigger:
            tick_time = prev_end + mode.config.gap_trigger + 0.05
            for chunk in seg.tick(tick_time):
                emissions.append((tick_time, chunk))
        for chunk in seg.feed(ev):
            emissions.append((ev.end, chunk))
        max_buffered = max(max_buffered, seg.buffered_words)
        prev_end = ev.end
    tail = seg.flush()
    if tail is not None:
        emissions.append((stream_end, tail))

    responses = [t + PROCESSING_S for t, _ in emissions]
    # Talked-over (speaking modes only): a response that lands while
    # the speaker has already resumed talking. Async doesn't speak —
    # it works and surfaces progress — so the metric doesn't apply.
    talked_over = None
    if not mode.work:
        talked_over = 0
        word_starts = [e.start for e in events]
        for rt in responses:
            nxt = next((s for s in word_starts if s > rt - PROCESSING_S),
                       None)
            if nxt is not None and nxt < rt:
                talked_over += 1

    result = {
        "mode": mode.name,
        "first_response_s": responses[0] if responses else None,
        "chunks": len(emissions),
        "responses": len(responses),
        "max_buffered_words": max_buffered,
        "talked_over": talked_over,
        "jobs_done_while_talking": None,
        "nudge_points": None,
    }

    if mode.work:
        jobs = [(t, 5.0 + 0.02 * c.word_count)
                for t, c in emissions if t < stream_end]
        done = sum(1 for t, d in jobs if t + d <= stream_end)
        nudges = 0
        # (a) each mid-stream emission is a moment you can react to
        nudges += len(jobs)
        # (b) each >5 s gap with a job in flight is an interrupt surface
        for a, b in zip(events, events[1:]):
            if b.start - a.end > 5.0:
                if any(t <= a.end < t + d for t, d in jobs):
                    nudges += 1
        # (c) progress ticks (25/50/75%) that surface while talking
        for t, d in jobs:
            for frac in (0.25, 0.5, 0.75):
                tick = t + frac * d
                if tick <= stream_end and not in_silence(tick, sils):
                    nudges += 1
        result["jobs_done_while_talking"] = done
        result["nudge_points"] = nudges
    return result


def fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.0f}s"
    return f"{v:,}"


def main() -> None:
    for name in ("walk", "monologue", "stop_and_think"):
        events = fixtures.ALL_FIXTURES[name]()
        span = events[-1].end
        print(f"\n== {name}: {len(events)} words over {span:,.0f}s "
              f"({span / 60:.0f} min) ==")
        print(f"  {'mode':8s} {'1st response':>12s} {'chunks':>6s} "
              f"{'responses':>9s} {'max buffered':>12s} {'talked over':>11s} "
              f"{'jobs done*':>10s} {'nudges':>7s}")
        for mode in MODES:
            r = simulate(mode, events)
            print(f"  {r['mode']:8s} {fmt(r['first_response_s']):>12s} "
                  f"{r['chunks']:>6d} {r['responses']:>9d} "
                  f"{r['max_buffered_words']:>12,d} "
                  f"{fmt(r['talked_over']):>11s} "
                  f"{fmt(r['jobs_done_while_talking']):>10s} "
                  f"{fmt(r['nudge_points']):>7s}")
        print("  * jobs finished before the speaker finished talking "
              "(async only); nudges = moments the speaker could "
              "interrupt or steer (async only). Emissions are timed "
              "with wall-clock ticks: a silence is noticed gap_trigger "
              "seconds into it, not when speech resumes.")


if __name__ == "__main__":
    main()

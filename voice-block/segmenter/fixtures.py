"""Synthetic word-timed transcript fixtures.

Deterministic (seeded) generators of WordEvent streams, each shaped
to exercise different segmenter behavior. Words come from a small
sentence pool so sentence boundaries are real; timings are modeled:

  * spoken word duration ~ U(0.20, 0.42) s
  * intra-sentence pause   ~ U(0.04, 0.16) s
  * sentence-final pause   ~ U(0.35, 0.95) s
"""

from __future__ import annotations

import random

from segmenter import WordEvent

SENTENCES = [
    "the tide was slack when we left the dock",
    "nobody had checked the bilge since tuesday",
    "you could hear the halyards ticking against the mast",
    "the chart said one thing and the sounder said another",
    "we marked the spot where the eddy folds back on itself",
    "a good watch is mostly a matter of noticing early",
    "the engine took two tries and then caught clean",
    "rain came sideways off the point just after dark",
    "keep the red nun to port and the channel opens up",
    "the gillnetter out of pelican was already working the line",
    "every harbor has one boat that never seems to move",
    "the coffee went cold before the fog burned off",
    "check the running lights before you check anything else",
    "the swell had a long period and a short temper",
    "by the time we anchored the bay had gone flat calm",
]


def _sentence_words(rng: random.Random) -> list[str]:
    words = rng.choice(SENTENCES).split()
    words[-1] = words[-1] + rng.choice([".", ".", ".", "!", "?"])
    return words


def _lay_words(rng: random.Random, clock: float, words: list[str],
               sent_pause: float) -> tuple[list[WordEvent], float]:
    """Place words starting at `clock`; returns (events, clock_after)."""
    events: list[WordEvent] = []
    for i, w in enumerate(words):
        dur = rng.uniform(0.20, 0.42)
        events.append(WordEvent(word=w, start=clock, end=clock + dur))
        clock += dur
        if i < len(words) - 1:
            clock += rng.uniform(0.04, 0.16)
    return events, clock + sent_pause


def monologue(seed: int = 7, n_sentences: int = 160) -> list[WordEvent]:
    """Steady dictation: no gaps over ~1.2 s. Exercises TIME/SIZE
    triggers and best-break selection over ~1,400 words / ~9 min."""
    rng = random.Random(seed)
    events: list[WordEvent] = []
    clock = 0.0
    for _ in range(n_sentences):
        evs, clock = _lay_words(rng, clock, _sentence_words(rng),
                                sent_pause=rng.uniform(0.35, 0.95))
        events.extend(evs)
    return events


def stop_and_think(seed: int = 11, n_bursts: int = 40) -> list[WordEvent]:
    """Short bursts separated by 6–12 s of silence. Every burst
    boundary should become a GAP-triggered chunk."""
    rng = random.Random(seed)
    events: list[WordEvent] = []
    clock = 0.0
    for _ in range(n_bursts):
        for _ in range(rng.randint(1, 3)):
            evs, clock = _lay_words(rng, clock, _sentence_words(rng),
                                    sent_pause=rng.uniform(0.35, 0.9))
            events.extend(evs)
        clock += rng.uniform(6.0, 12.0)
    return events


def rapid_fire(seed: int = 13, n_words: int = 1300) -> list[WordEvent]:
    """Dense stream, minimal pauses, sentence ends every ~30 words.
    The SIZE trigger fires with no long pauses to help it — best
    break has to settle for sentence boundaries."""
    rng = random.Random(seed)
    events: list[WordEvent] = []
    clock = 0.0
    pool = " ".join(SENTENCES).replace(".", "").split()
    next_end = rng.randint(24, 38)
    for i in range(n_words):
        w = pool[i % len(pool)]
        if i == next_end:
            w = w + "."
            next_end = i + rng.randint(24, 38)
        dur = rng.uniform(0.16, 0.30)
        events.append(WordEvent(word=w, start=clock, end=clock + dur))
        clock += dur + rng.uniform(0.02, 0.10)
    return events


def metronome(seed: int = 17, n_words: int = 50,
              spacing: float = 3.0) -> list[WordEvent]:
    """One word every `spacing` seconds: pauses (2.7 s) stay UNDER the
    5 s gap trigger while the clock crosses 60 s — pure TIME trigger."""
    rng = random.Random(seed)
    pool = " ".join(SENTENCES).replace(".", "").split()
    events: list[WordEvent] = []
    for i in range(n_words):
        start = i * spacing
        events.append(WordEvent(word=pool[i % len(pool)],
                                start=start, end=start + 0.3))
    return events


def walk(seed: int = 23, total_seconds: float = 1200.0) -> list[WordEvent]:
    """Casey's 20-minute sparse walk: talk 20–60 s, then silence
    30–110 s while he looks out the window. ~800 words total."""
    rng = random.Random(seed)
    events: list[WordEvent] = []
    clock = 0.0
    while clock < total_seconds - 60:
        # Talk burst.
        burst_end = clock + rng.uniform(20, 60)
        while clock < burst_end:
            evs, clock = _lay_words(rng, clock, _sentence_words(rng),
                                    sent_pause=rng.uniform(0.35, 0.95))
            events.extend(evs)
        # Silence.
        clock += rng.uniform(30, 110)
    return events


ALL_FIXTURES = {
    "monologue": monologue,
    "stop_and_think": stop_and_think,
    "rapid_fire": rapid_fire,
    "metronome": metronome,
    "walk": walk,
}

"""Tests for the voice-block segmenter. Stdlib unittest; run with:

    python3 -m unittest test_segmenter -v
"""

from __future__ import annotations

import unittest

import fixtures
from segmenter import (Chunk, Segmenter, SegmenterConfig, WordEvent,
                       ends_sentence, naive_fixed_window)


def run_stream(events: list[WordEvent],
               config: SegmenterConfig | None = None) -> list[Chunk]:
    seg = Segmenter(config)
    chunks: list[Chunk] = []
    for ev in events:
        chunks.extend(seg.feed(ev))
    tail = seg.flush()
    if tail is not None:
        chunks.append(tail)
    return chunks


def stream_words(chunks: list[Chunk]) -> list[str]:
    return [w.word for c in chunks for w in c.words]


class TestTriggers(unittest.TestCase):
    def test_gap_trigger_per_burst(self):
        events = fixtures.stop_and_think(n_bursts=12)
        chunks = run_stream(events)
        gap_chunks = [c for c in chunks if c.trigger == "gap"]
        # 12 bursts -> 11 inter-burst gaps, each ends a chunk.
        self.assertEqual(len(gap_chunks), 11)
        self.assertEqual(chunks[-1].trigger, "flush")
        # And every chunk ends where the silence starts: end_pause > 5.
        for c in gap_chunks:
            self.assertGreater(c.end_pause, 5.0)

    def test_time_trigger_only_metronome(self):
        events = fixtures.metronome(n_words=50, spacing=3.0)
        chunks = run_stream(events)
        triggers = {c.trigger for c in chunks}
        self.assertIn("time", triggers)
        self.assertNotIn("gap", triggers)     # 2.7 s pauses stay under 5 s
        self.assertNotIn("size", triggers)

    def test_size_trigger_rapid_fire(self):
        # Isolate SIZE: with the default 60 s time trigger also live,
        # real-time speech always trips TIME first (500 words takes
        # ~2.5 min to say). SIZE binds when word events arrive faster
        # than real time — batch/file STT catching up. Disable TIME
        # here to test SIZE on its own.
        cfg = SegmenterConfig(max_seconds=10**9)
        events = fixtures.rapid_fire(n_words=1300)
        chunks = run_stream(events, cfg)
        size_chunks = [c for c in chunks if c.trigger == "size"]
        self.assertGreaterEqual(len(size_chunks), 2)
        # Rapid stream has no pause > 5 s, so no gap chunks at all.
        self.assertEqual([c for c in chunks if c.trigger == "gap"], [])

    def test_time_beats_size_at_speech_rate(self):
        # Under the full default cadence, continuous speech trips the
        # 60 s trigger long before 500 words accumulate.
        chunks = run_stream(fixtures.rapid_fire(n_words=1300))
        self.assertTrue(any(c.trigger == "time" for c in chunks))
        self.assertEqual([c for c in chunks if c.trigger == "size"], [])

    def test_monologue_uses_time_and_breaks(self):
        chunks = run_stream(fixtures.monologue(n_sentences=60))
        self.assertTrue(any(c.trigger == "time" for c in chunks))


class TestInvariants(unittest.TestCase):
    def test_no_word_loss_anywhere(self):
        for name, gen in fixtures.ALL_FIXTURES.items():
            events = gen()
            chunks = run_stream(events)
            self.assertEqual(stream_words(chunks),
                             [e.word for e in events],
                             f"word loss in fixture {name}")

    def test_chunk_word_cap(self):
        cfg = SegmenterConfig()
        for name, gen in fixtures.ALL_FIXTURES.items():
            chunks = run_stream(gen(), cfg)
            for c in chunks:
                self.assertLessEqual(c.word_count, cfg.max_words,
                                     f"oversize chunk in {name}")

    def test_chunks_are_time_ordered(self):
        for name, gen in fixtures.ALL_FIXTURES.items():
            chunks = run_stream(gen())
            starts = [c.start for c in chunks]
            self.assertEqual(starts, sorted(starts), name)


class TestBestBreak(unittest.TestCase):
    def test_prefers_pause_plus_sentence_over_trigger_point(self):
        # 500 words: a sentence ends at word 480 followed by a 0.9 s
        # pause; words 481..500 are mid-sentence with tiny pauses.
        # The size trigger fires at word 500; the cut must land at 480.
        events: list[WordEvent] = []
        clock = 0.0
        for i in range(500):
            w = "word"
            if i == 479:
                w = "halt."
            # Fast delivery (batch STT): 500 words inside 60 s, so the
            # SIZE trigger — not TIME — is the one that fires.
            events.append(WordEvent(word=w, start=clock, end=clock + 0.08))
            clock += 0.08 + (0.9 if i == 479 else 0.02)
        chunks = run_stream(events)
        first = chunks[0]
        self.assertEqual(first.trigger, "size")
        self.assertEqual(first.word_count, 480)
        self.assertTrue(ends_sentence(first.words[-1].word))

    def test_break_beats_naive_mid_sentence_rate(self):
        events = fixtures.monologue(n_sentences=80)
        smart = run_stream(events)
        naive = naive_fixed_window(events)
        smart_mid = sum(c.ends_mid_sentence for c in smart) / len(smart)
        naive_mid = sum(c.ends_mid_sentence for c in naive) / len(naive)
        self.assertLess(smart_mid, naive_mid)


class TestMarkup(unittest.TestCase):
    def _one_chunk(self, events: list[WordEvent]) -> Chunk:
        seg = Segmenter()
        for ev in events:
            self.assertEqual(seg.feed(ev), [])
        chunk = seg.flush()
        assert chunk is not None
        return chunk

    def test_paragraph_break_at_long_pause(self):
        events = [WordEvent("alpha", 0.0, 0.3),
                  WordEvent("beta.", 0.35, 0.65),
                  WordEvent("gamma", 3.15, 3.45),   # 2.5 s pause before
                  WordEvent("delta.", 3.5, 3.8)]
        chunk = self._one_chunk(events)
        self.assertIn("\n\n", chunk.text)
        self.assertIn("Gamma", chunk.text)  # casing after sentence end

    def test_emphasis_on_held_word(self):
        events = []
        clock = 0.0
        for i in range(12):
            dur = 1.3 if i == 5 else 0.25
            events.append(WordEvent(word=f"w{i}", start=clock,
                                    end=clock + dur))
            clock += dur + 0.05
        chunk = self._one_chunk(events)
        self.assertIn("*w5*", chunk.text)
        self.assertNotIn("*w4*", chunk.text)

    def test_first_word_capitalized(self):
        chunk = self._one_chunk([WordEvent("hello", 0.0, 0.3),
                                 WordEvent("there.", 0.35, 0.65)])
        self.assertTrue(chunk.text.startswith("Hello"))


class TestTick(unittest.TestCase):
    def test_tick_emits_during_silence(self):
        seg = Segmenter()
        seg.feed(WordEvent("one", 0.0, 0.3))
        seg.feed(WordEvent("two.", 0.35, 0.65))
        self.assertEqual(seg.tick(3.0), [])        # gap so far 2.35 s
        out = seg.tick(6.0)                        # gap 5.35 s > 5 s
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].trigger, "gap")
        self.assertEqual(seg.tick(9.0), [])        # nothing left


class TestEdges(unittest.TestCase):
    def test_flush_empty(self):
        self.assertIsNone(Segmenter().flush())

    def test_single_word(self):
        seg = Segmenter()
        self.assertEqual(seg.feed(WordEvent("solo", 0.0, 0.3)), [])
        chunk = seg.flush()
        assert chunk is not None
        self.assertEqual(chunk.word_count, 1)
        self.assertEqual(chunk.trigger, "flush")


if __name__ == "__main__":
    unittest.main()

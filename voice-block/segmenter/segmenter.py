"""The voice block — segmenter (Python reference implementation).

Takes a word-timed transcript stream (as produced by an STT engine:
each word carries start/end times in seconds) and emits markdown
chunks of at most ~3/4 of a page (~500 words), on a cadence:

  * GAP  — a speech gap longer than `gap_trigger` (default 5 s) ends
           the current chunk. The gap is the natural break, and the
           interrupt surface in the modes built on top of this block.
  * SIZE — `max_words` (default 500) accumulated.
  * TIME — `max_seconds` (default 60 s) elapsed in the current chunk.

SIZE/TIME do not cut blindly at the trigger point: they pick the BEST
BREAK inside the buffer, scored as

    score(boundary after word i) = min(pause_after_i, 3.0)
                                   + 2.0 if word i ends a sentence

with ties going to the LATER boundary (more content per chunk). The
remainder after the break stays buffered and starts the next chunk.

The assembler adds light markup ("codings") that the timing signal
actually supports:

  * paragraph breaks at chunk starts and at internal pauses
    >= `para_pause` (default 2 s);
  * sentence casing (capitalize after sentence-final punctuation);
  * *emphasis* on words held notably long — duration >=
    `emphasis_ratio` x the chunk's median word duration and >=
    `emphasis_min_dur` seconds. Duration lengthening is the one
    prosodic stress cue a word-timed stream carries; it is a
    heuristic and is labeled as one.

Stdlib only. The TypeScript port in ../worker/src/segmenter.ts
implements the same trigger/scoring rules (minus emphasis/paragraph
markup, which the worker leaves to the renderer) so the two can be
cross-checked.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

SENTENCE_ENDERS = (".", "!", "?")


def ends_sentence(word: str) -> bool:
    w = word.rstrip().rstrip("\"'”’)]").rstrip()
    return w.endswith(SENTENCE_ENDERS)


def pause_after(words: list["WordEvent"], i: int) -> float:
    """Pause following words[i] within the buffer; 0.0 for the last word."""
    if i >= len(words) - 1:
        return 0.0
    return max(0.0, words[i + 1].start - words[i].end)


@dataclass
class WordEvent:
    word: str
    start: float  # seconds
    end: float    # seconds

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class SegmenterConfig:
    max_words: int = 500        # ~3/4 page
    max_seconds: float = 60.0   # cadence: time trigger
    gap_trigger: float = 5.0    # cadence: speech gap that emits
    para_pause: float = 2.0     # internal pause that becomes a paragraph break
    emphasis_ratio: float = 1.8
    emphasis_min_dur: float = 0.40


@dataclass
class Chunk:
    words: list[WordEvent]
    trigger: str                # 'gap' | 'size' | 'time' | 'flush'
    text: str = ""              # rendered markdown
    end_pause: float | None = None  # pause that followed this chunk, if known

    @property
    def start(self) -> float:
        return self.words[0].start

    @property
    def end(self) -> float:
        return self.words[-1].end

    @property
    def word_count(self) -> int:
        return len(self.words)

    @property
    def ends_mid_sentence(self) -> bool:
        return not ends_sentence(self.words[-1].word)


class Segmenter:
    def __init__(self, config: SegmenterConfig | None = None):
        self.config = config or SegmenterConfig()
        self._buf: list[WordEvent] = []

    # -- public API -----------------------------------------------------

    def feed(self, ev: WordEvent) -> list[Chunk]:
        """Feed one word event; returns any chunks it causes to emit."""
        emitted: list[Chunk] = []
        cfg = self.config

        # GAP trigger: the pause *before* this word ends the old chunk.
        if self._buf:
            gap = ev.start - self._buf[-1].end
            if gap > cfg.gap_trigger:
                emitted.append(self._emit(len(self._buf), "gap", end_pause=gap))

        self._buf.append(ev)

        # SIZE / TIME triggers, with best-break selection. Loop: the
        # remainder after a break may still violate a trigger (sparse
        # streams under the time trigger are the usual case).
        while self._buf:
            if len(self._buf) >= cfg.max_words:
                trig = "size"
            elif self._buf[-1].end - self._buf[0].start >= cfg.max_seconds:
                trig = "time"
            else:
                break
            cut = self._best_break()
            emitted.append(self._emit(cut, trig,
                                      end_pause=pause_after(self._buf, cut - 1)))
        return emitted

    def flush(self) -> Chunk | None:
        if not self._buf:
            return None
        return self._emit(len(self._buf), "flush", end_pause=None)

    def tick(self, now: float) -> list[Chunk]:
        """Wall-clock check, for live deployments: if the last word
        ended more than `gap_trigger` seconds ago, the gap has
        happened *now* — emit without waiting for speech to resume
        (which is when pure stream-driven feeding finds out). The
        recorded end_pause is a lower bound on the true gap."""
        if self._buf and now - self._buf[-1].end > self.config.gap_trigger:
            gap = now - self._buf[-1].end
            return [self._emit(len(self._buf), "gap", end_pause=gap)]
        return []

    @property
    def buffered_words(self) -> int:
        return len(self._buf)

    # -- internals ------------------------------------------------------

    def _best_break(self) -> int:
        """Return a cut index: emit buf[:cut], keep buf[cut:].

        Every boundary is a candidate; ties go to the later boundary.
        """
        best_i, best_score = len(self._buf), -1.0
        for i in range(len(self._buf)):
            score = min(pause_after(self._buf, i), 3.0)
            if ends_sentence(self._buf[i].word):
                score += 2.0
            if score >= best_score:  # >= : later boundary wins ties
                best_i, best_score = i + 1, score
        return best_i

    def _emit(self, cut: int, trigger: str, end_pause: float | None) -> Chunk:
        words, self._buf = self._buf[:cut], self._buf[cut:]
        chunk = Chunk(words=words, trigger=trigger, end_pause=end_pause)
        chunk.text = render_markdown(words, self.config)
        return chunk


def render_markdown(words: list[WordEvent], cfg: SegmenterConfig) -> str:
    """Assemble chunk text with the light, signal-supported markup."""
    if not words:
        return ""
    durations = [w.duration for w in words]
    median_dur = statistics.median(durations) if durations else 0.0

    def is_emphatic(w: WordEvent) -> bool:
        return (w.duration >= cfg.emphasis_min_dur
                and median_dur > 0
                and w.duration >= cfg.emphasis_ratio * median_dur)

    out: list[str] = []
    prev: WordEvent | None = None
    for i, w in enumerate(words):
        token = w.word
        # Paragraph break at a long internal pause.
        if prev is not None and (w.start - prev.end) >= cfg.para_pause:
            out.append("\n\n")
        # Sentence casing.
        if (i == 0 or ends_sentence(prev.word if prev else "")) \
                and token[:1].islower():
            token = token[:1].upper() + token[1:]
        if is_emphatic(w):
            token = f"*{token}*"
        out.append(token)
        prev = w
    # Join: words space-separated, paragraph markers already placed.
    text = ""
    for piece in out:
        if piece == "\n\n":
            text += "\n\n"
        elif text == "" or text.endswith("\n\n"):
            text += piece
        else:
            text += " " + piece
    return text


def naive_fixed_window(events: list[WordEvent],
                       config: SegmenterConfig | None = None) -> list[Chunk]:
    """Baseline: cut at exactly max_words or max_seconds, wherever the
    stream happens to be. No gap trigger, no break search, no markup
    beyond plain joining. Exists so demos/tests can price the
    best-break machinery against the dumb version."""
    cfg = config or SegmenterConfig()
    chunks: list[Chunk] = []
    buf: list[WordEvent] = []
    for ev in events:
        buf.append(ev)
        if len(buf) >= cfg.max_words or \
                (buf[-1].end - buf[0].start) >= cfg.max_seconds:
            chunks.append(Chunk(words=list(buf), trigger="naive",
                                text=" ".join(w.word for w in buf),
                                end_pause=None))
            buf = []
    if buf:
        chunks.append(Chunk(words=list(buf), trigger="naive",
                            text=" ".join(w.word for w in buf),
                            end_pause=None))
    return chunks

// segmenter.ts — pure voice-transcript segmenter.
//
// No platform dependencies (no Workers / Node APIs): this module is the
// exact algorithm from the spec and mirrors the Python reference
// implementation being built in parallel. Keep it that way — the worker
// handler (index.ts) and a future Durable Object (session-do.ts) are thin
// shells around SessionSegmenter.

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** One recognized word: text plus start/end times in seconds. */
export interface WordEvent {
  w: string;
  s: number;
  e: number;
}

export type Trigger = "gap" | "size" | "time" | "flush";

/** A finished block of transcript. start/end are first/last word times. */
export interface Chunk {
  text: string;
  wordCount: number;
  start: number;
  end: number;
  trigger: Trigger;
}

// ---------------------------------------------------------------------------
// Tunables (fixed by the spec — do not tweak without changing both impls)
// ---------------------------------------------------------------------------

export const GAP_THRESHOLD_S = 5.0; // silence longer than this splits the buffer
export const MAX_WORDS = 500; // buffer word-count ceiling -> "size" trigger
export const MAX_SPAN_S = 60; // buffer time-span ceiling (s) -> "time" trigger
export const PAUSE_SCORE_CAP_S = 3.0; // pause contribution to break score is capped
export const SENTENCE_BONUS = 2.0; // added when the word before a break ends a sentence
export const PARAGRAPH_PAUSE_S = 2.0; // pause at/above this renders as "\n\n"

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** True when the word's last character is sentence-ending punctuation. */
export function isSentenceEnd(word: string): boolean {
  if (word.length === 0) return false;
  const c = word.charAt(word.length - 1);
  return c === "." || c === "!" || c === "?";
}

/**
 * Render a chunk's words to display text:
 * - words joined with single spaces;
 * - "\n\n" instead of the space before any word whose preceding pause
 *   (this word's start minus the previous word's end) is >= 2.0 s;
 * - the first letter of the chunk, and of any word following a
 *   sentence-ending word, is capitalized when it starts lowercase a-z.
 */
export function renderChunkText(words: WordEvent[]): string {
  let out = "";
  for (let i = 0; i < words.length; i++) {
    let text = words[i].w;
    const capitalize =
      i === 0 || isSentenceEnd(words[i - 1].w);
    if (capitalize && text.length > 0) {
      const first = text.charAt(0);
      if (first >= "a" && first <= "z") {
        text = first.toUpperCase() + text.slice(1);
      }
    }
    if (i === 0) {
      out += text;
    } else {
      const pause = words[i].s - words[i - 1].e;
      out += (pause >= PARAGRAPH_PAUSE_S ? "\n\n" : " ") + text;
    }
  }
  return out;
}

/** Build the Chunk object for a non-empty word list. */
export function makeChunk(words: WordEvent[], trigger: Trigger): Chunk {
  return {
    text: renderChunkText(words),
    wordCount: words.length,
    start: words[0].s,
    end: words[words.length - 1].e,
    trigger,
  };
}

/**
 * Pick the best break boundary in a buffer that hit the size/time ceiling.
 *
 * Every boundary "after word i" (emit words 0..i, keep the rest) is scored:
 *   score = min(pauseAfter_i, 3.0) + (2.0 if word i ends a sentence)
 * where pauseAfter_i = buffer[i+1].s - buffer[i].e, and 0 for the final
 * word. The highest score wins; ties go to the LATER boundary.
 *
 * Returns the index of the last word included in the emitted chunk.
 */
export function bestBreakIndex(buffer: WordEvent[]): number {
  let bestIdx = buffer.length - 1;
  let bestScore = -Infinity;
  for (let i = 0; i < buffer.length; i++) {
    const pauseAfter =
      i + 1 < buffer.length ? buffer[i + 1].s - buffer[i].e : 0;
    let score = Math.min(pauseAfter, PAUSE_SCORE_CAP_S);
    if (isSentenceEnd(buffer[i].w)) score += SENTENCE_BONUS;
    // >= (not >) is what makes ties resolve to the later boundary.
    if (score >= bestScore) {
      bestScore = score;
      bestIdx = i;
    }
  }
  return bestIdx;
}

// ---------------------------------------------------------------------------
// Per-session state machine
// ---------------------------------------------------------------------------

/**
 * Holds one session's buffered words and every chunk emitted so far, and
 * advances the segmentation algorithm one word event at a time.
 */
export class SessionSegmenter {
  buffer: WordEvent[] = [];
  chunks: Chunk[] = [];

  /**
   * Feed one word event. Returns the chunks this event caused to be
   * emitted (usually none, occasionally one), in emission order.
   */
  ingest(event: WordEvent): Chunk[] {
    const emitted: Chunk[] = [];

    // 1. GAP trigger: a pause of more than 5.0 s before this event flushes
    //    whatever is buffered BEFORE the event itself is added.
    if (this.buffer.length > 0) {
      const lastBuffered = this.buffer[this.buffer.length - 1];
      if (event.s - lastBuffered.e > GAP_THRESHOLD_S) {
        emitted.push(this.emitBuffer("gap"));
      }
    }

    // 2. Add the event to the buffer.
    this.buffer.push(event);

    // 3. SIZE / TIME triggers, checked against the buffer as it now stands.
    let trigger: Trigger | null = null;
    if (this.buffer.length >= MAX_WORDS) {
      trigger = "size";
    } else if (event.e - this.buffer[0].s >= MAX_SPAN_S) {
      trigger = "time";
    }
    if (trigger !== null) {
      const idx = bestBreakIndex(this.buffer);
      const head = this.buffer.slice(0, idx + 1);
      this.buffer = this.buffer.slice(idx + 1);
      const chunk = makeChunk(head, trigger);
      this.chunks.push(chunk);
      emitted.push(chunk);
    }

    return emitted;
  }

  /** Feed a batch of events in order; returns every chunk they emit. */
  ingestAll(events: WordEvent[]): Chunk[] {
    const emitted: Chunk[] = [];
    for (const event of events) {
      emitted.push(...this.ingest(event));
    }
    return emitted;
  }

  /** Emit whatever is still buffered (trigger "flush"), or null if empty. */
  flush(): Chunk | null {
    if (this.buffer.length === 0) return null;
    return this.emitBuffer("flush");
  }

  private emitBuffer(trigger: Trigger): Chunk {
    const chunk = makeChunk(this.buffer, trigger);
    this.chunks.push(chunk);
    this.buffer = [];
    return chunk;
  }
}

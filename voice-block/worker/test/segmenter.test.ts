// segmenter.test.ts — algorithm tests for the pure segmenter.
// Runs with plain Node (type stripping), no build step:
//   node --test test/segmenter.test.ts test/worker.test.ts

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  SessionSegmenter,
  type WordEvent,
} from "../src/segmenter.ts";

/** Small builder: sequential words of fixed duration with a chosen pause after each. */
function stream(
  specs: Array<{ w: string; dur?: number; pauseAfter?: number }>,
): WordEvent[] {
  const out: WordEvent[] = [];
  let t = 0;
  for (const spec of specs) {
    const dur = spec.dur ?? 0.5;
    out.push({ w: spec.w, s: t, e: t + dur });
    t += dur + (spec.pauseAfter ?? 0.12);
  }
  return out;
}

test("gap: a >5s pause emits the buffer with trigger 'gap' before adding the new word", () => {
  const seg = new SessionSegmenter();
  const first = seg.ingestAll([
    { w: "alpha", s: 0.0, e: 0.4 },
    { w: "beta", s: 0.5, e: 0.9 },
    { w: "gamma", s: 1.0, e: 1.4 },
  ]);
  assert.equal(first.length, 0, "no chunk before the gap");

  // 8.0 - 1.4 = 6.6s of silence -> gap trigger.
  const emitted = seg.ingest({ w: "delta", s: 8.0, e: 8.4 });
  assert.equal(emitted.length, 1);
  assert.equal(emitted[0].trigger, "gap");
  assert.equal(emitted[0].wordCount, 3);
  assert.equal(emitted[0].text, "Alpha beta gamma");
  assert.equal(emitted[0].start, 0.0);
  assert.equal(emitted[0].end, 1.4);

  // The new word starts a fresh buffer; flush emits it alone.
  const rest = seg.flush();
  assert.ok(rest);
  assert.equal(rest.trigger, "flush");
  assert.equal(rest.wordCount, 1);
  assert.equal(rest.text, "Delta");
  assert.equal(seg.chunks.length, 2);
  assert.equal(seg.flush(), null, "second flush on empty buffer is null");
});

test("gap boundary: exactly 5.0s of silence does NOT split (rule is > 5.0)", () => {
  const seg = new SessionSegmenter();
  seg.ingest({ w: "one", s: 0, e: 1 });
  const emitted = seg.ingest({ w: "two", s: 6, e: 7 });
  assert.equal(emitted.length, 0);
  assert.equal(seg.buffer.length, 2);
});

test("size: 510 rapid words emit one 'size' chunk at the best break, remainder stays buffered", () => {
  const seg = new SessionSegmenter();
  const events: WordEvent[] = [];
  for (let i = 0; i < 510; i++) {
    const s = i * 0.1;
    events.push({ w: `w${i}`, s, e: s + 0.08 });
  }
  const emitted = seg.ingestAll(events);

  assert.equal(emitted.length, 1, "exactly one chunk emitted during ingest");
  const chunk = emitted[0];
  assert.equal(chunk.trigger, "size");
  // All interior pauses are 0.02 (score 0.02); the final word's pauseAfter
  // is 0 by definition, so the best break is after word index 498 and the
  // chunk holds 499 of the first 500 words. Ties go to the later boundary.
  assert.equal(chunk.wordCount, 499);
  assert.equal(chunk.start, 0);
  assert.ok(Math.abs(chunk.end - (498 * 0.1 + 0.08)) < 1e-9);

  // 1 leftover from the trigger batch + 10 more words = 11 buffered.
  const rest = seg.flush();
  assert.ok(rest);
  assert.equal(rest.trigger, "flush");
  assert.equal(rest.wordCount, 11);
});

test("time + best break: a sentence ending beats a larger raw pause", () => {
  // 120 words, 0.5s each, default pause 0.12s.
  // - after word 40 ("end."): pause 1.6 -> score min(1.6,3)+2.0 = 3.6
  // - after word 70: pause 2.9, no sentence end -> score 2.9
  // Every other boundary scores 0.12. The 60s span ceiling is first
  // crossed while ingesting word ~90, so both candidates are buffered
  // and the sentence boundary (word 40) must win despite the smaller pause.
  const specs = Array.from({ length: 120 }, (_, i) => ({
    w: i === 40 ? "end." : `t${i}`,
  }));
  specs[40] = { w: "end.", pauseAfter: 1.6 } as (typeof specs)[number];
  specs[70] = { w: "t70", pauseAfter: 2.9 } as (typeof specs)[number];
  const seg = new SessionSegmenter();
  const emitted = seg.ingestAll(stream(specs));

  assert.equal(emitted.length, 1, "exactly one chunk emitted during ingest");
  const chunk = emitted[0];
  assert.equal(chunk.trigger, "time");
  assert.equal(chunk.wordCount, 41, "break lands right after word index 40");
  assert.ok(chunk.text.endsWith("end."), `chunk ends at the sentence: ${chunk.text.slice(-20)}`);
  assert.equal(chunk.start, 0);
  assert.ok(Math.abs(chunk.end - 25.3) < 1e-6, `end=${chunk.end}`);

  // Remainder (words 41..119) never re-triggers and flushes as one chunk.
  const rest = seg.flush();
  assert.ok(rest);
  assert.equal(rest.trigger, "flush");
  assert.equal(rest.wordCount, 79);
});

test("rendering: paragraph break on >=2s pause and capitalization rules", () => {
  const seg = new SessionSegmenter();
  seg.ingestAll([
    { w: "hello", s: 0.0, e: 0.4 },
    { w: "world.", s: 0.5, e: 0.9 },
    { w: "next", s: 3.4, e: 3.8 }, // 2.5s pause -> "\n\n"; follows "world." -> capitalized
    { w: "again", s: 3.9, e: 4.3 }, // plain continuation, stays lowercase
  ]);
  const chunk = seg.flush();
  assert.ok(chunk);
  assert.equal(chunk.text, "Hello world.\n\nNext again");
  assert.equal(chunk.wordCount, 4);
  assert.equal(chunk.start, 0.0);
  assert.equal(chunk.end, 4.3);
});

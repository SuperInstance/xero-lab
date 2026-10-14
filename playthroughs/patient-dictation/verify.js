#!/usr/bin/env node
/*
 * verify.js — verify segmenter.js against the Python prototype.
 *
 *   A. The prototype's 16 unit tests (test_segmenter.py), ported
 *      assertion-for-assertion, run over the same fixture streams
 *      (fixtures.json — generated once by the real fixtures.py,
 *      since Python's PRNG is not JavaScript's).
 *   B. Full-output equality: for every stream, the JS chunk sequence
 *      (trigger, word count, rendered markdown, end_pause, boundary
 *      words) must equal ground-truth.json — the Python prototype's
 *      own recorded output on the identical streams. Same for the
 *      naive baseline and the size-isolated run.
 *   C. The modes simulator (modes/simulate.py), ported faithfully —
 *      tick interleaving, response timing, talked-over rule, async
 *      job model — must reproduce the simulator's published
 *      summaries (modes/RESULTS.md) exactly.
 *   D. demo.py's stats, recomputed from JS chunks, must match.
 *
 * Usage: node verify.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const VS = require(path.join(__dirname, "segmenter.js"));
const { Segmenter, endsSentence, naiveFixedWindow } = VS;

const fixtures = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures.json"), "utf8"));
const gt = JSON.parse(fs.readFileSync(path.join(__dirname, "ground-truth.json"), "utf8"));

let failures = 0;
let checksRun = 0;
function check(label, ok, detail) {
  checksRun++;
  console.log((ok ? "PASS" : "FAIL") + "  " + label + (detail ? " — " + detail : ""));
  if (!ok) failures++;
}
function eq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function close(a, b, tol) {
  if (a === null || b === null) return a === b;
  return Math.abs(a - b) <= (tol === undefined ? 1e-9 : tol);
}

function runStream(events, config) {
  const seg = new Segmenter(config);
  const chunks = [];
  for (const ev of events) chunks.push(...seg.feed(ev));
  const tail = seg.flush();
  if (tail !== null) chunks.push(tail);
  return chunks;
}
function streamWords(chunks) {
  return chunks.flatMap(c => c.words.map(w => w.word));
}
function W(word, start, end) { return { word, start, end }; }

/* ================= A. the 16 tests, ported ================= */

console.log("\n== A. test_segmenter.py, ported (16 tests) ==");

// TestTriggers.test_gap_trigger_per_burst
{
  const chunks = runStream(fixtures.stop_and_think_12);
  const gapChunks = chunks.filter(c => c.trigger === "gap");
  check("A1 gap trigger per burst (11 gap chunks, flush last, end_pause > 5)",
    gapChunks.length === 11 &&
    chunks[chunks.length - 1].trigger === "flush" &&
    gapChunks.every(c => c.endPause > 5.0),
    gapChunks.length + " gap chunks");
}

// TestTriggers.test_time_trigger_only_metronome
{
  const chunks = runStream(fixtures.metronome);
  const triggers = new Set(chunks.map(c => c.trigger));
  check("A2 metronome: time fires, gap/size never",
    triggers.has("time") && !triggers.has("gap") && !triggers.has("size"),
    [...triggers].join(","));
}

// TestTriggers.test_size_trigger_rapid_fire
{
  const chunks = runStream(fixtures.rapid_fire, { maxSeconds: 1e9 });
  const sizeChunks = chunks.filter(c => c.trigger === "size");
  check("A3 rapid fire, TIME disabled: >= 2 size chunks, no gap chunks",
    sizeChunks.length >= 2 && chunks.every(c => c.trigger !== "gap"),
    sizeChunks.length + " size chunks");
}

// TestTriggers.test_time_beats_size_at_speech_rate
{
  const chunks = runStream(fixtures.rapid_fire);
  check("A4 rapid fire, full cadence: time fires, size never",
    chunks.some(c => c.trigger === "time") &&
    chunks.every(c => c.trigger !== "size"), "");
}

// TestTriggers.test_monologue_uses_time_and_breaks
{
  const chunks = runStream(fixtures.monologue_60);
  check("A5 monologue uses the time trigger",
    chunks.some(c => c.trigger === "time"), chunks.length + " chunks");
}

// TestInvariants.test_no_word_loss_anywhere
{
  let ok = true, detail = "";
  for (const name of ["monologue", "stop_and_think", "rapid_fire", "metronome", "walk"]) {
    const events = fixtures[name];
    if (!eq(streamWords(runStream(events)), events.map(e => e.word))) {
      ok = false; detail = "word loss in " + name;
    }
  }
  check("A6 no word loss in any fixture", ok, detail || "all 5 fixtures, word-for-word");
}

// TestInvariants.test_chunk_word_cap
{
  let ok = true;
  for (const name of ["monologue", "stop_and_think", "rapid_fire", "metronome", "walk"]) {
    for (const c of runStream(fixtures[name])) if (c.wordCount > 500) ok = false;
  }
  check("A7 no chunk exceeds the 500-word cap", ok, "");
}

// TestInvariants.test_chunks_are_time_ordered
{
  let ok = true;
  for (const name of ["monologue", "stop_and_think", "rapid_fire", "metronome", "walk"]) {
    const starts = runStream(fixtures[name]).map(c => c.start);
    if (!eq(starts, starts.slice().sort((a, b) => a - b))) ok = false;
  }
  check("A8 chunks are time-ordered in every fixture", ok, "");
}

// TestBestBreak.test_prefers_pause_plus_sentence_over_trigger_point
{
  const events = [];
  let clock = 0.0;
  for (let i = 0; i < 500; i++) {
    let w = "word";
    if (i === 479) w = "halt.";
    events.push(W(w, clock, clock + 0.08));
    clock += 0.08 + (i === 479 ? 0.9 : 0.02);
  }
  const first = runStream(events)[0];
  check("A9 best break cuts at 480 (pause + sentence), not at the 500 trigger point",
    first.trigger === "size" && first.wordCount === 480 &&
    endsSentence(first.words[first.words.length - 1].word),
    "first chunk: " + first.trigger + ", " + first.wordCount + " words");
}

// TestBestBreak.test_break_beats_naive_mid_sentence_rate
{
  const events = fixtures.monologue_80;
  const smart = runStream(events);
  const naive = naiveFixedWindow(events);
  const rate = cs => cs.reduce((n, c) => n + (c.endsMidSentence ? 1 : 0), 0) / cs.length;
  check("A10 segmenter mid-sentence rate beats naive",
    rate(smart) < rate(naive),
    "smart " + rate(smart).toFixed(3) + " vs naive " + rate(naive).toFixed(3));
}

// TestMarkup helpers + tests
function oneChunk(events) {
  const seg = new Segmenter();
  for (const ev of events) {
    const out = seg.feed(ev);
    if (out.length !== 0) throw new Error("oneChunk: unexpected emission");
  }
  return seg.flush();
}
{
  const chunk = oneChunk([W("alpha", 0.0, 0.3), W("beta.", 0.35, 0.65),
                          W("gamma", 3.15, 3.45), W("delta.", 3.5, 3.8)]);
  check("A11 markup: paragraph break at a long pause, casing after sentence end",
    chunk.text.includes("\n\n") && chunk.text.includes("Gamma"),
    JSON.stringify(chunk.text));
}
{
  const events = [];
  let clock = 0.0;
  for (let i = 0; i < 12; i++) {
    const dur = i === 5 ? 1.3 : 0.25;
    events.push(W("w" + i, clock, clock + dur));
    clock += dur + 0.05;
  }
  const chunk = oneChunk(events);
  check("A12 markup: emphasis on the held word only",
    chunk.text.includes("*w5*") && !chunk.text.includes("*w4*"),
    JSON.stringify(chunk.text));
}
{
  const chunk = oneChunk([W("hello", 0.0, 0.3), W("there.", 0.35, 0.65)]);
  check("A13 markup: first word capitalized",
    chunk.text.startsWith("Hello"), JSON.stringify(chunk.text));
}

// TestTick.test_tick_emits_during_silence
{
  const seg = new Segmenter();
  seg.feed(W("one", 0.0, 0.3));
  seg.feed(W("two.", 0.35, 0.65));
  const early = seg.tick(3.0);
  const out = seg.tick(6.0);
  const after = seg.tick(9.0);
  check("A14 tick emits during silence, once",
    early.length === 0 && out.length === 1 && out[0].trigger === "gap" &&
    after.length === 0, "");
}

// TestEdges
check("A15 flush on an empty segmenter is null", new Segmenter().flush() === null, "");
{
  const seg = new Segmenter();
  const fed = seg.feed(W("solo", 0.0, 0.3));
  const chunk = seg.flush();
  check("A16 a single word flushes as a 1-word flush chunk",
    fed.length === 0 && chunk !== null && chunk.wordCount === 1 &&
    chunk.trigger === "flush", "");
}

/* ================= B. full-output equality vs Python ================= */

console.log("\n== B. chunk-for-chunk equality with the Python prototype ==");

function chunkDiff(jsChunks, pyChunks) {
  if (jsChunks.length !== pyChunks.length)
    return "chunk count " + jsChunks.length + " (JS) vs " + pyChunks.length + " (Python)";
  for (let i = 0; i < jsChunks.length; i++) {
    const j = jsChunks[i], p = pyChunks[i];
    if (j.trigger !== p.trigger) return "chunk " + i + ": trigger " + j.trigger + " vs " + p.trigger;
    if (j.wordCount !== p.wordCount) return "chunk " + i + ": " + j.wordCount + " words vs " + p.wordCount;
    if (j.text !== p.text) return "chunk " + i + ": rendered text differs";
    if (!close(j.endPause, p.endPause)) return "chunk " + i + ": endPause " + j.endPause + " vs " + p.endPause;
    if (j.endsMidSentence !== p.endsMidSentence) return "chunk " + i + ": mid-sentence flag differs";
    if (j.words[0].word !== p.firstWord || j.words[j.words.length - 1].word !== p.lastWord)
      return "chunk " + i + ": boundary words differ";
  }
  return null;
}

for (const name of Object.keys(fixtures)) {
  const events = fixtures[name];
  const d = chunkDiff(runStream(events), gt.streams[name].default);
  check("B default config == Python (" + name + ")", d === null,
    d || gt.streams[name].default.length + " chunks, texts identical");
  const dn = chunkDiff(naiveFixedWindow(events), gt.streams[name].naive);
  check("B naive baseline == Python (" + name + ")", dn === null,
    dn || gt.streams[name].naive.length + " chunks");
}
{
  const d = chunkDiff(runStream(fixtures.rapid_fire, { maxSeconds: 1e9 }),
                      gt.streams.rapid_fire.sizeIsolated);
  check("B size-isolated run == Python (rapid_fire)", d === null,
    d || gt.streams.rapid_fire.sizeIsolated.length + " chunks");
}

/* ================= C. modes simulator, ported ================= */

console.log("\n== C. modes simulator summaries == Python (modes/RESULTS.md numbers) ==");

const NEVER = 1e9;
const MODES = [
  { name: "eager", config: { maxWords: 120, maxSeconds: 15.0, gapTrigger: 0.8 }, work: false },
  { name: "patient", config: { maxWords: 500, maxSeconds: 1200.0, gapTrigger: NEVER }, work: false },
  { name: "async", config: {}, work: true }
];
const PROCESSING_S = 0.3;

function silences(events, minGap) {
  const out = [];
  for (let i = 0; i + 1 < events.length; i++) {
    if (events[i + 1].start - events[i].end > minGap)
      out.push([events[i].end, events[i + 1].start]);
  }
  return out;
}
function inSilence(t, sils) { return sils.some(([s, e]) => s <= t && t <= e); }

function simulate(mode, events) {
  const cfg = VS.makeConfig(mode.config);
  const seg = new Segmenter(mode.config);
  const streamEnd = events[events.length - 1].end;
  const sils = silences(events, 2.0);
  const emissions = [];
  let maxBuffered = 0, prevEnd = null;
  for (const ev of events) {
    if (prevEnd !== null && ev.start - prevEnd > cfg.gapTrigger) {
      const tickTime = prevEnd + cfg.gapTrigger + 0.05;
      for (const c of seg.tick(tickTime)) emissions.push([tickTime, c]);
    }
    for (const c of seg.feed(ev)) emissions.push([ev.end, c]);
    maxBuffered = Math.max(maxBuffered, seg.bufferedWords);
    prevEnd = ev.end;
  }
  const tail = seg.flush();
  if (tail !== null) emissions.push([streamEnd, tail]);

  const responses = emissions.map(([t]) => t + PROCESSING_S);
  const result = {
    first_response_s: responses.length ? responses[0] : null,
    chunks: emissions.length,
    responses: responses.length,
    max_buffered_words: maxBuffered,
    talked_over: null,
    jobs_done_while_talking: null,
    nudge_points: null
  };
  if (!mode.work) {
    let talked = 0;
    const starts = events.map(e => e.start);
    for (const rt of responses) {
      const nxt = starts.find(s => s > rt - PROCESSING_S);
      if (nxt !== undefined && nxt < rt) talked++;
    }
    result.talked_over = talked;
  }
  if (mode.work) {
    const jobs = emissions.filter(([t]) => t < streamEnd)
      .map(([t, c]) => [t, 5.0 + 0.02 * c.wordCount]);
    result.jobs_done_while_talking =
      jobs.filter(([t, d]) => t + d <= streamEnd).length;
    let nudges = jobs.length;
    for (let i = 0; i + 1 < events.length; i++) {
      const a = events[i], b = events[i + 1];
      if (b.start - a.end > 5.0 && jobs.some(([t, d]) => t <= a.end && a.end < t + d))
        nudges++;
    }
    for (const [t, d] of jobs) {
      for (const frac of [0.25, 0.5, 0.75]) {
        const tick = t + frac * d;
        if (tick <= streamEnd && !inSilence(tick, sils)) nudges++;
      }
    }
    result.nudge_points = nudges;
  }
  return result;
}

for (const name of ["walk", "monologue", "stop_and_think"]) {
  for (const mode of MODES) {
    const js = simulate(mode, fixtures[name]);
    const py = gt.modes[name][mode.name];
    const ok = close(js.first_response_s, py.first_response_s, 1e-6) &&
      js.chunks === py.chunks && js.responses === py.responses &&
      js.max_buffered_words === py.max_buffered_words &&
      js.talked_over === py.talked_over &&
      js.jobs_done_while_talking === py.jobs_done_while_talking &&
      js.nudge_points === py.nudge_points;
    check("C " + name + "/" + mode.name + " summary == Python", ok,
      "chunks " + js.chunks + ", 1st response " +
      (js.first_response_s === null ? "—" : js.first_response_s.toFixed(1) + "s") +
      ", max buffered " + js.max_buffered_words +
      (js.talked_over !== null ? ", talked over " + js.talked_over : "") +
      (js.jobs_done_while_talking !== null ?
        ", jobs " + js.jobs_done_while_talking + ", nudges " + js.nudge_points : ""));
  }
}

/* ================= D. demo.py stats from JS chunks ================= */

console.log("\n== D. demo.py stats recomputed from JS chunks ==");

function demoStats(chunks, events) {
  const mid = chunks.slice(0, -1).reduce((n, c) => n + (c.endsMidSentence ? 1 : 0), 0);
  const pauses = [];
  let n = 0;
  for (const c of chunks) {
    n += c.wordCount;
    if (n < events.length) pauses.push(events[n].start - events[n - 1].end);
  }
  return {
    chunks: chunks.length,
    midSentenceEnds: mid,
    meanBreakPause: pauses.length ? pauses.reduce((a, b) => a + b, 0) / pauses.length : 0.0
  };
}
for (const name of ["monologue", "stop_and_think", "rapid_fire", "walk"]) {
  const events = fixtures[name];
  const s = demoStats(runStream(events), events);
  const nv = demoStats(naiveFixedWindow(events), events);
  const p = gt.demo[name];
  check("D demo stats == Python (" + name + ")",
    s.chunks === p.segmenter.chunks &&
    s.midSentenceEnds === p.segmenter.midSentenceEnds &&
    close(s.meanBreakPause, p.segmenter.meanBreakPause) &&
    nv.chunks === p.naive.chunks &&
    nv.midSentenceEnds === p.naive.midSentenceEnds &&
    close(nv.meanBreakPause, p.naive.meanBreakPause),
    "segmenter " + s.chunks + " chunks, " + s.midSentenceEnds + " mid-sentence ends; " +
    "naive " + nv.chunks + " chunks, " + nv.midSentenceEnds + " mid-sentence ends");
}

console.log("\n" + (failures === 0
  ? "ALL CHECKS PASSED (" + checksRun + " checks)"
  : failures + " OF " + checksRun + " CHECK(S) FAILED"));
process.exit(failures === 0 ? 0 : 1);

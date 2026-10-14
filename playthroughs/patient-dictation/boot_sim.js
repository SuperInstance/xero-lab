#!/usr/bin/env node
"use strict";
/*
 * boot_sim.js — run the player.html boot check headlessly.
 *
 * Extracts the player's own boot-check functions (runStream,
 * silences, inSilence, SIM_MODES, simulate) and its pad schedule
 * builder (buildSchedule) verbatim from player.html, evaluates
 * them against segmenter.js, and executes:
 *   1. the exact comparisons the player's boot() performs against
 *      playthrough.json's finalState.checks;
 *   2. a pad sanity run: the sample script's schedule at 150 wpm
 *      through all three pad-mode configs with 50 ms wall-clock
 *      ticks — Patient must file nothing before the session-end
 *      flush; Eager must answer at a pause (gap chunk); words are
 *      conserved in every mode.
 * DOM rendering, animation, and live interaction are NOT covered
 * here — they need a real browser (see player.md).
 */
const fs = require("fs");
const path = require("path");

const HERE = __dirname;
const html = fs.readFileSync(path.join(HERE, "player.html"), "utf8");
const record = JSON.parse(fs.readFileSync(path.join(HERE, "playthrough.json"), "utf8"));
const fixtures = JSON.parse(fs.readFileSync(path.join(HERE, "fixtures.json"), "utf8"));
const VS = require(path.join(HERE, "segmenter.js"));

function extract(fromMarker, toMarker) {
  const a = html.indexOf(fromMarker);
  const b = html.indexOf(toMarker, a);
  if (a < 0 || b < 0) throw new Error("extraction failed: " + fromMarker);
  return html.slice(a, b);
}
const bootCode = extract("function runStream", "\n  function boot()");
const schedCode = extract("function buildSchedule", "\n  function updatePadStats");
const api = new Function("VS",
  bootCode + "\n" + schedCode +
  "\nreturn { runStream, simulate, SIM_MODES, buildSchedule };")(VS);

// ---- 1. the player's boot check, verbatim comparisons ----------------
const checks = record.finalState.checks;
let failures = 0, lines = [];
let totalChunks = 0;
for (const name of Object.keys(checks.fixtures)) {
  const events = fixtures[name];
  const chunks = api.runStream(events);
  const words = chunks.reduce((n, c) => n + c.wordCount, 0);
  const mid = chunks.slice(0, -1).reduce((n, c) => n + (c.endsMidSentence ? 1 : 0), 0);
  const want = checks.fixtures[name];
  totalChunks += chunks.length;
  const ok = chunks.length === want.chunks && words === want.words && mid === want.midSentenceEnds;
  if (!ok) failures++;
  lines.push(`${ok ? "PASS" : "FAIL"}  fixture ${name}: ${chunks.length} chunks, ` +
    `${words} words, ${mid} mid-sentence ends (record: ${want.chunks}/${want.words}/${want.midSentenceEnds})`);
}
for (const modeName of Object.keys(checks.walkModes)) {
  const got = api.simulate(api.SIM_MODES[modeName], fixtures.walk);
  const want = checks.walkModes[modeName];
  const ok = got.chunks === want.chunks && got.maxBuffered === want.maxBuffered &&
    got.talkedOver === want.talkedOver && got.jobsDone === want.jobsDone &&
    got.nudges === want.nudges &&
    Math.abs(got.firstResponseS - want.firstResponseS) <= 1e-6;
  if (!ok) failures++;
  lines.push(`${ok ? "PASS" : "FAIL"}  walk/${modeName}: ${got.chunks} chunks, ` +
    `maxBuffered ${got.maxBuffered}, first response ${got.firstResponseS.toFixed(3)} s ` +
    `(record matches: ${ok})`);
}

// ---- 2. pad sanity: sample schedule, three modes, 50 ms ticks --------
const SAMPLE = "the tide was slack when we left the dock and nobody had checked the bilge " +
  "since tuesday. you could hear the halyards ticking against the mast. the chart said " +
  "one thing and the sounder said another, so we marked the spot where the eddy folds " +
  "back on itself. a good watch is mostly a matter of noticing early. keep the red nun " +
  "to port and the channel opens up. the engine took two tries and then caught clean. " +
  "rain came sideways off the point just after dark. by the time we anchored the bay " +
  "had gone flat calm, and the coffee went cold before the fog burned off.";
const PAD = {
  patient: { maxWords: 500, maxSeconds: 1200, gapTrigger: 1e9 },
  eager: { maxWords: 120, maxSeconds: 15, gapTrigger: 0.8 },
  async: { maxWords: 500, maxSeconds: 60, gapTrigger: 5 },
};
for (const [mode, cfg] of Object.entries(PAD)) {
  const schedule = api.buildSchedule(SAMPLE, 150);
  const seg = new VS.Segmenter(cfg);
  const filed = [];
  let fed = 0, t = 0;
  const streamEnd = schedule[schedule.length - 1].end + 8; // 8 s of trailing silence
  while (t <= streamEnd) {
    while (fed < schedule.length && schedule[fed].end <= t) {
      seg.feed(schedule[fed]).forEach(c => filed.push(c));
      fed++;
    }
    seg.tick(t).forEach(c => filed.push(c));
    t += 0.05;
  }
  const tail = seg.flush();
  if (tail !== null) filed.push(tail);
  const wordsOut = filed.reduce((n, c) => n + c.wordCount, 0);
  const gapChunks = filed.filter(c => c.trigger === "gap").length;
  let ok = wordsOut === schedule.length;
  let note = "";
  if (mode === "patient") {
    const beforeFlush = filed.length - (tail !== null ? 1 : 0);
    ok = ok && beforeFlush === 0;
    note = `filed before session end: ${beforeFlush} (must be 0)`;
  }
  if (mode === "eager") {
    ok = ok && gapChunks >= 1;
    note = `gap chunks (answers at pauses): ${gapChunks} (must be ≥ 1)`;
  }
  if (!ok) failures++;
  lines.push(`${ok ? "PASS" : "FAIL"}  pad/${mode}: ${schedule.length} words in, ` +
    `${wordsOut} out, ${filed.length} chunks — ${note}`);
}

console.log(lines.join("\n"));
console.log(failures === 0
  ? `\nBOOT SIM: ALL PASS — the player's own boot code reproduces the record ` +
    `(${totalChunks} fixture chunks + the walk three ways), and the pad ` +
    `behaves per mode on the sample script.`
  : `\nBOOT SIM: ${failures} FAILURE(S)`);
process.exit(failures === 0 ? 0 : 1);

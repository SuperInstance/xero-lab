#!/usr/bin/env node
/*
 * verify.js — run the cascade.js port on the demo fixture and diff it
 * against the Python prototype's ground truth (ground-truth.json,
 * produced by trace.py from filing_loop.py itself).
 *
 * Checks:
 *   1. final file map byte-identical to Python's (every file's content)
 *   2. ledger (commit messages, in order) identical to Python's git log
 *   3. 35/35 entries survive (allSourceEntries per chat: 20 + 15)
 *   4. status counts match the prototype's (archive files, topic views)
 *   5. same topic assignments (topics/<chat>/*.md + INDEX.md contents —
 *      implied by check 1, asserted explicitly too)
 *   6. refine idempotent: state after a second refine round equals the
 *      state after the first, and equals Python's after-second-refine
 *
 * Usage: node verify.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { FilingStore } = require(path.join(__dirname, "cascade.js"));

const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, "fixture.json"), "utf8"));
const gt = JSON.parse(fs.readFileSync(path.join(__dirname, "ground-truth.json"), "utf8"));

let failures = 0;
function check(label, ok, detail) {
  console.log((ok ? "PASS" : "FAIL") + "  " + label + (detail ? " — " + detail : ""));
  if (!ok) failures++;
}

function diffMaps(a, b) {
  const diffs = [];
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of [...keys].sort()) {
    if (!(k in a)) diffs.push(k + " (only in Python)");
    else if (!(k in b)) diffs.push(k + " (only in JS)");
    else if (a[k] !== b[k]) diffs.push(k + " (content differs)");
  }
  return diffs;
}

// --- run the port on the fixture, exactly as demo.py does ---
const store = new FilingStore({ splitBytes: 1000, topicK: 8 });
store.init();
for (const d of fixture) store.deposit(d.chat, d.text, d.ts, d.source);
store.refine("telegram-main");
store.refine("zero-lab");
const afterRefine = store.snapshot();

// --- 1+2: state and ledger vs Python ---
const fileDiffs = diffMaps(gt.final.files, afterRefine.files);
check("final file map byte-identical to Python", fileDiffs.length === 0,
      fileDiffs.length ? fileDiffs.join("; ") : Object.keys(afterRefine.files).length + " files");

const ledgerSame = JSON.stringify(gt.final.ledger) === JSON.stringify(afterRefine.ledger);
check("ledger identical to Python git log", ledgerSame,
      afterRefine.ledger.length + " commits");

// --- 3: survival ---
const tm = store.allSourceEntries("telegram-main").length;
const zl = store.allSourceEntries("zero-lab").length;
check("35/35 entries survive the full cascade", tm + zl === 35 && tm === 20 && zl === 15,
      "telegram-main " + tm + ", zero-lab " + zl + ", deposited " + fixture.length);

// --- 4: status counts ---
const st = store.status();
check("status counts match the prototype",
      st.chats["telegram-main"].archiveFiles === 7 &&
      st.chats["telegram-main"].topicViews === 8 &&
      st.chats["zero-lab"].archiveFiles === 2 &&
      st.chats["zero-lab"].topicViews === 8 &&
      st.commits === 42,
      JSON.stringify(st.chats) + ", commits " + st.commits);

// --- 5: topic assignments (explicit) ---
function topicList(snap, chat) {
  const idx = snap.files["topics/" + chat + "/INDEX.md"] || "";
  return [...idx.matchAll(/^- \[(.+?)\]/gm)].map(m => m[1]);
}
check("topic assignments identical (telegram-main)",
      JSON.stringify(topicList(afterRefine, "telegram-main")) ===
      JSON.stringify(topicList(gt.final, "telegram-main")),
      topicList(afterRefine, "telegram-main").join(", "));
check("topic assignments identical (zero-lab)",
      JSON.stringify(topicList(afterRefine, "zero-lab")) ===
      JSON.stringify(topicList(gt.final, "zero-lab")),
      topicList(afterRefine, "zero-lab").join(", "));

// --- 6: idempotence ---
store.refine("telegram-main");
store.refine("zero-lab");
const afterRefine2 = store.snapshot();
check("refine idempotent (JS state unchanged by second refine)",
      JSON.stringify(afterRefine) === JSON.stringify(afterRefine2),
      "ledger still " + afterRefine2.ledger.length + " commits");
const fileDiffs2 = diffMaps(gt.after_second_refine.files, afterRefine2.files);
check("second-refine state also byte-identical to Python", fileDiffs2.length === 0,
      fileDiffs2.join("; "));

console.log(failures === 0 ? "\nALL CHECKS PASSED" : "\n" + failures + " CHECK(S) FAILED");
process.exit(failures === 0 ? 0 : 1);

/*
 * cascade.js — the filing cascade, ported faithfully from filing_loop.py
 * (the Python prototype in SuperInstance/xero-lab, filing-loop/).
 *
 * Chat deposits utterances into a folder; when the inbox file passes a
 * size gate it cascade-splits — first into daily archive files, then (if
 * a single day is still too big) into per-topic files inside that day.
 * An idle refine pass builds topic views + an index over the archive.
 * Every action appends to a ledger (in the prototype, the git log; here,
 * an in-memory list of the same commit messages).
 *
 * The store is an in-memory file map (path -> text). Pure, dependency-
 * free: runs in a browser or in Node. The port mirrors the Python
 * semantics exactly — same entry format, same keyword heuristic, same
 * tie-breaking (first-encounter order, as Python's Counter.most_common
 * documents) — and is verified byte-for-byte against the prototype on
 * the demo fixture (see VERIFY.md).
 *
 * Config: splitBytes (default 60000 ≈ 20 "pages"), topicK (default 8).
 */
(function (global) {
  "use strict";

  var SPLIT_BYTES_DEFAULT = 60000;
  var TOPIC_K_DEFAULT = 8;

  var HEADER_RE = /^## (\S+) — (.*)$/;
  var WORD_RE = /[a-z][a-z0-9\-]{2,}/g;
  var STOPWORDS = new Set(
    ("the a an and or of to in on for with is are was were be been it its " +
     "this that these those i you he she we they my his her our their me " +
     "him us them do does did can could will would should may might not " +
     "no yes if then than so as at by from into about over under again " +
     "just like get got one two all any out up down off too very").split(" ")
  );

  var encoder = typeof TextEncoder !== "undefined" ? new TextEncoder() : null;
  function byteSize(s) {
    if (encoder) return encoder.encode(s).length;
    // Fallback UTF-8 byte count (Node >= 11 and all modern browsers
    // have TextEncoder; this is belt-and-braces).
    var n = 0;
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c < 0x80) n += 1;
      else if (c < 0x800) n += 2;
      else if (c >= 0xd800 && c <= 0xdbff) { n += 4; i++; }
      else n += 3;
    }
    return n;
  }

  function wordFindall(text) {
    return text.match(WORD_RE) || [];
  }

  // ---------- entries ----------

  function parseEntries(text) {
    var entries = [], cur = null;
    var lines = text.split(/\r\n|\r|\n/);
    for (var i = 0; i < lines.length; i++) {
      var m = HEADER_RE.exec(lines[i]);
      if (m) {
        if (cur) entries.push(cur);
        cur = [m[1], m[2], []];
      } else if (cur !== null) {
        cur[2].push(lines[i]);
      }
    }
    if (cur) entries.push(cur);
    return entries.map(function (e) {
      return [e[0], e[1], e[2].join("\n").trim()];
    });
  }

  function renderEntry(ts, source, body) {
    return "## " + ts + " — " + source + "\n" + body.trim() + "\n\n";
  }

  // ---------- topics (deterministic heuristic, same seam as the Python) ----------

  // Counter over all texts; ties keep first-encounter order (Python's
  // Counter.most_common documents exactly this; JS Map preserves
  // insertion order and Array.sort is stable).
  function topKeywords(texts, k) {
    var counts = new Map();
    texts.forEach(function (t) {
      wordFindall(t.toLowerCase()).forEach(function (w) {
        if (STOPWORDS.has(w)) return;
        counts.set(w, (counts.get(w) || 0) + 1);
      });
    });
    return Array.from(counts.entries())
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, k)
      .map(function (e) { return e[0]; });
  }

  function primaryTopic(body, topics) {
    var words = new Map();
    wordFindall(body.toLowerCase()).forEach(function (w) {
      words.set(w, (words.get(w) || 0) + 1);
    });
    var best = "misc", bestN = 0;
    topics.forEach(function (t) {
      var n = words.get(t) || 0;
      if (n > bestN) { best = t; bestN = n; }
    });
    return best;
  }

  // ---------- the store ----------

  function FilingStore(options) {
    options = options || {};
    this.splitBytes = options.splitBytes != null ? options.splitBytes : SPLIT_BYTES_DEFAULT;
    this.topicK = options.topicK != null ? options.topicK : TOPIC_K_DEFAULT;
    this.files = new Map();   // path -> text
    this.ledger = [];         // commit messages, oldest -> newest
    this._committed = this._fingerprint();
  }

  FilingStore.prototype._fingerprint = function () {
    var keys = Array.from(this.files.keys()).sort();
    var parts = [];
    for (var i = 0; i < keys.length; i++) parts.push(keys[i] + "\0" + this.files.get(keys[i]));
    return parts.join("\0\0");
  };

  // Mirror of the prototype's git_commit: record only if state changed.
  FilingStore.prototype._commit = function (message) {
    var fp = this._fingerprint();
    if (fp === this._committed) return false;
    this._committed = fp;
    this.ledger.push(message);
    return true;
  };

  FilingStore.prototype._readEntries = function (path) {
    if (!this.files.has(path)) return [];
    return parseEntries(this.files.get(path));
  };

  FilingStore.prototype._appendEntries = function (path, entries) {
    var text = this.files.has(path) ? this.files.get(path) : "";
    for (var i = 0; i < entries.length; i++) {
      text += renderEntry(entries[i][0], entries[i][1], entries[i][2]);
    }
    this.files.set(path, text);
  };

  // Immediate child names (files and directory names) under dir.
  FilingStore.prototype._children = function (dir) {
    var prefix = dir + "/", names = new Set();
    this.files.forEach(function (_, key) {
      if (key.indexOf(prefix) === 0) {
        names.add(key.slice(prefix.length).split("/")[0]);
      }
    });
    return Array.from(names);
  };

  FilingStore.prototype._isDir = function (path) {
    var prefix = path + "/";
    var found = false;
    this.files.forEach(function (_, key) {
      if (key.indexOf(prefix) === 0) found = true;
    });
    return found;
  };

  // ---------- init ----------

  // Create the store if needed. Returns true if it was created.
  FilingStore.prototype.init = function () {
    if (this.files.size > 0) return false;
    this.files.set("README.md",
      "# filing-loop store\n\nChat deposits, filed by the loop. " +
      "The git log is the ledger.\n");
    this._commit("init: filing-loop store");
    return true;
  };

  // ---------- deposit ----------

  FilingStore.prototype.deposit = function (chat, text, ts, source) {
    if (ts == null) ts = localIsoSeconds(new Date());
    if (source == null) source = "chat";
    this._appendEntries("inbox/" + chat + "/current.md", [[ts, source, text]]);
    this._commit("deposit: " + chat + " " + ts);
    this.cascadeSplit(chat);
  };

  // ---------- cascade split ----------

  FilingStore.prototype.cascadeSplit = function (chat) {
    var cur = "inbox/" + chat + "/current.md";
    if (!this.files.has(cur) || byteSize(this.files.get(cur)) <= this.splitBytes) return;
    var entries = this._readEntries(cur);
    var byDay = new Map();
    entries.forEach(function (e) {
      var day = e[0].slice(0, 10);
      if (!byDay.has(day)) byDay.set(day, []);
      byDay.get(day).push(e);
    });
    var days = Array.from(byDay.keys()).sort();
    for (var i = 0; i < days.length; i++) {
      this._appendEntries("archive/" + chat + "/" + days[i] + ".md", byDay.get(days[i]));
    }
    this.files.set(cur, ""); // inbox drained
    this._commit("split L1: " + chat + " -> " + days.length + " daily file(s)");

    // level 2: any daily file still over the gate splits by topic
    for (var j = 0; j < days.length; j++) {
      var day = days[j];
      var dayFile = "archive/" + chat + "/" + day + ".md";
      if (byteSize(this.files.get(dayFile)) <= this.splitBytes) continue;
      var dayEntries = this._readEntries(dayFile);
      var topics = topKeywords(dayEntries.map(function (e) { return e[2]; }), this.topicK);
      var byTopic = new Map();
      dayEntries.forEach(function (e) {
        var t = primaryTopic(e[2], topics);
        if (!byTopic.has(t)) byTopic.set(t, []);
        byTopic.get(t).push(e);
      });
      var topicNames = Array.from(byTopic.keys()).sort();
      for (var k = 0; k < topicNames.length; k++) {
        this._appendEntries("archive/" + chat + "/" + day + "/" + topicNames[k] + ".md",
                            byTopic.get(topicNames[k]));
      }
      this.files.delete(dayFile);
      this._commit("split L2: " + chat + " " + day + " -> " + byTopic.size + " topic file(s)");
    }
  };

  // ---------- refine (idle churn): topic views + index ----------

  FilingStore.prototype.allSourceEntries = function (chat) {
    var entries = this._readEntries("inbox/" + chat + "/current.md");
    var arch = "archive/" + chat;
    var self = this;
    this._children(arch).sort().forEach(function (name) {
      var p = arch + "/" + name;
      if (self.files.has(p)) {
        if (name.slice(-3) === ".md") {
          entries = entries.concat(self._readEntries(p));
        }
      } else if (self._isDir(p)) {
        self._children(p).sort().forEach(function (sub) {
          if (sub.slice(-3) === ".md") {
            entries = entries.concat(self._readEntries(p + "/" + sub));
          }
        });
      }
    });
    return entries;
  };

  // Rebuild topic views for one chat. Returns entries processed.
  // Like the prototype: views are regenerated wholesale (stale topic
  // files are not deleted), so refine is idempotent.
  FilingStore.prototype.refine = function (chat) {
    var entries = this.allSourceEntries(chat);
    if (!entries.length) return 0;
    var topics = topKeywords(entries.map(function (e) { return e[2]; }), this.topicK);
    var tdir = "topics/" + chat;
    var index = ["# topics — " + chat + "\n",
                 entries.length + " entries, " + topics.length +
                   " topics. Generated by refine; regenerate freely.\n"];
    for (var i = 0; i < topics.length; i++) {
      var topic = topics[i];
      var hits = entries.filter(function (e) {
        return wordFindall(e[2].toLowerCase()).indexOf(topic) !== -1;
      });
      var content = "# " + topic + " — " + chat + "\n\n";
      hits.forEach(function (e) { content += renderEntry(e[0], e[1], e[2]); });
      this.files.set(tdir + "/" + topic + ".md", content);
      index.push("- [" + topic + "](" + topic + ".md) — " + hits.length + " entries");
    }
    this.files.set(tdir + "/INDEX.md", index.join("\n") + "\n");
    this._commit("refine: " + chat + " topics (" + topics.join(", ") + ")");
    return entries.length;
  };

  // ---------- status / snapshot ----------

  FilingStore.prototype.status = function () {
    var chats = new Set(), self = this;
    ["inbox", "archive", "topics"].forEach(function (sub) {
      self._children(sub).forEach(function (c) { chats.add(c); });
    });
    var out = { chats: {}, commits: this.ledger.length };
    Array.from(chats).sort().forEach(function (chat) {
      var nfiles = 0;
      self.files.forEach(function (_, key) {
        if (key.indexOf("archive/" + chat + "/") === 0 && key.slice(-3) === ".md") nfiles++;
      });
      var ntopics = 0;
      self.files.forEach(function (_, key) {
        if (key.indexOf("topics/" + chat + "/") === 0 &&
            key.slice(-3) === ".md" && key !== "topics/" + chat + "/INDEX.md") ntopics++;
      });
      out.chats[chat] = {
        entries: self.allSourceEntries(chat).length,
        archiveFiles: nfiles,
        topicViews: ntopics
      };
    });
    return out;
  };

  // Plain-object copy of the whole state ({files: {path: text}, ledger}).
  FilingStore.prototype.snapshot = function () {
    var files = {};
    var keys = Array.from(this.files.keys()).sort();
    for (var i = 0; i < keys.length; i++) files[keys[i]] = this.files.get(keys[i]);
    return { files: files, ledger: this.ledger.slice() };
  };

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function localIsoSeconds(d) {
    var off = -d.getTimezoneOffset();
    var sign = off >= 0 ? "+" : "-";
    off = Math.abs(off);
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) +
      sign + pad(Math.floor(off / 60)) + ":" + pad(off % 60);
  }

  var api = {
    FilingStore: FilingStore,
    parseEntries: parseEntries,
    renderEntry: renderEntry,
    topKeywords: topKeywords,
    primaryTopic: primaryTopic,
    byteSize: byteSize,
    STOPWORDS: STOPWORDS
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    global.FilingCascade = api;
  }
})(typeof window !== "undefined" ? window : globalThis);

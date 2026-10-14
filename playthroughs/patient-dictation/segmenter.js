/*
 * segmenter.js — the voice-block segmenter, ported faithfully from
 * segmenter.py (the Python reference implementation in
 * SuperInstance/xero-lab, voice-block/segmenter/).
 *
 * Takes a word-timed transcript stream (each word carries start/end
 * times in seconds, as an STT engine produces) and emits markdown
 * chunks of at most ~3/4 of a page (~500 words), on a cadence:
 *
 *   GAP  — a speech gap longer than gapTrigger (default 5 s) ends
 *          the current chunk. The gap is the natural break, and the
 *          interrupt surface in the modes built on top of this block.
 *   SIZE — maxWords (default 500) accumulated.
 *   TIME — maxSeconds (default 60 s) elapsed in the current chunk.
 *
 * SIZE/TIME do not cut blindly at the trigger point: they pick the
 * BEST BREAK inside the buffer, scored as
 *
 *     score(boundary after word i) = min(pause_after_i, 3.0)
 *                                    + 2.0 if word i ends a sentence
 *
 * with ties going to the LATER boundary. The remainder after the
 * break stays buffered and starts the next chunk.
 *
 * The assembler adds the light markup the timing signal supports:
 * paragraph breaks at chunk starts and at internal pauses >=
 * paraPause (default 2 s); sentence casing; *emphasis* on words
 * held notably long (duration >= emphasisRatio x the chunk's median
 * word duration and >= emphasisMinDur seconds).
 *
 * Pure, dependency-free: runs in a browser or in Node. The port
 * mirrors the Python semantics exactly — same triggers, same
 * scoring, same tie-breaking, same markup — and is verified against
 * the prototype test-for-test and chunk-for-chunk on the same
 * fixture streams (see VERIFY.md).
 */
(function (global) {
  "use strict";

  var SENTENCE_ENDERS = [".", "!", "?"];
  // Python: word.rstrip().rstrip("\"'”’)]").rstrip()
  var TRAILING_STRIP = "\"'”’)]";

  function rstripWs(s) {
    return s.replace(/\s+$/u, "");
  }

  function endsSentence(word) {
    var w = rstripWs(String(word));
    var cut = w.length;
    while (cut > 0 && TRAILING_STRIP.indexOf(w.charAt(cut - 1)) >= 0) cut--;
    w = rstripWs(w.slice(0, cut));
    return SENTENCE_ENDERS.indexOf(w.charAt(w.length - 1)) >= 0;
  }

  function pauseAfter(words, i) {
    if (i >= words.length - 1) return 0.0;
    return Math.max(0.0, words[i + 1].start - words[i].end);
  }

  function duration(w) {
    return w.end - w.start;
  }

  function median(xs) {
    // statistics.median: middle value, or mean of the two middles.
    var s = xs.slice().sort(function (a, b) { return a - b; });
    var n = s.length, mid = Math.floor(n / 2);
    return n % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2.0;
  }

  function isLowerChar(ch) {
    return ch.length === 1 && ch.toLowerCase() === ch && ch.toUpperCase() !== ch;
  }

  var CONFIG_DEFAULTS = {
    maxWords: 500,        // ~3/4 page
    maxSeconds: 60.0,     // cadence: time trigger
    gapTrigger: 5.0,      // cadence: speech gap that emits
    paraPause: 2.0,       // internal pause that becomes a paragraph break
    emphasisRatio: 1.8,
    emphasisMinDur: 0.40
  };

  function makeConfig(overrides) {
    var cfg = {};
    Object.keys(CONFIG_DEFAULTS).forEach(function (k) {
      cfg[k] = CONFIG_DEFAULTS[k];
    });
    if (overrides) {
      Object.keys(overrides).forEach(function (k) {
        if (k in CONFIG_DEFAULTS) cfg[k] = overrides[k];
      });
    }
    return cfg;
  }

  function Chunk(words, trigger, endPause) {
    this.words = words;
    this.trigger = trigger;              // 'gap' | 'size' | 'time' | 'flush'
    this.text = "";                      // rendered markdown
    this.endPause = (endPause === undefined ? null : endPause);
  }
  Object.defineProperties(Chunk.prototype, {
    start: { get: function () { return this.words[0].start; } },
    end: { get: function () { return this.words[this.words.length - 1].end; } },
    wordCount: { get: function () { return this.words.length; } },
    endsMidSentence: {
      get: function () { return !endsSentence(this.words[this.words.length - 1].word); }
    }
  });

  function Segmenter(config) {
    this.config = makeConfig(config);
    this._buf = [];
  }

  Segmenter.prototype.feed = function (ev) {
    /* Feed one word event {word, start, end}; returns any chunks emitted. */
    var emitted = [];
    var cfg = this.config;

    // GAP trigger: the pause *before* this word ends the old chunk.
    if (this._buf.length) {
      var gap = ev.start - this._buf[this._buf.length - 1].end;
      if (gap > cfg.gapTrigger) {
        emitted.push(this._emit(this._buf.length, "gap", gap));
      }
    }

    this._buf.push(ev);

    // SIZE / TIME triggers, with best-break selection. Loop: the
    // remainder after a break may still violate a trigger.
    while (this._buf.length) {
      var trig;
      if (this._buf.length >= cfg.maxWords) {
        trig = "size";
      } else if (this._buf[this._buf.length - 1].end - this._buf[0].start >= cfg.maxSeconds) {
        trig = "time";
      } else {
        break;
      }
      var cut = this._bestBreak();
      emitted.push(this._emit(cut, trig, pauseAfter(this._buf, cut - 1)));
    }
    return emitted;
  };

  Segmenter.prototype.flush = function () {
    if (!this._buf.length) return null;
    return this._emit(this._buf.length, "flush", null);
  };

  Segmenter.prototype.tick = function (now) {
    /* Wall-clock check, for live deployments: if the last word ended
     * more than gapTrigger seconds ago, the gap has happened *now* —
     * emit without waiting for speech to resume. The recorded
     * endPause is a lower bound on the true gap. */
    if (this._buf.length &&
        now - this._buf[this._buf.length - 1].end > this.config.gapTrigger) {
      var gap = now - this._buf[this._buf.length - 1].end;
      return [this._emit(this._buf.length, "gap", gap)];
    }
    return [];
  };

  Object.defineProperty(Segmenter.prototype, "bufferedWords", {
    get: function () { return this._buf.length; }
  });

  Segmenter.prototype._bestBreak = function () {
    /* Cut index: emit buf[:cut], keep buf[cut:]. Every boundary is a
     * candidate; ties go to the later boundary. */
    var bestI = this._buf.length, bestScore = -1.0;
    for (var i = 0; i < this._buf.length; i++) {
      var score = Math.min(pauseAfter(this._buf, i), 3.0);
      if (endsSentence(this._buf[i].word)) score += 2.0;
      if (score >= bestScore) {  // >= : later boundary wins ties
        bestI = i + 1; bestScore = score;
      }
    }
    return bestI;
  };

  Segmenter.prototype._emit = function (cut, trigger, endPause) {
    var words = this._buf.slice(0, cut);
    this._buf = this._buf.slice(cut);
    var chunk = new Chunk(words, trigger, endPause);
    chunk.text = renderMarkdown(words, this.config);
    return chunk;
  };

  function renderMarkdown(words, cfg) {
    /* Assemble chunk text with the light, signal-supported markup. */
    if (!words.length) return "";
    var durations = words.map(duration);
    var medianDur = durations.length ? median(durations) : 0.0;

    function isEmphatic(w) {
      return duration(w) >= cfg.emphasisMinDur &&
        medianDur > 0 &&
        duration(w) >= cfg.emphasisRatio * medianDur;
    }

    var out = [];
    var prev = null;
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      var token = w.word;
      // Paragraph break at a long internal pause.
      if (prev !== null && (w.start - prev.end) >= cfg.paraPause) {
        out.push("\n\n");
      }
      // Sentence casing.
      if ((i === 0 || endsSentence(prev ? prev.word : "")) &&
          token.length && isLowerChar(token.charAt(0))) {
        token = token.charAt(0).toUpperCase() + token.slice(1);
      }
      if (isEmphatic(w)) token = "*" + token + "*";
      out.push(token);
      prev = w;
    }
    // Join: words space-separated, paragraph markers already placed.
    var text = "";
    out.forEach(function (piece) {
      if (piece === "\n\n") text += "\n\n";
      else if (text === "" || text.endsWith("\n\n")) text += piece;
      else text += " " + piece;
    });
    return text;
  }

  function naiveFixedWindow(events, config) {
    /* Baseline: cut at exactly maxWords or maxSeconds, wherever the
     * stream happens to be. No gap trigger, no break search, no
     * markup beyond plain joining. */
    var cfg = makeConfig(config);
    var chunks = [];
    var buf = [];
    events.forEach(function (ev) {
      buf.push(ev);
      if (buf.length >= cfg.maxWords ||
          (buf[buf.length - 1].end - buf[0].start) >= cfg.maxSeconds) {
        var c = new Chunk(buf.slice(), "naive", null);
        c.text = buf.map(function (w) { return w.word; }).join(" ");
        chunks.push(c);
        buf = [];
      }
    });
    if (buf.length) {
      var c = new Chunk(buf.slice(), "naive", null);
      c.text = buf.map(function (w) { return w.word; }).join(" ");
      chunks.push(c);
    }
    return chunks;
  }

  var api = {
    Segmenter: Segmenter,
    Chunk: Chunk,
    makeConfig: makeConfig,
    CONFIG_DEFAULTS: CONFIG_DEFAULTS,
    endsSentence: endsSentence,
    pauseAfter: pauseAfter,
    renderMarkdown: renderMarkdown,
    naiveFixedWindow: naiveFixedWindow
  };

  global.VoiceSegmenter = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);

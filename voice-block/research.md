# Voice Block — Prior-Art Research (Seed)

**Date:** 2026-10-12
**Status:** Seed document for proof-of-concept work. Patterns to call on, not decisions. Anything marked **UNVERIFIED** was not confirmed against a source in this pass and should not be treated as fact.
**Scope:** A minimal voice agent that transcribes English speech, segments a word-timed transcript stream into markdown chunks of ≤ ~3/4 page (~500 words), and emits a chunk on a cadence of ≥60 s elapsed OR ≥3/4 page accumulated OR a speech gap >5 s, choosing the break point by pause duration and sentence boundaries. Three modes are configs of the same block: **EAGER**, **PATIENT**, **ASYNC-PARALLEL** (defined in §C).

## Method note

- A MiniMax synthesis pass was run first, as planned, via `~/workspace/skills/minimax/bin/chat.py` (full output saved by the runner to `/tmp/minimax-voiceblock.txt` during the session; an early partial log misleadingly showed a 401, but the completed run returned a full synthesis). Its output was **generic and largely unsourced**: correct on a few well-known facts, wrong or unverifiable on most specific numbers (itemised in §D, item 1). **No MiniMax number is used in this file unless it was independently verified** against vendor docs, project repos, benchmarks, or reporting via `browser.search` / page fetches.
- Two verification searches also failed at the tool level (Deepgram classic endpointing; one OpenAI Realtime query). Those topics are marked as gaps in §D rather than filled from memory.
- Sources are paraphrased, not quoted at length. Secondary sources are labelled as such; prefer the primary link where both exist.

---

## A. Landscape by topic

### 1. Endpointing / turn-taking

**The human baseline.** Cross-language conversation research (Stivers et al., 2009, as summarised by Scientific American and the EU INTERACT project) puts the typical gap between a question and its answer at roughly **200 ms**, with medians across languages in the 0–300 ms range. That speed is only possible because listeners predict the end of a turn while it is still unfolding — planning a single word already takes ~600 ms. Implication for the block: a purely reactive silence timer is structurally slower than human turn-taking; every production system below is, in some way, trying to predict rather than wait.
Sources: https://www.scientificamerican.com/article/universal-social-rules-underlie-languages · https://cordis.europa.eu/article/id/191265-turntaking-in-human-communication

**Layer 1 — VAD (is anyone speaking?).**

- **WebRTC VAD** — the classic signal-processing VAD. Per-frame binary decision on exactly **10, 20, or 30 ms** frames of 16-bit mono PCM at 8/16/32/48 kHz; aggressiveness **modes 0–3** (0 = least filtering, 3 = most; mode 2–3 is the usual choice for noisy real-world audio, 0–1 for clean close-mic). It has no segmentation logic of its own — hangover, min-speech, and min-silence rules are yours to build on top.
  Sources: https://github.com/kbhatiya999/webrtc-vad-demo · https://github.com/rolandhe/go-vad
- **Silero VAD** — small neural VAD (~1–2 MB ONNX in most distributions), returns a continuous **speech probability 0.0–1.0** instead of a binary flag, evaluated on **32 ms chunks** (512 samples @ 16 kHz; 256 @ 8 kHz), typically in under 1 ms per chunk on CPU. The near-universal default threshold is **0.5**. Only 8 kHz and 16 kHz are supported. In faster-whisper-style pipelines it is commonly paired with `min_silence_duration_ms` around **500 ms** so brief intra-sentence pauses are not treated as segment ends, and long silences (>2 s) are stripped before transcription.
  Sources: https://github.com/hagarmhassan/wavekat-vad · https://localai.io/docs/features/voice-activity-detection/

**Layer 2 — silence timers (the naive endpoint, still everywhere).** A fixed silence duration after last speech fires end-of-turn. Seen in the wild:

- Telephony/conversational agents cluster at **300–700 ms** (300 ms described as a reasonable phone floor; 500 ms+ of extra delay becomes audible on top of network transit).
- LiveKit Agents exposes the timer as a floor/ceiling pair: `min_endpointing_delay` / `max_endpointing_delay`, with example configurations of **0.5 s / 3.0 s**, **0.3 s / 5.0 s**, and **0.4 s / 6.0 s**. The ceiling matters as much as the floor — an unset ceiling can mean multi-second dead air on a noisy line.
  Sources (secondary, code examples): https://github.com/livekit/eot-bench · https://github.com/andre-mygentic/context-engineering-livekit/blob/HEAD/PRPs/ai_docs/livekit_patterns.md
- Gemini Live's automatic activity detection exposes the same shape: start/end-of-speech sensitivity (HIGH/LOW), `prefix_padding_ms` (example values 20–40 ms), and `silence_duration_ms` (examples and tuned values of **100 ms default in one secondary summary, 500 ms in tuned production configs**). Manual mode (client sends explicit activity start/end) is the documented escape hatch for push-to-talk and noisy environments.
  Source (secondary summary of Google's API): https://github.com/dhuynh95/duck_talk/blob/HEAD/docs/gemini-live-api-swift-reference.md

**Layer 3 — semantic / learned end-of-turn models.** The current direction of travel: a model scores whether the turn is *complete* (prosody and/or transcript), and the silence timer demotes to a backstop.

- **Deepgram Flux** (vendor docs, verified): turn detection is built into the STT model and exposed as confidence thresholds, not milliseconds. `eot_threshold` default **0.7** (range 0.5–1.0); `eager_eot_threshold` range 0.3–0.9, unset by default — crossing it fires an *EagerEndOfTurn* event that can start speculative LLM work, followed by either a confirmed *EndOfTurn* or a *TurnResumed* if the speaker continues; `eot_timeout_ms` default **5,000 ms** (range 500–60,000) is the hard silence backstop regardless of confidence. Recommended streaming chunk size is 80 ms of audio. Setting `eot_threshold` to 1.0 suppresses natural endpointing entirely so the application can drive turns itself.
  Sources: https://developers.deepgram.com/docs/flux/configuration · https://developers.deepgram.com/docs/flux/quickstart
- **Deepgram classic (Nova-era) endpointing / UtteranceEnd** — **UNVERIFIED in this pass** (see §D). Do not rely on remembered values for `endpointing` / `utterance_end_ms` without re-checking the docs.
- **LiveKit Turn Detector** — a learned detector layered over VAD + STT. LiveKit's own open benchmark (eot-bench) is the most useful artefact found in this whole pass: it scores detectors on the *trade-off* between false cutoffs and response latency rather than a single accuracy number. At a **5% false-cutoff budget**, its v1 detector's endpointing delay is **543 ms** (295 ms at a 10% budget), versus **1,600 ms for a silence-only VAD baseline** at the same budget. Other systems in the same table: Deepgram Flux 1,151 ms, Smart Turn v3.2 1,051 ms, Soniox 647 ms. VAD baseline false-cutoff rate at a 300 ms latency budget: **55.6%** — i.e., a fast silence timer cuts the speaker off more often than not.
  Source: https://github.com/livekit/eot-bench
- **Pipecat Smart Turn v3** — open (BSD-2) audio-prosody model: a Whisper-tiny encoder plus classifier head, ~8M parameters, reads up to the **last 8 seconds** of a turn at 16 kHz and outputs a single turn-complete probability; ~65 ms inference on a standard cloud instance (10–65 ms depending on hardware in secondary testing); 23 languages. Designed to run *when VAD fires*, not instead of it: VAD finds the pause, Smart Turn judges whether the pause is an ending. Pipecat uses it as its default turn-ending mechanism.
  Sources: https://github.com/godefroy/micdrop/blob/HEAD/website/src/content/blog/end-of-turn-detection-voice-agents/index.mdx · https://github.com/786262170/smart-turn
- **OpenAI Realtime "semantic VAD"** — secondary reporting describes an internal turn-detection score converted into a wait capped at **2, 4, or 8 seconds** depending on an `eagerness` setting. **Treat as UNVERIFIED against official docs** (the official-docs search failed in this pass; see §D).
  Source (secondary): https://github.com/godefroy/micdrop/blob/HEAD/website/src/content/blog/end-of-turn-detection-voice-agents/index.mdx
- **Azure Speech and Picovoice (Cobra VAD / endpointer products)** — **no verified specifics found in this pass** (see §D).

**Takeaway for the block:** the field has converged on a three-layer stack — VAD (10–32 ms frames) → learned completeness judgement → silence backstop measured in *seconds*. The voice block's >5 s gap rule sits comfortably in backstop territory; nothing found suggests 5 s is too long for a *dictation/chunking* (as opposed to conversational) backstop, and Flux's 5 s default backstop is a direct precedent.

### 2. Barge-in handling

**Mechanics (Pipecat pattern, the clearest public write-up found).** With interruptions enabled, VAD detecting user speech during agent playback pushes an interruption through the pipeline that does three things: (1) cancels in-flight LLM generation, (2) flushes the TTS stream and queued audio — actual silence arrives only after already-buffered audio plays out, on the order of **200–400 ms** in a telephony setup, and (3) records into context only the text that was *actually spoken* before the cut. Point (3) is the subtle, steal-worthy one: if the transcript-of-record keeps the full intended reply, the agent later believes it said things the user never heard.
Source: https://github.com/hhagenbuch/voice-agent/blob/HEAD/docs/notes/02-turn-taking-and-interruptions.md

**Supporting knobs seen in framework configs:**

- LiveKit-style `min_interruption_duration` ≈ **0.5 s** of user speech before an interruption is honoured — a debounce against coughs and backchannels ("mm-hm"). Other implementations use a shorter sustain window on echo-cleaned audio, ~**120–200 ms**.
  Sources: https://github.com/andre-mygentic/context-engineering-livekit/blob/HEAD/PRPs/ai_docs/livekit_patterns.md · https://github.com/salihavcioglu/sesly/blob/HEAD/docs/specs/02-conversational-agent.md
- Gemini Live makes barge-in a config choice: activity handling is either *start-of-activity interrupts* (default) or *no interruption*, in which case the model finishes speaking regardless.
  Source: https://github.com/dhuynh95/duck_talk/blob/HEAD/docs/gemini-live-api-swift-reference.md

**Failure modes (all documented in the sources above):**

1. **Self-interruption via echo.** On speakerphone, agent output leaks into the mic, VAD reads it as user speech, and the agent interrupts itself — and worse, *transcribes its own greeting as a user turn* and reasons over it. Word-count gates (require N words to interrupt while the agent is speaking) only partially help and break genuine one-word interruptions like "stop". Real fixes, in order of reliability: headphones (physical isolation), platform AEC with the far-end reference signal, muting input while speaking (works, but abolishes barge-in entirely). Noise suppression (RNNoise etc.) is **not** echo cancellation and cannot subtract a known talker.
   Sources: https://github.com/hhagenbuch/voice-agent/blob/HEAD/docs/notes/02-turn-taking-and-interruptions.md · https://www.testmuai.com/blog/barge-in-testing-voice-agents/
2. **Echo-cancellation warm-up eating short first answers.** A documented telephony defect: the AEC convergence window at call start can delete the first seconds of inbound audio, so a short first "yes" never reaches transcription. Also, gating the greeting on "call active" rather than "audio actually flowing" produces greetings spoken into a not-yet-ready pipe.
   Source: http://dev.to/rokasr/echo-cancellation-warm-up-eats-a-short-first-answer-on-phone-calls-3kad
3. **Residual echo after platform AEC.** A documented iOS fix combined device AEC with deliberately desensitised server VAD: start/end sensitivity LOW, `prefix_padding_ms` raised 20 → **40 ms**, `silence_duration_ms` raised 100 → **500 ms**, specifically so echo tails stop triggering false starts. Note the direction: fixing echo problems meant making endpointing *less* eager.
   Source: https://github.com/asavschaeffer/heard-ios/commit/2597f6540d143f6aa9d247576ea8b61ec3148755

**Takeaway for the block:** even though the voice block's "output" is markdown chunks rather than TTS, the ASYNC-PARALLEL mode inherits the core barge-in lessons — cancel speculative work on resume, flush queued output, and keep the record of what was *actually delivered*, not what was generated. And any future spoken output needs AEC-aware VAD tuning from day one, not as a patch.

### 3. Live-caption segmentation

**Broadcast/subtitle rules are the only mature, published chunking discipline found** — and they are about *display* chunks, much smaller than the voice block's ~500-word markdown chunks. The transferable part is the principles, not the sizes:

- **Line length:** 32–42 characters per line is the recurring broadcast range (legacy decoder limit 32; Netflix-style guides 42 for Latin alphabets; several national guides say 37–42). Max **2 lines** per caption block in most guides (FCC quality rules require captions to be accurate, synchronous, complete, and properly placed, without prescribing line length directly).
  Sources: https://github.com/yigitkonur/subtitle-linter/blob/HEAD/docs/RESEARCH.md · https://internt.slu.se/en/support-services/administrative-support/communication/language-writing/language-tools/subtitling/ · https://docs.fcc.gov/public/attachments/DA-21-469A1.pdf
- **Duration / reading speed:** Netflix-style timing: minimum duration ~**5/6 s**, maximum **7 s** per block. BBC-derived guidance: assume **160–180 words per minute** reading speed, i.e. roughly **0.3 s on screen per word** (a 4-word caption ≈ 1.2 s minimum); typical dwell is ~1.5–2 s for a short line, 3 s for a full line, 5–6 s for two full lines.
  Sources: https://github.com/yigitkonur/subtitle-linter/blob/HEAD/docs/RESEARCH.md · https://discussions.viki.com/t/how-quickly-can-a-viewer-read-subtitles/36040
- **Break at linguistic units:** every guide agrees segmentation should keep phrases intact and break at natural phrase/sentence boundaries rather than at fixed character counts — the direct ancestor of the voice block's "best break point" rule.
- **Inter-cue gaps:** a minimum gap between caption blocks (~0.15 s in EBU-aligned practice; older BBC guidance preferred ≥1 s between subtitles after a speech pause to avoid a jerky effect) — captions are allowed to *lag and breathe*, not required to be gapless.
  Sources: https://github.com/yigitkonur/subtitle-linter/blob/HEAD/docs/RESEARCH.md · https://trello.com/1/cards/58baed9d81307b8d369c1fdb/attachments/58bb12cd97765e26c11e5f83/download/online_sub_editorial_guidelines_vs1_1.pdf

**Web Speech API (the web's de-facto live-caption plumbing).** `SpeechRecognition` offers exactly two segmentation-relevant primitives: `interimResults` (unstable hypotheses, `isFinal=false`, shown live and replaced) and final results (`isFinal=true`, committed), plus `continuous` (keep listening past the first result instead of stopping). There is no word-timing, chunk-size, or pause-threshold control in the API — segmentation policy is entirely the application's problem, which is precisely the gap the voice block fills. A common implementation pattern: display interim text live, commit only final text, auto-restart on `onend` to fake a continuous session.
Source: https://getdocs.org/Web/API/SpeechRecognition

**YouTube live captions** — **no published chunk-size or timing guidance found in this pass** (see §D). Its visible behaviour (rolling lines that revise as more speech arrives) is consistent with the interim/final pattern above, but that is observation, not a sourced claim.

**Takeaway for the block:** captioning proves readers need *time-proportional* text release (0.3 s/word at display scale) and phrase-respecting breaks. Scaled up, it supports the block's shape: a ~500-word chunk at conversational speaking speed (~150 wpm) is ~3+ minutes of speech, so the 60 s cadence rule — not the word cap — will be the binding constraint in fluent speech. Expect most emitted chunks to be time-triggered, with the 3/4-page cap acting as a safety valve for fast/dense speakers.

### 4. Dictation-app chunking

**The dominant pattern is not streaming at all — it is push-to-talk batch.** Wispr Flow and Superwhisper both centre on: hold a key/button → record → release → transcribe the whole take → post-process (formatting, filler removal, light editing) → insert text. The user's hand *is* the endpointing algorithm, which is why these tools feel patient: there is no silence timer to cut you off. Hands-free toggle modes exist alongside (double-tap or a second shortcut), and `Esc` cancels.
Source (secondary research comparing the two products' official behaviour): https://github.com/tj-guruvelli/demod/blob/HEAD/docs/RESEARCH-wispr-superwhisper.md

**The known pain this design answers:** reviewers specifically praise Wispr Flow for never stopping mid-thought during a thinking pause, explicitly contrasting it with Gboard / standard Android voice input, which often does cut the speaker off while pausing to think. That complaint — stock dictation endpointing too eagerly — is the dictation-market version of the EAGER failure mode.
Source: https://www.fastcompany.com/91499738/wispr-flow-dictation-android-gboard-alternatives

**Under the hood, Whisper imposes its own chunking:** the model accepts at most **30 seconds** of audio per window; long-form transcription is a sliding/sequential chunking algorithm over 30 s slices (Hugging Face pipelines expose `chunk_length_s=30`), optionally with word/segment timestamps. Practical tools therefore chunk on *silences* (VAD-gated segments) rather than fixed 30 s cuts where possible — fixed cuts at boundaries can drop or garble words, and overlapping windows (1–5 s overlap in various implementations) are the usual workaround.
Source: https://huggingface.co/openai/whisper-medium

**Streaming variants exist at the edges:** some Whisper-based tools split a long recording into overlapping chunks and run cleanup on finished sentences *while the user is still talking*, so only the last chunk remains to process at release — an early, dictation-flavoured instance of the ASYNC-PARALLEL pattern. True word-by-word streaming generally comes from non-Whisper streaming STT (Deepgram, AssemblyAI, etc.), not from Whisper itself.
Source: https://github.com/desko77/whisper_ptt

**Not found:** official published silence/pause thresholds for Wispr Flow, Superwhisper, MacWhisper, Otter, Apple Dictation, or Google dictation (see §D). Vendors treat endpointing internals as implementation detail; what is public is the interaction model (hold-to-talk vs toggle), not the timers.

**Takeaway for the block:** dictation's lesson is that *explicit* ending (key release) beats *inferred* ending whenever the user is willing to supply it — the PATIENT mode should probably include a manual "emit now / I'm done" signal as a first-class input, inherited from push-to-talk, rather than relying purely on the >5 s gap rule.

### 5. The eager/patient tension in big products

**ChatGPT voice.** The original Advanced Voice Mode was turn-based and widely reported to mistake brief pauses for finished turns. OpenAI shipped an update (March 2025) whose stated purpose was reducing interruptions when users pause to think or breathe — i.e., a deliberate move from EAGER toward PATIENT, marketed as a feature. In July 2026 reporting, its successor (GPT-Live-1) moved to a **full-duplex** model that can listen and speak simultaneously, precisely to escape walkie-talkie turn-taking, and it *delegates* hard questions to a larger text model in the background, using filler acknowledgements to hold the floor while the work happens — a consumer-scale ASYNC-PARALLEL pattern. It also accepts a spoken instruction to simply wait and not reply until addressed again — patience as a user-invokable mode, not just a tuning value.
Sources: https://www.ghacks.net/2025/03/25/openai-updates-chatgpt-voice-mode-for-more-natural-and-engaging-interactions/ · https://finance.biggo.com/news/616bb5c6-18b6-4f05-9eb3-dd2dfffbfa31

**Gemini Live.** Architecturally the most configurable of the big products at the API level: sensitivity knobs, `prefix_padding_ms`, `silence_duration_ms`, interrupt-vs-no-interruption activity handling, and a fully manual activity mode (see §1, §2). The user-facing product exposes far less of this — the knobs live at the developer layer. Known failure shape in third-party integrations is the mirror of ChatGPT's: tuned too sensitively, residual echo triggers false interruptions on speakerphone; the documented fix was to desensitise (see §2).
Sources: https://github.com/dhuynh95/duck_talk/blob/HEAD/docs/gemini-live-api-swift-reference.md · https://github.com/asavschaeffer/heard-ios/commit/2597f6540d143f6aa9d247576ea8b61ec3148755

**The pattern across products:** (1) launch eager, because latency demos well; (2) get complaints about being cut off mid-thought; (3) ship patience as an update; (4) add speculative/background work so patience doesn't feel like slowness. The voice block's three modes are this exact history, turned into configs. Notably, **no big product found exposes an explicit eager/patient dial to end users** — patience is either a hidden tuning change or a spoken instruction. A visible mode switch would be a differentiator, and also an untested UX claim (see §D).

---

## B. Numbers worth stealing

| Parameter | Value | Where it's used | Source |
|---|---|---|---|
| Human turn gap (median) | ~200 ms (0–300 ms across languages) | Conversation research baseline | https://www.scientificamerican.com/article/universal-social-rules-underlie-languages |
| WebRTC VAD frame sizes | 10 / 20 / 30 ms only; modes 0–3 | Classic VAD | https://github.com/kbhatiya999/webrtc-vad-demo |
| Silero VAD chunk / threshold | 32 ms chunks; 0.5 probability default | Neural VAD everywhere | https://github.com/hagarmhassan/wavekat-vad |
| Silero min-silence (Whisper pipelines) | ~500 ms; strip silences >2 s | Dictation/transcription gating | https://github.com/jrufer/voxctrl/blob/HEAD/Resources/Arch%20Linux%20Real-Time%20Transcription%20Tool.md |
| Telephony endpointing floor | ~300 ms reasonable; 500 ms+ audible | Voice-agent rule of thumb | https://github.com/livekit/eot-bench |
| LiveKit endpointing floor/ceiling examples | 0.5 s / 3.0 s; 0.3 s / 5.0 s; 0.4 s / 6.0 s | AgentSession configs | https://github.com/andre-mygentic/context-engineering-livekit/blob/HEAD/PRPs/ai_docs/livekit_patterns.md |
| Deepgram Flux `eot_threshold` | default 0.7 (0.5–1.0) | Semantic EOT confidence | https://developers.deepgram.com/docs/flux/configuration |
| Deepgram Flux `eager_eot_threshold` | 0.3–0.9, off by default | Speculative (eager) EOT | https://developers.deepgram.com/docs/flux/configuration |
| Deepgram Flux `eot_timeout_ms` | default 5,000 ms (500–60,000) | Hard silence backstop | https://developers.deepgram.com/docs/flux/configuration |
| LiveKit Turn Detector v1 delay @ 5% false-cutoff | 543 ms (vs 1,600 ms VAD-only) | eot-bench, English | https://github.com/livekit/eot-bench |
| VAD-only false cutoffs @ 300 ms budget | 55.6% | eot-bench, English | https://github.com/livekit/eot-bench |
| Smart Turn v3 window / size / latency | last 8 s of audio; ~8M params; ~65 ms inference | Pipecat default EOT | https://github.com/godefroy/micdrop/blob/HEAD/website/src/content/blog/end-of-turn-detection-voice-agents/index.mdx |
| Gemini Live `silence_duration_ms` | 100 ms (one documented default summary) → 500 ms tuned | Automatic activity detection | https://github.com/dhuynh95/duck_talk/blob/HEAD/docs/gemini-live-api-swift-reference.md |
| Gemini Live `prefix_padding_ms` | 20 ms default; 40 ms when fighting echo | Start-of-speech commit | https://github.com/asavschaeffer/heard-ios/commit/2597f6540d143f6aa9d247576ea8b61ec3148755 |
| Min interruption duration | ~0.5 s (LiveKit-style); 120–200 ms sustain on AEC-cleaned audio | Barge-in debounce | https://github.com/andre-mygentic/context-engineering-livekit/blob/HEAD/PRPs/ai_docs/livekit_patterns.md |
| TTS flush lag after barge-in | ~200–400 ms of pre-buffered audio | Telephony Pipecat | https://github.com/hhagenbuch/voice-agent/blob/HEAD/docs/notes/02-turn-taking-and-interruptions.md |
| Caption line length | 32–42 chars/line, ≤2 lines | Broadcast/Netflix-style guides | https://github.com/yigitkonur/subtitle-linter/blob/HEAD/docs/RESEARCH.md |
| Caption dwell | ~0.3 s/word (160–180 wpm); block max ~7 s | BBC/Netflix-style timing | https://discussions.viki.com/t/how-quickly-can-a-viewer-read-subtitles/36040 |
| Whisper audio window | 30 s max; long-form = chunked sliding window | All Whisper tooling | https://huggingface.co/openai/whisper-medium |
| OpenAI semantic VAD eagerness caps | 2 / 4 / 8 s waits (**UNVERIFIED**, secondary only) | Realtime API | https://github.com/godefroy/micdrop/blob/HEAD/website/src/content/blog/end-of-turn-detection-voice-agents/index.mdx |

---

## C. Patterns per mode

### EAGER — respond at the first short pause
*Prior art:* telephony voice agents; Deepgram Flux with `eager_eot_threshold` set; OpenAI-style semantic VAD on its lowest eagerness setting (UNVERIFIED detail, pattern is real).
Borrow:
- **Two-threshold design** (Flux): a low-confidence *eager* trigger starts work speculatively; a higher-confidence trigger commits. If the speaker resumes (*TurnResumed*), discard or revise the speculative work. Never let the eager trigger directly emit a chunk — let it *prepare* one.
- **Benchmark the trade-off, don't vibe it** (eot-bench): measure false cutoffs at a fixed latency budget. For the voice block, the EAGER failure metric is "chunks emitted at pauses the speaker didn't mean as breaks."
- **Floor of ~300 ms** of silence before even the eager path may fire; below that you are interrupting breathing, not pauses.
Watch out for: this is the mode every big product launched with and then apologised for (§5). Its real cost is behavioural — speakers learn to perform continuous talking to avoid being cut off, which degrades the transcript itself.

### PATIENT — long window; accumulate through thinking pauses
*Prior art:* push-to-talk dictation (Wispr Flow / Superwhisper); ChatGPT voice's post-March-2025 anti-interruption update; Deepgram Flux with `eot_threshold` → 1.0 (vendor-driven turns only); Gemini Live manual activity mode.
Borrow:
- **Explicit end signal as a first-class input** (dictation's key-release): a button/key/"I'm done" phrase that emits immediately, so patience never has to be *inferred* perfectly.
- **Backstop, not timer:** within PATIENT, the >5 s gap rule should behave like Flux's `eot_timeout_ms` — a guaranteed eventual emit, not the primary segmentation logic. Sentence-boundary + longest-pause selection does the real work.
- **Desensitise when the environment fights you** (the iOS/Gemini echo fix): raising silence duration and lowering sensitivity is a legitimate, documented response to false triggers — PATIENT is the safe fallback mode for noisy/speakerphone setups.
Watch out for: unbounded patience reads as a hung system. Captioning's lesson (text must arrive at a readable cadence) argues for keeping the block's ≥60 s emit rule active even in PATIENT — accumulate *turns* patiently, but still surface chunks on the clock.

### ASYNC-PARALLEL — work while the speaker keeps talking
*Prior art:* Deepgram Flux EagerEndOfTurn → speculative LLM start, cancelled/revised on TurnResumed; GPT-Live-1 delegating hard questions to a background model while holding the floor with acknowledgements; Whisper-PTT-style pipelines running cleanup on finished sentences during ongoing recording; LiveKit/Pipecat preemptive generation.
Borrow:
- **Speculate at chunk boundaries, surface progress live:** when the cadence rule fires, hand the chunk to the agent immediately and show it as *in progress*; the speaker's next chunk is already accumulating. Progress display is part of the pattern in every prior-art instance — silent background work reads as latency.
- **Cancellation semantics from barge-in** (§2): on speaker nudge/interrupt — cancel in-flight generation, flush queued output, and record only what was actually delivered. A nudge mid-stream should be able to redirect the in-flight chunk's work, not just append a new instruction after it.
- **Generation-token discipline:** implementations that survive interruption races tag work with a generation/epoch counter and re-check it after every await, discarding stale results. Cheap to adopt at PoC stage, painful to retrofit.
Watch out for: speculative work multiplies cost and can produce confident output based on a chunk the speaker then revises ("no wait, I meant…"). The Flux pattern's answer — a similarity/commit check between speculative input and final input before surfacing results — is worth borrowing if revision turns out to be common.

---

## D. Open gaps (honest)

1. **MiniMax synthesis: received, but low value — assessment vs verification.**
   - *Right (and verified independently):* WebRTC VAD frame sizes 10/20/30 ms and aggressiveness 0–3; the general shape of the eager/patient trade-off and the standard complaint types (cut off mid-thought; dead air); barge-in failure classes at a generic level (false-positive/negative interruptions); captions breaking at linguistic boundaries.
   - *Wrong or misleading:* Silero VAD described as energy/spectral thresholds on 10–30 ms frames — it is a neural probability model on 32 ms chunks with a ~0.5 probability threshold (§1). LiveKit turn detection reduced to a "~700 ms silence threshold" — it is a learned model with floor/ceiling endpointing delays, benchmarked at 543 ms at a 5% false-cutoff budget (§1). Wispr/Superwhisper-style tools described as streaming with 300–500 ms pause triggers — the verified model is push-to-talk **batch** (§4).
   - *Unverified / apparently invented specifics:* Deepgram endpointing as "500 ms pause + linguistic context" (verified Flux design is confidence thresholds + a 5,000 ms backstop); Azure "~500 ms" and Picovoice "~400–500 ms" silence thresholds (no sources found — items 4 below); YouTube caption chunks of "10–15 words" with "1–2 s delay" (no published guidance found — item 5); Web Speech API interim/final timing of 300–500 ms / 1–2 s (the spec defines no such timings, §3); AEC latency "50–100 ms"; ChatGPT/Gemini eager/patient thresholds of 300–500 ms / 1–2 s and **user-adjustable sensitivity knobs** (no such end-user knobs were found — the Gemini knobs are developer-API level, §5). MiniMax's cited sources were mostly generic homepages/docs roots, not pages supporting the numbers attached to them.
   - Net: MiniMax was useful only as a topic checklist. Every load-bearing number in §§A–B comes from verification, not from the synthesis.
2. **Deepgram classic endpointing / UtteranceEnd: UNVERIFIED.** The verification search for Nova-era `endpointing`, `utterance_end_ms`, and `speech_final` semantics failed at the tool level. Only the newer Flux parameters (§1) are verified here.
3. **OpenAI Realtime API specifics: partially UNVERIFIED.** Semantic-VAD eagerness caps (2/4/8 s) and `server_vad` silence defaults come from secondary summaries only; the official-docs search failed. Verify against OpenAI's Realtime docs before using any number.
4. **Azure Speech endpointing and Picovoice: nothing verified.** No usable sources surfaced for Azure's silence/end-of-segmentation tuning or Picovoice Cobra's parameters in this pass.
5. **YouTube live captions internals: nothing published found.** No chunk-size, revision-window, or latency guidance from Google/YouTube was located — only the generic interim/final model from the Web Speech API.
6. **Dictation vendors' actual timers: unpublished.** No official silence thresholds for Wispr Flow, Superwhisper, MacWhisper, Otter, Apple Dictation, or Gboard were found; the market documents interaction models, not numbers. The "Gboard cuts you off while thinking" claim is reviewer-attested, not measured.
7. **No published chunking guidance at the voice block's scale.** Caption rules top out at ~7 s / ~84 characters per block; dictation tools emit per-recording. Nothing found addresses ~500-word / ~60 s markdown chunking directly — the block's cadence parameters (60 s / 3/4 page / >5 s gap) have **no direct prior-art precedent found** and will need empirical tuning. The nearest anchors are Flux's 5 s silence backstop and captioning's reading-speed math (§3).
8. **No user-facing eager/patient dial found in any big product.** The three-mode config framing appears to be the block's own contribution; there is no prior-art UX evidence for how users understand or misuse such a switch.

---

*Seed only — no decisions taken, nothing pushed. Next useful steps when the PoC starts: verify §D items 2–4 against official docs; instrument false-cutoff rate (eot-bench style) from the first working build; do not re-derive numbers from the MiniMax synthesis — use §B.*

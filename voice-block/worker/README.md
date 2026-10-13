# xero-voiceblock — Cloudflare Worker variant

A voice-transcript segmenter as a Cloudflare Worker, in TypeScript. It
consumes word-level transcript events (`{w, s, e}` — word text, start/end
in seconds) per session and emits readable chunks, implementing exactly
the shared segmentation algorithm (it mirrors the Python reference):

1. **Gap trigger** — if the buffer is non-empty and the incoming word
   starts more than 5.0 s after the last buffered word ended, the buffer
   is emitted as a chunk (`"gap"`) *before* the new word is added.
2. **Size / time triggers** — after adding a word, if the buffer holds
   ≥ 500 words (`"size"`) or spans ≥ 60 s from its first word (`"time"`),
   the buffer is split at the **best break**: every boundary is scored
   `min(pauseAfter, 3.0) + 2.0 if the preceding word ends a sentence`
   (`. ! ?`), highest score wins, ties go to the later boundary. Words up
   to the break are emitted; the remainder stays buffered.
3. **Rendering** — words joined with single spaces; `"\n\n"` replaces the
   space before any word whose preceding pause is ≥ 2.0 s; the first
   letter of the chunk and of any word following a sentence-ending word
   is capitalized (when it starts lowercase a–z).

A chunk is `{text, wordCount, start, end, trigger}` with start/end taken
from the first/last word times.

## Layout

| File | What |
|---|---|
| `src/segmenter.ts` | The pure algorithm (`SessionSegmenter`). No platform dependencies — this is the parity surface with the Python reference. |
| `src/index.ts` | Worker `fetch` handler: the HTTP endpoints below, backed by an in-memory `Map` (PoC state). |
| `src/session-do.ts` | **Stub/sketch only**: the production Durable Object design. Not bound, not exported, does not run. |
| `test/segmenter.test.ts` | Algorithm tests (gap, size, sentence best-break, rendering). |
| `test/worker.test.ts` | HTTP-level tests driving the real `fetch` handler with `Request` objects. |
| `wrangler.toml` | Worker config: name `xero-voiceblock`, **no `account_id`, no bindings**. |

## Endpoints

| Method & path | Body / params | Returns |
|---|---|---|
| `POST /ingest` | `{session: string, events: WordEvent[]}` | `{emitted: Chunk[]}` — chunks emitted while running the events in order |
| `POST /flush` | `{session: string}` | `{chunk: Chunk \| null}` — emits whatever is buffered, trigger `"flush"` |
| `GET /chunks?session=...` | — | `{chunks: Chunk[]}` — everything emitted for that session |
| `GET /health` | — | `{ok: true}` |

Bad JSON, malformed events, or a missing session return `400`; unknown
paths `404`; wrong method on a known path `405`.

## Run locally

Requirements: Node ≥ 22 (developed on Node 24). No build step — the
sources use explicit `.ts` import extensions so Node's native type
stripping runs them directly, and wrangler/esbuild bundles the same
files unchanged.

```sh
npm test            # 8 tests, node:test — no install needed for this alone
npm install         # only needed for the two commands below
npm run typecheck   # tsc --noEmit (strict)
npm run dev         # wrangler dev — serves the worker locally (miniflare)
```

Verified in this environment: `npm test` → 8 pass / 0 fail;
`tsc --noEmit` → clean; `wrangler deploy --dry-run` → bundles
successfully (6.04 KiB, no bindings) without contacting an account.

Manual smoke test once `wrangler dev` is up:

```sh
curl localhost:8787/health
curl -X POST localhost:8787/ingest -H 'content-type: application/json' \
  -d '{"session":"s1","events":[{"w":"hello","s":0,"e":0.4},{"w":"there","s":0.5,"e":0.9},{"w":"again","s":8,"e":8.4}]}'
curl -X POST localhost:8787/flush -H 'content-type: application/json' -d '{"session":"s1"}'
curl 'localhost:8787/chunks?session=s1'
```

## How it would deploy

**Not deployed** — this folder is deploy-ready code only; nobody has run
a real deploy and no Cloudflare account is referenced anywhere in it.

```sh
npx wrangler login        # or set CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN
npm run deploy            # wrangler deploy
```

`wrangler.toml` intentionally omits `account_id`; wrangler resolves the
account from the login/env at deploy time.

## What's stubbed

- **State is in-memory (PoC only).** `src/index.ts` keeps sessions in a
  module-level `Map`. Worker isolates are ephemeral and don't share
  memory: state can vanish on eviction and different requests for the
  same session can land in different isolates. Fine for local testing,
  wrong for production.
- **Production state → Durable Object (sketch in `src/session-do.ts`).**
  One Durable Object per session id (`env.SESSIONS.idFromName(session)`)
  gives a single-threaded, strongly consistent home for the
  `SessionSegmenter`; the object persists `{buffer, chunks}` to
  `state.storage` after each mutation and restores it on wake. To enable:
  export `SessionDurableObject` from `src/index.ts` and uncomment the
  `[[durable_objects.bindings]]` + `[[migrations]]` blocks in
  `wrangler.toml` (both are written out in `session-do.ts`'s header).
  The sketch does not run today — it is design documentation in code.
- **No auth, no rate limiting, no persistence of emitted chunks** beyond
  the session object's lifetime, and sessions are never expired. All of
  that is production-hardening on top of the PoC, deliberately out of
  scope here.
- `test/` is not covered by `npm run typecheck` (tsconfig includes only
  `src/`, to keep Workers types and Node test types from colliding);
  the tests are still type-stripped and executed by Node on every run.

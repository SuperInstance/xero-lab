// session-do.ts — PRODUCTION SKETCH ONLY. Not bound in wrangler.toml and
// not exported from index.ts in this PoC; nothing here runs yet.
//
// In production, per-session segmenter state belongs in a Durable Object
// keyed by session id: one object per session gives strong consistency,
// a single-threaded execution context (no cross-isolate Map divergence),
// and state that survives isolate eviction. The Worker fetch handler
// would then do:
//
//   const id = env.SESSIONS.idFromName(session);
//   const stub = env.SESSIONS.get(id);
//   return stub.fetch(request);            // same JSON shapes as index.ts
//
// wrangler.toml additions when enabling this:
//
//   [[durable_objects.bindings]]
//   name = "SESSIONS"
//   class_name = "SessionDurableObject"
//
//   [[migrations]]
//   tag = "v1"
//   new_sqlite_classes = ["SessionDurableObject"]
//
// and in index.ts:
//   export { SessionDurableObject } from "./session-do.ts";

import {
  SessionSegmenter,
  type Chunk,
  type WordEvent,
} from "./segmenter.ts";

// Structural stand-in for the real DurableObjectState from
// @cloudflare/workers-types, so this sketch type-checks in spirit without
// the PoC depending on the types package at runtime.
interface DurableObjectStorageLike {
  get<T>(key: string): Promise<T | undefined>;
  put(key: string, value: unknown): Promise<void>;
}
interface DurableObjectStateLike {
  storage: DurableObjectStorageLike;
}

export class SessionDurableObject {
  state: DurableObjectStateLike;
  seg: SessionSegmenter | null = null;

  constructor(state: DurableObjectStateLike) {
    this.state = state;
  }

  // Lazily restore the segmenter (buffer + emitted chunks) from storage.
  // The segmenter is plain JSON-shaped data, so it round-trips directly.
  async load(): Promise<SessionSegmenter> {
    if (this.seg) return this.seg;
    const saved = await this.state.storage.get<{
      buffer: WordEvent[];
      chunks: Chunk[];
    }>("segmenter");
    const seg = new SessionSegmenter();
    if (saved) {
      seg.buffer = saved.buffer;
      seg.chunks = saved.chunks;
    }
    this.seg = seg;
    return seg;
  }

  async persist(): Promise<void> {
    if (!this.seg) return;
    await this.state.storage.put("segmenter", {
      buffer: this.seg.buffer,
      chunks: this.seg.chunks,
    });
  }

  // Same request/response shapes as the PoC handler in index.ts:
  // POST {events} -> {emitted}, POST /flush-equivalent -> {chunk},
  // GET -> {chunks}. (Routing shape is illustrative.)
  async fetch(request: Request): Promise<Response> {
    const seg = await this.load();
    const url = new URL(request.url);
    const reply = (data: unknown) =>
      new Response(JSON.stringify(data), {
        headers: { "content-type": "application/json" },
      });

    if (request.method === "POST" && url.pathname.endsWith("/flush")) {
      const chunk = seg.flush();
      await this.persist();
      return reply({ chunk });
    }
    if (request.method === "POST") {
      const body = (await request.json()) as { events: WordEvent[] };
      const emitted = seg.ingestAll(body.events);
      await this.persist();
      return reply({ emitted });
    }
    return reply({ chunks: seg.chunks });
  }
}

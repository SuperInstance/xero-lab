// index.ts — Cloudflare Worker entry point for xero-voiceblock.
//
// Thin HTTP shell around the pure segmenter in ./segmenter.ts.
//
// STATE (PoC): sessions live in an in-memory Map in this module. That is
// fine for a proof of concept and for local testing, but it is NOT safe
// for production: a Worker isolate can be evicted or recycled at any
// time, multiple isolates do not share the Map, and nothing survives a
// restart. Production state belongs in a Durable Object keyed by session
// id — see ./session-do.ts for the sketch and README.md ("Production
// state") for the binding changes needed.
//
// NOTE: imports use explicit ".ts" extensions so the same sources run
// unmodified under Node >= 22 type stripping (the local test path) as
// well as under wrangler/esbuild bundling.

import {
  SessionSegmenter,
  type Chunk,
  type WordEvent,
} from "./segmenter.ts";

// To promote the Durable Object sketch to production, export it here:
//   export { SessionDurableObject } from "./session-do.ts";
// …and add the binding + migration shown in session-do.ts / README.md.

// ---------------------------------------------------------------------------
// In-memory session store (PoC only — see header comment)
// ---------------------------------------------------------------------------

const sessions = new Map<string, SessionSegmenter>();

function getSession(id: string): SessionSegmenter {
  let seg = sessions.get(id);
  if (!seg) {
    seg = new SessionSegmenter();
    sessions.set(id, seg);
  }
  return seg;
}

// ---------------------------------------------------------------------------
// HTTP helpers
// ---------------------------------------------------------------------------

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function isWordEvent(v: unknown): v is WordEvent {
  if (typeof v !== "object" || v === null) return false;
  const o = v as Record<string, unknown>;
  return (
    typeof o.w === "string" &&
    typeof o.s === "number" &&
    Number.isFinite(o.s) &&
    typeof o.e === "number" &&
    Number.isFinite(o.e)
  );
}

// Minimal structural type for the bits of Env we might grow into; the PoC
// itself needs no bindings at all.
interface Env {}

export default {
  async fetch(request: Request, _env: Env): Promise<Response> {
    const url = new URL(request.url);

    // GET /health -> { ok: true }
    if (url.pathname === "/health") {
      if (request.method !== "GET") return json({ error: "method not allowed" }, 405);
      return json({ ok: true });
    }

    // POST /ingest  { session, events: WordEvent[] } -> { emitted: Chunk[] }
    if (url.pathname === "/ingest") {
      if (request.method !== "POST") return json({ error: "method not allowed" }, 405);
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid JSON body" }, 400);
      }
      const b = body as { session?: unknown; events?: unknown };
      if (typeof b.session !== "string" || b.session.length === 0) {
        return json({ error: "body.session must be a non-empty string" }, 400);
      }
      if (!Array.isArray(b.events) || !b.events.every(isWordEvent)) {
        return json(
          { error: "body.events must be an array of {w: string, s: number, e: number}" },
          400,
        );
      }
      const seg = getSession(b.session);
      const emitted: Chunk[] = seg.ingestAll(b.events);
      return json({ emitted });
    }

    // POST /flush  { session } -> { chunk: Chunk | null }
    if (url.pathname === "/flush") {
      if (request.method !== "POST") return json({ error: "method not allowed" }, 405);
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid JSON body" }, 400);
      }
      const b = body as { session?: unknown };
      if (typeof b.session !== "string" || b.session.length === 0) {
        return json({ error: "body.session must be a non-empty string" }, 400);
      }
      const chunk = getSession(b.session).flush();
      return json({ chunk });
    }

    // GET /chunks?session=... -> { chunks: Chunk[] }
    if (url.pathname === "/chunks") {
      if (request.method !== "GET") return json({ error: "method not allowed" }, 405);
      const session = url.searchParams.get("session");
      if (!session) {
        return json({ error: "missing ?session= query parameter" }, 400);
      }
      return json({ chunks: getSession(session).chunks });
    }

    return json({ error: "not found" }, 404);
  },
};

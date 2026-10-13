// worker.test.ts — HTTP-level tests: drives the real fetch handler from
// src/index.ts with Request objects (no server, no network).

import { test } from "node:test";
import assert from "node:assert/strict";

import worker from "../src/index.ts";

function req(path: string, init?: RequestInit): Request {
  return new Request(`http://local.test${path}`, init);
}

function post(path: string, body: unknown): Request {
  return req(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

test("GET /health returns { ok: true }", async () => {
  const res = await worker.fetch(req("/health"), {});
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
});

test("ingest -> chunks -> flush round trip over HTTP", async () => {
  const session = "http-round-trip";
  const ingestRes = await worker.fetch(
    post("/ingest", {
      session,
      events: [
        { w: "alpha", s: 0.0, e: 0.4 },
        { w: "beta", s: 0.5, e: 0.9 },
        { w: "gamma", s: 8.0, e: 8.4 }, // 7.1s gap after beta -> gap chunk
      ],
    }),
    {},
  );
  assert.equal(ingestRes.status, 200);
  const ingestBody = (await ingestRes.json()) as {
    emitted: Array<{ trigger: string; text: string; wordCount: number }>;
  };
  assert.equal(ingestBody.emitted.length, 1);
  assert.equal(ingestBody.emitted[0].trigger, "gap");
  assert.equal(ingestBody.emitted[0].text, "Alpha beta");
  assert.equal(ingestBody.emitted[0].wordCount, 2);

  const chunksRes = await worker.fetch(req(`/chunks?session=${session}`), {});
  assert.equal(chunksRes.status, 200);
  const chunksBody = (await chunksRes.json()) as { chunks: unknown[] };
  assert.equal(chunksBody.chunks.length, 1);

  const flushRes = await worker.fetch(post("/flush", { session }), {});
  assert.equal(flushRes.status, 200);
  const flushBody = (await flushRes.json()) as {
    chunk: { trigger: string; text: string } | null;
  };
  assert.ok(flushBody.chunk);
  assert.equal(flushBody.chunk.trigger, "flush");
  assert.equal(flushBody.chunk.text, "Gamma");

  const afterRes = await worker.fetch(req(`/chunks?session=${session}`), {});
  const afterBody = (await afterRes.json()) as { chunks: unknown[] };
  assert.equal(afterBody.chunks.length, 2);

  // Flushing an empty buffer yields chunk: null.
  const againRes = await worker.fetch(post("/flush", { session }), {});
  const againBody = (await againRes.json()) as { chunk: unknown };
  assert.equal(againBody.chunk, null);
});

test("validation and routing errors", async () => {
  const badEvents = await worker.fetch(
    post("/ingest", { session: "x", events: [{ w: 1, s: 0, e: 1 }] }),
    {},
  );
  assert.equal(badEvents.status, 400);

  const badJson = await worker.fetch(
    req("/ingest", { method: "POST", body: "{not json" }),
    {},
  );
  assert.equal(badJson.status, 400);

  const noSession = await worker.fetch(req("/chunks"), {});
  assert.equal(noSession.status, 400);

  const unknown = await worker.fetch(req("/nope"), {});
  assert.equal(unknown.status, 404);

  const wrongMethod = await worker.fetch(req("/ingest"), {});
  assert.equal(wrongMethod.status, 405);
});

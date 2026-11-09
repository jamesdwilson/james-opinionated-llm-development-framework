import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { resolve } from 'node:path';
import { createTaskServer } from '../src/server.mjs';

async function startServer({ beforeMutationBodyRead } = {}) {
  const directory = await mkdtemp(join(resolve('.tmp'), 'methodology-api-'));
  const times = [
    '2026-11-07T20:00:00.000Z',
    '2026-11-07T20:05:00.000Z',
    '2026-11-07T20:06:00.000Z',
    '2026-11-07T20:07:00.000Z',
    '2026-11-07T20:08:00.000Z',
  ];
  const server = createTaskServer({
    databasePath: join(directory, 'tasks.sqlite'),
    clock: () => times.shift() ?? '2026-11-07T20:59:00.000Z',
    idFactory: () => 'task-api-1',
    beforeMutationBodyRead,
  });
  const address = await server.listen(0);
  return { server, directory, baseUrl: `http://127.0.0.1:${address.port}` };
}

async function jsonRequest(baseUrl, path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      ...(options.headers || {}),
    },
  });
  const body = await response.json();
  return { response, body };
}

async function heldJsonRequest(baseUrl, path, body) {
  const target = new URL(path, baseUrl);
  let release;
  let resolveReady;
  let rejectReady;
  const ready = new Promise((resolve, reject) => {
    resolveReady = resolve;
    rejectReady = reject;
  });
  let resolveResponse;
  let rejectResponse;
  const response = new Promise((resolve, reject) => {
    resolveResponse = resolve;
    rejectResponse = reject;
  });
  const request = http.request(target, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'transfer-encoding': 'chunked',
    },
  }, incoming => {
    const chunks = [];
    incoming.on('data', chunk => chunks.push(chunk));
    incoming.on('end', () => resolveResponse({
      status: incoming.statusCode,
      body: JSON.parse(Buffer.concat(chunks).toString('utf8')),
    }));
  });
  request.on('error', error => {
    rejectReady(error);
    rejectResponse(error);
  });
  request.on('socket', socket => {
    const start = () => {
      request.flushHeaders();
      release = () => request.end(JSON.stringify(body));
      resolveReady();
    };
    if (socket.connecting) socket.once('connect', start);
    else start();
  });
  await ready;
  return { release, response };
}

function mutationBodyBarrier(expectedArrivals) {
  let armed = false;
  let arrivals = 0;
  let resolveArrived;
  let release;
  const arrived = new Promise(resolve => { resolveArrived = resolve; });
  const released = new Promise(resolve => { release = resolve; });
  return {
    arm() { armed = true; },
    async beforeMutationBodyRead() {
      if (!armed) return;
      arrivals += 1;
      if (arrivals === expectedArrivals) resolveArrived();
      await released;
    },
    async waitForAll() {
      await Promise.race([
        arrived,
        new Promise((_, reject) => setTimeout(
          () => reject(new Error('Server did not reach the mutation body-read barrier.')),
          500,
        )),
      ]);
    },
    release,
  };
}

test('J01–J03 API contract enforces independent approval, idempotency and provenance', async (t) => {
  const { server, directory, baseUrl } = await startServer();
  t.after(async () => { await server.close(); await rm(directory, { recursive: true, force: true }); });

  const created = await jsonRequest(baseUrl, '/api/tasks', {
    method: 'POST',
    body: JSON.stringify({
      title: 'Wash dishes',
      creator: 'Alex',
      policy: 'approval',
    }),
  });
  assert.equal(created.response.status, 201);
  assert.equal(created.body.task.status, 'open');

  const requested = await jsonRequest(baseUrl, '/api/tasks/task-api-1/complete', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Alex' }),
  });
  assert.equal(requested.response.status, 200);
  assert.equal(requested.body.task.status, 'awaiting_approval');

  const selfApproval = await jsonRequest(baseUrl, '/api/tasks/task-api-1/approve', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Alex' }),
  });
  assert.equal(selfApproval.response.status, 403);
  assert.deepEqual(selfApproval.body.error, {
    code: 'independent_approval_required',
    message: 'Another household member must approve this completion.',
  });

  const approved = await jsonRequest(baseUrl, '/api/tasks/task-api-1/approve', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Sam' }),
  });
  assert.equal(approved.response.status, 200);
  assert.equal(approved.body.task.status, 'complete');
  assert.equal(approved.body.task.approvedBy, 'Sam');
  assert.equal(approved.body.idempotent, false);

  const repeated = await jsonRequest(baseUrl, '/api/tasks/task-api-1/approve', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Sam' }),
  });
  assert.equal(repeated.response.status, 200);
  assert.equal(repeated.body.idempotent, true);

  const events = await jsonRequest(baseUrl, '/api/tasks/task-api-1/events');
  assert.equal(events.response.status, 200);
  assert.deepEqual(events.body.events.map((event) => [event.type, event.actor]), [
    ['task.created', 'Alex'],
    ['task.completion_requested', 'Alex'],
    ['task.approved', 'Sam'],
  ]);

  const listed = await jsonRequest(baseUrl, '/api/tasks');
  assert.equal(listed.response.status, 200);
  assert.equal(listed.body.tasks.length, 1);
  assert.equal(listed.body.tasks[0].id, 'task-api-1');
});

test('J04 API rejects invalid input without creating a task', async (t) => {
  const { server, directory, baseUrl } = await startServer();
  t.after(async () => { await server.close(); await rm(directory, { recursive: true, force: true }); });

  const invalid = await jsonRequest(baseUrl, '/api/tasks', {
    method: 'POST',
    body: JSON.stringify({ title: '   ', creator: 'Alex', policy: 'approval' }),
  });
  assert.equal(invalid.response.status, 400);
  assert.equal(invalid.body.error.code, 'invalid_task');
  assert.match(invalid.body.error.message, /title is required/i);

  const listed = await jsonRequest(baseUrl, '/api/tasks');
  assert.deepEqual(listed.body.tasks, []);
});

test('API returns a stable not-found contract for unknown task IDs', async (t) => {
  const { server, directory, baseUrl } = await startServer();
  t.after(async () => { await server.close(); await rm(directory, { recursive: true, force: true }); });

  const missing = await jsonRequest(baseUrl, '/api/tasks/missing/complete', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Alex' }),
  });
  assert.equal(missing.response.status, 404);
  assert.deepEqual(missing.body.error, {
    code: 'task_not_found',
    message: 'Task not found.',
  });
});

test('overlapping approvals create one event and make the second request idempotent', async (t) => {
  const barrier = mutationBodyBarrier(2);
  const { server, directory, baseUrl } = await startServer({
    beforeMutationBodyRead: barrier.beforeMutationBodyRead,
  });
  t.after(async () => { await server.close(); await rm(directory, { recursive: true, force: true }); });

  await jsonRequest(baseUrl, '/api/tasks', {
    method: 'POST',
    body: JSON.stringify({ title: 'Wash dishes', creator: 'Alex', policy: 'approval' }),
  });
  await jsonRequest(baseUrl, '/api/tasks/task-api-1/complete', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Alex' }),
  });

  barrier.arm();
  const first = await heldJsonRequest(baseUrl, '/api/tasks/task-api-1/approve', { actor: 'Sam' });
  const second = await heldJsonRequest(baseUrl, '/api/tasks/task-api-1/approve', { actor: 'Sam' });
  await barrier.waitForAll();
  barrier.release();
  first.release();
  second.release();
  const responses = await Promise.all([first.response, second.response]);

  assert.deepEqual(responses.map(result => result.status), [200, 200]);
  assert.deepEqual(responses.map(result => result.body.idempotent).sort(), [false, true]);
  const events = await jsonRequest(baseUrl, '/api/tasks/task-api-1/events');
  assert.deepEqual(events.body.events.map(event => event.type), [
    'task.created',
    'task.completion_requested',
    'task.approved',
  ]);
});

test('a delayed stale completion cannot overwrite a later approved state', async (t) => {
  const barrier = mutationBodyBarrier(1);
  const { server, directory, baseUrl } = await startServer({
    beforeMutationBodyRead: barrier.beforeMutationBodyRead,
  });
  t.after(async () => { await server.close(); await rm(directory, { recursive: true, force: true }); });

  await jsonRequest(baseUrl, '/api/tasks', {
    method: 'POST',
    body: JSON.stringify({ title: 'Wash dishes', creator: 'Alex', policy: 'approval' }),
  });
  barrier.arm();
  const delayed = await heldJsonRequest(baseUrl, '/api/tasks/task-api-1/complete', { actor: 'Alex' });
  await barrier.waitForAll();
  barrier.release();
  await jsonRequest(baseUrl, '/api/tasks/task-api-1/complete', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Sam' }),
  });
  const requesterSelfApproval = await jsonRequest(baseUrl, '/api/tasks/task-api-1/approve', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Sam' }),
  });
  assert.equal(requesterSelfApproval.response.status, 403);
  await jsonRequest(baseUrl, '/api/tasks/task-api-1/approve', {
    method: 'POST',
    body: JSON.stringify({ actor: 'Alex' }),
  });
  delayed.release();
  const delayedResponse = await delayed.response;

  assert.equal(delayedResponse.status, 409);
  const listed = await jsonRequest(baseUrl, '/api/tasks');
  assert.equal(listed.body.tasks[0].status, 'complete');
  assert.equal(listed.body.tasks[0].approvedBy, 'Alex');
  const events = await jsonRequest(baseUrl, '/api/tasks/task-api-1/events');
  assert.deepEqual(events.body.events.map(event => event.type), [
    'task.created',
    'task.completion_requested',
    'task.approved',
  ]);
});

import http from 'node:http';
import { parseDsn } from '../public/monitoring.js';
import { readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { approveTask, createTask, requestCompletion } from './domain.mjs';
import { openTaskRepository } from './repository.mjs';

function sendJson(response, status, body) {
  const payload = JSON.stringify(body);
  response.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
  });
  response.end(payload);
}

async function readJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 64 * 1024) {
      throw new Error('Request body is too large.');
    }
    chunks.push(chunk);
  }
  if (chunks.length === 0) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw new Error('Request body must be valid JSON.');
  }
}

function taskNotFound(response) {
  sendJson(response, 404, {
    error: { code: 'task_not_found', message: 'Task not found.' },
  });
}

function sendDomainError(response, error, action) {
  const message = error instanceof Error ? error.message : 'Invalid request.';
  if (message === 'Another household member must approve this completion.') {
    sendJson(response, 403, {
      error: { code: 'independent_approval_required', message },
    });
    return;
  }
  sendJson(response, action === 'create' ? 400 : 409, {
    error: {
      code: action === 'create' ? 'invalid_task' : 'invalid_transition',
      message,
    },
  });
}

export function createTaskServer({
  databasePath,
  monitoring = {},
  clock = () => new Date().toISOString(),
  idFactory = () => randomUUID(),
  beforeMutationBodyRead = async () => {},
}) {
  parseDsn(monitoring.dsn);
  const browserConfig = { dsn: monitoring.dsn || '', release: monitoring.release, environment: monitoring.environment, canary: monitoring.canary, testCanary: monitoring.testCanary === true };
  const repository = openTaskRepository(databasePath);
  const server = http.createServer(async (request, response) => {
    const url = new URL(request.url || '/', 'http://127.0.0.1');

    try {
      if (request.method === 'GET' && url.pathname === '/monitoring-config') { sendJson(response, 200, browserConfig); return; }
      const assets = { '/': ['index.html', 'text/html'], '/ambiguous': ['index.html', 'text/html'], '/boot.js': ['boot.js', 'text/javascript'], '/monitoring.js': ['monitoring.js', 'text/javascript'], '/app.js': ['app.js', 'text/javascript'], '/style.css': ['style.css', 'text/css'] };
      if (request.method === 'GET' && Object.hasOwn(assets, url.pathname)) {
        const [file, type] = assets[url.pathname];
        const payload = await readFile(new URL('../public/' + file, import.meta.url));
        response.writeHead(200, { 'content-type': type + '; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' });
        response.end(payload); return;
      }
      if (request.method === 'GET' && url.pathname === '/api/tasks') {
        sendJson(response, 200, { tasks: repository.listTasks() });
        return;
      }

      if (request.method === 'POST' && url.pathname === '/api/tasks') {
        const body = await readJson(request);
        try {
          const result = createTask({
            id: idFactory(),
            title: body.title,
            creator: body.creator,
            policy: body.policy,
            now: clock(),
          });
          repository.save(result.task, result.event);
          sendJson(response, 201, { task: result.task });
        } catch (error) {
          sendDomainError(response, error, 'create');
        }
        return;
      }

      const eventsMatch = url.pathname.match(/^\/api\/tasks\/([^/]+)\/events$/);
      if (request.method === 'GET' && eventsMatch) {
        const taskId = decodeURIComponent(eventsMatch[1]);
        if (!repository.getTask(taskId)) {
          taskNotFound(response);
          return;
        }
        sendJson(response, 200, { events: repository.listEvents(taskId) });
        return;
      }

      const actionMatch = url.pathname.match(/^\/api\/tasks\/([^/]+)\/(complete|approve)$/);
      if (request.method === 'POST' && actionMatch) {
        const taskId = decodeURIComponent(actionMatch[1]);
        const action = actionMatch[2];
        if (!repository.getTask(taskId)) {
          taskNotFound(response);
          return;
        }
        await beforeMutationBodyRead({ taskId, action });
        const body = await readJson(request);
        const task = repository.getTask(taskId);
        if (!task) {
          taskNotFound(response);
          return;
        }
        try {
          const result = action === 'complete'
            ? requestCompletion({ task, actor: body.actor, now: clock() })
            : approveTask({ task, actor: body.actor, now: clock() });
          repository.save(result.task, result.event);
          sendJson(response, 200, {
            task: result.task,
            idempotent: result.idempotent ?? false,
          });
        } catch (error) {
          sendDomainError(response, error, action);
        }
        return;
      }

      sendJson(response, 404, {
        error: { code: 'route_not_found', message: 'Route not found.' },
      });
    } catch (error) {
      sendJson(response, 400, {
        error: {
          code: 'invalid_request',
          message: error instanceof Error ? error.message : 'Invalid request.',
        },
      });
    }
  });

  return {
    listen(port = 0) {
      return new Promise((resolve, reject) => {
        server.once('error', reject);
        server.listen(port, '127.0.0.1', () => {
          server.removeListener('error', reject);
          resolve(server.address());
        });
      });
    },

    close() {
      return new Promise((resolve, reject) => {
        server.close((error) => {
          repository.close();
          if (error) reject(error);
          else resolve();
        });
        server.closeAllConnections();
      });
    },
  };
}

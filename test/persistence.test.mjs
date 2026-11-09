import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { resolve } from 'node:path';
import { approveTask, createTask, requestCompletion } from '../src/domain.mjs';
import { openTaskRepository } from '../src/repository.mjs';

const at = (minute) => `2026-11-07T19:${String(minute).padStart(2, '0')}:00.000Z`;

test('J03 SQLite persistence survives reopen with ordered truthful provenance', async (t) => {
  const directory = await mkdtemp(join(resolve('.tmp'), 'methodology-lab-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const databasePath = join(directory, 'tasks.sqlite');

  const created = createTask({
    id: 'persisted-task',
    title: 'Wash dishes',
    creator: 'Alex',
    policy: 'approval',
    now: at(0),
  });

  let repository = openTaskRepository(databasePath);
  repository.save(created.task, created.event);

  const requested = requestCompletion({ task: created.task, actor: 'Alex', now: at(5) });
  repository.save(requested.task, requested.event);

  const approved = approveTask({ task: requested.task, actor: 'Sam', now: at(7) });
  repository.save(approved.task, approved.event);
  repository.close();

  repository = openTaskRepository(databasePath);
  assert.deepEqual(repository.getTask('persisted-task'), approved.task);
  assert.deepEqual(
    repository.listEvents('persisted-task').map(({ type, actor, occurredAt, details }) => ({
      type,
      actor,
      occurredAt,
      details,
    })),
    [
      {
        type: 'task.created',
        actor: 'Alex',
        occurredAt: at(0),
        details: { policy: 'approval', title: 'Wash dishes' },
      },
      {
        type: 'task.completion_requested',
        actor: 'Alex',
        occurredAt: at(5),
        details: {},
      },
      {
        type: 'task.approved',
        actor: 'Sam',
        occurredAt: at(7),
        details: { completedBy: 'Alex' },
      },
    ],
  );
  repository.close();
});

test('repository save with no event updates state without inventing provenance', async (t) => {
  const directory = await mkdtemp(join(resolve('.tmp'), 'methodology-lab-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const databasePath = join(directory, 'tasks.sqlite');
  const repository = openTaskRepository(databasePath);
  const created = createTask({
    id: 'idempotent-task',
    title: 'Wash dishes',
    creator: 'Alex',
    policy: 'approval',
    now: at(0),
  });
  repository.save(created.task, created.event);
  const requested = requestCompletion({ task: created.task, actor: 'Alex', now: at(5) });
  repository.save(requested.task, requested.event);
  const approved = approveTask({ task: requested.task, actor: 'Sam', now: at(7) });
  repository.save(approved.task, approved.event);
  const repeated = approveTask({ task: approved.task, actor: 'Sam', now: at(8) });
  repository.save(repeated.task, repeated.event);

  assert.equal(repository.listEvents('idempotent-task').length, 3);
  repository.close();
});

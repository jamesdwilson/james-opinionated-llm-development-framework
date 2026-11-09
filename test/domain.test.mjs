import test from 'node:test';
import assert from 'node:assert/strict';
import {
  approveTask,
  createTask,
  requestCompletion,
} from '../src/domain.mjs';

const at = (minute) => `2026-11-07T18:${String(minute).padStart(2, '0')}:00.000Z`;

function makeApprovalTask() {
  return createTask({
    id: 'task-1',
    title: '  Wash dishes  ',
    creator: 'Alex',
    policy: 'approval',
    now: at(0),
  });
}

test('J01 creates an approval task with normalized title and provenance', () => {
  const result = makeApprovalTask();

  assert.equal(result.task.title, 'Wash dishes');
  assert.equal(result.task.creator, 'Alex');
  assert.equal(result.task.policy, 'approval');
  assert.equal(result.task.status, 'open');
  assert.deepEqual(result.event, {
    type: 'task.created',
    taskId: 'task-1',
    actor: 'Alex',
    occurredAt: at(0),
    details: { policy: 'approval', title: 'Wash dishes' },
  });
});

test('J04 rejects blank titles and unknown actors at the domain boundary', () => {
  assert.throws(
    () => createTask({ id: 'blank', title: '   ', creator: 'Alex', policy: 'approval', now: at(0) }),
    /title is required/i,
  );
  assert.throws(
    () => createTask({ id: 'actor', title: 'Wash dishes', creator: 'Pat', policy: 'approval', now: at(0) }),
    /actor must be Alex or Sam/i,
  );
});

test('J02 approval policy requires a second actor and records exact transitions', () => {
  const created = makeApprovalTask();
  const requested = requestCompletion({ task: created.task, actor: 'Alex', now: at(5) });

  assert.equal(requested.task.status, 'awaiting_approval');
  assert.equal(requested.task.completedBy, 'Alex');
  assert.equal(requested.event.type, 'task.completion_requested');

  assert.throws(
    () => approveTask({ task: requested.task, actor: 'Alex', now: at(6) }),
    /another household member must approve/i,
  );

  const approved = approveTask({ task: requested.task, actor: 'Sam', now: at(7) });
  assert.equal(approved.task.status, 'complete');
  assert.equal(approved.task.approvedBy, 'Sam');
  assert.deepEqual(approved.event, {
    type: 'task.approved',
    taskId: 'task-1',
    actor: 'Sam',
    occurredAt: at(7),
    details: { completedBy: 'Alex' },
  });
});

test('J02 repeated approval is idempotent and emits no duplicate event', () => {
  const created = makeApprovalTask();
  const requested = requestCompletion({ task: created.task, actor: 'Alex', now: at(5) });
  const approved = approveTask({ task: requested.task, actor: 'Sam', now: at(7) });
  const repeated = approveTask({ task: approved.task, actor: 'Sam', now: at(8) });

  assert.equal(repeated.task, approved.task);
  assert.equal(repeated.event, null);
  assert.equal(repeated.idempotent, true);
});

test('direct-completion policy completes without an approval state', () => {
  const created = createTask({
    id: 'task-2',
    title: 'Take bins out',
    creator: 'Sam',
    policy: 'direct',
    now: at(0),
  });
  const completed = requestCompletion({ task: created.task, actor: 'Sam', now: at(5) });

  assert.equal(completed.task.status, 'complete');
  assert.equal(completed.task.approvedBy, null);
  assert.equal(completed.event.type, 'task.completed');
});

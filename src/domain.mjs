const ACTORS = new Set(['Alex', 'Sam']);
const POLICIES = new Set(['direct', 'approval']);

function requireActor(actor) {
  if (!ACTORS.has(actor)) {
    throw new Error('Actor must be Alex or Sam.');
  }
}

function normalizeTitle(title) {
  const normalized = typeof title === 'string' ? title.trim() : '';
  if (!normalized) {
    throw new Error('Task title is required.');
  }
  if (normalized.length > 80) {
    throw new Error('Task title must be 80 characters or fewer.');
  }
  return normalized;
}

function requirePolicy(policy) {
  if (!POLICIES.has(policy)) {
    throw new Error('Task policy must be direct or approval.');
  }
}

function event(type, taskId, actor, occurredAt, details = {}) {
  return { type, taskId, actor, occurredAt, details };
}

export function createTask({ id, title, creator, policy, now }) {
  requireActor(creator);
  requirePolicy(policy);
  const normalizedTitle = normalizeTitle(title);
  const task = {
    id,
    title: normalizedTitle,
    creator,
    policy,
    status: 'open',
    completedBy: null,
    approvedBy: null,
    createdAt: now,
    completedAt: null,
    approvedAt: null,
  };

  return {
    task,
    event: event('task.created', id, creator, now, {
      policy,
      title: normalizedTitle,
    }),
  };
}

export function requestCompletion({ task, actor, now }) {
  requireActor(actor);
  if (task.status !== 'open') {
    throw new Error('Only an open task can be marked complete.');
  }

  if (task.policy === 'direct') {
    return {
      task: {
        ...task,
        status: 'complete',
        completedBy: actor,
        completedAt: now,
      },
      event: event('task.completed', task.id, actor, now),
    };
  }

  return {
    task: {
      ...task,
      status: 'awaiting_approval',
      completedBy: actor,
      completedAt: now,
    },
    event: event('task.completion_requested', task.id, actor, now),
  };
}

export function approveTask({ task, actor, now }) {
  requireActor(actor);

  if (task.status === 'complete' && task.policy === 'approval' && task.approvedBy === actor) {
    return { task, event: null, idempotent: true };
  }
  if (task.status !== 'awaiting_approval') {
    throw new Error('Only a task waiting for approval can be approved.');
  }
  if (task.completedBy === actor) {
    throw new Error('Another household member must approve this completion.');
  }

  return {
    task: {
      ...task,
      status: 'complete',
      approvedBy: actor,
      approvedAt: now,
    },
    event: event('task.approved', task.id, actor, now, {
      completedBy: task.completedBy,
    }),
    idempotent: false,
  };
}

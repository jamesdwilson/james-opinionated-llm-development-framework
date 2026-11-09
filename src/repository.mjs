import { DatabaseSync } from 'node:sqlite';

function rowToTask(row) {
  if (!row) return null;
  return {
    id: row.id,
    title: row.title,
    creator: row.creator,
    policy: row.policy,
    status: row.status,
    completedBy: row.completed_by,
    approvedBy: row.approved_by,
    createdAt: row.created_at,
    completedAt: row.completed_at,
    approvedAt: row.approved_at,
  };
}

export function openTaskRepository(databasePath) {
  const database = new DatabaseSync(databasePath);
  database.exec(`
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      creator TEXT NOT NULL,
      policy TEXT NOT NULL,
      status TEXT NOT NULL,
      completed_by TEXT,
      approved_by TEXT,
      created_at TEXT NOT NULL,
      completed_at TEXT,
      approved_at TEXT
    );
    CREATE TABLE IF NOT EXISTS task_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      task_id TEXT NOT NULL REFERENCES tasks(id),
      type TEXT NOT NULL,
      actor TEXT NOT NULL,
      occurred_at TEXT NOT NULL,
      details_json TEXT NOT NULL
    );
  `);

  const upsertTask = database.prepare(`
    INSERT INTO tasks (
      id, title, creator, policy, status, completed_by, approved_by,
      created_at, completed_at, approved_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      title = excluded.title,
      creator = excluded.creator,
      policy = excluded.policy,
      status = excluded.status,
      completed_by = excluded.completed_by,
      approved_by = excluded.approved_by,
      created_at = excluded.created_at,
      completed_at = excluded.completed_at,
      approved_at = excluded.approved_at
  `);
  const insertEvent = database.prepare(`
    INSERT INTO task_events (task_id, type, actor, occurred_at, details_json)
    VALUES (?, ?, ?, ?, ?)
  `);
  const selectTask = database.prepare('SELECT * FROM tasks WHERE id = ?');
  const selectTasks = database.prepare('SELECT * FROM tasks ORDER BY created_at ASC, id ASC');
  const selectEvents = database.prepare(`
    SELECT id, task_id, type, actor, occurred_at, details_json
    FROM task_events
    WHERE task_id = ?
    ORDER BY id ASC
  `);

  return {
    save(task, taskEvent) {
      database.exec('BEGIN IMMEDIATE');
      try {
        upsertTask.run(
          task.id,
          task.title,
          task.creator,
          task.policy,
          task.status,
          task.completedBy,
          task.approvedBy,
          task.createdAt,
          task.completedAt,
          task.approvedAt,
        );
        if (taskEvent) {
          insertEvent.run(
            taskEvent.taskId,
            taskEvent.type,
            taskEvent.actor,
            taskEvent.occurredAt,
            JSON.stringify(taskEvent.details ?? {}),
          );
        }
        database.exec('COMMIT');
      } catch (error) {
        database.exec('ROLLBACK');
        throw error;
      }
    },

    getTask(id) {
      return rowToTask(selectTask.get(id));
    },

    listTasks() {
      return selectTasks.all().map(rowToTask);
    },

    listEvents(taskId) {
      return selectEvents.all(taskId).map((row) => ({
        id: Number(row.id),
        taskId: row.task_id,
        type: row.type,
        actor: row.actor,
        occurredAt: row.occurred_at,
        details: JSON.parse(row.details_json),
      }));
    },

    close() {
      database.close();
    },
  };
}

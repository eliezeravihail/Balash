"""SQLite implementation of the :class:`TaskStore` contract.

Same boundary as the JSON store: it translates the whole :class:`State`
snapshot to and from a set of relational tables. Persisting rewrites the tables
inside a single transaction, which keeps the store contract (load-all /
save-all) identical to the JSON backend and therefore invisible to the manager.

Assignees are stored as a small JSON column so the model's own (de)serialization
stays the single source of truth for that tagged union; execution history lives
in its own table so ordering falls out of an autoincrement rowid.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from .models import Agent, ExecutionResult, Status, Task, assignee_from_dict
from .store import State, TaskStore

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agents (
    id       TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TEXT NOT NULL,
    assignee_json TEXT
);
CREATE TABLE IF NOT EXISTS executions (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id  INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    success  INTEGER NOT NULL,
    output   TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
CREATE TABLE IF NOT EXISTS task_prerequisites (
    task_id   INTEGER NOT NULL,
    prereq_id INTEGER NOT NULL,
    ordinal   INTEGER NOT NULL,
    PRIMARY KEY (task_id, prereq_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (prereq_id) REFERENCES tasks(id)
);
"""


class SqliteTaskStore(TaskStore):
    def __init__(self, path: os.PathLike | str) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.executescript(_SCHEMA)
        return conn

    def load(self) -> State:
        conn = self._connect()
        try:
            state = State()

            for key, value in conn.execute("SELECT key, value FROM meta"):
                if key == "next_id":
                    state.next_id = int(value)
                elif key == "next_agent_seq":
                    state.next_agent_seq = int(value)

            for agent_id, provider, model in conn.execute(
                "SELECT id, provider, model FROM agents"
            ):
                state.agents[agent_id] = Agent(
                    id=agent_id, provider=provider, model=model
                )

            for row in conn.execute(
                "SELECT id, title, description, status, assignee_json "
                "FROM tasks ORDER BY id"
            ):
                task_id, title, description, status, assignee_json = row
                assignee = assignee_from_dict(
                    json.loads(assignee_json) if assignee_json else None
                )
                state.tasks[task_id] = Task(
                    id=task_id,
                    title=title,
                    description=description,
                    status=Status.from_value(status),
                    assignee=assignee,
                )

            for task_id, prereq_id in conn.execute(
                "SELECT task_id, prereq_id FROM task_prerequisites "
                "ORDER BY task_id, ordinal"
            ):
                state.tasks[task_id].prerequisites.append(prereq_id)

            for task_id, agent_id, success, output in conn.execute(
                "SELECT task_id, agent_id, success, output "
                "FROM executions ORDER BY id"
            ):
                state.tasks[task_id].executions.append(
                    ExecutionResult(
                        task_id=task_id,
                        agent_id=agent_id,
                        success=bool(success),
                        output=output,
                    )
                )

            return state
        finally:
            conn.close()

    def save(self, state: State) -> None:
        conn = self._connect()
        try:
            with conn:  # one atomic transaction: commit on success, rollback on error
                conn.execute("DELETE FROM task_prerequisites")
                conn.execute("DELETE FROM executions")
                conn.execute("DELETE FROM tasks")
                conn.execute("DELETE FROM agents")
                conn.execute("DELETE FROM meta")

                conn.executemany(
                    "INSERT INTO meta (key, value) VALUES (?, ?)",
                    [
                        ("next_id", str(state.next_id)),
                        ("next_agent_seq", str(state.next_agent_seq)),
                    ],
                )
                conn.executemany(
                    "INSERT INTO agents (id, provider, model) VALUES (?, ?, ?)",
                    [(a.id, a.provider, a.model) for a in state.agents.values()],
                )
                for task in state.tasks.values():
                    assignee_json = (
                        json.dumps(task.assignee.to_dict())
                        if task.assignee
                        else None
                    )
                    conn.execute(
                        "INSERT INTO tasks (id, title, description, status, "
                        "assignee_json) VALUES (?, ?, ?, ?, ?)",
                        (
                            task.id,
                            task.title,
                            task.description,
                            task.status.value,
                            assignee_json,
                        ),
                    )
                    for ordinal, prereq_id in enumerate(task.prerequisites):
                        conn.execute(
                            "INSERT INTO task_prerequisites (task_id, prereq_id, "
                            "ordinal) VALUES (?, ?, ?)",
                            (task.id, prereq_id, ordinal),
                        )
                    for execution in task.executions:
                        conn.execute(
                            "INSERT INTO executions (task_id, agent_id, success, "
                            "output) VALUES (?, ?, ?, ?)",
                            (
                                execution.task_id,
                                execution.agent_id,
                                int(execution.success),
                                execution.output,
                            ),
                        )
        finally:
            conn.close()

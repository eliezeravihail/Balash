"""The SQLite schema -- the one and only place the table/column shape is defined.

Every table, column, and constraint the SQLite backend relies on lives here as DDL, so
"what the relational shape is" is enforced in exactly one file. The repositories phrase
their statements against these names, but the shape itself is declared once, here.

Four real tables, one per entity -- native columns, not JSON blobs in a column:

- ``tasks`` stores the tagged assignee ``{kind, id}`` in TWO nullable columns
  (``assignee_kind``, ``assignee_id``). A paired CHECK makes "half-assigned"
  unrepresentable: either both are NULL (unassigned) or both are set. There are
  deliberately NO foreign keys from ``assignee_id`` to members/agents -- the domain
  requires a task pointing at a since-removed member/agent to still load, and an FK
  would make SQLite reject what JSON tolerates.
- ``members`` / ``agents`` are plain id-keyed rows; their "upsert by id" is done with
  ``INSERT ... ON CONFLICT(id) DO UPDATE`` in the repositories.
- ``results`` is append-only history. A private ``seq`` AUTOINCREMENT surrogate key
  preserves insertion order -- the relational equivalent of JSON's append position --
  so ``for_task`` can ``ORDER BY seq`` to return oldest-first. ``seq`` is never
  surfaced through any port; ``ExecutionResult`` still carries no id of its own. There
  are no foreign keys here either, for the same read-tolerance reason.
- ``succeeded`` is an INTEGER 0/1 (SQLite has no native boolean); the repository maps
  it back to a Python ``bool`` on read.
- ``task_prerequisites`` is a join table -- one row per "task X depends on task Y" edge,
  real columns rather than a list packed into a JSON column (the stage-3 requirement).
  A task with no prerequisites simply has no rows here; declared order is recovered by
  reading in insertion (rowid) order, the same device the other tables use. There is
  deliberately NO foreign key, for the same read-tolerance reason as the rest of the
  schema, and consistent with the JSON backend storing prerequisites as plain ids.
"""

from __future__ import annotations

import sqlite3

_DDL = """
CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TEXT NOT NULL,
    assignee_kind TEXT,
    assignee_id   TEXT,
    CHECK ((assignee_kind IS NULL) = (assignee_id IS NULL)),
    CHECK (assignee_kind IN ('member', 'agent') OR assignee_kind IS NULL)
);

CREATE TABLE IF NOT EXISTS members (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    provider     TEXT NOT NULL,
    model        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    seq       INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id   TEXT    NOT NULL,
    agent_id  TEXT    NOT NULL,
    succeeded INTEGER NOT NULL,
    output    TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_results_task ON results(task_id);

CREATE TABLE IF NOT EXISTS task_prerequisites (
    task_id   TEXT NOT NULL,          -- the dependent task
    prereq_id TEXT NOT NULL,          -- a task it must wait on
    PRIMARY KEY (task_id, prereq_id)  -- an edge is named once; dedup is structural
);

CREATE INDEX IF NOT EXISTS ix_prereq_task ON task_prerequisites(task_id);
"""


def ensure_schema(connection: sqlite3.Connection) -> None:
    """Create every table and index if it is not there yet. Idempotent, so it runs
    safely on every startup -- a fresh db is built, an existing one is left as-is."""
    connection.executescript(_DDL)
    connection.commit()

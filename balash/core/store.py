"""SQLite storage for one Balash instance.

One database per instance. Raw items are never overwritten. Every derived
row keeps the id of what it came from, so any alert can be traced back to the
original photo or PDF.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    sender TEXT,
    received_at TEXT NOT NULL,
    media_type TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    caption TEXT,
    status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    account_key TEXT,
    store_name TEXT,
    store_kind TEXT,
    receipt_number TEXT,
    date TEXT,
    time TEXT,
    total REAL,
    discount_total REAL,
    payment_method TEXT,
    tab_customer TEXT,
    tab_previous_balance REAL,
    tab_charged REAL,
    tab_paid REAL,
    tab_new_balance REAL,
    uncertain TEXT NOT NULL DEFAULT '[]',
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS receipts_account ON receipts(account_key, date, time);

CREATE TABLE IF NOT EXISTS lines (
    receipt_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    description TEXT NOT NULL,
    norm_desc TEXT NOT NULL,
    barcode TEXT,
    quantity REAL,
    unit TEXT,
    unit_price REAL,
    line_total REAL,
    discount REAL,
    PRIMARY KEY (receipt_id, idx)
);

CREATE TABLE IF NOT EXISTS statement_lines (
    receipt_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    date TEXT,
    description TEXT,
    amount REAL,
    reference TEXT,
    PRIMARY KEY (receipt_id, idx)
);

CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    account_key TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT,
    amount REAL NOT NULL,
    source TEXT NOT NULL,
    ref TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    norm_desc TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    dedupe_key TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    severity TEXT NOT NULL,
    account_key TEXT,
    message TEXT NOT NULL,
    data TEXT NOT NULL,
    cites TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS llm_cache (
    key TEXT PRIMARY KEY,
    block TEXT NOT NULL,
    output TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block TEXT NOT NULL,
    model TEXT,
    stop_reason TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cache_read_tokens INTEGER,
    latency_ms INTEGER,
    ok INTEGER NOT NULL,
    error TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    pipeline TEXT NOT NULL,
    trigger TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    log TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT NOT NULL,
    kind TEXT NOT NULL,
    body TEXT,
    media_path TEXT,
    created_at TEXT NOT NULL,
    sent_at TEXT,
    error TEXT
);

CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    def query(self, sql: str, params: tuple | dict = ()) -> list[sqlite3.Row]:
        with self._lock:
            return list(self._conn.execute(sql, params))

    def one(self, sql: str, params: tuple | dict = ()) -> sqlite3.Row | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    # ---- key/value -------------------------------------------------------

    def kv_get(self, key: str, default: str | None = None) -> str | None:
        row = self.one("SELECT value FROM kv WHERE key = ?", (key,))
        return row["value"] if row else default

    def kv_set(self, key: str, value: str) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO kv(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    # ---- items -----------------------------------------------------------

    def item_by_sha(self, sha256: str) -> sqlite3.Row | None:
        return self.one("SELECT * FROM items WHERE sha256 = ?", (sha256,))

    def insert_item(self, item: dict[str, Any]) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO items(id, source, sender, received_at, media_type, path, sha256, caption, status) "
                "VALUES(:id, :source, :sender, :received_at, :media_type, :path, :sha256, :caption, 'new')",
                item,
            )

    def set_item_status(self, item_id: str, status: str) -> None:
        with self.tx() as c:
            c.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))

    # ---- llm cache and call log -----------------------------------------

    def cache_get(self, key: str) -> dict | None:
        row = self.one("SELECT output FROM llm_cache WHERE key = ?", (key,))
        return json.loads(row["output"]) if row else None

    def cache_put(self, key: str, block: str, output: dict) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT OR REPLACE INTO llm_cache(key, block, output, created_at) VALUES(?, ?, ?, ?)",
                (key, block, json.dumps(output, ensure_ascii=False), utcnow()),
            )

    def log_llm_call(self, **row: Any) -> None:
        row.setdefault("created_at", utcnow())
        cols = ", ".join(row)
        marks = ", ".join(f":{k}" for k in row)
        with self.tx() as c:
            c.execute(f"INSERT INTO llm_calls({cols}) VALUES({marks})", row)

    # ---- findings --------------------------------------------------------

    def insert_finding(self, finding: dict[str, Any]) -> bool:
        """Insert a finding. Returns False when an identical one already exists."""
        with self.tx() as c:
            cur = c.execute(
                "INSERT OR IGNORE INTO findings(id, dedupe_key, kind, severity, account_key, message, data, cites, created_at) "
                "VALUES(:id, :dedupe_key, :kind, :severity, :account_key, :message, :data, :cites, :created_at)",
                {
                    **finding,
                    "data": json.dumps(finding["data"], ensure_ascii=False),
                    "cites": json.dumps(finding["cites"]),
                    "created_at": finding.get("created_at") or utcnow(),
                },
            )
            return cur.rowcount == 1

    # ---- runs ------------------------------------------------------------

    def start_run(self, run_id: str, pipeline: str, trigger: str) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO runs(id, pipeline, trigger, started_at, status) VALUES(?, ?, ?, ?, 'running')",
                (run_id, pipeline, trigger, utcnow()),
            )

    def finish_run(self, run_id: str, status: str, log: list[dict]) -> None:
        with self.tx() as c:
            c.execute(
                "UPDATE runs SET finished_at = ?, status = ?, log = ? WHERE id = ?",
                (utcnow(), status, json.dumps(log, ensure_ascii=False), run_id),
            )

    # ---- outbox ----------------------------------------------------------

    def queue_message(self, recipient: str, kind: str, body: str | None, media_path: str | None = None) -> int:
        with self.tx() as c:
            cur = c.execute(
                "INSERT INTO outbox(recipient, kind, body, media_path, created_at) VALUES(?, ?, ?, ?, ?)",
                (recipient, kind, body, media_path, utcnow()),
            )
            return int(cur.lastrowid)

    def mark_sent(self, msg_id: int, error: str | None = None) -> None:
        with self.tx() as c:
            if error:
                c.execute("UPDATE outbox SET error = ? WHERE id = ?", (error, msg_id))
            else:
                c.execute("UPDATE outbox SET sent_at = ?, error = NULL WHERE id = ?", (utcnow(), msg_id))

    def pending_messages(self, recipient: str) -> list[sqlite3.Row]:
        return self.query(
            "SELECT * FROM outbox WHERE recipient = ? AND sent_at IS NULL ORDER BY id", (recipient,)
        )

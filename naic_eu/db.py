"""Database helpers for SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from naic_eu.paths import DEFAULT_DB_PATH, SCHEMA_PATH


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def log_ingest(
    conn: sqlite3.Connection,
    job_name: str,
    status: str,
    instrument_id: int | None = None,
    records_count: int = 0,
    message: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO ingest_log (job_name, instrument_id, status, records_count, message, finished_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """,
        (job_name, instrument_id, status, records_count, message),
    )
    conn.commit()

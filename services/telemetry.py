"""Privacy-safe operational telemetry for CareerLens.

This module deliberately exposes metadata-only recording functions.  Their
signatures cannot accept resume/job text, prompts, responses, or identities.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Optional
from uuid import uuid4


_trace_id: ContextVar[Optional[str]] = ContextVar("careerlens_trace_id", default=None)


def database_path() -> Path:
    return Path(
        os.getenv(
            "CAREERLENS_TELEMETRY_DB",
            "data/telemetry/careerlens.sqlite3",
        )
    )


def _connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            trace_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL CHECK(success IN (0, 1)),
            processing_ms REAL NOT NULL CHECK(processing_ms >= 0),
            match_score REAL CHECK(match_score BETWEEN 0 AND 100),
            route TEXT CHECK(route IN ('application', 'learning_plan', 'unknown')),
            page_count INTEGER NOT NULL CHECK(page_count >= 0),
            redaction_count INTEGER NOT NULL CHECK(redaction_count >= 0),
            error_type TEXT
        );
        CREATE TABLE IF NOT EXISTS provider_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            latency_ms REAL NOT NULL CHECK(latency_ms >= 0),
            success INTEGER NOT NULL CHECK(success IN (0, 1)),
            http_status INTEGER,
            error_type TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_attempt_trace ON provider_attempts(trace_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_time ON analyses(timestamp);
        """
    )
    return connection


def new_trace_id() -> str:
    """Return an opaque identifier containing no user information."""
    return uuid4().hex


@contextmanager
def trace_context(trace_id: str):
    token = _trace_id.set(trace_id)
    try:
        yield
    finally:
        _trace_id.reset(token)


def current_trace_id() -> Optional[str]:
    return _trace_id.get()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record_provider_attempt(
    provider: str,
    latency_ms: float,
    success: bool,
    http_status: Optional[int] = None,
    error_type: Optional[str] = None,
) -> None:
    """Persist one provider attempt without any request or response content."""
    with _connect() as connection:
        connection.execute(
            """INSERT INTO provider_attempts
               (trace_id, timestamp, provider, latency_ms, success, http_status, error_type)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                current_trace_id(),
                _now(),
                provider,
                max(0, latency_ms),
                int(success),
                http_status,
                error_type,
            ),
        )


def record_analysis(
    trace_id: str,
    success: bool,
    processing_ms: float,
    match_score: Optional[float],
    route: str,
    page_count: int,
    redaction_count: int,
    error_type: Optional[str] = None,
) -> None:
    """Persist the final metadata-only outcome of an analysis."""
    if route not in {"application", "learning_plan", "unknown"}:
        raise ValueError("Invalid analysis route")
    with _connect() as connection:
        connection.execute(
            """INSERT OR REPLACE INTO analyses
               (trace_id, timestamp, success, processing_ms, match_score, route,
                page_count, redaction_count, error_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                trace_id,
                _now(),
                int(success),
                max(0, processing_ms),
                match_score,
                route,
                max(0, page_count),
                max(0, redaction_count),
                error_type,
            ),
        )


def query_rows(sql: str, parameters=()):
    """Run a read-only dashboard query and return plain dictionaries."""
    if not sql.lstrip().upper().startswith("SELECT"):
        raise ValueError("Telemetry dashboard queries must be read-only")
    with _connect() as connection:
        return [dict(row) for row in connection.execute(sql, parameters).fetchall()]

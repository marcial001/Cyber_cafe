import sqlite3
from typing import Any


class BaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _one(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        row = self._conn.execute(query, params).fetchone()
        return dict(row) if row else None

    def _all(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

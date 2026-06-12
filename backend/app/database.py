import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import settings
from app.exceptions import AppError

SCHEMA_VERSION = "2.0.1"


def _read_sql_file(path: Path) -> str:
    if not path.exists():
        raise AppError(f"Fichier SQL manquant : {path}")
    return path.read_text(encoding="utf-8")


def init_database() -> None:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    root = settings.db_path.parent.parent

    if settings.db_path.exists():
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT valeur FROM config_systeme WHERE cle = 'schema_version'"
                ).fetchone()
                if row and row[0] == SCHEMA_VERSION:
                    return
        except sqlite3.Error:
            pass
        settings.db_path.unlink(missing_ok=True)

    schema = _read_sql_file(root / "database" / "schema.sql")
    seed = _read_sql_file(root / "database" / "seed.sql")
    with get_connection() as conn:
        conn.executescript(schema)
        conn.executescript(seed)
        conn.execute(
            "INSERT OR REPLACE INTO config_systeme (cle, valeur) VALUES ('schema_version', ?)",
            (SCHEMA_VERSION,),
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

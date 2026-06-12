from app.repositories.base import BaseRepository


class JournalRepository(BaseRepository):
    def log(self, action: str, employe_id: int | None, details: str | None = None, poste_id: int | None = None) -> None:
        self._conn.execute(
            "INSERT INTO journaux (employe_id, action, details, poste_id) VALUES (?, ?, ?, ?)",
            (employe_id, action, details, poste_id),
        )

    def list_recent(self, limit: int = 50) -> list[dict]:
        return self._all(
            """
            SELECT j.*, e.nom AS employe_nom
            FROM journaux j LEFT JOIN employes e ON e.id = j.employe_id
            ORDER BY j.id DESC LIMIT ?
            """,
            (min(limit, 200),),
        )

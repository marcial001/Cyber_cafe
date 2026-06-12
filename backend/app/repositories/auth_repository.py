from app.repositories.base import BaseRepository


class AuthRepository(BaseRepository):
    def get_employe_by_login(self, login: str) -> dict | None:
        return self._one(
            """
            SELECT e.*, r.code AS role_code, r.permissions
            FROM employes e JOIN roles r ON r.id = e.role_id
            WHERE e.login = ? AND e.actif = 1
            """,
            (login.strip().lower(),),
        )

    def save_token(self, token: str, employe_id: int, expire_at: str) -> None:
        self._conn.execute(
            "INSERT INTO tokens_auth (token, employe_id, expire_at) VALUES (?, ?, ?)",
            (token, employe_id, expire_at),
        )

    def get_employe_by_token(self, token: str) -> dict | None:
        return self._one(
            """
            SELECT e.id, e.login, e.nom, r.code AS role_code, r.permissions, t.expire_at
            FROM tokens_auth t
            JOIN employes e ON e.id = t.employe_id
            JOIN roles r ON r.id = e.role_id
            WHERE t.token = ? AND e.actif = 1
            """,
            (token,),
        )

    def revoke_token(self, token: str) -> None:
        self._conn.execute("DELETE FROM tokens_auth WHERE token = ?", (token,))

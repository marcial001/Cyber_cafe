from app.repositories.base import BaseRepository


class VoucherRepository(BaseRepository):
    def get_by_code(self, code: str) -> dict | None:
        return self._one("SELECT * FROM vouchers WHERE code = ?", (code.strip().upper(),))

    def mark_used(self, voucher_id: int) -> None:
        self._conn.execute(
            "UPDATE vouchers SET utilise = 1, utilise_at = datetime('now') WHERE id = ? AND utilise = 0",
            (voucher_id,),
        )

    def list_available(self) -> list[dict]:
        return self._all("SELECT * FROM vouchers WHERE utilise = 0 ORDER BY id DESC LIMIT 100")

    def list_all(self) -> list[dict]:
        return self._all("SELECT * FROM vouchers ORDER BY id DESC LIMIT 200")

    def create(self, code: str, duree_minutes: int, expire_heures: int = 24) -> dict:
        from app.exceptions import ConflictError, ValidationError

        code = (code or "").strip().upper()
        if not code or len(code) < 4:
            raise ValidationError("Code voucher invalide (min. 4 caractères)")
        if duree_minutes <= 0 or duree_minutes > 480:
            raise ValidationError("Durée invalide (1-480 minutes)")
        existing = self.get_by_code(code)
        if existing:
            raise ConflictError("Ce code existe déjà")
        duree_sec = duree_minutes * 60
        self._conn.execute(
            """
            INSERT INTO vouchers (code, duree_secondes, expire_heures, cumul_autorise)
            VALUES (?, ?, ?, 0)
            """,
            (code, duree_sec, expire_heures),
        )
        return self.get_by_code(code)

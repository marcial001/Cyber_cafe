from app.repositories.base import BaseRepository


class PosteRepository(BaseRepository):
    def list_etat(self) -> list[dict]:
        return self._all("SELECT * FROM v_postes_etat ORDER BY numero ASC")

    def get_by_id(self, poste_id: int) -> dict | None:
        return self._one(
            """
            SELECT p.*, g.code AS groupe_code, g.libelle AS groupe_libelle, g.prix_par_heure
            FROM postes p JOIN groupes_pc g ON g.id = p.groupe_id
            WHERE p.id = ? AND p.actif = 1
            """,
            (poste_id,),
        )

    def has_active_session(self, poste_id: int) -> bool:
        row = self._one(
            "SELECT id FROM sessions WHERE poste_id = ? AND statut IN ('en_cours', 'pause')",
            (poste_id,),
        )
        return row is not None

    def set_etat_materiel(self, poste_id: int, etat: str) -> None:
        self._conn.execute(
            "UPDATE postes SET etat_materiel = ? WHERE id = ?",
            (etat, poste_id),
        )

    def list_for_plan(self) -> list[dict]:
        return self.list_etat()

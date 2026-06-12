from app.repositories.base import BaseRepository


class TarifRepository(BaseRepository):
    def list_actifs(self) -> list[dict]:
        return self._all(
            "SELECT id, code, libelle, prix_par_heure, heure_debut_nuit, heure_fin_nuit "
            "FROM tarifs WHERE actif = 1 ORDER BY id"
        )

    def get_by_code(self, code: str) -> dict | None:
        return self._one(
            "SELECT id, code, libelle, prix_par_heure FROM tarifs WHERE code = ? AND actif = 1",
            (code,),
        )

from app.repositories.base import BaseRepository


class PosRepository(BaseRepository):
    def list_produits(self) -> list[dict]:
        return self._all(
            "SELECT * FROM produits WHERE actif = 1 ORDER BY categorie, libelle"
        )

    def get_produit(self, produit_id: int) -> dict | None:
        return self._one("SELECT * FROM produits WHERE id = ? AND actif = 1", (produit_id,))

    def decrement_stock(self, produit_id: int, qty: int) -> None:
        self._conn.execute(
            "UPDATE produits SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (qty, produit_id, qty),
        )

    def create_vente(self, session_id: int | None, poste_id: int | None, employe_id: int, total: float) -> int:
        cur = self._conn.execute(
            "INSERT INTO ventes_pos (session_id, poste_id, employe_id, total) VALUES (?, ?, ?, ?)",
            (session_id, poste_id, employe_id, total),
        )
        return int(cur.lastrowid)

    def add_ligne(self, vente_id: int, produit_id: int, qty: int, prix: float, sous_total: float) -> None:
        self._conn.execute(
            "INSERT INTO lignes_vente (vente_id, produit_id, quantite, prix_unitaire, sous_total) VALUES (?, ?, ?, ?, ?)",
            (vente_id, produit_id, qty, prix, sous_total),
        )

    def stock_alerts(self) -> list[dict]:
        return self._all(
            "SELECT * FROM produits WHERE actif = 1 AND stock <= seuil_alerte ORDER BY stock"
        )

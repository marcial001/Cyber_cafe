from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.pos_repository import PosRepository
from app.repositories.session_repository import SessionRepository


class PosService:
    def __init__(self, pos_repo: PosRepository, session_repo: SessionRepository):
        self._pos = pos_repo
        self._sessions = session_repo

    def list_produits(self) -> list[dict]:
        return self._pos.list_produits()

    def stock_alerts(self) -> list[dict]:
        return self._pos.stock_alerts()

    def vendre(self, items: list[dict], session_id: int | None, poste_id: int | None, employe_id: int) -> dict:
        if not items:
            raise ValidationError("Panier vide")
        total = 0.0
        lignes = []
        for item in items:
            pid = int(item.get("produit_id", 0))
            qty = int(item.get("quantite", 0))
            if pid <= 0 or qty <= 0 or qty > 99:
                raise ValidationError("Ligne panier invalide")
            prod = self._pos.get_produit(pid)
            if not prod:
                raise NotFoundError(f"Produit {pid} introuvable")
            if prod["stock"] < qty:
                raise ConflictError(f"Stock insuffisant : {prod['libelle']}")
            sous = round(float(prod["prix"]) * qty, 0)
            total += sous
            lignes.append((pid, qty, prod["prix"], sous))

        if session_id:
            s = self._sessions.get_by_id(session_id)
            if not s or s["statut"] not in ("en_cours", "pause"):
                raise ConflictError("Session inactive pour ajout POS")

        vente_id = self._pos.create_vente(session_id, poste_id, employe_id, total)
        for pid, qty, prix, sous in lignes:
            self._pos.add_ligne(vente_id, pid, qty, prix, sous)
            self._pos.decrement_stock(pid, qty)

        if session_id:
            self._sessions.add_pos_amount(session_id, total)

        return {"vente_id": vente_id, "total": total, "lignes": len(lignes)}

from datetime import datetime

from app.domain.pricing import (
    appliquer_taxes,
    calculer_montant,
    generer_numero_ticket,
    multiplicateur_grille,
)
from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.poste_repository import PosteRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.tarif_repository import TarifRepository
from app.repositories.voucher_repository import VoucherRepository
from app.schemas import SessionStartIn, SessionStopIn


class SessionService:
    def __init__(
        self,
        poste_repo: PosteRepository,
        tarif_repo: TarifRepository,
        session_repo: SessionRepository,
        voucher_repo: VoucherRepository | None = None,
    ):
        self._postes = poste_repo
        self._tarifs = tarif_repo
        self._sessions = session_repo
        self._vouchers = voucher_repo

    def demarrer(self, payload: SessionStartIn, employe_id: int | None = None) -> dict:
        poste = self._postes.get_by_id(payload.poste_id)
        if not poste:
            raise NotFoundError("Poste introuvable")
        if poste.get("etat_materiel") in ("panne", "eteint", "maintenance"):
            raise ConflictError(f"Poste en état : {poste['etat_materiel']}")
        if self._postes.has_active_session(payload.poste_id):
            raise ConflictError("Ce poste est déjà occupé")

        tarif = self._tarifs.get_by_code(payload.tarif_code)
        if not tarif:
            raise NotFoundError("Tarif inconnu")

        mode = payload.mode_facturation or "postpay"
        voucher_id = None
        client_id = payload.client_id

        if mode == "voucher":
            if not self._vouchers or not payload.voucher_code:
                raise ValidationError("Code voucher requis")
            v = self._vouchers.get_by_code(payload.voucher_code)
            if not v or v["utilise"]:
                raise NotFoundError("Voucher invalide ou déjà utilisé")
            voucher_id = v["id"]

        if mode == "compte":
            if not client_id:
                raise ValidationError("Sélectionnez un compte client")
            client = self._sessions._conn.execute(
                "SELECT id, solde_xaf FROM clients WHERE id = ? AND actif = 1",
                (client_id,),
            ).fetchone()
            if not client:
                raise NotFoundError("Compte client introuvable")
            if float(client[1]) <= 0:
                raise ValidationError("Solde client insuffisant")

        debut = SessionRepository.now_iso()
        session_id = self._sessions.create(
            {
                "poste_id": payload.poste_id,
                "tarif_id": tarif["id"],
                "client_id": client_id,
                "voucher_id": voucher_id,
                "employe_id": employe_id,
                "mode_facturation": mode,
                "debut": debut,
                "notes": payload.notes,
            }
        )
        if voucher_id and self._vouchers:
            self._vouchers.mark_used(voucher_id)
        return self._sessions.get_by_id(session_id)

    def pause(self, session_id: int) -> dict:
        s = self._require_active(session_id)
        if s["statut"] == "pause":
            raise ConflictError("Session déjà en pause")
        self._sessions.update_statut(session_id, "pause")
        return self._sessions.get_by_id(session_id)

    def reprendre(self, session_id: int) -> dict:
        s = self._sessions.get_by_id(session_id)
        if not s or s["statut"] != "pause":
            raise ConflictError("Session non pausable")
        self._sessions.update_statut(session_id, "en_cours")
        return self._sessions.get_by_id(session_id)

    def prolonger(self, session_id: int, minutes: int) -> dict:
        if minutes <= 0 or minutes > 480:
            raise ValidationError("Durée de prolongation invalide (1-480 min)")
        self._require_active(session_id)
        self._sessions.add_extra_time(session_id, minutes * 60)
        return self._sessions.get_by_id(session_id)

    def transferer(self, session_id: int, new_poste_id: int) -> dict:
        self._require_active(session_id)
        poste = self._postes.get_by_id(new_poste_id)
        if not poste:
            raise NotFoundError("Poste cible introuvable")
        if self._postes.has_active_session(new_poste_id):
            raise ConflictError("Poste cible occupé")
        self._sessions.transfer(session_id, new_poste_id)
        return self._sessions.get_by_id(session_id)

    def arreter(self, payload: SessionStopIn) -> dict:
        session = self._require_active(payload.session_id)
        debut = self._parse_dt(session["debut"])
        fin_dt = datetime.fromisoformat(SessionRepository.now_iso())
        duree = int((fin_dt - debut).total_seconds()) + int(session.get("extra_secondes") or 0)
        if duree < 0:
            raise ValidationError("Durée incohérente")

        grilles = self._sessions.list_grille()
        mult = multiplicateur_grille(grilles, fin_dt, session.get("groupe_id"))
        prix = float(session["prix_par_heure"])
        montant_pc = calculer_montant(
            duree,
            prix,
            mult,
            int(session.get("deduction_min_sec") or 0),
            int(session.get("periode_grace_sec") or 0),
        )
        montant_pos = float(session.get("montant_pos") or 0)
        taxes = self._sessions.list_taxes()
        montant_ht = montant_pc + montant_pos
        montant_ttc, montant_taxes = appliquer_taxes(montant_ht, taxes)
        ticket = generer_numero_ticket(payload.session_id)

        self._sessions.close(
            payload.session_id,
            {
                "fin": fin_dt.isoformat(timespec="seconds"),
                "duree_secondes": duree,
                "montant_pc": montant_pc,
                "montant_pos": montant_pos,
                "montant_taxes": montant_taxes,
                "montant": montant_ttc,
                "numero_ticket": ticket,
            },
        )
        if session.get("mode_facturation") == "compte" and session.get("client_id"):
            self._sessions._conn.execute(
                "UPDATE clients SET solde_xaf = MAX(0, solde_xaf - ?) WHERE id = ?",
                (montant_ttc, session["client_id"]),
            )
        updated = self._sessions.get_by_id(payload.session_id)
        if not updated:
            raise NotFoundError("Échec clôture session")
        return updated

    def ticket(self, session_id: int) -> dict:
        session = self._sessions.get_by_id(session_id)
        if not session or session["statut"] != "terminee":
            raise NotFoundError("Ticket indisponible")
        return {
            "numero_ticket": session["numero_ticket"],
            "poste_numero": session["poste_numero"],
            "tarif_libelle": session["tarif_libelle"],
            "debut": session["debut"],
            "fin": session["fin"],
            "duree_minutes": int((session["duree_secondes"] or 0) / 60),
            "montant_pc": session.get("montant_pc"),
            "montant_pos": session.get("montant_pos"),
            "montant_taxes": session.get("montant_taxes"),
            "montant": session["montant"],
            "devise": "XAF",
        }

    def _require_active(self, session_id: int) -> dict:
        session = self._sessions.get_by_id(session_id)
        if not session:
            raise NotFoundError("Session introuvable")
        if session["statut"] not in ("en_cours", "pause"):
            raise ConflictError("Session non active")
        return session

    @staticmethod
    def _parse_dt(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError("Horodatage invalide") from exc

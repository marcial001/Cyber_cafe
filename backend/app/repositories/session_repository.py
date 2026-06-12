from datetime import datetime, timezone

from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    def get_by_id(self, session_id: int) -> dict | None:
        return self._one(
            """
            SELECT s.*, p.numero AS poste_numero, p.groupe_id, g.prix_par_heure AS groupe_prix,
                   t.code AS tarif_code, t.libelle AS tarif_libelle, t.prix_par_heure,
                   t.periode_grace_sec, t.deduction_min_sec
            FROM sessions s
            JOIN postes p ON p.id = s.poste_id
            JOIN groupes_pc g ON g.id = p.groupe_id
            JOIN tarifs t ON t.id = s.tarif_id
            WHERE s.id = ?
            """,
            (session_id,),
        )

    def create(self, data: dict) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO sessions (
                poste_id, tarif_id, client_id, voucher_id, employe_id,
                mode_facturation, debut, statut, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'en_cours', ?)
            """,
            (
                data["poste_id"],
                data["tarif_id"],
                data.get("client_id"),
                data.get("voucher_id"),
                data.get("employe_id"),
                data["mode_facturation"],
                data["debut"],
                data.get("notes"),
            ),
        )
        return int(cur.lastrowid)

    def update_statut(self, session_id: int, statut: str) -> None:
        self._conn.execute(
            "UPDATE sessions SET statut = ? WHERE id = ? AND statut IN ('en_cours', 'pause')",
            (statut, session_id),
        )

    def add_extra_time(self, session_id: int, seconds: int) -> None:
        self._conn.execute(
            "UPDATE sessions SET extra_secondes = extra_secondes + ? WHERE id = ?",
            (seconds, session_id),
        )

    def transfer(self, session_id: int, new_poste_id: int) -> None:
        self._conn.execute(
            "UPDATE sessions SET poste_id = ? WHERE id = ? AND statut IN ('en_cours', 'pause')",
            (new_poste_id, session_id),
        )

    def add_pos_amount(self, session_id: int, amount: float) -> None:
        self._conn.execute(
            "UPDATE sessions SET montant_pos = COALESCE(montant_pos, 0) + ? WHERE id = ?",
            (amount, session_id),
        )

    def close(self, session_id: int, data: dict) -> None:
        self._conn.execute(
            """
            UPDATE sessions SET
                fin = ?, duree_secondes = ?, montant_pc = ?, montant_pos = ?,
                montant_taxes = ?, montant = ?, statut = 'terminee', numero_ticket = ?
            WHERE id = ? AND statut IN ('en_cours', 'pause')
            """,
            (
                data["fin"],
                data["duree_secondes"],
                data["montant_pc"],
                data.get("montant_pos", 0),
                data.get("montant_taxes", 0),
                data["montant"],
                data["numero_ticket"],
                session_id,
            ),
        )

    def stats_journalieres(self, date_iso: str) -> dict:
        recettes = self._one(
            """
            SELECT COALESCE(SUM(montant), 0) AS total, COUNT(*) AS nb
            FROM sessions WHERE statut = 'terminee' AND date(debut) = date(?)
            """,
            (date_iso,),
        )
        postes = self._all(
            """
            SELECT p.numero, p.libelle, COUNT(s.id) AS nb_sessions,
                   COALESCE(SUM(s.montant), 0) AS recettes
            FROM sessions s JOIN postes p ON p.id = s.poste_id
            WHERE s.statut = 'terminee' AND date(s.debut) = date(?)
            GROUP BY p.id ORDER BY nb_sessions DESC LIMIT 8
            """,
            (date_iso,),
        )
        return {
            "recettes_totales": recettes["total"] if recettes else 0,
            "nombre_sessions": recettes["nb"] if recettes else 0,
            "postes_plus_utilises": postes,
        }

    def list_grille(self) -> list[dict]:
        return self._all("SELECT * FROM grille_horaire WHERE actif = 1")

    def list_taxes(self) -> list[dict]:
        return self._all("SELECT * FROM taxes WHERE actif = 1")

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")

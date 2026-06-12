from datetime import date

from app.repositories.poste_repository import PosteRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.tarif_repository import TarifRepository


class DashboardService:
    def __init__(
        self,
        poste_repo: PosteRepository,
        tarif_repo: TarifRepository,
        session_repo: SessionRepository,
    ):
        self._postes = poste_repo
        self._tarifs = tarif_repo
        self._sessions = session_repo

    def postes(self) -> list[dict]:
        return self._postes.list_etat()

    def tarifs(self) -> list[dict]:
        return self._tarifs.list_actifs()

    def stats_aujourd_hui(self) -> dict:
        today = date.today().isoformat()
        stats = self._sessions.stats_journalieres(today)
        return {"date": today, **stats}

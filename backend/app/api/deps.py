from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header

from app.database import get_connection
from app.repositories.auth_repository import AuthRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.pos_repository import PosRepository
from app.repositories.poste_repository import PosteRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.tarif_repository import TarifRepository
from app.repositories.voucher_repository import VoucherRepository
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.pos_service import PosService
from app.services.session_service import SessionService


def get_db() -> Generator:
    with get_connection() as conn:
        yield conn


def get_current_user(
    conn=Depends(get_db),
    x_auth_token: Annotated[str | None, Header()] = None,
):
    auth = AuthService(AuthRepository(conn))
    return auth.resolve_token(x_auth_token)


def build_session_service(conn) -> SessionService:
    return SessionService(
        PosteRepository(conn),
        TarifRepository(conn),
        SessionRepository(conn),
        VoucherRepository(conn),
    )


def build_dashboard_service(conn) -> DashboardService:
    return DashboardService(
        PosteRepository(conn),
        TarifRepository(conn),
        SessionRepository(conn),
    )


def build_pos_service(conn) -> PosService:
    return PosService(PosRepository(conn), SessionRepository(conn))


def build_auth_service(conn) -> AuthService:
    return AuthService(AuthRepository(conn))


def build_journal(conn) -> JournalRepository:
    return JournalRepository(conn)


def require_permission(permission: str):
    """FastAPI dependency: authenticated user must hold the given permission."""

    def _check(user=Depends(get_current_user), conn=Depends(get_db)):
        AuthService(AuthRepository(conn)).require_perm(user, permission)
        return user

    return _check

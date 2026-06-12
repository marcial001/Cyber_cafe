from datetime import datetime

from app.exceptions import ValidationError
from app.repositories.auth_repository import AuthRepository
from app.security import has_permission, new_token, parse_permissions, token_expiry, verify_password


class AuthService:
    def __init__(self, repo: AuthRepository):
        self._repo = repo

    def login(self, login: str, password: str) -> dict:
        login = (login or "").strip().lower()
        if not login or not password:
            raise ValidationError("Identifiants requis")
        employe = self._repo.get_employe_by_login(login)
        if not employe or not verify_password(password, employe["mot_de_passe"]):
            raise ValidationError("Login ou mot de passe incorrect")
        token = new_token()
        self._repo.save_token(token, employe["id"], token_expiry())
        perms = parse_permissions(employe["permissions"])
        return {
            "token": token,
            "employe": {
                "id": employe["id"],
                "login": employe["login"],
                "nom": employe["nom"],
                "role": employe["role_code"],
                "permissions": perms,
            },
        }

    def resolve_token(self, token: str | None) -> dict:
        if not token:
            raise ValidationError("Authentification requise")
        row = self._repo.get_employe_by_token(token)
        if not row:
            raise ValidationError("Session expirée ou invalide")
        if datetime.fromisoformat(row["expire_at"]) < datetime.utcnow():
            self._repo.revoke_token(token)
            raise ValidationError("Session expirée")
        return {
            "id": row["id"],
            "login": row["login"],
            "nom": row["nom"],
            "role": row["role_code"],
            "permissions": parse_permissions(row["permissions"]),
        }

    def require_perm(self, user: dict, perm: str) -> None:
        if not has_permission(user.get("permissions", []), perm):
            raise ValidationError(f"Permission refusée : {perm}")

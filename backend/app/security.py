import hashlib
import json
import secrets
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    if not password or len(password) < 3:
        raise ValueError("Mot de passe trop court")
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    if not password or not stored_hash:
        return False
    return secrets.compare_digest(hash_password(password), stored_hash)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_expiry(hours: int = 12) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat(timespec="seconds")


def parse_permissions(raw: str) -> list[str]:
    try:
        perms = json.loads(raw)
        return perms if isinstance(perms, list) else []
    except json.JSONDecodeError:
        return []


def has_permission(permissions: list[str], required: str) -> bool:
    if "*" in permissions:
        return True
    return required in permissions

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CyberCafé Manager API"
    api_prefix: str = "/api/v1"
    db_path: Path = Path(__file__).resolve().parents[2] / "data" / "cybercafe.db"
    tarifs_path: Path = Path(__file__).resolve().parents[2] / "config" / "tarifs.json"
    cors_origins: list[str] = ["http://localhost:5173", "file://"]

    class Config:
        env_prefix = "CYBERCAFE_"


settings = Settings()

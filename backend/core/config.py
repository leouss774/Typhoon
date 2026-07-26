"""
Environment & Application Configuration
========================================
Uses pydantic-settings to load from .env / environment variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — loaded from root .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Server ───
    PORT: int = 8000
    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    # ─── Database ───
    # SQLite for dev: sqlite:///./data/previa.db
    # Supabase PostgreSQL for prod: postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
    DATABASE_URL: str = "sqlite:///./data/previa.db"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql")

    # ─── Auth ───
    # Custom JWT (fallback when Supabase Auth is not used)
    JWT_SECRET: str = "change-me-to-a-long-random-secret-in-production"
    JWT_EXPIRATION_HOURS: int = 24
    COOKIE_SECURE: bool = False

    # ─── Supabase Auth (alternative to custom JWT) ───
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    @property
    def use_supabase_auth(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)

    # ─── External APIs ───
    GEORISQUES_V2_TOKEN: str = ""
    BDNB_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-large-latest"

    # ─── Uploads ───
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    # ─── CORS ───
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


# Ensure upload directory exists
settings = Settings()
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

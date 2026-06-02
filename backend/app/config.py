"""Application configuration.

Settings are read from environment variables (prefixed ``MUSICGEN_``) or an
optional ``.env`` file. Everything has a sensible default so the MVP runs with
zero configuration.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/  (this file lives in backend/app/config.py)
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
AUDIO_DIR = STORAGE_DIR / "audio"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MUSICGEN_",
        extra="ignore",
    )

    app_name: str = "Royalty-Free Music Generator"

    # Provider used when a request does not specify one.
    default_provider: str = "mock"

    # Storage / database locations.
    audio_dir: Path = AUDIO_DIR
    database_url: str = f"sqlite:///{(STORAGE_DIR / 'app.db').as_posix()}"

    # Frontend origins allowed by CORS.
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    # Allow any localhost/127.0.0.1 port in dev (Next.js falls back to 3001,
    # 3002, ... when 3000 is taken). Set to None in production and use the
    # explicit cors_origins list instead.
    cors_origin_regex: str | None = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"

    # Placeholder credentials for future real providers.
    mubert_api_key: str | None = None
    stable_audio_api_key: str | None = None
    local_loop_library_dir: Path | None = None


settings = Settings()

# Make sure the storage folders exist before anything tries to use them.
settings.audio_dir.mkdir(parents=True, exist_ok=True)

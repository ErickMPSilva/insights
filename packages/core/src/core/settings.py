from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "dev"

    app_database_url: str
    app_migrator_database_url: str
    warehouse_database_url: str
    redis_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()

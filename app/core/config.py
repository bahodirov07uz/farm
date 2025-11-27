from functools import lru_cache

from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "med"
    api_v1_prefix: str = "/api"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
    alembic_database_url: str | None = None

    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: list[AnyHttpUrl] = []

    @computed_field  # type: ignore[misc]
    @property
    def sync_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg"):
            return self.database_url.replace("+asyncpg", "")
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


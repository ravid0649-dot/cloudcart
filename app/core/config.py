from __future__ import annotations

from functools import lru_cache
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudCart"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    # SQLite default keeps local setup simple; set PostgreSQL URL in .env/Render for production.
    database_url: str = "sqlite:///./cloudcart.db"
    cors_origins: Union[List[AnyHttpUrl], List[str]] = ["http://localhost:8000"]
    uploads_dir: str = "app/static/uploads"
    max_upload_size_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

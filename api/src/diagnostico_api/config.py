"""Configuración por variables de entorno."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación (prefijo DIAGNOSTICO_)."""

    model_config = SettingsConfigDict(env_prefix="DIAGNOSTICO_")

    app_name: str = "diagnostico-api"
    version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()

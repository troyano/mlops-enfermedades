"""Configuración por variables de entorno."""

import os

DEFAULT_API_URL = "http://api:8000"


def get_api_url() -> str:
    """URL base de la API, sin barra final."""
    return os.environ.get("API_URL", DEFAULT_API_URL).rstrip("/")

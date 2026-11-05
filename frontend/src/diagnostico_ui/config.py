"""Configuración por variables de entorno."""

import os

DEFAULT_BACKEND_URL = "http://backend:8000"


def get_backend_url() -> str:
    """URL base del backend, sin barra final."""
    return os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")

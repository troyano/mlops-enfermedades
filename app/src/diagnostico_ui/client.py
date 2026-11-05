"""Cliente HTTP hacia la API."""

from typing import Any

import httpx


class ApiError(Exception):
    """La API no respondió o devolvió un error."""


def health(
    base_url: str, client: httpx.Client | None = None, timeout: float = 5.0
) -> dict[str, Any]:
    """Consulta GET /health y devuelve el JSON de respuesta."""
    own = client is None
    http = client or httpx.Client(timeout=timeout)
    try:
        response = http.get(f"{base_url}/health")
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data
    except (httpx.HTTPError, ValueError) as exc:
        raise ApiError(str(exc)) from exc
    finally:
        if own:
            http.close()

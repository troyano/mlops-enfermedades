"""Cliente HTTP hacia la API de diagnóstico."""

from typing import Any

import httpx

Consulta = dict[str, Any]


class ApiError(Exception):
    """La API devolvió una respuesta inesperada."""


class ApiUnavailableError(ApiError):
    """No se pudo contactar con la API (caída, red o tiempo de espera)."""


class ApiValidationError(ApiError):
    """La API rechazó los datos (422). `messages` trae textos legibles."""

    def __init__(self, messages: list[str]) -> None:
        super().__init__("; ".join(messages))
        self.messages = messages


def _send(
    method: str,
    url: str,
    client: httpx.Client | None,
    timeout: float,
    **kwargs: Any,
) -> httpx.Response:
    own = client is None
    http = client or httpx.Client(timeout=timeout)
    try:
        return http.request(method, url, **kwargs)
    except httpx.TimeoutException as exc:
        raise ApiUnavailableError(f"La API no respondió a tiempo ({url}).") from exc
    except httpx.TransportError as exc:
        raise ApiUnavailableError(f"No se pudo conectar con la API ({url}).") from exc
    finally:
        if own:
            http.close()


def _mensajes_422(response: httpx.Response) -> list[str]:
    """Convierte el detalle estándar de FastAPI en mensajes cortos."""
    try:
        detail = response.json().get("detail")
    except (ValueError, AttributeError):
        detail = None
    if isinstance(detail, str):
        return [detail]
    if not isinstance(detail, list):
        return ["La API rechazó los datos enviados."]
    mensajes: list[str] = []
    for item in detail:
        if not isinstance(item, dict):
            continue
        loc = [str(p) for p in item.get("loc", []) if p != "body"]
        msg = str(item.get("msg", "dato no válido"))
        mensajes.append(f"{' › '.join(loc)}: {msg}" if loc else msg)
    return mensajes or ["La API rechazó los datos enviados."]


def _json(response: httpx.Response) -> Any:
    if response.status_code == 422:
        raise ApiValidationError(_mensajes_422(response))
    if response.status_code >= 400:
        raise ApiError(f"La API respondió con el código {response.status_code}.")
    try:
        return response.json()
    except ValueError as exc:
        raise ApiError("La API devolvió una respuesta que no es JSON.") from exc


def health(
    base_url: str, client: httpx.Client | None = None, timeout: float = 5.0
) -> dict[str, Any]:
    """Consulta GET /health y devuelve el JSON de respuesta."""
    data = _json(_send("GET", f"{base_url}/health", client, timeout))
    if not isinstance(data, dict):
        raise ApiError("Respuesta inesperada de /health.")
    return data


def predecir(
    base_url: str,
    payload: dict[str, Any],
    client: httpx.Client | None = None,
    timeout: float = 10.0,
) -> Consulta:
    """Envía una consulta a POST /predecir y devuelve el registro creado."""
    data = _json(_send("POST", f"{base_url}/predecir", client, timeout, json=payload))
    if not isinstance(data, dict):
        raise ApiError("Respuesta inesperada de /predecir.")
    return data


def consultas(
    base_url: str,
    limite: int = 100,
    client: httpx.Client | None = None,
    timeout: float = 10.0,
) -> list[Consulta]:
    """Lista las consultas guardadas, de la más reciente a la más antigua."""
    data = _json(_send("GET", f"{base_url}/consultas", client, timeout, params={"limite": limite}))
    if not isinstance(data, list):
        raise ApiError("Respuesta inesperada de /consultas.")
    return data

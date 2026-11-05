import httpx
import pytest

from diagnostico_ui.client import ApiError, health


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_health_ok() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"status": "ok"}))
    assert health("http://x", _client(transport)) == {"status": "ok"}


def test_health_http_error() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(500))
    with pytest.raises(ApiError):
        health("http://x", _client(transport))


def test_health_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexión")

    with pytest.raises(ApiError):
        health("http://x", _client(httpx.MockTransport(handler)))

import json

import httpx
import pytest

from diagnostico_ui.client import (
    ApiError,
    ApiUnavailableError,
    ApiValidationError,
    consultas,
    health,
    predecir,
)


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


CONSULTA = {"id": "C-0001", "estado": "NO ENFERMO"}
PAYLOAD = {"nombre": "Ana Gómez", "temperatura": 36.5, "sintomas": []}


def test_predecir_ok_envia_json() -> None:
    vistos: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        vistos.append(request)
        return httpx.Response(200, json=CONSULTA)

    resultado = predecir("http://x", PAYLOAD, _client(httpx.MockTransport(handler)))
    assert resultado == CONSULTA
    assert vistos[0].method == "POST" and vistos[0].url.path == "/predecir"
    assert json.loads(vistos[0].content) == PAYLOAD


def test_predecir_422_da_mensajes_legibles() -> None:
    cuerpo = {
        "detail": [
            {"loc": ["body", "temperatura"], "msg": "debe estar entre 35 y 42"},
            {"loc": ["body", "sintomas", 0, "intensidad"], "msg": "máximo 10"},
        ]
    }
    transport = httpx.MockTransport(lambda r: httpx.Response(422, json=cuerpo))
    with pytest.raises(ApiValidationError) as info:
        predecir("http://x", PAYLOAD, _client(transport))
    assert info.value.messages == [
        "temperatura: debe estar entre 35 y 42",
        "sintomas › 0 › intensidad: máximo 10",
    ]


def test_predecir_422_con_detalle_texto_o_invalido() -> None:
    texto = httpx.MockTransport(lambda r: httpx.Response(422, json={"detail": "mal"}))
    with pytest.raises(ApiValidationError) as info:
        predecir("http://x", PAYLOAD, _client(texto))
    assert info.value.messages == ["mal"]
    roto = httpx.MockTransport(lambda r: httpx.Response(422, text="no json"))
    with pytest.raises(ApiValidationError) as info2:
        predecir("http://x", PAYLOAD, _client(roto))
    assert info2.value.messages == ["La API rechazó los datos enviados."]


def test_predecir_error_500_y_respuesta_no_json() -> None:
    with pytest.raises(ApiError, match="500"):
        predecir("http://x", PAYLOAD, _client(httpx.MockTransport(lambda r: httpx.Response(500))))
    with pytest.raises(ApiError, match="JSON"):
        predecir(
            "http://x",
            PAYLOAD,
            _client(httpx.MockTransport(lambda r: httpx.Response(200, text="x"))),
        )


def test_api_caida_y_timeout() -> None:
    def caida(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexión")

    def lenta(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("tarda")

    with pytest.raises(ApiUnavailableError, match="conectar"):
        predecir("http://x", PAYLOAD, _client(httpx.MockTransport(caida)))
    with pytest.raises(ApiUnavailableError, match="a tiempo"):
        consultas("http://x", client=_client(httpx.MockTransport(lenta)))


def test_consultas_ok_y_parametro_limite() -> None:
    vistos: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        vistos.append(request)
        return httpx.Response(200, json=[CONSULTA])

    assert consultas("http://x", 5, _client(httpx.MockTransport(handler))) == [CONSULTA]
    assert vistos[0].url.params["limite"] == "5"


def test_consultas_respuesta_inesperada() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"a": 1}))
    with pytest.raises(ApiError):
        consultas("http://x", client=_client(transport))

"""Pruebas de la interfaz con streamlit.testing (la API se sustituye por un doble)."""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from diagnostico_ui import client

APP = str(Path(__file__).parents[1] / "src" / "diagnostico_ui" / "app.py")

RESPUESTA: dict[str, Any] = {
    "id": "C-0001",
    "fecha": "2026-11-05T18:30:00+00:00",
    "nombre": "Marta Ospina Cruz",
    "temperatura": 39.0,
    "sintomas": [],
    "estado": "ENFERMEDAD AGUDA",
    "regla": "Intensidad de 7 o más",
    "resumen": {"cantidad_sintomas": 4, "intensidad_maxima": 8, "duracion_maxima_dias": 3},
    "version_modelo": "simulado-0.1.0",
    "aviso": "Solo didáctico.",
}


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    enviados: list[dict[str, Any]] = []

    def predecir(base_url: str, payload: dict[str, Any], **_: Any) -> dict[str, Any]:
        enviados.append(payload)
        return RESPUESTA

    monkeypatch.setattr(client, "predecir", predecir)
    monkeypatch.setattr(client, "consultas", lambda *a, **k: [RESPUESTA])
    return enviados


def _html(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def test_renderiza_sin_excepciones(api: list[dict[str, Any]]) -> None:
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.text_input(key="nombre").value == "Marta Ospina Cruz"
    assert "Aún no hay una consulta" in _html(at)
    assert "ENFERMEDAD AGUDA" in _html(at)  # el historial (doble) ya trae una consulta


def test_consultar_envia_payload_y_muestra_resultado(api: list[dict[str, Any]]) -> None:
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button(key="consultar").click().run()
    assert not at.exception and not at.error
    assert api[0]["nombre"] == "Marta Ospina Cruz" and api[0]["temperatura"] == 39.0
    assert len(api[0]["sintomas"]) == 4
    assert "dx-res-top" in _html(at) and "C-0001" in _html(at)


def test_validacion_local_muestra_errores_y_no_llama_a_la_api(api: list[dict[str, Any]]) -> None:
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_input(key="nombre").set_value("Ana").run()
    at.button(key="consultar").click().run()
    assert api == []
    assert any("nombre completo" in e.value for e in at.error)


def test_ejemplos_y_limpiar(api: list[dict[str, Any]]) -> None:
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button(key="ej_cronica").click().run()
    assert at.text_input(key="nombre").value == "Jorge Salazar Mena"
    assert at.number_input(key="temperatura").value == 36.8
    at.button(key="limpiar").click().run()
    assert at.text_input(key="nombre").value == ""
    assert at.number_input(key="temperatura").value is None


def test_errores_de_la_api(monkeypatch: pytest.MonkeyPatch) -> None:
    def caida(*a: Any, **k: Any) -> Any:
        raise client.ApiUnavailableError("No se pudo conectar con la API (http://api:8000).")

    def rechaza(*a: Any, **k: Any) -> Any:
        raise client.ApiValidationError(["temperatura: fuera de rango"])

    monkeypatch.setattr(client, "consultas", caida)
    monkeypatch.setattr(client, "predecir", caida)
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert any("historial" in w.value for w in at.warning)
    at.button(key="consultar").click().run()
    assert not at.exception and any("No se pudo conectar" in e.value for e in at.error)

    monkeypatch.setattr(client, "predecir", rechaza)
    at.button(key="consultar").click().run()
    assert any("fuera de rango" in e.value for e in at.error)

from typing import Any

from diagnostico_ui.estados import ESTADOS, obtener_estado
from diagnostico_ui.render import (
    footer_html,
    formato_fecha,
    formato_temperatura,
    hero_html,
    historial_html,
    resultado_html,
    resultado_vacio_html,
)

CONSULTA: dict[str, Any] = {
    "id": "C-0007",
    "fecha": "2026-11-05T18:30:00+00:00",
    "nombre": "Ana <b>Gómez</b>",
    "temperatura": 39.0,
    "sintomas": [{"descripcion": "Tos", "intensidad": 8, "duracion_dias": 3}],
    "estado": "ENFERMEDAD AGUDA",
    "regla": "Intensidad ≥ 7 & menos de 30 días",
    "resumen": {"cantidad_sintomas": 1, "intensidad_maxima": 8, "duracion_maxima_dias": 3},
    "version_modelo": "simulado-0.1.0",
    "aviso": "Solo didáctico.",
}


def test_estados_cubren_los_cuatro_y_tienen_neutro() -> None:
    assert set(ESTADOS) == {
        "NO ENFERMO", "ENFERMEDAD LEVE", "ENFERMEDAD AGUDA", "ENFERMEDAD CRÓNICA",
    }  # fmt: skip
    assert obtener_estado("OTRO").clase == "neutro"


def test_resultado_incluye_estado_clase_regla_y_escapa() -> None:
    html = resultado_html(CONSULTA)
    assert "ENFERMEDAD AGUDA" in html and "dx-estado-aguda" in html
    assert "Intensidad ≥ 7 &amp; menos de 30 días" in html
    assert "Ana &lt;b&gt;Gómez&lt;/b&gt;" in html and "<b>" not in html
    assert "39,0 °C" in html and "C-0007" in html and "simulado-0.1.0" in html
    assert "Solo didáctico." in html


def test_resultado_vacio_y_pie_y_cabecera() -> None:
    assert "Aún no hay una consulta" in resultado_vacio_html()
    pie = footer_html()
    assert "Maestría en Inteligencia Artificial Aplicada" in pie and "Alexander Amdor" in pie
    assert "Apoyo a la decisión médica" in hero_html()


def test_historial_tabla_y_vacio() -> None:
    html = historial_html([CONSULTA])
    assert "dx-estado-aguda" in html and "2026-11-05 18:30" in html and "&lt;b&gt;" in html
    assert "Sin consultas" in historial_html([])


def test_formatos_tolerantes() -> None:
    assert formato_temperatura(36.5) == "36,5"
    assert formato_temperatura(None) == "—"
    assert formato_fecha("no es fecha") == "no es fecha"
    assert formato_fecha(None) == ""

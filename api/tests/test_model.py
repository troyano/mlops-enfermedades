import pytest

from diagnostico_api.model import predecir
from diagnostico_api.schemas import EstadoSalud, Sintoma


def s(intensidad: int, dias: int, desc: str = "Síntoma") -> Sintoma:
    return Sintoma(descripcion=desc, intensidad=intensidad, duracion_dias=dias)


CASOS = [
    (36.5, [], EstadoSalud.NO_ENFERMO),
    (37.0, [s(2, 2), s(1, 2)], EstadoSalud.LEVE),
    (39.0, [s(8, 3), s(7, 3), s(6, 2), s(5, 2)], EstadoSalud.AGUDA),
    (36.8, [s(3, 45)], EstadoSalud.CRONICA),
    (37.0, [s(9, 15)], EstadoSalud.AGUDA),
    (38.0, [], EstadoSalud.LEVE),
    (38.5, [s(1, 1)], EstadoSalud.AGUDA),
    (37.0, [s(9, 30)], EstadoSalud.CRONICA),
    (37.5, [], EstadoSalud.LEVE),
    (37.0, [s(6, 29)], EstadoSalud.LEVE),
]


@pytest.mark.parametrize(("temp", "sintomas", "esperado"), CASOS)
def test_estados(temp: float, sintomas: list[Sintoma], esperado: EstadoSalud) -> None:
    assert predecir(temp, sintomas).estado == esperado


def test_resumen_y_regla() -> None:
    r = predecir(39.0, [s(8, 3), s(4, 10)])
    assert (r.resumen.cantidad_sintomas, r.resumen.intensidad_maxima) == (2, 8)
    assert r.resumen.duracion_maxima_dias == 10
    assert "Intensidad" in r.regla


def test_regla_sin_sintomas_con_fiebre() -> None:
    assert predecir(38.0, []).regla == "Temperatura elevada sin síntomas reportados"

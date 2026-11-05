import math

from diagnostico_ui.validation import (
    limpiar_filas,
    validar_consulta,
    validar_nombre,
    validar_sintoma,
    validar_temperatura,
)

NAN = math.nan


def fila(d: object = "Tos", i: object = 3, dias: object = 2) -> dict[str, object]:
    return {"descripcion": d, "intensidad": i, "duracion_dias": dias}


def test_nombre() -> None:
    assert validar_nombre("Ana Gómez") is None
    assert validar_nombre("  Ana   Gómez  ") is None
    assert validar_nombre("Ana") is not None
    assert validar_nombre("") is not None and validar_nombre(None) is not None
    assert validar_nombre("A B") is not None  # menos de 5 caracteres
    assert "120" in (validar_nombre("Ana " + "x" * 120) or "")


def test_temperatura() -> None:
    assert validar_temperatura(36.5) is None
    assert validar_temperatura(35.0) is None and validar_temperatura(42.0) is None
    assert validar_temperatura(None) == "Indica la temperatura."
    assert validar_temperatura(NAN) == "Indica la temperatura."
    assert "35,0 y 42,0" in (validar_temperatura(42.1) or "")
    assert validar_temperatura(34.9) is not None


def test_sintoma_limites() -> None:
    assert validar_sintoma(fila()) is None
    assert validar_sintoma(fila(i=0, dias=0)) is None
    assert validar_sintoma(fila(i=10, dias=3650)) is None
    assert "Describe" in (validar_sintoma(fila(d="x")) or "")
    assert "Describe" in (validar_sintoma(fila(d="x" * 81)) or "")
    assert "intensidad" in (validar_sintoma(fila(i=11)) or "")
    assert "intensidad" in (validar_sintoma(fila(i=2.5)) or "")
    assert "intensidad" in (validar_sintoma(fila(i=None)) or "")
    assert "días" in (validar_sintoma(fila(dias=-1)) or "")
    assert "días" in (validar_sintoma(fila(dias=3651)) or "")
    assert validar_sintoma(fila(i=True)) is not None


def test_limpiar_filas_descarta_vacias_y_nan() -> None:
    filas = limpiar_filas([fila(None, NAN, None), fila("  ", None, ""), fila("Tos", 3.0, NAN)])
    assert filas == [{"descripcion": "Tos", "intensidad": 3.0, "duracion_dias": None}]


def test_consulta_valida_construye_payload() -> None:
    r = validar_consulta(" Ana  Gómez ", 38.5, [fila("Tos ", 3.0, 2.0), fila(None, NAN, NAN)])
    assert r.ok
    assert r.payload == {
        "nombre": "Ana Gómez",
        "temperatura": 38.5,
        "sintomas": [{"descripcion": "Tos", "intensidad": 3, "duracion_dias": 2}],
    }


def test_consulta_sin_sintomas_es_valida() -> None:
    r = validar_consulta("Ana Gómez", 36.5, [])
    assert r.ok and r.payload is not None and r.payload["sintomas"] == []


def test_consulta_acumula_errores_con_posicion() -> None:
    r = validar_consulta("Ana", None, [fila(), fila(i=11), fila(d=None)])
    assert not r.ok and r.payload is None
    assert any("nombre completo" in e for e in r.errores)
    assert "Indica la temperatura." in r.errores
    assert any(e.startswith("Síntoma 2:") for e in r.errores)
    assert any(e.startswith("Síntoma 3:") for e in r.errores)
    assert not any(e.startswith("Síntoma 1:") for e in r.errores)


def test_maximo_20_sintomas() -> None:
    r = validar_consulta("Ana Gómez", 36.5, [fila() for _ in range(21)])
    assert any("20" in e for e in r.errores)
    assert validar_consulta("Ana Gómez", 36.5, [fila() for _ in range(20)]).ok

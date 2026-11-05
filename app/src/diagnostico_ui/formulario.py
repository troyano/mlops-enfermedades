"""Estado del formulario de consulta (sin dependencias de la interfaz)."""

from collections.abc import Sequence
from typing import Any

import pandas as pd

from diagnostico_ui.contenido import EJEMPLOS, Ejemplo
from diagnostico_ui.validation import CAMPOS


def tabla_sintomas(filas: Sequence[tuple[str, int, int]] = ()) -> pd.DataFrame:
    """DataFrame con las columnas de la tabla de síntomas."""
    df = pd.DataFrame(list(filas), columns=pd.Index(CAMPOS))
    return df.astype({"descripcion": "object", "intensidad": "float64", "duracion_dias": "float64"})


def ejemplo_por_clave(clave: str) -> Ejemplo:
    return next(e for e in EJEMPLOS if e.clave == clave)


def estado_inicial() -> dict[str, Any]:
    ejemplo = ejemplo_por_clave("aguda")
    return {
        "nombre": ejemplo.nombre,
        "temperatura": ejemplo.temperatura,
        "sintomas": tabla_sintomas(ejemplo.sintomas),
        "editor_version": 0,
        "resultado": None,
        "errores": [],
        "error_api": None,
    }

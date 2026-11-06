"""Validación de la consulta en el cliente (mismos límites que la API)."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

NOMBRE_MIN, NOMBRE_MAX = 5, 120
TEMP_MIN, TEMP_MAX = 35.0, 42.0
MAX_SINTOMAS = 20
DESC_MIN, DESC_MAX = 2, 80
INTENSIDAD_MIN, INTENSIDAD_MAX = 0, 10
DIAS_MIN, DIAS_MAX = 0, 3650

CAMPOS = ("descripcion", "intensidad", "duracion_dias")


@dataclass(frozen=True)
class Validacion:
    """Resultado: `payload` listo para enviar, o `errores` en español."""

    payload: dict[str, Any] | None
    errores: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errores


def _vacio(valor: Any) -> bool:
    if valor is None:
        return True
    if isinstance(valor, float) and valor != valor:  # NaN
        return True
    return isinstance(valor, str) and not valor.strip()


def limpiar_filas(registros: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Descarta filas totalmente vacías y convierte NaN/"" en None."""
    filas: list[dict[str, Any]] = []
    for registro in registros:
        fila = {c: (None if _vacio(registro.get(c)) else registro.get(c)) for c in CAMPOS}
        if any(v is not None for v in fila.values()):
            filas.append(fila)
    return filas


def _entero(valor: Any) -> int | None:
    """Devuelve el entero si `valor` es numérico y entero; si no, None."""
    if isinstance(valor, bool):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return int(numero) if numero == numero and numero.is_integer() else None


def normalizar_nombre(nombre: str | None) -> str:
    return " ".join((nombre or "").split())


def validar_nombre(nombre: str | None) -> str | None:
    limpio = normalizar_nombre(nombre)
    if len(limpio) > NOMBRE_MAX:
        return f"El nombre admite como máximo {NOMBRE_MAX} caracteres."
    if len(limpio) < NOMBRE_MIN or len(limpio.split(" ")) < 2:
        return "Escribe el nombre completo: nombre y al menos un apellido."
    return None


def validar_temperatura(temperatura: float | None) -> str | None:
    if temperatura is None or temperatura != temperatura:
        return "Indica la temperatura."
    if not TEMP_MIN <= temperatura <= TEMP_MAX:
        return "La temperatura debe estar entre 35,0 y 42,0 °C."
    return None


def validar_sintoma(fila: Mapping[str, Any]) -> str | None:
    descripcion = fila.get("descripcion")
    if not isinstance(descripcion, str) or not DESC_MIN <= len(descripcion.strip()) <= DESC_MAX:
        return f"Describe el síntoma ({DESC_MIN} a {DESC_MAX} caracteres)."
    intensidad = _entero(fila.get("intensidad"))
    if intensidad is None or not INTENSIDAD_MIN <= intensidad <= INTENSIDAD_MAX:
        return "La intensidad es un número entero de 0 a 10."
    dias = _entero(fila.get("duracion_dias"))
    if dias is None or not DIAS_MIN <= dias <= DIAS_MAX:
        return "Los días son un número entero de 0 a 3650."
    return None


def validar_consulta(
    nombre: str | None,
    temperatura: float | None,
    registros: Iterable[Mapping[str, Any]],
) -> Validacion:
    """Valida la consulta completa y construye el cuerpo para POST /predecir."""
    errores: list[str] = []
    for error in (validar_nombre(nombre), validar_temperatura(temperatura)):
        if error:
            errores.append(error)
    filas = limpiar_filas(registros)
    if len(filas) > MAX_SINTOMAS:
        errores.append(f"Se admiten como máximo {MAX_SINTOMAS} síntomas.")
    for posicion, fila in enumerate(filas, start=1):
        error = validar_sintoma(fila)
        if error:
            errores.append(f"Síntoma {posicion}: {error}")
    if errores or temperatura is None:
        return Validacion(None, errores)
    sintomas = [
        {
            "descripcion": str(f["descripcion"]).strip(),
            "intensidad": _entero(f["intensidad"]),
            "duracion_dias": _entero(f["duracion_dias"]),
        }
        for f in filas
    ]
    payload = {
        "nombre": normalizar_nombre(nombre),
        "temperatura": float(temperatura),
        "sintomas": sintomas,
    }
    return Validacion(payload, [])

"""Textos fijos y ejemplos de la interfaz."""

from dataclasses import dataclass

TITULO = "Apoyo a la decisión médica"
AVISO = (
    "Las reglas son una simulación. La clasificación no demuestra que una persona "
    "esté enferma ni permite descartar una enfermedad."
)
PIE_LINEAS = (
    "<strong>ICESI</strong> · Facultad Barberi de Ingeniería, Diseño y Ciencias Aplicadas · "
    "Programa Maestría en Inteligencia Artificial Aplicada",
    "Materia: Machine Learning Operations – MLOps · 262 · 2026-II",
    "Integrantes: Eduar Troyano Velasquez · Alexander Amdor",
)
PIE_NOTA = "Proyecto académico con datos simulados. No es una herramienta clínica."


@dataclass(frozen=True)
class Ejemplo:
    clave: str
    etiqueta: str
    nombre: str
    temperatura: float
    sintomas: tuple[tuple[str, int, int], ...]


EJEMPLOS: tuple[Ejemplo, ...] = (
    Ejemplo("no", "No enfermo", "Laura Martínez Gil", 36.5, ()),
    Ejemplo(
        "leve",
        "Leve",
        "Carlos Pérez Ríos",
        37.0,
        (("Congestión nasal", 2, 2), ("Estornudos", 1, 2)),
    ),
    Ejemplo(
        "aguda",
        "Aguda",
        "Marta Ospina Cruz",
        39.0,
        (
            ("Dolor de cabeza", 8, 3),
            ("Fiebre alta", 7, 3),
            ("Dolor muscular", 6, 2),
            ("Escalofríos", 5, 2),
        ),
    ),
    Ejemplo("cronica", "Crónica", "Jorge Salazar Mena", 36.8, (("Dolor articular", 3, 45),)),
)

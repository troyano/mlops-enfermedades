"""Estados devueltos por la API y su presentación."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Estado:
    nombre: str
    clase: str  # sufijo de la clase CSS (ver static/styles.css)


ESTADOS: dict[str, Estado] = {
    "NO ENFERMO": Estado("NO ENFERMO", "no"),
    "ENFERMEDAD LEVE": Estado("ENFERMEDAD LEVE", "leve"),
    "ENFERMEDAD AGUDA": Estado("ENFERMEDAD AGUDA", "aguda"),
    "ENFERMEDAD CRÓNICA": Estado("ENFERMEDAD CRÓNICA", "cronica"),
}


def obtener_estado(nombre: str) -> Estado:
    """Devuelve el estado conocido o uno neutro si la API envía otro texto."""
    return ESTADOS.get(nombre, Estado(nombre, "neutro"))

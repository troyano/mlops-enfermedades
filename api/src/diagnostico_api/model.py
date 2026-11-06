"""Función predecir() simulada: reglas didácticas, sin modelo entrenado."""

from collections.abc import Sequence

from diagnostico_api.schemas import EstadoSalud, Resultado, Resumen, Sintoma

VERSION_MODELO = "simulado-0.1.0"
AVISO = (
    "Reglas didácticas: la clasificación no demuestra que una persona esté enferma "
    "ni permite descartar una enfermedad."
)


def predecir(temperatura: float, sintomas: Sequence[Sintoma]) -> Resultado:
    """Clasifica según la primera regla que se cumpla."""
    n = len(sintomas)
    mi = max((s.intensidad for s in sintomas), default=0)
    md = max((s.duracion_dias for s in sintomas), default=0)

    if n == 0 and temperatura < 37.5:
        estado, regla = EstadoSalud.NO_ENFERMO, "Sin síntomas y temperatura menor a 37,5 °C"
    elif n > 0 and md >= 30:
        estado, regla = EstadoSalud.CRONICA, "Hay síntomas con 30 días o más de duración"
    elif n > 0 and (mi >= 7 or temperatura >= 38.5):
        estado = EstadoSalud.AGUDA
        regla = "Intensidad de 7 o más, o temperatura de 38,5 °C o más, con menos de 30 días"
    elif n == 0:
        estado, regla = EstadoSalud.LEVE, "Temperatura elevada sin síntomas reportados"
    else:
        estado, regla = EstadoSalud.LEVE, "Ningún criterio de gravedad: síntomas leves"

    return Resultado(
        estado=estado,
        regla=regla,
        resumen=Resumen(cantidad_sintomas=n, intensidad_maxima=mi, duracion_maxima_dias=md),
    )

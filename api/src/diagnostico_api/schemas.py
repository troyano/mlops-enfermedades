"""Modelos Pydantic de entrada y salida."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class EstadoSalud(StrEnum):
    """Estados posibles de la función simulada."""

    NO_ENFERMO = "NO ENFERMO"
    LEVE = "ENFERMEDAD LEVE"
    AGUDA = "ENFERMEDAD AGUDA"
    CRONICA = "ENFERMEDAD CRÓNICA"


class Sintoma(BaseModel):
    """Un síntoma reportado por el médico."""

    descripcion: Annotated[str, Field(min_length=2, max_length=80)]
    intensidad: Annotated[int, Field(ge=0, le=10)]
    duracion_dias: Annotated[int, Field(ge=0, le=3650)]

    @field_validator("descripcion", mode="before")
    @classmethod
    def _limpiar(cls, v: object) -> object:
        return " ".join(v.split()) if isinstance(v, str) else v


class ConsultaEntrada(BaseModel):
    """Cuerpo de POST /predecir."""

    nombre: str
    temperatura: Annotated[float, Field(ge=35.0, le=42.0)]
    sintomas: Annotated[list[Sintoma], Field(max_length=20)]

    @field_validator("nombre", mode="before")
    @classmethod
    def _normalizar_nombre(cls, v: object) -> object:
        return " ".join(v.split()) if isinstance(v, str) else v

    @field_validator("nombre")
    @classmethod
    def _validar_nombre(cls, v: str) -> str:
        if len(v) < 5 or len(v) > 120:
            raise ValueError("El nombre debe tener entre 5 y 120 caracteres.")
        if len(v.split(" ")) < 2:
            raise ValueError("Escribe el nombre y al menos un apellido.")
        return v


class Resumen(BaseModel):
    cantidad_sintomas: int
    intensidad_maxima: int
    duracion_maxima_dias: int


class Resultado(BaseModel):
    """Salida de la función simulada."""

    estado: EstadoSalud
    regla: str
    resumen: Resumen


class Consulta(BaseModel):
    """Consulta guardada y devuelta por la API."""

    id: str
    fecha: datetime
    nombre: str
    temperatura: float
    sintomas: list[Sintoma]
    estado: EstadoSalud
    regla: str
    resumen: Resumen
    version_modelo: str
    aviso: str

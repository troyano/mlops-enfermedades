"""Creación de la app FastAPI y rutas."""

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from diagnostico_api.config import Settings, get_settings
from diagnostico_api.model import AVISO, VERSION_MODELO, predecir
from diagnostico_api.schemas import Consulta, ConsultaEntrada
from diagnostico_api.storage import ConsultaStorage


def _mensaje(err: dict[str, Any]) -> str:
    """Traduce los errores estándar de Pydantic a mensajes claros en español."""
    tipo = str(err.get("type", ""))
    ctx = err.get("ctx") or {}
    campo = str(err["loc"][-1]) if err.get("loc") else "campo"
    if tipo == "missing":
        return f"Falta el campo «{campo}»."
    if tipo in ("greater_than_equal", "less_than_equal"):
        lim = ctx.get("ge", ctx.get("le"))
        return f"«{campo}» debe ser {'mayor' if tipo.startswith('g') else 'menor'} o igual a {lim}."
    if tipo == "string_too_short":
        return f"«{campo}» debe tener al menos {ctx.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"«{campo}» admite como máximo {ctx.get('max_length')} caracteres."
    if tipo == "too_long":
        return f"«{campo}» admite como máximo {ctx.get('max_length')} elementos."
    if tipo in ("int_parsing", "int_from_float", "int_type"):
        return f"«{campo}» debe ser un número entero."
    if tipo in ("float_parsing", "float_type"):
        return f"«{campo}» debe ser un número."
    if tipo == "value_error":
        return str(err.get("msg", "")).removeprefix("Value error, ")
    if tipo == "json_invalid":
        return "El cuerpo de la solicitud no es un JSON válido."
    return str(err.get("msg", "Valor no válido."))


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)
    storage = ConsultaStorage(settings.data_dir)

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        detail = [
            {"loc": list(e["loc"]), "msg": _mensaje(dict(e)), "type": e["type"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.get("/health", tags=["salud"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.version}

    @app.post("/predecir", tags=["consultas"], response_model=Consulta)
    def post_predecir(entrada: ConsultaEntrada) -> Consulta:
        resultado = predecir(entrada.temperatura, entrada.sintomas)

        def construir(id_: str) -> Consulta:
            return Consulta(
                id=id_,
                fecha=datetime.now(UTC),
                nombre=entrada.nombre,
                temperatura=entrada.temperatura,
                sintomas=entrada.sintomas,
                estado=resultado.estado,
                regla=resultado.regla,
                resumen=resultado.resumen,
                version_modelo=VERSION_MODELO,
                aviso=AVISO,
            )

        return storage.add(construir)

    @app.get("/consultas", tags=["consultas"], response_model=list[Consulta])
    def get_consultas(limite: Annotated[int, Query(ge=1, le=1000)] = 100) -> list[Consulta]:
        return storage.list(limite)

    return app


app = create_app()

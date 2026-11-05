"""Creación de la app FastAPI y rutas."""

from fastapi import FastAPI

from diagnostico_api.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)

    @app.get("/health", tags=["salud"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.version}

    return app


app = create_app()

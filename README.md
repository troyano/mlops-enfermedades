# mlops-enfermedades

Servicio de apoyo al médico que, a partir de síntomas del paciente, devuelve un estado simulado:
**NO ENFERMO**, **ENFERMEDAD LEVE**, **ENFERMEDAD AGUDA** o **ENFERMEDAD CRÓNICA**.
No hay un modelo entrenado: una función con reglas simula el modelo (Semanas 1-2 de MLOps).

## Estructura

| Ruta | Contenido |
|---|---|
| `api/` | Microservicio FastAPI (`diagnostico_api`), puerto 8000 |
| `app/` | Interfaz web Streamlit (`diagnostico_ui`), puerto 8501 |
| `docs/` | Documento del pipeline de MLOps (parte 1) |
| `docker-compose.yml`, `Makefile`, `.env.example` | Entorno reproducible y atajos |

## Requisitos

Docker con Compose. Para desarrollo sin contenedores: [uv](https://docs.astral.sh/uv/).

## Ejecución con Docker Compose (recomendada)

```bash
docker compose up --build -d
```

- Interfaz para el médico: http://localhost:8501
- API y documentación Swagger: http://localhost:8000/docs
- Verificar la API: `curl http://localhost:8000/health`
- Detener: `docker compose down`

## Cada servicio por separado

### API

```bash
docker build -t diagnostico-api ./api
docker run --rm -p 8000:8000 diagnostico-api
```

### Interfaz

La interfaz necesita alcanzar la API. Con la API ya publicada en el puerto 8000 del equipo anfitrión:

```bash
docker build -t diagnostico-ui ./app
docker run --rm -p 8501:8501 -e API_URL=http://host.docker.internal:8000 \
  --add-host=host.docker.internal:host-gateway diagnostico-ui
```

## Cómo obtener una respuesta

TODO (se completa con la función de predicción): ejemplo con `curl` a `POST /predecir` y uso del formulario.

## Desarrollo

```bash
make lint        # ruff
make typecheck   # mypy estricto
make test        # pytest
```

## Variables de entorno

Ver `.env.example`.

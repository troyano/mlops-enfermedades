# mlops-enfermedades

Servicio de apoyo al médico que, a partir de síntomas del paciente, devuelve un estado simulado:
NO ENFERMO, ENFERMEDAD LEVE, ENFERMEDAD AGUDA o ENFERMEDAD CRÓNICA. Proyecto de MLOps (Semanas 1-2).

## Estructura

- `api/`: microservicio FastAPI (`diagnostico_api`).
- `app/`: interfaz Streamlit (pendiente).
- `docs/`: documento del pipeline de MLOps (pendiente).
- `docker-compose.yml`, `Makefile`, `.env.example`.

## Desarrollo

`make lint`, `make typecheck`, `make test` (requiere [uv](https://docs.astral.sh/uv/)).

## Construir y ejecutar

TODO: `docker build` y `docker run` por servicio, y `docker compose up`.

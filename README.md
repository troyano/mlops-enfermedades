# mlops-enfermedades

Servicio de apoyo al médico que, a partir de síntomas del paciente, devuelve un estado simulado:
**NO ENFERMO**, **ENFERMEDAD LEVE**, **ENFERMEDAD AGUDA** o **ENFERMEDAD CRÓNICA**.
No hay un modelo entrenado: una función con reglas simula el modelo (Semanas 1-2 de MLOps).

## Objetivo del taller

Este repositorio es la entrega del taller **Semanas 1-2: Pipeline de MLOps + imagen de Docker**.

El problema que plantea el docente: en medicina existe abundante información de los pacientes, pero
para las enfermedades poco comunes, llamadas huérfanas, los datos escasean. Se requiere un modelo que,
a partir de los síntomas de un paciente, prediga si es posible que sufra alguna enfermedad, tanto
común (muchos datos) como huérfana (pocos datos).

El taller tiene dos partes, cada una con el 50 % de la unidad:

1. **Pipeline de MLOps:** proponer el proceso completo end-to-end (diseño, desarrollo y producción)
   para construir ese modelo, con un diagrama general y la explicación de cada etapa.
2. **Imagen de Docker:** construir un servicio que el médico pueda correr en su propio equipo. Una
   función simulada recibe por lo menos 3 valores y devuelve uno de cuatro estados: **NO ENFERMO**,
   **ENFERMEDAD LEVE**, **ENFERMEDAD AGUDA** o **ENFERMEDAD CRÓNICA**.

## Dónde está cada entregable

| Requisito del taller | Dónde está |
|---|---|
| **Parte 1:** pipeline de MLOps (diagrama general y explicación de etapas) | [`docs/brief.md`](docs/brief.md) |
| **Parte 2:** función simulada con los 4 estados | [`api/src/diagnostico_api/model.py`](api/src/diagnostico_api/model.py), función `predecir()` |
| **Parte 2:** Dockerfile | [`api/Dockerfile`](api/Dockerfile) (API) y [`app/Dockerfile`](app/Dockerfile) (interfaz) |
| **Parte 2:** forma de recibir los datos del médico | Página web en Streamlit (puerto 8501) y punto final `POST /predecir` en FastAPI (puerto 8000) |
| **Parte 2:** README con construcción, ejecución y cómo obtener respuestas | Este documento |
| **Parte 2:** extras | `docker-compose.yml`, historial de consultas, pruebas en `api/tests/` y `app/tests/`, diseño de la interfaz en [`docs/interfaz.md`](docs/interfaz.md) |

## Estructura

| Ruta | Contenido |
|---|---|
| `api/` | Microservicio FastAPI (`diagnostico_api`), puerto 8000 |
| `app/` | Interfaz web Streamlit (`diagnostico_ui`), puerto 8501 |
| `docs/` | Pipeline de MLOps (`brief.md`, parte 1) y diseño de la interfaz (`interfaz.md`, con prototipo) |
| `CONTRIBUTING.md` | Flujo de ramas y commits |
| `docker-compose.yml`, `Makefile`, `.env.example` | Entorno reproducible y atajos |

## Requisitos

Docker con Compose. Para desarrollo sin contenedores: [uv](https://docs.astral.sh/uv/).

En Windows, Docker Desktop necesita WSL 2. Si al abrirlo aparece "WSL not installed", ejecuta
`wsl --install --no-distribution` en PowerShell como administrador, reinicia el equipo y abre Docker
Desktop hasta que diga **Engine running**.

Los comandos de varias líneas de este README usan la sintaxis de bash (`\` para partir líneas y
comillas simples). En Windows, ejecútalos en Git Bash o WSL. Para probar la API sin `curl`, usa
Swagger en http://localhost:8000/docs.

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
docker run --rm -p 8000:8000 -v consultas:/data diagnostico-api
```

### Interfaz

La interfaz necesita alcanzar la API. Con la API ya publicada en el puerto 8000 del equipo anfitrión:

```bash
docker build -t diagnostico-ui ./app
docker run --rm -p 8501:8501 -e API_URL=http://host.docker.internal:8000 \
  --add-host=host.docker.internal:host-gateway diagnostico-ui
```

## Cómo obtener una respuesta

### Desde el navegador

Abre http://localhost:8501, escribe el nombre del paciente, la temperatura y agrega los síntomas
(descripción, intensidad de 0 a 10 y días). También puedes usar Swagger en http://localhost:8000/docs.

### Con `curl`

`POST /predecir` recibe `nombre`, `temperatura` (35,0 a 42,0 °C) y una lista de `sintomas`
(`descripcion` de 2 a 80 caracteres, `intensidad` entera de 0 a 10, `duracion_dias` entera de 0 a 3650;
máximo 20 síntomas).

```bash
# NO ENFERMO
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Laura Martínez Gil","temperatura":36.5,"sintomas":[]}'

# ENFERMEDAD LEVE
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Carlos Pérez Ríos","temperatura":37.0,"sintomas":[
        {"descripcion":"Congestión nasal","intensidad":2,"duracion_dias":2},
        {"descripcion":"Estornudos","intensidad":1,"duracion_dias":2}]}'

# ENFERMEDAD AGUDA
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Marta Ospina Cruz","temperatura":39.0,"sintomas":[
        {"descripcion":"Dolor de cabeza","intensidad":8,"duracion_dias":3},
        {"descripcion":"Fiebre alta","intensidad":7,"duracion_dias":3}]}'

# ENFERMEDAD CRÓNICA
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Jorge Salazar Mena","temperatura":36.8,"sintomas":[
        {"descripcion":"Dolor articular","intensidad":3,"duracion_dias":45}]}'
```

La respuesta incluye `id`, `fecha`, `estado`, `regla` (la regla aplicada), `resumen`,
`version_modelo` y un `aviso` didáctico.

La función `predecir()` usa la temperatura y, de la lista de síntomas, la cantidad, la intensidad
máxima y la duración máxima en días. Reglas, evaluadas en orden (la primera que se cumple):

1. **NO ENFERMO:** sin síntomas y temperatura menor a 37,5 °C.
2. **ENFERMEDAD CRÓNICA:** hay síntomas y alguno dura 30 días o más.
3. **ENFERMEDAD AGUDA:** hay síntomas y (intensidad máxima de 7 o más, o temperatura de 38,5 °C o más).
4. **ENFERMEDAD LEVE:** cualquier otro caso.

Si los datos no son válidos, la API responde `422` con mensajes en español:

```bash
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","temperatura":50,"sintomas":[]}'
# {"detail":[{"loc":["body","nombre"],"msg":"El nombre debe tener entre 5 y 120 caracteres.", ...},
#            {"loc":["body","temperatura"],"msg":"«temperatura» debe ser menor o igual a 42.0.", ...}]}
```

### Historial y persistencia

Cada consulta se guarda en `/data/consultas.json` dentro del contenedor de la API, y
`GET /consultas?limite=100` las devuelve, las más recientes primero.

La persistencia **requiere un volumen**: sin él, los datos se pierden al eliminar el contenedor.
Con Compose el volumen `consultas` ya está configurado. Con `docker run`:

```bash
docker run --rm -p 8000:8000 -v consultas:/data diagnostico-api
```

El historial contiene nombres de pacientes: usa solo datos ficticios en la demostración.

## Desarrollo

```bash
make lint        # ruff
make typecheck   # mypy estricto
make test        # pytest
```

## Variables de entorno

Ver `.env.example`.

## Flujo de ramas

`feature/*` → `dev` → `stage` → `main`, con etiqueta por versión. Detalle en [CONTRIBUTING.md](CONTRIBUTING.md).

## Autores

Eduar Troyano Velasquez y Alexander Amador. Maestría en Inteligencia Artificial Aplicada, ICESI. Materia: Machine Learning Operations – MLOps, 2026-II.

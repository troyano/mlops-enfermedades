# Flujo de ramas y contribución

## Ramas

```
feature/*  ──PR──►  dev  ──PR──►  stage  ──PR──►  main  ── etiqueta vX.Y.Z
(trabajo)        (integración)  (validación)    (entrega)
```

| Rama | Propósito | Quién escribe en ella | Regla |
|---|---|---|---|
| `main` | Versión entregable. Siempre arranca con Docker | Solo PR desde `stage` | Protegida: exige PR, sin push directo. Cada entrega lleva una etiqueta |
| `stage` | Candidato a entrega: el equipo clona, ejecuta `docker compose up` y revisa el README | Solo PR desde `dev` | Solo se corrige lo que falle en la validación |
| `dev` | Integración y pulido conjunto | PR desde `feature/*` | Protegida: exige PR |
| `feature/*` | Una pieza de trabajo acotada | Su autor | Se borra al fusionar |

## Nombres de ramas de trabajo

`feature/<tema-corto>`, por ejemplo `feature/api-predecir` o `feature/app-formulario`. Para correcciones sobre `stage` se usa `fix/<tema-corto>` con PR a `stage` y luego a `dev`.

## Commits

Se usa [Conventional Commits](https://www.conventionalcommits.org/es/): `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, con un alcance opcional (`feat(api): ...`). Un commit por fase o cambio lógico.

## Antes de abrir un PR

```bash
make lint typecheck test
docker compose up --build -d   # api en :8000 y app en :8501 deben quedar healthy
docker compose down -v
```

## Liberar una versión

1. Validar en `dev` y abrir PR `dev` → `stage`.
2. El equipo revisa `stage` clonándolo en una carpeta limpia y siguiendo el README.
3. Abrir PR `stage` → `main`.
4. Etiquetar: `git tag v1.0.0 && git push origin v1.0.0`. GitHub genera el ZIP de esa etiqueta.

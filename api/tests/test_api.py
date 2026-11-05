from typing import Any

from fastapi.testclient import TestClient

BASE: dict[str, Any] = {"nombre": "Laura Martínez Gil", "temperatura": 36.5, "sintomas": []}


def sint(i: int = 5, d: int = 2, desc: str = "Tos seca") -> dict[str, Any]:
    return {"descripcion": desc, "intensidad": i, "duracion_dias": d}


def test_cuatro_estados(client: TestClient) -> None:
    casos = [
        (BASE, "NO ENFERMO"),
        ({**BASE, "temperatura": 37.0, "sintomas": [sint(2, 2), sint(1, 2)]}, "ENFERMEDAD LEVE"),
        (
            {
                **BASE,
                "temperatura": 39.0,
                "sintomas": [sint(8, 3), sint(7, 3), sint(6, 2), sint(5, 2)],
            },
            "ENFERMEDAD AGUDA",
        ),
        ({**BASE, "temperatura": 36.8, "sintomas": [sint(3, 45)]}, "ENFERMEDAD CRÓNICA"),
    ]
    for cuerpo, estado in casos:
        r = client.post("/predecir", json=cuerpo)
        assert r.status_code == 200
        assert r.json()["estado"] == estado


def test_respuesta_completa(client: TestClient) -> None:
    r = client.post("/predecir", json={**BASE, "nombre": "  Laura   Martínez  Gil "})
    data = r.json()
    assert data["id"] == "C-0001"
    assert data["nombre"] == "Laura Martínez Gil"
    assert data["version_modelo"] == "simulado-0.1.0"
    assert data["fecha"].endswith("Z") or "+00:00" in data["fecha"]
    assert data["resumen"] == {
        "cantidad_sintomas": 0,
        "intensidad_maxima": 0,
        "duracion_maxima_dias": 0,
    }
    assert "no demuestra" in data["aviso"]


def test_validaciones_422(client: TestClient) -> None:
    malos = [
        {**BASE, "nombre": "Ana"},
        {**BASE, "nombre": "Anastasia"},
        {**BASE, "nombre": "A" * 121 + " B"},
        {**BASE, "temperatura": 34.9},
        {**BASE, "temperatura": 42.1},
        {**BASE, "sintomas": [sint(11, 1)]},
        {**BASE, "sintomas": [sint(-1, 1)]},
        {**BASE, "sintomas": [sint(5, 3651)]},
        {**BASE, "sintomas": [sint(5, -1)]},
        {**BASE, "sintomas": [sint(5.5, 1)]},  # type: ignore[arg-type]
        {**BASE, "sintomas": [sint(5, 1, "x")]},
        {**BASE, "sintomas": [sint(5, 1, "x" * 81)]},
        {**BASE, "sintomas": [sint()] * 21},
        {"nombre": "Laura Gil"},
    ]
    for cuerpo in malos:
        r = client.post("/predecir", json=cuerpo)
        assert r.status_code == 422, cuerpo
        assert r.json()["detail"][0]["msg"]


def test_limites_validos(client: TestClient) -> None:
    cuerpo = {**BASE, "temperatura": 42.0, "sintomas": [sint(10, 3650)] * 20}
    assert client.post("/predecir", json=cuerpo).status_code == 200
    assert client.post("/predecir", json={**BASE, "temperatura": 35.0}).status_code == 200


def test_mensajes_en_espanol(client: TestClient) -> None:
    r = client.post("/predecir", json={**BASE, "nombre": "Ana"})
    assert (
        "al menos un apellido" in r.json()["detail"][0]["msg"]
        or "caracteres" in r.json()["detail"][0]["msg"]
    )
    r = client.post("/predecir", json={**BASE, "temperatura": 50})
    assert "42" in r.json()["detail"][0]["msg"]


def test_consultas_orden_y_persistencia(client: TestClient, tmp_path: Any) -> None:
    assert client.get("/consultas").json() == []
    client.post("/predecir", json=BASE)
    client.post("/predecir", json={**BASE, "nombre": "Carlos Pérez Ríos"})
    lista = client.get("/consultas").json()
    assert [c["id"] for c in lista] == ["C-0002", "C-0001"]
    assert client.get("/consultas?limite=1").json()[0]["id"] == "C-0002"
    assert (tmp_path / "consultas.json").exists()


def test_los_datos_sobreviven_a_otra_app(tmp_path: Any) -> None:
    from diagnostico_api.config import Settings
    from diagnostico_api.main import create_app

    a = TestClient(create_app(Settings(data_dir=tmp_path)))
    a.post("/predecir", json=BASE)
    b = TestClient(create_app(Settings(data_dir=tmp_path)))
    assert b.get("/consultas").json()[0]["id"] == "C-0001"
    assert b.post("/predecir", json=BASE).json()["id"] == "C-0002"


def test_directorio_inexistente_se_crea(tmp_path: Any) -> None:
    from diagnostico_api.config import Settings
    from diagnostico_api.main import create_app

    c = TestClient(create_app(Settings(data_dir=tmp_path / "nuevo" / "dir")))
    assert c.post("/predecir", json=BASE).status_code == 200

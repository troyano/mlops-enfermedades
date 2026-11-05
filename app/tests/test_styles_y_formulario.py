import tomllib
from pathlib import Path

from diagnostico_ui.contenido import EJEMPLOS
from diagnostico_ui.estados import ESTADOS
from diagnostico_ui.formulario import ejemplo_por_clave, estado_inicial, tabla_sintomas
from diagnostico_ui.styles import CSS_PATH, read_css
from diagnostico_ui.validation import validar_consulta

RAIZ = Path(__file__).parents[1]


def test_css_centralizado_define_todos_los_estados() -> None:
    css = read_css()
    assert CSS_PATH.name == "styles.css"
    for estado in ESTADOS.values():
        assert f".dx-estado-{estado.clase}" in css


def test_tema_streamlit() -> None:
    config = tomllib.loads((RAIZ / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert config["theme"]["base"] == "dark"
    assert config["theme"]["backgroundColor"] == "#0C0C14"


def test_ejemplos_son_validos_y_cubren_los_cuatro_casos() -> None:
    assert [e.clave for e in EJEMPLOS] == ["no", "leve", "aguda", "cronica"]
    for e in EJEMPLOS:
        tabla = tabla_sintomas(e.sintomas)
        assert validar_consulta(e.nombre, e.temperatura, tabla.to_dict("records")).ok


def test_estado_inicial_es_el_ejemplo_agudo() -> None:
    estado = estado_inicial()
    assert estado["nombre"] == ejemplo_por_clave("aguda").nombre
    assert len(estado["sintomas"]) == 4 and estado["resultado"] is None
    assert list(tabla_sintomas().columns) == ["descripcion", "intensidad", "duracion_dias"]

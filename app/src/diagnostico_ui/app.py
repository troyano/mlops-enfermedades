"""Interfaz Streamlit para el médico: consulta, resultado e historial."""

from typing import Any

import pandas as pd
import streamlit as st

from diagnostico_ui import client
from diagnostico_ui.config import get_api_url
from diagnostico_ui.contenido import EJEMPLOS
from diagnostico_ui.formulario import ejemplo_por_clave, estado_inicial, tabla_sintomas
from diagnostico_ui.render import (
    footer_html,
    hero_html,
    historial_html,
    resultado_html,
    resultado_vacio_html,
)
from diagnostico_ui.styles import inject_styles
from diagnostico_ui.validation import MAX_SINTOMAS, validar_consulta


def _cargar_ejemplo(clave: str) -> None:
    ejemplo = ejemplo_por_clave(clave)
    st.session_state.update(
        nombre=ejemplo.nombre,
        temperatura=ejemplo.temperatura,
        sintomas=tabla_sintomas(ejemplo.sintomas),
        editor_version=st.session_state.editor_version + 1,
        errores=[],
        error_api=None,
    )


def _limpiar() -> None:
    st.session_state.update(
        nombre="",
        temperatura=None,
        sintomas=tabla_sintomas(),
        editor_version=st.session_state.editor_version + 1,
        resultado=None,
        errores=[],
        error_api=None,
    )


def _consultar(sintomas: pd.DataFrame, api_url: str) -> None:
    ss = st.session_state
    validacion = validar_consulta(ss.nombre, ss.temperatura, sintomas.to_dict("records"))
    ss.errores, ss.error_api = list(validacion.errores), None
    if validacion.payload is None:
        return
    try:
        ss.resultado = client.predecir(api_url, validacion.payload)
    except client.ApiValidationError as exc:
        ss.errores = exc.messages
    except client.ApiError as exc:
        ss.error_api = str(exc)


def _formulario(api_url: str) -> None:
    ss = st.session_state
    with st.container(border=True):
        st.subheader("Nueva consulta")
        st.caption("Registra al paciente y sus síntomas. Sin síntomas, deja la tabla vacía.")
        c1, c2 = st.columns([2, 1])
        c1.text_input("Nombre completo del paciente", key="nombre", placeholder="Nombre y apellido")
        c2.number_input(
            "Temperatura (°C)", key="temperatura", value=None, step=0.1, format="%.1f",
            placeholder="36,5",
        )  # fmt: skip
        st.markdown(
            f'<div class="dx-label">Síntomas reportados (máx. {MAX_SINTOMAS})</div>',
            unsafe_allow_html=True,
        )
        sintomas = st.data_editor(
            ss.sintomas,
            key=f"editor_{ss.editor_version}",
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            column_config={
                "descripcion": st.column_config.TextColumn("Descripción", max_chars=80),
                "intensidad": st.column_config.NumberColumn(
                    "Intensidad (0–10)", min_value=0, max_value=10, step=1, format="%d"
                ),
                "duracion_dias": st.column_config.NumberColumn(
                    "Días", min_value=0, max_value=3650, step=1, format="%d"
                ),
            },
        )
        st.markdown('<div class="dx-label">Cargar un ejemplo</div>', unsafe_allow_html=True)
        cols = st.columns(len(EJEMPLOS))
        for col, e in zip(cols, EJEMPLOS, strict=True):
            col.button(
                e.etiqueta, key=f"ej_{e.clave}", on_click=_cargar_ejemplo, args=(e.clave,),
                width="stretch",
            )  # fmt: skip
        b1, b2 = st.columns(2)
        consultar = b1.button("Consultar", key="consultar", type="primary", width="stretch")
        b2.button("Limpiar formulario", key="limpiar", on_click=_limpiar, width="stretch")
        if consultar:
            _consultar(sintomas, api_url)
        if ss.errores:
            st.error("\n".join(f"- {m}" for m in ss.errores))
        if ss.error_api:
            st.error(ss.error_api)


def _resultado() -> None:
    st.subheader("Resultado")
    consulta: dict[str, Any] | None = st.session_state.resultado
    html = resultado_html(consulta) if consulta else resultado_vacio_html()
    st.markdown(html, unsafe_allow_html=True)


def _historial(api_url: str) -> None:
    with st.container(border=True):
        st.subheader("Historial de consultas")
        st.caption("Las más recientes primero. Se guardan en el servicio de la API.")
        try:
            consultas = client.consultas(api_url)
        except client.ApiError as exc:
            st.warning(f"No se pudo cargar el historial: {exc}")
            return
        st.markdown(historial_html(consultas), unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Apoyo a la decisión médica", page_icon="🩺", layout="wide")
    inject_styles()
    for clave, valor in estado_inicial().items():
        st.session_state.setdefault(clave, valor)
    api_url = get_api_url()
    st.markdown(hero_html(), unsafe_allow_html=True)
    izquierda, derecha = st.columns([1.35, 1], gap="large")
    with izquierda:
        _formulario(api_url)
    with derecha:
        _resultado()
    _historial(api_url)
    st.markdown(footer_html(), unsafe_allow_html=True)


main()

"""Página Streamlit mínima: estado de la API."""

import streamlit as st

from diagnostico_ui.client import ApiError, health
from diagnostico_ui.config import get_api_url


def main() -> None:
    st.set_page_config(page_title="Diagnóstico", page_icon="🩺")
    st.title("Diagnóstico simulado")
    url = get_api_url()
    try:
        data = health(url)
    except ApiError as exc:
        st.error(f"API no disponible en {url}: {exc}")
        return
    st.success(f"API conectada: {data}")


main()

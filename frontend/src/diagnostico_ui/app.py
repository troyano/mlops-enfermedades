"""Página Streamlit mínima: estado del backend."""

import streamlit as st

from diagnostico_ui.client import BackendError, health
from diagnostico_ui.config import get_backend_url


def main() -> None:
    st.set_page_config(page_title="Diagnóstico", page_icon="🩺")
    st.title("Diagnóstico simulado")
    url = get_backend_url()
    try:
        data = health(url)
    except BackendError as exc:
        st.error(f"Backend no disponible en {url}: {exc}")
        return
    st.success(f"Backend conectado: {data}")


main()

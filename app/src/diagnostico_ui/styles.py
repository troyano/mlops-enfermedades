"""Carga de la hoja de estilos centralizada."""

from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).parent / "static" / "styles.css"


def read_css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def inject_styles() -> None:
    """Único punto donde la app aplica `static/styles.css`."""
    st.markdown(f"<style>{read_css()}</style>", unsafe_allow_html=True)

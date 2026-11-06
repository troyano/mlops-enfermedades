"""Constructores de HTML para la interfaz (puros y escapados)."""

from collections.abc import Sequence
from datetime import datetime
from html import escape
from typing import Any

from diagnostico_ui.contenido import AVISO, PIE_LINEAS, PIE_NOTA, TITULO
from diagnostico_ui.estados import obtener_estado


def formato_temperatura(valor: Any) -> str:
    try:
        return f"{float(valor):.1f}".replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def formato_fecha(valor: Any) -> str:
    """Muestra la fecha ISO como `AAAA-MM-DD HH:MM`; si no se entiende, la deja igual."""
    texto = str(valor or "")
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return texto


def _e(valor: Any) -> str:
    return escape(str(valor if valor is not None else ""))


def hero_html() -> str:
    return (
        '<header class="dx-hero">'
        '<div class="dx-hero-a"><div class="dx-eyebrow">MLOps · Semanas 1 y 2</div>'
        f"<h1>{_e(TITULO)}</h1>"
        "<p>Registra los síntomas del paciente y obtén un estado simulado: no enfermo, "
        "leve, agudo o crónico.</p></div>"
        '<div class="dx-hero-b"><strong>Uso didáctico</strong>'
        f"<span>{_e(AVISO)}</span></div></header>"
    )


def footer_html() -> str:
    lineas = "<br>".join(PIE_LINEAS)  # contenido fijo del proyecto, no entrada del usuario
    return f'<footer class="dx-footer">{lineas}<div class="dx-proto">{_e(PIE_NOTA)}</div></footer>'


def resultado_vacio_html() -> str:
    return (
        '<div class="dx-empty">Aún no hay una consulta. Completa el formulario o carga un '
        "ejemplo y pulsa Consultar.</div>"
    )


def resultado_html(consulta: dict[str, Any]) -> str:
    estado = obtener_estado(str(consulta.get("estado", "")))
    resumen = consulta.get("resumen") or {}
    aviso = consulta.get("aviso") or AVISO
    datos = (
        ("Síntomas", resumen.get("cantidad_sintomas", len(consulta.get("sintomas") or []))),
        ("Intensidad máx.", resumen.get("intensidad_maxima", "—")),
        ("Días máx.", resumen.get("duracion_maxima_dias", "—")),
        ("Temperatura", f"{formato_temperatura(consulta.get('temperatura'))} °C"),
    )
    hechos = "".join(f"<div><dt>{_e(k)}</dt><dd>{_e(v)}</dd></div>" for k, v in datos)
    return (
        '<div class="dx-res">'
        f'<div class="dx-res-top dx-estado-{estado.clase}"><small>Estado simulado</small>'
        f"<h3>{_e(estado.nombre)}</h3><p>{_e(consulta.get('regla'))}</p></div>"
        f'<div class="dx-res-body"><dl class="dx-facts">{hechos}</dl>'
        f'<p class="dx-meta">Paciente: {_e(consulta.get("nombre"))} · Consulta '
        f"{_e(consulta.get('id'))} · Modelo {_e(consulta.get('version_modelo'))}</p>"
        f'<p class="dx-meta">{_e(aviso)}</p></div></div>'
    )


def historial_html(consultas: Sequence[dict[str, Any]]) -> str:
    if not consultas:
        return '<div class="dx-empty">Sin consultas guardadas todavía.</div>'
    filas = []
    for c in consultas:
        estado = obtener_estado(str(c.get("estado", "")))
        n = (c.get("resumen") or {}).get("cantidad_sintomas", len(c.get("sintomas") or []))
        filas.append(
            f"<tr><td>{_e(formato_fecha(c.get('fecha')))}</td><td>{_e(c.get('nombre'))}</td>"
            f'<td><span class="dx-tag dx-estado-{estado.clase}">{_e(estado.nombre)}</span></td>'
            f'<td class="dx-num">{_e(n)}</td>'
            f'<td class="dx-num">{_e(formato_temperatura(c.get("temperatura")))}</td>'
            f"<td>{_e(c.get('regla'))}</td></tr>"
        )
    return (
        '<div class="dx-scroll"><table class="dx-table"><thead><tr><th>Fecha (UTC)</th>'
        '<th>Paciente</th><th>Estado</th><th class="dx-num">Síntomas</th>'
        '<th class="dx-num">Temp. °C</th><th>Regla aplicada</th></tr></thead>'
        f"<tbody>{''.join(filas)}</tbody></table></div>"
    )

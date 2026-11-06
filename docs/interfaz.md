# Diseño de la interfaz

Boceto y decisiones de la interfaz para el médico (servicio `app/`, Streamlit). Prototipo interactivo navegable: [`mockup/interfaz.html`](mockup/interfaz.html) (abrir en el navegador; es solo un prototipo, no es la aplicación).

## Boceto

```
┌────────────────────────────────────────────────────────────────┐
│ ████ Apoyo a la decisión médica ████ │ ░░ Uso didáctico ░░░░░░ │
│ ████ MLOps · Semanas 1 y 2       ████ │ ░░ (aviso de reglas) ░░ │
├───────────────────────────────────────┬────────────────────────┤
│ Nueva consulta                        │ Resultado              │
│ Nombre completo [________________]    │ ┌────────────────────┐ │
│ Temperatura (°C) [ 39.0 ]             │ │ ENFERMEDAD AGUDA   │ │
│                                       │ │ regla aplicada     │ │
│ Síntomas reportados (4 de 20)         │ └────────────────────┘ │
│ ┌──────────────────┬────────┬─────┬──┐│ Síntomas       4       │
│ │ Descripción      │Intens. │Días │  ││ Intensidad máx 8       │
│ │ Dolor de cabeza  │   8    │  3  │✕ ││ Días máx       3       │
│ │ Fiebre alta      │   7    │  3  │✕ ││ Temperatura    39,0 °C │
│ └──────────────────┴────────┴─────┴──┘│ Paciente · consulta ·  │
│ [+ Agregar síntoma]                   │ versión del modelo     │
│ Ejemplos: [No enfermo][Leve]          │                        │
│           [Aguda][Crónica]            │                        │
│ [Consultar]  [Limpiar formulario]     │                        │
├───────────────────────────────────────┴────────────────────────┤
│ Historial de consultas (más recientes primero)                 │
│ Fecha │ Paciente │ Estado │ Síntomas │ Temp. │ Regla aplicada   │
├────────────────────────────────────────────────────────────────┤
│ Pie: institución, programa, materia e integrantes              │
└────────────────────────────────────────────────────────────────┘
```

## Decisiones

- **Entradas:** nombre completo, temperatura y una tabla de síntomas con descripción, intensidad (0 a 10) y días. Hasta 20 síntomas.
- **Valores derivados para la función:** cantidad de síntomas (filas), intensidad máxima y días máximos.
- **Validación:** el servicio valida con Pydantic y devuelve mensajes claros. La interfaz aplica los mismos límites antes de enviar y muestra los errores de la API.
- **Resultado:** estado con color propio, regla aplicada, versión del modelo y aviso didáctico.
- **Historial:** cada consulta se guarda en un archivo JSON dentro de un volumen del contenedor de la API; la interfaz lo muestra en una tabla.
- **Estilos:** una sola hoja de estilos (`styles.css`) cargada desde un único punto, más el tema base de Streamlit en `.streamlit/config.toml`.
- **Paleta:** azul índigo `#5657EC`, lima `#E3EA55`, negro y blanco, con verde `#4DB87B`, naranja `#EB6B3F` y violeta `#8A5CF0` para los estados. Tipografías Sora (títulos) y Figtree (texto).
- **Pie de página:** institución, facultad, programa, materia e integrantes del grupo.

## Colores por estado

| Estado | Color |
|---|---|
| NO ENFERMO | Verde |
| ENFERMEDAD LEVE | Lima |
| ENFERMEDAD AGUDA | Naranja |
| ENFERMEDAD CRÓNICA | Violeta |

## Nota sobre datos personales

El nombre del paciente se almacena en el historial. En la demostración se usan solo nombres ficticios; un uso real requeriría consentimiento y cumplimiento de la Ley 1581 de 2012.

"""
app.py — Interfaz Streamlit para CCL Eventos
Corre con:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from scraper import CATEGORIAS, obtener_eventos

# ── Página ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CCL Eventos",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://ccleventos.pe/assets/images/logo.webp", width=180)
    st.markdown("## Filtros")

    categoria     = st.selectbox("Categoría", CATEGORIAS)
    buscar        = st.text_input("🔍 Buscar", placeholder="ej: marketing, exportación...")

    st.divider()
    ejecutar = st.button("▶️ Obtener eventos", type="primary", use_container_width=True)
    st.caption("Fuente: [ccleventos.pe](https://ccleventos.pe)")

# ── Cabecera ───────────────────────────────────────────────────────
st.title("🏛️ Eventos CCL")
st.markdown("Cámara de Comercio de Lima — eventos, capacitaciones y ferias")
st.divider()

# ── Estado de sesión ───────────────────────────────────────────────
if "eventos" not in st.session_state:
    st.session_state.eventos = []

# ── Fetch ──────────────────────────────────────────────────────────
if ejecutar:
    with st.spinner("Obteniendo eventos... ⏳"):
        try:
            st.session_state.eventos = obtener_eventos(categoria)
        except Exception as e:
            st.error(f"Error al consultar la API: {e}")
            st.stop()

# ── Sin datos ──────────────────────────────────────────────────────
eventos = st.session_state.eventos
if not eventos:
    st.info("👈 Selecciona una categoría y pulsa **Obtener eventos**.")
    st.stop()

# ── Filtro por texto ───────────────────────────────────────────────
if buscar:
    kw = buscar.lower()
    eventos = [
        e for e in eventos
        if kw in e["titulo"].lower()
        or kw in e["descripcion"].lower()
        or kw in e["lugar"].lower()
    ]

# ── Métricas ───────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Eventos", len(eventos))
c2.metric("Categoría", categoria)
c3.metric("Tipos únicos", len({e["tipo"] for e in eventos}))
st.divider()

# ── Tabs ───────────────────────────────────────────────────────────
tab_cards, tab_tabla, tab_csv = st.tabs(["🃏 Tarjetas", "📋 Tabla", "⬇️ Exportar CSV"])

# Tarjetas
with tab_cards:
    if not eventos:
        st.warning("Sin resultados para ese filtro.")
    else:
        cols = st.columns(3)
        for i, ev in enumerate(eventos):
            with cols[i % 3]:
                with st.container(border=True):
                    if ev["imagen"]:
                        st.image(ev["imagen"], use_container_width=True)
                    st.markdown(f"**{ev['titulo']}**")
                    st.caption(f"📅 {ev['fecha']}")
                    st.caption(f"📍 {ev['lugar']}")
                    st.caption(f"🏷️ {ev['tipo']} · {ev['categoria']}")
                    st.caption(f"💰 {ev['precio']}")
                    st.link_button("Ver evento →", ev["url"], use_container_width=True)

# Tabla
with tab_tabla:
    df = pd.DataFrame(eventos)
    st.dataframe(
        df[["titulo", "fecha", "categoria", "tipo", "lugar", "precio", "clase", "url"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "url": st.column_config.LinkColumn("Enlace", display_text="Abrir →"),
        },
    )

# CSV
with tab_csv:
    df  = pd.DataFrame(eventos)
    csv = df.drop(columns=["descripcion"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name="eventos_ccl.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.dataframe(df.drop(columns=["descripcion", "imagen"]),
                 use_container_width=True, hide_index=True)
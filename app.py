"""
app.py
------
Interfaz Streamlit para el scraper de CCL Eventos.
Corre con:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from scraper import CATEGORIAS, obtener_eventos

# ── Configuración de página ────────────────────────────────────────
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

    categoria = st.selectbox("Categoría", CATEGORIAS)
    buscar_titulo = st.text_input("🔍 Buscar por palabra clave", placeholder="ej: marketing, export...")

    st.divider()
    ejecutar = st.button("▶️ Scrapear ahora", type="primary", use_container_width=True)

    st.caption("Fuente: [ccleventos.pe](https://ccleventos.pe) · Cámara de Comercio de Lima")

# ── Cabecera ───────────────────────────────────────────────────────
st.title("🏛️ Eventos CCL")
st.markdown("Cámara de Comercio de Lima — eventos, capacitaciones y ferias")
st.divider()

# ── Estado de sesión ───────────────────────────────────────────────
if "eventos" not in st.session_state:
    st.session_state.eventos = []
if "metodo" not in st.session_state:
    st.session_state.metodo = ""

# ── Acción de scrape ───────────────────────────────────────────────
if ejecutar:
    ruta = CATEGORIAS[categoria]
    with st.spinner("Scrapeando eventos... puede tardar unos segundos ⏳"):
        st.session_state.eventos = obtener_eventos(categoria)
    st.session_state.eventos = eventos
    st.session_state.metodo  = metodo

# ── Mostrar resultados ─────────────────────────────────────────────
eventos = st.session_state.eventos

if not eventos:
    st.info("👈 Selecciona una categoría y haz clic en **Scrapear ahora**.")
    st.stop()

# Filtro por palabra clave (sobre los resultados ya scrapeados)
if buscar_titulo:
    kw = buscar_titulo.lower()
    eventos = [e for e in eventos if kw in e["titulo"].lower() or kw in e["categoria"].lower()]

# Métricas rápidas
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Eventos encontrados", len(eventos))
col_m2.metric("Categoría", categoria.split(" ", 1)[-1])
col_m3.metric("Motor usado", st.session_state.metodo.split(" ")[0].capitalize())

st.divider()

# Pestañas: Tarjetas | Tabla | Descargar
tab_cards, tab_tabla, tab_csv = st.tabs(["🃏 Tarjetas", "📋 Tabla", "⬇️ Exportar"])

# ── Tab 1: Tarjetas ────────────────────────────────────────────────
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
                    if ev["fecha"]:
                        st.caption(f"📅 {ev['fecha']}")
                    if ev["categoria"]:
                        st.caption(f"🏷️ {ev['categoria']}")
                    if ev["precio"]:
                        st.caption(f"💰 {ev['precio']}")
                    if ev["url"]:
                        st.link_button("Ver evento →", ev["url"], use_container_width=True)

# ── Tab 2: Tabla ───────────────────────────────────────────────────
with tab_tabla:
    if eventos:
        df = pd.DataFrame(eventos)
        st.dataframe(
            df[["titulo", "fecha", "categoria", "precio", "url"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "url": st.column_config.LinkColumn("Enlace", display_text="Abrir →"),
            },
        )

# ── Tab 3: Exportar CSV ────────────────────────────────────────────
with tab_csv:
    if eventos:
        df = pd.DataFrame(eventos)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar como CSV",
            data=csv_bytes,
            file_name="eventos_ccl.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

import streamlit as st

st.set_page_config(
    page_title="Panel de Control - Obra",
    layout="centered"
)

# LOGO DE LA EMPRESA
logo_url = "https://i.postimg.cc/66Hm1Vpz/Captura-de-pantalla-2026-05-12-212819.png"

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_url, width=150)

st.title("Panel de Control")
st.markdown("---")
st.markdown("### Selecciona la aplicación que deseas usar:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Seguimiento de Obra")
    st.markdown("Registro de tareas, avances y fotos de la instalación eléctrica")
    # Redirección directa con HTML
    st.markdown('[<button style="background-color:#ff4b4b; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; width:100%; font-size:16px;">🔨 Acceder a Obra</button>](https://app-seguimientoobra-j5yuvdg2whwie4ifdqcpzh.streamlit.app)', unsafe_allow_html=True)

with col2:
    st.subheader("Seguimiento de Presupuesto")
    st.markdown("Control de gastos, albaranes y facturación de la obra")
    # Redirección directa con HTML
    st.markdown('[<button style="background-color:#ff4b4b; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; width:100%; font-size:16px;">💰 Acceder a Presupuesto</button>](https://seguimiento-presupuesto-lsxmwf6sovvawruyiraqky.streamlit.app)', unsafe_allow_html=True)

st.markdown("---")
st.markdown("**Sistema de Gestión de Obra** | Fundación Masaveu")

import streamlit as st

st.set_page_config(
    page_title="Panel de Control - Obra",
    page_icon="🏠",
    layout="centered"
)

# LOGO DE LA EMPRESA
logo_url = "https://i.postimg.cc/66Hm1Vpz/Captura-de-pantalla-2026-05-12-212819.png"

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_url, width=150)

st.title("🏠 Panel de Control")
st.markdown("---")
st.markdown("### Selecciona la aplicación que deseas usar:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📋")
    st.subheader("Seguimiento de Obra")
    st.markdown("Registro de tareas, avances y fotos de la instalación eléctrica")
    if st.button("🔨 Acceder a Obra", use_container_width=True, type="primary"):
        st.markdown('[Ir a Seguimiento de Obra](https://app-seguimientoobra-j5yuvdg2whwie4ifdqcpzh.streamlit.app)', unsafe_allow_html=True)
        st.info("Haz clic en el enlace: https://app-seguimientoobra-j5yuvdg2whwie4ifdqcpzh.streamlit.app")

with col2:
    st.markdown("## 💰")
    st.subheader("Seguimiento de Presupuesto")
    st.markdown("Control de gastos, albaranes y facturación de la obra")
    if st.button("📊 Acceder a Presupuesto", use_container_width=True, type="primary"):
        st.markdown('[Ir a Seguimiento de Presupuesto](https://seguimiento-presupuesto-lsxmwf6sovvawruyiraqky.streamlit.app)', unsafe_allow_html=True)
        st.info("Haz clic en el enlace: https://seguimiento-presupuesto-lsxmwf6sovvawruyiraqky.streamlit.app")

st.markdown("---")
st.markdown("🏗️ **Sistema de Gestión de Obra** | Fundación Masaveu")

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import base64
import os

# Configuración de la página
st.set_page_config(
    page_title="Seguimiento de Obra",
    page_icon="🏗️",
    layout="centered"
)

#def get_logo_base64():
    return "https://i.postimg.cc/66Hm1Vpz/Captura-de-pantalla-2026-05-12-212819.png"
# Título y logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(get_logo_base64(), width=150)
st.title("📋 Seguimiento de Obra")
st.markdown("---")

# Lista de tareas
tareas = [
    "Trazado y marcado de cajas, tubos y cuadros",
    "Ejecución rozas en paredes y techos",
    "Montaje de soportes",
    "Colocación tubos y conductos",
    "Tendido de cables",
    "Identificación y etiquetado",
    "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos",
    "Fijación de carril DIN y mecanismos en cuadro eléctrico",
    "Cableado interno del cuadro eléctrico",
    "Configuración de equipos domóticos y/o automáticos",
    "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
    "Pruebas de continuidad",
    "Pruebas de aislamiento",
    "Verificación de tierras",
    "Programación del automatismo",
    "Pruebas de funcionamiento"
]

# Estados de avance
estados = [
    "🟢 Avance 25%",
    "🟡 Avance 50%",
    "🟠 Avance 75%",
    "✅ OK, finalizado sin errores",
    "⚠️ Finalizado, pero con errores pendientes de corregir",
    "🔧 Finalizado y corregidos los errores"
]

# Inicializar DataFrame en session_state
if 'df_registros' not in st.session_state:
    st.session_state.df_registros = pd.DataFrame(columns=[
        "Fecha", "Trabajador", "Tarea", "Estado", "Hora_Registro"
    ])

# Formulario de entrada
st.subheader("➕ Nuevo Registro")

with st.form("form_registro"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_trabajador = st.text_input("👷 Nombre del trabajador", placeholder="Ej: Pedro Martínez")
        fecha = st.date_input("📅 Fecha", datetime.now())
    
    with col2:
        tarea_seleccionada = st.selectbox("📌 Tarea", tareas)
        estado_seleccionado = st.selectbox("📊 Estado", estados)
    
    submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
    
    if submitted:
        if not nombre_trabajador:
            st.error("❌ Por favor, ingrese el nombre del trabajador")
        else:
            nuevo_registro = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Trabajador": nombre_trabajador,
                "Tarea": tarea_seleccionada,
                "Estado": estado_seleccionado,
                "Hora_Registro": datetime.now().strftime("%H:%M:%S")
            }])
            st.session_state.df_registros = pd.concat([st.session_state.df_registros, nuevo_registro], ignore_index=True)
            st.success("✅ Registro guardado correctamente")
            st.balloons()

st.markdown("---")

# Mostrar registros existentes
st.subheader("📊 Registros Actuales")

if not st.session_state.df_registros.empty:
    st.dataframe(st.session_state.df_registros, use_container_width=True, height=300)
    
    # Estadísticas rápidas
    st.subheader("📈 Resumen de tareas")
    resumen = st.session_state.df_registros.groupby("Estado").size().reset_index(name="Cantidad")
    st.bar_chart(resumen.set_index("Estado"))
else:
    st.info("ℹ️ No hay registros aún. Complete el formulario para comenzar.")

st.markdown("---")

# Función para generar Excel
def generar_excel():
    if st.session_state.df_registros.empty:
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.df_registros.to_excel(writer, sheet_name='Seguimiento_Obra', index=False)
        
        # Ajustar anchos de columna
        worksheet = writer.sheets['Seguimiento_Obra']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 40)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

# Botón para descargar Excel
st.subheader("💾 Exportar Datos")

col1, col2 = st.columns(2)

with col1:
    if not st.session_state.df_registros.empty:
        excel_data = generar_excel()
        if excel_data:
            b64 = base64.b64encode(excel_data.getvalue()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="seguimiento_obra_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx">📥 Descargar Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No hay datos para exportar")

with col2:
    # Botón para limpiar registros
    if st.button("🗑️ Limpiar todos los registros", use_container_width=True):
        st.session_state.df_registros = pd.DataFrame(columns=[
            "Fecha", "Trabajador", "Tarea", "Estado", "Hora_Registro"
        ])
        st.rerun()

st.markdown("---")

# Envío de correo
st.subheader("📧 Enviar por Correo Electrónico")

# Configuración de correo (para producción, usar st.secrets)
# En Streamlit Cloud, configurar en .streamlit/secrets.toml
if 'email_config' not in st.session_state:
    # Configuración por defecto - CAMBIAR ESTOS VALORES
    st.session_state.email_config = {
        'destinatario': 'profesora@email.com',  # Cambiar por email de la profesora
        'remitente': 'tu_email@gmail.com',       # Cambiar por tu email
        'password': ''                           # Contraseña de aplicación
    }

with st.expander("⚙️ Configurar envío de correo"):
    destinatario = st.text_input("📧 Correo del destinatario (empresa/profesora)", 
                                 value=st.session_state.email_config['destinatario'])
    remitente = st.text_input("📤 Correo remitente (tu correo)", 
                              value=st.session_state.email_config['remitente'])
    password = st.text_input("🔑 Contraseña de aplicación (Gmail)", 
                             type="password",
                             value=st.session_state.email_config.get('password', ''))
    
    st.caption("""
    **Nota:** Para Gmail, debes usar una [Contraseña de aplicación](https://myaccount.google.com/apppasswords).
    No uses tu contraseña normal de Gmail por seguridad.
    """)
    
    if st.button("💾 Guardar configuración"):
        st.session_state.email_config['destinatario'] = destinatario
        st.session_state.email_config['remitente'] = remitente
        st.session_state.email_config['password'] = password
        st.success("Configuración guardada temporalmente")

# Función para enviar email
def enviar_email(destinatario, remitente, password, archivo_excel):
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Informe Seguimiento Obra - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Cuerpo del mensaje
        cuerpo = f"""
        Informe de seguimiento de obra generado desde la app.
        
        Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        Total de registros: {len(st.session_state.df_registros)}
        
        Adjunto encontrará el archivo Excel con todos los registros.
        
        ---
        Generado automáticamente por App Seguimiento de Obra
        """
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        # Adjuntar archivo
        if archivo_excel:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(archivo_excel.getvalue())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=seguimiento_obra_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            msg.attach(part)
        
        # Enviar correo
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
        
        return True, "Correo enviado correctamente"
    
    except Exception as e:
        return False, f"Error al enviar: {str(e)}"

# Botón para enviar correo
col1, col2 = st.columns([2, 1])
with col1:
    if st.button("📧 Enviar Excel por correo", use_container_width=True, type="primary"):
        if st.session_state.df_registros.empty:
            st.warning("⚠️ No hay registros para enviar")
        elif not st.session_state.email_config.get('password'):
            st.error("❌ Por favor, configure la contraseña en el panel de configuración")
        else:
            with st.spinner("Enviando correo..."):
                excel_data = generar_excel()
                if excel_data:
                    success, message = enviar_email(
                        st.session_state.email_config['destinatario'],
                        st.session_state.email_config['remitente'],
                        st.session_state.email_config['password'],
                        excel_data
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.info(f"📧 Enviado a: {st.session_state.email_config['destinatario']}")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("No se pudo generar el archivo Excel")

with col2:
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

# Información de ayuda
st.markdown("---")
st.caption("""
**ℹ️ Nota importante:** 
- Los datos solo se guardan mientras la app esté activa (máximo ~2-3 horas en Streamlit Cloud)
- Descarga el Excel periódicamente o envíalo por correo para conservar los registros
- Para usar el envío de correo, activa el acceso a apps no seguras o genera una contraseña de aplicación en Gmail
""")

# Footer
st.markdown("---")
st.markdown("🏗️ **App Seguimiento de Obra** | Desarrollado para Fundación Masaveu")


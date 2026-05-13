import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import base64
from PIL import Image

st.set_page_config(
    page_title="Seguimiento de Obra",
    page_icon="🏗️",
    layout="centered"
)

# LOGO DE LA EMPRESA
logo_url = "https://i.postimg.cc/66Hm1Vpz/Captura-de-pantalla-2026-05-12-212819.png"

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_url, width=150)

st.title("📋 Seguimiento de Obra")
st.markdown("---")

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

estados = [
    "🟢 Avance 25%",
    "🟡 Avance 50%",
    "🟠 Avance 75%",
    "✅ OK, finalizado sin errores",
    "⚠️ Finalizado, pero con errores pendientes de corregir",
    "🔧 Finalizado y corregidos los errores"
]

if 'df_registros' not in st.session_state:
    st.session_state.df_registros = pd.DataFrame(columns=[
        "Fecha", "Trabajador", "Tarea", "Estado", "Hora_Registro", "Fotos"
    ])

if 'fotos_obra' not in st.session_state:
    st.session_state.fotos_obra = {}

st.subheader("➕ Nuevo Registro")

with st.form("form_registro"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_trabajador = st.text_input("👷 Nombre del trabajador", placeholder="Ej: Pedro Martínez")
        # Fecha con valor por defecto = hoy, pero editable
        fecha = st.date_input("📅 Fecha", datetime.now(), format="DD/MM/YYYY")
    
    with col2:
        tarea_seleccionada = st.selectbox("📌 Tarea", tareas)
        estado_seleccionado = st.selectbox("📊 Estado", estados)
    
    st.markdown("📸 **Fotos del avance (opcional - puedes subir varias)**")
    fotos_subidas = st.file_uploader("Seleccionar imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
    
    if submitted:
        if not nombre_trabajador:
            st.error("❌ Por favor, ingrese el nombre del trabajador")
        else:
            lista_fotos = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for i, foto in enumerate(fotos_subidas):
                nombre_foto = f"obra_{timestamp}_{tarea_seleccionada[:20]}_{i}.jpg"
                st.session_state.fotos_obra[nombre_foto] = foto.getvalue()
                lista_fotos.append(nombre_foto)
            
            hora_espana = (datetime.now() + timedelta(hours=2)).strftime("%H:%M:%S")
            
            nuevo_registro = pd.DataFrame([{
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Trabajador": nombre_trabajador,
                "Tarea": tarea_seleccionada,
                "Estado": estado_seleccionado,
                "Hora_Registro": hora_espana,
                "Fotos": ", ".join(lista_fotos) if lista_fotos else ""
            }])
            st.session_state.df_registros = pd.concat([st.session_state.df_registros, nuevo_registro], ignore_index=True)
            st.success(f"✅ Registro guardado correctamente con {len(lista_fotos)} fotos")
            st.balloons()

st.markdown("---")

st.subheader("📊 Registros Actuales")

if not st.session_state.df_registros.empty:
    df_mostrar = st.session_state.df_registros.copy()
    df_mostrar = df_mostrar.drop(columns=["Fotos"], errors='ignore')
    st.dataframe(df_mostrar, use_container_width=True, height=300)
    
    st.subheader("📸 Ver fotos guardadas")
    if len(st.session_state.df_registros) > 0:
        registro_seleccionado = st.selectbox("Selecciona un registro para ver sus fotos", 
                                              st.session_state.df_registros["Tarea"].tolist())
        
        if registro_seleccionado:
            fila = st.session_state.df_registros[st.session_state.df_registros["Tarea"] == registro_seleccionado].iloc[0]
            if fila["Fotos"] and fila["Fotos"] != "":
                nombres_fotos = fila["Fotos"].split(", ")
                for nombre_foto in nombres_fotos:
                    if nombre_foto in st.session_state.fotos_obra:
                        st.image(st.session_state.fotos_obra[nombre_foto], caption=nombre_foto, width=200)
            else:
                st.info("Este registro no tiene fotos")
    
    st.subheader("📈 Resumen de tareas")
    resumen = st.session_state.df_registros.groupby("Estado").size().reset_index(name="Cantidad")
    st.bar_chart(resumen.set_index("Estado"))
else:
    st.info("ℹ️ No hay registros aún. Complete el formulario para comenzar.")

st.markdown("---")

def generar_excel():
    if st.session_state.df_registros.empty:
        return None
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = st.session_state.df_registros.drop(columns=["Fotos"], errors='ignore')
        df_export.to_excel(writer, sheet_name='Seguimiento_Obra', index=False)
        
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

st.subheader("💾 Exportar Datos")

col1, col2, col3 = st.columns(3)

with col1:
    if not st.session_state.df_registros.empty:
        excel_data = generar_excel()
        if excel_data:
            b64 = base64.b64encode(excel_data.getvalue()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="seguimiento_obra_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx">📥 Descargar Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No hay datos")

with col2:
    if st.button("🗑️ Limpiar registros", use_container_width=True):
        st.session_state.df_registros = pd.DataFrame(columns=[
            "Fecha", "Trabajador", "Tarea", "Estado", "Hora_Registro", "Fotos"
        ])
        st.session_state.fotos_obra = {}
        st.rerun()

st.markdown("---")

st.subheader("📧 Enviar por Correo Electrónico")

if 'email_config' not in st.session_state:
    st.session_state.email_config = {
        'destinatario': 'profesora@email.com',
        'remitente': 'tu_email@gmail.com',
        'password': ''
    }

with st.expander("⚙️ Configurar envío de correo"):
    destinatario = st.text_input("📧 Correo del destinatario", 
                                 value=st.session_state.email_config['destinatario'])
    remitente = st.text_input("📤 Correo remitente (tu correo)", 
                              value=st.session_state.email_config['remitente'])
    password = st.text_input("🔑 Contraseña de aplicación (Gmail)", 
                             type="password",
                             value=st.session_state.email_config.get('password', ''))
    
    st.caption("Para Gmail, usa una [Contraseña de aplicación](https://myaccount.google.com/apppasswords)")
    
    if st.button("💾 Guardar configuración"):
        st.session_state.email_config['destinatario'] = destinatario
        st.session_state.email_config['remitente'] = remitente
        st.session_state.email_config['password'] = password
        st.success("Configuración guardada")

def enviar_email(destinatario, remitente, password, archivo_excel):
    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Informe Obra + Fotos - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        cuerpo = f"""
        Informe de seguimiento de OBRA con fotos.
        
        Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        Total de registros: {len(st.session_state.df_registros)}
        Total de fotos: {len(st.session_state.fotos_obra)}
        
        Adjuntos: Excel con datos y {len(st.session_state.fotos_obra)} fotos.
        """
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        if archivo_excel:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(archivo_excel.getvalue())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                           f'attachment; filename=obra_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
            msg.attach(part)
        
        for nombre_foto, datos_foto in st.session_state.fotos_obra.items():
            part_img = MIMEBase('application', 'octet-stream')
            part_img.set_payload(datos_foto)
            encoders.encode_base64(part_img)
            part_img.add_header('Content-Disposition', f'attachment; filename={nombre_foto}')
            msg.attach(part_img)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
        
        return True, f"Correo enviado con {len(st.session_state.fotos_obra)} fotos"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

col1, col2 = st.columns([2, 1])
with col1:
    if st.button("📧 Enviar Excel y fotos por correo", use_container_width=True, type="primary"):
        if st.session_state.df_registros.empty:
            st.warning("⚠️ No hay registros")
        elif not st.session_state.email_config.get('password'):
            st.error("❌ Configure la contraseña")
        else:
            with st.spinner("Enviando..."):
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
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("Error")

with col2:
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

st.markdown("---")
st.caption("""
**ℹ️ Nota importante:** 
- Puedes subir varias fotos por registro
- Las fotos se envían automáticamente por correo
- La fecha aparece automáticamente con el día actual, pero puedes cambiarla si es necesario
""")
st.markdown("🏗️ **App Seguimiento de Obra con Fotos** | Fundación Masaveu")

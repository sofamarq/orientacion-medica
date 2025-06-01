
import streamlit as st
from supabase_connection import supabase
from registro_login import login
from triaje import orientacion_medica
from historial import mostrar_historial
import datetime
from turnos import ver_mis_turnos

st.set_page_config(page_title="Orientación Médica", page_icon="🩺")

# Inicializar estado de sesión si no existe
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"

if "especialidad_a_reservar" not in st.session_state:
    st.session_state.especialidad_a_reservar = None

# ✅ Inicializamos el estado de triaje correctamente
if "triaje_estado" not in st.session_state:
    st.session_state.triaje_estado = {
        "sintomas": [],
        "analisis_realizado": False,
        "especialidad": None,
        "urgencia_api": None
    }

# ✅ Creamos el estado auxiliar para detectar cambio de menú
if "ultimo_menu" not in st.session_state:
    st.session_state.ultimo_menu = "Inicio"

# Si no está logueado: primero registrar o loguear
if not st.session_state.usuario:
    login()
else:
    usuario = st.session_state.usuario
    st.sidebar.markdown(
        f"""
        <h2 style='font-size: 26px; margin-bottom: 30px;'>
            👋 Hola, {usuario['nombre']} {usuario['apellido']}!
        </h2>
        """, 
        unsafe_allow_html=True
    )

    opciones_menu = ["Inicio", "Orientación Médica", "Historial", "Mis Datos", "Mis Turnos", "Cerrar sesión"]
    menu = st.sidebar.radio("Menú", opciones_menu, index=opciones_menu.index(st.session_state.menu))

    # Detectamos si el usuario cambió de vista
    if menu != st.session_state.ultimo_menu:
        if menu == "Orientación Médica":
            # Reset de síntomas al ingresar nuevamente
            st.session_state.triaje_estado = {
                "sintomas": [],
                "analisis_realizado": False,
                "especialidad": None,
                "urgencia_api": None
            }
        st.session_state.ultimo_menu = menu

    st.session_state.menu = menu

    if st.session_state.menu == "Inicio":
        st.title("🩺 Asistente de Orientación Médica")

        st.markdown("""
        <div style="
            background-color: #fff3cd;
            border-left: 5px solid #ffa500;
            padding: 25px;
            border-radius: 12px;
            font-size: 18px;
            margin-top: 20px;
        ">
        ⚠️ <strong>IMPORTANTE:</strong> Esta herramienta está diseñada para brindar una orientación clínica inicial basada en algoritmos validados y guías clínicas internacionales.
        <ul>
            <li>No reemplaza el juicio ni la consulta médica profesional.</li>
            <li>No constituye diagnóstico definitivo ni prescripción de tratamiento.</li>
            <li>Ante dudas o síntomas graves, consultar SIEMPRE al profesional de la salud.</li>
        </ul>
        <p style='font-size: 0.9em; color: #555;'>Toda la información personal es confidencial y este sistema actúa únicamente como herramienta de ayuda al paciente.</p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.menu == "Orientación Médica":
        orientacion_medica(st.session_state.usuario)

    elif st.session_state.menu == "Historial":
        mostrar_historial(st.session_state.usuario['id'])

    elif st.session_state.menu == "Mis Datos":
        usuario = st.session_state.usuario
        st.header("👤 Mis Datos")
        st.markdown(
            f"""
            <div style="background-color:#f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #dee2e6; max-width: 600px; margin: auto; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); font-size: 18px;">
                <p><strong>DNI:</strong> {usuario['id']}</p>
                <p><strong>Nombre:</strong> {usuario['nombre']} {usuario['apellido']}</p>
                <p><strong>Fecha de nacimiento:</strong> {usuario['fecha_nacimiento']}</p>
                <p><strong>Género:</strong> {'Femenino' if usuario['genero']=='female' else 'Masculino'}</p>
                <p><strong>Cobertura médica:</strong> {usuario['cobertura']}</p>
                <p><strong>Número de afiliado:</strong> {usuario['numero_afiliado']}</p>
            </div>
            """, unsafe_allow_html=True
        )

    elif st.session_state.menu == "Mis Turnos":
        ver_mis_turnos(st.session_state.usuario['id'])

    elif st.session_state.menu == "Cerrar sesión":
        st.session_state.usuario = None
        st.session_state.menu = "Inicio"
        st.rerun()

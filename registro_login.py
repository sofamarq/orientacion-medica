import streamlit as st
import datetime
from supabase_connection import supabase
from utils import hash_password, verify_password

def login():
    st.title("Bienvenido a la App de Orientación Médica Inicial (sin nombre)")

    tabs = st.tabs(["Iniciar Sesión", "Registrarse"])

    ### LOGIN TAB
    with tabs[0]:
        st.subheader("Iniciar sesión")

        dni_login = st.text_input("DNI", key="login_dni")
        password_login = st.text_input("Contraseña", type="password", key="login_password")

        if st.button("Ingresar", key="login_boton"):
            user = supabase.table("usuarios").select("*").eq("id", dni_login).execute()
            if not user.data:
                st.error("Usuario no encontrado")
                return

            user_data = user.data[0]
            if verify_password(password_login, user_data["password"]):
                st.session_state.usuario = user_data
                st.session_state.vista_actual = "Inicio"
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
                return None

    ### REGISTRO TAB
    with tabs[1]:
        st.subheader("Registro de nuevo usuario")

        dni_registro = st.text_input("DNI", key="registro_dni")
        nombre = st.text_input("Nombre", key="registro_nombre")
        apellido = st.text_input("Apellido", key="registro_apellido")
        fecha_nacimiento = st.date_input("Fecha de nacimiento", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key="registro_fecha")
        genero_key = st.radio("Género", ["Femenino", "Masculino"], key="registro_genero")
        genero = "female" if genero_key == "Femenino" else "male"
        cobertura = st.selectbox("Cobertura médica", ["Plan de Salud HUA"], key="registro_cobertura")
        numero_afiliado = st.text_input("Número de afiliado", key="registro_afiliado")
        password_registro = st.text_input("Contraseña", type="password", key="registro_password")

        # Checkbox de aceptación de términos
        aceptar_terminos = st.checkbox("Acepto los términos y condiciones", key="registro_terminos")
        with st.expander("Ver términos y condiciones"):
            st.markdown("""
                **Términos y Condiciones de Uso**

                Esta aplicación constituye un sistema de orientación médica preliminar, basado en algoritmos validados y guías clínicas de práctica médica. Su finalidad es sugerir posibles especialidades médicas a las cuales podría corresponder realizar una consulta, a partir de los síntomas ingresados por el usuario.

                Esta herramienta no reemplaza la evaluación ni diagnóstico de un profesional médico. Las recomendaciones son orientativas. Ante dudas, agravamiento o signos de alarma, debe consultar a un profesional de la salud o acudir a un centro médico.

                El usuario autoriza el uso anónimo de los datos ingresados con fines estadísticos, epidemiológicos y de mejora del sistema.

                La información es confidencial y protegida bajo normativa vigente. Los datos no serán compartidos con terceros fuera del ámbito de la institución.

                Al registrarse, el usuario declara haber leído y aceptar estos términos.
                """)
            #st.write("Aquí irían los términos y condiciones completos...")

        if st.button("Registrarse", key="registro_boton"):
            if not (dni_registro and nombre and apellido and password_registro and aceptar_terminos):
                st.warning("Completá todos los campos y aceptá los términos")
                return

            existe = supabase.table("usuarios").select("*").eq("id", dni_registro).execute()
            if existe.data:
                st.error("El usuario ya está registrado.")
                return

            supabase.table("usuarios").insert({
                "id": dni_registro,
                "nombre": nombre,
                "apellido": apellido,
                "fecha_nacimiento": str(fecha_nacimiento),
                "genero": genero,
                "cobertura": cobertura,
                "numero_afiliado": numero_afiliado,
                "password": hash_password(password_registro)
            }).execute()

            st.success("✅ Registro exitoso. Redirigiendo al login...")
            time.sleep(3)
            st.session_state.vista_actual = "Inicio"
            st.rerun()

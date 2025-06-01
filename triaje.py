#esta andando mal el triaje. Decirle que lo revise
import streamlit as st
import pandas as pd
import requests
import datetime
from supabase_connection import supabase
import time

# Inicializamos las variables de estado una sola vez
if "triaje_estado" not in st.session_state:
    st.session_state.triaje_estado = {
        "sintomas": [],
        "analisis_realizado": False,
        "especialidad": None,
        "urgencia_api": None,
        "turno_reservado": None
    }

def orientacion_medica(user_data):
    st.header("🩺 Orientación Médica Inicial")

    # Cargar archivos
    df_sintomas = pd.read_csv("sintomas_final.csv")
    df_sintomas.columns = df_sintomas.columns.str.strip().str.lower()
    sintomas_dict = dict(zip(df_sintomas["name"], df_sintomas["id"]))

    df_diagnosticos = pd.read_csv("diagnosticos_clasificados.csv")
    df_diagnosticos.columns = df_diagnosticos.columns.str.strip().str.lower()

    edad = calcular_edad(user_data["fecha_nacimiento"])
    sexo = user_data["genero"]

    # Selección de síntomas
    sintomas = st.multiselect("Seleccioná tus síntomas:", list(sintomas_dict.keys()), default=st.session_state.triaje_estado["sintomas"])

    if st.button("Analizar síntomas"):
        if not sintomas:
            st.warning("Por favor seleccioná al menos un síntoma.")
            return

        st.session_state.triaje_estado["sintomas"] = sintomas
        analizar_sintomas(user_data, sintomas, sintomas_dict, df_diagnosticos, edad, sexo)

    if st.session_state.triaje_estado["analisis_realizado"]:
        mostrar_resultado(user_data)


def analizar_sintomas(user_data, sintomas, sintomas_dict, df_diagnosticos, edad, sexo):
    evidence = [{"id": sintomas_dict[s], "choice_id": "present"} for s in sintomas]

    headers = {
        "App-Id": "6139445b",
        "App-Key": "9a2dbf062fab6a0b6d5010c2fdd8366f",
        "Content-Type": "application/json",
        "Accept-Language": "es"
    }

    payload = {
        "sex": sexo,
        "age": {"value": edad},
        "evidence": evidence,
        "extras": {"enable_triage_5": True}
    }

    url = "https://api.infermedica.com/v3/diagnosis"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        condiciones = data.get("conditions", [])

        if not condiciones:
            st.info("No se detectaron condiciones claras.")
            return

        # --------------------
        # Extraer ESPECIALIDAD (primer diagnóstico)
        top = condiciones[0]
        codigo_top = top['id']
        fila_top = df_diagnosticos[df_diagnosticos["condition_id"] == codigo_top]

        if not fila_top.empty:
            especialidad = fila_top.iloc[0]["especialidad"]
        else:
            especialidad = "Clínica Médica"

        # --------------------
        # Extraer URGENCIA (revisamos top 3)
        urgencia_api = "Consulta"  # default

        for c in condiciones[:3]:
            codigo = c['id']
            fila = df_diagnosticos[df_diagnosticos["condition_id"] == codigo]

            if not fila.empty:
                urgencia = fila.iloc[0]["nivel_urgencia"]
                if urgencia == "Emergencia":
                    urgencia_api = "Emergencia"
                    break
                elif urgencia == "Urgente" and urgencia_api != "Emergencia":
                    urgencia_api = "Urgente"

        # Guardamos estado
        st.session_state.triaje_estado["especialidad"] = especialidad
        st.session_state.triaje_estado["urgencia_api"] = urgencia_api
        st.session_state.triaje_estado["analisis_realizado"] = True

        supabase.table("historial_consultas").insert({
            "usuario_id": user_data["id"],
            "fecha": datetime.date.today().isoformat(),
            "sintomas": ", ".join(sintomas),
            "especialidad": especialidad
        }).execute()

        st.rerun()

    else:
        st.error("❌ Error al consultar la API de Infermedica.")


def mostrar_resultado(user_data):
    especialidad = st.session_state.triaje_estado["especialidad"]
    urgencia_api = st.session_state.triaje_estado["urgencia_api"]

    if urgencia_api == "Emergencia":
        st.markdown("""
            <div style='
                padding: 25px; 
                background-color: #ffe6e6; 
                border-left: 8px solid #d60000; 
                border-radius: 10px; 
                font-size: 18px; 
                margin-top: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                🚨 <strong>Se detectó al menos una condición que requiere atención médica inmediata.</strong><br><br>
                Dirigite inmediatamente a una guardia médica o contactá un profesional de emergencia.
            </div>
            """, unsafe_allow_html=True)
        st.warning("⚠️ Esta orientación es solo una sugerencia. Ante dudas consulte siempre con un profesional de la salud.")



    # elif urgencia_api == "Urgente":
    #     st.markdown(f"""
    #         <div style='
    #             background-color:#fff8e6;
    #             padding:25px;
    #             border-radius:12px;
    #             border: 2px solid #ffa500;
    #             box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    #             margin-top:20px;
    #             margin-bottom:30px;
    #             text-align:center;
    #         '>
    #             <h2 style='color:#ff7700;'>Consulta urgente</h2>
    #             <h3 style='color:#333;'>Especialidad sugerida: <span style='color:#0077b6;'>{especialidad}</span></h3>
    #             <p style='font-size:18px; margin-top:15px;'>
    #                 Es recomendable ser evaluado por un profesional de <b>{especialidad}</b> lo antes posible, idealmente en las próximas horas.
    #             </p>
    #         </div>
    #     """, unsafe_allow_html=True)
    #     st.warning("⚠️ Esta orientación es solo una sugerencia. Ante dudas consulte siempre con un profesional de la salud.")



    elif urgencia_api == "Urgente":
        st.markdown(f"""
            <div style='
                padding: 25px; 
                background-color: #fff4e6; 
                border-left: 8px solid #ffa500; 
                border-radius: 10px; 
                font-size: 18px; 
                margin-top: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                Especialidad sugerida: <b>{especialidad}</b><br><br>
                🟠 <strong>Se detectó una condición que requiere atención médica en las próximas horas.</strong>
            </div>
            """, unsafe_allow_html=True)
        st.warning("⚠️ Esta orientación es solo una sugerencia. Ante dudas consulte siempre con un profesional de la salud.")



    elif urgencia_api == "Consulta":
        st.markdown(f"""
            <div style='
                padding: 25px; 
                background: linear-gradient(135deg, #e6f7ff, #ffffff); 
                border-left: 8px solid #0077b6; 
                border-radius: 10px; 
                font-size: 18px; 
                margin-top: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                Especialidad sugerida: <b>{especialidad}</b><br><br>
                🔵 <strong>Se recomienda seguimiento ambulatorio con el especialista correspondiente.</strong>
            </div>
            """, unsafe_allow_html=True)

        st.warning("⚠️ Esta orientación es solo una sugerencia. Ante dudas consulte siempre con un profesional de la salud.")

        mostrar_turnos(user_data["id"], especialidad)



def mostrar_turnos(usuario_id, especialidad):
    st.markdown("---")
    st.subheader("Turnos disponibles con especialista")

    turnos = supabase.table("turnos_disponibles")\
                .select("*")\
                .eq("especialidad", especialidad)\
                .eq("disponible", True)\
                .order("fecha", desc=False)\
                .execute().data

    if not turnos:
        st.info("Por el momento no hay turnos disponibles.")
        return

    for turno in turnos:
        with st.container():
            st.markdown(f"""
                <div style='
                    background-color: #f9f9f9; 
                    border: 1px solid #ddd; 
                    border-radius: 12px; 
                    padding: 20px; 
                    margin-top: 20px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                '>
                    <p style='font-size:18px;'>
                        📅 <b>Fecha:</b> {turno['fecha']}<br>
                        ⏰ <b>Hora:</b> {turno['hora']}<br>
                        🏥 <b>Centro Médico:</b> {turno['centro_medico']}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            reservar = st.button("Reservar este turno", key=turno['id'])
            if reservar:
                supabase.table("turnos_reservados").insert({
                    "usuario_id": usuario_id,
                    "turno_id": turno['id']
                }).execute()

                supabase.table("turnos_disponibles").update({"disponible": False}).eq("id", turno['id']).execute()

                st.success("✅ Turno reservado correctamente.")
                st.info("Redirigiendo al inicio...")
                time.sleep(3)
                st.session_state.menu = "Inicio"
                st.rerun()


def calcular_edad(fecha_nacimiento):
    hoy = datetime.date.today()
    nacimiento = datetime.date.fromisoformat(fecha_nacimiento)
    edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    return edad

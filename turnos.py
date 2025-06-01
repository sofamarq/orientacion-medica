import streamlit as st
import datetime
from supabase_connection import supabase

# def reservar_turno(usuario_id):
#     st.header("📅 Reserva de Turno")

#     especialidad = st.session_state.get("especialidad_a_reservar")
#     if not especialidad:
#         st.warning("No hay especialidad seleccionada para reservar. Realice primero una orientación médica.")
#         return

#     turnos_disponibles = supabase.table("turnos_disponibles").select("*").eq("especialidad", especialidad).eq("disponible", True).execute().data

#     if not turnos_disponibles:
#         st.error("No hay turnos disponibles en esta especialidad.")
#         return

#     opciones = [f"{t['fecha']} - {t['hora']} en {t['centro_medico']}" for t in turnos_disponibles]
#     seleccion = st.selectbox("Seleccione un turno:", opciones)

#     if st.button("Confirmar reserva"):
#         turno = turnos_disponibles[opciones.index(seleccion)]
#         supabase.table("turnos_reservados").insert({
#             "usuario_id": usuario_id,
#             "turno_id": turno["id"],
#             "fecha": turno["fecha"],
#             "hora": turno["hora"],
#             "especialidad": turno["especialidad"],
#             "centro_medico": turno["centro_medico"]
#         }).execute()

#         # Actualizamos la disponibilidad
#         supabase.table("turnos_disponibles").update({"disponible": False}).eq("id", turno["id"]).execute()

#         st.success("✅ Turno reservado correctamente.")
#         del st.session_state["especialidad_a_reservar"]


def ver_mis_turnos(usuario_id):
    st.header("📅 Mis Turnos")

    turnos_reservados = supabase.table("turnos_reservados").select("*").eq("usuario_id", usuario_id).execute().data

    if not turnos_reservados:
        st.info("No tenés turnos reservados.")
        return

    ids_turnos = [t['turno_id'] for t in turnos_reservados]
    turnos_info = supabase.table("turnos_disponibles").select("*").in_("id", ids_turnos).execute().data
    turnos_info = sorted(turnos_info, key=lambda x: (x['fecha'], x['hora']))

    for turno in turnos_info:
        st.markdown(
            f"""
            <div style='
                background-color: #f9fafc; 
                border: 1px solid #d1d9e0; 
                border-radius: 12px; 
                padding: 20px; 
                margin-bottom: 30px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
                font-size: 17px;
            '>
                <p><b>📅 Fecha:</b> {turno['fecha']}</p>
                <p><b>⏰ Hora:</b> {turno['hora']}</p>
                <p><b>🏥 Centro Médico:</b> {turno['centro_medico']}</p>
                <p><b>👩‍⚕️ Especialidad:</b> {turno['especialidad']}</p>
            </div>
            """, unsafe_allow_html=True
        )


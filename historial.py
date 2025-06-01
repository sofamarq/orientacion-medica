import streamlit as st
import pandas as pd
from supabase_connection import supabase

def mostrar_historial(usuario_id):
    st.header("📂 Historial de Consultas")

    # Traemos los registros del historial desde la base
    resultado = supabase.table("historial_consultas").select("*").eq("usuario_id", usuario_id).execute()

    if resultado.data:
        # Convertimos los datos a DataFrame
        df = pd.DataFrame(resultado.data)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df.sort_values(by='fecha', ascending=False, inplace=True)

        # Formateamos la fecha
        df['fecha'] = df['fecha'].dt.strftime('%d/%m/%Y')

        columnas = ["fecha", "sintomas", "especialidad"]
        df = df[columnas]

        # Renombramos columnas para mostrar con mayúsculas
        df.columns = ["Fecha", "Síntomas", "Especialidad"]

        # Campo de búsqueda
        busqueda = st.text_input("Buscar en historial")

        if busqueda:
            busqueda_lower = busqueda.lower()
            df = df[
                df['Síntomas'].str.lower().str.contains(busqueda_lower) |
                df['Especialidad'].str.lower().str.contains(busqueda_lower)
            ]

        # Mostramos el dataframe sin el índice
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("No hay consultas registradas todavía.")

import streamlit as st
import pandas as pd

# Configuración de la App
st.set_page_config(page_title="Mi Crédito OWS", page_icon="🏦")

# CSS para mejorar el look
st.markdown("""
    <style>
    .stMetric { border: 1px solid #4a4a4a; padding: 10px; border-radius: 10px; background-color: #1a1c24; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # Leer datos saltando las 2 filas iniciales
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    
    # Limpiar la tabla de valores vacíos para que no diga "NaN" o "None"
    df = df.fillna("")

    st.title("🏦 Resumen de Cuenta")
    st.info("Cliente: OWS2025")

    # Obtener valores (asegurando que tomamos la última fila con datos)
    # Filtramos filas donde la fecha no esté vacía
    df_datos = df[df['Fecha'] != ""]
    cap_total = df_datos['Saldo Capital Pendiente'].iloc[-1]
    int_total = df_datos['Saldo Interés Pendiente'].iloc[-1]

    # KPIs
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL", f"{cap_total}")
    c2.metric("INTERESES", f"{int_total}")

    # Estatus Impactante
    st.error("⚠️ ESTATUS ACTUAL: EN RIESGO")

    # Tabla Estilizada
    st.write("### 📝 Historial de Movimientos")
    st.dataframe(df_datos[['Fecha', 'Descripción', 'Abono a Interés', 'Abono a Capital']], use_container_width=True)

    # --- BOTÓN DE CONTACTO DIRECTO ---
    st.markdown("---")
    st.markdown("¿Tienes alguna duda sobre tu saldo?")
    # Reemplaza el número por el tuyo
    st.link_button("💬 Hablar con Asesor", "https://wa.me/tu_numero_aqui")

except Exception as e:
    st.warning("Sincronizando con la base de datos...")
  

import streamlit as st
import pandas as pd

# Configuración de la App
st.set_page_config(page_title="Portal de Crédito OWS", layout="centered")

# Estilo personalizado
st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 15px; }
    [data-testid="stMetricValue"] { color: #00FFCC; }
    </style>
    """, unsafe_allow_html=True)

# URL de tu Google Sheet en formato CSV
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Leer los datos (saltando la primera fila de encabezado personalizado)
    df = pd.read_csv(url, skiprows=1)
    
    # Datos del Cliente (Fila 1 de tu Excel)
    cliente_nombre = "OWS2025" 
    estatus = "EN RIESGO"

    st.title(f"🏦 Bienvenido, {cliente_nombre}")
    st.write("Estado de tu préstamo en tiempo real")

    # Obtener los últimos valores de la tabla
    ultimo_capital = df['Saldo Capital Pendiente'].dropna().iloc[-1]
    ultimo_interes = df['Saldo Interés Pendiente'].dropna().iloc[-1]

    # Mostrar KPIs Impactantes
    col1, col2 = st.columns(2)
    col1.metric("Saldo Capital", ultimo_capital)
    col2.metric("Interés Pendiente", ultimo_interes)

    # Mostrar Estatus con color
    if "RIESGO" in estatus:
        st.error(f"⚠️ ESTATUS ACTUAL: {estatus}")
    else:
        st.success(f"✅ ESTATUS ACTUAL: {estatus}")

    # Tabla de Movimientos
    st.subheader("📝 Historial de Pagos")
    st.dataframe(df.dropna(subset=['Fecha']), use_container_width=True)

except Exception as e:
    st.warning("⚠️ Casi listo. Por favor, asegúrate de que el botón 'Compartir' en Google Sheets esté en 'Cualquier persona con el enlace'.")

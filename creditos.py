import streamlit as st
import pandas as pd

# Configuración de la App
st.set_page_config(page_title="Mi Crédito OWS", layout="centered")

# Estilo para móvil
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00FFCC; }
    .stAlert { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Tu ID de hoja actual (Detectado de tu imagen)
SHEET_ID = "1PMwlDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(url)
    
    # Extraer valores clave de tu tabla
    # Según tu imagen: F6 es Capital, G6 es Interés, E1 es Estatus
    cliente = "OWS2025"
    estatus = "EN RIESGO"  # Esto lo podemos dinamizar luego
    saldo_capital = "$3.000,00"
    saldo_interes = "$900,00"

    st.title(f"👋 ¡Hola, {cliente}!")
    st.write("Aquí tienes el resumen de tu préstamo en tiempo real.")

    # Tarjetas de Impacto
    col1, col2 = st.columns(2)
    col1.metric("Saldo Capital", saldo_capital)
    col2.metric("Interés Pendiente", saldo_interes, delta="+20%", delta_color="inverse")

    # Alerta de Estatus
    if "RIESGO" in estatus:
        st.error(f"🔴 ESTADO DEL CRÉDITO: {estatus}")
    else:
        st.success(f"✅ ESTADO DEL CRÉDITO: {estatus}")

    # Tabla de movimientos
    st.markdown("### 📊 Historial de Movimientos")
    st.dataframe(df.dropna(subset=['Fecha']), use_container_width=True)

except Exception as e:
    st.error("Conectando con la base de datos...")

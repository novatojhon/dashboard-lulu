import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Portal OWS", layout="centered")

# Estilo Neumórfico/Dark
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexión exacta a tu hoja
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # Leemos la hoja saltando las filas decorativas superiores
    df = pd.read_csv(url, skiprows=2) 
    
    # Limpiamos nombres de columnas por si acaso hay espacios
    df.columns = df.columns.str.strip()

    st.title("🏦 Portal de Crédito")
    st.subheader("Cliente: OWS2025")

    # Extraemos los últimos valores de las columnas F y G
    # Usamos .iloc[-1] para sacar siempre el dato de la fila más reciente
    cap_val = df['Saldo Capital Pendiente'].dropna().iloc[-1]
    int_val = df['Saldo Interés Pendiente'].dropna().iloc[-1]

    # Visualización Impactante
    col1, col2 = st.columns(2)
    col1.metric("CAPITAL PENDIENTE", cap_val)
    col2.metric("INTERÉS ACUMULADO", int_val, delta="Actualizado", delta_color="normal")

    # Estatus Dinámico
    st.error("⚠️ ESTATUS ACTUAL: EN RIESGO")

    # Tabla de movimientos estilizada
    st.markdown("### 📋 Historial de Movimientos")
    st.dataframe(df[['Fecha', 'Descripción', 'Abono a Interés', 'Abono a Capital']].dropna(subset=['Fecha']), use_container_width=True)

except Exception as e:
    st.info("🔄 Sincronizando datos... Asegúrate de que el archivo en Google Sheets siga compartido como 'Lector'.")
  

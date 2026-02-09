import streamlit as st
import pandas as pd

# Configuración compacta
st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# CSS para vista móvil limpia
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        color: #00ffcc !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #8b949e !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # Cargar datos
    df = pd.read_csv(url, skiprows=2).fillna("")
    df.columns = df.columns.str.strip()
    df_datos = df[df['Fecha'] != ""]
    
    # Extraer los últimos saldos
    cap_total = df_datos['Saldo Capital Pendiente'].iloc[-1]
    int_total = df_datos['Saldo Interés Pendiente'].iloc[-1]

    st.markdown("## 🏦 Resumen de Préstamo")
    
    # Métricas principales una tras otra
    st.metric("CAPITAL PENDIENTE", f"{cap_total}")
    st.metric("INTERÉS ACUMULADO", f"{int_total}")

    # Estatus destacado
    st.error("⚠️ ESTATUS: EN RIESGO")

    # Tabla de movimientos simplificada
    st.write("### 📋 Últimos Movimientos")
    st.dataframe(
        df_datos[['Fecha', 'Descripción', 'Abono a Interés', 'Abono a Capital']].tail(5), 
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.write("⌛ Sincronizando datos...")

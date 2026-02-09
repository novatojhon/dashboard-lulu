import streamlit as st
import pandas as pd

# Configuración compacta para celular
st.set_page_config(page_title="Mi Crédito OWS", layout="centered")

# CSS para forzar la estética de App móvil
st.markdown("""
    <style>
    /* Ocultar menús innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tarjetas de métricas estilo neón */
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 2px solid #00ffcc;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        color: #00ffcc !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    df = pd.read_csv(url, skiprows=2).fillna("")
    df.columns = df.columns.str.strip()
    df_datos = df[df['Fecha'] != ""]
    
    # Extraer saldos
    cap_total = df_datos['Saldo Capital Pendiente'].iloc[-1]
    int_total = df_datos['Saldo Interés Pendiente'].iloc[-1]

    st.markdown("### 🏦 Mi Estado de Cuenta")
    
    # Métricas una debajo de otra (mejor para móvil)
    st.metric("CAPITAL PENDIENTE", f"{cap_total}")
    st.metric("INTERÉS ACUMULADO", f"{int_total}")

    # Alerta de Estatus
    st.error("⚠️ ESTATUS: EN RIESGO")

    # Tabla con scroll lateral automático
    st.write("📋 **Últimos Movimientos**")
    st.dataframe(df_datos[['Fecha', 'Descripción', 'Abono a Capital']].tail(5), use_container_width=True)

    # Botón flotante simulado
    st.link_button("💬 SOLICITAR SOPORTE", "https://wa.me/tu_numero", use_container_width=True)

except:
    st.write("⌛ Actualizando datos...")

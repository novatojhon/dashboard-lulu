import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS para ocultar menús y definir el color rojo para el estatus
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px;
    }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #00ffcc !important; }
    
    /* Estilo para el texto en rojo */
    .status-rojo {
        color: #ff4b4b;
        font-size: 26px;
        font-weight: bold;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# URL de tu base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def clean_num(value):
    if str(value) == 'nan' or value == "": return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except:
        return 0.0

try:
    # Leer datos básicos
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]
    
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    df_limpio = df.dropna(subset=['Fecha']).copy()

    # --- LÓGICA FINANCIERA (La que ya funcionaba) ---
    total_interes_generado = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
    total_abonos_interes = df_limpio['Abono a Interés'].apply(clean_num).sum()
    interes_pendiente = total_interes_generado - total_abonos_interes
    
    # Capital: buscamos la última celda con datos
    ultima_fila_cap = df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]
    cap_pend = ultima_fila_cap['Saldo Capital Pendiente']

    # --- INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL PENDIENTE", f"{cap_pend}")
    c2.metric("INTERÉS ACUMULADO", f"${total_interes_generado:,.2f}".replace

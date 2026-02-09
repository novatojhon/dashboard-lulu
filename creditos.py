import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS Ajustado: Solo añadimos el color amarillo a los labels de las métricas
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px;
    }
    /* COLOR AMARILLO PARA LOS TÍTULOS DE LAS CUADRÍCULAS */
    [data-testid="stMetricLabel"] {
        color: #ffff00 !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] { 
        font-size: 26px !important; 
        color: #00ffcc !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# URL de la base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def clean_num(value):
    if pd.isna(value) or value == "" or value == 0: return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except:
        return 0.0

try:
    # Leer datos del cliente y tabla
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]
    
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    df_limpio = df.dropna(subset=['Fecha']).copy()

    # --- LÓGICA DE CÁLCULOS (INTACTA) ---
    total_gen = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
    total_pagado_int = df_limpio['Abono a Interés'].apply(clean_num).sum()
    int_pendiente = total_gen - total_pagado_int
    
    cap_pend = df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]['Saldo Capital Pendiente']

    # --- MOSTRAR INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL PENDIENTE", f"{cap_pend}")
    c2.metric("INTERÉS ACUMULADO", f"${total_gen:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    c3, c4 = st.columns(2)
    c3.metric("INTERÉS PENDIENTE", f"${int_pendiente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Estatus con color ROJO y título en AMARILLO
    with c4:

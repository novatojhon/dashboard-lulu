import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS: Mantenemos títulos amarillos, valores verde neón y añadimos estilo a la barra
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px;
    }
    [data-testid="stMetricLabel"] { color: #ffff00 !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #00ffcc !important; }
    
    /* Estilo para la barra de progreso */
    .stProgress > div > div > div > div {
        background-color: #00ffcc;
    }
    </style>
    """, unsafe_allow_html=True)

# URL de la base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def clean_num(value):
    if pd.isna(value) or value == "" or value == 0:
        return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except:
        return 0.0

try:
    # Leer datos
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]
    
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    df_limpio = df.dropna(subset=['Fecha']).copy()

    # --- LÓGICA DE CÁLCULOS ---
    total_gen = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
    total_pagado_int = df_limpio['Abono a Interés'].apply(clean_num).sum()
    int_pendiente = total_gen - total_pagado_int
    
    # Capital Inicial y Pendiente para la Barra
    cap_inicial = clean_num(df_limpio.iloc[0]['Saldo Capital Pendiente'])
    cap_actual = clean_num(df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]['Saldo Capital Pendiente'])
    
    # Calcular porcentaje pagado (evitando error si cap_inicial es 0)
    porcentaje_pagado = 0.0
    if cap_inicial > 0:
        total_abonado_cap = df_limpio['Abono a Capital'].apply(clean_num).sum()
        porcentaje_pagado = min(total_abonado_cap / cap_inicial, 1.0)

    # --- INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    # Insertar la Barra de Progreso
    st.write(f"📊 **Progreso de Pago de Capital: {int(porcentaje_pagado * 100)}%**")
    st.progress(porcentaje_pagado)
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2

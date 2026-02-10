import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS: Títulos amarillos y montos verde neón
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
    .stProgress > div > div > div > div { background-color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# ID de tu Google Sheets
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"

def clean_num(value):
    if pd.isna(value) or value == "" or value == 0: return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except: return 0.0

# --- MAPEO DE GIDs CORREGIDO SEGÚN TUS CAPTURAS ---
clientes = {
    "cliente1": "77813725",
    "cliente2": "1520750286",
    "cliente3": "1167219686", # FL2025
    "cliente4": "136743788",  # CORREGIDO (VH2025)
    "cliente5": "1738221516", # CORREGIDO (Cliente5)
    "cliente6": "650082110"   # MGZ2025
}

cliente_id = st.query_params.get("id")

if cliente_id in clientes:
    try:
        gid = clientes[cliente_id]
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        
        # Lectura de datos
        df_raw = pd.read_csv(url, header=None, nrows=1)
        nombre_cliente = df_raw.iloc[0, 2] # C1
        estatus_excel = df_raw.iloc[0, 4]  # E1
        
        df = pd.read_csv(url, skiprows=2)
        df.columns = df.columns.str.strip()
        df_limpio = df.dropna(subset=['Fecha']).copy()

        # Cálculos Financieros
        total_gen = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
        total_pagado_int = df_limpio['Abono a Interés'].apply(clean_num).sum()
        int_pendiente = total_gen - total_pagado_int
        
        cap_inicial = clean_num(df_limpio.iloc[0]['Saldo Capital Pendiente'])
        cap_actual = clean_num(df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]['Saldo Capital Pendiente'])
        total_abonado_cap = df_limpio['Abono a Capital'].apply(clean_num).sum()
        porcentaje = min(total_abonado_cap / cap_inicial, 1.0) if cap_inicial > 0 else 0.0

        # --- INTERFAZ ---
        st.markdown(f"### 🏦 {nombre_cliente}")
        st.write(f"📊 **Progreso de Pago: {int(porcentaje * 100)}%**")
        st.progress(porcentaje)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("CAPITAL PENDIENTE", f"${cap_actual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        c2.metric("INTERÉS ACUMULADO", f"${total_gen:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
      
    

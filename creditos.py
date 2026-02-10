import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS: Títulos amarillos, montos verde neón y barra de progreso
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

# --- LÓGICA DE PRIVACIDAD ---
# Captura el ID del cliente desde la URL (ejemplo: ?id=IEP)
query_params = st.query_params
cliente_id = query_params.get("id", None)

if cliente_id:
    try:
        # Cargamos la pestaña específica basada en el ID
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={cliente_id}"
        
        # Datos de cabecera
        df_raw = pd.read_csv(url, header=None, nrows=1)
        nombre_cliente = df_raw.iloc[0, 2]  # Celda C1
        estatus_excel = df_raw.iloc[0, 4]   # Celda E1
        
        # Datos de la tabla
        df = pd.read_csv(url, skiprows=2)
        df.columns = df.columns.str.strip()
        df_limpio = df.dropna(subset=['Fecha']).copy()

        # Cálculos exactos
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
        
        c3, c4 = st.columns(2)
        c3.metric("INTERÉS PENDIENTE", f"${int_pendiente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        with c4:
            # Color dinámico según la celda E1
            es_riesgo = str(estatus_excel).strip().upper() == "EN RIESGO"
            color_st = "#ff4b4b" if es_riesgo else "#00ffcc"
            st.markdown(f"""
                <div style="background-color: #111111; border: 1px solid {color_st}; border-radius: 12px; padding: 10px; text-align: center;">

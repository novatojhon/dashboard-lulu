import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# Estilo para que se vea impecable en celular
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
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # 1. Extraer nombre del cliente
    df_raw = pd.read_csv(url, header=None)
    nombre_cliente = df_raw.iloc[0, 2] 

    # 2. Leer tabla principal
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    
    # Limpiamos filas que no tengan fecha
    df = df.dropna(subset=['Fecha'])

    # 3. LÓGICA DE PRECISIÓN:
    # Buscamos la última fila que tenga el Saldo Capital Pendiente (Fila 6 en tu imagen actual)
    df_con_saldo = df[df['Saldo Capital Pendiente'].notrender() & (df['Saldo Capital Pendiente'] != 0)]
    
    if not df_con_saldo.empty:
        ultima_valida = df_con_saldo.iloc[-1]
        cap_total = ultima_valida['Saldo Capital Pendiente']
        int_total = ultima_valida['Saldo Interés Pendiente']
    else:
        # Si algo falla, toma la última fila disponible
        cap_total = df['Saldo Capital Pendiente'].iloc[-1]
        int_total = df['Saldo Interés Pendiente'].iloc[-1]

    # Extraer el interés generado (tomamos el último registro que tenga ese dato)
    col_int_gen = [c for
 

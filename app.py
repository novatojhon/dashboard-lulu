import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (Colores basados en el logo)
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide", page_icon="👗")

st.markdown("""
    <style>
    /* Estilo para las métricas con los colores del logo */
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #f2a7b5; } /* Rosa del logo */
    [data-testid="stMetricLabel"] { color: #88d4b3; font-weight: bold; } /* Verde del logo */
    .main { background-color: #ffffff; }
    hr { border-top: 2px solid #f2a7b5; }
    </style>
    """, unsafe_allow_html=True)

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

# --- ENCABEZADO CON TU LOGO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    # Usamos el logo cargado
    st.image("lulus6.png", width=120) 
with col_titulo:
    st.title("LULUS | Business Intelligence")
    st.write("Panel de Control: Clothing for Little Ones")

st.markdown("---")

# 2. CONEXIÓN (IDs verificados)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=704711518"

try:
    # 3. PROCESAMIENTO DE INVENTARIO
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # 4. MÉTRICAS SUPERIORES
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("💰 Inversiones", formato_moneda(2000.00))
    with m2: st.metric("🛒 Compras", formato_moneda(1825.17))
    with m3: st.metric("📈 Total Ventas", formato_moneda(425.00))
    with m4: st.metric("🏦 Caja", formato_moneda(599.84))
    with m5: st.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 5. SECCIÓN SUPER
    

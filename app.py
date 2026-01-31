import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (MANTENIDA)
st.set_page_config(page_title="Lulus Dashboard", layout="wide", page_icon="👗")

# Estilos CSS mejorados: Sombreado en tarjetas y encabezados rosas
st.markdown("""
    <style>
    /* Efecto de sombra para métricas */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #f2a7b5;
    }
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #f2a7b5; } 
    [data-testid="stMetricLabel"] { color: #88d4b3; font-weight: bold; }
    
    /* Encabezados de tablas en rosa LULUS */
    thead tr th {
        background-color: #f2a7b5 !important;
        color: white !important;
    }
    
    hr { border-top: 2px solid #f2a7b5; }
    </style>
    """, unsafe_allow_html=True)

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

# --- ENCABEZADO CON LOGO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("lulus6.png", width=140) 
    except:
        st.markdown("### LULUS")

with col_titulo:
    st.title("LULUS | Centro de Control")
    st.write("Clothing for Little Ones • Gestión Estratégica")

st.markdown("---")

# 2. CONEXIÓN A DATOS (ID MANTENIDOS)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=704711518"

try:
    # 3. PROCESAMIENTO INVENTARIO (LÓGICA INTACTA)
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    
    def limpiar_precio(serie):
        return pd.to_numeric(serie.astype(str).str.replace('$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)

    df_inv['Precio_Num'] = limpiar_precio(df_inv['Precio Venta'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # --- BARRA LATERAL: ALERTAS CRÍTICAS (MANTENIDA) ---
    with st.sidebar:
        st.header("🚨 Estado Crítico")
        agotados = df_inv[df_inv['Stock Actual'] == 0]['Prenda'].tolist()
        if agotados:
            for producto in agotados:
                st.error(f"AGOTADO: {producto}")
        else:
            st.success("Inventario al día")

    # 4. MÉTRICAS CON NOMBRES ELEGANTES
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("💰 Inversión Operativa", formato_moneda(2000.00))
    with m2: st.metric("🛒 Suministros", formato_moneda(1825.17))
    with m3: st.metric("📈 Volumen de Venta", formato_moneda(425.00))
    with m4: st.metric("🏦 Liquidez en Caja", formato_moneda(599.84))
    with m5: st.metric("📦 Valor en Stock", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 5. INVENTARIO Y TOP VENTAS
    c1, c2 = st.columns([1.2, 0.8], gap="large")

    with c1:
        st.subheader("📋 Disponibilidad de Prendas")
        busqueda = st.text_input("🔍 Buscar en colección...", key="search_bar")
        df_f = df_inv.copy()
        if busqueda:
            df_f = df_f[df_f['Prenda'].str.contains(busqueda, case=False)]
        
        def color_stock(val):
            if val == 0: return 'background-color: #fce4e4; color: #cc000

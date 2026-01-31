import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página profesional
st.set_page_config(page_title="Maestro Lulu Business Intelligence", layout="wide", page_icon="👗")

# Diseño estético con CSS
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1f1f1f; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👗 Maestro Lulu | Business Intelligence")
st.markdown("---")

# URL de tu Google Sheet (Hoja Inventario)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    # Carga de datos
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # --- BUSCADOR INTELIGENTE ---
    busqueda = st.text_input("🔍 Buscador de inventario (Escribe el nombre de la prenda...)", "")
    if busqueda:
        df = df[df['Prenda'].str.contains(busqueda, case=False)]

    # --- SECCIÓN 1: CINTAS FINANCIERAS ---
    # Calculamos la ganancia proyectada basada en Stock Actual y Precio Venta
    # Convertimos a número por si acaso vienen como texto
    stock_val = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0)
    precio_val = pd.to_numeric(df['Precio Venta'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    total_proyectado = (stock_val * precio_val).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", "$2,000.00")
    c2.metric("🛒 Compras", "$1,825.17")
    c3.metric("📈 Total Ventas", "$425.00")
    c4.metric("🏦 Caja + Proyección", f"${599.84 + total_proyectado:,.2f}")

    st.markdown("###")

    # --- SECCIÓN 2: INVENTARIO Y GRÁFICO ---
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📦 Detalle de Existencias")
        # Columnas solicitadas: Prenda, Stock Inicial, Stock Actual, Precio Venta
        cols_tab = ['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']
        st.dataframe(df[cols_tab], use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📊 Stock Actual")
        fig_stock = px.bar(df, x='Stock Actual', y='Prenda', orientation='h',
                          text='Stock Actual', color='Stock Actual',
                          color_continuous_scale='Greens')
        fig_stock.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_stock, use_container_width=True)

    # --- SECCIÓN 3: RENDIMIENTO ---
    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🔥 Lo más vendido")
        # Calculamos vendidos como Inicial - Actual
        df['Vendidos'] = pd.to_numeric(df['Stock Inicial'], errors='coerce') - pd.to_numeric(df['Stock Actual'], errors='coerce')
        vendidos_df = df[df['Vendidos'] > 0]
        
        if not vendidos_df.empty:
            fig_pie = px.pie(vendidos_df, values='Vendidos', names='Prenda', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Purp)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay ventas registradas todavía.")

    with col4:
        st.subheader("🏢 Valor del Inventario")
        df['Valor'] = stock_val * precio_val
        fig_val = px.treemap(df, path=['Prenda'], values='Valor',
                            color='Valor', color_continuous_scale='YlGn')
        st.plotly_chart(fig_val, use_container_width=True)

    # --- ALERTAS LATERALES ---
    st.sidebar.header("Sistema de Alertas")
    for _, row in df.iterrows():
        stk = row['Stock Actual']
        if stk == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")
        elif stk <= 2:
            st.sidebar.warning(f"⚠️ RECOMPRAR: {row['Prenda']} ({stk} und)")

except Exception as e:
    st.error(f"Error al conectar datos: {e}")

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración profesional
st.set_page_config(page_title="Maestro Lulu Business Intelligence", layout="wide", page_icon="👗")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# URL de tu Google Sheet
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # Limpieza de datos numéricos
    df['Stock Actual'] = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0)
    df['Stock Inicial'] = pd.to_numeric(df['Stock Inicial'], errors='coerce').fillna(0)
    df['Precio Venta'] = pd.to_numeric(df['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    
    # Cálculo de valor por producto (Dinero en estante)
    df['Valor Inventario'] = df['Stock Actual'] * df['Precio Venta']

    # --- MÉTRICAS SUPERIORES ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", "$2,000.00")
    c2.metric("🛒 Compras", "$1,825.17")
    c3.metric("📈 Total Ventas", "$425.00")
    # Sumamos el total de dinero que hay en ropa actualmente
    valor_total_ropa = df['Valor Inventario'].sum()
    c4.metric("🏦 Valor en Mercancía", f"${valor_total_ropa:,.2f}")

    st.markdown("###")

    # --- TABLA Y GRÁFICO ---
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📦 Detalle con Semáforo de Stock")
        
        # Función para dar color a las celdas de Stock Actual
        def color_stock(val):
            if val == 0: color = '#ff4b4b' # Rojo
            elif val <= 5: color = '#ffa500' # Naranja
            else: color = '#28a745' # Verde
            return f'background-color: {color}; color: white; font-weight: bold'

        cols_tab = ['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']
        st.dataframe(
            df[cols_tab].style.applymap(color_stock, subset=['Stock Actual']),
            use_container_width=True, 
            hide_index=True
        )

    with col2:
        st.subheader("💰 ¿Dónde está el dinero?")
        # Gráfico que muestra el valor monetario del stock actual
        fig_dinero = px.pie(df[df['Valor Inventario'] > 0], 
                           values='Valor Inventario', names='Prenda',
                           hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r,
                           title="Distribución de Valor en Ropa")
        st.plotly_chart(fig_dinero, use_container_width=True)

    # --- ALERTAS ---
    st.sidebar.header("Sistema de Alertas")
    agotados = df[df['Stock Actual'] == 0]['Prenda'].tolist()
    for prod in agotados:
        st.sidebar.error(f"🚫 AGOTADO: {prod}")

except Exception as e:
    st.error(f"Error al conectar con Maestro Lulu: {e}")

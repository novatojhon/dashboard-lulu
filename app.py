import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página con tema profesional
st.set_page_config(page_title="Maestro Lulu Pro", layout="wide", page_icon="👗")

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("👗 Maestro Lulu | Business Intelligence")
st.markdown("---")

# URL de tu Google Sheet
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    # Carga y limpieza
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # --- BUSCADOR INTELIGENTE ---
    with st.container():
        busqueda = st.text_input("🔍 Buscador de inventario (Escribe el nombre de la prenda...)", "")
        if busqueda:
            df = df[df['Prenda'].str.contains(busqueda, case=False)]

    # --- CÁLCULOS DE NEGOCIO ---
    df['Vendidos'] = df['Stock Inicial'] - df['Stock Actual']
    # Calculamos ganancia proyectada basada en lo que queda
    ganancia_proyectada = (df['Stock Actual'] * df['Precio Venta']).sum()

    # --- SECCIÓN 1: KPI CINTAS (REORDENADAS) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💰 Inversiones", "$2,000.00")
    with c2:
        st.metric("🛒 Compras", "$1,825.17")
    with c3:
        st.metric("📈 Total Ventas", "$425.00", delta="En curso")
    with c4:
        st.metric("🏦 En Caja", "$599.84", delta=f"${ganancia_proyectada:,.2f} por vender", delta_color="normal")

    st.markdown("###")

    # --- SECCIÓN 2: INVENTARIO Y GRÁFICO ---
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📦 Detalle de Existencias")
        cols_mostrar = ['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']
        st.dataframe(df[cols_mostrar].style.background_gradient(subset=['Stock Actual'], cmap='RdYlGn'), 
                     use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📊 Nivel de Stock")
        fig_stock = px.bar(df, x='Stock Actual', y='Prenda', orientation='h',
                          text='Stock Actual', color='Stock Actual',
                          color_continuous_scale='Greens', template="plotly_white")
        fig_stock.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_stock, use_container_width=True)

    st.divider()

    # --- SECCIÓN 3: VENTAS Y RENDIMIENTO ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🔥 Lo más vendido")
        if df['Vendidos'].sum() > 0:
            fig_pie = px.sunburst(df[df['Vendidos'] > 0], path=['Prenda'], values='Vendidos',
                                 color='Vendidos', color_continuous_scale='Purples')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aún no hay rotación de inventario registrada.")

    with col4:
        st.subheader("📅 Tendencia de Ventas")
        if 'Fecha' in df.columns:
            df_fecha = df.groupby('Fecha')['Vendidos'].sum().reset_index()
            fig_line = px.area(df_fecha, x='Fecha', y='Vendidos', 
                               title="Unidades vendidas por día", line_shape="spline")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Agrega una columna 'Fecha' en tu Excel para activar el historial diario.")

    # --- BARRA LATERAL (SEMÁFORO) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=100)
    st.sidebar.header("Sistema de Alertas")
    
    for _, row in df.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")
        elif row['Stock Actual'] <= 2:
            st.sidebar.warning(f"⚠️ RECOMPRAR: {row['Prenda']} ({row['Stock Actual']} und)")

except Exception as e:
    st.error(f"Conectando con la base de datos de Maestro Lulu... {e}")

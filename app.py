import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración visual
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide")

st.title("👗 Maestro Lulu: Panel de Control de Ventas")

# URL de tu Google Sheet (Ajustada a la hoja de 'Inventario')
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
# Usamos gid=0 porque es la pestaña de Inventario según tu imagen
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

# Carga de datos
try:
    df = pd.read_csv(url)
    
    # Limpiamos filas vacías para que no den error
    df = df.dropna(subset=['Prenda'])

    # --- SECCIÓN DE KPIs ---
    st.subheader("💰 Resumen Financiero")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inversión Inicial", "$2,000.00")
    c2.metric("Ventas Totales", "$425.00", delta="Activo")
    c3.metric("Caja", "$599.84")
    c4.metric("Compras", "$1,825.17")

    st.divider()

    # --- SECCIÓN DE INVENTARIO ---
    col_inv, col_graf = st.columns([1, 1])

    with col_inv:
        st.subheader("📦 Stock Actual")
        # Columnas según tu imagen: Prenda, Costo Unitario, Precio Venta, Stock Actual
        columnas_visibles = ['Prenda', 'Costo Unitario', 'Precio Venta', 'Stock Actual']
        st.dataframe(df[columnas_visibles], use_container_width=True)

    with col_graf:
        st.subheader("📊 Gráfico de Inventario")
        # Gráfico dinámico con tus columnas
        fig = px.bar(df, x='Prenda', y='Stock Actual', color='Stock Actual', 
                     color_continuous_scale='RdYlGn', title="Unidades disponibles")
        st.plotly_chart(fig, use_container_width=True)

    # --- ALERTAS EN LA BARRA LATERAL ---
    st.sidebar.header("⚠️ Alertas de Inventario")
    # Alerta si el Stock Actual es 0 o menos
    agotados = df[df['Stock Actual'] <= 0]['Prenda'].tolist()
    for prod in agotados:
        st.sidebar.error(f"¡AGOTADO!: {prod}")

except Exception as e:
    st.error(f"Estamos conectando con los datos... Si ves esto mucho tiempo, verifica que el Excel sea público. Error: {e}")

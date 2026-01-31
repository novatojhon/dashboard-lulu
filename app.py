import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración visual
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide")

st.title("👗 Maestro Lulu: Panel de Control de Ventas")

# URL de tu Google Sheet (formato exportable a CSV)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# Carga de datos
try:
    # Leemos el CSV y saltamos filas si es necesario (ajustado para tu estructura)
    df = pd.read_csv(url)
    
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
        # Mostramos solo las columnas relevantes si existen
        columnas_interes = ['Producto', 'Costo', 'Ganancia %', 'Venta', 'Stock']
        st.dataframe(df.filter(items=columnas_interes), use_container_width=True)

    with col_graf:
        st.subheader("📊 Gráfico de Inventario")
        if 'Producto' in df.columns and 'Stock' in df.columns:
            fig = px.bar(df, x='Producto', y='Stock', color='Stock', 
                         color_continuous_scale='RdYlGn', title="Unidades disponibles")
            st.plotly_chart(fig, use_container_width=True)

    # --- ALERTAS ---
    st.sidebar.header("⚠️ Alertas de Inventario")
    if 'Stock' in df.columns:
        agotados = df[df['Stock'] <= 0]['Producto'].tolist()
        for prod in agotados:
            st.sidebar.error(f"¡AGOTADO!: {prod}")

except Exception as e:
    st.error("Conectando con Google Sheets... asegúrate de que el enlace sea público.")

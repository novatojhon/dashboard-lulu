import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración visual
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide")

st.title("👗 Maestro Lulu: Control de Inventario")

# URL de tu Google Sheet (Ajustada a la hoja de 'Inventario')
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

# Carga de datos
try:
    df = pd.read_csv(url)
    
    # Limpiamos filas vacías para evitar errores visuales
    df = df.dropna(subset=['Prenda'])

    # --- SECCIÓN DE KPIs ---
    st.subheader("💰 Resumen Financiero")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inversión Inicial", "$2,000.00")
    c2.metric("Ventas Totales", "$425.00")
    c3.metric("Caja", "$599.84")
    c4.metric("Compras", "$1,825.17")

    st.divider()

    # --- SECCIÓN DE INVENTARIO ---
    col_inv, col_graf = st.columns([1, 1])

    with col_inv:
        st.subheader("📦 Comparativa de Stock")
        # Mostramos exactamente: Prenda, Stock Inicial y Stock Actual
        # Asegúrate de que en tu Excel los nombres sean idénticos
        columnas_visibles = ['Prenda', 'Stock Inicial', 'Stock Actual']
        st.dataframe(df[columnas_visibles], use_container_width=True, hide_index=True)

    with col_graf:
        st.subheader("📊 Visualización de Existencias")
        # Gráfico que muestra el Stock Actual de cada prenda
        fig = px.bar(df, x='Prenda', y='Stock Actual', 
                     text='Stock Actual',
                     color='Stock Actual', 
                     color_continuous_scale='Greens',
                     title="Unidades en Mano")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # --- BARRA LATERAL CON ALERTAS ---
    st.sidebar.header("⚠️ Estado Crítico")
    # Filtramos productos que ya no tienen nada
    agotados = df[df['Stock Actual'] <= 0]['Prenda'].tolist()
    if agotados:
        for prod in agotados:
            st.sidebar.error(f"AGOTADO: {prod}")
    else:
        st.sidebar.success("✅ Todo está en stock")

except Exception as e:
    st.error(f"Actualizando datos... Si el error persiste, revisa que el Excel sea público. Error: {e}")

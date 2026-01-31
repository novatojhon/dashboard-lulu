import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

# Función para dar formato de moneda regional ($ 1.234,56)
def formato_moneda(valor):
    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # Conversión a números enteros para Stocks (Sin decimales)
    df['Stock Actual'] = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df['Stock Inicial'] = pd.to_numeric(df['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    
    # Limpieza de Precios y cálculos
    df['Precio Venta'] = pd.to_numeric(df['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Vendidos'] = df['Stock Inicial'] - df['Stock Actual']
    df['Valor Inventario'] = df['Stock Actual'] * df['Precio Venta']

    # --- 1. RESUMEN FINANCIERO ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. INVENTARIO Y VALOR (Con más espacio) ---
    col1, col2 = st.columns([1.1, 0.9], gap="large") # Agregamos 'gap' para que no se amontonen

    with col1:
        st.subheader("📦 Semáforo de Inventario")
        df_display = df[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        
        def color_stock(val):
            if val == 0: color = '#ff4b4b'
            elif val <= 5: color = '#ffa500'
            else: color = '#28a745'
            return f'background-color: {color}; color: white; font-weight: bold;'

        # Formatear Precio Venta solo para mostrar en tabla
        df_display['Precio Venta'] = df_display['Precio Venta'].apply(formato_moneda)

        st.dataframe(
            df_display.style.applymap(color_stock, subset=['Stock Actual']),
            use_container_width=True, 
            hide_index=True,
            height=400 # Altura fija para evitar saltos
        )

    with col2:
        st.subheader("💰 Distribución de Capital")
        # Gráfico de anillo más limpio y pequeño para que no choque
        fig_dinero = px.pie(df[df['Valor Inventario'] > 0], 
                           values='Valor Inventario', names='Prenda',
                           hole=0.6, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_dinero.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_dinero, use_container_width=True)

    st.divider()

    # --- 3. RENDIMIENTO ---
    st.subheader("🔥 Rendimiento de Ventas")
    col3, col4 = st.columns(2, gap="large")

    with col3:
        # Gráfico de barras de lo más vendido
        vendidos_df = df[df['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not vendidos_df.empty:
            fig_bar = px.bar(vendidos_df, x='Vendidos', y='Prenda', 
                             orientation='h', color='Vendidos', 
                             color_continuous_scale='Purples',
                             title="Unidades Vendidas por Artículo",
                             text_auto='.0f') # Solo números enteros
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas.")

    with col4:
        # En lugar del aviso de Excel, mostraremos la Participación de Ventas en Dinero
        df['Dinero Ventas'] = df['Vendidos'] * df['Precio Venta']
        ventas_dinero_df = df[df['Dinero Ventas'] > 0]
        
        if not ventas_dinero_df.empty:
            fig_ventas = px.bar(ventas_dinero_df, x='Prenda', y='Dinero Ventas',
                               title="Ingresos Generados por Prenda",
                               color_discrete_sequence=['#28a745'])
            st.plotly_chart(fig_ventas, use_container_width=True)
        else:
            st.info("Esperando datos de ventas para mostrar ingresos.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas de Stock")
    for _, row in df.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st.error(f"Error al organizar el dashboard: {e}")

  
 

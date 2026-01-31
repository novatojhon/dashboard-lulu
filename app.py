import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

# Función para dar formato de moneda regional ($ 1.234,56)
def formato_moneda(valor):
    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("👗 Maestro Lulu | Dashboard Integral")
st.markdown("---")

sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # Conversión a números enteros para Stocks
    df['Stock Actual'] = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df['Stock Inicial'] = pd.to_numeric(df['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    
    # Limpieza de Precios
    df['Precio Venta'] = pd.to_numeric(df['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Vendidos'] = df['Stock Inicial'] - df['Stock Actual']
    df['Valor Inventario'] = df['Stock Actual'] * df['Precio Venta']

    # --- 1. RESUMEN FINANCIERO (Con formato regional) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. INVENTARIO Y VALOR ---
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📦 Semáforo de Inventario")
        
        # Formatear la tabla para mostrar enteros y moneda
        df_display = df[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        
        def color_stock(val):
            if val == 0: color = '#ff4b4b'
            elif val <= 5: color = '#ffa500'
            else: color = '#28a745'
            return f'background-color: {color}; color: white;'

        # Aplicar formato de moneda a la columna Precio Venta en la vista
        df_display['Precio Venta'] = df_display['Precio Venta'].apply(formato_moneda)

        st.dataframe(
            df_display.style.applymap(color_stock, subset=['Stock Actual']),
            use_container_width=True, 
            hide_index=True
        )

    with col2:
        st.subheader("💰 Inversión por Prenda")
        fig_dinero = px.pie(df[df['Valor Inventario'] > 0], 
                           values='Valor Inventario', names='Prenda',
                           hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_dinero.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_dinero, use_container_width=True)

    st.divider()

    # --- 3. RENDIMIENTO Y VENTAS ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🔥 Lo más vendido (Unidades)")
        vendidos_df = df[df['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not vendidos_df.empty:
            fig_bar = px.bar(vendidos_df, x='Vendidos', y='Prenda', 
                             orientation='h', color='Vendidos', 
                             color_continuous_scale='Purples',
                             text_auto='.0f') # .0f fuerza a números enteros
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas.")

    with col4:
        st.subheader("📅 Historial de Ventas")
        if 'Fecha' in df.columns:
            df_fecha = df.groupby('Fecha')['Vendidos'].sum().reset_index()
            fig_line = px.area(df_fecha, x='Fecha', y='Vendidos', color_discrete_sequence=['#28a745'])
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("💡 Tip: Agrega una columna 'Fecha' en tu Excel para activar esta gráfica.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas de Stock")
    for _, row in df.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st.error(f"Error en formato de datos: {e}")

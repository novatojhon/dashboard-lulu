import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración Inicial (Mantenida)
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

st.title("👗 Maestro Lulu | Business Intelligence")
st.markdown("---")

# IDs de conexión (Verificar que el GID de Ventas Diarias sea 1119747535)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1119747535"

try:
    # 2. CARGA DE INVENTARIO (Sin cambios para no dañar lo anterior)
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # 3. MÉTRICAS (Las 5 que pediste)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Caja", formato_moneda(599.84))
    c5.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 4. SECCIÓN SUPERIOR (TABLA | BARRAS LO MÁS VENDIDO)
    col_izq, col_der = st.columns([1.2, 0.8], gap="large")

    with col_izq:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", "")
        df_f = df_inv.copy()
        if busqueda:
            df_f = df_f[df_f['Prenda'].str.contains(busqueda, case=False)]
        
        def color_stock(val):
            if val == 0: return 'background-color: #ff4b4b; color: white; font-weight: bold;'
            elif val <= 5: return 'background-color: #ffa500; color: white; font-weight: bold;'
            else: return 'background-color: #28a745; color: white; font-weight: bold;'

        view_inv = df_f[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        view_inv['Precio Venta'] = df_f['Precio_Num'].apply(formato_moneda)
        st.dataframe(view_inv.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=380)

    with col_der:
        st.subheader("🔥 Lo Más Vendido (Unidades)")
        df_top = df_inv[df_inv['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not df_top.empty:
            fig_bar = px.bar(df_top, x='Vendidos', y='Prenda', orientation='h',
                             color_discrete_sequence=['#28a745'], text_auto='.0f')
            fig_bar.update_layout(showlegend=False, xaxis_title="Unidades", yaxis_title="", margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 5. SECCIÓN INFERIOR: TENDENCIA DE VENTAS POR DÍA (CORREGIDA)
    st.subheader("📅 Tendencia de Ventas por Día")
    try:
        # Forzamos la descarga para evitar el error 400
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha'])
        
        # Limpieza robusta del campo Total
        df_v['Total_Num'] = pd.to_numeric(df_v['Total'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
        
        # Agrupamos por fecha
        df_diario = df_v.groupby('Fecha')['Total_Num'].sum().reset_index()
        
        # Gráfica de tendencia
        fig_trend = px.bar(df_diario, x='Fecha', y='Total_Num', 
                           color_discrete_sequence=['#1f77b4'],
                           text_auto=True, title="Ventas Totales por Día ($)")
        
        fig_trend.update_layout(xaxis_title="Día", yaxis_title="Monto Vendido", height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Detalle de la tabla de ventas
        st.markdown("**Registro Detallado de Ventas**")
        df_v_show = df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']].copy()
        st.dataframe(df_v_show, use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Aviso: Asegúrate de que la pestaña 'Ventas Diarias' tenga datos válidos. Error: {e}")

except Exception as e:
    st.error(f"Error de conexión general: {e}")

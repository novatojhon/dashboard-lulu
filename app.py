import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Mantenida intacta)
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide", page_icon="👗")

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# 2. Conexión con los IDs correctos
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=704711518"

try:
    # 3. CARGA DE INVENTARIO
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    # Limpieza corregida: quitamos el punto de miles y cambiamos coma por punto decimal
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # 4. MÉTRICAS SUPERIORES
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Inversiones", formato_moneda(2000.00))
    m2.metric("🛒 Compras", formato_moneda(1825.17))
    m3.metric("📈 Total Ventas", formato_moneda(425.00))
    m4.metric("🏦 Caja", formato_moneda(599.84))
    m5.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 5. SECCIÓN SUPERIOR: INVENTARIO (IZQ) | LO MÁS VENDIDO (DER)
    col_izq, col_der = st.columns([1.2, 0.8], gap="large")

    with col_izq:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", key="search_bar")
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

    # 6. SECCIÓN INFERIOR: VENTAS POR DÍA (GRÁFICA CORREGIDA)
    st.subheader("📅 Total de Ventas por Día")
    try:
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha', 'Total'])
        
        # CORRECCIÓN CLAVE: Limpiamos el campo 'Total' para que el gráfico no sume mal
        # Eliminamos el símbolo $, luego eliminamos el punto de miles, y cambiamos coma por punto
        df_v['Total_Limpio'] = df_v['Total'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True)
        df_v['Total_Num'] = pd.to_numeric(df_v['Total_Limpio'], errors='coerce').fillna(0)
        
        # Agrupar por fecha usando el valor numérico real
        df_diario = df_v.groupby('Fecha')['Total_Num'].sum().reset_index()
        
        # Gráfica de barras unicolor con valores reales
        fig_trend = px.bar(df_diario, x='Fecha', y='Total_Num', 
                           color_discrete_sequence=['#1f77b4'], 
                           text_auto=True)
        
        fig_trend.update_layout(xaxis_title="Día", yaxis_title="Dinero Vendido ($)", height=400)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("**Detalle de Ventas Diarias**")
        # Mostramos la tabla original que mencionas que está correcta
        st.dataframe(df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Error al cargar la gráfica de ventas: {e}")

except Exception as e:
    st.error(f"Error general de conexión: {e}")

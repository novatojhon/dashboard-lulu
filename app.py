import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

# Función para formato de moneda regional ($ 1.234,56)
def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# IDs de conexión
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1119747535"

try:
    # 1. CARGA Y LIMPIEZA DE INVENTARIO
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    
    # Asegurar que los Stocks sean enteros para la tabla
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    
    # Cálculos financieros
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # --- 1. TOTALES SUPERIORES ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Caja", formato_moneda(599.84))
    c5.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. SECCIÓN SUPERIOR: INVENTARIO | BARRAS ---
    col_izq, col_der = st.columns([1.2, 0.8], gap="large")

    with col_izq:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", "")
        df_f = df_inv.copy()
        if busqueda:
            df_f = df_f[df_f['Prenda'].str.contains(busqueda, case=False)]
        
        # Formato de la tabla
        def color_stock(val):
            if val == 0: return 'background-color: #ff4b4b; color: white; font-weight: bold;'
            elif val <= 5: return 'background-color: #ffa500; color: white; font-weight: bold;'
            else: return 'background-color: #28a745; color: white; font-weight: bold;'

        # Preparar vista con formatos correctos
        view_inv = df_f[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        view_inv['Precio Venta'] = df_f['Precio_Num'].apply(formato_moneda)
        
        st.dataframe(view_inv.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=380)

    with col_der:
        st.subheader("🔥 Lo Más Vendido")
        # Gráfico de barras horizontales sin leyenda
        df_top = df_inv[df_inv['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not df_top.empty:
            fig_bar = px.bar(df_top, x='Vendidos', y='Prenda', orientation='h',
                             color_discrete_sequence=['#28a745'], text_auto='.0f')
            fig_bar.update_layout(showlegend=False, xaxis_title="Unidades", yaxis_title="", 
                                 margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún.")

    st.divider()

    # --- 3. SECCIÓN INFERIOR: VENTAS DIARIAS ---
    st.subheader("📅 Detalle de Ventas Diarias")
    try:
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha'])
        df_v_view = df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']].copy()
        # Formatear el total en la tabla de ventas
        df_v_view['Total'] = df_v_view['Total'].apply(lambda x: formato_moneda(str(x).replace('$', '').replace('.', '').replace(',', '.')))
        st.dataframe(df_v_view, use_container_width=True, hide_index=True)
    except:
        st.error("Error al cargar la pestaña 'Ventas Diarias'.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas Críticas")
    for _, row in df_inv.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st.error(f"Error en el sistema: {e}")

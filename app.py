import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro (No se toca)
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
    # 1. CARGA Y LIMPIEZA DE INVENTARIO (MANTENIDO)
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # --- TOTALES SUPERIORES (MANTENIDO CON CAJA) ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Caja", formato_moneda(599.84))
    c5.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # --- SECCIÓN SUPERIOR: INVENTARIO | BARRAS (MANTENIDO) ---
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
        st.subheader("🔥 Lo Más Vendido")
        df_top = df_inv[df_inv['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not df_top.empty:
            fig_bar = px.bar(df_top, x='Vendidos', y='Prenda', orientation='h',
                             color_discrete_sequence=['#28a745'], text_auto='.0f')
            fig_bar.update_layout(showlegend=False, xaxis_title="Unidades", yaxis_title="", 
                                 margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 3. SECCIÓN INFERIOR: GRÁFICA DE VENTAS POR DÍA ---
    st.subheader("📅 Tendencia de Ventas por Día")
    try:
        # Carga de ventas diarias
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha', 'Total'])
        
        # Limpieza del campo Total para que sea numérico
        df_v['Total_Num'] = pd.to_numeric(df_v['Total'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
        
        # Agrupamos por fecha para obtener el total diario
        ventas_diarias = df_v.groupby('Fecha')['Total_Num'].sum().reset_index()
        
        # Gráfica de barras para ventas por día
        fig_dia = px.bar(ventas_diarias, x='Fecha', y='Total_Num', 
                         title="Ventas Totales ($) por Fecha",
                         color_discrete_sequence=['#1f77b4'],
                         text_auto=True)
        
        fig_dia.update_layout(yaxis_title="Monto Total ($)", xaxis_title="Día", height=400)
        st.plotly_chart(fig_dia, use_container_width=True)
        
        # Tabla de detalle (mantenida como pediste)
        st.markdown("**Detalle de Transacciones Diarias**")
        df_v_view = df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']].copy()
        st.dataframe(df_v_view, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error al generar gráfica de ventas: {e}")

except Exception as e:
    st.error(f"Error en el sistema: {e}")

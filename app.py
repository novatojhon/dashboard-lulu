import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

# Función para formato de moneda regional
def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# ID de tu Google Sheet
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"

# URLs para las pestañas (Inventario gid=0, Ventas Diarias gid=1119747535)
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1119747535"

try:
    # --- CARGA DE DATOS ---
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    
    # Limpieza de Inventario
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Precio Venta Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio Venta Num']

    # --- 1. MÉTRICAS SUPERIORES ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. SECCIÓN SUPERIOR: INVENTARIO (IZQ) | ANILLO (DER) ---
    col_izq, col_der = st.columns([1.2, 0.8], gap="large")

    with col_izq:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", "")
        
        df_filtrado = df_inv.copy()
        if busqueda:
            df_filtrado = df_filtrado[df_filtrado['Prenda'].str.contains(busqueda, case=False)]
        
        def color_stock(val):
            if val == 0: return 'background-color: #ff4b4b; color: white; font-weight: bold;'
            elif val <= 5: return 'background-color: #ffa500; color: white; font-weight: bold;'
            else: return 'background-color: #28a745; color: white; font-weight: bold;'

        view_inv = df_filtrado[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        st.dataframe(view_inv.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=380)

    with col_der:
        st.subheader("💰 Distribución de Capital")
        fig_pie = px.pie(df_inv[df_inv['Valor Inventario'] > 0], 
                        values='Valor Inventario', names='Prenda', hole=0.6,
                        color_discrete_sequence=px.colors.sequential.Greens_r)
        # ELIMINAR LEYENDA Y MEJORAR ETIQUETAS
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10))
        fig_pie.update_traces(textinfo='label+percent', textposition='outside')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # --- 3. SECCIÓN INFERIOR: TABLA DE VENTAS DIARIAS ---
    st.subheader("📅 Detalle de Ventas Diarias")
    try:
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha'])
        
        # Ajustamos los nombres de columnas para que se vean bien
        df_v_view = df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']].copy()
        
        # Aplicamos formato de moneda a la columna Total
        df_v_view['Total'] = df_v_view['Total'].apply(lambda x: formato_moneda(str(x).replace('$', '').replace('.', '').replace(',', '.')))
        
        st.dataframe(df_v_view, use_container_width=True, hide_index=True)
    except:
        st.info("Conectando con la pestaña de Ventas Diarias... Verifica que la hoja sea pública.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas Críticas")
    for _, row in df_inv.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st.error(f"Error en el dashboard: {e}")

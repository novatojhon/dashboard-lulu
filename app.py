import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Pro
st.set_page_config(page_title="Maestro Lulu Master Dashboard", layout="wide", page_icon="👗")

# Función para formato de moneda regional
def formato_moneda(valor):
    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# ID de tu Google Sheet
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"

# URL para la hoja de Inventario (gid=0)
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
# URL para la hoja de Ventas Diarias (Basado en tu imagen, probamos el gid de la siguiente pestaña)
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1119747535"

try:
    # 1. CARGA DE INVENTARIO
    df = pd.read_csv(url_inv)
    df = df.dropna(subset=['Prenda'])
    
    # Limpieza de datos
    df['Stock Actual'] = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df['Stock Inicial'] = pd.to_numeric(df['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df['Precio Venta'] = pd.to_numeric(df['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Valor Inventario'] = df['Stock Actual'] * df['Precio Venta']

    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df['Valor Inventario'].sum()))

    st.markdown("###")

    # --- SECCIÓN SUPERIOR (TABLA IZQ | ANILLO DER SIN LEYENDA) ---
    col_izq, col_der = st.columns([1.2, 0.8], gap="large")

    with col_izq:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", "")
        
        df_display = df.copy()
        if busqueda:
            df_display = df_display[df_display['Prenda'].str.contains(busqueda, case=False)]
        
        def color_stock(val):
            if val == 0: return 'background-color: #ff4b4b; color: white;'
            elif val <= 5: return 'background-color: #ffa500; color: white;'
            else: return 'background-color: #28a745; color: white;'

        tabla_view = df_display[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        tabla_view['Precio Venta'] = tabla_view['Precio Venta'].apply(formato_moneda)
        
        st.dataframe(tabla_view.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=350)

    with col_der:
        st.subheader("💰 Distribución de Capital")
        fig_dinero = px.pie(df[df['Valor Inventario'] > 0], 
                           values='Valor Inventario', names='Prenda',
                           hole=0.6, color_discrete_sequence=px.colors.sequential.Greens_r)
        # ELIMINAMOS LA LEYENDA AQUÍ
        fig_dinero.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        fig_dinero.update_traces(textinfo='label+percent')
        st.plotly_chart(fig_dinero, use_container_width=True)

    st.divider()

    # --- 2. SECCIÓN INFERIOR: VENTAS POR DÍA ---
    st.subheader("📅 Detalle de Ventas Diarias por Producto")
    
    try:
        df_v = pd.read_csv(url_ventas)
        if 'Fecha' in df_v.columns:
            # Mostramos la tabla de ventas tal cual está en tu pestaña
            st.dataframe(df_v, use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontró la columna 'Fecha' en la pestaña de Ventas Diarias.")
    except:
        st.info("Conectando con la pestaña de Ventas Diarias... Asegúrate de que el nombre sea exacto.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas Críticas")
    for _, row in df.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st

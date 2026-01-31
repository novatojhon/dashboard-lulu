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

sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

try:
    df = pd.read_csv(url)
    df = df.dropna(subset=['Prenda'])
    
    # --- CÁLCULOS Y LIMPIEZA ---
    df['Stock Actual'] = pd.to_numeric(df['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df['Stock Inicial'] = pd.to_numeric(df['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df['Precio Venta'] = pd.to_numeric(df['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Valor Inventario'] = df['Stock Actual'] * df['Precio Venta']

    # --- 1. MÉTRICAS RÁPIDAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. SECCIÓN SUPERIOR (INVENTARIO IZQ | ANILLO DER) ---
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

        # Vista de tabla
        tabla_view = df_display[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        tabla_view['Precio Venta'] = tabla_view['Precio Venta'].apply(formato_moneda)
        
        st.dataframe(tabla_view.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=350)

    with col_der:
        st.subheader("💰 Distribución de Capital")
        fig_dinero = px.pie(df[df['Valor Inventario'] > 0], 
                           values='Valor Inventario', names='Prenda',
                           hole=0.6, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_dinero.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
        st.plotly_chart(fig_dinero, use_container_width=True)

    st.divider()

    # --- 3. SECCIÓN INFERIOR: VENTAS DIARIAS POR PRODUCTO ---
    st.subheader("📅 Detalle de Ventas Diarias por Producto")
    
    # Para que esto funcione, el Excel debe tener columnas: 'Fecha', 'Prenda' y 'Monto Venta' (o similar)
    if 'Fecha' in df.columns:
        # Aquí agrupamos por Fecha y Prenda para ver el total por día de cada cosa
        # Si usas la misma hoja de inventario, esto asume que tienes registros de fecha ahí
        df_ventas = df.dropna(subset=['Fecha'])
        df_ventas['Monto_Num'] = pd.to_numeric(df_ventas['Precio Venta'], errors='coerce').fillna(0)
        
        resumen_diario = df_ventas.groupby(['Fecha', 'Prenda'])['Monto_Num'].sum().reset_index()
        resumen_diario.columns = ['Fecha', 'Producto Vendido', 'Total del Día']
        
        # Formatear moneda para la tabla
        resumen_diario['Total del Día'] = resumen_diario['Total del Día'].apply(formato_moneda)
        
        st.dataframe(resumen_diario, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Para mostrar las ventas diarias, asegúrate de que tu Excel tenga una columna llamada 'Fecha'.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas Críticas")
    agotados = df[df['Stock Actual'] == 0]['Prenda'].tolist()
    for prod in agotados:
        st.sidebar.error(f"🚫 AGOTADO: {prod}")

except Exception as e:
    st.error(f"Error al organizar el dashboard: {e}")

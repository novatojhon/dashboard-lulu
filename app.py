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
    
    # --- BUSCADOR INTELIGENTE (Arriba para fácil acceso) ---
    busqueda = st.text_input("🔍 Buscar prenda en el inventario...", "")
    if busqueda:
        df_filtrado = df[df['Prenda'].str.contains(busqueda, case=False)]
    else:
        df_filtrado = df

    # Conversión de datos
    df_filtrado['Stock Actual'] = pd.to_numeric(df_filtrado['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_filtrado['Precio Venta'] = pd.to_numeric(df_filtrado['Precio Venta'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df_filtrado['Valor Inventario'] = df_filtrado['Stock Actual'] * df_filtrado['Precio Venta']

    # --- 1. RESUMEN FINANCIERO ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Inversiones", formato_moneda(2000.00))
    c2.metric("🛒 Compras", formato_moneda(1825.17))
    c3.metric("📈 Total Ventas", formato_moneda(425.00))
    c4.metric("🏦 Valor en Mercancía", formato_moneda(df_filtrado['Valor Inventario'].sum()))

    st.markdown("###")

    # --- 2. SECCIÓN SUPERIOR: SOLO ANILLO ---
    st.subheader("💰 Distribución de Capital (Inversión en Stock)")
    fig_dinero = px.pie(df_filtrado[df_filtrado['Valor Inventario'] > 0], 
                       values='Valor Inventario', names='Prenda',
                       hole=0.6, color_discrete_sequence=px.colors.sequential.Greens_r)
    fig_dinero.update_layout(margin=dict(t=30, b=30, l=0, r=0))
    st.plotly_chart(fig_dinero, use_container_width=True)

    st.divider()

    # --- 3. SECCIÓN MEDIA: TABLA DE INVENTARIO ---
    st.subheader("📦 Estado del Inventario")
    def color_stock(val):
        if val == 0: return 'background-color: #ff4b4b; color: white;'
        elif val <= 5: return 'background-color: #ffa500; color: white;'
        else: return 'background-color: #28a745; color: white;'

    df_inv_view = df_filtrado[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
    df_inv_view['Precio Venta'] = df_inv_view['Precio Venta'].apply(formato_moneda)
    
    st.dataframe(df_inv_view.style.applymap(color_stock, subset=['Stock Actual']),
                 use_container_width=True, hide_index=True)

    st.divider()

    # --- 4. SECCIÓN INFERIOR: VENTAS POR DÍA ---
    st.subheader("📅 Resumen de Ventas Diarias")
    
    # Intentamos leer la columna de fecha si existe para hacer el resumen
    if 'Fecha' in df.columns:
        # Asumimos que hay una columna 'Total Ventas' o calculamos una
        df['Ventas_Num'] = pd.to_numeric(df['Total Ventas'].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
        ventas_dia = df.groupby('Fecha')['Ventas_Num'].sum().reset_index()
        ventas_dia.columns = ['Fecha', 'Monto Total Vendido']
        
        # Formatear el monto para la tabla
        ventas_dia_ver = ventas_dia.copy()
        ventas_dia_ver['Monto Total Vendido'] = ventas_dia_ver['Monto Total Vendido'].apply(formato_moneda)
        
        st.table(ventas_dia_ver) # Usamos st.table para que se vea más limpio
    else:
        st.info("Para activar la tabla de ventas diarias, asegúrate de tener una columna llamada 'Fecha' en tu Excel.")

    # --- SIDEBAR ---
    st.sidebar.header("Alertas Críticas")
    for _, row in df.iterrows():
        if row['Stock Actual'] == 0:
            st.sidebar.error(f"🚫 AGOTADO: {row['Prenda']}")

except Exception as e:
    st.error(f"Error al organizar el dashboard: {e}")
  
 

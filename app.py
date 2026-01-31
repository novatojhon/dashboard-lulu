import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Intacta)
st.set_page_config(page_title="Maestro Lulu Dashboard", layout="wide", page_icon="👗")

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

st.title("👗 Maestro Lulu | Dashboard de Negocio")
st.markdown("---")

# 2. Conexión con los IDs (gid=0 Inventario, gid=704711518 Ventas)
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=704711518"

try:
    # 3. CARGA DE INVENTARIO (Sin cambios)
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    
    # Limpieza para cálculos de inventario
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # 4. MÉTRICAS SUPERIORES (Las 5 fijas)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Inversiones", formato_moneda(2000.00))
    m2.metric("🛒 Compras", formato_moneda(1825.17))
    m3.metric("📈 Total Ventas", formato_moneda(425.00))
    m4.metric("🏦 Caja", formato_moneda(599.84))
    m5.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 5. SECCIÓN SUPERIOR: INVENTARIO | LO MÁS VENDIDO (Sin cambios)
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

    # 6. SECCIÓN INFERIOR: VENTAS POR DÍA (GRÁFICA CON TOTALES CORREGIDOS)
    st.subheader("📅 Total de Ventas por Día")
    try:
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha', 'Total'])
        
        # PROCESAMIENTO MATEMÁTICO DEL TOTAL (Igual a la tabla)
        # 1. Quitamos el símbolo $ y espacios
        # 2. Quitamos los puntos de miles (muy importante para que no multiplique el valor)
        # 3. Cambiamos la coma decimal por punto para que Python lo entienda
        df_v['Total_Para_Grafico'] = (
            df_v['Total'].astype(str)
            .str.replace('$', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )
        df_v['Total_Num'] = pd.to_numeric(df_v['Total_Para_Grafico'], errors='coerce').fillna(0)
        
        # Agrupamos por fecha sumando los valores numéricos correctos
        df_diario = df_v.groupby('Fecha')['Total_Num'].sum().reset_index()
        
        # Gráfica Unicolor
        fig_trend = px.bar(df_diario, x='Fecha', y='Total_Num', 
                           color_discrete_sequence=['#1f77b4'], text_auto=True)
        
        fig_trend.update_layout(
            xaxis_title="Día", 
            yaxis_title="Monto Real Vendido ($)", 
            height=400,
            yaxis=dict(tickformat=",.2f") # Esto asegura que el eje Y también se vea bien
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("**Detalle de Ventas Diarias**")
        st.dataframe(df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Error al procesar totales: {e}")

except Exception as e:
    st.error(f"Error de conexión general: {e}")

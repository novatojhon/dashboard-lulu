import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
st.set_page_config(page_title="Lulus Dashboard", layout="wide", page_icon="👗")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #f2a7b5; } 
    [data-testid="stMetricLabel"] { color: #88d4b3; font-weight: bold; }
    hr { border-top: 2px solid #f2a7b5; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def formato_moneda(valor):
    try:
        return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

# --- ENCABEZADO CON LOGO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("lulus6.png", width=140) 
    except:
        st.markdown("### LULUS")

with col_titulo:
    st.title("LULUS | Business Intelligence")
    st.write("Panel de Control: Clothing for Little Ones")

st.markdown("---")

# 2. CONEXIÓN A DATOS
sheet_id = "1eTx9A4Gdvo17nliZ8J2FHVwa72Vq9lmUJCcGXmXNTGs"
url_inv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_ventas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=704711518"

try:
    # 3. PROCESAMIENTO INVENTARIO
    df_inv = pd.read_csv(url_inv).dropna(subset=['Prenda'])
    df_inv['Stock Actual'] = pd.to_numeric(df_inv['Stock Actual'], errors='coerce').fillna(0).astype(int)
    df_inv['Stock Inicial'] = pd.to_numeric(df_inv['Stock Inicial'], errors='coerce').fillna(0).astype(int)
    df_inv['Precio_Num'] = pd.to_numeric(df_inv['Precio Venta'].astype(str).replace('[\$,]', '', regex=True).replace('\.', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0)
    df_inv['Valor Inventario'] = df_inv['Stock Actual'] * df_inv['Precio_Num']
    df_inv['Vendidos'] = df_inv['Stock Inicial'] - df_inv['Stock Actual']

    # --- BARRA LATERAL: ALERTAS CRÍTICAS ---
    with st.sidebar:
        st.header("🚨 Alertas Críticas")
        agotados = df_inv[df_inv['Stock Actual'] == 0]['Prenda'].tolist()
        if agotados:
            for producto in agotados:
                st.error(f"AGOTADO: {producto}")
        else:
            st.success("Inventario al día")

    # 4. MÉTRICAS SUPERIORES
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("💰 Inversiones", formato_moneda(2000.00))
    with m2: st.metric("🛒 Compras", formato_moneda(1825.17))
    with m3: st.metric("📈 Total Ventas", formato_moneda(425.00))
    with m4: st.metric("🏦 Caja", formato_moneda(599.84))
    with m5: st.metric("📦 Valor Mercancía", formato_moneda(df_inv['Valor Inventario'].sum()))

    st.markdown("###")

    # 5. INVENTARIO Y TOP VENTAS
    c1, c2 = st.columns([1.2, 0.8], gap="large")

    with c1:
        st.subheader("📦 Control de Inventario")
        busqueda = st.text_input("🔍 Buscar prenda...", key="search_bar")
        df_f = df_inv.copy()
        if busqueda:
            df_f = df_f[df_f['Prenda'].str.contains(busqueda, case=False)]
        
        def color_stock(val):
            if val == 0: return 'background-color: #fce4e4; color: #cc0000; font-weight: bold;'
            elif val <= 5: return 'background-color: #fff9e6; color: #997a00; font-weight: bold;'
            else: return 'background-color: #e6f9f0; color: #006633; font-weight: bold;'

        view_inv = df_f[['Prenda', 'Stock Inicial', 'Stock Actual', 'Precio Venta']].copy()
        view_inv['Precio Venta'] = df_f['Precio_Num'].apply(formato_moneda)
        st.dataframe(view_inv.style.applymap(color_stock, subset=['Stock Actual']),
                     use_container_width=True, hide_index=True, height=380)

    with c2:
        st.subheader("🔥 Top Ventas (Unidades)")
        df_top = df_inv[df_inv['Vendidos'] > 0].sort_values('Vendidos', ascending=True)
        if not df_top.empty:
            fig_bar = px.bar(df_top, x='Vendidos', y='Prenda', orientation='h',
                             color_discrete_sequence=['#88d4b3'], text_auto='.0f')
            fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="", margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 6. GRÁFICA DE VENTAS DIARIAS
    st.subheader("📅 Tendencia de Ventas Diarias")
    try:
        df_v = pd.read_csv(url_ventas).dropna(subset=['Fecha', 'Total'])
        df_v['Total_Num'] = pd.to_numeric(
            df_v['Total'].astype(str).str.replace('$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), 
            errors='coerce'
        ).fillna(0)
        
        df_diario = df_v.groupby('Fecha')['Total_Num'].sum().reset_index()
        fig_trend = px.bar(df_diario, x='Fecha', y='Total_Num', color_discrete_sequence=['#f2a7b5'], text_auto=True)
        fig_trend.update_layout(xaxis_title="", yaxis_title="Monto ($)", height=400)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("**Detalle de Ventas**")
        st.dataframe(df_v[['Fecha', 'Nombre del Producto', 'Cantidad Vendida', 'Total']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Error en datos de ventas: {e}")

except Exception as e:
    st.error(f"Error crítico: {e}")

import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# CSS para ocultar menús y definir el color rojo del estatus
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px;
    }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #00ffcc !important; }
    </style>
    """, unsafe_allow_html=True)

# URL de la base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def clean_num(value):
    """Limpia formatos de moneda de Excel para cálculos"""
    if pd.isna(value) or value == "" or value == 0: return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except:
        return 0.0

try:
    # Leer datos del cliente y tabla
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]
    
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    df_limpio = df.dropna(subset=['Fecha']).copy()

    # --- LÓGICA DE CÁLCULOS ---
    # Interés Acumulado: Suma de la columna de intereses generados
    total_gen = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
    # Interés Pendiente: Acumulado menos lo que ha abonado a interés
    total_pagado_int = df_limpio['Abono a Interés'].apply(clean_num).sum()
    int_pendiente = total_gen - total_pagado_int
    
    # Capital: Último saldo registrado
    cap_pend = df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]['Saldo Capital Pendiente']

    # --- MOSTRAR INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL PENDIENTE", f"{cap_pend}")
    c2.metric("INTERÉS ACUMULADO", f"${total_gen:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    c3, c4 = st.columns(2)
    c3.metric("INTERÉS PENDIENTE", f"${int_pendiente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Estatus con color ROJO forzado mediante HTML simple
    with c4:
        st.markdown(f"""
            <div style="background-color: #111111; border: 1px solid #ff4b4b; border-radius: 12px; padding: 10px; text-align: center;">
                <p style="color: #8b949e; font-size: 14px; margin: 0;">ESTATUS</p>
                <p style="color: #ff4b4b; font-size: 26px; font-weight: bold; margin: 0;">EN RIESGO</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    # Columnas finales solicitadas
    columnas = ['Fecha', 'Descripción', 'Interés Generado (20%)', 'Abono a Interés', 'Abono a Capital', 'Saldo Capital Pendiente']
    st.dataframe(df_limpio[columnas].fillna("-"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Error de conexión. Por favor revisa el archivo Excel.")

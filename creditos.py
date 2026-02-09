import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estado de Cuenta OWS", layout="centered")

# Estilo visual
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

SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def clean_num(value):
    """Convierte moneda de texto a número para cálculos"""
    if str(value) == 'nan' or value == "": return 0.0
    try:
        res = str(value).replace('$', '').replace('.', '').replace(',', '.').strip()
        return float(res)
    except:
        return 0.0

try:
    # Nombre del cliente
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]

    # Tabla principal
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    df_limpio = df.dropna(subset=['Fecha']).copy()

    # --- CÁLCULOS DINÁMICOS ---
    # 1. Suma de todos los intereses generados
    total_interes_generado = df_limpio['Interés Generado (20%)'].apply(clean_num).sum()
    
    # 2. Suma de todos los abonos realizados al interés
    total_abonos_interes = df_limpio['Abono a Interés'].apply(clean_num).sum()
    
    # 3. Interés Pendiente (Resta)
    interes_pendiente = total_interes_generado - total_abonos_interes
    
    # 4. Último Saldo Capital
    ultimo_capital = df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]['Saldo Capital Pendiente']

    # --- INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL PENDIENTE", f"{ultimo_capital}")
    c2.metric("INTERÉS ACUMULADO", f"${total_interes_generado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    c3, c4 = st.columns(2)
    c3.metric("INTERÉS PENDIENTE", f"${interes_pendiente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    c4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    columnas_tabla = ['Fecha', 'Descripción', 'Interés Generado (20%)', 'Abono a Interés', 'Abono a Capital', 'Saldo Capital Pendiente']
    st.dataframe(df_limpio[columnas_tabla].fillna("-"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error en sincronización: {e}")

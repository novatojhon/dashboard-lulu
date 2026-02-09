import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# Estilo para móvil
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

# URL exacta de tu hoja
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

def limpiar_moneda(valor):
    """Convierte texto como '$3.000,00' en número real"""
    if isinstance(valor, str):
        return valor.replace('$', '').replace('.', '').replace(',', '.').strip()
    return valor

try:
    # 1. Extraer nombre del cliente
    df_raw = pd.read_csv(url, header=None)
    nombre_cliente = df_raw.iloc[0, 2] 

    # 2. Leer tabla principal
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    
    # Filtramos filas vacías
    df = df.dropna(subset=['Fecha'])

    # 3. EXTRAER VALORES (Arreglando los ceros)
    # Tomamos la última fila disponible
    ultima_fila = df.iloc[-1]
    
    cap_pend = ultima_fila['Saldo Capital Pendiente']
    int_pend = ultima_fila['Saldo Interés Pendiente']
    int_gen = ultima_fila['Interés Generado (20%)']

    # Mostrar Interfaz
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL TOTAL", cap_pend)
    c2.metric("INTERÉS TOTAL", int_pend)
    
    c3, c4 = st.columns(2)
    c3.metric("INTERÉS GENERADO", int_gen)
    c4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    # Tabla con las columnas que necesitas ver
    columnas_tabla = [
        'Fecha', 
        'Interés Generado (20%)', 
        'Abono a Interés', 
        'Abono a Capital', 
        'Saldo Capital Pendiente'
    ]
    st.dataframe(df[columnas_tabla], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error en la base de datos: {e}")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# Estilo visual consistente
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

# URL de tu base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # 1. Obtener el nombre del cliente desde la celda C1
    df_nombre = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_nombre.iloc[0, 2]

    # 2. Leer la tabla principal (datos reales)
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    
    # IMPORTANTE: Eliminamos filas donde la fecha esté vacía para evitar el "nan"
    df = df.dropna(subset=['Fecha'])
    
    # 3. Extraer los datos de la ÚLTIMA fila con información
    ultima_fila = df.iloc[-1]
    
    cap_pend = ultima_fila['Saldo Capital Pendiente']
    int_pend = ultima_fila['Saldo Interés Pendiente']
    # Buscamos la columna de interés generado aunque tenga el (20%)
    col_int_gen = [c for c in df.columns if 'Interés Generado' in c][0]
    int_gen = ultima_fila[col_int_gen]

    # --- MOSTRAR EN PANTALLA ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    col1, col2 = st.columns(2)
    col1.metric("CAPITAL TOTAL", cap_pend)
    col2.metric("INTERÉS TOTAL", int_pend)
    
    col3, col4 = st.columns(2)
    col3.metric("INTERÉS GENERADO", int_gen)
    col4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    # Tabla limpia con los nombres exactos de tus columnas
    columnas_a_mostrar = ['Fecha', col_int_gen, 'Abono a Interés', 'Abono a Capital', 'Saldo Capital Pendiente']
    st.dataframe(df[columnas_a_mostrar].fillna(""), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Sincronizando con la base de datos... Por favor refresca la página.")

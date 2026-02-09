import streamlit as st
import pandas as pd

# 1. Configuración básica
st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# CSS para ocultar menús y mejorar visualización en móvil
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

# 2. Conexión a la base de datos
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # Leer nombre del cliente
    df_raw = pd.read_csv(url, header=None)
    nombre_cliente = df_raw.iloc[0, 2] 

    # Leer la tabla principal (datos reales)
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()
    
    # Limpiar: Solo nos interesan filas que tengan una fecha válida
    df = df.dropna(subset=['Fecha'])

    # 3. Extraer los datos de la ÚLTIMA fila con información real
    ultima_fila = df.iloc[-1]
    
    cap_pend = ultima_fila['Saldo Capital Pendiente']
    int_pend = ultima_fila['Saldo Interés Pendiente']
    int_gen = ultima_fila['Interés Generado (20%)']

    # --- MOSTRAR EN PANTALLA ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL TOTAL", f"{cap_pend}")
    c2.metric("INTERÉS TOTAL", f"{int_pend}")
    
    c3, c4 = st.columns(2)
    c3.metric("INTERÉS GENERADO", f"{int_gen}")
    c4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    # Tabla con las columnas exactas de tu imagen
    columnas_visibles = ['Fecha', 'Interés Generado (20%)', 'Abono a Interés', 'Abono a Capital', 'Saldo Capital Pendiente']
    st.dataframe(df[columnas_visibles].fillna(""), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al conectar: {e}")

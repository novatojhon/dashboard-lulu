import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# CSS para que se vea como una App de Finanzas
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

try:
    # Leer nombre del cliente (C1)
    df_raw = pd.read_csv(url, header=None)
    nombre_cliente = df_raw.iloc[0, 2] 

    # Leer tabla principal (saltando 2 filas)
    df = pd.read_csv(url, skiprows=2).fillna(0)
    df.columns = df.columns.str.strip()
    
    # Filtrar solo filas con datos
    df_datos = df[df['Fecha'] != 0]
    
    # Valores de la última fila para las métricas superiores
    ultima_fila = df_datos.iloc[-1]

    st.markdown(f"### 🏦 {nombre_cliente}")
    
    # Cuadrícula de métricas (4 campos clave)
    c1, c2 = st.columns(2)
    c1.metric("CAPITAL TOTAL", f"{ultima_fila['Saldo Capital Pendiente']}")
    c2.metric("INTERÉS TOTAL", f"{ultima_fila['Saldo Interés Pendiente']}")
    
    c3, c4 = st.columns(2)
    # Aquí está el campo que faltaba
    c3.metric("INTERÉS GENERADO", f"{ultima_fila['Interés Generado (20%)']}")
    c4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Detalle de Movimientos**")
    
    # Mostramos la tabla con todas las columnas de tu imagen
    columnas_visibles = [
        'Fecha', 
        'Interés Generado (20%)', 
        'Abono a Interés', 
        'Abono a Capital', 
        'Saldo Capital Pendiente'
    ]
    
    st.dataframe(
        df_datos[columnas_visibles], 
        use_container_width=True, 
        hide_index=True
    )

except Exception as e:
    st.error("Sincronizando con Google Sheets...")

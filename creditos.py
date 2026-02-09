import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Estado de Cuenta", layout="centered")

# CSS para vista móvil profesional
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

# 2. Conexión a Google Sheets
SHEET_ID = "1PMwIDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=77813725"

try:
    # Leer nombre del cliente (Celda C1)
    df_raw = pd.read_csv(url, header=None, nrows=1)
    nombre_cliente = df_raw.iloc[0, 2]

    # Leer la tabla principal
    df = pd.read_csv(url, skiprows=2)
    df.columns = df.columns.str.strip()

    # --- LÓGICA DE SEGURIDAD PARA EVITAR EL 'NAN' ---
    # Limpiamos filas que no tengan fecha y convertimos a texto para mostrar tal cual está en el Excel
    df_limpio = df.dropna(subset=['Fecha']).copy()
    
    # Buscamos la última fila que tenga un Saldo Capital Pendiente (para los cuadros de arriba)
    fila_con_totales = df_limpio[df_limpio['Saldo Capital Pendiente'].notna()].iloc[-1]
    
    cap_total = fila_con_totales['Saldo Capital Pendiente']
    int_total = fila_con_totales['Saldo Interés Pendiente']
    
    # Buscamos el último interés generado que no sea nulo
    int_gen = df_limpio[df_limpio['Interés Generado (20%)'].notna()].iloc[-1]['Interés Generado (20%)']

    # --- INTERFAZ ---
    st.markdown(f"### 🏦 {nombre_cliente}")
    
    col1, col2 = st.columns(2)
    col1.metric("CAPITAL PENDIENTE", f"{cap_total}")
    col2.metric("INTERÉS ACUMULADO", f"{int_total}")
    
    col3, col4 = st.columns(2)
    col3.metric("INTERÉS GENERADO", f"{int_gen}")
    col4.metric("ESTATUS", "EN RIESGO")

    st.markdown("---")
    st.write("📊 **Historial de Movimientos**")
    
    # Mostramos todas las columnas incluyendo Descripción
    columnas_tabla = [
        'Fecha', 
        'Descripción', 
        'Interés Generado (20%)', 
        'Abono a Interés', 
        'Abono a Capital', 
        'Saldo Capital Pendiente'
    ]
    
    # Llenamos vacíos con "-" para que no salga "None" o "nan"
    st.dataframe(df_limpio[columnas_tabla].fillna("-"), use_container_width=True, hide_index=True)

except Exception as e:
    st.warning("Sincronizando datos... Por favor, refresca la página.")

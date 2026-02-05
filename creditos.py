import streamlit as st
import pandas as pd

# CONFIGURACIÓN INDEPENDIENTE
st.set_page_config(page_title="Control de Préstamos Jhon", layout="wide")

# Reemplaza con el link de tu nueva hoja de Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI/export?format=csv"

def load_data():
    df = pd.read_csv(SHEET_URL)
    # Convertimos a número las columnas de tu imagen
    for col in ['Saldo Capital Pendiente', 'Saldo Interés Pendiente']:
        df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
    return df

df = load_data()
ultimo = df.iloc[-1]

st.title("💰 Estado de Cuenta: Cliente")
st.metric("TOTAL DEUDA", f"${ultimo['Saldo Capital Pendiente'] + ultimo['Saldo Interés Pendiente']:,.2f}")

# Esto mostrará la tabla limpia que vimos en tu captura
st.subheader("Historial de movimientos")
st.table(df[['Fecha', 'Descripción', 'Abono a Interés', 'Abono a Capital', 'Saldo Capital Pendiente', 'Saldo Interés Pendiente']])

# Este código genera el JSON que Softr va a leer
import pandas as pd
import json

# Tu ID de hoja actual
SHEET_ID = "1PMwlDdoXm1U02g-nTtkoq14wihv7ORpHEsla0FbgSJ8"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

df = pd.read_csv(url)

# Limpiamos y sumamos
df['capital'] = df['Saldo Capital Pendiente'].replace('[\$,]', '', regex=True).astype(float)
df['interes'] = df['Saldo Interés Pendiente'].replace('[\$,]', '', regex=True).astype(float)
df['total'] = df['capital'] + df['interes']

# Creamos el JSON final para Softr
resultado = df.to_dict(orient='records')
with open('data.json', 'w') as f:
    json.dump(resultado, f)

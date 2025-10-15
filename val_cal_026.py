import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.title("📊 Generador de Archivos CSV")

# Entrada de parámetros
mes = st.number_input("Mes (1-12):", min_value=1, max_value=12, value=12)
año = st.number_input("Año:", min_value=2000, max_value=2100, value=2024)

ipp_base = 147.65

# Subida de archivos
st.write("### Cargar archivos Excel")
archivos = st.file_uploader("Selecciona los archivos (.xlsx)", type=["xlsx"], accept_multiple_files=True)

if archivos and st.button("Generar Archivo Consolidado"):
    datos_consolidados = []

    for archivo in archivos:
        df = pd.read_excel(archivo, sheet_name=0)

        # Extrae valores de celdas específicas
        valor_a1 = df.iloc[5, 1]  
        valor_a2 = df.iloc[5, 2]  
        valor_a3 = df.iloc[5, 3]  
        valor_a4 = df.iloc[5, 4]  
        valor_a5 = df.iloc[8, 2]  
        valor_a6 = df.iloc[9, 2]  
        valor_a7 = df.iloc[10, 2]  
        valor_a8 = df.iloc[12, 2]  
        valor_a9 = df.iloc[78, 2]  
        valor_a10 = df.iloc[79, 2]  
        valor_a11 = df.iloc[81, 2]  
        valor_a12 = df.iloc[110, 2]  
        valor_a13 = df.iloc[111, 2]  
        valor_a14 = df.iloc[112, 2]  
        valor_a15 = df.iloc[113, 2]  
        valor_a16 = df.iloc[114, 2]  
        valor_a17 = df.iloc[110, 3]  
        valor_a18 = df.iloc[111, 3]  
        valor_a19 = df.iloc[112, 3]  
        valor_a20 = df.iloc[113, 3]  
        valor_a21 = df.iloc[114, 3]  
        valor_a22 = df.iloc[122, 2]  
        valor_a23 = df.iloc[123, 2]  
        valor_a24 = df.iloc[124, 2]  
        valor_a25 = df.iloc[125, 2]  
        valor_a26 = df.iloc[127, 2]  
        valor_a27 = df.iloc[129, 2]  
        valor_a28 = df.iloc[122, 4]  
        valor_a29 = df.iloc[122, 5]  
        valor_a30 = df.iloc[125, 5]  
        valor_a31 = df.iloc[126, 5]  

        datos_consolidados.append({
            'Archivo': archivo.name,
            'Departamento': valor_a1,
            'Municipio': valor_a2,
            'Divipola': valor_a3,
            'Radiacion': valor_a4,
            'Tipo de Sistema': valor_a5,
            'Almacenamiento': valor_a6,
            'Whd': valor_a7,
            'IPP_base': ipp_base,
            'IPPm_1': valor_a8,
            'Cartera vencida 90_360': valor_a9,
            'Cartera_Subs': valor_a10,
            'Tasa_Costo_Fin': valor_a11,
            'AMGCnu_0': valor_a12,
            'AMGCvi_0': valor_a13,
            'AMGCau_0': valor_a14,
            'AMGCnf_0': valor_a15,
            'AMGCro_0': valor_a16,
            'AMGCnu_m': valor_a17,
            'AMGCvi_m': valor_a18,
            'AMGCau_m': valor_a19,
            'AMGCnf_m': valor_a20,
            'AMGCro_m': valor_a21,
            'Inversio': valor_a22,
            'AMGCm': valor_a23,
            'Disponibilidad': valor_a24,
            'Facturacion_mes': valor_a25,
            'Subsidio_mes': valor_a26,
            'Tarifa_mes': valor_a27,
            'Empresa SIN': valor_a28,
            'Tarifa SIN': valor_a29,
            'Subsidio_dia': valor_a30,
            'Porcentaje_subsidio': valor_a31,
            'Año': año,
            'Mes': mes
        })

    if datos_consolidados:
        df_consolidado = pd.DataFrame(datos_consolidados)

        # Mostrar tabla en la app
        st.dataframe(df_consolidado)

        # Descargar CSV
        buffer = BytesIO()
        df_consolidado.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)

        st.download_button(
            label="📥 Descargar CSV",
            data=buffer,
            file_name="consolidado.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No se encontraron datos válidos para consolidar.")

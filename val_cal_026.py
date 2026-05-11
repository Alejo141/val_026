import streamlit as st
import pandas as pd
from io import BytesIO

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(page_title="Generador CSV", page_icon="📊", layout="wide")
st.title("📊 Generador de Archivos CSV")

# ── Parámetros de entrada ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    mes = st.number_input("Mes (1-12):", min_value=1, max_value=12, value=12)
with col2:
    año = st.number_input("Año:", min_value=2000, max_value=2100, value=2024)

IPP_BASE = 147.65

# ── Mapa de celdas: nombre → (fila, columna) ────────────────────────────────
CELDAS = {
    "Departamento":            (5,   1),
    "Municipio":               (5,   2),
    "Divipola":                (5,   3),
    "Radiacion":               (5,   4),
    "Tipo de Sistema":         (8,   2),
    "Almacenamiento":          (9,   2),
    "Whd":                     (10,  2),
    "IPPm_1":                  (12,  2),
    "Cartera vencida 90_360":  (78,  2),
    "Cartera_Subs":            (79,  2),
    "Tasa_Costo_Fin":          (81,  2),
    "AMGCnu_0":                (110, 2),
    "AMGCvi_0":                (111, 2),
    "AMGCau_0":                (112, 2),
    "AMGCnf_0":                (113, 2),
    "AMGCro_0":                (114, 2),
    "AMGCnu_m":                (110, 3),
    "AMGCvi_m":                (111, 3),
    "AMGCau_m":                (112, 3),
    "AMGCnf_m":                (113, 3),
    "AMGCro_m":                (114, 3),
    "Inversio":                (122, 2),
    "AMGCm":                   (123, 2),
    "Disponibilidad":          (124, 2),
    "Facturacion_mes":         (125, 2),
    "Subsidio_mes":            (127, 2),
    "Tarifa_mes":              (129, 2),
    "Empresa SIN":             (122, 4),
    "Tarifa SIN":              (122, 5),
    "Subsidio_dia":            (125, 5),
    "Porcentaje_subsidio":     (126, 5),
}

# ── Orden final de columnas ──────────────────────────────────────────────────
ORDEN_COLUMNAS = [
    "Archivo",
    "Departamento", "Municipio", "Divipola", "Radiacion",
    "Tipo de Sistema", "Almacenamiento", "Whd", "llave",
    "IPP_base", "IPPm_1",
    "Cartera vencida 90_360", "Cartera_Subs", "Tasa_Costo_Fin",
    "AMGCnu_0", "AMGCvi_0", "AMGCau_0", "AMGCnf_0", "AMGCro_0",
    "AMGCnu_m", "AMGCvi_m", "AMGCau_m", "AMGCnf_m", "AMGCro_m",
    "Inversio", "AMGCm", "Disponibilidad", "Facturacion_mes",
    "Subsidio_mes", "Tarifa_mes",
    "Empresa SIN", "Tarifa SIN",
    "Subsidio_dia", "tarifa_dia", "fact_dia",
    "Porcentaje_subsidio",
    "Año", "Mes",
]


def extraer_fila(df: pd.DataFrame, nombre_archivo: str) -> dict:
    """Extrae todos los valores de un DataFrame usando el mapa CELDAS."""
    fila = {"Archivo": nombre_archivo}

    for campo, (row, col) in CELDAS.items():
        try:
            fila[campo] = df.iloc[row, col]
        except IndexError:
            fila[campo] = None
            st.warning(f"⚠️ [{nombre_archivo}] Celda ({row},{col}) fuera de rango para '{campo}'.")

    fila["IPP_base"] = IPP_BASE
    return fila


def calcular_campos_derivados(fila: dict) -> dict:
    """Calcula los campos derivados: llave, tarifa_dia y fact_dia."""
    # llave = Divipola + Whd
    divipola = fila.get("Divipola", "")
    whd      = fila.get("Whd", "")
    fila["llave"] = f"{divipola}{whd}"

    # tarifa_dia = Tarifa_mes / Disponibilidad
    try:
        disponibilidad = float(fila.get("Disponibilidad") or 0)
        fila["tarifa_dia"] = float(fila["Tarifa_mes"]) / disponibilidad if disponibilidad else None
    except (TypeError, ValueError):
        fila["tarifa_dia"] = None

    # fact_dia = Facturacion_mes / Disponibilidad
    try:
        disponibilidad = float(fila.get("Disponibilidad") or 0)
        fila["fact_dia"] = float(fila["Facturacion_mes"]) / disponibilidad if disponibilidad else None
    except (TypeError, ValueError):
        fila["fact_dia"] = None

    return fila


def procesar_archivos(archivos, mes: int, año: int) -> pd.DataFrame:
    """Procesa la lista de archivos y retorna un DataFrame consolidado."""
    filas = []
    barra = st.progress(0, text="Procesando archivos…")

    for i, archivo in enumerate(archivos):
        try:
            df = pd.read_excel(archivo, sheet_name=0)
            fila = extraer_fila(df, archivo.name)
            fila = calcular_campos_derivados(fila)
            fila["Año"] = año
            fila["Mes"] = mes
            filas.append(fila)
        except Exception as e:
            st.error(f"❌ Error procesando '{archivo.name}': {e}")

        barra.progress((i + 1) / len(archivos), text=f"Procesando {i + 1}/{len(archivos)}")

    barra.empty()

    if not filas:
        return pd.DataFrame()

    df_resultado = pd.DataFrame(filas)

    # Reordena columnas; agrega al final las que no estén en ORDEN_COLUMNAS
    columnas_extra = [c for c in df_resultado.columns if c not in ORDEN_COLUMNAS]
    df_resultado = df_resultado[ORDEN_COLUMNAS + columnas_extra]

    return df_resultado


# ── Interfaz de carga ────────────────────────────────────────────────────────
st.write("### Cargar archivos Excel")
archivos = st.file_uploader(
    "Selecciona uno o varios archivos (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True,
)

if archivos and st.button("⚙️ Generar Archivo Consolidado", type="primary"):
    df_consolidado = procesar_archivos(archivos, mes, año)

    if df_consolidado.empty:
        st.warning("⚠️ No se encontraron datos válidos para consolidar.")
    else:
        st.success(f"✅ {len(df_consolidado)} archivo(s) procesado(s) correctamente.")
        st.dataframe(df_consolidado, use_container_width=True)

        col_csv, col_xlsx = st.columns(2)

        with col_csv:
            buffer_csv = BytesIO()
            df_consolidado.to_csv(buffer_csv, index=False, encoding="utf-8-sig")
            buffer_csv.seek(0)
            st.download_button(
                label="📥 Descargar CSV",
                data=buffer_csv,
                file_name=f"consolidado_{año}_{mes:02d}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_xlsx:
            buffer_xlsx = BytesIO()
            with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as writer:
                df_consolidado.to_excel(writer, index=False, sheet_name="Consolidado")
            buffer_xlsx.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=buffer_xlsx,
                file_name=f"consolidado_{año}_{mes:02d}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

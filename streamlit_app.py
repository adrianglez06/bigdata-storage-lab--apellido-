# streamlit_app.py
# App Streamlit sobria para ingesta, normalización, linaje, validación y agregación por mes.
# Requiere: streamlit, pandas, pyarrow, python-dateutil
from __future__ import annotations

import io
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# Importa funciones del pipeline
from src.transform import normalize_columns, to_silver
from src.validate import basic_checks
from src.ingest import tag_lineage, concat_bronze


# ---------- Utilidades ----------

def read_csv_safely(file) -> pd.DataFrame:
    """
    Lee un CSV intentando primero UTF-8 y luego latin-1.
    Devuelve DataFrame; levanta excepción si ambos fallan.
    """
    try:
        return pd.read_csv(file)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="latin-1")


def build_mapping(src_date: str, src_partner: str, src_amount: str, df_cols: List[str]) -> Dict[str, str]:
    """
    Construye mapping origen->canónico validando que existan en el DataFrame.
    No lanza excepción: el renombrado en normalize_columns añadirá NA si falta algo.
    """
    mapping: Dict[str, str] = {}
    if src_date in df_cols:
        mapping[src_date] = "date"
    if src_partner in df_cols:
        mapping[src_partner] = "partner"
    if src_amount in df_cols:
        mapping[src_amount] = "amount"
    return mapping


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes CSV sin índice."""
    return df.to_csv(index=False).encode("utf-8")


# ---------- UI ----------

st.set_page_config(page_title="Big Data Storage Lab", layout="wide")

st.title("De CSVs heterogéneos a un almacén analítico confiable")
st.caption("Sube múltiples CSVs, normaliza a esquema canónico, valida y agrega a silver por partner y mes.")

with st.sidebar:
    st.header("Configuración")
    st.markdown("Especifica las columnas de origen para mapear al esquema canónico:")
    src_date = st.text_input("Columna de fecha (origen)", value="date")
    src_partner = st.text_input("Columna de partner (origen)", value="partner")
    src_amount = st.text_input("Columna de amount (origen)", value="amount")
    st.markdown("---")
    st.markdown("Formatos soportados de amount: `1.234,56 €`, `1234.56`, `(123,45)`...")

uploaded_files = st.file_uploader(
    "Sube uno o más archivos CSV",
    type=["csv"],
    accept_multiple_files=True,
    help="Se intentará leer primero en UTF-8 y si falla, en latin-1."
)

if not uploaded_files:
    st.info("Sube archivos para iniciar el flujo.")
    st.stop()

bronze_frames: List[pd.DataFrame] = []
file_reports: List[Tuple[str, List[str], pd.DataFrame]] = []

st.subheader("Procesamiento por archivo")

for uf in uploaded_files:
    with st.expander(f"Archivo: {uf.name}", expanded=False):
        # Leer
        df_raw = read_csv_safely(uf)
        st.write("Vista previa origen:", df_raw.head())

        # Mapping dinámico según inputs de la barra lateral
        mapping = build_mapping(src_date, src_partner, src_amount, df_raw.columns.tolist())

        # Normalizar a canónico
        df_norm = normalize_columns(df_raw, mapping)

        # Tag de linaje
        df_tagged = tag_lineage(df_norm, source_name=uf.name)

        # Validación
        errors = basic_checks(df_tagged[["date", "partner", "amount"]])

        # Guardar para bronze
        bronze_frames.append(df_tagged)
        file_reports.append((uf.name, errors, df_tagged))

        # Mostrar resultados del archivo
        st.write("Canónico + linaje (preview):", df_tagged.head())

        if errors:
            st.error("Errores de validación:")
            for e in errors:
                st.write(f"- {e}")
        else:
            st.success("Validación básica OK.")

# Unificación bronze
bronze = concat_bronze([fr for _, _, fr in file_reports])

st.subheader("Tabla bronze unificada")
st.dataframe(bronze, use_container_width=True)

# Validaciones globales
global_errors = basic_checks(bronze[["date", "partner", "amount"]])
if global_errors:
    st.error("Errores globales de validación en bronze. Corrige antes de derivar a silver:")
    for e in global_errors:
        st.write(f"- {e}")
    # Descargas de bronze aún disponibles para depurar
else:
    st.success("Bronze válido. Derivando a silver...")

# KPI simples sobre bronze
st.markdown("### KPIs de calidad (bronze)")
total_rows = len(bronze)
valid_date = bronze["date"].notna().sum()
valid_partner = bronze["partner"].notna().sum()
valid_amount = bronze["amount"].notna().sum()
non_negative = (pd.to_numeric(bronze["amount"], errors="coerce") >= 0).sum()

kpi_df = pd.DataFrame(
    {
        "KPI": [
            "Filas totales",
            "date no nulo",
            "partner no nulo",
            "amount no nulo",
            "amount ≥ 0",
        ],
        "Valor": [total_rows, valid_date, valid_partner, valid_amount, non_negative],
    }
)
st.table(kpi_df)

# Si bronze válido, generar silver
if not global_errors and total_rows > 0:
    silver = to_silver(bronze[["date", "partner", "amount"]])

    st.subheader("Tabla silver: agregación por partner y mes")
    st.dataframe(silver, use_container_width=True)

    # KPIs simples sobre silver
    st.markdown("### KPIs (silver)")
    kpi_silver = pd.DataFrame(
        {
            "KPI": [
                "Partners únicos",
                "Meses únicos",
                "Total registros silver",
                "Suma amount silver",
            ],
            "Valor": [
                silver["partner"].nunique(),
                silver["month"].nunique(),
                len(silver),
                float(silver["amount"].sum()),
            ],
        }
    )
    st.table(kpi_silver)

    # Gráfico de barras: mes vs amount (total por mes)
    st.markdown("### Gráfico: amount total por mes")
    by_month = silver.groupby("month", as_index=False)["amount"].sum().sort_values("month")
    # Streamlit usará su charting interno; no colores personalizados.
    st.bar_chart(data=by_month, x="month", y="amount", use_container_width=True)

    # Descargas
    st.markdown("### Descargas")
    bronze_bytes = df_to_csv_bytes(bronze)
    silver_bytes = df_to_csv_bytes(silver)

    st.download_button(
        label="Descargar bronze.csv",
        data=bronze_bytes,
        file_name="bronze.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Descargar silver.csv",
        data=silver_bytes,
        file_name="silver.csv",
        mime="text/csv",
    )
else:
    st.warning("No se generó silver por errores de validación o ausencia de datos.")

st.caption("Nota: las validaciones son mínimas. Si quieres reglas adicionales, impleméntalas en src/validate.py y reusa este front-end.")


from __future__ import annotations

import re
from typing import Dict

import pandas as pd


def _normalize_amount_series(s: pd.Series) -> pd.Series:
    """
    Normaliza importes europeos a float:
    - Elimina símbolo € y espacios.
    - Convierte separadores europeos ('.' miles, ',' decimal) a formato estándar.
    - Maneja negativos con paréntesis.
    """
    if s.empty:
        return pd.Series([], dtype="float64")

    # A texto para limpieza
    txt = s.astype(str).str.strip()

    # Negativos con paréntesis: "(123,45)" -> "-123,45"
    txt = txt.str.replace(r"^\((.*)\)$", r"-\1", regex=True)

    # Quita símbolo € y espacios no separadores
    txt = (
        txt.str.replace("€", "", regex=False)
        .str.replace(r"\s+", "", regex=True)
    )

    # Casos con ambos separadores: "1.234,56" -> "1234,56"
    txt = txt.str.replace(r"\.(?=\d{3}(?:\D|$))", "", regex=True)

    # Decimal europeo: "," -> "."
    txt = txt.str.replace(",", ".", regex=False)

    # Vacíos o no numéricos a NaN, luego a float
    out = pd.to_numeric(txt, errors="coerce")

    return out


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Renombra columnas según mapping (origen -> {'date','partner','amount'}),
    parsea fechas a datetime (día), normaliza amount y limpia partner.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada con columnas de origen.
    mapping : Dict[str, str]
        Mapeo origen->canónico. Ej: {'fecha':'date','cliente':'partner','importe':'amount'}

    Returns
    -------
    pd.DataFrame
        DataFrame con columnas canónicas: date (datetime64[ns]),
        partner (string), amount (float64).
    """
    # Renombrar a canónico
    out = df.rename(columns=mapping).copy()

    # Asegurar existencia de columnas canónicas ausentes
    for col in ("date", "partner", "amount"):
        if col not in out.columns:
            out[col] = pd.NA

    # Fecha a datetime normalizado al día
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.normalize()

    # Partner: recortar, colapsar espacios internos, quitar control chars
    partner = out["partner"].astype(str).str.strip()
    partner = partner.str.replace(r"\s+", " ", regex=True)
    partner = partner.str.replace(r"[\x00-\x1F\x7F]", "", regex=True)
    # Vacíos a NA
    partner = partner.replace({"": pd.NA})
    out["partner"] = partner

    # Amount a float normalizado
    out["amount"] = _normalize_amount_series(out["amount"])

    # Tipos finales
    out = out.astype({"amount": "float64"})
    # partner puede contener NA; usar dtype pandas string para consistencia
    out["partner"] = out["partner"].astype("string")

    return out[["date", "partner", "amount"]]



# src/transform.py

def to_silver(bronze: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega amount por partner y mes.
    - month: inicio de mes (Timestamp).
    """
    df = bronze.copy()

    # Asegura datetime y genera el inicio de mes sin usar 'MS' como freq
    d = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = d.dt.to_period("M").dt.to_timestamp(how="start")  # inicio de mes

    # Elimina filas sin fecha válida o sin partner
    df = df.dropna(subset=["month", "partner"])

    # Agregación
    agg = (
        df.groupby(["partner", "month"], as_index=False, dropna=True)["amount"]
          .sum()
    )

    # Tipos coherentes
    agg["partner"] = agg["partner"].astype("string")
    agg["amount"] = agg["amount"].astype("float64")

    return agg[["partner", "month", "amount"]]



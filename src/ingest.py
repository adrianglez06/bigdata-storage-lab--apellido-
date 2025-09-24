from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List

import pandas as pd


def tag_lineage(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Añade metadatos de linaje:
    - source_file: nombre del archivo/fuente
    - ingested_at: timestamp UTC ISO 8601
    """
    out = df.copy()
    ts = datetime.now(timezone.utc).isoformat()
    out["source_file"] = source_name
    out["ingested_at"] = ts
    return out


def concat_bronze(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatena DataFrames a esquema bronze unificado:
    columnas: date, partner, amount, source_file, ingested_at
    Faltantes se rellenan con NA antes de concatenar.
    """
    cols: List[str] = ["date", "partner", "amount", "source_file", "ingested_at"]
    prepared: List[pd.DataFrame] = []

    for f in frames:
        tmp = f.copy()
        # Asegurar columnas
        for c in cols:
            if c not in tmp.columns:
                tmp[c] = pd.NA
        prepared.append(tmp[cols])

    if not prepared:
        return pd.DataFrame(columns=cols)

    bronze = pd.concat(prepared, ignore_index=True)

    # Tipos suaves para evitar errores en concatenaciones heterogéneas
    bronze["date"] = pd.to_datetime(bronze["date"], errors="coerce").dt.normalize()
    bronze["partner"] = bronze["partner"].astype("string")
    bronze["amount"] = pd.to_numeric(bronze["amount"], errors="coerce").astype("float64")
    # source_file y ingested_at pueden venir como string con NA
    bronze["source_file"] = bronze["source_file"].astype("string")
    bronze["ingested_at"] = bronze["ingested_at"].astype("string")

    return bronze[cols]


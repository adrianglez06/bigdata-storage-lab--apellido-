from __future__ import annotations

from typing import List

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_numeric_dtype


def basic_checks(df: pd.DataFrame) -> List[str]:
    """
    Valida requisitos mínimos del esquema canónico.
    - Columnas presentes: date, partner, amount
    - amount numérico y >= 0
    - date en datetime y no NaT

    Returns
    -------
    List[str]
        Lista de errores encontrados. Vacía si todo OK.
    """
    errors: List[str] = []

    required = {"date", "partner", "amount"}
    missing = required.difference(df.columns)
    if missing:
        errors.append(f"Faltan columnas canónicas: {sorted(missing)}")
        # Si faltan, el resto de validaciones serán ruidosas
        return errors

    # date debe ser datetime y sin NaT
    if not is_datetime(df["date"]):
        try:
            coerced = pd.to_datetime(df["date"], errors="coerce")
        except Exception:
            errors.append("date no es datetime y no se pudo convertir.")
        else:
            if coerced.isna().any():
                errors.append("date contiene valores no parseables a datetime.")
    else:
        if pd.isna(df["date"]).any():
            errors.append("date contiene NaT.")

    # amount debe ser numérico
    if not is_numeric_dtype(df["amount"]):
        try:
            _ = pd.to_numeric(df["amount"], errors="raise")
        except Exception:
            errors.append("amount no es numérico.")
    # amount >= 0
    try:
        negatives = pd.to_numeric(df["amount"], errors="coerce") < 0
        if negatives.any():
            errors.append("amount contiene valores negativos.")
    except Exception:
        # Si no se puede convertir, el error anterior ya lo marca
        pass

    return errors


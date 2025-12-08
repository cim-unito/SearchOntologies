from pathlib import Path
from typing import Iterable

import pandas as pd


def read_fields_from_columns(
        file_path: str,
        fields: Iterable[str],
        key_column: int = 0,
        value_column: int = 1,
) -> dict[str, object]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    fields = list(fields)

    dataframe = pd.read_excel(path, sheet_name=0, header=None)

    if max(key_column, value_column) >= dataframe.shape[1]:
        raise ValueError(
            f"Expected at least {max(key_column, value_column) + 1} columns "
            f"but found {dataframe.shape[1]}"
        )

    keys = (
        dataframe.iloc[:, key_column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    values = dataframe.iloc[:, value_column]

    lookup = {}
    for idx in keys.index:
        key = keys.loc[idx]
        if key not in lookup:
            value = values.loc[idx]
            lookup[key] = None if pd.isna(value) else value

    result = {
        str(field).strip(): lookup.get(str(field).casefold())
        for field in fields
    }
    return result
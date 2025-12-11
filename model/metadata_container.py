from dataclasses import dataclass
from typing import List

from model.metadata import Metadata


@dataclass
class MetadataContainer:
    sheet_name: str
    column_index: int
    cells: List[Metadata]

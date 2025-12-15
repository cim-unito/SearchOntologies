from dataclasses import dataclass, field
from typing import Dict, Iterator, Tuple, Iterable

from model.domain import Domain
from model.metadata import Metadata


@dataclass
class MetadataContainer:
    sheet_name: str
    column_index: int
    cells: Dict[str, Metadata]

    def get_cells(self) -> Dict[str, Metadata] | None:
        return self.cells

    def get_metadata(self, code: str) -> Metadata | None:
        return self.cells.get(code)

    def get_domain(self, code: str) -> Domain:
        metadata = self.get_metadata(code)
        return metadata.domain

    def get_value(self, code: str) -> str:
        metadata = self.get_metadata(code)
        return metadata.cell_value

    def codes(self) -> list[str]:
        return list(self.cells.keys())

    def set_value(self, code: str, value: str) -> None:
        if code not in self.cells:
            raise KeyError(f"Unknown metadata code: {code}")
        metadata = self.get_metadata(code)
        metadata.cell_value = value




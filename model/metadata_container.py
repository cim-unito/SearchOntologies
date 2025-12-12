from dataclasses import dataclass, field
from typing import Dict, Iterator, Tuple, Iterable

from model.metadata import Metadata


@dataclass
class MetadataContainer:
    sheet_name: str
    column_index: int
    definitions: Dict[str, Metadata]
    values: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.sheet_name, str) or not self.sheet_name.strip():
            raise ValueError("sheet_name must be a non-empty string")
        if not isinstance(self.column_index, int) or self.column_index < 0:
            raise ValueError("column_index must be a non-negative integer")

        # Ensure internal mappings are owned copies to avoid accidental mutation
        self.definitions = dict(self.definitions)
        self.values = dict(self.values)

    def get_definition(self, code: str) -> Metadata | None:
        return self.definitions.get(code)

    def get_value(self, code: str, default: str = "") -> str:
        return self.values.get(code, default)

    def set_value(self, code: str, value: str) -> None:
        if code not in self.definitions:
            raise KeyError(f"Unknown metadata code: {code}")
        self.values[code] = value

    def codes(self) -> list[str]:
        return list(self.definitions.keys())

    def items(self) -> Iterable[Tuple[str, Metadata, str]]:
        for code, definition in self.definitions.items():
            yield code, definition, self.values.get(code, "")

    def __iter__(self) -> Iterator[Tuple[Metadata, str]]:
        for _, definition, value in self.items():
            yield definition, value

    def __len__(self) -> int:
        return len(self.definitions)
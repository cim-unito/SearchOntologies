"""Container for metadata definitions used to read/write Excel files."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, ItemsView, KeysView, Mapping, ValuesView

from model.domain import Domain
from model.metadata import Metadata


@dataclass
class MetadataContainer:
    sheet_name: str
    column_index: int
    cells: Dict[str, Metadata] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.cells, Mapping):
            raise TypeError("cells must be a mapping of codes to Metadata"
                            "instances")

        self.cells = dict(self.cells)

        for code, metadata in self.cells.items():
            if not isinstance(code, str):
                raise TypeError("metadata codes must be strings")
            if not isinstance(metadata, Metadata):
                raise TypeError(
                    f"metadata for code '{code}' must be a Metadata instance"
                )

        self._cells_view: Mapping[str, Metadata] = MappingProxyType(self.cells)

    def get_cells(self) -> Mapping[str, Metadata]:
        """Return the metadata mapping keyed by code."""
        return self._cells_view

    def get_metadata(self, code: str) -> Metadata | None:
        """Return the metadata entry for ``code`` if present."""

        return self.cells.get(code)

    def get_domain(self, code: str) -> Domain:
        """Return the domain for the given metadata code."""

        metadata = self._require_metadata(code)
        return metadata.domain

    def get_value(self, code: str) -> str:
        """Return the stored cell value for ``code``."""

        metadata = self._require_metadata(code)
        return metadata.cell_value

    def codes(self) -> list[str]:
        """Return the list of available metadata codes."""

        return list(self.cells.keys())

    def keys(self) -> KeysView[str]:
        """Return a view of metadata codes."""

        return self._cells_view.keys()

    def values(self) -> ValuesView[Metadata]:
        """Return a view of metadata objects."""

        return self._cells_view.values()

    def items(self) -> ItemsView[str, Metadata]:
        """Return a view of (code, metadata) pairs."""

        return self._cells_view.items()

    def set_value(self, code: str, value: str) -> None:
        """Set the cell value for ``code``.

        Raises
        ------
        KeyError
            If the provided ``code`` is not present in the container.
        """

        metadata = self._require_metadata(code)
        metadata.cell_value = value

    def _require_metadata(self, code: str) -> Metadata:
        """Return metadata for ``code`` or raise ``KeyError`` if missing."""

        try:
            return self.cells[code]
        except KeyError as exc:
            raise KeyError(f"Unknown metadata code: {code}") from exc
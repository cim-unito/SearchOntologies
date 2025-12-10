from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from model.metadata import Metadata


class MetadataExcelIO:
    """Handle reading and writing metadata values from/to Excel files.
    """

    def read_metadata_values(
            self, metadata_list: Iterable[Metadata], file_path: str | Path
    ) -> list[Metadata] | None:
        """Populate metadata ``cell_value`` fields using the given Excel file.

        The Excel sheet is expected to contain a cell per metadata item whose
        coordinate matches ``metadata.code`` and whose value matches
        ``metadata.cell_name`` (case-insensitive). The actual metadata value is
        read from the cell immediately to the right.
        """

        workbook = load_workbook(file_path, read_only=True, data_only=True)
        metadata_by_code = {m.code.strip().upper(): m for m in metadata_list}
        missing_codes = set(metadata_by_code.keys())

        try:
            for sheet in workbook.worksheets:
                for code in list(missing_codes):
                    metadata = metadata_by_code[code]
                    try:
                        cell = sheet[code]
                    except ValueError:
                        print(
                            f"Invalid cell coordinate '{code}' for metadata"
                            f"'{metadata.cell_name}'"
                        )
                        missing_codes.discard(code)
                        continue

                    label = self._normalize(cell.value)
                    expected_label = self._normalize(metadata.cell_name)
                    if label is None:
                        continue
                    if expected_label is None or label != expected_label:
                        print(
                            f"Cell {code} in sheet '{sheet.title}' does not"
                            f"match expected name. Expected"
                            f"'{metadata.cell_name}', found '{cell.value}'"
                        )
                        continue

                    neighbor_value = self._stringify(
                        cell.offset(row=0, column=1).value)
                    metadata.cell_value = neighbor_value
                    missing_codes.discard(code)

                if not missing_codes:
                    break
        finally:
            workbook.close()

        if missing_codes:
            print(
                f"Metadata codes not found in workbook:"
                f"{', '.join(sorted(missing_codes))}"
            )

        return list(metadata_list)

    def write_metadata_values(self):
        pass

    def _normalize(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned.casefold() if cleaned else None

    def _stringify(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
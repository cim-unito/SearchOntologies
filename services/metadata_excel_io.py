from pathlib import Path

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from model.metadata import Metadata
from model.metadata_container import MetadataContainer


class MetadataExcelIO:
    """Handle reading and writing metadata values from/to Excel files.
    """

    def read_metadata_values(
            self, metadata: MetadataContainer, file_path: Path
    ) -> MetadataContainer | None:
        """Populate metadata ``cell_value`` fields using the given Excel file.

        The Excel sheet is expected to contain a cell per metadata item whose
        coordinate matches ``metadata.code`` and whose value matches
        ``metadata.cell_name`` (case-insensitive). The actual metadata value is
        read from the cell immediately to the right.
        """

        workbook = load_workbook(file_path, data_only=True)
        missing_codes = list(set(metadata.cells.keys()))
        iteration = 0

        try:
            for sheet in workbook.worksheets:
                for code in missing_codes:
                    metadata = metadata_by_code[code]
                    try:
                        cell = sheet[code]
                    except ValueError:
                        print(
                            f"Invalid cell coordinate '{code}' for metadata"
                            f"'{metadata.cell_name}'"
                        )
                        iteration += 1
                        continue

                    label = self._normalize(cell.value)
                    expected_label = self._normalize(metadata.cell_name)
                    if label is None:
                        iteration += 1
                        continue
                    if expected_label is None or label != expected_label:
                        print(
                            f"Cell {code} in sheet '{sheet.title}' does not"
                            f"match expected name. Expected"
                            f"'{metadata.cell_name}', found '{cell.value}'"
                        )
                        iteration += 1
                        continue
                    neighbor_value = cell.offset(row=0,
                                                 column=DEFAULT_OFFSET)
                    neighbor_value = self._stringify(neighbor_value.value)
                    metadata.cell_value = neighbor_value
                    iteration += 1

                if iteration == len(missing_codes):
                    break
        finally:
            workbook.close()

        return list(metadata_list)

    def write_metadata_values(self):
        pass

    def _normalize(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned.casefold() if cleaned else None

    def _stringify(self, value: object) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        return text
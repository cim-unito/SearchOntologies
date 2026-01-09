import flet as ft
from flet.core.file_picker import FilePickerFile

from config.config import ConfigError


class ControllerOntology:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the
        # persistence
        self._model = model

    def get_metadata_excel_file(self,
                                metadata_xlsx_file: list[
                                                        FilePickerFile] | None):
        """Read predefined fields from the selected Excel file."""
        if not metadata_xlsx_file:
            self._view.create_alert("No file selected!")
            return

        file_info = metadata_xlsx_file[0]
        file_path = getattr(file_info, "path", None)

        if not file_path:
            self._view.create_alert("Unable to read the selected file path")
            return

        try:
            metadata_container = self._model.read_metadata_fields(file_path)
        except (ValueError, FileNotFoundError) as exc:
            self._view.create_alert(str(exc))
            return

        self._view.update_metadata_table(
            self._build_metadata_rows(metadata_container))

    def lookup_term(self, e):
        """BioPortal lookups from the UI."""
        try:
            term_results = self._model.search_terms_from_metadata()
            rows = self._build_term_rows(term_results)
            self._view.update_metadata_table(rows)
            return rows
        except (ValueError, ConfigError) as exc:
            self._view.create_alert(str(exc))
            return []

    def _build_metadata_rows(self, metadata_container):
        entries = []
        metadata_container_sorted = metadata_container.get_cells_sorted()
        for code in metadata_container_sorted.keys():
            metadata = metadata_container.get_metadata(code)
            if metadata is None:
                continue

            ontology = metadata.domain.ontology if metadata.domain else None
            terms = self._model.split_terms(metadata.cell_value)
            if not terms:
                terms = [""]
            for term in terms:
                entries.append((metadata, term, ontology))

        return self._build_rows(entries)

    def _build_term_rows(self, term_results):
        return self._build_rows(term_results)

    @staticmethod
    def _build_rows(entries):
        rows = []
        for metadata, term, ontology in entries:
            ontology_display = ""
            if ontology:
                if ontology.value:
                    ontology_display = f"{ontology.id}: {ontology.value}"
                else:
                    ontology_display = ontology.id

            rows.append({
                "code": metadata.code,
                "subdomain": metadata.subdomain,
                "value": term,
                "ontology": ontology_display,
                "synonyms": ", ".join(ontology.synonyms)
                if ontology and ontology.synonyms else "",
                "iri": ontology.base_uri if ontology else "",
            })

        return rows

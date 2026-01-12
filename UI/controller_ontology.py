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
        self._user_selection: dict[str, str] = {}

    def set_user_selection(self, group_id: str, value: str):
        self._user_selection[group_id] = value

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
                entries.append(
                    (metadata, term, [ontology] if ontology else []))

        return self._build_rows(entries, allow_selection=False)

    def _build_term_rows(self, term_results):
        return self._build_rows(term_results, allow_selection=True)

    def _build_rows(self, entries, allow_selection: bool):
        rows = []
        group_index = 0
        for metadata, term, ontology in entries:
            ontology_display = ""
            candidates = ontology or []
            if not candidates:
                candidates = [None]
            group_id = f"{metadata.code}:{term}"
            selected_value = self._user_selection.get(group_id, "")
            choice_options = []
            for candidate in candidates:
                selection_option = None
                if allow_selection and candidate:
                    label = candidate.value or candidate.base_uri or candidate.id
                    value = candidate.base_uri or candidate.value or candidate.id
                    if value:
                        selection_option = {"label": label, "value": value}
                if candidate:
                    if candidate.value:
                        ontology_display = (
                            f"{candidate.id}: {candidate.value}"
                        )
                    else:
                        ontology_display = candidate.id
                else:
                    ontology_display = ""

                rows.append({
                    "code": metadata.code,
                    "subdomain": metadata.subdomain,
                    "value": term,
                    "ontology": ontology_display,
                    "synonyms": ", ".join(candidate.synonyms)
                    if candidate and candidate.synonyms else "",
                    "iri": candidate.base_uri if candidate else "",
                    "group_index": group_index,
                    "selection_group": group_id,
                    "selection_option": selection_option,
                    "selected_value": selected_value,
                })

            group_index += 1

        return rows

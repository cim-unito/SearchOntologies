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

            ontology = metadata.domain.ontology if getattr(metadata, "domain",
                                                           None) else None
            terms = self._model.split_terms(
                getattr(metadata, "cell_value", "")) or [""]
            candidates = [ontology] if ontology else []

            for term in terms:
                entries.append((metadata, term, candidates))

        return self._build_rows(entries, allow_selection=False)

    def _build_term_rows(self, term_results):
        self._update_default_selection(term_results)
        return self._build_rows(term_results, allow_selection=True)

    def _update_default_selection(self, entries):
        for metadata, term, ontology in entries:
            candidates = list(ontology or []) or [None]
            group_id = f"{metadata.code}:{term}"
            if self._user_selection.get(group_id):
                continue
            for candidate in candidates:
                candidate_value = self._candidate_value(candidate)
                if candidate_value:
                    self._user_selection[group_id] = candidate_value
                    break

    def _build_rows(self, entries, allow_selection: bool):
        rows = []
        group_index = 0
        for metadata, term, ontology in entries:
            candidates = list(ontology or []) or [None]
            group_id = f"{metadata.code}:{term}"
            default_value = self._user_selection.get(group_id, "")
            for candidate in candidates:
                selection_option = None
                if allow_selection and candidate:
                    label = self._candidate_label(candidate)
                    value = self._candidate_value(candidate)
                    if value:
                        selection_option = {"label": label or value,
                                            "value": value}

                rows.append({
                    "code": metadata.code,
                    "subdomain": metadata.subdomain,
                    "value": term,
                    "ontology": self._format_ontology_display(candidate),
                    "synonyms": ", ".join(getattr(candidate, "synonyms", []))
                    if getattr(candidate, "synonyms", None) else "",
                    "iri": getattr(candidate, "base_uri",
                                   "") if candidate else "",
                    "group_index": group_index,
                    "selection_group": group_id,
                    "selection_option": selection_option,
                    "selected_value": default_value,
                })

            group_index += 1

        return rows

    @staticmethod
    def _candidate_value(candidate):
        if not candidate:
            return None
        return (
                getattr(candidate, "base_uri", None)
                or getattr(candidate, "value", None)
                or getattr(candidate, "id", None)
        )

    @staticmethod
    def _candidate_label(candidate):
        if not candidate:
            return None
        return (
                getattr(candidate, "value", None)
                or getattr(candidate, "base_uri", None)
                or getattr(candidate, "id", None)
        )

    @staticmethod
    def _format_ontology_display(candidate):
        if not candidate:
            return ""
        value = getattr(candidate, "value", None)
        ident = getattr(candidate, "id", None)
        if value:
            return f"{ident}: {value}" if ident else value
        return ident or ""
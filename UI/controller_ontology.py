from typing import Iterable, Optional

import flet as ft
from flet.core.file_picker import FilePickerFile

from config.config import ConfigError
from model.metadata import Metadata
from model.metadata_container import MetadataContainer
from model.ontology import Ontology
from model.ontology_selection import OntologySelection


class ControllerOntology:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the
        # persistence
        self._model = model
        self._user_selection: dict[str, str] = {}
        self._selection_candidates: dict[str, dict[str, OntologySelection]] = {}
        self._selection_details: dict[str, OntologySelection] = {}

    def set_user_selection(self, group_id: str, value: str):
        """Store the user's selection for a given row group."""
        self._user_selection[group_id] = value
        selection = self._selection_candidates.get(group_id, {}).get(value)
        if selection:
            self._selection_details[group_id] = selection
        else:
            self._selection_details.pop(group_id, None)

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

    def lookup_term(self, e: ft.ControlEvent) -> list:
        """BioPortal lookups from the UI."""
        try:
            term_results = self._model.search_terms_from_metadata()
            rows = self._build_term_rows(term_results)
            self._view.update_metadata_table(rows)
            return rows
        except (ValueError, ConfigError) as exc:
            self._view.create_alert(str(exc))
            return []

    def export_csv(self, directory_path: str):
        """Export ontology codes to a single CSV file."""
        if not directory_path:
            self._view.create_alert("No folder selected!")
            return
        export_paths = self._model.export_csv(
            directory_path,
            self._user_selection,
            list(self._selection_details.values()),
        )

        if not export_paths:
            self._view.create_alert("No metadata terms available to export.")
            return

        exported_files = "\n".join(f"- {path}" for path in export_paths)
        self._view.create_alert(
            "CSV files saved:\n"
            f"{exported_files}"
        )

    def _build_metadata_rows(self,
                             metadata_container: MetadataContainer,
                             ) -> list:
        """Build read-only table rows from metadata container values."""
        entries = []
        metadata_container_sorted = metadata_container.get_cells_sorted()

        for metadata in metadata_container_sorted.values():
            if metadata is None:
                continue

            domain = metadata.get_domain()
            if domain.id.casefold() == "dataset":
                continue

            ontology = metadata.domain.ontology if getattr(metadata, "domain",
                                                           None) else None
            terms = self._model.split_terms(
                getattr(metadata, "cell_value", "")) or [""]

            for term in terms:
                entries.append((metadata, term, ontology))

        return self._build_rows(entries, allow_selection=False)

    def _build_term_rows(
            self,
            term_results: list[tuple[Metadata, str, list[Ontology]]],
    ) -> list:
        """Build selectable table rows for ontology term lookup results."""
        self._update_default_selection(term_results)
        return self._build_rows(term_results, allow_selection=True)

    def _update_default_selection(
            self,
            entries: Iterable[
                tuple[Metadata, str, Optional[Iterable[Ontology]]]
            ],
    ):
        """Set default selections for term groups if missing."""
        for index, (metadata, term, ontology) in enumerate(entries):
            candidates = self._normalize_candidates(ontology)
            group_id = self._model.build_group_id(metadata, term, index)
            if self._user_selection.get(group_id):
                continue
            for candidate in candidates:
                candidate_value = self._candidate_value(candidate)
                if candidate_value:
                    self._user_selection[group_id] = candidate_value
                    break

    def _build_rows(
            self,
            entries: Iterable[
                tuple[Metadata, str, Optional[Iterable[Ontology]]]
            ],
            allow_selection: bool,
    ) -> list:
        """Create UI table row dictionaries for metadata or term results."""
        rows = []
        group_index = 0
        if allow_selection:
            self._selection_candidates = {}
            self._selection_details = {}
        for index, (metadata, term, ontology) in enumerate(entries):
            candidates = self._normalize_candidates(ontology)
            group_id = self._model.build_group_id(metadata, term, index)
            default_value = self._user_selection.get(group_id, "")
            if allow_selection:
                self._selection_candidates[group_id] = {}
            for candidate in candidates:
                selection_option = None
                if allow_selection and candidate:
                    label = self._candidate_label(candidate)
                    value = self._candidate_value(candidate)
                    if value:
                        selection_option = {"label": label or value,
                                            "value": value}
                        selection_details = self._build_selection_details(
                            term, candidate
                        )
                        if selection_details:
                            self._selection_candidates[group_id][
                                value] = selection_details

                rows.append({
                    "code": metadata.code,
                    "domain": metadata.subdomain,
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

            if allow_selection and default_value:
                selection = self._selection_candidates[group_id].get(
                    default_value
                )
                if selection:
                    self._selection_details[group_id] = selection

            group_index += 1

        return rows
    @staticmethod
    def _build_selection_details(
            term: str,
            candidate: Ontology,
    ) -> OntologySelection | None:
        code = ControllerOntology._candidate_value(candidate)
        if not code:
            return None
        synonyms = ControllerOntology._merge_synonyms(
            term,
            getattr(candidate, "synonyms", []),
        )
        return OntologySelection(code=code, synonyms=synonyms)

    @staticmethod
    def _merge_synonyms(term: str, synonyms: list[str]) -> list[str]:
        merged = []
        seen = set()
        if term:
            merged.append(term)
            seen.add(term.casefold())
        for synonym in synonyms or []:
            if not synonym:
                continue
            key = synonym.casefold()
            if key in seen:
                continue
            merged.append(synonym)
            seen.add(key)
        return merged

    @staticmethod
    def _normalize_candidates(ontology):
        if ontology is None:
            return [None]
        if isinstance(ontology, str):
            return [ontology]
        try:
            candidates = list(ontology)
        except TypeError:
            return [ontology]
        return candidates or [None]

    @staticmethod
    def _candidate_value(candidate: Ontology | None) -> Optional[str]:
        """Return the value used to identify a candidate in selection menus."""
        if not candidate:
            return None
        ident = getattr(candidate, "id", None)
        value = getattr(candidate, "value", None)
        if ident and value:
            if value.startswith(f"{ident}:"):
                return value
            return f"{ident}:{value}"
        return ident or value

    @staticmethod
    def _candidate_label(candidate: Ontology | None) -> Optional[str]:
        """Return the readable label for a candidate option."""
        if not candidate:
            return None
        return (
                getattr(candidate, "value", None)
                or getattr(candidate, "base_uri", None)
                or getattr(candidate, "id", None)
        )

    @staticmethod
    def _format_ontology_display(candidate: Ontology | None) -> str:
        """Format ontology display text for the table view."""
        if not candidate:
            return ""
        value = getattr(candidate, "value", None)
        ident = getattr(candidate, "id", None)
        if value:
            return f"{ident}: {value}" if ident else value
        return ident or ""
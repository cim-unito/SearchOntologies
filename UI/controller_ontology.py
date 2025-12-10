import flet as ft
from flet.core.file_picker import FilePickerFile

from config.config import ConfigError


class ControllerOntology:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
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
            metadata = self._model.read_metadata_fields(file_path)
        except (ValueError, FileNotFoundError) as exc:
            self._view.create_alert(str(exc))
            return

        self._view.display_metadata(file_path, metadata)

    def lookup_term(self, e):
        """BioPortal lookups from the UI."""
        try:
            print(self._model.bioportal.search_ontology(term="Mice", ontology="NCIT"))
            #return self._model.bioportal.find_term(term, ontology)
        except (ValueError, ConfigError) as exc:
            self._view.create_alert(str(exc))
            return None
import flet as ft

from config import ConfigError

DEFAULT_METADATA_FIELDS = (
    "disease model",
    "organ or tissue",
    "imaging modality",
    "species",
    "strain"
)


class ControllerOntology:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def get_metadata_excel_file(self, metadata_xlsx_file):
        print(metadata_xlsx_file)
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
            metadata = self._model.read_metadata_fields(file_path,
                                                        fields=DEFAULT_METADATA_FIELDS)
        except (ValueError, FileNotFoundError) as exc:
            self._view.create_alert(str(exc))
            return

        self._view.display_metadata(file_path, metadata)

    def lookup_term(self, e):
        """BioPortal lookups from the UI."""
        try:
            print(self._model.bioportal.search_ontology(term="cancer", ontology="DOID"))
            #return self._model.bioportal.find_term(term, ontology)
        except (ValueError, ConfigError) as exc:
            self._view.create_alert(str(exc))
            return None
import flet as ft

from config import ConfigError


class ControllerOntology:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def get_metadata_excel_file(self, metadata_xlsx_file):
        print(metadata_xlsx_file)

    def lookup_term(self, term="cancer", ontology="DOID"):
        """BioPortal lookups from the UI."""
        try:
            a = self._model.bioportal.find_term(term, ontology)
            return self._model.bioportal.find_term(term, ontology)
        except (ValueError, ConfigError) as exc:
            self._view.create_alert(str(exc))
            return None
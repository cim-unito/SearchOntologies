from model.bio_portal_client import BioPortalClient
from model.metadata_reader import read_fields_from_columns


class ModelOntology:
    """
    Instantiate the BioPortal client here so all controllers/views depend on a
    single, configured entry point for ontology lookups.
    """

    def __init__(self, api_key=None):
        self._bioportal = BioPortalClient(api_key=api_key)

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal

    def read_metadata_fields(self, file_path: str, fields: tuple[str, ...]) -> dict[str, object]:
        """Read metadata values."""
        return read_fields_from_columns(file_path, fields)
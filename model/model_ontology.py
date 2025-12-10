from model.bio_portal_client import BioPortalClient
from model.metadata_reader import read_fields_from_columns
from data.domain_ontology_dao import DomainOntologyDao
from data.metadata_mapping_dao import MetadataMappingDao

class ModelOntology:
    """
    Instantiate the BioPortal client here so all controllers/views depend on a
    single, configured entry point for ontology lookups.
    """

    def __init__(self, api_key=None):
        self._bioportal = BioPortalClient(api_key=api_key)
        self._domains = DomainOntologyDao.load_domain_ontologies()
        self._metadata = MetadataMappingDao.load_metadata_mapping(
            self._domains)

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal

    def read_metadata_fields(self, file_path: str) -> dict[str, object]:
        """Read metadata values."""
        a = self._metadata
        return read_fields_from_columns(file_path)
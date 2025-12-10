from model.bio_portal_client import BioPortalClient
from persistence.domain_ontology_dao import DomainOntologyDao
from persistence.metadata_mapping_dao import MetadataMappingDao
from services.metadata_excel_io import MetadataExcelIO

class ModelOntology:
    """
    Instantiate the BioPortal client here so all controllers/views depend on a
    single, configured entry point for ontology lookups.
    """

    def __init__(self, api_key=None,
                 metadata_excel_io: MetadataExcelIO | None = None):
        self._bioportal = BioPortalClient(api_key=api_key)
        self._domains = DomainOntologyDao.load_domain_ontologies()
        self._metadata = MetadataMappingDao.load_metadata_mapping(
            self._domains)
        self._metadata_excel_io = metadata_excel_io or MetadataExcelIO()

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal

    def read_metadata_fields(self, file_path: str):
        """Populate metadata values by reading the provided Excel file.

        The Excel file is expected to contain, for each metadata entry, a cell
        whose coordinate matches ``metadata.code`` (e.g. ``"B29"``) and whose
        value matches ``metadata.cell_name``. The value to be stored in
        ``metadata.cell_value`` is read from the adjacent cell to the right.
        """

        return self._metadata_excel_io.read_metadata_values(self._metadata,
                                                            file_path)

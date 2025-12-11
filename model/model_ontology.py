from pathlib import Path

from model.bio_portal_client import BioPortalClient
from model.ontology import Ontology
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
        file_path = Path(file_path)
        return self._metadata_excel_io.read_metadata_values(self._metadata, file_path)

    def search_ontology_from_metadata(self):
        """Use BioPortal to populate ontology details for each metadata term.

        The Excel-derived ``cell_value`` of each metadata entry is used as
        search term and the corresponding ``domain.ontology.id`` drives which
        ontology is queried. When a match is found, a dedicated ``Ontology``
        instance is attached to the metadata with ``value`` (notation),
        ``base_uri`` (purl/IRI) and ``synonyms`` populated.
        """

        for metadata in self._metadata:
            term = metadata.cell_value.upper()
            ontology_id = metadata.domain.ontology.id.upper()

            if not term:
                continue

            result = self._bioportal.search_ontology(term=term,
                                                     ontology=ontology_id)
            if result is None:
                metadata.ontology = Ontology(id=ontology_id)
                continue

            metadata.domain.ontology = Ontology(
                id=ontology_id,
                value=result.get("notation", "") or result.get("identifier",
                                                               ""),
                base_uri=result.get("purl", ""),
                synonyms=result.get("synonyms", []),
            )

        return self._metadata
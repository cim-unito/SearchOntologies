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
        self._domains = DomainOntologyDao.load_domain_ontologies()
        self._bioportal = BioPortalClient(
            api_key=api_key)
        self._metadata_container = MetadataMappingDao.load_metadata_mapping(
            self._domains)
        self._metadata_excel_io = metadata_excel_io or MetadataExcelIO()

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal

    def read_metadata_fields(self, file_path: str):
        """Populate metadata values by reading the provided Excel file."""
        file_path = Path(file_path)
        return self._metadata_excel_io.read_metadata_values(
            self._metadata_container,
            file_path)

    def search_ontology_from_metadata(self):
        """
        Use BioPortal to populate ontology details for each metadata term.
        """
        metadata_dict = self._metadata_container.get_cells()
        for code, meta in metadata_dict.items():
            domain = meta.get_domain()
            cell_value = meta.get_cell_value()

            if not cell_value or not domain or not domain.ontology:
                continue

            if domain.id.casefold() == "dataset":
                continue

            ontology_id = meta.get_ontology_id()
            if not ontology_id:
                continue

            result = self._bioportal.search_ontology(cell_value=cell_value,
                                                     ontology_id=ontology_id)
            if result is None:
                domain.ontology = Ontology(id=ontology_id)
                continue

            domain.ontology = Ontology(
                id=ontology_id,
                value=result.get("notation", ""),
                base_uri=result.get("purl", ""),
                synonyms=result.get("synonyms", []),
            )

        return self._metadata_container

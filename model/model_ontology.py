from pathlib import Path

from model.bio_portal_client import BioPortalClient
from model.metadata import Metadata
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

    def search_terms_from_metadata(self) -> list[tuple[Metadata, str, Ontology]]:
        """
        Use BioPortal to populate ontology details for each metadata term.

        Returns a list of (metadata, term, ontology) tuples.
        """
        metadata_dict = self._metadata_container.get_cells()
        results: list[tuple[Metadata, str, Ontology]] = []
        cache: dict[tuple[str, str], dict | None] = {}
        for meta in metadata_dict.values():
            domain = meta.get_domain()
            cell_value = meta.get_cell_value()

            if not cell_value or not domain or not domain.ontology:
                continue

            if domain.id.casefold() == "dataset":
                continue

            ontology_id = meta.get_ontology_id()
            if not ontology_id:
                continue

            terms = self._split_terms(cell_value)
            for term in terms:
                cache_key = (ontology_id, term.casefold())
                if cache_key not in cache:
                    cache[cache_key] = self._bioportal.search_ontology(
                        cell_value=term,
                        ontology_id=ontology_id
                    )
                result = cache[cache_key]
                if result is None:
                    ontology = Ontology(id=ontology_id)
                else:
                    ontology = Ontology(
                        id=ontology_id,
                        value=result.get("notation", ""),
                        base_uri=result.get("purl", ""),
                        synonyms=result.get("synonyms", []),
                    )

                results.append((meta, term, ontology))

        return results

    def split_terms(self, cell_value: str) -> list[str]:
        """Return a cleaned list of comma-separated terms."""
        return self._split_terms(cell_value)

    @staticmethod
    def _split_terms(cell_value: str) -> list[str]:
        if not cell_value:
            return []
        parts = [part.strip() for part in cell_value.split(",")]
        return [part for part in parts if part]
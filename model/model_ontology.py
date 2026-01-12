from pathlib import Path

from model.bio_portal_client import BioPortalClient
from model.metadata import Metadata
from model.ontology import Ontology
from persistence.domain_ontology_dao import DomainOntologyDao
from persistence.metadata_mapping_dao import MetadataMappingDao
from services.metadata_file_io import MetadataFileIO


class ModelOntology:
    """
    Instantiate the BioPortal client here so all controllers/views depend on a
    single, configured entry point for ontology lookups.
    """

    def __init__(self, api_key=None,
                 metadata_file_io: MetadataFileIO | None = None):
        self._domains = DomainOntologyDao.load_domain_ontologies()
        self._bioportal = BioPortalClient(
            api_key=api_key)
        self._metadata_container = MetadataMappingDao.load_metadata_mapping(
            self._domains)
        self._metadata_file_io = metadata_file_io or MetadataFileIO()

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal

    def read_metadata_fields(self, file_path: str):
        """Populate metadata values by reading the provided Excel file."""
        file_path = Path(file_path)
        return self._metadata_file_io.read_metadata_values(
            self._metadata_container,
            file_path)

    def export_csvs(self, directory_path: str,
                    user_selection: dict[str, str]):
        """Export ontology selections and terms to CSV files."""
        metadata_container = self._metadata_container
        dataset_id = self._get_dataset_id(metadata_container)
        code_rows, term_rows = self._build_export_rows(
            metadata_container, user_selection, dataset_id
        )

        if not code_rows and not term_rows:
            return None, None

        directory = Path(directory_path)
        codes_path = directory / "ontology_codes.csv"
        terms_path = directory / "ontology_terms.csv"

        self._metadata_file_io.write_csv(
            codes_path,
            ["DatasetId", "OntologyDomain", "OntologyCode"],
            code_rows,
        )
        self._metadata_file_io.write_csv(
            terms_path,
            ["DatasetId", "OntologyDomain", "OntologyTerm"],
            term_rows,
        )

        return codes_path, terms_path

    def search_terms_from_metadata(self) -> list[
        tuple[Metadata, str, list[Ontology]]]:
        """
        Use BioPortal to populate ontology details for each metadata term.

        Returns a list of (metadata, term, ontology) tuples.
        """
        metadata_dict = self._metadata_container.get_cells()
        results = []
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
                result_items = self._bioportal.search_ontology(
                    cell_value=term,
                    ontology_id=ontology_id
                )
                candidates = []
                for item in result_items:
                    candidates.append(Ontology(
                        id=ontology_id,
                        value=item.get("notation", ""),
                        base_uri=item.get("purl", ""),
                        synonyms=item.get("synonyms", []),
                    ))

                results.append((meta, term, candidates))

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

    def _build_export_rows(self, metadata_container,
                           user_selection: dict[str, str],
                           dataset_id: str):
        code_rows = []
        term_rows = []
        metadata_container_sorted = metadata_container.get_cells_sorted()

        for metadata in metadata_container_sorted.values():
            domain = getattr(metadata, "domain", None)
            if not domain or not domain.ontology:
                continue
            if domain.id.casefold() == "dataset":
                continue

            terms = self.split_terms(
                getattr(metadata, "cell_value", "")
            )
            if not terms:
                continue

            ontology_domain = self._format_ontology_domain(metadata)
            for term in terms:
                group_id = f"{metadata.code}:{term}"
                ontology_code = user_selection.get(group_id, "")
                code_rows.append({
                    "DatasetId": dataset_id,
                    "OntologyDomain": ontology_domain,
                    "OntologyCode": ontology_code,
                })
                term_rows.append({
                    "DatasetId": dataset_id,
                    "OntologyDomain": ontology_domain,
                    "OntologyTerm": term,
                })

        return code_rows, term_rows

    def _get_dataset_id(self, metadata_container) -> str:
        for metadata in metadata_container.get_cells().values():
            domain = getattr(metadata, "domain", None)
            if domain and domain.id.casefold() == "dataset":
                return getattr(metadata, "cell_value", "") or ""
        return ""

    def _format_ontology_domain(self, metadata) -> str:
        ontology_id = getattr(metadata.domain.ontology, "id", "") or ""
        domain_value = metadata.subdomain or metadata.domain.id
        return f"{self._pascal_case(ontology_id)}{self._pascal_case(domain_value)}"

    @staticmethod
    def _pascal_case(value: str) -> str:
        if not value:
            return ""
        cleaned = "".join(
            char if char.isalnum() else " "
            for char in value.strip()
        )
        return "".join(word.capitalize() for word in cleaned.split())
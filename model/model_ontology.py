from pathlib import Path

from model.bio_portal_client import BioPortalClient
from model.metadata import Metadata
from model.ontology import Ontology
from model.ontology_selection import OntologySelection
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

    def get_dataset_id(self) -> str:
        """Return the dataset id from loaded metadata."""
        return self._metadata_container.get_dataset_id()

    def export_csv(
            self,
            directory_path: str,
            user_selection: dict[str, str],
            selection_details: list[OntologySelection] | None = None,
            export_format: str = "csv",
            empty_value: str = "",
    ) -> list[Path]:
        """Export ontology selections to CSV or Excel files."""
        metadata_container = self._metadata_container
        dataset_id = metadata_container.get_dataset_id()
        fieldnames, row = self._build_export_row(
            metadata_container, user_selection, dataset_id, empty_value
        )
        directory = Path(directory_path)
        export_paths: list[Path] = []
        if fieldnames:
            export_paths.extend(
                self._write_ontology_export(
                    directory,
                    dataset_id,
                    fieldnames,
                    [row],
                    export_format,
                )
            )

        selection_details = selection_details or []
        selection_rows = self._build_selection_rows(
            selection_details,
            empty_value,
        )
        if selection_rows:
            export_paths.extend(
                self._write_synonyms_export(
                    directory,
                    dataset_id,
                    selection_rows,
                    export_format,
                )
            )

        return export_paths

    def reset_metadata(self) -> None:
        """Reset stored metadata values to initial state."""
        self._metadata_container.reset_values()

    def search_terms_from_metadata(self) -> list[
        tuple[Metadata, str, list[Ontology]]]:
        """
        Use BioPortal to populate ontology details for each metadata term.

        Returns a list of (metadata, term, ontology) tuples.
        """
        metadata_dict = self._metadata_container.get_cells_sorted()
        results = []
        for meta in metadata_dict.values():
            domain = meta.get_domain()

            if not domain or domain.id.casefold() == "dataset":
                continue

            cell_value = meta.get_cell_value()
            terms = self._split_terms(cell_value) if cell_value else [""]
            ontology_id = (
                meta.get_ontology_id()
                if getattr(domain, "ontology", None)
                else ""
            )

            for term in terms:
                candidates = []

                if term and ontology_id:
                    result_items = self._bioportal.search_ontology(
                        cell_value=term,
                        ontology_id=ontology_id,
                    )
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
    def build_group_id(metadata, term: str, index: int) -> str:
        safe_term = term if term else "<empty>"
        return f"{metadata.code}:{safe_term}:{index}"

    @staticmethod
    def _split_terms(cell_value: str) -> list[str]:
        if not cell_value:
            return []
        parts = [part.strip() for part in cell_value.split(",")]
        return [part for part in parts if part]

    def _build_export_row(self, metadata_container,
                          user_selection: dict[str, str],
                          dataset_id: str,
                          empty_value: str):
        domain_order = []
        domain_values = {}
        entry_index = 0

        for metadata in metadata_container.get_cells_sorted().values():
            domain = getattr(metadata, "domain", None)
            if not domain or not domain.ontology:
                continue
            if domain.id.casefold() == "dataset":
                continue

            ontology_domain = self._format_ontology_domain(metadata)
            if ontology_domain not in domain_values:
                domain_order.append(ontology_domain)
                domain_values[ontology_domain] = []

            terms = self.split_terms(
                getattr(metadata, "cell_value", "")
            )
            if not terms:
                continue

            for term in terms:
                group_id = self.build_group_id(metadata, term, entry_index)
                entry_index += 1
                ontology_code = user_selection.get(group_id, "")
                if ontology_code:
                    domain_values[ontology_domain].append(ontology_code)

        if not domain_order:
            return [], {}

        row = {"DatasetId": dataset_id}
        for ontology_domain in domain_order:
            row[ontology_domain] = self._format_cell_value(
                domain_values.get(ontology_domain, []),
                empty_value,
            )

        return ["DatasetId", *domain_order], row

    def _build_selection_rows(
            self,
            selection_details: list[OntologySelection],
            empty_value: str,
    ) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for selection in selection_details:
            if not selection.code:
                continue
            grouped.setdefault(selection.code, [])
            grouped[selection.code].extend(selection.synonyms or [])

        rows = []
        for code, synonyms in grouped.items():
            rows.append({
                "OntologyCode": code,
                "Synonyms": self._format_cell_value(
                    self._unique_synonyms(synonyms),
                    empty_value,
                ),
            })
        return rows

    def _write_ontology_export(
            self,
            directory: Path,
            dataset_id: str,
            fieldnames: list[str],
            rows: list[dict],
            export_format: str,
    ) -> list[Path]:
        if export_format == "excel":
            return [
                self._metadata_file_io.write_ontology_export_excel(
                    directory,
                    dataset_id,
                    fieldnames,
                    rows,
                )
            ]
        return [
            self._metadata_file_io.write_ontology_export(
                directory,
                dataset_id,
                fieldnames,
                rows,
            )
        ]

    def _write_synonyms_export(
            self,
            directory: Path,
            dataset_id: str,
            rows: list[dict],
            export_format: str,
    ) -> list[Path]:
        if export_format == "excel":
            return [
                self._metadata_file_io.write_synonyms_export_excel(
                    directory,
                    dataset_id,
                    rows,
                )
            ]
        return [
            self._metadata_file_io.write_synonyms_export(
                directory,
                dataset_id,
                rows,
            )
        ]

    def _format_ontology_domain(self, metadata) -> str:
        ontology_id = getattr(metadata.domain.ontology, "id", "") or ""
        domain_value = metadata.subdomain or metadata.domain.id
        return f"{self._pascal_case(ontology_id)}{self._pascal_case(domain_value)}"

    @staticmethod
    def _format_cell_value(values: list[str], empty_value: str) -> str:
        cleaned = [value for value in values if value]
        if not cleaned:
            return "NULL"
        return ";".join(cleaned) if cleaned else empty_value

    @staticmethod
    def _unique_synonyms(values: list[str]) -> list[str]:
        unique = []
        seen = set()
        for value in values or []:
            if not value:
                continue
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            unique.append(value)
        return unique

    @staticmethod
    def _pascal_case(value: str) -> str:
        if not value:
            return ""
        cleaned = "".join(
            char if char.isalnum() else " "
            for char in value.strip()
        )
        return "".join(word.capitalize() for word in cleaned.split())
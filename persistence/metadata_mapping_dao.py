from pathlib import Path
from typing import Mapping
import re

from model.metadata_container import MetadataContainer
from model.ontology import Ontology
from persistence.json_reader import JsonReader, JsonFormatError
from model.domain import Domain
from model.metadata import Metadata


class MetadataMappingDao:
    METADATA_MAPPING_JSON = Path(
        __file__).resolve().parent / "metadata_mapping.json"

    @classmethod
    def load_metadata_mapping(cls, domain_lookup: Mapping[str, Domain]
                              ) -> MetadataContainer:
        """Load metadata entries."""
        raw = JsonReader.read_json(cls.METADATA_MAPPING_JSON)
        if not isinstance(raw, dict):
            raise JsonFormatError(
                "Expected a JSON array of metadata entries")

        domains = {name.casefold(): domain for name, domain in
                   domain_lookup.items()}

        cells = {}
        raw_cells = raw.get("cells")
        if not isinstance(raw_cells, dict):
            raise JsonFormatError("Field 'cells' must be an object mapping")
        for id_cell, item_cell in raw_cells.items():
            code = cls._get_valid_id(id_cell)
            cell_name = cls._get_required_str(item_cell, "cell_name")
            domain_name = cls._get_required_str(item_cell, "domain")
            subdomain = cls._get_required_str(item_cell, "subdomain")

            domain = domains.get(domain_name.casefold())
            if domain is None:
                raise JsonFormatError(
                    f"Unknown domain '{domain_name}'"
                )

            domain = Domain(
                id=domain.id,
                ontology=Ontology(
                    id=domain.ontology.id,
                    value=domain.ontology.value,
                    base_uri=domain.ontology.base_uri,
                    synonyms=list(domain.ontology.synonyms),
                ),
            )

            cells[code] = Metadata(
                code=code,
                cell_name=cell_name,
                domain=domain,
                subdomain=subdomain,
            )

        return MetadataContainer(
            sheet_name=raw["sheet_name"],
            column_index=raw["column_index"],
            cells=cells
        )

    @classmethod
    def _get_valid_id(cls, id_cell) -> str:
        if not isinstance(id_cell, str):
            raise JsonFormatError(
                f"Field '{id_cell}' must be a string,"
                f" got {type(id_cell).__name__}"
            )

        cleaned = id_cell.strip()
        if not cleaned:
            raise JsonFormatError(
                f"Field '{id_cell}' cannot be empty")

        match = re.fullmatch(r"([A-Za-z]+)([0-9]+)", id_cell)
        if not match:
            raise JsonFormatError(
                f"Field '{id_cell}' must be letters + numbers"
                f" (e.g. B29, AA1035)")

        return cleaned

    @classmethod
    def _get_required_str(cls, mapping: Mapping[str, object], key: str) -> str:
        try:
            value = mapping[key]
        except KeyError as exc:
            raise JsonFormatError(
                f"Missing required field '{key}'") from exc

        if not isinstance(value, str):
            raise JsonFormatError(
                f"Field '{key}' must be a string,"
                f" got {type(value).__name__}"
            )

        cleaned = value.strip()
        if not cleaned:
            raise JsonFormatError(
                f"Field '{key}' cannot be empty")

        return cleaned
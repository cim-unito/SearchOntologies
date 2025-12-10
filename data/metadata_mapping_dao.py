from pathlib import Path
from typing import Mapping

from data.json_reader import JsonReader, JsonFormatError
from model.domain import Domain
from model.metadata import Metadata
from model.ontology import Ontology


class DomainOntologyDao:
    DOMIAN_ONTOLOGY_JSON = Path(__file__).resolve().parent / "metadata_mapping_dao.json"

    @classmethod
    def load_metadata_mapping(
            cls, domain_lookup: Mapping[str, Domain]
    ) -> list[Metadata]:
        """Load metadata entries and resolve domains using ``domain_lookup``."""

        raw = JsonReader.read_json(cls.DOMIAN_ONTOLOGY_JSON)
        if not isinstance(raw, list):
            raise JsonFormatError(
                "Expected a JSON array of metadata entries")

        domains = {name.casefold(): domain for name, domain in
                   domain_lookup.items()}

        metadata_items: list[Metadata] = []
        for idx, item in enumerate(raw, start=1):
            if not isinstance(item, Mapping):
                raise JsonFormatError(
                    f"Metadata entry #{idx} must be an object, got {type(item).__name__}"
                )

            code = cls._get_required_str(item, "code", idx)
            cell_name = cls._get_required_str(item, "cell_name", idx)
            domain_name = cls._get_required_str(item, "domain", idx)
            subdomain = cls._get_required_str(item, "subdomain", idx)

            domain = domains.get(domain_name.casefold())
            if domain is None:
                raise JsonFormatError(
                    f"Unknown domain '{domain_name}' in metadata entry #{idx}"
                )

            metadata_items.append(
                Metadata(
                    code=code,
                    cell_name=cell_name,
                    domain=domain,
                    subdomain=subdomain,
                )
            )

        return metadata_items

    @classmethod
    def _get_required_str(cls, mapping: Mapping[str, object], key: str,
                          index: int) -> str:
        try:
            value = mapping[key]
        except KeyError as exc:
            raise JsonFormatError(
                f"Missing required field '{key}' in item #{index}") from exc

        if not isinstance(value, str):
            raise JsonFormatError(
                f"Field '{key}' in item #{index} must be a string, got {type(value).__name__}"
            )

        cleaned = value.strip()
        if not cleaned:
            raise JsonFormatError(
                f"Field '{key}' in item #{index} cannot be empty")

        return cleaned
from pathlib import Path
from typing import Mapping

from persistence.json_reader import JsonReader, JsonFormatError
from model.domain import Domain
from model.metadata import Metadata


class MetadataMappingDao:
    METADATA_MAPPING_JSON = Path(
        __file__).resolve().parent / "metadata_mapping.json"

    @classmethod
    def load_metadata_mapping(cls, domain_lookup: Mapping[str, Domain]
                              ) -> list[Metadata]:
        """Load metadata entries."""
        raw = JsonReader.read_json(cls.METADATA_MAPPING_JSON)
        if not isinstance(raw, list):
            raise JsonFormatError(
                "Expected a JSON array of metadata entries")

        domains = {name.casefold(): domain for name, domain in
                   domain_lookup.items()}

        metadata_list: list[Metadata] = []
        for idx, item in enumerate(raw, start=1):
            code = cls._get_required_str(item, "code", idx)
            cell_name = cls._get_required_str(item, "cell_name", idx)
            domain_name = cls._get_required_str(item, "domain", idx)
            subdomain = cls._get_required_str(item, "subdomain", idx)

            domain = domains.get(domain_name.casefold())
            if domain is None:
                raise JsonFormatError(
                    f"Unknown domain '{domain_name}' in metadata entry #{idx}"
                )

            metadata_list.append(
                Metadata(
                    code=code,
                    cell_name=cell_name,
                    domain=domain,
                    subdomain=subdomain,
                )
            )

        return metadata_list

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
                f"Field '{key}' in item #{index} must be a string,"
                f" got {type(value).__name__}"
            )

        cleaned = value.strip()
        if not cleaned:
            raise JsonFormatError(
                f"Field '{key}' in item #{index} cannot be empty")

        return cleaned
from pathlib import Path

from persistence.json_reader import JsonReader, JsonFormatError
from model.domain import Domain
from model.ontology import Ontology


class DomainOntologyDao:
    DOMAIN_ONTOLOGY_JSON = Path(
        __file__).resolve().parent / "domain_ontology.json"

    @classmethod
    def load_domain_ontologies(cls) -> dict[str, Domain]:
        """Load domain→ontology mapping into Domain objects."""
        raw = JsonReader.read_json(cls.DOMAIN_ONTOLOGY_JSON)
        if not isinstance(raw, dict):
            raise JsonFormatError(
                "Expected a JSON object mapping domain to ontology id")

        domains = {}
        for domain_name, ontology_id in raw.items():
            if not isinstance(domain_name, str) or not isinstance(ontology_id,
                                                                  str):
                raise JsonFormatError(
                    "Domain and ontology ids must be strings")

            domain_value = domain_name.strip()
            ontology_code = ontology_id.strip()
            if not domain_value or not ontology_code:
                raise JsonFormatError(
                    "Domain and ontology ids cannot be empty")

            key = domain_value.casefold()
            if key in domains:
                raise JsonFormatError(f"Duplicate domain entry: {domain_name}")

            domains[key] = Domain(
                id=domain_value,
                ontology=Ontology(id=ontology_code),
            )

        return domains

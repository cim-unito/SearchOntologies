from pathlib import Path

from data.json_reader import JsonReader, JsonFormatError
from model.domain import Domain
from model.ontology import Ontology


class DomainOntologyDao:
    DOMIAN_ONTOLOGY_JSON = Path(__file__).resolve().parent / "domain_ontology.json"

    @classmethod
    def load_domain_ontologies(cls) -> dict[str, Domain]:
        """
        Load domain→ontology mapping into Domain objects.
        """
        raw = JsonReader.read_json(cls.DOMIAN_ONTOLOGY_JSON)
        if not isinstance(raw, dict):
            raise JsonFormatError(
                "Expected a JSON object mapping domain to ontology id")

        domains = {}
        for domain_name, ontology_id in raw.items():
            if not isinstance(domain_name, str) or not isinstance(ontology_id,
                                                                  str):
                raise JsonFormatError(
                    "Domain and ontology ids must be strings")

            name = domain_name.strip()
            ontology_code = ontology_id.strip()
            if not name or not ontology_code:
                raise JsonFormatError(
                    "Domain and ontology ids cannot be empty")

            key = name.casefold()
            if key in domains:
                raise JsonFormatError(f"Duplicate domain entry: {domain_name}")

            domains[key] = Domain(
                id=name,
                ontology=Ontology(id=ontology_code, base_uri="", synonyms=[]),
            )

        return domains

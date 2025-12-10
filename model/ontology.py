from dataclasses import dataclass


@dataclass
class Ontology:
    id: str
    base_uri: str
    synonyms: list[str]


from dataclasses import dataclass


@dataclass
class Ontology:
    id: str
    base_uri: str
    synonyms: str


from dataclasses import dataclass, field


@dataclass
class Ontology:
    id: str
    base_uri: str = ""
    synonyms: list[str] = field(default_factory=list)


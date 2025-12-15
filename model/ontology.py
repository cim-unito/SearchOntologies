from dataclasses import dataclass, field


@dataclass
class Ontology:
    """Describe an ontology entry and its metadata."""
    id: str
    value: str = ""
    base_uri: str = ""
    synonyms: list[str] = field(default_factory=list)


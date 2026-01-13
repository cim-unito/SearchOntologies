from dataclasses import dataclass, field


@dataclass(frozen=True)
class OntologySelection:
    """Describe a selected ontology entry for export."""
    code: str
    synonyms: list[str] = field(default_factory=list)
from dataclasses import dataclass, field


@dataclass
class Ontology:
    id: str
    value: str = ""
    base_uri: str = ""
    synonyms: list[str] = field(default_factory=list)

    def get_id(self) -> str:
        return self.id
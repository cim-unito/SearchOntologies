"""Ontology representation with optional synonyms."""

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Ontology:
    """Describe an ontology entry and its metadata."""

    id: str
    value: str = ""
    base_uri: str = ""
    synonyms: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("id must be a string")
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")
        if not isinstance(self.base_uri, str):
            raise TypeError("base_uri must be a string")

        if isinstance(self.synonyms, Iterable) and not isinstance(
                self.synonyms, list):
            self.synonyms = list(self.synonyms)

        if not isinstance(self.synonyms, list):
            raise TypeError("synonyms must be provided as a list of strings")
        if not all(isinstance(synonym, str) for synonym in self.synonyms):
            raise TypeError("all synonyms must be strings")

    def get_id(self) -> str:
        """Return the ontology identifier."""

        return self.id
"""Definitions for ontology domains."""

from dataclasses import dataclass

from model.ontology import Ontology


@dataclass
class Domain:
    """Associate a domain identifier with its ontology."""

    id: str
    ontology: Ontology

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("id must be a string")
        if not isinstance(self.ontology, Ontology):
            raise TypeError("ontology must be an Ontology instance")

    def get_ontology(self) -> Ontology:
        """Return the ontology that owns this domain."""

        return self.ontology
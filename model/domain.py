from dataclasses import dataclass

from model.ontology import Ontology


@dataclass
class Domain:
    """Associate a domain identifier with its ontology."""
    id: str
    ontology: Ontology

    def get_ontology(self) -> Ontology:
        """Return the ontology that owns this domain."""
        return self.ontology
from dataclasses import dataclass

from model.data.ontology import Ontology


@dataclass(frozen=True)
class Domain:
    id: str
    ontology: Ontology
from dataclasses import dataclass

from model.ontology import Ontology


@dataclass
class Domain:
    id: str
    ontology: Ontology = None

    def get_ontology(self):
        return self.ontology
from dataclasses import dataclass

from model.domain import Domain


@dataclass
class Metadata:
    code: str
    cell_name: str
    subdomain: str
    domain: Domain
    cell_value: str = ""

    def get_domain(self):
        return self.domain

    def get_cell_value(self):
        return self.cell_value
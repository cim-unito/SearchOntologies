from dataclasses import dataclass

from model.domain import Domain


@dataclass
class Metadata:
    code: str
    cell_name: str
    subdomain: str
    domain: Domain = None
    cell_value: str = ""

    def get_domain(self):
        return self.domain
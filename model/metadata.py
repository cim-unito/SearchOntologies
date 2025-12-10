from dataclasses import dataclass

from model.domain import Domain


@dataclass
class Metadata:
    code: str
    cell_name: str
    domain: Domain
    subdomain: str

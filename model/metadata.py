from dataclasses import dataclass

from model.domain import Domain


@dataclass
class Metadata:
    """Describe a metadata cell within a sheet."""
    code: str
    cell_name: str
    subdomain: str
    domain: Domain
    cell_value: str = ""

    def get_domain(self) -> Domain:
        """Return the domain for this metadata entry."""
        return self.domain

    def get_cell_value(self) -> str:
        """Return the stored value for this metadata entry."""
        return self.cell_value
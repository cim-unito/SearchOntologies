"""Definitions for metadata items used in Excel extraction/serialization."""

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

    def __post_init__(self) -> None:
        if not isinstance(self.code, str):
            raise TypeError("code must be a string")
        if not isinstance(self.cell_name, str):
            raise TypeError("cell_name must be a string")
        if not isinstance(self.subdomain, str):
            raise TypeError("subdomain must be a string")
        if not isinstance(self.domain, Domain):
            raise TypeError("domain must be a Domain instance")
        if not isinstance(self.cell_value, str):
            raise TypeError("cell_value must be a string")

    def get_domain(self) -> Domain:
        """Return the domain for this metadata entry."""

        return self.domain

    def get_cell_value(self) -> str:
        """Return the stored value for this metadata entry."""

        return self.cell_value
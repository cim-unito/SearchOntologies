from model.bio_portal_client import BioPortalClient


class ModelOntology:
    """
    Instantiate the BioPortal client here so all controllers/views depend on a
    single, configured entry point for ontology lookups.
    """

    def __init__(self, api_key=None):
        self._bioportal = BioPortalClient(api_key=api_key)

    @property
    def bioportal(self) -> BioPortalClient:
        return self._bioportal
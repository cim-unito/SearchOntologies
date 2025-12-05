import requests

from config import Config, ConfigError

BIOPORTAL_URL = "https://data.bioontology.org/search"
DEFAULT_TIMEOUT = 30


class BioPortalError(RuntimeError):
    """Raised for unexpected BioPortal communication issues."""


class BioPortalClient:
    """
    The API key is resolved once at initialization to avoid repeated reads and
    to centralize where ``Config.api_key`` is invoked.
    """

    def __init__(
            self, api_key: str | None = None,
            session: requests.Session | None = None
    ):
        self._api_key = (api_key or Config.api_key()).strip()
        self._session = session or requests.Session()

    @property
    def api_key(self) -> str:
        return self._api_key

    def search_ontology(self, term: str, ontology: str) -> str | None:
        """
        Search a single ontology and return the best-matching identifier.

        Raises:
            BioPortalError: when the service returns an unexpected status code
                or the response cannot be parsed.
        """

        params = {"q": term, "ontologies": ontology, "apikey": self._api_key}

        try:
            response = self._session.get(
                BIOPORTAL_URL, params=params, timeout=DEFAULT_TIMEOUT
            )
        except requests.RequestException as exc:
            raise BioPortalError(
                f"Communication error with BioPortal: {exc}") from exc

        if response.status_code != 200:
            raise BioPortalError(
                "BioPortal responded with an unexpected status: "
                f"{response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise BioPortalError(
                "Invalid BioPortal response (JSON expected)") from exc

        items = payload.get("collection", [])
        if not items:
            return None

        return self._best_identifier(items[0])

    @staticmethod
    def _best_identifier(item) -> str | None:
        """Return the best identifier from a BioPortal result."""

        for key in ("obo_id", "notation", "@id"):
            candidate = item.get(key)
            if candidate:
                return str(candidate)
        return None

import requests

from config.config import Config, ConfigError

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

    def search_ontology(self, term: str, ontology: str) -> dict | None:
        """
        Search a single ontology and return details of the best match.

        The returned dictionary contains, when available:
        ``identifier`` (best IRI/obo id), ``notation`` (compact code), ``purl``
        and ``synonyms`` (list of strings).
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

        first_item = items[0]
        identifier = self._best_identifier(first_item)

        return {
            "identifier": identifier,
            "notation": self._best_notation(first_item, identifier),
            "purl": self._extract_purl(first_item, identifier),
            "synonyms": self._extract_synonyms(first_item),
        }

    @staticmethod
    def _best_identifier(item) -> str | None:
        """Return the best identifier from a BioPortal result."""

        for key in ("obo_id", "notation", "@id"):
            candidate = item.get(key)
            if candidate:
                return str(candidate)
        return None

    @staticmethod
    def _best_notation(item: dict, identifier: str | None) -> str:
        """Extract a compact notation (e.g., ``162`` from ``DOID:162``)."""

        notation = item.get("notation") or item.get("obo_id")
        if isinstance(notation, str) and notation:
            if ":" in notation:
                return notation.split(":", maxsplit=1)[-1]
            return notation

        if identifier and "_" in identifier:
            return identifier.rsplit("_", maxsplit=1)[-1]

        if identifier and "/" in identifier:
            return identifier.rstrip("/").rsplit("/", maxsplit=1)[-1]

        return ""

    @staticmethod
    def _extract_purl(item: dict, identifier: str | None) -> str:
        """Return the primary IRI/purl if present."""

        iri = item.get("@id") or item.get("links", {}).get("self")
        if iri:
            return str(iri)
        return identifier or ""

    @staticmethod
    def _extract_synonyms(item: dict) -> list[str]:
        """Collect synonyms from common BioPortal fields."""

        candidates = item.get("synonym") or item.get("synonyms") or []
        if isinstance(candidates, str):
            return [candidates.strip()] if candidates.strip() else []
        if isinstance(candidates, list):
            return [str(s).strip() for s in candidates if str(s).strip()]
        return []
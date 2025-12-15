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
            session: requests.Session | None = None,
            allowed_ontologies: set[str] | None = None,
    ):
        self._api_key = (api_key or Config.api_key()).strip()
        if not self._api_key:
            raise ConfigError("BioPortal API key is missing or empty")

        self._allowed_ontologies = (
            {self._normalize_ontology_id(o) for o in allowed_ontologies}
            if allowed_ontologies else None
        )
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

        ontology_code = self._normalize_ontology_id(ontology)
        if self._allowed_ontologies is not None and ontology_code not in self._allowed_ontologies:
            raise BioPortalError(
                f"Ontology '{ontology}' is not declared in the allowed list")

        params = {
            "q": term.strip(),
            "ontologies": ontology_code,
            "apikey": self._api_key,
        }

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
        best_item = self._select_best_item(term, items)
        if not best_item:
            return None

        identifier = self._best_identifier(best_item)

        return {
            "identifier": identifier,
            "notation": self._best_notation(best_item, identifier),
            "purl": self._extract_purl(best_item, identifier),
            "synonyms": self._extract_synonyms(best_item),
        }

    @staticmethod
    def _normalize_ontology_id(ontology: str | None) -> str:
        """Normalize ontology identifiers for consistent comparisons."""

        return (ontology or "").strip().upper()

    @staticmethod
    def _select_best_item(term: str, items: list[dict]) -> dict | None:
        """Pick the most relevant result returned by BioPortal.

        The original implementation relied solely on the numeric ``score``
        returned by BioPortal. This version keeps that as the baseline but
        strongly prioritizes exact matches on ``prefLabel``, ``synonym`` and
        ``notation`` so that the "best" item reflects label quality as well as
        BioPortal's relevance score.
        """

        if not isinstance(items, list) or not items:
            return None

        normalized_term = BioPortalClient._normalize_text(term)

        def weighting(item: dict) -> tuple[int, int, int, float, str]:
            try:
                base_score = float(item.get("score", 0))
            except (TypeError, ValueError):
                base_score = 0.0

            pref_label = BioPortalClient._normalize_text(item.get("prefLabel"))
            synonyms = {
                BioPortalClient._normalize_text(s)
                for s in (item.get("synonym") or item.get("synonyms") or [])
                if BioPortalClient._normalize_text(s)
            }
            notation = BioPortalClient._normalize_text(item.get("notation"))

            pref_match = 1 if pref_label and pref_label == normalized_term else 0
            synonym_match = 1 if normalized_term in synonyms else 0
            notation_match = 1 if notation and notation == normalized_term else 0

            return (
                pref_match,
                synonym_match,
                notation_match,
                base_score,
                pref_label or "",
            )

        return max(items, key=weighting)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        """Lowercase/trim a text value for comparisons."""
        return value.strip().casefold() if isinstance(value, str) else ""

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
        """
        Derive a canonical PURL for the result.

        Even when a caller already has an identifier, this helper is still
        required to normalize CURIEs/IRIs into the OBO PURL form so that the
        rest of the application can rely on consistent values.
        """

        # Prefer OBO-style PURLs when an ``obo_id``/CURIE is available so that
        # NCIT, MONDO, DOID, etc. are always returned in the
        # ``http://purl.obolibrary.org/obo/`` form.
        for candidate in (item.get("obo_id"), identifier):
            purl = BioPortalClient._obo_id_to_purl(candidate)
            if purl:
                return purl

        iri = item.get("@id") or item.get("links", {}).get("self") or identifier

        ncit_purl = BioPortalClient._ncit_iri_to_purl(iri)
        if ncit_purl:
            return ncit_purl

        if iri:
            return str(iri)
        return identifier or ""

    @staticmethod
    def _obo_id_to_purl(value: str | None) -> str:
        """Convert CURIE/obo_id values to an OBO PURL if possible."""

        if not isinstance(value, str):
            return ""

        trimmed = value.strip()
        if not trimmed:
            return ""

        if trimmed.startswith(("http://purl.obolibrary.org/obo/",
                               "https://purl.obolibrary.org/obo/")):
            return trimmed

        # Ignore full IRIs such as "http://ncicb.nci.nih.gov/..." to avoid
        # producing broken PURLs like
        # ``http://purl.obolibrary.org/obo/http_//ncicb.nci.nih.gov/...``.
        if "://" in trimmed or "/" in trimmed.split(":", maxsplit=1)[-1]:
            return ""

        if ":" in trimmed:
            prefix, local_id = trimmed.split(":", maxsplit=1)
        elif "_" in trimmed:
            prefix, local_id = trimmed.split("_", maxsplit=1)
        else:
            return ""

        if not prefix or not local_id:
            return ""
        return f"http://purl.obolibrary.org/obo/{prefix}_{local_id}"

    @staticmethod
    def _ncit_iri_to_purl(value: str | None) -> str:
        """Convert common NCIT IRIs to the canonical OBO PURL form.

        BioPortal sometimes returns NCIT results without an ``obo_id``/CURIE,
        leaving only the NCIT-specific IRI. This helper ensures those cases are
        still normalized to the standard ``.../obo/NCIT_<id>`` PURL.
        """

        if not isinstance(value, str):
            return ""

        trimmed = value.strip()
        if not trimmed:
            return ""

        if trimmed.startswith(
                ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                 "https://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#")):
            local_id = trimmed.rsplit("#", maxsplit=1)[-1]
        elif trimmed.startswith(("http://purl.bioontology.org/ontology/NCIT/",
                                 "https://purl.bioontology.org/ontology/NCIT/")):
            local_id = trimmed.rstrip("/").rsplit("/", maxsplit=1)[-1]
        else:
            return ""

        if not local_id:
            return ""

        return f"http://purl.obolibrary.org/obo/NCIT_{local_id}"

    @staticmethod
    def _extract_synonyms(item: dict) -> list[str]:
        """Collect synonyms from common BioPortal fields."""
        candidates = item.get("synonym") or item.get("synonyms") or []
        if isinstance(candidates, str):
            return [candidates.strip()] if candidates.strip() else []
        if isinstance(candidates, list):
            return [str(s).strip() for s in candidates if str(s).strip()]
        return []
from pathlib import Path
from typing import Mapping, MutableMapping

from dotenv import dotenv_values


class ConfigError(RuntimeError):
    """Raised when configuration values cannot be loaded."""


class Config:
    """Access to configuration values stored in the project's .env file."""
    ENV_FILE = Path(__file__).resolve().parent / ".env"

    @classmethod
    def api_key(cls) -> str:
        """Return the BIOPORTAL_API_KEY from the .env file or environment."""
        env = cls._load_env(cls.ENV_FILE)
        return cls._get_api_key(env)

    @staticmethod
    def _load_env(env_path: Path) -> MutableMapping[str, str | None]:
        """Load key/value pairs from the .env file."""
        if not env_path.exists():
            raise ConfigError(
                "Missing .env file.\n"
                f"Expected in: {env_path.resolve()}\n"
                "Create a .env file with, for example:\n"
                "BIOPORTAL_API_KEY=your_bioportal_api_key"
            )

        env = dotenv_values(env_path)
        if not env:
            raise ConfigError(
                "The .env file was found but appears to be empty.\n"
                "Add a line like:\n"
                "BIOPORTAL_API_KEY=your_bioportal_api_key"
            )

        return env

    @staticmethod
    def _get_api_key(env: Mapping[str, str | None]) -> str:
        """Extract and validate the API key from the loaded environment mapping."""
        api_key = env.get("BIOPORTAL_API_KEY")

        if not api_key or not api_key.strip():
            raise ConfigError(
                "BIOPORTAL_API_KEY is missing or empty.\n"
                "Add a line like:\n"
                "BIOPORTAL_API_KEY=your_bioportal_api_key"
            )

        return api_key.strip()
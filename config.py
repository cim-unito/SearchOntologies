from pathlib import Path
from dotenv import dotenv_values


class Config:
    @classmethod
    def api_key(cls) -> str:
        """
        Returns BIOPORTAL_API_KEY by reading the .env file.
        """
        env = cls._load_env()
        return cls._get_api_key(env)

    @staticmethod
    def _load_env():
        """
        Upload the .env file.
        """
        env_path = Path.cwd() / ".env"

        if not env_path.exists():
            raise Exception(
                f"Missing .env file!\n"
                f"Expected in: {env_path.resolve()}\n"
                "Create a .env file with, for example:\n"
                "BIOPORTAL_API_KEY=your_bioportal_api_key"
            )

        return dotenv_values(env_path)

    @staticmethod
    def _get_api_key(env):
        api_key = env.get("BIOPORTAL_API_KEY")

        if not api_key or not api_key.strip():
            raise Exception(
                "BIOPORTAL_API_KEY is missing or empty in the .env file!\n"
                "Add a line like:\n"
                "BIOPORTAL_API_KEY=your_bioportal_api_key"
            )

        return api_key.strip()

import json
from pathlib import Path


class JsonFormatError(ValueError):
    """Raised when a JSON file does not match the expected schema."""


class JsonReader:
    @staticmethod
    def read_json(path: Path) -> object:
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise JsonFormatError(
                f"Invalid JSON content in {path}: {exc}") from exc
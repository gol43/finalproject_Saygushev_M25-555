import json
from pathlib import Path


class DatabaseManager:
    _instance = None
    BASE_DIR = Path(__file__).parent.parent.parent

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_json(self, filename: str):
        path = self.BASE_DIR / "data" / filename
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_json(self, filename: str, data) -> None:
        path = self.BASE_DIR / "data" / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

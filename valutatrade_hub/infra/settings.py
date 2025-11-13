import tomllib
from pathlib import Path
from typing import Any


class SettingsLoader:
    """Синглтон для работы с переменными из настроек"""
    _instance = None
    _config_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    _project_root = Path(__file__).parent.parent.parent

    # Используем __new__, потому что он проще и понятнее:
    # позволяет легко контролировать создание одного экземпляра класса без лишней магии.
    # Метакласс дал бы ту же функциональность,
    # но усложнил бы код и снизил читабельность без реальной пользы для проекта.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        if not self._config_path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {self._config_path}")

        with open(self._config_path, "rb") as f:
            toml_data = tomllib.load(f)

        self._config = toml_data.get("tool", {}).get("valutatrade", {})

        self._config.setdefault("data_path", "data")
        self._config.setdefault("rates_ttl_seconds", 300)
        self._config.setdefault("default_base_currency", "USD")

        self._config.setdefault("log_path", "logs/actions.log")
        self._config.setdefault("parser_log_path", "data/parser.log")

        self._config["data_path"] = self._project_root / self._config["data_path"]
        self._config["log_path"] = self._project_root / self._config["log_path"]
        self._config["parser_log_path"]=self._project_root / self._config["parser_log_path"]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)


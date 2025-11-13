import json
import os

from valutatrade_hub.logging_config import parser_logger

logger = parser_logger


class RatesStorage:
    """Сохранение курса валют в файл"""
    def __init__(self, rates_path, history_path):
        self.rates_path = str(rates_path)
        self.history_path = str(history_path)

    def _load(self, path, default):
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:     
                return default 

        try:
            return json.loads(content)
        except Exception:
            logger.warning(f"Файл {path} сломан, возвращаю пустой")
            return default

    def save_rates(self, rates, last_time):
        data = {
            "pairs": rates,
            "last_refresh": last_time
        }
        self._save(self.rates_path, data)

    def save_one_rate(self, rate_info):
        history = self._load(self.history_path, [])
        new_history = []
        for h in history:
            if h.get("id") != rate_info.get("id"):
                new_history.append(h)
        history = new_history
        history.append(rate_info)
        self._save(self.history_path, history)

    def _save(self, path, data):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if os.path.exists(path):
            os.remove(path)
        os.rename(tmp, path)

    def get_rates(self):
        return self._load(self.rates_path, {"pairs": {}, "last_refresh": "неизвестно"})
import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json(path_income):
    path = os.path.join(BASE_DIR, 'data', path_income)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(path_income, data):
    path = os.path.join(BASE_DIR, 'data', path_income)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_fresh(ts_str):
    ts = datetime.fromisoformat(ts_str)
    return datetime.now() - ts < timedelta(minutes=5)


def fetch_rate(from_code, to_code):
    # Заглушка на реальный ParserService, пока не понятно чё писать то.
    return None
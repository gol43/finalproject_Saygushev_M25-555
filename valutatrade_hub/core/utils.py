import os
from datetime import datetime, timedelta

from constants import DEFAULT_BASE_CURRENCY, RATES_FILE, RATES_TTL
from core.exceptions import ApiRequestError
from infra.database import DatabaseManager
from parser_service.config import ParserConfig
from parser_service.updater import RatesUpdater

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# нужно для правильной работы импортов

db = DatabaseManager()

def is_fresh(ts_str):
    """Проверка на актуальность курса валют"""
    # Тут я нашёл крупный Баг, при update-rates
    # у меня всегда выводилось неправильное время
    # Условно API выводило 2025-11-11T20:01:48
    # А по моим часам было 2025-11-11T22:01:48
    # То есть тут два часа разницы.
    # Из-за этого при get-rate всегда приходилось
    # выводить сообщение об неактуальности данных
    if not ts_str or ts_str == "неизвестно":
        return False
    try:
        ts_api = datetime.fromisoformat(ts_str)
        now_local = datetime.now()
        now_utc = now_local - timedelta(hours=2)
        return now_utc - ts_api < timedelta(seconds=RATES_TTL)
    except Exception as e:
        print(f"Ошибка парсинга времени: {e}")
        return False
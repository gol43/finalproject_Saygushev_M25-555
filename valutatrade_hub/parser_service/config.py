from constants import (
    DEFAULT_BASE_CURRENCY,
    EXCHANGE_RATE_FILE,
    EXCHANGERATE_API_KEY,
    RATES_FILE,
)

if not EXCHANGERATE_API_KEY:
    raise ValueError("EXCHANGERATE_API_KEY не найден в .env! Добавь: EXCHANGERATE_API_KEY=твой_ключ")


class ParserConfig:
    """Настройки для парсера"""
    def __init__(self):
        self.EXCHANGERATE_API_KEY = EXCHANGERATE_API_KEY
        self.COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
        self.EXCHANGERATE_API_URL = "https://v6.exchangerate-api.com/v6"
        self.BASE_CURRENCY = DEFAULT_BASE_CURRENCY
        self.FIAT_CURRENCIES = ("EUR", "GBP", "RUB")
        self.CRYPTO_CURRENCIES = ("BTC", "ETH", "SOL")
        self.CRYPTO_ID_MAP = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana"}
        self.RATES_FILE_PATH = RATES_FILE
        self.HISTORY_FILE_PATH = EXCHANGE_RATE_FILE
        self.REQUEST_TIMEOUT = 10

    def get_exchangerate_url(self) -> str:
        return f"{self.EXCHANGERATE_API_URL}/{self.EXCHANGERATE_API_KEY}/latest/{self.BASE_CURRENCY}"
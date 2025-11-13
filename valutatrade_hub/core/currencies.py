from core.exceptions import CurrencyNotFoundError
from core.models import CryptoCurrency, Currency, FiatCurrency

CURRENCY_REGISTRY = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "GBP": FiatCurrency("British Pound", "GBP", "United Kingdom"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),

    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 3.85e11),
    "SOL": CryptoCurrency("Solana", "SOL", "Proof-of-History", 7.5e10),
}

def get_currency(code: str) -> Currency:
    """Функция получения валюты"""
    if not isinstance(code, str):
        raise TypeError("code должен быть str.")
    normalized = code.strip().upper()
    if normalized not in CURRENCY_REGISTRY:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{normalized}'")
    return CURRENCY_REGISTRY[normalized]
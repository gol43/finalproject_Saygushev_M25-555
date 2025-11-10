from models import Currency, FiatCurrency, CryptoCurrency
from exceptions import CurrencyNotFoundError


CURRENCY_REGISTRY = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 3.85e11),
}


def get_currency(code: str) -> Currency:
    if not isinstance(code, str):
        raise TypeError("code должен быть str.")

    normalized = code.strip().upper()

    if normalized not in CURRENCY_REGISTRY:
        raise CurrencyNotFoundError(f"Валюта '{normalized}' не найдена в реестре.")

    return CURRENCY_REGISTRY[normalized]


print(get_currency('usd').get_display_info())
print(get_currency('btc').get_display_info())
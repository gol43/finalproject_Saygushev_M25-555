from abc import ABC, abstractmethod
from typing import Dict

import requests
from core.exceptions import ApiRequestError

from valutatrade_hub.logging_config import parser_logger

from .config import ParserConfig

logger = parser_logger


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass


class CoinGeckoClient(BaseApiClient):
    """API клиент для получения курса Крипты"""
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self) -> Dict[str, float]:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())
        params = {"ids": ids, "vs_currencies": self.config.BASE_CURRENCY.lower()}
        try:
            response = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as e:
            status = response.status_code
            print(f"ОШИБКА HTTP: {response.status_code}")
            if status == 429:
                msg = "CoinGecko: Слишком много запросов (429)"
            elif status == 401:
                msg = "CoinGecko: Проблема с доступом (401)"
            elif status == 403:
                msg = "CoinGecko: Запрещено (403)"
            else:
                text = response.text[:80].replace("\n", " ")
                msg = f"CoinGecko: Ошибка {status} — {text}"
            logger.error(msg)
            raise ApiRequestError(msg) from e
        except Exception as e:
            msg = f"CoinGecko: Что-то пошло не так: {e}"
            logger.error(msg)
            raise ApiRequestError(msg) from e
        rates = {}
        base = self.config.BASE_CURRENCY.lower()
        for code, cg_id in self.config.CRYPTO_ID_MAP.items():
            if cg_id in data and base in data[cg_id]:
                rates[f"{code}_{self.config.BASE_CURRENCY}"] = float(data[cg_id][base])
        return rates


class ExchangeRateApiClient(BaseApiClient):
    """API клиент для получения курса Фиата"""
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self) -> Dict[str, float]:
        url = self.config.get_exchangerate_url()

        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as e:
            status = response.status_code
            if status == 429:
                msg = "ExchangeRate-API: Лимит запросов (429)"
            elif status == 401:
                msg = "ExchangeRate-API: Неверный API-ключ (401)"
            elif status == 403:
                msg = "ExchangeRate-API: Доступ запрещён (403)"
            else:
                text = response.text[:80].replace("\n", " ")
                msg = f"ExchangeRate-API: Ошибка {status} — {text}"
            logger.error(msg)
            raise ApiRequestError(msg) from e
        except Exception as e:
            msg = f"ExchangeRate-API: Неизвестная ошибка: {e}"
            logger.error(msg)
            raise ApiRequestError(msg) from e
        rates = {}
        base_rates = data.get("conversion_rates", {})
        for code in self.config.FIAT_CURRENCIES:
            if code in base_rates:
                rate = 1.0 / float(base_rates[code])
                rates[f"{code}_{self.config.BASE_CURRENCY}"] = rate
        return rates
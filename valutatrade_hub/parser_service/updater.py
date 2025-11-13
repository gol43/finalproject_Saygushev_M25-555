from datetime import datetime

from valutatrade_hub.logging_config import parser_logger

from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage

logger = parser_logger


class RatesUpdater:
    """Обновление курса валют"""
    def __init__(self, config):
        self.config = config
        self.storage = RatesStorage(config.RATES_FILE_PATH, config.HISTORY_FILE_PATH)
        self.coingecko = CoinGeckoClient(config)
        self.exchangerate = ExchangeRateApiClient(config)

    def run_update(self, source=None):
        logger.info("Обновляю курсы...")
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        all_rates = {}
        if source:
            source = source.lower()
            if "coin" in source:
                clients = [("CoinGecko", self.coingecko)]
            elif "exchange" in source or "er" in source:
                clients = [("ExchangeRate-API", self.exchangerate)]
            else:
                print("Не знаю такой источник. Используй coingecko или exchangerate")
                return 0
        else:
            clients = [("CoinGecko", self.coingecko), ("ExchangeRate-API", self.exchangerate)]

        for name, client in clients:
            try:
                rates = client.fetch_rates()
                for pair, rate in rates.items():
                    from_c, to_c = pair.split("_")
                    rate_id = f"{from_c}_{to_c}_{now.replace(':', '').replace('-', '')}"
                    entry = {
                        "id": rate_id,
                        "from_currency": from_c,
                        "to_currency": to_c,
                        "rate": rate,
                        "timestamp": now,
                        "source": name
                    }
                    self.storage.save_one_rate(entry)
                    all_rates[pair] = {"rate": rate, "updated_at": now, "source": name}
                logger.info(f"{name}: получено {len(rates)} курсов")
            except Exception as e:
                logger.error(f"{name} упал: {e}")
        if all_rates:
            self.storage.save_rates(all_rates, now)
            logger.info(f"Сохранено {len(all_rates)} курсов")
        return len(all_rates)
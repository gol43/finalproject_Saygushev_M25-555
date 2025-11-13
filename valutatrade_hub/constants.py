import os

from dotenv import load_dotenv
from infra.settings import SettingsLoader

load_dotenv()
settings = SettingsLoader()

DEFAULT_BASE_CURRENCY = settings.get("default_base_currency")
USERS_FILE = settings.get("data_path") / "users.json"
PORTFOLIOS_FILE = settings.get("data_path") / "portfolios.json"
RATES_FILE = settings.get("data_path") / "rates.json"
EXCHANGE_RATE_FILE = settings.get("data_path") / "exchange_rates.json"
DEFAULT_BASE_CURRENCY = settings.get("default_base_currency")
RATES_TTL = settings.get("rates_ttl_seconds", 300)
SALT = "haleluya2003"
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
PARSER_LOG = "data/parser.log"
ACTIONS_LOG = "data/actions.log"
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
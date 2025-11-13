import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# нужно для правильной работы импортов

from constants import (
    DEFAULT_BASE_CURRENCY,
    PORTFOLIOS_FILE,
    RATES_FILE,
    SALT,
    USERS_FILE,
)
from core.currencies import get_currency
from core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from core.models import Portfolio, User, Wallet
from core.utils import is_fresh
from decorators import log_action
from infra.database import DatabaseManager
from parser_service.config import ParserConfig
from parser_service.updater import RatesUpdater

db = DatabaseManager()


def register(username: str, password: str):
    """Регистрация"""
    if not username:
        return "Ошибка: username не может быть пустым."
    if len(password) < 4:
        return "Ошибка: пароль должен быть длиной не менее 4 символов."
    
    user_data = db.load_json(USERS_FILE)
    if user_data:
        for i in user_data:
            if i['username'] == username:
                return f"Ошибка: пользователь '{username}' уже существует."
        
    user_id = len(user_data) + 1

    user_model = User(user_id=user_id, username=username, password=password, salt=SALT)
    
    user_model_data = {
        "user_id": user_model._user_id,
        "username": user_model._username,
        "hashed_password": user_model._hashed_password,
        "salt": user_model._salt,
        "registration_date": user_model._registration_date.isoformat()
    }
    user_data.append(user_model_data)
    
    
    portfolio_data = db.load_json(PORTFOLIOS_FILE)
    
    portfolio_model = Portfolio(user_id=user_id, wallets={})
    
    portfolio_model_data = {
        "user_id": portfolio_model._user_id,
        "wallets": {}
    }
    portfolio_data.append(portfolio_model_data)
    
    db.save_json(PORTFOLIOS_FILE, portfolio_data)
    db.save_json(USERS_FILE, user_data)
    
    msg = (f"Пользователь '{user_model._username}' зарегистрирован "
          f"(id={user_model._user_id}). "
          f"Войдите: login --username {user_model._username} --password ****")
    return msg


def login(username: str, password: str):
    """Авторизация"""
    user_data = db.load_json(USERS_FILE)

    user_data_json = None
    for user in user_data:
        if user["username"] == username:
            user_data_json = user
            break
    if not user_data_json:
        return None, f"Пользователь '{username}' не найден."
    else:
        try:
            user_model = User(user_id=user_data_json["user_id"],
                              username=username,
                              password=password,
                              salt=SALT)
        except ValueError as e:
            return None, str(e)
        if not user_model.verify_password(user_data_json["hashed_password"]):
                return None, "Неверный пароль"

        return user["user_id"], f"Вы вошли как '{username}'"


def show_portfolio(user_id: int, base_currency: str = None):
    """Показать портфель пользователя"""
    if base_currency is None:
        base_currency = DEFAULT_BASE_CURRENCY
        
    exchange_rates_json = db.load_json(RATES_FILE)
    try:
        exchange_rates_json = exchange_rates_json['pairs']
    except Exception as e:
        return f"Ошибка чтения курсов: {e}. Выполните 'update-rates'."
    base_key = f"{base_currency}_{DEFAULT_BASE_CURRENCY}"
    if base_key not in exchange_rates_json and base_currency != DEFAULT_BASE_CURRENCY:
        return f"Неизвестная базовая валюта '{base_currency}'"
    
    if base_currency == DEFAULT_BASE_CURRENCY:
        base_rate = 1.0
    else:
        base_rate = exchange_rates_json[base_key]["rate"]
    
    portfolio = db.load_json(PORTFOLIOS_FILE)
    
    for i in portfolio:
        if i["user_id"] == user_id:
            user_data: dict = i
            break
    
    user_id = user_data.get('user_id')
    wallets_map: dict = user_data.get('wallets', {})
    
    if wallets_map == {}:
        return "У вас пока нет валютных кошельков."
    wallets = {}
    
    for currency_code, info in wallets_map.items():
        balance_value = info.get('balance', 0.0)
        wallets[currency_code] = Wallet(currency_code=currency_code,
                                        balance=balance_value)
    user_portfolio = Portfolio(user_id=user_id, wallets=wallets)

    user_data = db.load_json(USERS_FILE)
    username = None
    for i in user_data:
        if i["user_id"] == user_id:
            username = i["username"]
            break
    
    if not username:
        return f'Пользователь с таким user_id: {user_id} не найден.'
    
    lines = [f"Портфель пользователя '{username}' (база: {base_currency}):"]
    total = 0.0
    for currency_code, wallet in user_portfolio.wallets.items():
        if currency_code == DEFAULT_BASE_CURRENCY:
            rate = 1.0
        else:
            rate_key = f"{currency_code}_{DEFAULT_BASE_CURRENCY}"
            if rate_key in exchange_rates_json:
                rate = exchange_rates_json[rate_key]["rate"]
            else:
                rate = 0.0
        converted = wallet.balance * rate / base_rate
        lines.append(f"- {currency_code}: {wallet.balance:.2f} "
                     f"→ {converted:.2f} {base_currency}")
        total += converted

    lines.append("-" * 35)
    lines.append(f"ИТОГО: {total:.2f} {base_currency}")
    return "\n".join(lines)
    
    
@log_action("BUY", verbose=True)
def buy(user_id: int, currency_code: str, amount: str):
    """Функция покупки валют"""
    exchange_rates_json = db.load_json(RATES_FILE)
    try:
        exchange_rates_json = exchange_rates_json['pairs']
    except Exception as e:
        return f"Ошибка чтения курсов: {e}. Выполните 'update-rates'."
    rate_key = f"{currency_code}_{DEFAULT_BASE_CURRENCY}"
    
    currency = get_currency(currency_code).get_display_info()
    if not currency:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{currency_code}")

    if currency_code == DEFAULT_BASE_CURRENCY:
        rate = 1.0
    else:
        if rate_key not in exchange_rates_json:
            return f"Не удалось получить курс '{currency_code}→{DEFAULT_BASE_CURRENCY}'"
        rate = exchange_rates_json[rate_key]["rate"]
    portfolios_json = db.load_json(PORTFOLIOS_FILE)
    
    for p in portfolios_json:
        if p["user_id"] == user_id:
            portfolio_data = p
            break

    wallets_map: dict = portfolio_data.get("wallets", {})
    if currency_code not in wallets_map:
        wallets_map[currency_code] = {"balance": 0.0}

    old_balance = wallets_map[currency_code]["balance"]
    wallet_obj = Wallet(currency_code, old_balance)
    wallet_obj.deposit(amount)

    new_balance = wallet_obj.balance
    wallets_map[currency_code]["balance"] = new_balance
    db.save_json(PORTFOLIOS_FILE, portfolios_json)
    cost_base_currency = amount * rate
    return (
        f"Покупка выполнена: {amount:.4f} {currency_code}"
        f"по курсу {rate:.2f} {DEFAULT_BASE_CURRENCY}/{currency_code}\n"
        f"- {currency_code}: было {old_balance:.4f} → стало {new_balance:.4f}\n"
        f"Стоимость покупки: {cost_base_currency:,.2f} {DEFAULT_BASE_CURRENCY}")


@log_action("SELL", verbose=True)
def sell(user_id: int, currency_code: str, amount: float):
    """Функция продажи валют"""
    exchange_rates = db.load_json(RATES_FILE)
    try:
        exchange_rates = exchange_rates['pairs']
    except Exception as e:
        return f"Ошибка чтения курсов: {e}. Выполните 'update-rates'."
    rate_key = f"{currency_code}_{DEFAULT_BASE_CURRENCY}"

    currency = get_currency(currency_code).get_display_info()
    if not currency:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{currency_code}")
        
    if currency_code == DEFAULT_BASE_CURRENCY:
        rate = 1.0
    else:
        if rate_key not in exchange_rates:
            return (f"Не удалось получить курс "
                    f"'{currency_code}→{DEFAULT_BASE_CURRENCY}'")
        rate = exchange_rates[rate_key]["rate"]

    portfolios_json = db.load_json(PORTFOLIOS_FILE)

    for rec in portfolios_json:
        if rec["user_id"] == user_id:
            portfolio_record = rec
            break

    wallets_map: dict = portfolio_record.get("wallets", {})
    if currency_code not in wallets_map:
        return (f"У вас нет кошелька '{currency_code}'. "
               f"Добавьте валюту: она создаётся автоматически при первой покупке.")
    wallets = {}
    for code, info in wallets_map.items():
        wallets[code] = Wallet(currency_code=code, balance=info.get("balance", 0.0))
    wallet = wallets[currency_code]
    old_balance = wallet.balance

    if amount > old_balance:
        raise InsufficientFundsError(
            f"Недостаточно средств: доступно {old_balance:.2f} {currency_code},"
            f"требуется {amount:.2f}")
        
    wallet.withdraw(amount)
    new_balance = wallet.balance
    portfolio_record["wallets"][currency_code]["balance"] = new_balance
    db.save_json(PORTFOLIOS_FILE, portfolios_json)
    profit_base_currency = amount * rate
    return (
        f"Продажа выполнена: {amount:.4f} {currency_code} "
        f"по курсу {rate:.2f} {DEFAULT_BASE_CURRENCY}/{currency_code}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_code}: было {old_balance:.2f} → стало {new_balance:.2f}\n"
        f"Оценочная выручка: {profit_base_currency:,.2f} {DEFAULT_BASE_CURRENCY}")


def get_rate(from_code: str, to_code: str):
    """Функция получения стоимости валюты относительно USD"""
    exchange_rates_json = db.load_json(RATES_FILE)
    try:
        exchange_rates = exchange_rates_json['pairs']
    except Exception as e:
        return f"Ошибка чтения курсов: {e}. Выполните 'update-rates'."
    key = f"{from_code}_{to_code}".upper()
    if key not in exchange_rates:
        raise CurrencyNotFoundError(f"Пара {key} не найдена")
    rate_data = exchange_rates[key]
    rate = rate_data['rate']

    last_refresh = exchange_rates_json.get("last_refresh", "неизвестно")
    is_fresh_flag = is_fresh(last_refresh)
    reverse = 1.0 / rate if rate else 0
    msg = (f"Курс {from_code}→{to_code}: {rate:.8f} (обновлено: {last_refresh})\n"
           f"Обратный: {reverse:.8f}")
    if not is_fresh_flag:
        msg += ("\n\nДанные устарели.\n"
                "Для точности выполните: update-rates")
    return msg


def update_rates(source: str = None) -> int:
    """Обновление курса валют"""
    config = ParserConfig()
    updater = RatesUpdater(config)
    count = updater.run_update(source)
    return count


def show_rates(currency: str = None, top_n: int = None) -> str:
    """Показать все курсы валют"""
    cache = db.load_json(RATES_FILE)
    if not isinstance(cache, dict) or "pairs" not in cache:
        return "Локальный кэш курсов пуст или повреждён. Выполните 'update-rates'."
    pairs = cache.get("pairs", {})
    last_refresh = cache.get("last_refresh", "N/A")
    if not pairs:
        return "Локальный кэш курсов пуст. Выполните 'update-rates'."
    filtered = {}
    if currency:
        currency = currency.upper()
        prefix = currency + "_"
        for pair_name, data in pairs.items():
            if pair_name.startswith(prefix):
                filtered[pair_name] = data
        if not filtered:
            return f"Курс для '{currency}' не найден в кеше."
    else:
        filtered = pairs

    if top_n:
        temp_list = []
        for name, info in filtered.items():
            rate = info.get("rate", 0.0)
            temp_list.append((rate, name, info))
        temp_list.sort(reverse=True)
        filtered = {}
        for i in range(min(top_n, len(temp_list))):
            rate, name, info = temp_list[i]
            filtered[name] = info

    if not filtered:
        return "Нет доступных курсов."
    lines = [f"Курсы (обновлено: {last_refresh}):"]
    for pair, data in filtered.items():
        lines.append(f"- {pair}: {data['rate']:.6f} ({data['source']})")
    return "\n".join(lines)
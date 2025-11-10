import sys
import os
from tabnanny import check
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import load_json, save_json, is_fresh, fetch_rate
from core.models import User, Portfolio, Wallet
from core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError

from infra.settings import SettingsLoader
from pathlib import Path


settings = SettingsLoader()
USERS_FILE = settings.get("data_path") / "users.json"
PORTFOLIOS_FILE = settings.get("data_path") / "portfolios.json"
RATES_FILE = settings.get("data_path") / "rates.json"

RATES_TTL = settings.get("rates_ttl_seconds")
DEFAULT_BASE_CURRENCY = settings.get("default_base_currency")
LOG_PATH = settings.get("log_path")

SALT = "haleluya2003"


def register(username: str, password: str):
    if not username:
        return "Ошибка: username не может быть пустым."
    if len(password) < 4:
        return "Ошибка: пароль должен быть длиной не менее 4 символов."
    
    user_data = load_json(USERS_FILE)
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
    
    
    portfolio_data = load_json(PORTFOLIOS_FILE)
    
    portfolio_model = Portfolio(user_id=user_id, wallets={})
    
    portfolio_model_data = {
        "user_id": portfolio_model._user_id,
        "wallets": {}
    }
    portfolio_data.append(portfolio_model_data)
    
    save_json(PORTFOLIOS_FILE, portfolio_data)
    save_json(USERS_FILE, user_data)
    
    msg = f"Пользователь '{user_model._username}' зарегистрирован (id={user_model._user_id}). Войдите: login --username {user_model._username} --password ****"
    return msg



def login(username: str, password: str):
    user_data = load_json(USERS_FILE)

    user_data_json = None
    for user in user_data:
        if user["username"] == username:
            user_data_json = user
            break
    if not user_data_json:
        return None, f"Пользователь '{username}' не найден."
    else:
        try:
            user_model = User(user_id=user_data_json["user_id"], username=username, password=password, salt=SALT)
        except ValueError as e:
            return None, str(e)
        if not user_model.verify_password(user_data_json["hashed_password"]):
                return None, "Неверный пароль"

        return user["user_id"], f"Вы вошли как '{username}'"



def show_portfolio(user_id: int, base_currency: str = "USD"):
    exchange_rates_json = load_json(RATES_FILE)
    base_key = f"{base_currency}_USD"
    if base_key not in exchange_rates_json and base_currency != "USD":
        return f"Неизвестная базовая валюта '{base_currency}'"

    base_rate = 1.0 if base_currency == "USD" else exchange_rates_json[base_key]["rate"]
    
    portfolio = load_json(PORTFOLIOS_FILE)
    
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
        wallets[currency_code] = Wallet(currency_code=currency_code, balance=balance_value)
    user_portfolio = Portfolio(user_id=user_id, wallets=wallets)

    user_data = load_json(USERS_FILE)
    for i in user_data:
        if i["user_id"] == user_id:
            username = i["username"]
        break
    
    lines = [f"Портфель пользователя '{username}' (база: {base_currency}):"]
    total = 0.0
    for currency_code, wallet in user_portfolio.wallets.items():
        rate = 1.0 if currency_code == "USD" else exchange_rates_json[f"{currency_code}_USD"]["rate"]
        converted = wallet.balance * rate / base_rate
        lines.append(f"- {currency_code}: {wallet.balance:.2f} → {converted:.2f} {base_currency}")
        total += converted

    lines.append("-" * 35)
    lines.append(f"ИТОГО: {total:.2f} {base_currency}")

    return "\n".join(lines)
    
    

def buy(user_id: int, currency_code: str, amount: str):
    exchange_rates_json = load_json(RATES_FILE)
    rate_key = f"{currency_code}_USD"

    if currency_code == "USD":
        rate = 1.0
    else:
        if rate_key not in exchange_rates_json:
            raise CurrencyNotFoundError(f"Не удалось получить курс '{currency_code}→USD'")
        rate = exchange_rates_json[rate_key]["rate"]
    
    portfolios_json = load_json(PORTFOLIOS_FILE)
    
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

    save_json(PORTFOLIOS_FILE, portfolios_json)

    cost_usd = amount * rate

    return (
        f"Покупка выполнена: {amount:.4f} {currency_code} по курсу {rate:.2f} USD/{currency_code}\n"
        f"- {currency_code}: было {old_balance:.4f} → стало {new_balance:.4f}\n"
        f"Стоимость покупки: {cost_usd:,.2f} USD"
    )


def sell(user_id: int, currency_code: str, amount: float):
    exchange_rates = load_json(RATES_FILE)
    rate_key = f"{currency_code}_USD"

    if currency_code == "USD":
        rate = 1.0
    else:
        if rate_key not in exchange_rates:
            raise CurrencyNotFoundError(f"Не удалось получить курс '{currency_code}→USD'")
        rate = exchange_rates[rate_key]["rate"]

    portfolios_json = load_json(PORTFOLIOS_FILE)

    for rec in portfolios_json:
        if rec["user_id"] == user_id:
            portfolio_record = rec
            break

    wallets_map: dict = portfolio_record.get("wallets", {})

    if currency_code not in wallets_map:
        return f"У вас нет кошелька '{currency_code}'. Добавьте валюту: она создаётся автоматически при первой покупке."

    wallets = {}
    for code, info in wallets_map.items():
        wallets[code] = Wallet(currency_code=code, balance=info.get("balance", 0.0))

    wallet = wallets[currency_code]

    old_balance = wallet.balance

    if amount > old_balance:
        raise InsufficientFundsError(
            f"Недостаточно средств: доступно {old_balance:.2f} {currency_code},"
            f"требуется {amount:.2f}"
        )
        
    wallet.withdraw(amount)

    new_balance = wallet.balance

    portfolio_record["wallets"][currency_code]["balance"] = new_balance
    save_json(PORTFOLIOS_FILE, portfolios_json)

    profit_usd = amount * rate

    return (
        f"Продажа выполнена: {amount:.4f} {currency_code} по курсу {rate:.2f} USD/{currency_code}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_code}: было {old_balance:.2f} → стало {new_balance:.2f}\n"
        f"Оценочная выручка: {profit_usd:,.2f} USD"
    )


def get_rate(from_code: str, to_code: str):
    exchange_rates = load_json(RATES_FILE)
    key = f"{from_code}_{to_code}"

    if key not in exchange_rates:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{from_code}' или '{to_code}'")

    rate_data = exchange_rates[key]
    if not is_fresh(rate_data['updated_at']):
        try:
            new_rate = fetch_rate(from_code, to_code)  # Заглушка для API
        except Exception as e:
            raise ApiRequestError(f"Ошибка при обращении к внешнему API: {e}")

    rate = rate_data['rate']
    reverse = 1.0 / rate

    return (
        f'Курс {from_code}->{to_code}: {rate} (обновлено: {rate_data["updated_at"]})\n'
        f'Обратный курс {to_code}->{from_code}: {reverse:.8f}'
    )
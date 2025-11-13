import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

from constants import DEFAULT_BASE_CURRENCY


class User:
    """Пользователь системы"""
    def __init__(self, user_id: int, username: str, password: str, salt: str):
        self._user_id = user_id
        self.username = username
        self.salt = salt
        self.password = password
        self._registration_date = datetime.now()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        v = value.strip()
        if not v:
            raise  ValueError("Имя пользователя не может быть пустым.")
        self._username = v

    @property
    def password(self):
        return self._hashed_password

    @password.setter
    def password(self, value):
        if len(value) < 4:
            raise  ValueError("Пароль должен быть не короче 4 символов.")
        self._hashed_password = self._hash(value)
        
    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, value):
        self._salt = value

    def _hash(self, p):
        return hashlib.sha256(f"{p}{self._salt}".encode()).hexdigest()

    def get_user_info(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def verify_password(self, password_from_json):
        return self._hashed_password == password_from_json

    def change_password(self, new_password):
        self.password = new_password


class Wallet:
    """Кошелёк пользователя для одной конкретной валюты"""
    def __init__(self, currency_code: str, balance: float):
        self.currency_code = currency_code
        self.balance = balance
    
    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, float):
            raise TypeError('Баланс должен быть числового типа float.')
        if value < 0:
            raise ValueError('Баланс не может быть отрицательным.')
        self._balance = float(value)
    
    def deposit(self, amount: float):
        if amount < 0:
            raise ValueError("Сумма пополнения (deposit) не может быть отрицательной.")
        self.balance = self.balance + amount
        
    def withdraw(self, amount: float):
        if amount > self.balance:
            return ('На балансе недостаточно средств.')
        self.balance = self.balance - amount
    
    def get_balance_info(self):
        return self.balance
    
    
class Portfolio:
    """Управление всеми кошельками одного пользователя"""
    def __init__(self, user_id: int, wallets: dict[str, Wallet] | None = None):
        self._user_id = user_id
        self._wallets: dict[str, Wallet] = wallets or {}

    @property
    def user(self):
        return self._user_id

    @property
    def wallets(self):
        return dict(self._wallets)

    def add_currency(self, currency_code: str, initial_balance: float = 0.0):
        """Добавляет новый кошелёк (если ещё нет)"""
        code = currency_code.upper()
        if code in self._wallets:
            raise ValueError(f"Кошелёк для {code} уже существует.")
        self._wallets[code] = Wallet(code, initial_balance)

    def get_wallet(self, currency_code: str):
        code = currency_code.upper()
        if code not in self._wallets:
            raise KeyError(f"Кошелёк для {code} не найден.")
        return self._wallets[code]

    def get_total_value(self, base_currency=DEFAULT_BASE_CURRENCY, exchange_rates=None):
        """Возвращает суммарную стоимость всех кошельков в базовой валюте"""
        if exchange_rates is None:
            exchange_rates = {
                'USD': 1.0,
                'BTC': 30000.0,
                'EUR': 1.1}
        base_rate = exchange_rates.get(base_currency.upper(), 1.0)
        total = 0.0
        for wallet in self._wallets.values():
            rate = exchange_rates.get(wallet.currency_code, 0)
            total += wallet.balance * rate / base_rate
        return total



class Currency(ABC):
    """Абстрактный класс валюты"""
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name должен быть str.")
        value = value.strip()
        if not value:
            raise ValueError("name не может быть пустым.")
        self._name = value

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("code должен быть str.")
        value = value.strip().upper()
        if not (2 <= len(value) <= 5) or " " in value:
            raise ValueError("code должен быть 2–5 символов, "
                             "верхний регистр, без пробелов.")
        self._code = value

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    """Фиатная валюта"""
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    @property
    def issuing_country(self) -> str:
        return self._issuing_country

    @issuing_country.setter
    def issuing_country(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("issuing_country должен быть str.")
        value = value.strip()
        if not value:
            raise ValueError("issuing_country не может быть пустым.")
        self._issuing_country = value

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    """Криптовалюта"""
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("algorithm должен быть str.")
        value = value.strip()
        if not value:
            raise ValueError("algorithm не может быть пустым.")
        self._algorithm = value

    @property
    def market_cap(self) -> float:
        return self._market_cap

    @market_cap.setter
    def market_cap(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("market_cap должен быть числом.")
        if value < 0:
            raise ValueError("market_cap должен быть ≥ 0.")
        self._market_cap = float(value)

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})")
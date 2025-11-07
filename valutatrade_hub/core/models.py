import hashlib
from datetime import datetime


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
            raise ValueError("Имя пользователя не может быть пустым.")
        self._username = v

    @property
    def password(self):
        return self._hashed_password

    @password.setter
    def password(self, value):
        if len(value) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
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

    def verify_password(self, password):
        return self._hashed_password == self._hash(password)

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
    def __init__(self, user_id: int):
        self._user_id = user_id
        self._wallets: dict[str, Wallet] = {}

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

    def get_total_value(self, base_currency='USD', exchange_rates=None):
        """Возвращает суммарную стоимость всех кошельков в базовой валюте"""
        if exchange_rates is None:
            exchange_rates = {
                'USD': 1.0,
                'BTC': 30000.0,
                'EUR': 1.1
            }
        base_rate = exchange_rates.get(base_currency.upper(), 1.0)
        total = 0.0
        for wallet in self._wallets.values():
            rate = exchange_rates.get(wallet.currency_code, 0)
            total += wallet.balance * rate / base_rate
        return total
# D:\cod\Dev\Dev-v1\yo-yo\finalproject_Saygushev_M25-555\valutatrade_hub\core\exceptions.py
class CurrencyNotFoundError(Exception):
    """Ошибка: валюта не найдена в реестре."""
    pass

class InsufficientFundsError(Exception):
    """Ошибка: недостаточно средств для операции."""
    pass


class ApiRequestError(Exception):
    """Ошибка: ошибка при обращении к внешнему API."""
    pass
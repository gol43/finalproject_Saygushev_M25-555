class CurrencyNotFoundError(Exception):
    """Ошибка: валюта не найдена в реестре."""
    pass

class InsufficientFundsError(Exception):
    """Ошибка: недостаточно средств для операции."""
    pass


class ApiRequestError(Exception):
    """Ошибка: ошибка при обращении к внешнему API."""
    pass
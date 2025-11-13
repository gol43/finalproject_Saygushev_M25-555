import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# нужно для правильной работы импортов
from core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from core.usecases import (
    buy,
    get_rate,
    login,
    register,
    sell,
    show_portfolio,
    show_rates,
    update_rates,
)
from parser_service.scheduler import RatesScheduler

from valutatrade_hub.constants import DEFAULT_BASE_CURRENCY


def process_command(command: str, current_user_id: int | None):
    """Основная функция по обработке комманд из терминала"""
    command = command.strip()
    if not command:
        return True, current_user_id

    if command.startswith('register'):
        parts = command.split()
        args = {}
        i = 1
        while i < len(parts):
            if parts[i] == "--username" and i + 1 < len(parts):
                args["username"] = parts[i + 1]
                i += 2
            elif parts[i] == "--password" and i + 1 < len(parts):
                args["password"] = parts[i + 1]
                i += 2
            else:
                print("Ошибка: неверный формат команды. "
                      "Используйте --username NAME --password PASS")
                return True, current_user_id

        if "username" not in args or "password" not in args:
            print("Использование: register --username NAME --password PASS")
            return True, current_user_id

        msg = register(args["username"], args["password"])
        print(msg)
        return True, current_user_id

    elif command.startswith('login'):
        parts = command.split()
        args = {}
        i = 1
        while i < len(parts):
            if parts[i] == "--username" and i + 1 < len(parts):
                args["username"] = parts[i + 1]
                i += 2
            elif parts[i] == "--password" and i + 1 < len(parts):
                args["password"] = parts[i + 1]
                i += 2
            else:
                print("Ошибка: неверный формат команды. "
                      "Используйте --username NAME --password PASS")
                return True, current_user_id

        if "username" not in args or "password" not in args:
            print("Использование: login --username NAME --password PASS")
            return True, current_user_id

        user_id, msg = login(args["username"], args["password"])
        print(msg)
        return True, user_id

    elif command.startswith('show-portfolio'):
        if not check_auth(current_user_id):
            return True, current_user_id
        
        parts = command.split()
        base = DEFAULT_BASE_CURRENCY

        for i in range(1, len(parts)):
            if parts[i].startswith("--base"):
                base = parts[i+1]
        base = base.upper()
        msg = show_portfolio(current_user_id, base)
        print(msg)
        return True, current_user_id

    elif command.startswith('buy'):
        if not check_auth(current_user_id):
            return True, current_user_id
        parts = command.split()
        args = {}
        for i in range(1, len(parts)):
            if parts[i].startswith("--currency"):
                args["currency"] = parts[i+1].upper()
            if parts[i].startswith("--amount"):
                args["amount"] = float(parts[i+1])
        
        if "currency" not in args or "amount" not in args:
            print("Использование: buy --currency CODE --amount VALUE")
            return True, current_user_id
        if args["amount"] < 0:
            print("'amount' должен быть положительным числом")
            return True, current_user_id
        try:
            msg = buy(current_user_id, args["currency"], args["amount"])
        except CurrencyNotFoundError as e:
            msg = f"{e}\nСправка: используйте help."
        except Exception as e:
            msg = str(e)
        print(msg)
        return True, current_user_id
        
    elif command.startswith('sell'):
        if not check_auth(current_user_id):
            return True, current_user_id
        parts = command.split()
        args = {}
        for i in range(1, len(parts)):
            if parts[i].startswith("--currency"):
                args["currency"] = parts[i+1].upper()
            if parts[i].startswith("--amount"):
                args["amount"] = float(parts[i+1])

        if "currency" not in args or "amount" not in args:
            print("Использование: sell --currency CODE --amount VALUE")
            return True, current_user_id
        if args["amount"] < 0:
            print("'amount' должен быть положительным числом")
            return True, current_user_id
        try:
            msg = sell(current_user_id, args["currency"], args["amount"])
        except InsufficientFundsError as e:
            msg = str(e)
        except CurrencyNotFoundError as e:
            msg = f"{e}\nСправка: используйте help."
        except Exception as e:
            msg = str(e)
        print(msg)
        return True, current_user_id
        
    elif command.startswith('get-rate'):
        parts = command.split()
        args = {}
        for i in range(1, len(parts)):
            if parts[i].startswith("--from"):
                args["from"] = parts[i+1].upper()
            if parts[i].startswith("--to"):
                args["to"] = parts[i+1].upper()
        if "from" not in args or "to" not in args:
            print("Использование: get-rate --from CODE --to CODE")
            return True, current_user_id
        try:
            msg = get_rate(args["from"], args["to"])
        except CurrencyNotFoundError as e:
            msg = f"{e}\nСправка: используйте help."
        except ApiRequestError as e:
            msg = f"{e}\nПопробуйте позже или проверьте соединение с сетью."
        except Exception as e:
            msg = e
        print(msg)
        return True, current_user_id

    elif command.startswith('update-rates'):
        try:
            parts = command.split()
            source = None
            if len(parts) > 2 and parts[1] == "--source":
                raw = parts[2].lower()
                if raw in ["coingecko", "cg"]:
                    source = "CoinGecko"
                elif raw in ["exchangerate", "er", "exchange"]:
                    source = "ExchangeRate-API"
                else:
                    print("Ошибка: --source должен быть coingecko или exchangerate")
                    return True, current_user_id
            update_rates(source)
            print("Курсы успешно обновлены.")
        except Exception as e:
            print(f"Ошибка при обновлении: {e}")
        return True, current_user_id


    elif command.startswith('show-rates'):
        try:
            parts = command.split()
            currency = None
            top_n = None
            i = 1
            while i < len(parts):
                if parts[i] == "--currency" and i + 1 < len(parts):
                    currency = parts[i + 1]
                    i += 2
                elif parts[i] == "--top" and i + 1 < len(parts):
                    try:
                        top_n = int(parts[i + 1])
                        i += 2
                    except ValueError:
                        print("Ошибка: --top должен быть числом")
                        return True, current_user_id
                else:
                    i += 1
            result = show_rates(currency=currency, top_n=top_n)
            print(result)
        except Exception as e:
            print(f"Ошибка: {e}")
        return True, current_user_id
    
    elif command.startswith('help'):
        print(show_help())
        return True, current_user_id
    elif command in ('quit', 'exit'):
        return False, current_user_id
    else:
        print('Неизвестная команда. Введите help для списка команд.')
        return True, current_user_id
    

def show_help():
    """Вывод всех команд"""
    return ('у нас есть следующие команды:\n'
            '1. зарегистрироваться (register);\n'
            '2. войти в систему (login);\n'
            '3. посмотреть свой портфель и балансы (show-portfolio);\n'
            '4. купить валюту (buy);\n'
            '5. продать валюту (sell);\n'
            '6. получить курс валюты (get-rate);\n'
            '7. обновить курс валют (update-rates);\n'
            '8. показать весь курс валют (show-rates).')


def get_input(prompt="> "):
    """Функция, которая принимает введённое сообщения пользователя"""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из сервиса")
        return "quit"


def check_auth(current_user_id):
    """Проверка аутентификации пользователя"""
    if current_user_id is None:
        print("Ошибка: вы не вошли в систему. Используйте login.")
        return False
    return True


def run_cli():
    """Функция запуска обработки комманд из терминала"""
    print('Добро пожаловать!')
    scheduler = RatesScheduler()
    scheduler.start()
    current_user_id = None
    work = True
    while work:
        command = get_input("> ")
        work, current_user_id = process_command(command, current_user_id)
        scheduler.run_once()
        time.sleep(0.1)
    scheduler.stop()
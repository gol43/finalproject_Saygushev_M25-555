import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from core.usecases import buy, get_rate, login, register, sell, show_portfolio


def process_command(command: str, current_user_id: int | None):
    command = command.strip()
    if not command:
        return True, current_user_id

    if command.startswith('register'):
        parts = command.split()
        args = {}

        for i in range(1, len(parts)):
            if parts[i].startswith("--username"):
                args["username"] = parts[i+1]
            if parts[i].startswith("--password"):
                args["password"] = parts[i+1]

        if "username" not in args or "password" not in args:
            print("Использование: register --username NAME --password PASS")
            return True, current_user_id

        msg = register(args["username"], args["password"])
        print(msg)
        return True, current_user_id
    
    elif command.startswith('login'):
        parts = command.split()
        args = {}
        
        for i in range(1, len(parts)):
            if parts[i].startswith("--username"):
                args["username"] = parts[i+1]
            if parts[i].startswith("--password"):
                args["password"] = parts[i+1]
        
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
        base = "USD"

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
            msg = str(e)

        print(msg)
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
    return ('у нас есть следующие команды:\n'
            '1. зарегистрироваться (register);\n'
            '2. войти в систему (login);\n'
            '3. посмотреть свой портфель и балансы (show-portfolio);\n'
            '4. купить валюту (buy);\n'
            '5. продать валюту (sell);\n'
            '6. получить курс валюты (get-rate).')


def get_input(prompt="> "):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из сервиса")
        return "quit"


def check_auth(current_user_id):
    if current_user_id is None:
        print("Ошибка: вы не вошли в систему. Используйте login.")
        return False
    return True


def run_cli():
    print('Добро пожаловать в наш сервис!')
    current_user_id = None
    work = True
    while work:
        command = get_input("> ")
        work, current_user_id = process_command(command, current_user_id)

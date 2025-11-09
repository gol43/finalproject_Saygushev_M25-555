import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.usecases import register


def process_command(command: str):
    command = command.strip()
    if not command:
        return True

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
            return True

        msg = register(args["username"], args["password"])
        print(msg)
        return True
    
    elif command == 'login':
        pass
    elif command == 'show-portfolio':
        pass
    elif command == 'buy':
        pass
    elif command == 'sell':
        pass
    elif command == 'get-rate':
        pass
    elif command == 'help':
        print(show_help())
    elif command in ('quit', 'exit'):
        return False
    else:
        print('Неизвестная команда. Введите help для списка команд.')

    return True


def show_help():
    return (f'у нас есть следующие команды:\n'
            f'1. зарегистрироваться (register);\n'
            f'2. войти в систему (login);\n'
            f'3. посмотреть свой портфель и балансы (show-portfolio);\n'
            f'4. купить валюту (buy);\n'
            f'5. продать валюту (sell);\n'
            f'6. получить курс валюты (get-rate).')


def get_input(prompt="> "):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из сервиса")
        return "quit"

    
def run_cli():
    print('Добро пожаловать в наш сервис!')
    work = True
    while work:
        command = get_input("> ")
        work = process_command(command)

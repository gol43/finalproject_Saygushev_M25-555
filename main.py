import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from valutatrade_hub.cli.interface import run_cli

def main():
    run_cli()  # просто запускаем CLI, ничего не возвращаем

if __name__ == "__main__":
    main()

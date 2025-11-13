import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# нужно для правильной работы импортов

from valutatrade_hub.cli.interface import run_cli


def main():
    """Гланва точка входа"""
    run_cli()

if __name__ == "__main__":
    main()
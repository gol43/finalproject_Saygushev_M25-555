import logging

from constants import ACTIONS_LOG, DATE_FORMAT, LOG_FORMAT, PARSER_LOG

parser_logger = logging.getLogger("parser")
parser_logger.setLevel(logging.INFO)
parser_logger.handlers.clear()

console = logging.StreamHandler()
console.setFormatter(logging.Formatter("INFO: %(message)s"))
parser_logger.addHandler(console)

parser_file = logging.FileHandler(PARSER_LOG, encoding="utf-8")
parser_file.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT[:-3]))
parser_logger.addHandler(parser_file)

actions_logger = logging.getLogger("actions")
actions_logger.setLevel(logging.INFO)
actions_logger.handlers.clear()

actions_file = logging.FileHandler(ACTIONS_LOG, encoding="utf-8")
actions_file.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT[:-3]))
actions_logger.addHandler(actions_file)
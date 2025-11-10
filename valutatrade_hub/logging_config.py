import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from infra.settings import SettingsLoader

settings = SettingsLoader()
log_file = settings.get("data_path") / "actions.log"
log_file.parent.mkdir(exist_ok=True)

handler = RotatingFileHandler(log_file, encoding="utf-8")

formatter = logging.Formatter(
    "%(levelname)s %(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
handler.setFormatter(formatter)

logger = logging.getLogger("actions")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

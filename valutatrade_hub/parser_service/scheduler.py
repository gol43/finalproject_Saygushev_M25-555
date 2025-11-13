import logging

import schedule

from .config import ParserConfig
from .updater import RatesUpdater

logger = logging.getLogger("parser.scheduler")


class RatesScheduler:
    """Автоматическое обновление курса валют"""
    def __init__(self):
        self.config = ParserConfig()
        self.updater = RatesUpdater(self.config)
        self.running = False

    def _job(self):
        try:
            logger.info("Запуск ежедневного обновления курсов...")
            self.updater.run_update()
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")

    def start(self):
        if not self.running:
            self.running = True
            schedule.every().day.at("11:36").do(self._job)
            # обновы работают следующим образом:
            # ждёте назначенного времени или ставите сами, а потом в CLI нажмите Enter и всё обновится)))

    def stop(self):
        if self.running:
            self.running = False
            schedule.clear()

    def run_once(self):
        if self.running:
            schedule.run_pending()
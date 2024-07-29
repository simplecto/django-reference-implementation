import logging
import time
import traceback
import signal
from django.core.management import BaseCommand
from django.db import transaction

from myapp.models import WorkerConfiguration, WorkerError


LOG_LEVELS = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}


def get_log_level_name(log_level_number):
    return LOG_LEVELS.get(log_level_number, "UNKNOWN")


class BaseWorkerCommand(BaseCommand):
    """Process embeddings with OpenAI"""

    abstract = True

    help = "UPDATE ME"

    NAME = "UPDATE ME"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.help == "UPDATE ME":
            raise NotImplementedError("Please update the help string.")

        if self.NAME == "UPDATE ME":
            raise NotImplementedError("Please update the NAME string.")

        self.config, created = WorkerConfiguration.objects.get_or_create(
            name=self.NAME
        )

        if created:
            logging.critical("WorkerConfiguration created: %s", self.NAME)

        self.current_log_level = self.logger.getEffectiveLevel()
        self.keep_running = True

    def _update_log_level(self):
        """Update the log level if it has changed."""
        self.current_log_level = self.logger.getEffectiveLevel()

        if self.current_log_level != self.config.log_level:
            self.logger.setLevel(self.config.log_level)
            self.logger.critical(
                "Log level changed: %s -> %s",
                get_log_level_name(self.current_log_level),
                get_log_level_name(self.config.log_level),
            )

    def _log_crawl_error(self, the_exception=None):
        """Log a crawl error."""
        self.logger.error("Crawl Error: %s", the_exception)
        error = f"{str(the_exception)}\n\n{traceback.format_exc()}"

        WorkerError.objects.create(
            error=error,
            worker=self.config,
        )

    @property
    def logger(self):
        return logging.getLogger(f"{self.__class__.__name__}.{self.NAME}")

    def run(self):
        """Run the worker."""
        raise NotImplementedError("Please implement the run method.")

    def signal_handler(self, the_signal, frame):
        self.logger.critical("Received %d. Stopping the worker.", the_signal)
        self.keep_running = False

    def handle(self, *args, **options):
        self.logger.info("Starting worker...")

        # Set up the signal handler to handle SIGINT and SIGTERM
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        while self.keep_running:
            self.config.refresh_from_db()
            self._update_log_level()

            if self.config.is_enabled:
                with transaction.atomic():
                    self.run()
            else:
                self.logger.debug("Job is disabled.")

            self.logger.debug(
                "Sleeping for %d seconds.",
                self.config.sleep_seconds,
            )
            time.sleep(self.config.sleep_seconds)

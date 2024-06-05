"""Sample async worker that runs a job every N seconds."""

import time
import logging

from django.core.management import BaseCommand
import myapp.models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Simple Async Worker."""

    help = "Simple Async Worker"

    def __init__(self):
        super().__init__()
        self.config = myapp.models.SiteConfiguration.get_solo()

    def handle(self, *args, **options):

        logger.info("Starting job...")

        while True:
            self.config.refresh_from_db()

            if self.config.worker_enabled:
                logger.info("Running the job.")
            else:
                logger.info("Job is disabled.")

            logger.info("Sleeping for %d seconds.", self.config.worker_sleep_seconds)
            time.sleep(self.config.worker_sleep_seconds)

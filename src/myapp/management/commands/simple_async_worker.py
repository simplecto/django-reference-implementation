from django.core.management import BaseCommand
from myapp.models import SiteConfiguration
import time

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Simple Async Worker"

    def __init__(self):
        super().__init__()
        self.config = SiteConfiguration.get_solo()

    def handle(self, *args, **options):

        logger.info("Starting job...")

        while True:
            self.config.refresh_from_db()

            if self.config.worker_enabled:
                logger.info(f"Running the job.")
            else:
                logger.info(f"Job is disabled.")

            logger.info(f"Sleeping for {self.config.worker_sleep_seconds} seconds.")
            time.sleep(self.config.worker_sleep_seconds)

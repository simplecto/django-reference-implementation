"""Show how to raise an unhandled exception to show up in Sentry"""

import logging
import django.core.management.base


logger = logging.getLogger(__name__)


class Command(django.core.management.base.BaseCommand):
    """Raise an unhandled exception to show up in Sentry"""

    help = "Raise an unhandled exception to show up in sentry"

    def handle(self, *args, **options):

        # pylint: disable=no-member
        self.stdout.write(
            self.style.SUCCESS("Raising unhandled exception for Sentry...")
        )
        raise django.core.management.base.CommandError("Check for this in Sentry...")

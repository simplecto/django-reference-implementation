"""Show how to raise an unhandled exception to show up in Sentry."""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Raise an unhandled exception to show up in Sentry."""

    help = "Raise an unhandled exception to show up in sentry"

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        """Handle the command."""
        # pylint: disable=no-member
        self.stdout.write(
            self.style.SUCCESS("Raising unhandled exception for Sentry...")
        )
        error_msg = "Check for this in Sentry..."
        raise CommandError(error_msg)

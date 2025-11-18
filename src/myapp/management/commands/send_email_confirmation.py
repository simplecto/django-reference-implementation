from django.core.mail import send_mail

from myapp.management.commands._base import BaseWorkerCommand


class Command(BaseWorkerCommand):
    """Simple Async Worker."""

    help = "Send organization invite email"
    NAME = "send_email_invite"

    def run(self) -> None:
        """Run the worker."""
        self.logger.debug("I'm here, running things...")

        send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )

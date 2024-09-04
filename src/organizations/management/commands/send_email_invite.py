from django.contrib.sites.models import Site
from django.core.mail import send_mail

from myapp.management.commands._base import BaseWorkerCommand
from organizations.models import Invitation


class Command(BaseWorkerCommand):
    """Simple Async Worker."""

    help = "Send email confirmation"
    NAME = "send_email_confirmation"

    def run(self) -> None:
        """Run the worker."""
        self.logger.debug("I'm here, running things...")
        site = Site.objects.get_current()

        for invite in Invitation.objects.filter(email_sent=False).all():
            msg = f"Sending email to {invite.email}"
            self.logger.debug(msg)

            text = f"""Join the org: {invite.organization.name}

Click here to confirm your email: http://{site}/organizations/accept-invite/{invite.invite_key}/

The Firm.
"""
            send_mail(
                "You've been invited to join the firm",
                text,
                "no-reply@agentsasylum.com",
                [invite.email],
                fail_silently=False,
            )

            invite.email_sent = True
            invite.save()

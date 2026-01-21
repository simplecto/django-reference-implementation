"""Service objects for the organizations app."""

from hashlib import sha256

from organizations.models import Invitation, InvitationLog


def invite_log(invite: Invitation, message: str) -> None:
    """Log an invitation.

    Args:
    ----
        invite: The invitation object.
        message: The message to log.

    Returns:
    -------
        None

    """
    InvitationLog.objects.create(
        email_hash=sha256(invite.email.encode()).hexdigest(),
        organization=invite.organization,
        message=message,
    )

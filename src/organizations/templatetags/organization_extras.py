from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

from organizations.models import Organization, OrganizationMember

if TYPE_CHECKING:
    from django.contrib.auth.models import User

register = template.Library()


@register.filter
def get_user_role(organization: Organization, user: User) -> str | None:
    """Get the role of a user in an organization.

    Args:
    ----
        organization: Organization object.
        user: User object.

    Returns:
    -------
        str: The role of the user in the organization.

    """
    try:
        org_member = OrganizationMember.objects.get(
            organization=organization, user=user
        )
    except OrganizationMember.DoesNotExist:
        return None

    return org_member.role

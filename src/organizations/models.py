"""Models for the organizations app."""

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Organization(models.Model):
    """An organization model."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for the organization model."""

        ordering = ["name"]  # noqa: RUF012
        verbose_name = "organization"
        verbose_name_plural = "organizations"

    def __str__(self) -> str:
        """Return the name of the organization."""
        return self.name

    def save(self, *args, **kwargs) -> None:  # noqa: ANN003, ANN002
        """Override save method to auto-generate slug.

        Args:
        ----
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
        -------
            None

        """
        if not self.slug:
            self.slug = slugify(self.name).lower()
        super().save(*args, **kwargs)

    def has_admin_permission(self, user: User) -> bool:
        """Return True if the user is an owner of the organization.

        Args:
        ----
            user: User object.

        Returns:
        -------
            bool

        """
        return self.members.filter(
            user=user, role=OrganizationMember.RoleChoices.OWNER
        ).exists()

    def is_owner(self, user: User) -> bool:
        """Return True if the user is an owner of the organization.

        Args:
        ----
            user: User object.

        Returns:
        -------
            bool

        """
        return self.members.filter(
            user=user, role=OrganizationMember.RoleChoices.OWNER
        ).exists()

    @property
    def owners(self) -> models.QuerySet:
        """Return the owners of the organization."""
        return self.members.filter(role=OrganizationMember.RoleChoices.OWNER)

    @property
    def admins(self) -> models.QuerySet:
        """Return the admins of the organization."""
        return self.members.filter(role=OrganizationMember.RoleChoices.ADMIN)

    @property
    def members(self) -> models.QuerySet:
        """Return the members of the organization."""
        return self.members.filter(role=OrganizationMember.RoleChoices.MEMBER)


class OrganizationMember(models.Model):
    """An organization member model."""

    # choices for the role field
    class RoleChoices(models.TextChoices):
        """Role choices for the organization member model."""

        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    class StatusChoices(models.TextChoices):
        """Status choices for the organization member model."""

        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        INVITED = "INVITED", "Invited"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organizations"
    )
    role = models.CharField(
        max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER
    )
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE
    )

    class Meta:
        """Meta options for the organization member model."""

        unique_together = ["organization", "user"]  # noqa: RUF012
        verbose_name = "organization member"
        verbose_name_plural = "organization members"

    def __str__(self) -> str:
        """Return the name of the organization member."""
        return f"{self.user} - {self.organization}"

    @property
    def can_admin(self) -> bool:
        """Return True if the user can admin the organization."""
        return self.role in (self.RoleChoices.OWNER, self.RoleChoices.ADMIN)

    @property
    def is_owner(self) -> bool:
        """Return True if the user is an owner of the organization."""
        return self.role == self.RoleChoices.OWNER


class Invitation(models.Model):
    """An invitation model."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="invitations"
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="invitations_sent",
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations_received",
        null=True,
        blank=True,
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.RoleChoices.choices,
        default=OrganizationMember.RoleChoices.MEMBER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    invite_key = models.UUIDField(unique=True)

    class Meta:
        """Meta options for the invitation model."""

        verbose_name = "invitation"
        verbose_name_plural = "invitations"

    def __str__(self) -> str:
        """Return the email of the invitation."""
        return self.email

    def save(self, *args, **kwargs) -> None:  # noqa: ANN003, ANN002
        """Override save method to auto-generate invite key.

        Args:
        ----
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
        -------
            None

        """
        if not self.invite_key:
            self.invite_key = str(uuid.uuid4())

        # if user email matches the email of the user, set the user field
        if self.user is None:
            self.user = User.objects.filter(email=self.email).first()

        super().save(*args, **kwargs)

    @property
    def user_exists(self) -> bool:
        """Return True if the user exists."""
        return self.user is not None

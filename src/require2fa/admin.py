"""Admin interface for Two-Factor Authentication configuration."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import TwoFactorConfig


@admin.register(TwoFactorConfig)
class TwoFactorConfigAdmin(SingletonModelAdmin):
    """Admin interface for TwoFactorConfig."""

    fieldsets = (
        (
            "Two-Factor Authentication Settings",
            {
                "fields": ("required",),
                "description": "Configure site-wide 2FA enforcement policies.",
            },
        ),
    )

    def has_delete_permission(self, request, obj=None) -> bool:  # noqa: ANN001, ARG002
        """Prevent deletion of the singleton configuration."""
        return False

"""Two-Factor Authentication configuration models."""

import solo.models
from django.db import models


class TwoFactorConfig(solo.models.SingletonModel):
    """Configuration for Two-Factor Authentication enforcement."""

    required = models.BooleanField(
        default=False,
        help_text="Require 2FA for all authenticated users.",
        verbose_name="Require Two-Factor Authentication",
    )

    class Meta:
        """Model metadata for TwoFactorConfig."""

        verbose_name = "Two-Factor Authentication Configuration"

    def __str__(self) -> str:
        """Return a string representation of the configuration."""
        return f"2FA Required: {'Yes' if self.required else 'No'}"

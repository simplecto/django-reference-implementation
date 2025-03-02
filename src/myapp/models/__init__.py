"""Module for models."""

import solo.models
from django.db import models

from .worker_configurations import WorkerConfiguration
from .worker_errors import WorkerError

FIVE_SECONDS = 5


class SiteConfiguration(solo.models.SingletonModel):
    """Store the configuration of the site."""

    worker_enabled = models.BooleanField(default=False)
    worker_sleep_seconds = models.IntegerField(default=FIVE_SECONDS)

    required_2fa = models.BooleanField(default=False, help_text="Require 2FA for all users.")

    js_head = models.TextField(
        blank=True,
        default="",
        help_text="Javascript to be included in the head tag. You should include the script tags.",
    )
    js_body = models.TextField(
        blank=True,
        default="",
        help_text="Javascript to be included before the closing body tag. You should include the script tags.",
    )

    def __str__(self) -> str:
        """Return the model name."""
        return "Site Configuration"


__all__ = ["SiteConfiguration", "WorkerConfiguration", "WorkerError"]

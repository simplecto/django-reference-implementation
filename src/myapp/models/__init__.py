"""Module for models."""

import solo.models
from django.db import models


class SiteConfiguration(solo.models.SingletonModel):
    """Store the configuration of the site."""

    include_staff_in_analytics = models.BooleanField(
        default=False,
        help_text="Include staff in analytics.",
    )

    js_analytics = models.TextField(
        blank=True,
        default="",
        help_text="Javascript to be included before the closing body tag. You should include the script tags.",
    )

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


__all__ = ["SiteConfiguration"]

import solo.models
from django.db import models


FIVE_SECONDS = 5


class SiteConfiguration(solo.models.SingletonModel):
    """
    Site Configuration model. This model is used to store the configuration
    of the site.
    """

    worker_enabled = models.BooleanField(default=False)
    worker_sleep_seconds = models.IntegerField(default=FIVE_SECONDS)

    js_head = models.TextField(
        blank=True,
        null=True,
        default="",
        help_text="Javascript to be included in the head tag. "
        "You should include the script tags.",
    )
    js_body = models.TextField(
        blank=True,
        null=True,
        default="",
        help_text="Javascript to be included before the closing body tag. "
        "You should include the script tags.",
    )

    def __str__(self):
        return "Site Configuration"

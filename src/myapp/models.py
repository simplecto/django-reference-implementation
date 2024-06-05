"""All of our Django models will be defined in this file."""

import solo.models
from django.db import models


FIVE_SECONDS = 5


class SiteConfiguration(solo.models.SingletonModel):
    """
    Site Configuration model. This model is used to store the configuration of the site.
    """

    worker_enabled = models.BooleanField(default=False)
    worker_sleep_seconds = models.IntegerField(default=FIVE_SECONDS)

    def __str__(self):
        return "Site Configuration"

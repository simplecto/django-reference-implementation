from solo.models import SingletonModel
from django.db import models


FIVE_SECONDS = 5


class SiteConfiguration(SingletonModel):

    worker_enabled = models.BooleanField(default=False)
    worker_sleep_seconds = models.IntegerField(default=FIVE_SECONDS)

    def __str__(self):
        return 'Site Configuration'

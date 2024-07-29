import uuid
from django.db import models


class WorkerConfiguration(models.Model):
    # these values match the python logging module values
    LOG_LEVEL_DEBUG = 10
    LOG_LEVEL_INFO = 20
    LOG_LEVEL_WARNING = 30
    LOG_LEVEL_ERROR = 40
    LOG_LEVEL_CRITICAL = 50
    LOG_LEVEL_CHOICES = [
        (LOG_LEVEL_DEBUG, "DEBUG"),
        (LOG_LEVEL_INFO, "INFO"),
        (LOG_LEVEL_WARNING, "WARNING"),
        (LOG_LEVEL_ERROR, "ERROR"),
        (LOG_LEVEL_CRITICAL, "CRITICAL"),
    ]

    uuid = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=False)
    sleep_seconds = models.IntegerField(default=10)

    log_level = models.IntegerField(
        choices=LOG_LEVEL_CHOICES,
        default=LOG_LEVEL_WARNING,
    )

    custom = models.JSONField(default=dict, null=True, blank=True)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

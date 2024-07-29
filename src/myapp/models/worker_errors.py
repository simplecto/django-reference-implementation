import uuid
from django.db import models


class WorkerError(models.Model):
    """
    Worker Error model. This model is used to store the errors encountered
    by the worker.
    """

    ERROR_OPEN = "O"
    ERROR_CLOSED = "C"
    ERROR_STATUS_CHOICES = ((ERROR_OPEN, "Open"), (ERROR_CLOSED, "Closed"))

    uuid = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )
    error = models.TextField()
    error_status = models.CharField(
        max_length=1, choices=ERROR_STATUS_CHOICES, default=ERROR_OPEN
    )

    worker = models.ForeignKey(
        "WorkerConfiguration",
        on_delete=models.CASCADE,
        related_name="worker_errors",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.worker.name

    class Meta:
        ordering = ["-created_at"]

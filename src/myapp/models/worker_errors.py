import uuid

from django.db import models


class WorkerError(models.Model):
    """Store the errors encountered by the worker."""

    ERROR_OPEN = "O"
    ERROR_CLOSED = "C"
    ERROR_STATUS_CHOICES = ((ERROR_OPEN, "Open"), (ERROR_CLOSED, "Closed"))

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    error = models.TextField()
    error_status = models.CharField(max_length=1, choices=ERROR_STATUS_CHOICES, default=ERROR_OPEN)

    worker = models.ForeignKey(
        "WorkerConfiguration",
        on_delete=models.CASCADE,
        related_name="worker_errors",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for the model."""

        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return the worker name."""
        return self.worker.name

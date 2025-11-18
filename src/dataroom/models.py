"""Models for the dataroom app."""

import uuid

from django.conf import settings
from django.db import models


class Customer(models.Model):
    """Customer model for tracking data room customers."""

    name = models.CharField(max_length=255, help_text="Company or project name")
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Freeform notes (contacts, emails, project details, etc.)",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="customers_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Customer model."""

        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self) -> str:
        """Return string representation."""
        return self.name


class DataEndpoint(models.Model):
    """Data endpoint for file uploads - identified by UUID for privacy."""

    STATUS_ACTIVE = "active"
    STATUS_DISABLED = "disabled"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="endpoints",
    )
    name = models.CharField(max_length=255, help_text="e.g., 'Q1 POC Upload', 'Phase 2 Data'")
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="endpoints_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for DataEndpoint model."""

        ordering = ["-created_at"]
        verbose_name = "Data Endpoint"
        verbose_name_plural = "Data Endpoints"

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.customer.name} - {self.name}"

    def get_upload_url(self) -> str:
        """Return the upload URL for this endpoint."""
        return f"/upload/{self.id}/"


class UploadedFile(models.Model):
    """File uploaded to a data endpoint."""

    endpoint = models.ForeignKey(
        DataEndpoint,
        on_delete=models.CASCADE,
        related_name="files",
    )
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, help_text="Relative path in MEDIA_ROOT")
    file_size_bytes = models.BigIntegerField()
    content_type = models.CharField(max_length=255, blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by_ip = models.GenericIPAddressField(null=True, blank=True)

    # Soft delete fields
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        """Meta options for UploadedFile model."""

        ordering = ["-uploaded_at"]
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.filename} ({self.endpoint.name})"

    @property
    def is_deleted(self) -> bool:
        """Check if file is soft-deleted."""
        return self.deleted_at is not None


class FileDownload(models.Model):
    """Audit log for file downloads by internal staff."""

    file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="downloads",
    )
    downloaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="file_downloads",
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        """Meta options for FileDownload model."""

        ordering = ["-downloaded_at"]
        verbose_name = "File Download"
        verbose_name_plural = "File Downloads"

    def __str__(self) -> str:
        """Return string representation."""
        user_str = self.downloaded_by.email if self.downloaded_by else "Unknown"
        return f"{self.file.filename} by {user_str} at {self.downloaded_at}"


class BulkDownload(models.Model):
    """Audit log for bulk downloads (zip files) of entire endpoints."""

    endpoint = models.ForeignKey(
        DataEndpoint,
        on_delete=models.CASCADE,
        related_name="bulk_downloads",
    )
    downloaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bulk_downloads",
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    file_count = models.IntegerField(help_text="Number of files included in the zip")
    total_bytes = models.BigIntegerField(help_text="Total size of all files in bytes")

    class Meta:
        """Meta options for BulkDownload model."""

        ordering = ["-downloaded_at"]
        verbose_name = "Bulk Download"
        verbose_name_plural = "Bulk Downloads"

    def __str__(self) -> str:
        """Return string representation."""
        user_str = self.downloaded_by.email if self.downloaded_by else "Unknown"
        return f"{self.endpoint} ({self.file_count} files) by {user_str} at {self.downloaded_at}"

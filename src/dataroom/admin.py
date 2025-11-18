"""Admin configuration for dataroom models."""

import io
import os
import re
import zipfile
from datetime import datetime

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, HttpRequest, HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import BulkDownload, Customer, DataEndpoint, FileDownload, UploadedFile


class DataEndpointInline(admin.TabularInline):
    """Inline admin for data endpoints."""

    model = DataEndpoint
    extra = 0
    fields = ("name", "status", "created_at", "copy_url_button")
    readonly_fields = ("created_at", "copy_url_button")
    can_delete = False

    def copy_url_button(self, obj: DataEndpoint) -> str:
        """Display a button to copy the upload URL."""
        if obj.pk:
            url = f"{settings.BASE_URL}/upload/{obj.id}/"
            return format_html(
                '<button type="button" onclick="navigator.clipboard.writeText(\'{}\'); '
                'alert(\'URL copied to clipboard!\');" '
                'style="padding: 4px 8px; cursor: pointer;">Copy Upload URL</button>',
                url,
            )
        return "-"

    copy_url_button.short_description = "Upload URL"  # type: ignore[attr-defined]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin for Customer model."""

    list_display = ("name", "created_by", "created_at", "endpoint_count")
    list_filter = ("created_at", "created_by")
    search_fields = ("name", "notes")
    readonly_fields = ("created_at",)
    inlines = [DataEndpointInline]

    fieldsets = (
        (None, {"fields": ("name", "notes")}),
        ("Metadata", {"fields": ("created_by", "created_at")}),
    )

    def endpoint_count(self, obj: Customer) -> int:
        """Show number of endpoints for this customer."""
        return obj.endpoints.count()

    endpoint_count.short_description = "Endpoints"  # type: ignore[attr-defined]

    def save_model(self, request: HttpRequest, obj: Customer, form, change: bool) -> None:  # type: ignore[no-untyped-def]
        """Set created_by to current user if creating new customer."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class UploadedFileInline(admin.TabularInline):
    """Inline admin for uploaded files."""

    model = UploadedFile
    extra = 0
    fields = ("filename", "file_size_display", "uploaded_at", "is_deleted_display")
    readonly_fields = ("filename", "file_size_display", "uploaded_at", "is_deleted_display")
    can_delete = False

    def file_size_display(self, obj: UploadedFile) -> str:
        """Display file size in human-readable format."""
        size = obj.file_size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    file_size_display.short_description = "Size"  # type: ignore[attr-defined]

    def is_deleted_display(self, obj: UploadedFile) -> str:
        """Display deletion status."""
        if obj.is_deleted:
            return format_html('<span style="color: red;">Deleted</span>')
        return format_html('<span style="color: green;">Active</span>')

    is_deleted_display.short_description = "Status"  # type: ignore[attr-defined]


@admin.register(DataEndpoint)
class DataEndpointAdmin(admin.ModelAdmin):
    """Admin for DataEndpoint model."""

    list_display = ("name", "customer", "status", "created_by", "created_at", "file_count", "upload_url_link")
    list_filter = ("status", "created_at", "created_by")
    search_fields = ("name", "customer__name", "description")
    readonly_fields = ("id", "created_at", "upload_url_display")
    inlines = [UploadedFileInline]
    actions = ["download_endpoint_as_zip"]

    fieldsets = (
        (None, {"fields": ("customer", "name", "description", "status")}),
        ("Upload Information", {"fields": ("id", "upload_url_display")}),
        ("Metadata", {"fields": ("created_by", "created_at")}),
    )

    def file_count(self, obj: DataEndpoint) -> int:
        """Show number of files for this endpoint."""
        return obj.files.filter(deleted_at__isnull=True).count()

    file_count.short_description = "Active Files"  # type: ignore[attr-defined]

    def upload_url_display(self, obj: DataEndpoint) -> str:
        """Display the full upload URL with copy button."""
        if obj.pk:
            url = f"{settings.BASE_URL}/upload/{obj.id}/"
            return format_html(
                '<div><a href="{}" target="_blank">{}</a> '
                '<button type="button" onclick="navigator.clipboard.writeText(\'{}\'); '
                'alert(\'URL copied to clipboard!\');" '
                'style="padding: 4px 8px; cursor: pointer; margin-left: 10px;">Copy URL</button></div>',
                url,
                url,
                url,
            )
        return "-"

    upload_url_display.short_description = "Upload URL"  # type: ignore[attr-defined]

    def upload_url_link(self, obj: DataEndpoint) -> str:
        """Show clickable link in list view."""
        if obj.pk:
            url = f"/upload/{obj.id}/"
            return format_html('<a href="{}" target="_blank">View Upload Page</a>', url)
        return "-"

    upload_url_link.short_description = "Upload Page"  # type: ignore[attr-defined]

    def save_model(self, request: HttpRequest, obj: DataEndpoint, form, change: bool) -> None:  # type: ignore[no-untyped-def]
        """Set created_by to current user if creating new endpoint."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Download all files as ZIP")
    def download_endpoint_as_zip(self, request: HttpRequest, queryset) -> HttpResponse:  # type: ignore[no-untyped-def]
        """Download all files from selected endpoint as a zip file."""
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one endpoint to download.", level="error")
            return HttpResponse()

        endpoint = queryset.first()

        # Get all non-deleted files for this endpoint
        files = endpoint.files.filter(deleted_at__isnull=True).order_by("filename")

        # Check if there are any files to download
        if not files.exists():
            self.message_user(request, "No files available to download for this endpoint.", level="warning")
            return HttpResponse()

        # Get client IP
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        # Calculate total size
        total_bytes = sum(f.file_size_bytes for f in files)

        # Create zip filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        customer_name_clean = re.sub(r"[^\w\-]", "_", endpoint.customer.name)
        endpoint_name_clean = re.sub(r"[^\w\-]", "_", endpoint.name)
        zip_filename = f"{customer_name_clean}-{endpoint_name_clean}-{timestamp}.zip"

        # Create in-memory buffer for zip file
        buffer = io.BytesIO()

        # Create zip file
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for uploaded_file in files:
                # Construct full file path
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file_path)

                # Check if file exists on disk
                if os.path.exists(file_path):
                    # Add file to zip with original filename
                    zip_file.write(file_path, uploaded_file.filename)

                    # Create individual FileDownload audit record
                    FileDownload.objects.create(
                        file=uploaded_file,
                        downloaded_by=request.user,
                        ip_address=ip_address,
                    )

        # Create BulkDownload audit record
        BulkDownload.objects.create(
            endpoint=endpoint,
            downloaded_by=request.user,
            ip_address=ip_address,
            file_count=files.count(),
            total_bytes=total_bytes,
        )

        # Show success message to user
        self.message_user(
            request,
            f"Downloaded {files.count()} files from {endpoint.name}",
            level="success",
        )

        # Get zip content
        zip_content = buffer.getvalue()

        # Create response
        response = HttpResponse(zip_content, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
        response["Content-Length"] = len(zip_content)

        return response


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """Admin for UploadedFile model."""

    list_display = (
        "filename",
        "endpoint",
        "file_size_display",
        "uploaded_at",
        "is_deleted_display",
        "download_count",
    )
    list_filter = ("uploaded_at", "deleted_at", "endpoint__customer", "endpoint")
    search_fields = ("filename", "endpoint__name", "endpoint__customer__name")
    readonly_fields = (
        "filename",
        "file_path",
        "file_size_bytes",
        "content_type",
        "uploaded_at",
        "uploaded_by_ip",
        "deleted_at",
        "deleted_by_ip",
    )
    actions = ["download_file"]

    fieldsets = (
        (None, {"fields": ("endpoint", "filename", "file_size_bytes", "content_type")}),
        ("Upload Information", {"fields": ("uploaded_at", "uploaded_by_ip", "file_path")}),
        ("Deletion Information", {"fields": ("deleted_at", "deleted_by_ip")}),
    )

    def file_size_display(self, obj: UploadedFile) -> str:
        """Display file size in human-readable format."""
        size = obj.file_size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    file_size_display.short_description = "Size"  # type: ignore[attr-defined]
    file_size_display.admin_order_field = "file_size_bytes"  # type: ignore[attr-defined]

    def is_deleted_display(self, obj: UploadedFile) -> str:
        """Display deletion status with color."""
        if obj.is_deleted:
            return format_html('<span style="color: red; font-weight: bold;">Deleted</span>')
        return format_html('<span style="color: green; font-weight: bold;">Active</span>')

    is_deleted_display.short_description = "Status"  # type: ignore[attr-defined]

    def download_count(self, obj: UploadedFile) -> int:
        """Show number of times file has been downloaded."""
        return obj.downloads.count()

    download_count.short_description = "Downloads"  # type: ignore[attr-defined]

    @admin.action(description="Download selected files")
    def download_file(self, request: HttpRequest, queryset) -> HttpResponse:  # type: ignore[no-untyped-def]
        """Download the selected file and log the download."""
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one file to download.", level="error")
            return HttpResponse()

        uploaded_file = queryset.first()

        # Build full file path
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file_path)

        if not os.path.exists(file_path):
            self.message_user(request, f"File not found: {uploaded_file.filename}", level="error")
            return HttpResponse()

        # Get client IP
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        # Log the download
        FileDownload.objects.create(
            file=uploaded_file,
            downloaded_by=request.user,
            ip_address=ip_address,
        )

        # Serve the file
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=uploaded_file.filename)
        return response


@admin.register(FileDownload)
class FileDownloadAdmin(admin.ModelAdmin):
    """Admin for FileDownload model (read-only audit log)."""

    list_display = ("file", "downloaded_by", "downloaded_at", "ip_address")
    list_filter = ("downloaded_at", "downloaded_by")
    search_fields = ("file__filename", "downloaded_by__email", "ip_address")
    readonly_fields = ("file", "downloaded_by", "downloaded_at", "ip_address")

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent manual creation of download logs."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:  # type: ignore[no-untyped-def]
        """Prevent deletion of audit logs."""
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:  # type: ignore[no-untyped-def]
        """Make this read-only."""
        return False


@admin.register(BulkDownload)
class BulkDownloadAdmin(admin.ModelAdmin):
    """Admin for BulkDownload model (read-only audit log)."""

    list_display = ("endpoint", "downloaded_by", "downloaded_at", "file_count", "total_size_display", "ip_address")
    list_filter = ("downloaded_at", "downloaded_by", "endpoint__customer")
    search_fields = ("endpoint__name", "endpoint__customer__name", "downloaded_by__email", "ip_address")
    readonly_fields = ("endpoint", "downloaded_by", "downloaded_at", "file_count", "total_bytes", "ip_address")

    def total_size_display(self, obj: BulkDownload) -> str:
        """Display total size in human-readable format."""
        size = obj.total_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    total_size_display.short_description = "Total Size"  # type: ignore[attr-defined]
    total_size_display.admin_order_field = "total_bytes"  # type: ignore[attr-defined]

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent manual creation of bulk download logs."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:  # type: ignore[no-untyped-def]
        """Prevent deletion of audit logs."""
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:  # type: ignore[no-untyped-def]
        """Make this read-only."""
        return False
